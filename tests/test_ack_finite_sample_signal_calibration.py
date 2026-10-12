"""Independent exact-binomial coverage and calibration data-boundary witnesses.

All generated responses in this test file are SYNTHETIC, not PhysX results.
"""
from math import isfinite

import numpy as np
import pytest
from scipy.stats import binom

from research.action_abi_history_observer import TargetPose
from research.ack_native_probe_source_adapter import propose_from_common_native_action
from research.ack_finite_sample_signal_calibration import (
    exact_binomial_interval, simultaneous_ack_signal_calibration,
)
from research.ack_robust_readback_value import decide_probe_vs_readback


def proposal(name, u=0, cost=.01, physically_attested=True):
    states = {
        "held": TargetPose.from_arrays([0, 0, 0], [0, 0, 0, 1]),
        "applied": TargetPose.from_arrays([.04, 0, 0], [0, 0, 0, 1]),
    }
    return propose_from_common_native_action(
        states, [u, 0, 0, 0, 0, 0], name=name,
        pos_lower=-.1, pos_upper=.1, rot_lower=-np.pi/2,
        declared_action_cost=cost,
        independent_controller_mapping_attestation=physically_attested,
        external_physical_admissibility_attestation=physically_attested,
    )


def synthetic_perfect_rows(n):
    return [
        (seed, truth, int(truth == "applied"))
        for seed in range(1000, 1000+n)
        for truth in ("held", "applied")
    ]


def calibrate(n, *, assumed=True, k=1):
    ps = [proposal(f"p{i}", 0.2*i) for i in range(k)]
    observations = {p.name: synthetic_perfect_rows(n) for p in ps}
    return simultaneous_ack_signal_calibration(
        ps, observations, heldout_evaluation_reset_ids=[9001,9002],
        frozen_binary_signal_rule="Z := frozen public signal > declared threshold",
        independently_verified_reset_sampling=assumed,
        externally_verified_physical_source=assumed,
        independently_calibrated_action_costs=assumed,
    )


def decision(result):
    return decide_probe_vs_readback(
        prior_applied=.5, false_applied_cost=1, false_held_cost=1,
        candidates=[r.evidence for r in result],
        abstain_cost=.4, trusted_readback_cost=.2,
        prior_externally_calibrated=True,
        readback_state_authoritative_attested=True,
        maximum_acceptable_wrong_classification_risk=.05,
    )


def test_exact_binomial_boundary_interval_is_not_a_point_estimate():
    lo, hi = exact_binomial_interval(0, 4, .05)
    assert lo == 0.0 and hi > .5
    lo, hi = exact_binomial_interval(4, 4, .05)
    assert lo < .5 and hi == 1.0


def test_exact_binomial_interval_discrete_coverage_oracle():
    # Enumeration of all binomial observations, independent of beta.ppf.
    alpha = .05
    for n in (1, 3, 8, 16):
        intervals = [exact_binomial_interval(k, n, alpha)
                     for k in range(n+1)]
        for p in np.linspace(0, 1, 101):
            covered = sum(float(binom.pmf(k, n, p))
                          for k, (lo, hi) in enumerate(intervals)
                          if lo - 1e-14 <= p <= hi + 1e-14)
            assert covered >= 1 - alpha - 1e-11


def test_small_calibration_forces_readback_not_fake_confident_probe():
    cert, = calibrate(4, assumed=True)
    assert cert.samples_per_history == 4
    assert cert.held_probability_interval[1] > .5
    assert cert.applied_probability_interval[0] < .5
    assert decision((cert,)).decision == "READBACK"
    assert not cert.physical_response_safety_certified


def test_large_independent_calibration_can_conditionally_enable_probe():
    cert, = calibrate(100, assumed=True)
    assert cert.held_probability_interval[1] < .07
    assert cert.applied_probability_interval[0] > .93
    selected = decision((cert,))
    assert selected.decision == "PROBE"
    assert selected.name == "p0"
    assert selected.signal_zero_decision == "HELD"
    assert selected.signal_one_decision == "APPLIED"
    assert selected.worst_classification_loss <= .05
    assert selected.physical_safety_certified is False


def test_familywise_bonferroni_alpha_accounts_for_full_candidate_count():
    one, = calibrate(40, k=1)
    first, second = calibrate(40, k=2)
    assert first.marginal_miscoverage_budget == pytest.approx(.05/4)
    assert one.marginal_miscoverage_budget == pytest.approx(.05/2)
    assert first.held_probability_interval[1] > one.held_probability_interval[1]
    assert second.calibration_reset_ids == first.calibration_reset_ids
    assert len(first.source_digest_sha256) == 64
    assert all(isfinite(x) for x in first.held_probability_interval)


def test_flags_are_not_automatically_authenticated_by_input_hash():
    cert, = calibrate(100, assumed=False)
    assert len(cert.source_digest_sha256) == 64
    assert cert.evidence.independent_holdout_calibration_attested is False
    assert cert.evidence.calibrated_cost_attested is False
    assert decision((cert,)).decision == "READBACK"


def test_refuse_overlapping_calibration_and_evaluation_seed():
    p = proposal("p0")
    with pytest.raises(ValueError, match="overlap"):
        simultaneous_ack_signal_calibration(
            [p], {"p0": synthetic_perfect_rows(4)},
            heldout_evaluation_reset_ids=[1000],
            frozen_binary_signal_rule="frozen", family_miscoverage=.05,
        )


@pytest.mark.parametrize("mutate,reason", [
    (lambda r: r + [r[0]], "duplicate"),
    (lambda r: [v for v in r if v[1] != "held"], "incomplete"),
    (lambda r: [(seed, truth, 2 if idx==0 else z)
                 for idx,(seed,truth,z) in enumerate(r)], "invalid original"),
])
def test_bad_or_correlated_denominator_rejected(mutate, reason):
    p = proposal("p0")
    with pytest.raises(ValueError, match=reason):
        simultaneous_ack_signal_calibration(
            [p], {"p0": mutate(synthetic_perfect_rows(4))},
            heldout_evaluation_reset_ids=[9001],
            frozen_binary_signal_rule="frozen",
        )


def test_all_original_candidates_required_and_no_posthoc_family_silence():
    ps = [proposal("p0"),proposal("p1")]
    with pytest.raises(ValueError, match="full original"):
        simultaneous_ack_signal_calibration(
            ps, {"p0": synthetic_perfect_rows(4)},
            heldout_evaluation_reset_ids=[9001],
            frozen_binary_signal_rule="frozen",
        )


@pytest.mark.parametrize("n,k,alpha", [
    (0,0,.05), (2,-1,.05), (3,4,.05), (3,2,1),
    (3,2,float("nan")), (3,2,0),
])
def test_invalid_binomial_arguments_fail_closed(n,k,alpha):
    with pytest.raises(ValueError):
        exact_binomial_interval(k,n,alpha)
