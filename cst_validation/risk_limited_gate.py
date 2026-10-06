from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .closed_loop_transport import ClosedLoopTransportCertificate, LinearClosedLoopModel
from .dominance_gate import model_next


@dataclass(frozen=True)
class ConformalResidualBound:
    """Finite-sample split-conformal upper bound for one-step model residuals.

    The marginal coverage statement requires exchangeability between calibration
    residual scores and the future query score. The state/action box is an
    additional fail-closed deployment guard; it is not a conditional-coverage
    claim.
    """

    alpha: float
    sample_count: int
    order_statistic_rank: int
    residual_quantile: float
    finite: bool
    state_abs_limit: np.ndarray
    action_abs_limit: np.ndarray
    reason: str


@dataclass(frozen=True)
class RiskLimitedDominanceCertificate:
    use_transport: bool
    inside_calibration_domain: bool
    target_action: np.ndarray
    fallback_action: np.ndarray
    predicted_transport_mismatch: float
    predicted_fallback_mismatch: float
    transport_upper_bound: float
    fallback_lower_bound: float
    certified_margin: float
    source_residual_bound: float
    target_residual_bound: float
    familywise_miscoverage_upper_bound: float
    familywise_coverage_lower_bound: float
    required_coverage: float
    finite_sample_resolution_satisfied: bool
    reason: str


