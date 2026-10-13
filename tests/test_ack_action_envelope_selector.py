"""Action-dependent gain can change visibility; common affine actions cannot fake it."""
import numpy as np
import pytest

from research.action_abi_history_observer import TargetPose
from research.ack_native_probe_source_adapter import propose_from_common_native_action
from research.ack_action_envelope_selector import (
    ActionEnvelope, choose_under_action_envelopes,
)


def pose(x):
    return TargetPose.from_arrays([x, 0, 0], [0, 0, 0, 1])


def actions(*, admitted=True):
    states = {"held": pose(0), "applied": pose(.04)}
    def make(name, action, cost):
        return propose_from_common_native_action(
            states, action, name=name, pos_lower=-.1, pos_upper=.1,
            rot_lower=-np.pi/2, declared_action_cost=cost,
            independent_controller_mapping_attestation=admitted,
            external_physical_admissibility_attestation=admitted,
        )
    return (
        make("zero", [0]*6, 1),
        make("physical_nonzero", [.6, 0, 0, 0, 0, 0], 2),
    )


def envelope(gain, *, source="independent-calibration", attested=True, eps=.009):
    return ActionEnvelope(gain, gain, eps, attested, source)


def select(proposals, envelopes):
    return choose_under_action_envelopes(
        (0, 0, 0), ("held", "applied"), proposals, envelopes,
        maximum_declared_cost=3,
    )


def test_action_dependent_gain_can_conditionally_resolve_hidden_history():
    """This is a SYNTHETIC mechanism test, not a PhysX result."""
    zero, moving = actions()
    r = select([zero, moving], {
        "zero": envelope(.4), # margin = .016-.018 < 0, cannot distinguish
        "physical_nonzero": envelope(.9),  # margin = .036-.018 > 0
    })
    assert r.name == "physical_nonzero"
    assert r.native_action == moving.native_action
    assert r.conditional_gap_m == pytest.approx(.018 - 2e-9)
    assert not r.physical_safety_certified


def test_no_reward_for_extra_action_under_equal_fixed_gain_and_more_cost():
    """Prior Panda/xArm6 real negative study motivates this falsifier."""
    zero, moving = actions()
    result = select([moving, zero], {
        "zero": envelope(.9), "physical_nonzero": envelope(.9)
    })
    assert result.name == "zero"
    assert result.attempted == 2
    assert result.score > 0


def test_action_specific_calibration_cannot_be_borrowed_from_other_probe():
    zero, moving = actions()
    r = select([zero, moving], {"zero": envelope(.4)})
    assert r.name is None
    r = select([zero, moving], {
        "zero": envelope(.4),
        "physical_nonzero": envelope(.9, source="", attested=True)
    })
    assert r.name is None
    r = select([zero, moving], {
        "zero": envelope(.4),
        "physical_nonzero": envelope(.9, attested=False)
    })
    assert r.name is None


def test_native_source_fidelity_without_independent_attestation_refuses_action():
    zero, moving = actions(admitted=False)
    r = select([zero, moving], {
        "zero": envelope(.9), "physical_nonzero": envelope(.9)
    })
    assert r.name is None


def test_uncertain_gain_interval_and_wide_error_can_force_abstention():
    zero, moving = actions()
    r = select([zero, moving], {
        "zero": ActionEnvelope(.1, 1, .02, True, "calibration"),
        "physical_nonzero": ActionEnvelope(.1, 1, .02, True, "calibration")
    })
    assert r.name is None


@pytest.mark.parametrize("gain_min,gain_max,eps", [
    (-.1, 1, 0), (.5, .4, .01), (0, 2, .01),
    (0, 1, -.01), (0, 1, float("nan"))
])
def test_invalid_individual_action_envelopes_rejected(gain_min, gain_max, eps):
    zero, _ = actions()
    with pytest.raises(ValueError, match="invalid candidate-specific bounds"):
        select([zero], {"zero": ActionEnvelope(
            gain_min, gain_max, eps, True, "calibration"
        )})


def test_duplicate_names_fail_closed_even_if_geometry_valid():
    zero, _ = actions()
    with pytest.raises(ValueError, match="duplicate"):
        select([zero, zero], {"zero": envelope(.9)})
