"""Live budgeted probe adapter for the EXISTING directional-anytime CRG math.

Adds an actual four-policy-forward-call loop, per-seed source accounting,
preflight admissibility, fail-closed I/O and sequential stop conditions.
All concentration/mean-secant calculations delegate to the existing
directional_anytime_probes module. No duplicated new Hoeffding theorem.

This controls conditional *mean response* decisions only; it does not
certify stochastic single-action or robot collision safety.
The opt-in transfer-only mode can refuse to spend queries when the existing
certificate is mathematically impossible at the frozen budget.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Callable, Mapping, Sequence

import numpy as np

from research.crg_core.directional_anytime_probes import (
    DirectionalDecision,
    DirectionalResult,
    inspect_directional_samples,
    paired_directional_secant,
)


class ProbeExecutionStatus(str, Enum):
    CONDITIONAL_MEAN_TRANSFER = "CONDITIONAL_MEAN_TRANSFER"
    DO_NOT_TRANSFER_DISTINCT = "DO_NOT_TRANSFER_DISTINCT"
    ABSTAIN_QUERY_BUDGET = "ABSTAIN_QUERY_BUDGET"
    ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE = "ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE"
    REJECT_UNSUPPORTED_ASSUMPTIONS = "REJECT_UNSUPPORTED_ASSUMPTIONS"


@dataclass(frozen=True)
class ProbeExecution:
    status: ProbeExecutionStatus
    seeds_attempted: tuple[int, ...]
    charged_policy_forward_queries: int
    max_policy_forward_queries: int
    latest_diagnostic: DirectionalResult | None
    allows_actual_policy_transfer: bool
    independently_validated: bool
    deterministic_safety_guarantee: bool
    reason: str


def execute_directional_probe_budget(
    query_paired_plus_minus_actions: Callable[
        [int, np.ndarray, float], Mapping[str, Sequence[float]]
    ],
    physical_direction: Sequence[float],
    *,
    prespecified_iid_seeds: Sequence[int],
    probe_fraction: float,
    trusted_action_lows: Sequence[float],
    trusted_action_highs: Sequence[float],
    locality_remainder_bound: float | None,
    physical_response_tolerance: float,
    familywise_error_budget: float,
    max_policy_forward_queries: int,
    independent_seeds_verified: bool,
    controller_bounds_verified: bool,
    common_physical_chart_verified: bool,
    controller_authority_verified: bool,
    transfer_only: bool = False,
    confidence_method: str = "hoeffding",
) -> ProbeExecution:
    """Execute four forward passes for each paired seed and stop on evidence.

    One callback invocation must return four first physical actions at
    (+fraction*h,-fraction*h) for policy A and B, same frozen state,
    within-policy RNG seed held constant for +/- requests. The callback
    must not inspect hidden true held-out outcomes. The adapter cannot
    authenticate these external facts; all provenance flags are required.

    A separate independently trusted secant-to-target locality remainder
    is mandatory; missing it means zero queries and no transfer.

    Executed counts conservatively CHARGE four calls for an attempted seed
    even if a callback fails and its actual forward count is unknown.
    Real policy wrappers must additionally log actual model calls.
    """
    if confidence_method not in ("hoeffding", "empirical_bernstein"):
        raise ValueError("confidence_method must be hoeffding or empirical_bernstein")
    if not isinstance(max_policy_forward_queries, int) or max_policy_forward_queries < 4 or max_policy_forward_queries % 4:
        raise ValueError("fixed policy forward-query budget must be a positive multiple of four")
    if not isfinite(float(physical_response_tolerance)) or physical_response_tolerance < 0:
        raise ValueError("physical response tolerance must be finite and nonnegative")
    if not isfinite(float(familywise_error_budget)) or not 0 < familywise_error_budget < 1:
        raise ValueError("invalid familywise confidence budget")
    max_pairs = max_policy_forward_queries // 4
    seeds = tuple(prespecified_iid_seeds)
    if len(seeds) != max_pairs or len(set(seeds)) != len(seeds) or any(
        isinstance(s, bool) or not isinstance(s, int) or s < 0 for s in seeds
    ):
        raise ValueError("require exactly one distinct precommitted RNG seed per probe round")

    def finish(status, attempted, latest, reason) -> ProbeExecution:
        return ProbeExecution(
            status, tuple(attempted), 4 * len(attempted),
            max_policy_forward_queries, latest,
            status is ProbeExecutionStatus.CONDITIONAL_MEAN_TRANSFER,
            False, False, reason,
        )

    h = np.asarray(physical_direction, dtype=float)
    low = np.asarray(trusted_action_lows, dtype=float)
    high = np.asarray(trusted_action_highs, dtype=float)
    if (h.ndim != 1 or not h.size or not np.isfinite(h).all()
        or low.ndim != 1 or high.shape != low.shape or not low.size
        or not (np.isfinite(low).all() and np.isfinite(high).all())
        or not np.all(high > low) or not isfinite(float(probe_fraction))
        or not 0 < probe_fraction <= 1):
        return finish(ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS, (), None,
                      "physical perturbation, action bounds or probe fraction invalid")
    if (locality_remainder_bound is None or
        not isfinite(float(locality_remainder_bound)) or locality_remainder_bound < 0 or
        not all(x is True for x in (
            independent_seeds_verified, controller_bounds_verified,
            common_physical_chart_verified, controller_authority_verified,
        ))):
        return finish(ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS, (), None,
                      "independent seeds, physical bounds, authority or locality envelope not established")

    # Only transfer authorization is useful in this optional mode.
    # When even a zero mean cannot overcome the worst-case confidence radius,
    # no sequence of observations could authorize, so spend ZERO queries.
    # Do not apply this optimization when distinct-response diagnosis matters.
    if transfer_only:
        if confidence_method == "hoeffding":
            from research.crg_core.transfer_certifiability_preflight import (
                inspect_transfer_budget_feasibility as check_feasibility,
            )
        else:
            from research.crg_core.variance_adaptive_paired_response import (
                inspect_eb_transfer_budget_feasibility as check_feasibility,
            )

        preflight = check_feasibility(
            trusted_action_lows=low,
            trusted_action_highs=high,
            probe_fraction=probe_fraction,
            locality_remainder_bound=locality_remainder_bound,
            physical_response_tolerance=physical_response_tolerance,
            familywise_error_budget=familywise_error_budget,
            max_policy_forward_queries=max_policy_forward_queries,
        )
        if not preflight.could_ever_authorize_with_budget:
            return finish(
                ProbeExecutionStatus.ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE,
                (), None,
                "no stochastic mean data can authorize transfer within the "
                f"fixed budget: best-case confidence upper bound "
                f"{preflight.minimum_possible_upper_bound:.9g} exceeds "
                f"tolerance {physical_response_tolerance:.9g}; "
                "this does NOT mean the policies are dissimilar",
            )

    secants = []
    attempted = []
    latest = None
    for seed in seeds:
        attempted.append(seed)  # count full round even if callback aborts mid-way
        try:
            obs = query_paired_plus_minus_actions(seed, h.copy(), probe_fraction)
            if not isinstance(obs, Mapping) or set(obs) != {
                "plus_a", "minus_a", "plus_b", "minus_b"
            }:
                raise ValueError("callback must return the four named policy first actions")
            z = paired_directional_secant(
                np.asarray(obs["plus_a"], dtype=float),
                np.asarray(obs["minus_a"], dtype=float),
                np.asarray(obs["plus_b"], dtype=float),
                np.asarray(obs["minus_b"], dtype=float),
                probe_fraction=probe_fraction,
                trusted_action_lows=low,
                trusted_action_highs=high,
            )
        except (ValueError, TypeError, KeyError) as error:
            return finish(ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS,
                          attempted, None, f"paired probe invalid: {error}")
        secants.append(z)
        if confidence_method == "hoeffding":
            inspector = inspect_directional_samples
        else:
            from research.crg_core.variance_adaptive_paired_response import (
                inspect_empirical_bernstein_samples,
            )
            inspector = inspect_empirical_bernstein_samples
        latest = inspector(
            np.asarray(secants),
            probe_fraction=probe_fraction,
            action_coordinate_span_a=high-low,
            action_coordinate_span_b=high-low,
            locality_remainder_bound=locality_remainder_bound,
            trusted_response_tolerance=physical_response_tolerance,
            familywise_error_budget=familywise_error_budget,
            max_seed_pairs=max_pairs,
            independent_seeds_verified=True,
            controller_bounds_verified=True,
            common_physical_chart_verified=True,
        )
        if latest.decision is DirectionalDecision.CONDITIONAL_SIMILAR_MEAN_RESPONSE:
            return finish(ProbeExecutionStatus.CONDITIONAL_MEAN_TRANSFER,
                          attempted, latest,
                          "conditional stochastic mean response similar; not single-action safety")
        if latest.decision is DirectionalDecision.CONDITIONAL_DISTINCT_MEAN_RESPONSE:
            return finish(ProbeExecutionStatus.DO_NOT_TRANSFER_DISTINCT,
                          attempted, latest, "mean policy responses distinct: refuse transfer")
        if latest.decision is DirectionalDecision.REJECT_UNTRUSTED_BOUND:
            return finish(ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS,
                          attempted, latest, latest.reason)
    if latest is None or latest.decision is not DirectionalDecision.ABSTAIN_QUERY_BUDGET:
        raise AssertionError("budget exhaustion must end in the core's abstention status")
    return finish(ProbeExecutionStatus.ABSTAIN_QUERY_BUDGET,
                  attempted, latest, "insufficient evidence within prespecified query budget")
