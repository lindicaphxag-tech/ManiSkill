"""Time-uniform empirical-Bernstein decision for IID paired policy secants.

This is a coordinatewise union-bound adaptation of Maurer-Pontil (2009),
NOT a new concentration theorem. Source:
https://arxiv.org/abs/0907.3740

An independent, trustworthy secant-to-full-request remainder is compulsory.
The statement concerns stochastic MEAN first actions, not rollout or
single-action physical safety.
"""
from __future__ import annotations

from math import isfinite, log, sqrt
import numpy as np

from research.crg_core.directional_anytime_probes import (
    DirectionalDecision, DirectionalResult,
)
from research.crg_core.transfer_certifiability_preflight import (
    TransferCertifiability,
)


def _eb_coordinate_radius(data: np.ndarray, width: np.ndarray, alpha: float) -> np.ndarray:
    """Bessel sample variance + finite-horizon-uniform Maurer-Pontil union."""
    n, d = data.shape
    if n < 2:
        return np.full(d, np.inf, dtype=float)
    # At n, each coordinate has two one-sided bounds. Allocate
    # delta = alpha / (2*d*n*(n+1)) per side. Summing over n>=2
    # gives at most alpha/2 familywise failure (intentionally safe).
    tail_log = log(4.0 * d * n * (n + 1) / alpha)
    sample_var = np.var(data, axis=0, ddof=1)
    return np.sqrt(2.0 * sample_var * tail_log / n) + (
        7.0 * width * tail_log / (3.0 * (n - 1))
    )


def inspect_empirical_bernstein_samples(
    paired_secants: np.ndarray,
    *,
    probe_fraction: float,
    action_coordinate_span_a: np.ndarray,
    action_coordinate_span_b: np.ndarray,
    locality_remainder_bound: float | None,
    trusted_response_tolerance: float,
    familywise_error_budget: float = 0.1,
    max_seed_pairs: int = 16,
    independent_seeds_verified: bool = False,
    controller_bounds_verified: bool = False,
    common_physical_chart_verified: bool = False,
) -> DirectionalResult:
    """Adapt to observed *paired* variance with anytime-valid mean bounds.

    The provided paired secant must originate from actual four-call rounds,
    sharing the same random seed for +/- within each policy. Independent
    draws are needed ACROSS seed pairs. No empirical min/max substitutes
    for physical hard action bounds.
    """
    z = np.asarray(paired_secants, dtype=float)
    n = z.shape[0] if z.ndim >= 1 else 0
    tau, alpha = float(trusted_response_tolerance), float(familywise_error_budget)

    def reject(reason: str) -> DirectionalResult:
        return DirectionalResult(
            DirectionalDecision.REJECT_UNTRUSTED_BOUND, n, 4*n,
            None, None, locality_remainder_bound, None, None,
            tau, alpha,
            "conditional stochastic mean; empirical-Bernstein union, no robot safety proof",
            False, reason,
        )

    if not isfinite(tau) or tau < 0 or not isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("invalid tolerance or familywise error budget")
    if not isinstance(max_seed_pairs, int) or isinstance(max_seed_pairs, bool) or max_seed_pairs < 1:
        raise ValueError("max_seed_pairs must be positive integer")
    if z.ndim != 2 or n < 1 or z.shape[1] < 1 or not np.isfinite(z).all():
        return reject("missing, nonfinite or malformed paired observations")
    if n > max_seed_pairs:
        return reject("more paired observations than frozen budget")
    d = z.shape[1]
    sa, sb = np.asarray(action_coordinate_span_a, dtype=float), np.asarray(action_coordinate_span_b, dtype=float)
    if (sa.shape != (d,) or sb.shape != (d,)
            or not np.isfinite(sa).all() or not np.isfinite(sb).all()
            or np.any(sa <= 0) or np.any(sb <= 0)):
        return reject("invalid independently committed action-coordinate spans")
    eps = float(probe_fraction)
    if not isfinite(eps) or not 0 < eps <= 1:
        return reject("invalid probe fraction")
    if locality_remainder_bound is None:
        return reject("no independent secant-to-full-request remainder")
    remainder = float(locality_remainder_bound)
    if not isfinite(remainder) or remainder < 0:
        return reject("invalid local model remainder")
    if not all(x is True for x in (
        independent_seeds_verified, controller_bounds_verified,
        common_physical_chart_verified,
    )):
        return reject("hard bounds, independent seeds or physical chart unauthenticated")
    width = (sa + sb) / eps
    if not np.isfinite(width).all():
        return reject("secant theoretical range overflow")
    # The signed central secant lies in [-W_j/2,+W_j/2].
    if np.any(np.abs(z) > width / 2.0 + 1e-10):
        return reject("data violates trusted secant support; clipping forbidden")
    center = float(np.linalg.norm(z.mean(axis=0)))
    radius = float(np.linalg.norm(_eb_coordinate_radius(z, width, alpha)))
    if not isfinite(center):
        return reject("nonfinite sample mean")
    if n == 1:
        # Empirical variance requires >=2 draws. Refuse to borrow a zero
        # variance estimate at n=1.
        decision = (DirectionalDecision.ABSTAIN_QUERY_BUDGET if n == max_seed_pairs
                    else DirectionalDecision.CONTINUE_PROBING)
        return DirectionalResult(
            decision, n, 4*n, center, None, remainder, None, None,
            tau, alpha, "empirical-Bernstein unavailable until two independent pairs",
            False, "need at least two independent paired seeds to estimate variance",
        )
    upper = center + radius + remainder
    lower = max(0.0, center - radius - remainder)
    if not all(isfinite(x) for x in (radius, upper, lower)):
        return reject("arithmetic overflow in variance-adaptive bound")
    if upper <= tau:
        decision = DirectionalDecision.CONDITIONAL_SIMILAR_MEAN_RESPONSE
        reason = "variance-adaptive anytime mean certificate, plus independent locality bound"
    elif lower > tau:
        decision = DirectionalDecision.CONDITIONAL_DISTINCT_MEAN_RESPONSE
        reason = "variance-adaptive anytime mean discrepancy exceeds tolerance"
    elif n == max_seed_pairs:
        decision = DirectionalDecision.ABSTAIN_QUERY_BUDGET
        reason = "variance-adaptive confidence insufficient at precommitted query limit"
    else:
        decision = DirectionalDecision.CONTINUE_PROBING
        reason = "acquire another independently seeded paired secant"
    return DirectionalResult(
        decision, n, 4*n, center, radius, remainder,
        lower, upper, tau, alpha,
        "coordinatewise Maurer-Pontil union bound on stochastic mean; not action safety",
        False, reason,
    )


