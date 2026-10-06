from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np
from scipy.optimize import least_squares

from semantic_morphism import (
    LinearSemanticMorphismCertificate,
    SemanticMorphismKind,
    analyze_linear_semantic_morphism,
)


@dataclass(frozen=True)
class NonlinearControllerIR:
    """Controller action semantics as a bounded nonlinear map to one common goal."""

    action_dim: int
    goal_dim: int
    native_low: np.ndarray
    native_high: np.ndarray
    goal_fn: Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]
    state_dim: int = 0
    hidden_dim: int = 0
    jacobian_fn: Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray] | None = None
    name: str = ""

    def __post_init__(self) -> None:
        low = np.asarray(self.native_low, dtype=float)
        high = np.asarray(self.native_high, dtype=float)
        if self.action_dim <= 0 or self.goal_dim <= 0:
            raise ValueError("action_dim and goal_dim must be positive")
        if low.shape != (self.action_dim,) or high.shape != (self.action_dim,):
            raise ValueError("native bounds must match action_dim")
        if np.any(~np.isfinite(low)) or np.any(~np.isfinite(high)) or np.any(high <= low):
            raise ValueError("native bounds must be finite and ordered")
        object.__setattr__(self, "native_low", low)
        object.__setattr__(self, "native_high", high)

    def goal(self, u: np.ndarray, x: np.ndarray, z: np.ndarray) -> np.ndarray:
        u = np.asarray(u, dtype=float)
        x = np.asarray(x, dtype=float)
        z = np.asarray(z, dtype=float)
        if u.shape != (self.action_dim,):
            raise ValueError("action dimension mismatch")
        if x.shape != (self.state_dim,):
            raise ValueError("state dimension mismatch")
        if z.shape != (self.hidden_dim,):
            raise ValueError("hidden-state dimension mismatch")
        y = np.asarray(self.goal_fn(u, x, z), dtype=float)
        if y.shape != (self.goal_dim,) or not np.all(np.isfinite(y)):
            raise ValueError("goal_fn returned invalid canonical goal")
        return y


@dataclass(frozen=True)
class NonlinearTransportCertificate:
    source_goal: np.ndarray
    target_action: np.ndarray | None
    reconstructed_goal: np.ndarray | None
    residual_norm: float
    relative_residual: float
    exact: bool
    target_local_rank: int
    target_local_nullity: int
    target_local_condition: float
    local_structure: LinearSemanticMorphismCertificate | None
    distinct_exact_solutions: int
    native_margin: np.ndarray | None
    solver_attempts: int
    reason: str


def finite_difference_action_jacobian(
    controller: NonlinearControllerIR,
    action: np.ndarray,
    state: np.ndarray,
    hidden: np.ndarray,
    *,
    relative_step: float = 1e-6,
) -> np.ndarray:
    """Central-difference Jacobian of canonical goal with respect to native action."""
    u = np.asarray(action, dtype=float)
    J = np.zeros((controller.goal_dim, controller.action_dim), dtype=float)
    for j in range(controller.action_dim):
        step = relative_step * max(1.0, abs(float(u[j])))
        plus = u.copy()
        minus = u.copy()
        plus[j] = min(controller.native_high[j], u[j] + step)
        minus[j] = max(controller.native_low[j], u[j] - step)
        denom = plus[j] - minus[j]
        if denom <= 0:
            raise ValueError("cannot form finite difference inside native bounds")
        J[:, j] = (
            controller.goal(plus, state, hidden)
            - controller.goal(minus, state, hidden)
        ) / denom
    return J


def action_jacobian(
    controller: NonlinearControllerIR,
    action: np.ndarray,
    state: np.ndarray,
    hidden: np.ndarray,
) -> np.ndarray:
    if controller.jacobian_fn is None:
        return finite_difference_action_jacobian(controller, action, state, hidden)
    J = np.asarray(controller.jacobian_fn(action, state, hidden), dtype=float)
    if J.shape != (controller.goal_dim, controller.action_dim):
        raise ValueError("jacobian_fn returned wrong shape")
    if not np.all(np.isfinite(J)):
        raise ValueError("jacobian_fn returned non-finite values")
    return J


def _condition_nonzero(J: np.ndarray, rtol: float) -> tuple[int, float]:
    singular = np.linalg.svd(J, compute_uv=False)
    if singular.size == 0:
        return 0, float("inf")
    threshold = rtol * max(float(singular[0]), 1.0)
    nz = singular[singular > threshold]
    if nz.size == 0:
        return 0, float("inf")
    return int(nz.size), float(nz[0] / nz[-1])


def _cluster_exact_solutions(
    solutions: list[np.ndarray],
    *,
    tol: float,
) -> list[np.ndarray]:
    clusters: list[np.ndarray] = []
    for solution in solutions:
        if all(np.linalg.norm(solution - old) > tol for old in clusters):
            clusters.append(solution)
    return clusters


