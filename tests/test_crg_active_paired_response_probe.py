"""The adapter's regression tests are synthetic, NOT frozen policy validation."""
import numpy as np
import pytest

from research.crg_core.active_paired_response_probe import (
    ProbeExecutionStatus,
    execute_directional_probe_budget,
)


def sampler(*, contrast=0.0, common_random_amplitude=0.0):
    def fn(seed, direction, fraction):
        a_noise = ((seed*17)%23 / 23 - .5) * common_random_amplitude
        b_noise = ((seed*13)%19 / 19 - .5) * common_random_amplitude
        # Per-policy paired '+'/'-' action queries share the SAME noise.
        # Contrast is the two POLICY central secants' difference.
        return {
            "plus_a": [.02 + contrast/4 + a_noise],
            "minus_a": [-.02 - contrast/4 + a_noise],
            "plus_b": [.02 - contrast/4 + b_noise],
            "minus_b": [-.02 + contrast/4 + b_noise],
        }
    return fn


def run(f, *, total=128, tau=.30, remainder=.005, verified=True):
    return execute_directional_probe_budget(
        f,[1.0],
        prespecified_iid_seeds=list(range(1, total//4+1)),
        probe_fraction=1.0,
        trusted_action_lows=[-.1],
        trusted_action_highs=[.1],
        locality_remainder_bound=remainder,
        physical_response_tolerance=tau,
        familywise_error_budget=.1,
        max_policy_forward_queries=total,
        independent_seeds_verified=verified,
        controller_bounds_verified=True,
        common_physical_chart_verified=True,
        controller_authority_verified=True,
    )


def test_adapter_executes_four_queries_per_seed_and_stops_early():
    result=run(sampler(common_random_amplitude=.01),tau=.30)
    assert result.status is ProbeExecutionStatus.CONDITIONAL_MEAN_TRANSFER
    assert result.allows_actual_policy_transfer
    assert 0 < result.charged_policy_forward_queries < 128
    assert result.charged_policy_forward_queries % 4 == 0
    assert result.latest_diagnostic.upper_mean_response_gap <= .30
    assert len(result.seeds_attempted) == result.charged_policy_forward_queries//4
    assert not result.independently_validated
    assert not result.deterministic_safety_guarantee


def test_confirming_distinct_means_prevents_transfer():
    result=run(sampler(contrast=.16),total=1024,tau=.02,remainder=0)
    assert result.status is ProbeExecutionStatus.DO_NOT_TRANSFER_DISTINCT
    assert not result.allows_actual_policy_transfer
    assert result.latest_diagnostic.lower_mean_response_gap > .02
    assert result.charged_policy_forward_queries <= 1024


def test_insufficient_query_budget_abstains():
    result=run(sampler(contrast=.16),total=8,tau=.02,remainder=0)
    assert result.status is ProbeExecutionStatus.ABSTAIN_QUERY_BUDGET
    assert result.charged_policy_forward_queries == 8
    assert not result.allows_actual_policy_transfer


def test_missing_provenance_and_locality_evidence_rejects_before_any_policy_call():
    calls = []
    def tracked(seed,h,eps):
        calls.append(seed)
        return sampler()(seed,h,eps)
    assert run(tracked,verified=False).status is ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert run(tracked,remainder=None).status is ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert calls == []


def test_no_untrusted_action_clipping_and_conservative_budget_accounting():
    def outside(seed,h,eps):
        return {"plus_a":[.2],"minus_a":[-.02],
                "plus_b":[0.],"minus_b":[0.]}
    r=run(outside)
    assert r.status is ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert r.charged_policy_forward_queries == 4
    assert r.seeds_attempted == (1,)
    assert not r.allows_actual_policy_transfer


def test_missing_fields_and_nan_never_authorize():
    def incomplete(seed,h,eps):
        return {"plus_a":[0.],"minus_a":[0.],"plus_b":[0.]}
    assert run(incomplete).status is ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert run(incomplete).charged_policy_forward_queries == 4
    def invalid(seed,h,eps):
        x=sampler()(seed,h,eps)
        x["plus_a"]=[float("nan")]
        return x
    assert run(invalid).status is ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS


def test_frozen_query_budget_and_unique_seed_schedule():
    with pytest.raises(ValueError,match="multiple of four"):
        run(sampler(),total=5)
    with pytest.raises(ValueError,match="distinct"):
        execute_directional_probe_budget(
            sampler(),[1.0],
            prespecified_iid_seeds=[1,1],
            probe_fraction=1.0,
            trusted_action_lows=[-.1], trusted_action_highs=[.1],
            locality_remainder_bound=0.,
            physical_response_tolerance=.2,
            familywise_error_budget=.1,
            max_policy_forward_queries=8,
            independent_seeds_verified=True,
            controller_bounds_verified=True,
            common_physical_chart_verified=True,
            controller_authority_verified=True,
        )


def test_matched_noise_cancels_only_in_the_synthetic_mechanism():
    a=run(sampler(common_random_amplitude=.01),total=32,tau=.01)
    b=run(sampler(common_random_amplitude=0),total=32,tau=.01)
    assert a.latest_diagnostic.estimated_mean_directional_gap == (
        b.latest_diagnostic.estimated_mean_directional_gap
    )
    assert not a.allows_actual_policy_transfer
