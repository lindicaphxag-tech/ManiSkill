from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .closed_loop_transport import ClosedLoopTransportCertificate, LinearClosedLoopModel
from .dominance_gate import model_next


@dataclass(frozen=True)
class EpisodeMaxResidualBound:
    """Split-conformal bound on the maximum residual over a whole episode.

    Each calibration episode is one exchangeable object. Its score is the
    maximum residual over every predeclared model-query event in that episode.
    Therefore, when calibration episodes and the future deployment episode are
    exchangeable and the event-scoring rule is frozen before calibration, the
    conformal statement applies to the *episode maximum*, not to individually
    assumed exchangeable time steps.
    """

    alpha: float
    episode_count: int
    order_statistic_rank: int
    max_residual_quantile: float
    finite: bool
    min_events_per_episode: int
    max_events_per_episode: int
    reason: str


@dataclass(frozen=True)
class EpisodeRiskDominanceCertificate:
    use_transport: bool
    target_action: np.ndarray
    fallback_action: np.ndarray
    predicted_transport_mismatch: float
    predicted_fallback_mismatch: float
    transport_upper_bound: float
    fallback_lower_bound: float
    certified_margin: float
    episode_residual_bound: float
    episode_miscoverage: float
    episode_coverage_lower_bound: float
    required_episode_coverage: float
    finite_sample_resolution_satisfied: bool
    reason: str


