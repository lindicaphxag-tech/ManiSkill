"""Algorithmic math/guard tests; synthetic policy responses are NOT real trials."""
import numpy as np
import pytest

from research.crg_core.directional_anytime_probes import (
    DirectionalDecision, inspect_directional_samples, paired_directional_secant,
)


def _call(values, *, sa=0.01, sb=0.01, eps=1.0, tau=0.05,
          nmax=64, remainder=0.0, **flags):
    data=np.asarray(values,dtype=float).reshape((-1,1))
    return inspect_directional_samples(
        data, probe_fraction=eps, action_coordinate_span_a=np.array([sa]),
        action_coordinate_span_b=np.array([sb]),
        locality_remainder_bound=remainder,
        trusted_response_tolerance=tau,
        max_seed_pairs=nmax,
        independent_seeds_verified=flags.get("seeds",True),
        controller_bounds_verified=flags.get("bounds",True),
        common_physical_chart_verified=flags.get("chart",True),
    )


def test_four_evaluations_cancel_matched_seed_policy_baselines():
    z = paired_directional_secant(
        np.array([1.3]),np.array([0.9]),np.array([1.05]),
        np.array([0.95]),probe_fraction=0.5,
        trusted_action_lows=np.array([0.0]),trusted_action_highs=np.array([2.0]),
    )
    np.testing.assert_allclose(z,[0.3])
    with pytest.raises(ValueError,match="do NOT silently clip"):
        paired_directional_secant(
            np.array([2.1]),np.array([0.9]),np.array([1.0]),np.array([1.0]),
            probe_fraction=0.5,
            trusted_action_lows=np.array([0.0]),trusted_action_highs=np.array([2.0]),
        )


def test_small_action_span_permits_conditional_mean_transfer():
    result=_call(np.zeros(64),sa=0.01,sb=0.01,eps=1.0,tau=0.05,
                 nmax=64,remainder=0.002)
    assert result.decision is DirectionalDecision.CONDITIONAL_SIMILAR_MEAN_RESPONSE
    assert result.policy_forward_queries==256
    assert result.observed_seed_pairs==64
    assert result.upper_mean_response_gap < 0.05
    assert result.external_validation is False
    assert "MEAN" in result.evidence_type


def test_distinct_sequential_decision_is_not_transfer_permission():
    result=_call(np.full(1024,0.08),sa=0.08,sb=0.08,eps=1.0,
                 tau=0.04,nmax=1024,remainder=0.002)
    assert result.decision is DirectionalDecision.CONDITIONAL_DISTINCT_MEAN_RESPONSE
    assert result.lower_mean_response_gap>0.04
    assert result.policy_forward_queries==4096


def test_mid_budget_collects_more_and_terminal_budget_abstains():
    for count,expected in [(2,DirectionalDecision.CONTINUE_PROBING),
                           (4,DirectionalDecision.ABSTAIN_QUERY_BUDGET)]:
        result=_call(np.zeros(count),sa=1.0,sb=1.0,nmax=4,
                     tau=0.02,remainder=0.0)
        assert result.decision is expected
        assert result.policy_forward_queries==4*count


def test_missing_locality_and_unverified_seed_independence_fail_closed():
    for opts in [
        dict(remainder=None),
        dict(seeds=False),
        dict(bounds=False),
        dict(chart=False),
    ]:
        result=_call(np.zeros(8),**opts)
        assert result.decision is DirectionalDecision.REJECT_UNTRUSTED_BOUND
        assert result.lower_mean_response_gap is None


def test_violated_support_bound_is_rejected():
    result=_call(np.array([0.2,0.25]),sa=0.01,sb=0.01,eps=1.0)
    assert result.decision is DirectionalDecision.REJECT_UNTRUSTED_BOUND


def test_more_data_cannot_shrink_missing_guarantees_into_a_certificate():
    for count in (2,20,200):
        r=_call(np.zeros(count),nmax=200,remainder=None)
        assert r.decision is DirectionalDecision.REJECT_UNTRUSTED_BOUND


def test_nonfinite_samples_and_invalid_budget_never_certify():
    assert _call([float("nan")]).decision is DirectionalDecision.REJECT_UNTRUSTED_BOUND
    with pytest.raises(ValueError, match="positive"):
        _call([0.0],nmax=0)
    with pytest.raises(ValueError,match="familywise"):
        inspect_directional_samples(
            np.zeros((1,1)),probe_fraction=1,
            action_coordinate_span_a=np.array([1.]),
            action_coordinate_span_b=np.array([1.]),
            locality_remainder_bound=0, trusted_response_tolerance=1,
            familywise_error_budget=1.0,
        )


def test_two_dimensional_control_requires_simultaneous_component_bounding():
    result=inspect_directional_samples(
        np.zeros((32,2)),probe_fraction=1,
        action_coordinate_span_a=np.array([0.1,0.1]),
        action_coordinate_span_b=np.array([0.1,0.1]),
        locality_remainder_bound=0.01,
        trusted_response_tolerance=0.01,
        max_seed_pairs=32,independent_seeds_verified=True,
        controller_bounds_verified=True,common_physical_chart_verified=True,
    )
    assert result.decision is DirectionalDecision.ABSTAIN_QUERY_BUDGET
    assert result.simultaneous_confidence_radius > 0.0
