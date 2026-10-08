from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .robust_repairability import PhysicalMapUncertainty, empirical_operator_envelope


@dataclass(frozen=True)
class LocalityRefinementResult:
    coarse_fine_drift: float
    fine_finer_drift: float
    contraction_ratio: float
    contracting: bool
    finer_stochastic_radius: float
    refined_uncertainty_radius: float
    refined_center: np.ndarray
    recommended_trust_radius: float
    reason: str


def evaluate_locality_refinement(
    *,
    coarse_map: np.ndarray,
    fine_map_replicates: np.ndarray,
    finer_map_replicates: np.ndarray,
    contraction_threshold: float = 0.75,
    refined_trust_radius: float = 0.125,
    quantile: float = 1.0,
    atol: float = 1e-12,
) -> tuple[LocalityRefinementResult, PhysicalMapUncertainty]:
    """Prospective multi-scale locality diagnostic.

    This is an empirical gate, not a theorem about unobserved states.

    D1 = ||G_coarse - center(G_fine)||_2
    D2 = ||center(G_fine) - center(G_finer)||_2
    q  = D2 / D1

    If q <= the frozen threshold, the smallest-scale map is allowed to define a
    new *empirical* local model with uncertainty max(stochastic_finer, D2).
    Otherwise the first-order model is rejected for this state.
    """

    if not 0 < contraction_threshold:
        raise ValueError("contraction_threshold must be positive")
    if refined_trust_radius < 0:
        raise ValueError("refined_trust_radius must be nonnegative")

    coarse = np.asarray(coarse_map, dtype=float)
    fine = np.asarray(fine_map_replicates, dtype=float)
    finer = np.asarray(finer_map_replicates, dtype=float)
    if fine.ndim != 3 or finer.ndim != 3 or fine.shape[1:] != finer.shape[1:]:
        raise ValueError("fine/finer replicates must have compatible [n,p,s] shape")
    if coarse.shape != fine.shape[1:]:
        raise ValueError("coarse map shape must match replicate map shape")

    fine_center, _ = empirical_operator_envelope(fine, quantile=quantile)
    finer_center, finer_stochastic = empirical_operator_envelope(
        finer, quantile=quantile
    )

    d1 = float(np.linalg.norm(coarse - fine_center, ord=2))
    d2 = float(np.linalg.norm(fine_center - finer_center, ord=2))

    if d1 <= atol:
        ratio = 0.0 if d2 <= atol else float("inf")
    else:
        ratio = d2 / d1

    contracting = bool(ratio <= contraction_threshold)
    refined_uncertainty = float(max(finer_stochastic.epsilon_g, d2))

    if contracting:
        reason = (
            "observed map drift contracts at the frozen scale ladder; "
            "a smaller empirical first-order trust region may be evaluated"
        )
    else:
        reason = (
            "observed map drift does not contract at the frozen scale ladder; "
            "reject the first-order local model and replan or validate a richer model"
        )

    result = LocalityRefinementResult(
        coarse_fine_drift=d1,
        fine_finer_drift=d2,
        contraction_ratio=float(ratio),
        contracting=contracting,
        finer_stochastic_radius=float(finer_stochastic.epsilon_g),
        refined_uncertainty_radius=refined_uncertainty,
        refined_center=finer_center,
        recommended_trust_radius=float(refined_trust_radius),
        reason=reason,
    )
    return result, PhysicalMapUncertainty(refined_uncertainty)
