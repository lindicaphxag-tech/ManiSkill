import copy

from research.eprc.cross_policy_report_adjudicator import adjudicate


def _report(model_id: str):
    return {
        "status": "completed",
        "protocol_id": "same-protocol",
        "policy_identity": {"model_id": model_id},
        "state_restore_protocol": "exact-state-v1",
        "environment_reset_seed": 17,
        "fine_physical_probe": [4.0, 4.0, 0.02],
        "coarse_physical_probe": [8.0, 8.0, 0.04],
        "heldout_physical_delta": [10.0, -6.0, 0.35],
        "jacobian_support_units": ["pixel", "pixel", "radian"],
        "support_metric_physical": [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        "heldout_first_action_response": [0.2, -0.1],
        "robust_crg": {"decision": "CERTIFIED_REPAIR"},
        "dec": {
            "first_action_step_jacobian": [
                [1.0, 0.0, 0.2],
                [0.0, 0.5, 0.1],
            ],
            "replicate_stability_certified": True,
        },
    }


def test_same_frozen_protocol_is_comparable():
    a = _report("diffusion")
    b = _report("vqbet")
    out = adjudicate(a, b)
    assert out.comparable
    assert out.dec_signature_distance == 0.0
    assert out.heldout_response_relative_distance == 0.0
    assert out.robust_decisions_agree
    assert out.both_dec_stable


def test_protocol_drift_fails_closed():
    a = _report("diffusion")
    b = _report("vqbet")
    b["heldout_physical_delta"] = [9.0, -6.0, 0.35]
    out = adjudicate(a, b)
    assert not out.comparable
    assert "heldout_physical_delta" in out.reason


def test_dec_instability_is_visible_not_hidden():
    a = _report("diffusion")
    b = _report("vqbet")
    b["dec"]["replicate_stability_certified"] = False
    out = adjudicate(a, b)
    assert out.comparable
    assert not out.both_dec_stable
    assert "failed the stability gate" in out.reason


def test_decision_disagreement_is_preserved():
    a = _report("diffusion")
    b = copy.deepcopy(_report("vqbet"))
    b["robust_crg"]["decision"] = "CERTIFIED_IMPOSSIBLE"
    out = adjudicate(a, b)
    assert out.comparable
    assert not out.robust_decisions_agree