def compile_nonlinear_transport(
    *,
    source: NonlinearControllerIR,
    target: NonlinearControllerIR,
    source_action: np.ndarray,
    source_state: np.ndarray,
    source_hidden: np.ndarray,
    target_state: np.ndarray,
    target_hidden: np.ndarray,
    initial_guesses: Iterable[np.ndarray] | None = None,
    atol: float = 1e-8,
    rtol: float = 1e-8,
    solution_cluster_tol: float = 1e-4,
) -> NonlinearTransportCertificate:
    """Bounded multi-start transport through a shared nonlinear physical goal.

    Success certifies only the chosen canonical goal, not trajectory or drive
    equivalence. Failure to find an exact solution is fail-closed but is not a
    mathematical proof that no global inverse exists.
    """
    if source.goal_dim != target.goal_dim:
        raise ValueError("source and target must share canonical goal dimension")

    source_action = np.asarray(source_action, dtype=float)
    target_state = np.asarray(target_state, dtype=float)
    target_hidden = np.asarray(target_hidden, dtype=float)
    y = source.goal(source_action, source_state, source_hidden)
    scale = max(float(np.linalg.norm(y)), 1.0)
    threshold = atol + rtol * scale

    starts = [0.5 * (target.native_low + target.native_high)]
    if initial_guesses is not None:
        starts.extend(np.asarray(s, dtype=float) for s in initial_guesses)
    # Deterministic corners broaden the basin search without pretending to be
    # an exhaustive global inverse solver.
    starts.extend([
        target.native_low + 0.25 * (target.native_high - target.native_low),
        target.native_low + 0.75 * (target.native_high - target.native_low),
    ])

    exact_solutions: list[np.ndarray] = []
    best = None
    best_residual = float("inf")
    for start in starts:
        if start.shape != (target.action_dim,):
            raise ValueError("initial guess dimension mismatch")
        start = np.clip(start, target.native_low, target.native_high)
        result = least_squares(
            lambda u: target.goal(u, target_state, target_hidden) - y,
            x0=start,
            bounds=(target.native_low, target.native_high),
            xtol=1e-12,
            ftol=1e-12,
            gtol=1e-12,
            max_nfev=2000,
        )
        candidate = np.asarray(result.x, dtype=float)
        reconstructed = target.goal(candidate, target_state, target_hidden)
        residual = float(np.linalg.norm(reconstructed - y))
        if residual < best_residual:
            best = candidate
            best_residual = residual
        if result.success and residual <= threshold:
            exact_solutions.append(candidate)

    clusters = _cluster_exact_solutions(exact_solutions, tol=solution_cluster_tol)
    if best is None:
        return NonlinearTransportCertificate(
            y, None, None, float("inf"), float("inf"), False, 0,
            target.action_dim, float("inf"), None, 0, None, len(starts),
            "nonlinear target solver produced no candidate",
        )

    reconstructed = target.goal(best, target_state, target_hidden)
    exact = bool(best_residual <= threshold)
    J_target = action_jacobian(target, best, target_state, target_hidden)
    rank, condition = _condition_nonzero(J_target, rtol)
    nullity = target.action_dim - rank
    margin = np.minimum(
        (best - target.native_low) / (target.native_high - target.native_low),
        (target.native_high - best) / (target.native_high - target.native_low),
    )

    local_structure = None
    try:
        J_source = action_jacobian(
            source, source_action, source_state, source_hidden
        )
        local_structure = analyze_linear_semantic_morphism(
            J_source, J_target, rtol=max(rtol, 1e-10)
        )
    except ValueError:
        local_structure = None

    if not exact:
        reason = (
            "no exact bounded target was found by deterministic multi-start; "
            "refuse execution rather than treating the closest goal as equivalent"
        )
    elif len(clusters) > 1:
        reason = (
            "canonical goal is exactly reachable but multiple separated target "
            "actions were found; target inverse is globally ambiguous"
        )
    elif nullity > 0:
        reason = (
            "canonical goal is exact but the local target Jacobian has nullspace "
            "freedom; only observable-level equivalence is certified"
        )
    elif local_structure is not None and local_structure.kind is SemanticMorphismKind.EXACT_EQUIVALENCE:
        reason = "exact bounded goal with locally bijective controller semantics"
    else:
        reason = "exact bounded canonical goal; stronger semantic equivalence is not certified"

    return NonlinearTransportCertificate(
        source_goal=y,
        target_action=best if exact else None,
        reconstructed_goal=reconstructed,
        residual_norm=best_residual,
        relative_residual=best_residual / scale,
        exact=exact,
        target_local_rank=rank,
        target_local_nullity=nullity,
        target_local_condition=condition,
        local_structure=local_structure,
        distinct_exact_solutions=len(clusters),
        native_margin=margin,
        solver_attempts=len(starts),
        reason=reason,
    )


def planar_two_link_joint_chart(
    *,
    link_lengths: tuple[float, float] = (1.0, 1.0),
    joint_limit: float = np.pi,
    name: str = "planar_two_link_joint",
) -> NonlinearControllerIR:
    """Two-link FK chart used as a deterministic cross-family CST assay."""
    l1, l2 = map(float, link_lengths)

    def goal(u, _x, _z):
        q1, q2 = u
        return np.array([
            l1 * np.cos(q1) + l2 * np.cos(q1 + q2),
            l1 * np.sin(q1) + l2 * np.sin(q1 + q2),
        ])

    def jac(u, _x, _z):
        q1, q2 = u
        return np.array([
            [
                -l1 * np.sin(q1) - l2 * np.sin(q1 + q2),
                -l2 * np.sin(q1 + q2),
            ],
            [
                l1 * np.cos(q1) + l2 * np.cos(q1 + q2),
                l2 * np.cos(q1 + q2),
            ],
        ])

    return NonlinearControllerIR(
        action_dim=2,
        goal_dim=2,
        native_low=np.full(2, -joint_limit),
        native_high=np.full(2, joint_limit),
        goal_fn=goal,
        jacobian_fn=jac,
        name=name,
    )


def planar_cartesian_chart(
    *,
    limit: float = 3.0,
    name: str = "planar_cartesian",
) -> NonlinearControllerIR:
    return NonlinearControllerIR(
        action_dim=2,
        goal_dim=2,
        native_low=np.full(2, -limit),
        native_high=np.full(2, limit),
        goal_fn=lambda u, _x, _z: np.asarray(u, dtype=float),
        jacobian_fn=lambda _u, _x, _z: np.eye(2),
        name=name,
    )
