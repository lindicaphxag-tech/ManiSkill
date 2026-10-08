"""Request-conditioned interval transfer for two frozen policy local models.

The result is a CONDITIONAL local-linear geometric bound, not a deployment
safety guarantee, a learned model, or externally verified experimental proof.
No frozen 20-case data or thresholds are fitted in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite

import numpy as np


class TransferDecision(str, Enum):
    CERTIFIED_SIMILAR_RESPONSE = "CERTIFIED_SIMILAR_RESPONSE"
    CERTIFIED_DISTINCT_RESPONSE = "CERTIFIED_DISTINCT_RESPONSE"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNSUPPORTED_LOCAL_MODEL = "UNSUPPORTED_LOCAL_MODEL"


@dataclass(frozen=True)
class TransferCertificate:
    decision: TransferDecision
    nominal_response_disagreement: float | None
    uncertainty_radius: float | None
    response_disagreement_lower: float | None
    response_disagreement_upper: float | None
    tolerance: float
    conditional_on_physical_assumptions: bool
    external_empirical_verification: bool
    reason: str


def certify_response_transfer(
    map_a: np.ndarray,
    map_b: np.ndarray,
    physical_perturbation: np.ndarray,
    *,
    operator_bound_a: float,
    operator_bound_b: float,
    locality_remainder_bound_a: float,
    locality_remainder_bound_b: float,
    trusted_response_tolerance: float,
    model_a_admissible: bool,
    model_b_admissible: bool,
    support_admissible: bool,
    controller_authority_admissible: bool,
) -> TransferCertificate:
    """Bound true response disagreement without making new policy queries.

    Assumptions (not established by this function):
        ||G_i - Ghat_i||_2 <= eps_i
        ||response_i(h) - G_i h||_2 <= locality_remainder_i
    for the concrete physical perturbation h, within the same physical
    command chart and valid controller authority. Then triangle inequality:

        center = ||(Ghat_a - Ghat_b)h||
        radius = (eps_a+eps_b)||h|| + remainder_a + remainder_b
        max(0, center-radius) <= ||response_a(h)-response_b(h)||
                              <= center+radius.

    Q95 replicate variability is NOT a proven operator-norm envelope;
    treating sample q95 as eps without extra calibration is unsound.
    """

    def reject(reason: str) -> TransferCertificate:
        return TransferCertificate(
            TransferDecision.UNSUPPORTED_LOCAL_MODEL,
            None, None, None, None,
            float(trusted_response_tolerance),
            False, False, reason,
        )

    scalars = (
        operator_bound_a, operator_bound_b,
        locality_remainder_bound_a, locality_remainder_bound_b,
        trusted_response_tolerance,
    )
    if any(not isfinite(float(x)) or float(x) < 0 for x in scalars):
        return reject("nonfinite or negative trusted physical bounds")
    if any(flag is not True for flag in (
        model_a_admissible, model_b_admissible,
        support_admissible, controller_authority_admissible,
    )):
        return reject("missing locality, support or controller-authority admissibility")

    A = np.asarray(map_a, dtype=float)
    B = np.asarray(map_b, dtype=float)
    h = np.asarray(physical_perturbation, dtype=float)
    if (A.ndim != 2 or B.ndim != 2 or h.ndim != 1 or
        A.shape != B.shape or A.shape[1] != h.size or
        not A.size or h.size == 0):
        return reject("physical response maps or perturbation have incompatible dimensions")
    if not (np.isfinite(A).all() and np.isfinite(B).all() and np.isfinite(h).all()):
        return reject("nonfinite physical map or intervention")

    center = float(np.linalg.norm((A-B) @ h))
    radius = float(
        (operator_bound_a + operator_bound_b) * np.linalg.norm(h)
        + locality_remainder_bound_a + locality_remainder_bound_b
    )
    low = max(0.0, center-radius)
    high = center+radius
    if not all(isfinite(x) for x in (center, radius, low, high)):
        return reject("overflow in local-response bound")

    if high <= trusted_response_tolerance:
        decision = TransferDecision.CERTIFIED_SIMILAR_RESPONSE
        reason = "entire admissible local response interval lies within tolerance"
    elif low > trusted_response_tolerance:
        decision = TransferDecision.CERTIFIED_DISTINCT_RESPONSE
        reason = "even the closest admissible responses exceed tolerance"
    else:
        decision = TransferDecision.INCONCLUSIVE
        reason = "uncertainty crosses the request-conditioned transfer tolerance"

    return TransferCertificate(
        decision, center, radius, low, high,
        float(trusted_response_tolerance), True, False, reason,
    )
