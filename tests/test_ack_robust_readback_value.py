"""Synthetic minimax decision/LP tests. These are NOT measured PhysX likelihoods."""
import numpy as np
import pytest

from research.action_abi_history_observer import TargetPose
from research.ack_native_probe_source_adapter import propose_from_common_native_action
from research.ack_robust_readback_value import (
    BinaryProbeEvidence, decide_probe_vs_readback, robust_binary_posterior_risk,
)


def risk(prior, q_held, q_applied, fp=1, fn=1):
    a, b = (1-prior)*fp, prior*fn
    return min(a*q_held, b*q_applied) + min(a*(1-q_held), b*(1-q_applied))


def candidate(name, held_bounds, applied_bounds, cost=.05, attested=True):
    states = {
        "held": TargetPose.from_arrays([0,0,0], [0,0,0,1]),
        "applied": TargetPose.from_arrays([.04,0,0], [0,0,0,1]),
    }
    proposal = propose_from_common_native_action(
        states, [.3, 0, 0, 0, 0, 0], name=name,
        pos_lower=-.1, pos_upper=.1, rot_lower=-np.pi/2,
        declared_action_cost=cost,
        independent_controller_mapping_attestation=attested,
        external_physical_admissibility_attestation=attested,
    )
    return BinaryProbeEvidence(
        proposal, held_bounds, applied_bounds,
        attested, attested, "SYNTHETIC-CONTRACT-NOT-A-PHYSICAL-RECEIPT",
    )


def choose(candidates, **changes):
    params = dict(prior_applied=.5, false_applied_cost=1,
                  false_held_cost=1, candidates=candidates, abstain_cost=.4,
                  trusted_readback_cost=.2,
                  prior_externally_calibrated=True,
                  readback_state_authoritative_attested=True,
                  maximum_acceptable_wrong_classification_risk=.05)
    params.update(changes)
    return decide_probe_vs_readback(**params)


def test_perfect_synthetic_signal_prefers_real_native_candidate():
    v = choose([candidate("probe", (0,0), (1,1))])
    assert v.decision == "PROBE"
    assert v.name == "probe"
    assert v.native_action == (.3, 0, 0, 0, 0, 0)
    assert v.worst_classification_loss <= 1e-8
    assert v.guaranteed_information_value == pytest.approx(.5, abs=1e-7)
    assert not v.physical_safety_certified
    assert (v.signal_zero_decision, v.signal_one_decision) == ("HELD", "APPLIED")


def test_unchanged_public_information_or_wide_uncertainty_prefers_readback():
    for held, applied in [
        ((.5,.5), (.5,.5)),
        ((0,1), (0,1)),
        ((.2,.8), (.2,.8)),
    ]:
        result = choose([candidate("no_gain", held, applied)])
        assert result.decision == "READBACK"
        assert result.worst_classification_loss == 0


def test_lp_maximum_can_be_interior_of_probability_uncertainty_rectangle():
    worst, baseline = robust_binary_posterior_risk(
        .5, (.2,.6), (.4,.8)
    )
    corners = max(risk(.5, h, a)
                  for h in (.2,.6) for a in (.4,.8))
    assert worst == pytest.approx(.5, abs=1e-8)
    assert baseline == pytest.approx(.5)
    assert corners <= .4 + 1e-12
    assert worst > corners + .09


def test_lp_is_upper_bound_on_dense_independent_grid_oracle():
    rng = np.random.default_rng(10132026)
    for _ in range(150):
        prior = float(rng.uniform(.01,.99))
        fp, fn = rng.uniform(.3,3,2)
        bounds = [tuple(sorted(rng.uniform(0,1,2))) for _ in range(2)]
        worst, baseline = robust_binary_posterior_risk(
            prior, *bounds, false_applied_cost=fp, false_held_cost=fn
        )
        q0 = np.linspace(*bounds[0], 41)
        q1 = np.linspace(*bounds[1], 41)
        grid_max = max(risk(prior, x, y, fp, fn) for x in q0 for y in q1)
        assert 0 <= grid_max <= worst + 1e-7
        assert worst - grid_max < .025 * max(fp, fn)
        assert worst <= baseline + 1e-7


def test_robust_error_budget_and_probe_cost_cannot_be_ignored():
    assert choose([candidate("expensive", (0,0), (1,1), cost=.3)]).decision == "READBACK"
    assert choose([candidate("accurate", (.01,.01), (.99,.99), cost=.01)],
                  maximum_acceptable_wrong_classification_risk=.005).decision == "READBACK"
    assert choose([candidate("accurate", (.01,.01), (.99,.99), cost=.01)],
                  false_applied_cost=9.0,
                  maximum_acceptable_wrong_classification_risk=.06).decision == "PROBE"


def test_unattested_prior_or_probes_are_never_accepted_as_physical_evidence():
    strong = candidate("looks_good", (0,0), (1,1), attested=False)
    assert choose([strong]).decision == "READBACK"
    assert choose([candidate("looks_good", (0,0), (1,1))],
                  prior_externally_calibrated=False).decision == "READBACK"
    assert choose([candidate("looks_good", (0,0), (1,1))],
                  prior_externally_calibrated=False,
                  readback_state_authoritative_attested=False).decision == "ABSTAIN"


def test_nearly_certain_attested_prior_can_choose_no_probe():
    assert choose([candidate("uninformative", (.5,.5), (.5,.5))],
                  prior_applied=.001).decision == "NO_PROBE"


