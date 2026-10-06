from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class TransportStatus(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    IMPOSSIBLE = "impossible"


@dataclass(frozen=True)
class ClosedLoopTransportCertificate:
    """Local certificate for transporting one controller through another.

    Source local dynamics:
        x' = A_s x + B_s u_s

    Target local dynamics:
        x' = A_t x + B_t u_t

    Adapter:
        u_t = K_x x + K_u u_s

    Exact local transport exists iff every column of
        [A_s - A_t, B_s]
    lies in image(B_t).
    """

    status: TransportStatus
    exact_possible: bool
    K_state: np.ndarray
    K_action: np.ndarray
    state_residual: np.ndarray
    action_residual: np.ndarray
    relative_residual: float
    exact_impossibility_lower_bound: float
    witness_input: np.ndarray
    witness_unmatched_direction: np.ndarray
    target_rank: int
    target_condition_number: float
    reason: str


@dataclass(frozen=True)
class FiniteHorizonCertificate:
    horizon: int
    adapted_state_matrix: np.ndarray
    adapted_action_matrix: np.ndarray
    contraction_factor: float
    one_step_mismatch_bound: float
    initial_error: float
    error_bound: float
    contractive: bool


def _matrix(value: np.ndarray, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise ValueError(f"{name} must be a non-empty matrix")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _spectral_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord=2))


def _condition_number_on_image(matrix: np.ndarray, rtol: float) -> float:
    singular = np.linalg.svd(matrix, compute_uv=False)
    if singular.size == 0:
        return float("inf")
    threshold = rtol * max(float(singular[0]), 1.0)
    nz = singular[singular > threshold]
    if nz.size == 0:
        return float("inf")
    return float(nz[0] / nz[-1])


def synthesize_local_closed_loop_transport(
    source_A: np.ndarray,
    source_B: np.ndarray,
    target_A: np.ndarray,
    target_B: np.ndarray,
    *,
    exact_rtol: float = 1e-10,
    approximate_relative_tolerance: float = 5e-2,
) -> ClosedLoopTransportCertificate:
    """Synthesize the minimum-norm local stateful controller adapter.

    The source and target models must use the same chosen shared state / physical
    observable coordinates. Hidden controller state can be included by augmenting
    that state before calling this function.

    The target adapter is affine in local deviations without a constant term:
        u_t = K_state @ x + K_action @ u_s.

    A non-zero projection residual is also a constructive witness that exact
    local transport is impossible through the target actuation image.
    """
    A_s = _matrix(source_A, "source_A")
    B_s = _matrix(source_B, "source_B")
    A_t = _matrix(target_A, "target_A")
    B_t = _matrix(target_B, "target_B")

    n = A_s.shape[0]
    if A_s.shape != (n, n) or A_t.shape != (n, n):
        raise ValueError("source_A and target_A must be square with equal state dimension")
    if B_s.shape[0] != n or B_t.shape[0] != n:
        raise ValueError("source_B and target_B must map into the shared state dimension")
    if exact_rtol <= 0 or not np.isfinite(exact_rtol):
        raise ValueError("exact_rtol must be finite and positive")
    if approximate_relative_tolerance < 0 or not np.isfinite(
        approximate_relative_tolerance
    ):
        raise ValueError("approximate_relative_tolerance must be finite and non-negative")

    demand = np.concatenate([A_s - A_t, B_s], axis=1)
    target_pinv = np.linalg.pinv(B_t, rcond=exact_rtol)
    adapter = target_pinv @ demand
    K_state = adapter[:, :n]
    K_action = adapter[:, n:]

    projected = B_t @ adapter
    residual = demand - projected
    state_residual = residual[:, :n]
    action_residual = residual[:, n:]

    demand_scale = max(_spectral_norm(demand), 1.0)
    residual_norm = _spectral_norm(residual)
    relative_residual = residual_norm / demand_scale
    exact_possible = bool(residual_norm <= exact_rtol * demand_scale)

    if residual_norm > 0:
        _, _, vh = np.linalg.svd(residual, full_matrices=False)
        witness_input = vh[0]
        unmatched = residual @ witness_input
        unmatched_norm = float(np.linalg.norm(unmatched))
        if unmatched_norm > 0:
            witness_unmatched_direction = unmatched / unmatched_norm
        else:
            witness_unmatched_direction = np.zeros(n)
    else:
        witness_input = np.zeros(demand.shape[1])
        witness_unmatched_direction = np.zeros(n)

    if exact_possible:
        status = TransportStatus.EXACT
        reason = (
            "source closed-loop state/action demand lies inside the target "
            "actuation image"
        )
    elif relative_residual <= approximate_relative_tolerance:
        status = TransportStatus.APPROXIMATE
        reason = (
            "exact transport is impossible locally, but the unmatched demand "
            "is below the declared approximation tolerance"
        )
    else:
        status = TransportStatus.IMPOSSIBLE
        reason = (
            "a source closed-loop demand direction lies outside the target "
            "actuation image"
        )

    return ClosedLoopTransportCertificate(
        status=status,
        exact_possible=exact_possible,
        K_state=K_state,
        K_action=K_action,
        state_residual=state_residual,
        action_residual=action_residual,
        relative_residual=relative_residual,
        exact_impossibility_lower_bound=residual_norm,
        witness_input=witness_input,
        witness_unmatched_direction=witness_unmatched_direction,
        target_rank=int(np.linalg.matrix_rank(B_t, tol=exact_rtol)),
        target_condition_number=_condition_number_on_image(B_t, exact_rtol),
        reason=reason,
    )