def _episode_score(values: np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size == 0 or not np.all(np.isfinite(arr)):
        raise ValueError("each episode residual vector must be finite and non-empty")
    if np.any(arr < 0.0):
        raise ValueError("residuals must be non-negative")
    return float(np.max(arr))


def calibrate_episode_max_residual(
    episode_residuals: Sequence[np.ndarray],
    *,
    alpha: float,
) -> EpisodeMaxResidualBound:
    """Calibrate a finite-sample bound for the maximum residual of a new episode.

    The score for episode i is

        S_i = max_j r_{i,j},

    where j ranges over the complete, predeclared family of residual events
    that may be used by the deployment rule (for example source-model,
    adapted-target, and fallback-target residuals at every step).

    Split conformal is then applied across episode scores rather than across
    adaptively selected time steps.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    if len(episode_residuals) == 0:
        raise ValueError("at least one calibration episode is required")

    scores = []
    event_counts = []
    for residuals in episode_residuals:
        arr = np.asarray(residuals, dtype=float)
        scores.append(_episode_score(arr))
        event_counts.append(int(arr.size))

    n = len(scores)
    rank = int(np.ceil((n + 1) * (1.0 - alpha)))
    if rank > n:
        q = float("inf")
        finite = False
        reason = (
            "requested episode miscoverage is below the finite-sample resolution; "
            "no finite trajectory-level conformal bound is certified"
        )
    else:
        q = float(np.sort(np.asarray(scores))[rank - 1])
        finite = True
        reason = (
            "finite split-conformal bound calibrated on exchangeable episode-max scores"
        )

    return EpisodeMaxResidualBound(
        alpha=float(alpha),
        episode_count=n,
        order_statistic_rank=rank,
        max_residual_quantile=q,
        finite=finite,
        min_events_per_episode=min(event_counts),
        max_events_per_episode=max(event_counts),
        reason=reason,
    )


def collect_episode_event_residuals(
    model: LinearClosedLoopModel,
    states: np.ndarray,
    actions: np.ndarray,
    observed_next_states: np.ndarray,
) -> np.ndarray:
    """Return one residual event per transition for episode-level scoring."""
    states = np.asarray(states, dtype=float)
    actions = np.asarray(actions, dtype=float)
    observed = np.asarray(observed_next_states, dtype=float)
    if states.ndim != 2 or actions.ndim != 2 or observed.ndim != 2:
        raise ValueError("states, actions and observed_next_states must be rank-2")
    if states.shape[0] != actions.shape[0] or states.shape != observed.shape:
        raise ValueError("episode arrays have incompatible shapes")
    if states.shape[0] == 0:
        raise ValueError("episode must contain at least one transition")
    predicted = np.stack([model_next(model, x, u) for x, u in zip(states, actions)])
    return np.linalg.norm(observed - predicted, axis=1)


def combine_episode_event_families(*families: np.ndarray) -> np.ndarray:
    """Combine all residual events that the frozen deployment rule may query.

    A single episode-max conformal score can cover this whole declared family
    without a per-time-step union bound, provided the same family construction
    is used for calibration and the future exchangeable episode.
    """
    if len(families) == 0:
        raise ValueError("at least one event family is required")
    arrays = []
    for family in families:
        arr = np.asarray(family, dtype=float)
        if arr.ndim != 1 or arr.size == 0 or not np.all(np.isfinite(arr)):
            raise ValueError("event families must be finite non-empty vectors")
        if np.any(arr < 0.0):
            raise ValueError("residuals must be non-negative")
        arrays.append(arr)
    return np.concatenate(arrays)


def certify_episode_risk_dominance(
    source_model: LinearClosedLoopModel,
    target_model: LinearClosedLoopModel,
    transport: ClosedLoopTransportCertificate,
    *,
    state: np.ndarray,
    source_action: np.ndarray,
    episode_residual: EpisodeMaxResidualBound,
    required_episode_coverage: float,
    fallback_action: np.ndarray | None = None,
) -> EpisodeRiskDominanceCertificate:
    """Select transport only if it dominates fallback under an episode-max bound.

    The single residual radius q is assumed to cover every residual event in the
    frozen episode event family simultaneously. At one deployment decision,
    both the desired source next-state model and either target candidate can
    therefore deviate by at most q on the covered event, giving +/-2q mismatch
    intervals.

    This is an episode-marginal statement under exchangeability of episodes. It
    is not a conditional guarantee for arbitrary distribution shift.
    """
    if not 0.0 < required_episode_coverage < 1.0:
        raise ValueError("required_episode_coverage must lie strictly between 0 and 1")

    x = np.asarray(state, dtype=float)
    u_src = np.asarray(source_action, dtype=float)
    if x.ndim != 1 or u_src.ndim != 1:
        raise ValueError("state and source_action must be vectors")

    u_adapt = np.asarray(
        transport.state_gain @ x + transport.action_gain @ u_src,
        dtype=float,
    )
    u_fallback = (
        u_src.copy()
        if fallback_action is None
        else np.asarray(fallback_action, dtype=float)
    )

    desired = model_next(source_model, x, u_src)
    adapted = model_next(target_model, x, u_adapt)
    fallback = model_next(target_model, x, u_fallback)
    d_adapt = float(np.linalg.norm(adapted - desired))
    d_fallback = float(np.linalg.norm(fallback - desired))

    q = float(episode_residual.max_residual_quantile)
    upper = float(d_adapt + 2.0 * q)
    lower = float(max(0.0, d_fallback - 2.0 * q))
    margin = float(lower - upper)
    coverage_lower = float(1.0 - episode_residual.alpha)
    coverage_ok = coverage_lower + 1e-15 >= required_episode_coverage
    use = bool(
        episode_residual.finite
        and coverage_ok
        and np.isfinite(upper)
        and margin > 0.0
    )

    if not episode_residual.finite:
        reason = (
            "episode calibration count cannot resolve the requested risk; "
            "transport is refused"
        )
    elif not coverage_ok:
        reason = (
            "episode-level conformal coverage is below the requested deployment "
            "coverage; transport is refused"
        )
    elif use:
        reason = (
            "under the frozen episode-max residual certificate, transported "
            "mismatch is strictly separated from fallback mismatch"
        )
    else:
        reason = (
            "episode-risk mismatch intervals overlap; transport advantage is "
            "not certified"
        )

    return EpisodeRiskDominanceCertificate(
        use_transport=use,
        target_action=u_adapt,
        fallback_action=u_fallback,
        predicted_transport_mismatch=d_adapt,
        predicted_fallback_mismatch=d_fallback,
        transport_upper_bound=upper,
        fallback_lower_bound=lower,
        certified_margin=margin,
        episode_residual_bound=q,
        episode_miscoverage=float(episode_residual.alpha),
        episode_coverage_lower_bound=coverage_lower,
        required_episode_coverage=float(required_episode_coverage),
        finite_sample_resolution_satisfied=episode_residual.finite,
        reason=reason,
    )
