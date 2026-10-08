"""CPU-only synthetic mechanism tests; no measured real-policy improvement."""
import numpy as np
import pytest

from research.crg_core.active_paired_response_probe import (
    ResponseProbeDecision,
    probe_pairwise_mean_response,
)


def query(*, gap=0.0, noise=0.0):
    def fn(seed, h):
        # Same RNG noise in baseline and perturbed inputs, separately
        # within each policy. Matched-noise finite contrast is known.
        z = (seed % 101) / 100 * noise
        return {
            "baseline_a": [z, -z],
            "perturbed_a": [z + float(h[0]), -z],
            "baseline_b": [3*z, 2*z],
            "perturbed_b": [3*z + float(h[0]) - gap, 2*z],
        }
    return fn


def run(f, *, max_queries=64, B=.04, tau=.20, aligned=True, attested=True):
    return probe_pairwise_mean_response(
        f, [1.0], prespecified_iid_seed_draws=list(range(1, max_queries//4+1)),
        hard_coordinate_contrast_bound=B,
        max_policy_queries=max_queries,
        response_tolerance=tau,
        alpha=0.1,
        physical_charts_aligned=aligned,
        controller_authority_valid=True,
        population_bound_independently_justified=attested,
        iid_seed_draw_design_attested=True,
    )


def test_paired_query_stops_early_for_compatible_mean_responses():
    result = run(query(gap=0, noise=4), B=.04)
    assert result.decision is ResponseProbeDecision.STATISTICAL_MEAN_SIMILAR
    assert result.total_policy_queries < 64
    assert result.total_policy_queries % 4 == 0
    assert result.final_mean_gap_upper <= result.response_tolerance
    assert len(result.rounds) == result.total_policy_queries//4
    assert not result.deterministic_safety_guarantee
    assert not result.externally_validated


def test_distinct_mean_responses_can_be_detected_with_enough_budget():
    result = run(query(gap=.18), max_queries=512, B=.2, tau=.02)
    assert result.decision is ResponseProbeDecision.STATISTICAL_MEAN_DISTINCT
    assert result.final_mean_gap_lower > .02
    assert result.total_policy_queries <= 512


def test_small_budget_abstains_without_relaxing_confidence():
    result = run(query(gap=.18), max_queries=4, B=.2, tau=.02)
    assert result.decision is ResponseProbeDecision.ABSTAIN_BUDGET_EXHAUSTED
    assert result.total_policy_queries == 4
    assert result.final_mean_gap_lower <= .02 <= result.final_mean_gap_upper


def test_no_independent_support_bound_or_controller_permission_means_zero_calls():
    calls = []
    def traced(seed, h):
        calls.append(seed)
        return query()(seed,h)
    for kw in (dict(attested=False), dict(aligned=False), dict(B=None)):
        out = run(traced, **kw)
        assert out.decision is ResponseProbeDecision.REJECT_UNSUPPORTED_ASSUMPTIONS
        assert out.total_policy_queries == 0
    assert calls == []


def test_seed_precommitment_and_query_budget_are_enforced():
    with pytest.raises(ValueError, match="multiple of four"):
        run(query(),max_queries=5)
    with pytest.raises(ValueError,match="distinct"):
        probe_pairwise_mean_response(
            query(),[1.],prespecified_iid_seed_draws=[1,1],
            hard_coordinate_contrast_bound=.1,max_policy_queries=8,
            response_tolerance=.2,alpha=.1,physical_charts_aligned=True,
            controller_authority_valid=True,
            population_bound_independently_justified=True,
            iid_seed_draw_design_attested=True,
        )


def test_bound_violation_fails_closed_and_charges_attempted_query_cost():
    bad = run(query(gap=.5), B=.1)
    assert bad.decision is ResponseProbeDecision.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert bad.total_policy_queries == 4
    assert bad.seeds_used == (1,)
    assert len(bad.rounds) == 0
    assert bad.confidence_level_if_assumptions_hold is None


def test_invalid_action_shape_and_nan_fail_closed_without_forging_valid_rounds():
    def wrong(seed,h):
        return {"baseline_a":[0.,0.],"perturbed_a":[0.,0.],
                "baseline_b":[0.],"perturbed_b":[0.]}
    assert run(wrong).decision is ResponseProbeDecision.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert run(wrong).total_policy_queries == 4
    def nan_probe(seed,h):
        return {"baseline_a":[0.,0.],"perturbed_a":[float("nan"),0.],
                "baseline_b":[0.,0.],"perturbed_b":[0.,0.]}
    assert run(nan_probe).decision is ResponseProbeDecision.REJECT_UNSUPPORTED_ASSUMPTIONS


def test_matched_randomness_removes_common_stochastic_component_in_constructed_example():
    result1=run(query(gap=0, noise=100),B=.04)
    result2=run(query(gap=0, noise=0),B=.04)
    assert result1.decision is ResponseProbeDecision.STATISTICAL_MEAN_SIMILAR
    assert result1.rounds[0].response_contrast == result2.rounds[0].response_contrast
    # Demonstrates coupling in this *constructed toy*, not proven real-policy variance reduction.