def certify_finite_horizon_transport(
    certificate: ClosedLoopTransportCertificate,
    source_A: np.ndarray,
    source_B: np.ndarray,
    target_A: np.ndarray,
    target_B: np.ndarray,
    *,
    horizon: int,
    source_state_radius: float,
    source_action_radius: float,
    initial_error: float = 0.0,
) -> FiniteHorizonCertificate:
    """Bound trajectory deviation under the synthesized local adapter.

    With e_t = x_target - x_source,
        ||e_{t+1}|| <= rho ||e_t|| + delta,
    where rho is the adapted target state-map norm and delta bounds the
    state/action semantic mismatch over the declared source region.
    """
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    if source_state_radius < 0 or source_action_radius < 0 or initial_error < 0:
        raise ValueError("radii and initial_error must be non-negative")

    A_s = _matrix(source_A, "source_A")
    B_s = _matrix(source_B, "source_B")
    A_t = _matrix(target_A, "target_A")
    B_t = _matrix(target_B, "target_B")

    A_adapted = A_t + B_t @ certificate.K_state
    B_adapted = B_t @ certificate.K_action
    R_A = A_adapted - A_s
    R_B = B_adapted - B_s

    rho = _spectral_norm(A_adapted)
    delta = (
        _spectral_norm(R_A) * float(source_state_radius)
        + _spectral_norm(R_B) * float(source_action_radius)
    )

    if horizon == 0:
        bound = float(initial_error)
    elif abs(rho - 1.0) <= 1e-12:
        bound = float(initial_error + horizon * delta)
    else:
        geometric = (rho**horizon - 1.0) / (rho - 1.0)
        bound = float((rho**horizon) * initial_error + geometric * delta)

    return FiniteHorizonCertificate(
        horizon=horizon,
        adapted_state_matrix=A_adapted,
        adapted_action_matrix=B_adapted,
        contraction_factor=rho,
        one_step_mismatch_bound=delta,
        initial_error=float(initial_error),
        error_bound=bound,
        contractive=bool(rho < 1.0),
    )


def rollout_linear_system(
    A: np.ndarray,
    B: np.ndarray,
    x0: np.ndarray,
    actions: np.ndarray,
) -> np.ndarray:
    """Reference rollout used by tests and evidence generation."""
    A = _matrix(A, "A")
    B = _matrix(B, "B")
    x = np.asarray(x0, dtype=float)
    actions = np.asarray(actions, dtype=float)
    if x.shape != (A.shape[0],):
        raise ValueError("x0 dimension mismatch")
    if actions.ndim != 2 or actions.shape[1] != B.shape[1]:
        raise ValueError("actions dimension mismatch")
    states = [x.copy()]
    for action in actions:
        x = A @ x + B @ action
        states.append(x.copy())
    return np.stack(states)
