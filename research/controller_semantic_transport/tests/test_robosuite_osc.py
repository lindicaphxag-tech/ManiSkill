import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from cst.robosuite_osc import OSCState, absolute_pose_to_delta_action


def state():
    return OSCState(
        achieved_pos=np.array([0.2, -0.1, 0.4]),
        achieved_ori=Rotation.from_euler("xyz", [0.1, -0.2, 0.3]).as_matrix(),
        desired_pos=np.array([0.25, -0.08, 0.45]),
        desired_ori=Rotation.from_euler("xyz", [0.15, -0.1, 0.25]).as_matrix(),
    )


@pytest.mark.parametrize("mode", ["achieved", "desired"])
def test_absolute_to_delta_roundtrip_semantics(mode):
    absolute = np.r_[
        np.array([0.27, -0.04, 0.48]),
        Rotation.from_euler("xyz", [0.18, -0.04, 0.32]).as_rotvec(),
    ]
    cert = absolute_pose_to_delta_action(
        absolute_action=absolute,
        state=state(),
        goal_update_mode=mode,
        input_min=-np.ones(6),
        input_max=np.ones(6),
        output_min=np.array([-0.2, -0.2, -0.2, -0.5, -0.5, -0.5]),
        output_max=np.array([0.2, 0.2, 0.2, 0.5, 0.5, 0.5]),
    )
    assert cert.accepted, cert.reason
    assert cert.position_residual <= 1e-12
    assert cert.orientation_residual <= 1e-8


def test_achieved_and_desired_modes_require_different_hidden_state():
    absolute = np.r_[
        np.array([0.30, -0.02, 0.50]),
        Rotation.from_euler("xyz", [0.20, 0.0, 0.35]).as_rotvec(),
    ]
    kwargs = dict(
        absolute_action=absolute,
        state=state(),
        input_min=-np.ones(6),
        input_max=np.ones(6),
        output_min=-0.5 * np.ones(6),
        output_max=0.5 * np.ones(6),
    )
    a = absolute_pose_to_delta_action(goal_update_mode="achieved", **kwargs)
    d = absolute_pose_to_delta_action(goal_update_mode="desired", **kwargs)
    assert not np.allclose(a.physical_delta, d.physical_delta)


def test_unrepresentable_absolute_pose_fails_closed():
    absolute = np.r_[
        np.array([2.0, 0.0, 0.0]),
        np.zeros(3),
    ]
    cert = absolute_pose_to_delta_action(
        absolute_action=absolute,
        state=state(),
        goal_update_mode="achieved",
        input_min=-np.ones(6),
        input_max=np.ones(6),
        output_min=-0.1 * np.ones(6),
        output_max=0.1 * np.ones(6),
    )
    assert not cert.accepted
    assert cert.saturation_margin < 0
    assert "outside" in cert.reason
