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
                  false_applied_cost=9.0).decision == "PROBE"


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
