from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class ClosedLoopTransportKind(str, Enum):
    """Local status of source->target executable semantic transport."""

    EXACT = "exact"
    APPROXIMATE = "approximate"
    LOCALLY_UNREPRESENTABLE = "locally_unrepresentable"


@dataclass(frozen=True)
class LocalClosedLoopTransportCertificate:
    """Certificate for a local linear transport between executable effects.

    source_effect and target_effect map native action perturbations into the
    same declared *augmented* one-step observable.  The observable may include
    physical state and controller-owned semantic state; omitting hidden state
    deliberately weakens the claim.

    The synthesized adapter K minimizes the unavoidable residual in the common
    observable:
        target_effect @ K ~= source_effect.
    """

    kind: ClosedLoopTransportKind
    adapter: np.ndarray
    source_effect: np.ndarray
    target_effect: np.ndarray
    reconstructed_source_effect: np.ndarray
    irreducible_residual: np.ndarray
    residual_fro_norm: float
    residual_operator_norm: float
    worst_case_unit_action_lower_bound: float
    source_rank: int
    target_rank: int
    source_image_in_target_residual: float
    exact: bool
    reason: str


@dataclass(frozen=True)
class FiniteHorizonBehaviorCertificate:
    """A finite-horizon deviation bound induced by local transport residuals."""

    horizon: int
    contraction_factor: float
    initial_error: float
    action_norm_bounds: np.ndarray
    model_slack_bounds: np.ndarray
    one_step_transport_gain: float
    error_upper_bounds: np.ndarray
    final_error_upper_bound: float
    asymptotic_error_upper_bound: float | None
    contractive: bool
    reason: str


