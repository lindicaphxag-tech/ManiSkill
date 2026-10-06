from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import inf

import numpy as np

from .robust_repairability import empirical_operator_envelope


class ScaleLimitStatus(str, Enum):
    CONVERGENCE_SUPPORTED = "CONVERGENCE_SUPPORTED"
    STOCHASTICALLY_UNRESOLVED = "STOCHASTICALLY_UNRESOLVED"
    NONCONTRACTING = "NONCONTRACTING"


@dataclass(frozen=True)
class ScaleLimitCertificate:
    status: ScaleLimitStatus
    center_drifts: tuple[float, ...]
    drift_lower_bounds: tuple[float, ...]
    drift_upper_bounds: tuple[float, ...]
    robust_contraction_lower: tuple[float, ...]
    robust_contraction_upper: tuple[float, ...]
    stochastic_radii: tuple[float, ...]
    q_max: float
    conditional_tail_bound: float | None
    finest_center: np.ndarray
    reason: str


def certify_scale_limit(
    map_replicates_by_scale: list[np.ndarray] | tuple[np.ndarray, ...],
    *,
    q_max: float = 0.75,
    min_contraction_ratios: int = 2,
    quantile: float = 1.0,
    atol: float = 1e-12,
) -> ScaleLimitCertificate:
    """Certify or reject geometric convergence of a local physical map.

    Each entry has shape [n_replicates, physical_dim, support_dim], ordered from
    coarsest to finest physical perturbation scale.

    The certificate separates center-map scale drift from same-scale stochastic
    envelopes.  It does not assume the unobserved scale limit exists unless the
    robust observed contraction ratios support that model.
    """

    if not 0 < q_max < 1:
        raise ValueError("q_max must lie in (0, 1)")
    if min_contraction_ratios < 1:
        raise ValueError("min_contraction_ratios must be >= 1")
    if len(map_replicates_by_scale) < 3:
        raise ValueError("at least three perturbation scales are required")

    centers: list[np.ndarray] = []
    radii: list[float] = []
    expected_shape = None
    for maps in map_replicates_by_scale:
        arr = np.asarray(maps, dtype=float)
        if arr.ndim != 3:
            raise ValueError("each scale must have shape [n,p,s]")
        if expected_shape is None:
            expected_shape = arr.shape[1:]
        elif arr.shape[1:] != expected_shape:
            raise ValueError("all scale maps must share physical/support dimensions")
        center, envelope = empirical_operator_envelope(arr, quantile=quantile)
        centers.append(center)
        radii.append(float(envelope.epsilon_g))

    drifts: list[float] = []
    lower: list[float] = []
    upper: list[float] = []
    for i in range(len(centers) - 1):
        d = float(np.linalg.norm(centers[i] - centers[i + 1], ord=2))
        noise_pair = radii[i] + radii[i + 1]
        drifts.append(d)
        lower.append(max(0.0, d - noise_pair))
        upper.append(d + noise_pair)

    q_lower: list[float] = []
    q_upper: list[float] = []
    for i in range(len(drifts) - 1):
        prev_lo = lower[i]
        prev_hi = upper[i]
        next_lo = lower[i + 1]
        next_hi = upper[i + 1]
        q_lower.append(next_lo / prev_hi if prev_hi > atol else (0.0 if next_lo <= atol else inf))
        q_upper.append(next_hi / prev_lo if prev_lo > atol else (0.0 if next_hi <= atol else inf))

    # Strong rejection: even the most favorable stochastic interpretation
    # cannot make at least one observed ratio contract below q_max.
    if any(q > q_max for q in q_lower):
        return ScaleLimitCertificate(
            status=ScaleLimitStatus.NONCONTRACTING,
            center_drifts=tuple(drifts),
            drift_lower_bounds=tuple(lower),
            drift_upper_bounds=tuple(upper),
            robust_contraction_lower=tuple(q_lower),
            robust_contraction_upper=tuple(q_upper),
            stochastic_radii=tuple(radii),
            q_max=q_max,
            conditional_tail_bound=None,
            finest_center=centers[-1],
            reason=(
                "at least one scale transition remains non-contracting even under "
                "the most favorable same-scale stochastic envelope"
            ),
        )

    if len(q_upper) < min_contraction_ratios or any(not np.isfinite(q) or q > q_max for q in q_upper):
        return ScaleLimitCertificate(
            status=ScaleLimitStatus.STOCHASTICALLY_UNRESOLVED,
            center_drifts=tuple(drifts),
            drift_lower_bounds=tuple(lower),
            drift_upper_bounds=tuple(upper),
            robust_contraction_lower=tuple(q_lower),
            robust_contraction_upper=tuple(q_upper),
            stochastic_radii=tuple(radii),
            q_max=q_max,
            conditional_tail_bound=None,
            finest_center=centers[-1],
            reason=(
                "observed scale contraction is insufficiently separated from "
                "same-scale stochastic uncertainty or too few robust ratios exist"
            ),
        )

    # Conditional tail: if future scale differences continue to contract by at
    # most q_max, the unobserved center-map tail is bounded by the geometric sum.
    last_upper = upper[-1]
    tail = q_max * last_upper / (1.0 - q_max)
    total = float(radii[-1] + tail)

    return ScaleLimitCertificate(
        status=ScaleLimitStatus.CONVERGENCE_SUPPORTED,
        center_drifts=tuple(drifts),
        drift_lower_bounds=tuple(lower),
        drift_upper_bounds=tuple(upper),
        robust_contraction_lower=tuple(q_lower),
        robust_contraction_upper=tuple(q_upper),
        stochastic_radii=tuple(radii),
        q_max=q_max,
        conditional_tail_bound=total,
        finest_center=centers[-1],
        reason=(
            "multiple consecutive scale transitions robustly contract below the "
            "frozen q_max; the reported limit-map radius is conditional on that "
            "contraction continuing to finer unobserved scales"
        ),
    )
