from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .robust_repairability import PhysicalMapUncertainty, empirical_operator_envelope


@dataclass(frozen=True)
class LocalityUncertaintyBreakdown:
    center: np.ndarray
    stochastic_radius: float
    scale_drift_radius: float
    combined_radius: float


def empirical_locality_envelope(
    fine_map_replicates: np.ndarray,
    coarse_map: np.ndarray,
    *,
    quantile: float = 1.0,
) -> tuple[np.ndarray, PhysicalMapUncertainty, LocalityUncertaintyBreakdown]:
    """Empirical local-map uncertainty from repeatability and probe-scale drift.

    The stochastic term measures repeated fine-probe variation around their
    center. The locality term measures operator-norm drift between that fine
    center and an independently estimated coarser finite-difference map.

    The combined radius is max(stochastic_radius, scale_drift_radius). This is
    an empirical envelope, not a statistical confidence interval or a theorem
    about all unseen states.
    """

    reps = np.asarray(fine_map_replicates, dtype=float)
    coarse = np.asarray(coarse_map, dtype=float)
    center, stochastic = empirical_operator_envelope(reps, quantile=quantile)

    if coarse.shape != center.shape:
        raise ValueError("coarse map must match the fine-map shape")

    scale_drift = float(np.linalg.norm(coarse - center, ord=2))
    combined = float(max(stochastic.epsilon_g, scale_drift))
    breakdown = LocalityUncertaintyBreakdown(
        center=center,
        stochastic_radius=float(stochastic.epsilon_g),
        scale_drift_radius=scale_drift,
        combined_radius=combined,
    )
    return center, PhysicalMapUncertainty(combined), breakdown