def _matrix(value: np.ndarray, *, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise ValueError(f"{name} must be a non-empty matrix")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _vector(value: np.ndarray, *, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 1:
        raise ValueError(f"{name} must be a vector")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _rank(matrix: np.ndarray, rtol: float) -> int:
    singular = np.linalg.svd(matrix, compute_uv=False)
    if singular.size == 0:
        return 0
    threshold = rtol * max(float(singular[0]), 1.0)
    return int(np.sum(singular > threshold))


def synthesize_local_closed_loop_transport(
    source_effect: np.ndarray,
    target_effect: np.ndarray,
    *,
    atol: float = 1e-10,
    rtol: float = 1e-10,
    approximate_tolerance: float | None = None,
) -> LocalClosedLoopTransportCertificate:
    """Synthesize the minimum-residual linear adapter in a shared observable.

    Let S map source action perturbations to the declared one-step observable
    and T map target action perturbations to the same observable.  We synthesize

        K = pinv(T) S.

    The residual
        R = S - T K = (I - P_T) S
    is the component of source behavior outside the target executable image.

    For unit-norm source action perturbations, ||R||_2 is an unavoidable local
    worst-case error lower bound for *any* linear adapter.  Therefore a
    non-zero residual is evidence of representational impossibility, not merely
    optimizer failure.
    """
    S = _matrix(source_effect, name="source_effect")
    T = _matrix(target_effect, name="target_effect")
    if S.shape[0] != T.shape[0]:
        raise ValueError("source and target effects must share observable dimension")
    if atol < 0 or rtol <= 0 or not np.isfinite(atol) or not np.isfinite(rtol):
        raise ValueError("invalid tolerances")
    if approximate_tolerance is not None and (
        approximate_tolerance < 0 or not np.isfinite(approximate_tolerance)
    ):
        raise ValueError("approximate_tolerance must be finite and non-negative")

    adapter = np.linalg.pinv(T, rcond=rtol) @ S
    reconstructed = T @ adapter
    residual = S - reconstructed

    residual_fro = float(np.linalg.norm(residual, ord="fro"))
    residual_op = float(np.linalg.norm(residual, ord=2))
    source_scale = max(float(np.linalg.norm(S, ord="fro")), 1.0)
    inclusion_residual = residual_fro / source_scale
    threshold = atol + rtol * max(float(np.linalg.norm(S, ord=2)), 1.0)
    exact = bool(residual_op <= threshold)

    if exact:
        kind = ClosedLoopTransportKind.EXACT
        reason = (
            "the source executable-effect image lies in the target executable image"
        )
    elif approximate_tolerance is not None and residual_op <= approximate_tolerance:
        kind = ClosedLoopTransportKind.APPROXIMATE
        reason = (
            "exact transport is impossible locally, but the irreducible residual "
            "is within the declared approximation tolerance"
        )
    else:
        kind = ClosedLoopTransportKind.LOCALLY_UNREPRESENTABLE
        reason = (
            "the source has an executable-effect component outside the target image; "
            "the reported operator norm is an unavoidable unit-action error lower bound"
        )

    return LocalClosedLoopTransportCertificate(
        kind=kind,
        adapter=adapter,
        source_effect=S,
        target_effect=T,
        reconstructed_source_effect=reconstructed,
        irreducible_residual=residual,
        residual_fro_norm=residual_fro,
        residual_operator_norm=residual_op,
        worst_case_unit_action_lower_bound=residual_op,
        source_rank=_rank(S, rtol),
        target_rank=_rank(T, rtol),
        source_image_in_target_residual=inclusion_residual,
        exact=exact,
        reason=reason,
    )


def certify_finite_horizon_behavior(
    local_certificate: LocalClosedLoopTransportCertificate,
    *,
    contraction_factor: float,
    action_norm_bounds: np.ndarray,
    initial_error: float = 0.0,
    model_slack_bounds: np.ndarray | None = None,
) -> FiniteHorizonBehaviorCertificate:
    """Propagate local transport residual into an H-step behavior bound.

    Assumes an incremental error inequality

        e[t+1] <= rho * e[t] + ||R||_2 * ||u[t]|| + slack[t],

    where R is the irreducible one-step transport residual.  The state whose
    distance is bounded may be an augmented state containing both physical and
    controller-semantic variables, provided the local effects were constructed
    in that same space.
    """
    rho = float(contraction_factor)
    if rho < 0 or not np.isfinite(rho):
        raise ValueError("contraction_factor must be finite and non-negative")
    if initial_error < 0 or not np.isfinite(initial_error):
        raise ValueError("initial_error must be finite and non-negative")

    action_bounds = _vector(action_norm_bounds, name="action_norm_bounds")
    if action_bounds.size == 0:
        raise ValueError("horizon must contain at least one step")
    if np.any(action_bounds < 0):
        raise ValueError("action_norm_bounds must be non-negative")

    if model_slack_bounds is None:
        slack = np.zeros_like(action_bounds)
    else:
        slack = _vector(model_slack_bounds, name="model_slack_bounds")
        if slack.shape != action_bounds.shape:
            raise ValueError("model_slack_bounds must match action_norm_bounds")
        if np.any(slack < 0):
            raise ValueError("model_slack_bounds must be non-negative")

    gain = local_certificate.residual_operator_norm
    errors = np.empty(action_bounds.size + 1, dtype=float)
    errors[0] = float(initial_error)
    for t in range(action_bounds.size):
        errors[t + 1] = rho * errors[t] + gain * action_bounds[t] + slack[t]

    contractive = bool(rho < 1.0)
    if contractive:
        uniform_disturbance = float(np.max(gain * action_bounds + slack))
        asymptotic = uniform_disturbance / (1.0 - rho)
        reason = (
            "finite-horizon bound is contractive; bounded transport/model residual "
            "induces a finite asymptotic error envelope"
        )
    else:
        asymptotic = None
        reason = (
            "finite-horizon bound is valid, but no finite asymptotic envelope is "
            "certified because the declared incremental factor is not contractive"
        )

    return FiniteHorizonBehaviorCertificate(
        horizon=int(action_bounds.size),
        contraction_factor=rho,
        initial_error=float(initial_error),
        action_norm_bounds=action_bounds,
        model_slack_bounds=slack,
        one_step_transport_gain=gain,
        error_upper_bounds=errors,
        final_error_upper_bound=float(errors[-1]),
        asymptotic_error_upper_bound=asymptotic,
        contractive=contractive,
        reason=reason,
    )
