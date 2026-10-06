from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LinearClosedLoopModel:
    """Local common-state model x' = A x + B u.

    x is a shared physical / semantic state. It may be augmented with
    controller-owned state when that state is part of the declared contract.
    """

    A: np.ndarray
    B: np.ndarray


@dataclass(frozen=True)
class ClosedLoopTransportCertificate:
    """Local state-feedback transport u_tgt = Kx x_tgt + Ku u_src."""

    state_gain: np.ndarray
    action_gain: np.ndarray
    state_residual: np.ndarray
    action_residual: np.ndarray
    max_state_residual_norm: float
    max_action_residual_norm: float
    unavoidable_operator_residual: float
    exact: bool
    target_effect_rank: int
    target_effect_condition_number: float
    witness_state: np.ndarray
    witness_action: np.ndarray
    witness_residual: np.ndarray
    reason: str


@dataclass(frozen=True)
class FiniteHorizonDeviationCertificate:
    horizon: int
    contraction_factor: float
    per_step_model_defect_bound: float
    initial_error_bound: float
    final_error_bound: float
    trajectory_error_bounds: np.ndarray
    exact_if_same_initial_state: bool
    reason: str


def _matrix(value: np.ndarray, *, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise ValueError(f"{name} must be a non-empty matrix")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _validate_model(model: LinearClosedLoopModel, *, name: str) -> tuple[np.ndarray, np.ndarray]:
    A = _matrix(model.A, name=f"{name}.A")
    B = _matrix(model.B, name=f"{name}.B")
    if A.shape[0] != A.shape[1]:
        raise ValueError(f"{name}.A must be square")
    if B.shape[0] != A.shape[0]:
        raise ValueError(f"{name}.B row dimension must match {name}.A")
    return A, B


def _nonzero_condition_number(matrix: np.ndarray, rtol: float) -> float:
    singular = np.linalg.svd(matrix, compute_uv=False)
    if singular.size == 0:
        return float("inf")
    threshold = rtol * max(float(singular[0]), 1.0)
    nonzero = singular[singular > threshold]
    if nonzero.size == 0:
        return float("inf")
    return float(nonzero[0] / nonzero[-1])


def synthesize_closed_loop_transport(
    source: LinearClosedLoopModel,
    target: LinearClosedLoopModel,
    *,
    atol: float = 1e-10,
    rtol: float = 1e-10,
) -> ClosedLoopTransportCertificate:
    """Synthesize the minimum-norm local transport and an impossibility witness.

    The target receives

        u_tgt = Kx x_tgt + Ku u_src.

    Exact one-step common-state equivalence requires

        A_tgt + B_tgt Kx = A_src
        B_tgt Ku = B_src.

    These equations are solvable exactly iff every column of
    [A_src - A_tgt, B_src] lies in image(B_tgt).  When this is false, the
    certificate returns the source state/action direction with maximum
    unavoidable one-step residual under the local linear model.
    """

    A_s, B_s = _validate_model(source, name="source")
    A_t, B_t = _validate_model(target, name="target")
    if A_s.shape != A_t.shape:
        raise ValueError("source and target must use the same common-state dimension")
    if atol < 0 or rtol <= 0 or not np.isfinite(atol) or not np.isfinite(rtol):
        raise ValueError("atol must be non-negative and rtol finite and positive")

    pinv_t = np.linalg.pinv(B_t, rcond=rtol)
    state_gain = pinv_t @ (A_s - A_t)
    action_gain = pinv_t @ B_s

    target_closed_loop_A = A_t + B_t @ state_gain
    target_closed_loop_B = B_t @ action_gain
    state_residual = target_closed_loop_A - A_s
    action_residual = target_closed_loop_B - B_s

    state_norm = float(np.linalg.norm(state_residual, ord=2))
    action_norm = float(np.linalg.norm(action_residual, ord=2))

    # Structural witness: the component of requested source dynamics/effects
    # outside the target controller's locally executable image.
    projector = B_t @ pinv_t
    requested = np.concatenate([A_s - A_t, B_s], axis=1)
    impossible = (np.eye(A_s.shape[0]) - projector) @ requested
    if impossible.size:
        _, singular, vh = np.linalg.svd(impossible, full_matrices=False)
        if singular.size:
            witness_vector = vh[0]
            unavoidable = float(singular[0])
        else:
            witness_vector = np.zeros(requested.shape[1], dtype=float)
            unavoidable = 0.0
    else:
        witness_vector = np.zeros(requested.shape[1], dtype=float)
        unavoidable = 0.0

    n_state = A_s.shape[1]
    witness_state = witness_vector[:n_state]
    witness_action = witness_vector[n_state:]
    witness_residual = impossible @ witness_vector

    scale_state = max(float(np.linalg.norm(A_s, ord=2)), 1.0)
    scale_action = max(float(np.linalg.norm(B_s, ord=2)), 1.0)
    exact = bool(
        state_norm <= atol + rtol * scale_state
        and action_norm <= atol + rtol * scale_action
    )

    rank_target = int(np.linalg.matrix_rank(B_t, tol=rtol * max(float(np.linalg.norm(B_t, ord=2)), 1.0)))
    if exact:
        reason = (
            "target input image can reproduce both the source local state dynamics "
            "and source action effects under the synthesized feedback transport"
        )
    else:
        reason = (
            "some requested source closed-loop direction lies outside the target "
            "controller input image; no local linear state-feedback adapter can "
            "remove the returned witness residual"
        )

    return ClosedLoopTransportCertificate(
        state_gain=state_gain,
        action_gain=action_gain,
        state_residual=state_residual,
        action_residual=action_residual,
        max_state_residual_norm=state_norm,
        max_action_residual_norm=action_norm,
        unavoidable_operator_residual=unavoidable,
        exact=exact,
        target_effect_rank=rank_target,
        target_effect_condition_number=_nonzero_condition_number(B_t, rtol),
        witness_state=witness_state,
        witness_action=witness_action,
        witness_residual=witness_residual,
        reason=reason,
    )


def certify_finite_horizon_deviation(
    source: LinearClosedLoopModel,
    target: LinearClosedLoopModel,
    transport: ClosedLoopTransportCertificate,
    *,
    horizon: int,
    source_state_radius: float,
    source_action_radius: float,
    initial_error_bound: float = 0.0,
) -> FiniteHorizonDeviationCertificate:
    """Bound H-step common-state deviation for the synthesized transport.

    For e_t = x_tgt - x_src,

        ||e_{t+1}|| <= rho ||e_t|| + delta,

    where
        rho   = ||A_tgt + B_tgt Kx||_2
        delta = ||R_x|| X + ||R_u|| U.

    X and U are declared bounds on source state and source native action norms.
    This is a local certificate: it is valid only where the supplied
    linearizations and radii remain valid.
    """

    A_s, B_s = _validate_model(source, name="source")
    A_t, B_t = _validate_model(target, name="target")
    if A_s.shape != A_t.shape:
        raise ValueError("source and target must use the same common-state dimension")
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    for name, value in (
        ("source_state_radius", source_state_radius),
        ("source_action_radius", source_action_radius),
        ("initial_error_bound", initial_error_bound),
    ):
        if value < 0 or not np.isfinite(value):
            raise ValueError(f"{name} must be finite and non-negative")

    if transport.state_gain.shape != (B_t.shape[1], A_t.shape[0]):
        raise ValueError("transport.state_gain shape is incompatible with target model")
    if transport.action_gain.shape != (B_t.shape[1], B_s.shape[1]):
        raise ValueError("transport.action_gain shape is incompatible with models")

    target_closed_loop = A_t + B_t @ transport.state_gain
    rho = float(np.linalg.norm(target_closed_loop, ord=2))
    defect = (
        transport.max_state_residual_norm * float(source_state_radius)
        + transport.max_action_residual_norm * float(source_action_radius)
    )

    bounds = [float(initial_error_bound)]
    current = float(initial_error_bound)
    for _ in range(horizon):
        current = rho * current + defect
        bounds.append(float(current))

    exact_same_initial = bool(
        initial_error_bound == 0.0
        and transport.exact
        and defect <= 1e-15
    )
    if exact_same_initial:
        reason = (
            "the local transport exactly matches source dynamics/effects, so "
            "identical initial common state implies zero certified deviation"
        )
    elif rho < 1.0:
        reason = (
            "transport is contractive in the declared local model; residual "
            "model defect accumulates to a bounded geometric series"
        )
    else:
        reason = (
            "finite-horizon bound is valid, but the transported target model is "
            "not contractive under the induced 2-norm"
        )

    return FiniteHorizonDeviationCertificate(
        horizon=horizon,
        contraction_factor=rho,
        per_step_model_defect_bound=float(defect),
        initial_error_bound=float(initial_error_bound),
        final_error_bound=float(bounds[-1]),
        trajectory_error_bounds=np.asarray(bounds, dtype=float),
        exact_if_same_initial_state=exact_same_initial,
        reason=reason,
    )
