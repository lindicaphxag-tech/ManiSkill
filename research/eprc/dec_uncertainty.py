from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .contract_signature import contract_signature, signature_distance


class ComparisonDecision(str, Enum):
    EQUIVALENT = "EQUIVALENT"
    DIFFERENT = "DIFFERENT"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class DECUncertaintyEstimate:
    center_jacobian: np.ndarray
    replicate_count: int
    q95_signature_radius: float
    median_signature_radius: float
    stable: bool


@dataclass(frozen=True)
class DECComparison:
    decision: ComparisonDecision
    center_distance: float
    combined_uncertainty_radius: float
    lower_separation_bound: float
    upper_equivalence_bound: float
    reason: str


def estimate_dec_uncertainty(
    physical_jacobian_replicates: np.ndarray,
    *,
    min_replicates: int = 5,
    max_q95_radius: float = 0.15,
) -> DECUncertaintyEstimate:
    """Build an empirical DEC uncertainty envelope from repeated intervention assays.

    q95 is an empirical robustness radius, not a formal frequentist confidence
    interval. Replicates should come from independently repeated probe seeds/runs.
    """

    reps = np.asarray(physical_jacobian_replicates, dtype=float)
    if reps.ndim != 3:
        raise ValueError("replicates must have shape [n, physical_dim, support_dim]")
    if reps.shape[0] == 0:
        raise ValueError("at least one replicate is required")

    center = np.mean(reps, axis=0)
    center_sig = contract_signature(center)
    radii = np.asarray(
        [signature_distance(contract_signature(rep), center_sig) for rep in reps],
        dtype=float,
    )
    q95 = float(np.quantile(radii, 0.95, method='higher'))
    median = float(np.median(radii))
    stable = reps.shape[0] >= min_replicates and np.isfinite(q95) and q95 <= max_q95_radius
    return DECUncertaintyEstimate(
        center_jacobian=center,
        replicate_count=int(reps.shape[0]),
        q95_signature_radius=q95,
        median_signature_radius=median,
        stable=bool(stable),
    )


def compare_dec_with_uncertainty(
    a: DECUncertaintyEstimate,
    b: DECUncertaintyEstimate,
    *,
    equivalence_tolerance: float = 0.10,
    difference_tolerance: float = 0.20,
) -> DECComparison:
    """Conservative three-way DEC comparison.

    No equivalence/difference claim is made unless both estimates are stable.
    The uncertainty radii are added to form a worst-case empirical envelope.
    """

    center_distance = signature_distance(
        contract_signature(a.center_jacobian),
        contract_signature(b.center_jacobian),
    )
    radius = a.q95_signature_radius + b.q95_signature_radius
    lower = max(0.0, center_distance - radius)
    upper = center_distance + radius

    if not a.stable or not b.stable:
        return DECComparison(
            decision=ComparisonDecision.INCONCLUSIVE,
            center_distance=center_distance,
            combined_uncertainty_radius=radius,
            lower_separation_bound=lower,
            upper_equivalence_bound=upper,
            reason="one or both DEC estimates fail the replicate-stability gate",
        )

    if upper <= equivalence_tolerance:
        return DECComparison(
            decision=ComparisonDecision.EQUIVALENT,
            center_distance=center_distance,
            combined_uncertainty_radius=radius,
            lower_separation_bound=lower,
            upper_equivalence_bound=upper,
            reason="entire empirical uncertainty envelope lies inside equivalence tolerance",
        )

    if lower >= difference_tolerance:
        return DECComparison(
            decision=ComparisonDecision.DIFFERENT,
            center_distance=center_distance,
            combined_uncertainty_radius=radius,
            lower_separation_bound=lower,
            upper_equivalence_bound=upper,
            reason="entire empirical uncertainty envelope lies beyond difference tolerance",
        )

    return DECComparison(
        decision=ComparisonDecision.INCONCLUSIVE,
        center_distance=center_distance,
        combined_uncertainty_radius=radius,
        lower_separation_bound=lower,
        upper_equivalence_bound=upper,
        reason="uncertainty overlaps the undecided region",
    )