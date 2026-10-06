from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import lsq_linear


@dataclass(frozen=True)
class AffineControllerIR:
    """Canonical-goal semantics for one local affine controller region.

    The controller maps native action u, measured state x and hidden controller
    state z into a canonical physical goal

        y* = U u + X x + Z z + b.

    This IR describes goal semantics only. Drive gains, saturation outside the
    native bounds, IK branches, contacts and nonlinear task-space charts require
    separate certificates.
    """

    U: np.ndarray
    X: np.ndarray
    Z: np.ndarray
    b: np.ndarray
    native_low: np.ndarray
    native_high: np.ndarray
    name: str = ""

    def __post_init__(self) -> None:
        U = np.asarray(self.U, dtype=float)
        X = np.asarray(self.X, dtype=float)
        Z = np.asarray(self.Z, dtype=float)
        b = np.asarray(self.b, dtype=float)
        low = np.asarray(self.native_low, dtype=float)
        high = np.asarray(self.native_high, dtype=float)
        if U.ndim != 2:
            raise ValueError("U must have shape [goal_dim, action_dim]")
        goal_dim, action_dim = U.shape
        if X.ndim != 2 or X.shape[0] != goal_dim:
            raise ValueError("X must share goal dimension with U")
        if Z.ndim != 2 or Z.shape[0] != goal_dim:
            raise ValueError("Z must share goal dimension with U")
        if b.shape != (goal_dim,):
            raise ValueError("b must have shape [goal_dim]")
        if low.shape != (action_dim,) or high.shape != (action_dim,):
            raise ValueError("native bounds must have shape [action_dim]")
        if np.any(high <= low):
            raise ValueError("native high bounds must exceed low bounds")
        for item in (U, X, Z, b, low, high):
            if not np.all(np.isfinite(item)):
                raise ValueError("IR parameters must be finite")
        object.__setattr__(self, "U", U)
        object.__setattr__(self, "X", X)
        object.__setattr__(self, "Z", Z)
        object.__setattr__(self, "b", b)
        object.__setattr__(self, "native_low", low)
        object.__setattr__(self, "native_high", high)

    @property
    def goal_dim(self) -> int:
        return int(self.U.shape[0])

    @property
    def action_dim(self) -> int:
        return int(self.U.shape[1])

    @property
    def state_dim(self) -> int:
        return int(self.X.shape[1])

    @property
    def hidden_dim(self) -> int:
        return int(self.Z.shape[1])

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
        return self.U @ u + self.X @ x + self.Z @ z + self.b


@dataclass(frozen=True)
class AffineTransportCertificate:
    target_action: np.ndarray
    bounded_target_action: np.ndarray
    source_goal: np.ndarray
    reconstructed_goal: np.ndarray
    residual_norm: float
    relative_residual: float
    bounded_residual_norm: float
    bounded_relative_residual: float
    target_rank: int
    target_nullity: int
    algebraically_representable: bool
    bounded_representable: bool
    unique_if_exact: bool
    native_margin: np.ndarray
    bounded_native_margin: np.ndarray
    bounded_solver_success: bool
    reason: str


def _native_margin(action: np.ndarray, low: np.ndarray, high: np.ndarray) -> np.ndarray:
    width = high - low
    return np.minimum((action - low) / width, (high - action) / width)