def _vector(value, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 1 or out.size == 0 or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be a finite non-empty vector")
    return out


def calibrate_split_conformal_residual(
    model: LinearClosedLoopModel,
    states: np.ndarray,
    actions: np.ndarray,
    observed_next_states: np.ndarray,
    *,
    alpha: float,
) -> ConformalResidualBound:
    """Calibrate a distribution-free marginal upper bound on one-step error.

    For n calibration residuals, the split-conformal order statistic is

        k = ceil((n + 1) * (1 - alpha)).

    If k > n, the requested risk level is not resolvable with the available
    calibration sample size. We return +inf instead of silently weakening the
    requested guarantee.
    """
    states = np.asarray(states, dtype=float)
    actions = np.asarray(actions, dtype=float)
    observed = np.asarray(observed_next_states, dtype=float)
    if states.ndim != 2 or actions.ndim != 2 or observed.ndim != 2:
        raise ValueError("states, actions and observed_next_states must be rank-2")
    if states.shape[0] == 0:
        raise ValueError("calibration set must be non-empty")
    if states.shape[0] != actions.shape[0] or states.shape != observed.shape:
        raise ValueError("calibration arrays have incompatible shapes")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")

    predictions = np.stack(
        [model_next(model, x, u) for x, u in zip(states, actions)]
    )
    residuals = np.linalg.norm(observed - predictions, axis=1)
    if not np.all(np.isfinite(residuals)):
        raise ValueError("calibration residuals must be finite")

    n = int(residuals.size)
    rank = int(np.ceil((n + 1) * (1.0 - alpha)))
    if rank > n:
        quantile = float("inf")
        finite = False
        reason = (
            "requested miscoverage is below the finite-sample resolution; "
            "no finite split-conformal upper bound is certified"
        )
    else:
        quantile = float(np.sort(residuals)[rank - 1])
        finite = True
        reason = "finite split-conformal residual upper bound calibrated"

    return ConformalResidualBound(
        alpha=float(alpha),
        sample_count=n,
        order_statistic_rank=rank,
        residual_quantile=quantile,
        finite=finite,
        state_abs_limit=np.max(np.abs(states), axis=0),
        action_abs_limit=np.max(np.abs(actions), axis=0),
        reason=reason,
    )


def _inside(bound: ConformalResidualBound, state, action) -> bool:
    x = _vector(state, "state")
    u = _vector(action, "action")
    if x.shape != bound.state_abs_limit.shape or u.shape != bound.action_abs_limit.shape:
        raise ValueError("query dimensions differ from calibration domain")
    return bool(
        np.all(np.abs(x) <= bound.state_abs_limit + 1e-15)
        and np.all(np.abs(u) <= bound.action_abs_limit + 1e-15)
    )


def certify_risk_limited_dominance(
    source_model: LinearClosedLoopModel,
    target_model: LinearClosedLoopModel,
    transport: ClosedLoopTransportCertificate,
    *,
    state: np.ndarray,
    source_action: np.ndarray,
    source_residual: ConformalResidualBound,
    target_residual: ConformalResidualBound,
    required_coverage: float,
    fallback_action: np.ndarray | None = None,
) -> RiskLimitedDominanceCertificate:
    """Risk-limit transport-vs-passthrough selection using conformal residuals.

    Three future residual events are needed simultaneously:
      1) source model at the source action,
      2) target model at the adapted action,
      3) target model at the fallback action.

    The same target calibration bound is reused for (2) and (3), but the
    simultaneous statement is protected conservatively with a union bound:

        alpha_family <= alpha_source + 2 * alpha_target.

    No independence assumption is used. The marginal conformal statements still
    require exchangeability for each deployment residual score.
    """
    if not 0.0 < required_coverage < 1.0:
        raise ValueError("required_coverage must lie strictly between 0 and 1")

    x = _vector(state, "state")
    u_src = _vector(source_action, "source_action")
    u_adapt = np.asarray(
        transport.state_gain @ x + transport.action_gain @ u_src,
        dtype=float,
    )
    u_fallback = (
        u_src.copy()
        if fallback_action is None
        else _vector(fallback_action, "fallback_action")
    )

    desired = model_next(source_model, x, u_src)
    adapted = model_next(target_model, x, u_adapt)
    fallback = model_next(target_model, x, u_fallback)

    d_adapt = float(np.linalg.norm(adapted - desired))
    d_fallback = float(np.linalg.norm(fallback - desired))

    alpha_family = min(
        1.0,
        float(source_residual.alpha + 2.0 * target_residual.alpha),
    )
    coverage_lower = max(0.0, 1.0 - alpha_family)
    finite_resolution = bool(source_residual.finite and target_residual.finite)

    inside = bool(
        _inside(source_residual, x, u_src)
        and _inside(target_residual, x, u_adapt)
        and _inside(target_residual, x, u_fallback)
    )

    q_src = float(source_residual.residual_quantile)
    q_tgt = float(target_residual.residual_quantile)
    upper = float(d_adapt + q_src + q_tgt)
    lower = float(max(0.0, d_fallback - q_src - q_tgt))
    margin = float(lower - upper)

    coverage_ok = bool(coverage_lower + 1e-15 >= required_coverage)
    use = bool(
        finite_resolution
        and inside
        and coverage_ok
        and np.isfinite(upper)
        and margin > 0.0
    )

    if not finite_resolution:
        reason = (
            "calibration sample size cannot resolve the requested component risk; "
            "transport is refused"
        )
    elif not inside:
        reason = "query leaves the frozen calibration box; transport is refused"
    elif not coverage_ok:
        reason = (
            "union-bound familywise coverage is below the requested deployment "
            "coverage; transport is refused"
        )
    elif use:
        reason = (
            "at the declared familywise coverage, transported worst-case mismatch "
            "is strictly below fallback best-case mismatch"
        )
    else:
        reason = (
            "risk-limited transport and fallback mismatch intervals overlap; "
            "transport advantage is not certified"
        )

    return RiskLimitedDominanceCertificate(
        use_transport=use,
        inside_calibration_domain=inside,
        target_action=u_adapt,
        fallback_action=u_fallback,
        predicted_transport_mismatch=d_adapt,
        predicted_fallback_mismatch=d_fallback,
        transport_upper_bound=upper,
        fallback_lower_bound=lower,
        certified_margin=margin,
        source_residual_bound=q_src,
        target_residual_bound=q_tgt,
        familywise_miscoverage_upper_bound=alpha_family,
        familywise_coverage_lower_bound=coverage_lower,
        required_coverage=float(required_coverage),
        finite_sample_resolution_satisfied=finite_resolution,
        reason=reason,
    )
