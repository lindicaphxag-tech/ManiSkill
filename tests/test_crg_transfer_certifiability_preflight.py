"""Executable arithmetic and integration regressions for CRG budget preflight.

All outputs are synthetic; no claims about real frozen policy authorization.
"""
import numpy as np
import pytest

from research.crg_core.transfer_certifiability_preflight import (
    inspect_transfer_budget_feasibility,
)
from research.crg_core.active_paired_response_probe import (
    ProbeExecutionStatus,
    execute_directional_probe_budget,
)
from research.crg_core.directional_anytime_probes import inspect_directional_samples


def settings(*, total=128, tolerance=1.0, remainder=0.05, fraction=1.0,
             transfer_only=True, verified=True):
    return dict(
        prespecified_iid_seeds=list(range(1, total // 4 + 1)),
        probe_fraction=fraction,
        trusted_action_lows=[0.0, 0.0],
        trusted_action_highs=[1.0, 1.0],
        locality_remainder_bound=remainder,
        physical_response_tolerance=tolerance,
        familywise_error_budget=0.1,
        max_policy_forward_queries=total,
        independent_seeds_verified=verified,
        controller_bounds_verified=True,
        common_physical_chart_verified=True,
        controller_authority_verified=True,
        transfer_only=transfer_only,
    )


def constant_matching_callback(seed, h, eps):
    return dict(plus_a=[0.7, 0.7], minus_a=[0.3, 0.3],
                plus_b=[0.7, 0.7], minus_b=[0.3, 0.3])


def check(**kw):
    opts = settings(**kw)
    return inspect_transfer_budget_feasibility(
        trusted_action_lows=opts["trusted_action_lows"],
        trusted_action_highs=opts["trusted_action_highs"],
        probe_fraction=opts["probe_fraction"],
        locality_remainder_bound=opts["locality_remainder_bound"],
        physical_response_tolerance=opts["physical_response_tolerance"],
        familywise_error_budget=opts["familywise_error_budget"],
        max_policy_forward_queries=opts["max_policy_forward_queries"],
    )


def test_budget_impossibility_is_a_mathematical_obstruction_not_dissimilarity():
    r = check(total=128)
    assert r.best_seed_pair_count == 32
    assert r.minimum_possible_upper_bound > 1.0
    assert not r.could_ever_authorize_with_budget
    # Even with paired mean exactly ZERO, original confidence radius
    # exceeds the frozen tolerance; no response trace can change this.
    core = inspect_directional_samples(
        np.zeros((32, 2)),
        probe_fraction=1.0,
        action_coordinate_span_a=np.ones(2),
        action_coordinate_span_b=np.ones(2),
        locality_remainder_bound=0.05,
        trusted_response_tolerance=1.0,
        familywise_error_budget=0.1,
        max_seed_pairs=32,
        independent_seeds_verified=True,
        controller_bounds_verified=True,
        common_physical_chart_verified=True,
    )
    assert core.upper_mean_response_gap == pytest.approx(
        r.minimum_possible_upper_bound, abs=1e-12
    )
    assert core.decision.value == "ABSTAIN_QUERY_BUDGET"


def test_transfer_only_impossibility_spends_zero_calls():
    observed = []
    def tracked(seed, h, eps):
        observed.append(seed)
        return constant_matching_callback(seed, h, eps)
    r = execute_directional_probe_budget(
        tracked, [0.1, 0.0], **settings(total=128)
    )
    assert r.status is ProbeExecutionStatus.ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE
    assert r.seeds_attempted == ()
    assert r.charged_policy_forward_queries == 0
    assert observed == []
    assert not r.allows_actual_policy_transfer
    assert not r.independently_validated
    assert not r.deterministic_safety_guarantee
    assert "does NOT mean" in r.reason


def test_mathematically_feasible_budget_still_runs_and_requires_data():
    r = check(total=512)
    assert r.could_ever_authorize_with_budget
    calls = []
    def tracked(seed, h, eps):
        calls.append(seed)
        return constant_matching_callback(seed, h, eps)
    result = execute_directional_probe_budget(
        tracked, [0.1, 0.0], **settings(total=512)
    )
    assert result.status is ProbeExecutionStatus.CONDITIONAL_MEAN_TRANSFER
    assert 0 < result.charged_policy_forward_queries <= 512
    assert result.charged_policy_forward_queries == 4 * len(calls)
    assert not result.deterministic_safety_guarantee


def test_legacy_and_diagnostic_modes_remain_unchanged():
    calls = []
    def tracked(seed, h, eps):
        calls.append(seed)
        return constant_matching_callback(seed, h, eps)
    result = execute_directional_probe_budget(
        tracked, [0.1, 0.0], **settings(total=128, transfer_only=False)
    )
    assert result.status is ProbeExecutionStatus.ABSTAIN_QUERY_BUDGET
    assert result.charged_policy_forward_queries == 128
    assert len(calls) == 32


def test_invalid_authority_is_not_mislabeled_budget_infeasibility():
    calls = []
    def tracked(seed, h, eps):
        calls.append(seed)
        return constant_matching_callback(seed, h, eps)
    result = execute_directional_probe_budget(
        tracked, [0.1, 0.0], **settings(total=128, verified=False)
    )
    assert result.status is ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert calls == []


def test_preflight_more_conservative_with_smaller_eps_or_larger_remainder():
    wide = check(total=128, fraction=1.0)
    narrow = check(total=128, fraction=0.5)
    assert narrow.minimum_possible_upper_bound > wide.minimum_possible_upper_bound
    larger = check(total=128, remainder=0.5)
    assert larger.minimum_possible_upper_bound > wide.minimum_possible_upper_bound


def test_strict_validation_of_untrusted_bounds_and_budget():
    opts = settings()
    bare = {k: opts[k] for k in (
        "trusted_action_lows", "trusted_action_highs", "probe_fraction",
        "locality_remainder_bound", "physical_response_tolerance",
        "familywise_error_budget", "max_policy_forward_queries"
    )}
    with pytest.raises(ValueError, match="hard action range"):
        inspect_transfer_budget_feasibility(**(bare | {
            "trusted_action_highs": [float("nan"), 1.0]
        }))
    with pytest.raises(ValueError, match="multiple of four"):
        inspect_transfer_budget_feasibility(**(bare | {
            "max_policy_forward_queries": 6
        }))
    with pytest.raises(ValueError, match="alpha"):
        inspect_transfer_budget_feasibility(**(bare | {
            "familywise_error_budget": 1.0
        }))