def compile_affine_transport(
    *,
    source: AffineControllerIR,
    target: AffineControllerIR,
    source_action: np.ndarray,
    source_state: np.ndarray,
    source_hidden: np.ndarray,
    target_state: np.ndarray,
    target_hidden: np.ndarray,
    atol: float = 1e-10,
    rtol: float = 1e-10,
) -> AffineTransportCertificate:
    """Compile and certify unconstrained and bounded target transports.

    The Moore-Penrose solution determines whether the source canonical goal is
    in the target controller's algebraic image. A bounded convex least-squares
    solve then determines whether the same goal is reachable inside native
    action limits. When exact bounded transport is impossible, the bounded
    solution is still returned as the closest admissible goal-level
    approximation, together with its residual.
    """
    if source.goal_dim != target.goal_dim:
        raise ValueError("source and target canonical goal dimensions must match")

    y_source = source.goal(source_action, source_state, source_hidden)
    target_offset = (
        target.X @ np.asarray(target_state, dtype=float)
        + target.Z @ np.asarray(target_hidden, dtype=float)
        + target.b
    )
    rhs = y_source - target_offset
    scale = max(float(np.linalg.norm(y_source)), 1.0)
    threshold = atol + rtol * scale

    target_action = np.linalg.pinv(target.U) @ rhs
    reconstructed = target.U @ target_action + target_offset
    residual = float(np.linalg.norm(reconstructed - y_source))
    algebraic = bool(residual <= threshold)

    bounded_result = lsq_linear(
        target.U,
        rhs,
        bounds=(target.native_low, target.native_high),
        lsmr_tol="auto",
        tol=max(atol, 1e-12),
    )
    bounded_action = np.asarray(bounded_result.x, dtype=float)
    bounded_reconstructed = target.U @ bounded_action + target_offset
    bounded_residual = float(np.linalg.norm(bounded_reconstructed - y_source))
    bounded = bool(bounded_result.success and bounded_residual <= threshold)

    rank = int(np.linalg.matrix_rank(target.U))
    nullity = int(target.action_dim - rank)
    margin = _native_margin(target_action, target.native_low, target.native_high)
    bounded_margin = _native_margin(
        bounded_action, target.native_low, target.native_high
    )

    if not algebraic:
        reason = (
            "target algebraic image does not contain the source goal; bounded "
            "action is the closest admissible approximation"
        )
    elif bounded and nullity > 0:
        reason = (
            "bounded exact transport exists; target action is algebraically "
            "non-unique because the target map has nullspace freedom"
        )
    elif bounded:
        reason = "unique bounded action exactly preserves the canonical physical goal"
    else:
        reason = (
            "source goal is algebraically representable but no exact action "
            "exists inside the target native bounds"
        )

    return AffineTransportCertificate(
        target_action=target_action,
        bounded_target_action=bounded_action,
        source_goal=y_source,
        reconstructed_goal=reconstructed,
        residual_norm=residual,
        relative_residual=residual / scale,
        bounded_residual_norm=bounded_residual,
        bounded_relative_residual=bounded_residual / scale,
        target_rank=rank,
        target_nullity=nullity,
        algebraically_representable=algebraic,
        bounded_representable=bounded,
        unique_if_exact=bool(algebraic and nullity == 0),
        native_margin=margin,
        bounded_native_margin=bounded_margin,
        bounded_solver_success=bool(bounded_result.success),
        reason=reason,
    )


def normalized_joint_position_ir(
    *,
    mode: str,
    physical_low: np.ndarray,
    physical_high: np.ndarray,
    name: str = "",
) -> AffineControllerIR:
    """Compile a normalized joint-position controller into affine CST IR.

    mode is one of: absolute, delta_current, delta_target.
    State x and hidden z both use q-space dimension D. Only the semantically
    relevant reference matrix is activated.
    """
    low = np.asarray(physical_low, dtype=float)
    high = np.asarray(physical_high, dtype=float)
    if low.ndim != 1 or high.shape != low.shape:
        raise ValueError("physical bounds must have shape [D]")
    D = low.shape[0]
    scale = np.diag(0.5 * (high - low))
    midpoint = 0.5 * (high + low)
    zeros = np.zeros((D, D))
    if mode == "absolute":
        X, Z = zeros, zeros
    elif mode == "delta_current":
        X, Z = np.eye(D), zeros
    elif mode == "delta_target":
        X, Z = zeros, np.eye(D)
    else:
        raise ValueError("unknown joint-position mode")
    return AffineControllerIR(
        U=scale,
        X=X,
        Z=Z,
        b=midpoint,
        native_low=-np.ones(D),
        native_high=np.ones(D),
        name=name or mode,
    )
