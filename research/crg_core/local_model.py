from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import inf, log

import numpy as np

from .core import empirical_operator_envelope


class LocalModelStatus(str, Enum):
    FIRST_ORDER_ADMISSIBLE = "FIRST_ORDER_ADMISSIBLE"
    STOCHASTICALLY_UNRESOLVED = "STOCHASTICALLY_UNRESOLVED"
    FIRST_ORDER_REJECTED = "FIRST_ORDER_REJECTED"


@dataclass(frozen=True)
class LocalModelAdmissibility:
    status: LocalModelStatus
    coarse_fine_drift: float
    fine_finer_drift: float
    fine_stochastic_radius: float
    finer_stochastic_radius: float
    contraction_ratio: float
    observed_convergence_order: float
    same_scale_queries_authorized: bool
    first_order_crg_authorized: bool
    route: str
    reason: str


def assess_first_order_admissibility(
    *,
    coarse_map: np.ndarray,
    fine_map_replicates: np.ndarray,
    finer_map_replicates: np.ndarray,
    scale_ratio: float = 2.0,
    contraction_threshold: float = 0.75,
    stochastic_dominance_ratio: float = 1.0,
    quantile: float = 1.0,
    atol: float = 1e-12,
) -> LocalModelAdmissibility:
    """Gate first-order CRG on observed locality rather than repeatability alone."""
    if scale_ratio <= 1:
        raise ValueError("scale_ratio must be > 1")
    if contraction_threshold <= 0:
        raise ValueError("contraction_threshold must be positive")
    if stochastic_dominance_ratio < 0:
        raise ValueError("stochastic_dominance_ratio must be nonnegative")

    coarse = np.asarray(coarse_map, dtype=float)
    fine = np.asarray(fine_map_replicates, dtype=float)
    finer = np.asarray(finer_map_replicates, dtype=float)

    if fine.ndim != 3 or finer.ndim != 3 or fine.shape[1:] != finer.shape[1:]:
        raise ValueError("fine/finer replicates must have compatible [n,p,s] shape")
    if coarse.shape != fine.shape[1:]:
        raise ValueError("coarse map shape must match replicate map shape")

    fine_center, fine_noise = empirical_operator_envelope(fine, quantile=quantile)
    finer_center, finer_noise = empirical_operator_envelope(finer, quantile=quantile)

    d1 = float(np.linalg.norm(coarse - fine_center, ord=2))
    d2 = float(np.linalg.norm(fine_center - finer_center, ord=2))

    if d1 <= atol:
        ratio = 0.0 if d2 <= atol else inf
    else:
        ratio = d2 / d1

    if d1 <= atol and d2 <= atol:
        order = inf
    elif d1 <= atol:
        order = -inf
    elif d2 <= atol:
        order = inf
    else:
        order = log(d1 / d2) / log(scale_ratio)

    noise = max(float(fine_noise), float(finer_noise))
    locality_signal = max(d1, d2)

    if noise > atol and locality_signal <= stochastic_dominance_ratio * noise:
        return LocalModelAdmissibility(
            LocalModelStatus.STOCHASTICALLY_UNRESOLVED,
            d1,
            d2,
            float(fine_noise),
            float(finer_noise),
            float(ratio),
            float(order),
            True,
            False,
            "COLLECT_SAME_SCALE_REPLICATES",
            "scale drift is not separated from repeated-probe stochastic variation",
        )

    if ratio <= contraction_threshold:
        return LocalModelAdmissibility(
            LocalModelStatus.FIRST_ORDER_ADMISSIBLE,
            d1,
            d2,
            float(fine_noise),
            float(finer_noise),
            float(ratio),
            float(order),
            False,
            True,
            "FIRST_ORDER_CRG",
            "multi-scale derivative drift contracts beyond the frozen threshold",
        )

    return LocalModelAdmissibility(
        LocalModelStatus.FIRST_ORDER_REJECTED,
        d1,
        d2,
        float(fine_noise),
        float(finer_noise),
        float(ratio),
        float(order),
        False,
        False,
        "REQUERY_OR_RICHER_LOCAL_MODEL",
        "repeatable probes expose non-contracting scale drift; more same-scale samples are not authorized",
    )


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
    """Certify or reject contraction of a local physical map across scales."""
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
        center, radius = empirical_operator_envelope(arr, quantile=quantile)
        centers.append(center)
        radii.append(float(radius))

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
        prev_lo, prev_hi = lower[i], upper[i]
        next_lo, next_hi = lower[i + 1], upper[i + 1]
        q_lower.append(
            next_lo / prev_hi if prev_hi > atol else (0.0 if next_lo <= atol else inf)
        )
        q_upper.append(
            next_hi / prev_lo if prev_lo > atol else (0.0 if next_hi <= atol else inf)
        )

    if any(q > q_max for q in q_lower):
        return ScaleLimitCertificate(
            ScaleLimitStatus.NONCONTRACTING,
            tuple(drifts),
            tuple(lower),
            tuple(upper),
            tuple(q_lower),
            tuple(q_upper),
            tuple(radii),
            q_max,
            None,
            centers[-1],
            "at least one scale transition remains non-contracting under the most favorable stochastic envelope",
        )

    if len(q_upper) < min_contraction_ratios or any(
        (not np.isfinite(q)) or q > q_max for q in q_upper
    ):
        return ScaleLimitCertificate(
            ScaleLimitStatus.STOCHASTICALLY_UNRESOLVED,
            tuple(drifts),
            tuple(lower),
            tuple(upper),
            tuple(q_lower),
            tuple(q_upper),
            tuple(radii),
            q_max,
            None,
            centers[-1],
            "noise envelopes or too few robust transitions prevent a convergence claim",
        )

    last_upper = upper[-1]
    tail = q_max * last_upper / (1.0 - q_max)
    total = float(radii[-1] + tail)
    return ScaleLimitCertificate(
        ScaleLimitStatus.CONVERGENCE_SUPPORTED,
        tuple(drifts),
        tuple(lower),
        tuple(upper),
        tuple(q_lower),
        tuple(q_upper),
        tuple(radii),
        q_max,
        total,
        centers[-1],
        "multiple robust scale transitions contract below q_max; reported tail bound is conditional on continued contraction",
    )
