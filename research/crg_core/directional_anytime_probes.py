"""Anytime-valid sequential local *directional* policy-response screening.

No full Jacobian, solver or held-out/full-request outcome is consumed here.
The mathematical guarantee is only about the mean *central secant*
under IID paired random-seed draws and known precommitted action-coordinate
bounds. A separately trusted nonlinearity envelope is REQUIRED to infer
the unseen full-request response from the central secant.

This is a cautious experimental mechanism, NOT deployed robot safety.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite, log, sqrt
import numpy as np


class DirectionalDecision(str, Enum):
    CONDITIONAL_SIMILAR_MEAN_RESPONSE = "CONDITIONAL_SIMILAR_MEAN_RESPONSE"
    CONDITIONAL_DISTINCT_MEAN_RESPONSE = "CONDITIONAL_DISTINCT_MEAN_RESPONSE"
    CONTINUE_PROBING = "CONTINUE_PROBING"
    ABSTAIN_QUERY_BUDGET = "ABSTAIN_QUERY_BUDGET"
    REJECT_UNTRUSTED_BOUND = "REJECT_UNTRUSTED_BOUND"


@dataclass(frozen=True)
class DirectionalResult:
    decision: DirectionalDecision
    observed_seed_pairs: int
    policy_forward_queries: int
    estimated_mean_directional_gap: float | None
    simultaneous_confidence_radius: float | None
    full_request_locality_remainder: float | None
    lower_mean_response_gap: float | None
    upper_mean_response_gap: float | None
    trusted_response_tolerance: float
    familywise_error_budget: float
    evidence_type: str
    external_validation: bool
    reason: str


def paired_directional_secant(
    plus_a: np.ndarray,
    minus_a: np.ndarray,
    plus_b: np.ndarray,
    minus_b: np.ndarray,
    *,
    probe_fraction: float,
    trusted_action_lows: np.ndarray,
    trusted_action_highs: np.ndarray,
) -> np.ndarray:
    """Return (f_A(+eps h)-f_A(-eps h)-f_B(+eps h)+f_B(-eps h))/(2eps).

    The four arrays must be outputs from identical physical state/perturbation
    charts, with *matched within-policy random seeds*. An experiment runner
    must additionally authenticate those properties; this function cannot.
    Coordinates are REQUIRED to lie in trusted controller action bounds; do
    not silently clip them to manufacture a bounded guarantee.
    """
    eps = float(probe_fraction)
    if not isfinite(eps) or not 0 < eps <= 1:
        raise ValueError("probe_fraction must be in (0,1]")
    arrays = [np.asarray(x, dtype=float) for x in (
        plus_a, minus_a, plus_b, minus_b,
    )]
    low = np.asarray(trusted_action_lows, dtype=float)
    high = np.asarray(trusted_action_highs, dtype=float)
    if low.ndim != 1 or high.shape != low.shape or low.size == 0:
        raise ValueError("trusted physical action bounds dimensions invalid")
    if any(a.ndim != 1 or a.shape != low.shape for a in arrays):
        raise ValueError("policy output coordinates mismatch")
    if not (np.isfinite(low).all() and np.isfinite(high).all() and
            np.all(high > low) and all(np.isfinite(a).all() for a in arrays)):
        raise ValueError("nonfinite or invalid trusted action bounds or responses")
    if any((a < low).any() or (a > high).any() for a in arrays):
        raise ValueError("sample outside trusted action bounds; do NOT silently clip")
    return (arrays[0] - arrays[1] - arrays[2] + arrays[3]) / (2 * eps)


def inspect_directional_samples(
    paired_secants: np.ndarray,
    *,
    probe_fraction: float,
    action_coordinate_span_a: np.ndarray,
    action_coordinate_span_b: np.ndarray,
    locality_remainder_bound: float | None,
    trusted_response_tolerance: float,
    familywise_error_budget: float = 0.10,
    max_seed_pairs: int = 16,
    independent_seeds_verified: bool = False,
    controller_bounds_verified: bool = False,
    common_physical_chart_verified: bool = False,
) -> DirectionalResult:
    """Time-uniform confidence ball and sequential decision.

    Assume independent, identically distributed paired seed draws in a
    fixed physical state and all four action outputs within *a priori*
    coordinate ranges. For output coordinate j, the central secant Z_j has
    support width W_j=(span_Aj+span_Bj)/eps. With alpha/(n(n+1))
    allocated to each inspection n and a union bound over coordinates,
    t_j(n)=W_j*sqrt(log(2*d*n*(n+1)/alpha)/(2*n))
    simultaneously covers all n>=1 with probability >=1-alpha.
    Therefore ||mean(Z)-E Z||_2 <= ||t(n)||_2 anytime-valid.

    The UNKNOWN full-request difference requires an independently validated
    deterministic/valid coverage envelope for the mean secant-to-heldout
    curvature remainder. If unavailable, the caller must reject.
    """

    data = np.asarray(paired_secants, dtype=float)
    n = data.shape[0] if data.ndim >= 1 else 0
    tau = float(trusted_response_tolerance)
    alpha = float(familywise_error_budget)

    def reject(reason):
        return DirectionalResult(
            DirectionalDecision.REJECT_UNTRUSTED_BOUND, n, 4*n,
            None, None, locality_remainder_bound,
            None, None, tau, alpha,
            "conditional mean-response only; no deployment safety proof",
            False, reason,
        )

    if not isfinite(tau) or tau < 0 or not isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("invalid fixed response tolerance or familywise error budget")
    if not isinstance(max_seed_pairs, int) or max_seed_pairs < 1:
        raise ValueError("max_seed_pairs must be a positive integer")
    if data.ndim != 2 or n < 1 or data.shape[1] < 1 or not np.isfinite(data).all():
        return reject("nonfinite/absent paired directional observations")
    if n > max_seed_pairs:
        return reject("more samples than frozen probe budget")
    d = data.shape[1]
    sa = np.asarray(action_coordinate_span_a, dtype=float)
    sb = np.asarray(action_coordinate_span_b, dtype=float)
    if (sa.shape != (d,) or sb.shape != (d,) or
        not (np.isfinite(sa).all() and np.isfinite(sb).all()) or
        (sa <= 0).any() or (sb <= 0).any()):
        return reject("missing or invalid precommitted action coordinate spans")
    eps = float(probe_fraction)
    if not isfinite(eps) or not 0 < eps <= 1:
        return reject("invalid fixed directional probe fraction")
    if locality_remainder_bound is None:
        return reject("no independent secant-to-full-request locality remainder bound")
    remainder = float(locality_remainder_bound)
    if not isfinite(remainder) or remainder < 0:
        return reject("invalid locality bound")
    if not all(x is True for x in (
        independent_seeds_verified, controller_bounds_verified,
        common_physical_chart_verified,
    )):
        return reject("independent seeds, physical chart or bounds not authenticated")

    # Also enforce that submitted secants themselves fit their theoretical
    # ranges. This does NOT replace authenticating the source measurements.
    width = (sa + sb) / eps
    bound = width / 2
    if (np.abs(data) > (bound + 1e-10)).any():
        return reject("observed paired central secant violates trusted bounds")
    mean = data.mean(axis=0)
    center = float(np.linalg.norm(mean))
    radii = width * np.sqrt(np.log(2 * d * n * (n + 1) / alpha) / (2 * n))
    uncertainty = float(np.linalg.norm(radii))
    upper = center + uncertainty + remainder
    lower = max(0.0, center - uncertainty - remainder)
    if not all(isfinite(x) for x in (center, uncertainty, lower, upper)):
        return reject("arithmetic overflow in response interval")

    if upper <= tau:
        status = DirectionalDecision.CONDITIONAL_SIMILAR_MEAN_RESPONSE
        reason = "time-uniform mean secant ball plus independent locality remainder lies within tau"
    elif lower > tau:
        status = DirectionalDecision.CONDITIONAL_DISTINCT_MEAN_RESPONSE
        reason = "time-uniform mean secant ball minus independent locality remainder exceeds tau"
    elif n == max_seed_pairs:
        status = DirectionalDecision.ABSTAIN_QUERY_BUDGET
        reason = "bounded query budget exhausted before separating the tolerance"
    else:
        status = DirectionalDecision.CONTINUE_PROBING
        reason = "collect another independently seeded matched four-query block"

    return DirectionalResult(
        status, n, 4*n, center, uncertainty, remainder,
        lower, upper, tau, alpha,
        "time-uniform conditional stochastic MEAN, not per-run physical safety",
        False, reason,
    )