def inspect_eb_transfer_budget_feasibility(
    *,
    trusted_action_lows: np.ndarray,
    trusted_action_highs: np.ndarray,
    probe_fraction: float,
    locality_remainder_bound: float,
    physical_response_tolerance: float,
    familywise_error_budget: float,
    max_policy_forward_queries: int,
) -> TransferCertifiability:
    """Zero-call obstruction for the EB certifier; n>=2, zero sample variance.

    Passing means transfer is *mathematically possible*, not likely.
    An empirical variance bound cannot be made smaller than its additive
    range correction even with identically zero observations.
    """
    low, high = np.asarray(trusted_action_lows, float), np.asarray(trusted_action_highs, float)
    if (not isinstance(max_policy_forward_queries, int)
            or isinstance(max_policy_forward_queries, bool)
            or max_policy_forward_queries < 4 or max_policy_forward_queries % 4):
        raise ValueError("budget must be a positive multiple of four")
    if (low.ndim != 1 or not low.size or high.shape != low.shape
            or not np.isfinite(low).all() or not np.isfinite(high).all()
            or np.any(high <= low)):
        raise ValueError("untrusted controller output interval")
    eps, rem, tau, alpha = map(float, (
        probe_fraction, locality_remainder_bound,
        physical_response_tolerance, familywise_error_budget,
    ))
    if (not all(isfinite(x) for x in (eps, rem, tau, alpha))
            or not 0 < eps <= 1 or rem < 0 or tau < 0 or not 0 < alpha < 1):
        raise ValueError("invalid fixed tolerance, alpha, fraction or locality remainder")
    nmax, d = max_policy_forward_queries // 4, len(low)
    width = 2.0*(high-low)/eps
    width_norm = float(np.linalg.norm(width))
    if not isfinite(width_norm):
        raise ValueError("invalid/overflowed hard secant support")
    best, best_n = float("inf"), 0
    for n in range(2, nmax+1):
        floor = width_norm * (7.0 * log(4.0*d*n*(n+1)/alpha)/(3.0*(n-1))) + rem
        if floor < best:
            best, best_n = floor, n
    # Budget of one seed-pair cannot support an empirical-variance result.
    if nmax < 2:
        return TransferCertifiability(
            False, float("inf"), float("inf"), 0, nmax, tau, rem,
        )
    if not isfinite(best):
        raise ValueError("empirical-Bernstein feasibility arithmetic overflow")
    return TransferCertifiability(
        best <= tau, best, best-rem, best_n, nmax, tau, rem,
    )
