"""Synthetic regressions for established bounded empirical-Bernstein anytime CS.

These tests are NOT evidence on real Diffusion/VQ-BeT policies.
"""
import numpy as np
import pytest

from research.crg_core.active_paired_response_probe import (
    ProbeExecutionStatus,
    execute_directional_probe_budget,
)
from research.crg_core.directional_anytime_probes import DirectionalDecision
from research.crg_core.variance_adaptive_paired_response import (
    inspect_eb_transfer_budget_feasibility,
    inspect_empirical_bernstein_samples,
)


def options(*, method="empirical_bernstein", budget=2048,
            tau=0.25, remainder=0, transfer_only=True):
    return dict(
        prespecified_iid_seeds=list(range(1, budget // 4 + 1)),
        probe_fraction=1.0,
        trusted_action_lows=[0, 0],
        trusted_action_highs=[1, 1],
        locality_remainder_bound=remainder,
        physical_response_tolerance=tau,
        familywise_error_budget=0.1,
        max_policy_forward_queries=budget,
        independent_seeds_verified=True,
        controller_bounds_verified=True,
        common_physical_chart_verified=True,
        controller_authority_verified=True,
        transfer_only=transfer_only,
        confidence_method=method,
    )


def identical_callback(seed, direction, epsilon):
    return dict(
        plus_a=[0.6, 0.6], minus_a=[0.4, 0.4],
        plus_b=[0.6, 0.6], minus_b=[0.4, 0.4],
    )


def test_empirical_bound_passes_known_constant_observations_and_is_anytime():
    opts = dict(
        probe_fraction=1.0,
        action_coordinate_span_a=np.ones(2),
        action_coordinate_span_b=np.ones(2),
        locality_remainder_bound=0.0,
        trusted_response_tolerance=0.25,
        familywise_error_budget=0.1,
        max_seed_pairs=512,
        independent_seeds_verified=True,
        controller_bounds_verified=True,
        common_physical_chart_verified=True,
    )
    data = np.zeros((512, 2))
    early = inspect_empirical_bernstein_samples(data[:1], **opts)
    assert early.decision is DirectionalDecision.CONTINUE_PROBING
    assert early.simultaneous_confidence_radius is None  # no sample var with n=1
    final = inspect_empirical_bernstein_samples(data, **opts)
    assert final.decision is DirectionalDecision.CONDITIONAL_SIMILAR_MEAN_RESPONSE
    assert final.upper_mean_response_gap <= 0.25
    assert final.lower_mean_response_gap == 0
    assert not final.external_validation


def test_runtime_method_switch_exhibits_real_query_saving_on_synthetic_low_variance():
    q_eb = []
    q_h = []
    def eb_callback(seed, direction, eps):
        q_eb.append(seed)
        return identical_callback(seed, direction, eps)
    def h_callback(seed, direction, eps):
        q_h.append(seed)
        return identical_callback(seed, direction, eps)
    eb = execute_directional_probe_budget(
        eb_callback, [0.1, 0], **options()
    )
    h = execute_directional_probe_budget(
        h_callback, [0.1, 0], **options(method="hoeffding")
    )
    assert eb.status is ProbeExecutionStatus.CONDITIONAL_MEAN_TRANSFER
    assert 0 < eb.charged_policy_forward_queries < 2048
    assert eb.charged_policy_forward_queries == 4*len(q_eb)
    # The default (nonadaptive) certificate cannot succeed at this budget.
    assert h.status is ProbeExecutionStatus.ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE
    assert h.charged_policy_forward_queries == 0
    assert q_h == []
    assert not eb.deterministic_safety_guarantee


def test_eb_impossible_budget_no_calls_but_diagnostic_mode_runs():
    attempts = []
    def counted(seed, h, eps):
        attempts.append(seed)
        return identical_callback(seed, h, eps)
    kw = options(budget=128)
    impossible = execute_directional_probe_budget(counted, [0.1, 0], **kw)
    assert impossible.status is ProbeExecutionStatus.ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE
    assert impossible.charged_policy_forward_queries == 0
    assert attempts == []
    diagnostic = execute_directional_probe_budget(
        counted, [0.1, 0], **(kw | {"transfer_only": False})
    )
    assert diagnostic.status is ProbeExecutionStatus.ABSTAIN_QUERY_BUDGET
    assert diagnostic.charged_policy_forward_queries == 128
    assert len(attempts) == 32


def test_eb_best_case_preflight_matches_actual_zero_variance_radius():
    kw = options(budget=2048)
    f = inspect_eb_transfer_budget_feasibility(
        trusted_action_lows=np.array(kw["trusted_action_lows"]),
        trusted_action_highs=np.array(kw["trusted_action_highs"]),
        probe_fraction=kw["probe_fraction"],
        locality_remainder_bound=kw["locality_remainder_bound"],
        physical_response_tolerance=kw["physical_response_tolerance"],
        familywise_error_budget=kw["familywise_error_budget"],
        max_policy_forward_queries=kw["max_policy_forward_queries"],
    )
    assert f.could_ever_authorize_with_budget
    assert f.best_seed_pair_count > 1
    r = inspect_empirical_bernstein_samples(
        np.zeros((f.best_seed_pair_count, 2)),
        probe_fraction=1,
        action_coordinate_span_a=np.ones(2),
        action_coordinate_span_b=np.ones(2),
        locality_remainder_bound=0,
        trusted_response_tolerance=.25,
        familywise_error_budget=.1,
        max_seed_pairs=512,
        independent_seeds_verified=True,
        controller_bounds_verified=True,
        common_physical_chart_verified=True,
    )
    assert r.upper_mean_response_gap == pytest.approx(
        f.minimum_possible_upper_bound, abs=1e-12
    )


def test_sample_variance_not_statically_assumed_to_be_zero():
    rng = np.random.default_rng(99)
    # Each secant is a bounded two-vector with high variance.
    z = rng.choice([-0.8, 0.8], size=(512, 2))
    r = inspect_empirical_bernstein_samples(
        z, probe_fraction=1,
        action_coordinate_span_a=np.ones(2),
        action_coordinate_span_b=np.ones(2),
        locality_remainder_bound=0,
        trusted_response_tolerance=.25,
        familywise_error_budget=.1,
        max_seed_pairs=512,
        independent_seeds_verified=True,
        controller_bounds_verified=True,
        common_physical_chart_verified=True,
    )
    assert r.decision is DirectionalDecision.ABSTAIN_QUERY_BUDGET
    assert r.upper_mean_response_gap > 0.25
    assert r.simultaneous_confidence_radius > .25


def test_dangerous_missing_physical_assumptions_fail_closed_before_querying():
    attempts = []
    def cb(seed, d, eps):
        attempts.append(seed)
        return identical_callback(seed, d, eps)
    base = options() | {"locality_remainder_bound": None}
    r = execute_directional_probe_budget(cb, [0.1,0], **base)
    assert r.status is ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert attempts == []
    untrusted = options() | {"controller_bounds_verified": False}
    r2 = execute_directional_probe_budget(cb, [0.1,0], **untrusted)
    assert r2.status is ProbeExecutionStatus.REJECT_UNSUPPORTED_ASSUMPTIONS
    assert attempts == []


def test_fixed_remainder_larger_than_tolerance_prevents_any_transfer():
    kw = options(tau=.25, remainder=.3)
    r = execute_directional_probe_budget(
        identical_callback, [0.1,0], **kw
    )
    assert r.status is ProbeExecutionStatus.ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE
    assert r.charged_policy_forward_queries == 0


def test_no_pseudoreplication_unknown_method_or_out_of_support_clipping():
    with pytest.raises(ValueError, match="confidence_method"):
        execute_directional_probe_budget(
            identical_callback, [0.1,0],
            **options(method="fabricated")
        )
    r = inspect_empirical_bernstein_samples(
        np.array([[3.,0.], [3.,0.]]),
        probe_fraction=1,
        action_coordinate_span_a=np.ones(2),
        action_coordinate_span_b=np.ones(2),
        locality_remainder_bound=0,
        trusted_response_tolerance=1.,
        familywise_error_budget=.1,
        max_seed_pairs=2,
        independent_seeds_verified=True,
        controller_bounds_verified=True,
        common_physical_chart_verified=True,
    )
    assert r.decision is DirectionalDecision.REJECT_UNTRUSTED_BOUND
    assert not r.external_validation


def test_single_seed_budget_always_abstains_without_empirical_variance():
    f = inspect_eb_transfer_budget_feasibility(
        trusted_action_lows=np.zeros(1),
        trusted_action_highs=np.ones(1),
        probe_fraction=1.0,
        locality_remainder_bound=0.,
        physical_response_tolerance=10.,
        familywise_error_budget=.1,
        max_policy_forward_queries=4,
    )
    assert not f.could_ever_authorize_with_budget
    assert f.best_seed_pair_count == 0
    assert not np.isfinite(f.minimum_possible_upper_bound)
