"""Native ACK-probe proposals must come from ONE real normalized controller action."""
import numpy as np
import pytest

from research.action_abi_history_observer import ActionHistoryObserver, TargetPose
from research.ack_robust_active_probe import Candidate, choose_probe, audit_fixed_gain_common_probe_null
from research.ack_native_probe_source_adapter import (
    propose_from_common_native_action, verify_candidate_against_native_source,
)


def pose(x, q=(0, 0, 0, 1)):
    return TargetPose.from_arrays([x, 0, 0], q)


def propose(histories, action, name, cost=1, **kwargs):
    return propose_from_common_native_action(
        histories, action, name=name, pos_lower=-.1, pos_upper=.1,
        rot_lower=-np.pi/2, declared_action_cost=cost, **kwargs)


def test_identical_native_action_replays_real_source_recurrence_independently():
    histories = {"held": pose(0), "applied": pose(.04)}
    action = np.array([.5, -.25, 0, 0, 0, .4])
    p = propose(histories, action, "nonzero")
    assert p.native_action == tuple(action)
    assert p.maximum_translation_deviation_m <= 1e-10
    assert p.source_kinematics_verified
    assert not p.physical_safety_certified
    assert not p.candidate.controller_mapping_attested
    assert not p.candidate.physical_admissibility_attested
    assert p.candidate.targets["held"] == pytest.approx((.05, -.025, 0))
    assert p.candidate.targets["applied"] == pytest.approx((.09, -.025, 0))
    for h, starting in histories.items():
        independent = ActionHistoryObserver(-.1, .1, -np.pi/2)
        independent.reset(starting)
        ticket = independent.prepare(action)
        independent.acknowledge(ticket.ticket, applied=True)
        assert p.candidate.targets[h] == pytest.approx(independent.pose.position)
    verify_candidate_against_native_source(
        p.candidate, histories, action, pos_lower=-.1, pos_upper=.1,
        rot_lower=-np.pi/2,
    )


def test_one_common_native_action_cannot_forge_history_dependent_separation():
    states = {"held": pose(0), "applied": pose(.04)}
    proposed = propose(states, [0, 0, 0, 0, 0, 0], "real")
    fake = Candidate("fake",
        targets={"held": (1, 0, 0), "applied": (-1, 0, 0)},
        cost=proposed.candidate.cost, controller_mapping_attested=True,
        physical_admissibility_attested=True)
    geometric = choose_probe((0, 0, 0), ("held", "applied"), [fake],
        alpha_min=1, alpha_max=1, model_and_sensor_error_m=.01,
        maximum_cost=3, response_envelope_independently_attested=True)
    assert geometric.candidate == "fake"  # synthetic toy is misleading
    with pytest.raises(ValueError, match="not induced"):
        verify_candidate_against_native_source(
            fake, states, [0, 0, 0, 0, 0, 0],
            pos_lower=-.1, pos_upper=.1, rot_lower=-np.pi/2,
        )


def test_native_candidate_fixed_gain_null_for_nonzero_translation():
    states = {"held": pose(0), "applied": pose(.04)}
    zero = propose(states, [0]*6, "zero", 1,
        independent_controller_mapping_attestation=True,
        external_physical_admissibility_attestation=True)
    nonzero = propose(states, [.6, -.2, .1, .1, 0, 0], "moving", 2,
        independent_controller_mapping_attestation=True,
        external_physical_admissibility_attestation=True)
    audit = audit_fixed_gain_common_probe_null(
        zero.candidate, nonzero.candidate, ("held", "applied"),
        response_gain=.7, common_gain_independently_attested=True,
        action_invariant_noise_independently_attested=True,
    )
    assert audit.probe_has_incremental_information is False
    assert audit.center_gap_zero_m == pytest.approx(audit.center_gap_probe_m)
    assert nonzero.maximum_translation_deviation_m <= 1e-10


def test_root_translation_remains_common_with_different_initial_orientations():
    from scipy.spatial.transform import Rotation
    q = tuple(Rotation.from_euler("XYZ", [.5, -.3, .1]).as_quat())
    states = {"held": pose(0), "applied": pose(.04, q)}
    p = propose(states, [.7, -.4, .2, 0, .3, 0], "orientation_control")
    a, b = (np.array(p.candidate.targets[h]) - np.array(states[h].position)
            for h in states)
    np.testing.assert_allclose(a, b, atol=1e-12)


@pytest.mark.parametrize("action", [
    [2, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 0],
    [0, 0, 0, np.nan, 0, 0],
    [0, 0, 0],
])
def test_invalid_native_action_rejected_before_model_prediction(action):
    with pytest.raises(ValueError):
        propose({"held": pose(0), "applied": pose(.04)}, action, "bad")


def test_two_histories_required_and_attestation_does_not_auto_generate():
    with pytest.raises(ValueError):
        propose({"one": pose(0)}, [0]*6, "invalid")
    p = propose({"held": pose(0), "applied": pose(.04)}, [0]*6, "valid")
    selected = choose_probe((0, 0, 0), ("held", "applied"), [p.candidate],
        alpha_min=1, alpha_max=1, model_and_sensor_error_m=0,
        maximum_cost=10, response_envelope_independently_attested=True)
    assert selected.candidate is None  # source fidelity alone is not attestation


def test_forecast_with_valid_shape_but_wrong_native_mapping_rejected():
    states = {"held": pose(0), "applied": pose(.04)}
    p = propose(states, [0]*6, "zero")
    fake = Candidate("fake", {"held": p.candidate.targets["held"],
                               "applied": (.0401, 0, 0)}, 1, True, True)
    with pytest.raises(ValueError, match="not induced"):
        verify_candidate_against_native_source(
            fake, states, [0]*6, pos_lower=-.1, pos_upper=.1,
            rot_lower=-np.pi/2,
        )
