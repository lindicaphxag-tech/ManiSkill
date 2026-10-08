"""Pre-query feasibility of the existing CRG time-uniform transfer certificate.

Pure arithmetic on precommitted hard action ranges and query limits.  The
minimum possible upper bound, even for an exactly zero observed mean, is
the time-uniform radius plus the separately trusted locality remainder.

This is a *certificate-feasibility* check, NOT a claim about the underlying
policy responses, transfer accuracy, or physical safety.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, sqrt
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class TransferCertifiability:
    could_ever_authorize_with_budget: bool
    minimum_possible_upper_bound: float
    least_statistical_radius: float
    best_seed_pair_count: int
    max_seed_pairs: int
    precommitted_tolerance: float
    locality_remainder: float


def inspect_transfer_budget_feasibility(
    *,
    trusted_action_lows: Sequence[float],
    trusted_action_highs: Sequence[float],
    probe_fraction: float,
    locality_remainder_bound: float,
    physical_response_tolerance: float,
    familywise_error_budget: float,
    max_policy_forward_queries: int,
) -> TransferCertifiability:
    """Check whether the ORIGINAL CRG certificate could ever license transfer.

    Exactly matches inspect_directional_samples' coordinatewise Hoeffding
    radius for the adapter's common A/B hard action bounds:

      W_j = 2 * (high_j - low_j) / probe_fraction
      r(n) = ||W||_2 * sqrt(log(2*d*n*(n+1)/alpha) / (2*n))

    A transfer is permitted only if ||sample mean||_2 + r(n) + L <= tau.
    Since ||sample mean||_2 >= 0, no observed policy data can produce a
    transfer certificate when min_{1<=n<=N}(r(n)+L) > tau.

    The converse is NOT true: passing this feasibility check does not imply
    the actual policies will be certifiable. It also does NOT rule out
    a statistically distinct response (a nontransfer decision).
    """
    if (not isinstance(max_policy_forward_queries, int)
            or isinstance(max_policy_forward_queries, bool)
            or max_policy_forward_queries < 4
            or max_policy_forward_queries % 4):
        raise ValueError("budget must be a positive multiple of four")
    a = np.asarray(trusted_action_lows, dtype=float)
    b = np.asarray(trusted_action_highs, dtype=float)
    if (a.ndim != 1 or not a.size or b.shape != a.shape
            or not np.isfinite(a).all() or not np.isfinite(b).all()
            or not np.all(b > a)):
        raise ValueError("invalid independently trusted hard action range")
    eps, rem, tau, alpha = (float(probe_fraction),
                            float(locality_remainder_bound),
                            float(physical_response_tolerance),
                            float(familywise_error_budget))
    if (not all(isfinite(x) for x in (eps, rem, tau, alpha))
            or not 0 < eps <= 1 or rem < 0 or tau < 0
            or not 0 < alpha < 1):
        raise ValueError("invalid precommitted probe fraction, remainder, tolerance or alpha")

    width = 2.0 * (b - a) / eps
    width_norm = float(np.linalg.norm(width))
    if not isfinite(width_norm):
        raise ValueError("unbounded or overflowed theoretical secant support")
    d = len(a)
    N = max_policy_forward_queries // 4
    best_n = 0
    best_radius = float("inf")
    # Scan the finite prespecified inspection budget; do not assume
    # the time-uniform radius is monotone for an arbitrary boundary case.
    for n in range(1, N + 1):
        radius = width_norm * sqrt(log(2.0 * d * n * (n + 1) / alpha) / (2 * n))
        if radius < best_radius:
            best_n, best_radius = n, radius
    floor = best_radius + rem
    if not isfinite(floor):
        raise ValueError("certificate lower envelope overflow")
    return TransferCertifiability(
        could_ever_authorize_with_budget=(floor <= tau),
        minimum_possible_upper_bound=floor,
        least_statistical_radius=best_radius,
        best_seed_pair_count=best_n,
        max_seed_pairs=N,
        precommitted_tolerance=tau,
        locality_remainder=rem,
    )