def test_invalid_probability_and_provenance_contracts_fail_closed():
    with pytest.raises(ValueError):
        robust_binary_posterior_risk(.5, (.9,.1), (.1,.9))
    with pytest.raises(ValueError):
        robust_binary_posterior_risk(float("nan"), (0,1), (0,1))
    with pytest.raises(ValueError):
        choose([], abstain_cost=0)
    with pytest.raises(ValueError):
        choose([], trusted_readback_cost=-1)
    with pytest.raises(ValueError, match="duplicate"):
        choose([candidate("same", (0,0), (1,1)),
                candidate("same", (0,0), (1,1))])


def test_fixed_decoder_cannot_adapt_to_unknown_true_likelihood():
    from research.ack_robust_readback_value import robust_binary_decision_rule
    for held, applied, expected in [
        ((0, 0), (1, 1), ("HELD", "APPLIED")),
        ((1, 1), (0, 0), ("APPLIED", "HELD")),
    ]:
        negative, positive, bound = robust_binary_decision_rule(
            .5, held, applied
        )
        assert (negative, positive) == expected
        assert bound < 1e-7

    # Interior worst-case probability distributions must not silently
    # produce an optimistic mapping chosen after seeing the true q.
    negative, positive, bound = robust_binary_decision_rule(
        .5, (.2, .6), (.4, .8)
    )
    assert bound == pytest.approx(.5, abs=1e-7)
    assert (negative, positive) in (
        ("HELD", "HELD"), ("APPLIED", "APPLIED"),
        ("HELD", "APPLIED"), ("APPLIED", "HELD"),
    )


def test_robust_decoder_worst_risk_matches_explicit_policy_enumeration():
    from research.ack_robust_readback_value import robust_binary_decision_rule
    rng = np.random.default_rng(20261013)
    for _ in range(200):
        prior = float(rng.uniform(.01, .99))
        fp, fn = rng.uniform(.2, 4, 2)
        held = tuple(sorted(rng.uniform(0, 1, 2)))
        applied = tuple(sorted(rng.uniform(0, 1, 2)))
        out_zero, out_one, worst = robust_binary_decision_rule(
            prior, held, applied,
            false_applied_cost=fp, false_held_cost=fn,
        )
        a, b = (1 - prior) * fp, prior * fn
        # This is the actual precommitted decoder's expected loss.
        def decoder_risk(q0, q1):
            false_applied = (1 - q0 if out_zero == "APPLIED" else 0)
            false_applied += q0 if out_one == "APPLIED" else 0
            false_held = (1 - q1 if out_zero == "HELD" else 0)
            false_held += q1 if out_one == "HELD" else 0
            return a * false_applied + b * false_held
        actual_worst = max(
            decoder_risk(q0, q1)
            for q0 in held for q1 in applied
        )
        assert actual_worst <= worst + 1e-7
        assert worst - actual_worst <= 2e-7 * max(1, a, b)


def test_prior_interval_rejects_overconfident_probe_under_prior_shift():
    # Same frozen conditional likelihood and same legal source-native action.
    # Nominal p=.5 appears safe (worst risk=.105), but p=.95 gives .1905.
    # A strict .12 risk cap must prefer authoritative readback.
    evidence = candidate("signal", (.01, .01), (.8, .8), cost=.01)
    nominal = choose([evidence],
        maximum_acceptable_wrong_classification_risk=.12)
    assert nominal.decision == "PROBE"
    shifted = choose([evidence], prior_applied_interval=(.5, .95),
        maximum_acceptable_wrong_classification_risk=.12)
    assert shifted.decision == "READBACK"
    assert shifted.signal_zero_decision is None
    assert not shifted.physical_safety_certified


def test_worst_case_prior_rule_matches_independent_vertex_oracle():
    from research.ack_robust_readback_value import (
        robust_binary_decision_rule_prior_interval,
    )
    rng = np.random.default_rng(2000013)
    for _ in range(300):
        priors = tuple(sorted(rng.uniform(0, 1, 2)))
        held = tuple(sorted(rng.uniform(0, 1, 2)))
        applied = tuple(sorted(rng.uniform(0, 1, 2)))
        fp, fn = rng.uniform(.1, 7, 2)
        z0, z1, risk_bound = robust_binary_decision_rule_prior_interval(
            priors, held, applied,
            false_applied_cost=fp, false_held_cost=fn,
        )
        def risk(p, q0, q1):
            return (
                (1-p) * fp * (
                    (1-q0) * (z0 == "APPLIED") + q0 * (z1 == "APPLIED")
                )
                + p * fn * (
                    (1-q1) * (z0 == "HELD") + q1 * (z1 == "HELD")
                )
            )
        exact = max(risk(p, h, a)
                    for p in priors for h in held for a in applied)
        assert risk_bound == pytest.approx(exact, abs=1e-11)
        assert risk_bound >= 0


def test_prior_interval_no_probe_returns_actual_minimax_ack_label():
    p = candidate("uninformative", (.5, .5), (.5, .5))
    selected = choose([p], prior_applied=.01,
                      prior_applied_interval=(.001, .02))
    assert selected.decision == "NO_PROBE"
    assert selected.no_probe_history_decision == "HELD"
    assert selected.signal_zero_decision is None
    assert selected.worst_classification_loss == pytest.approx(.02)


def test_prior_interval_requires_nominal_containment_and_valid_bounds():
    with pytest.raises(ValueError, match="outside declared"):
        choose([], prior_applied=.5, prior_applied_interval=(.6, .8))
    with pytest.raises(ValueError, match="interval probabilities"):
        choose([], prior_applied=.5, prior_applied_interval=(.8, .6))
    with pytest.raises(ValueError, match="interval probabilities"):
        choose([], prior_applied=.5, prior_applied_interval=(0, 2))
