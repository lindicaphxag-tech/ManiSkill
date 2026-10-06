from math import pi
from types import MethodType, SimpleNamespace

import numpy as np
import pytest
import sapien
import torch

from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory.utils.actions.conversion import (
    _normalized_pd_ee_rotation_action,
    delta_pose_to_pd_ee_delta,
)
from mani_skill.utils import gym_utils
from mani_skill.utils.geometry import rotation_conversions


def _controller():
    controller = object.__new__(PDEEPoseController)
    controller.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
        rot_lower=-2 * pi,
        rot_upper=2 * pi,
    )
    controller.action_space_low = torch.tensor(
        [-0.1] * 3 + [-2 * pi] * 3, dtype=torch.float64
    )
    controller.action_space_high = torch.tensor(
        [0.1] * 3 + [2 * pi] * 3, dtype=torch.float64
    )
    return controller


def _sign_preserving_scale(self, action):
    pos_action = gym_utils.clip_and_scale_action(
        action[:, :3], self.action_space_low[:3], self.action_space_high[:3]
    )
    rot_action = action[:, 3:].clone()
    rot_norm = torch.linalg.norm(rot_action, axis=1)
    rot_action[rot_norm > 1] = torch.mul(
        rot_action, 1 / rot_norm[:, None]
    )[rot_norm > 1]
    rot_action = rot_action * self.config.rot_upper
    return torch.hstack([pos_action, rot_action])


def _cross_coupled_scale(self, action):
    out = _sign_preserving_scale(self, action)
    out[:, 4] = out[:, 4] + 0.25 * out[:, 3]
    return out


def _inverse_delta_pose(expected_euler):
    expected_euler = torch.tensor(expected_euler, dtype=torch.float64)
    desired_quaternion = rotation_conversions.matrix_to_quaternion(
        rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")
    )
    inverse_quaternion = rotation_conversions.quaternion_invert(desired_quaternion)
    return (
        expected_euler,
        sapien.Pose(
            np.array([0.01, -0.02, 0.03]),
            inverse_quaternion.numpy(),
        ),
    )


@pytest.mark.parametrize("sign_preserving_controller", [False, True])
@pytest.mark.parametrize(
    "expected_euler",
    [
        [0.08, -0.06, 0.05],
        [-0.04, 0.07, -0.03],
        [0.11, 0.02, -0.09],
    ],
)
def test_converter_inverts_actual_controller_contract(
    sign_preserving_controller, expected_euler
):
    controller = _controller()
    if sign_preserving_controller:
        controller._clip_and_scale_action = MethodType(
            _sign_preserving_scale, controller
        )

    expected_euler, delta_pose = _inverse_delta_pose(expected_euler)
    action = delta_pose_to_pd_ee_delta(controller, delta_pose)
    realized = controller._clip_and_scale_action(
        torch.as_tensor(
            action, dtype=controller.action_space_low.dtype
        )[None, :]
    )[0]

    np.testing.assert_allclose(realized[:3].numpy(), delta_pose.p, atol=1e-6)
    np.testing.assert_allclose(
        realized[3:].numpy(), expected_euler.numpy(), atol=1e-6
    )


@pytest.mark.parametrize("sign_preserving_controller", [False, True])
def test_infeasible_rotation_preserves_caller_retry_signal(
    sign_preserving_controller,
):
    controller = _controller()
    if sign_preserving_controller:
        controller._clip_and_scale_action = MethodType(
            _sign_preserving_scale, controller
        )

    desired = np.array([10.0, 0.0, 0.0])
    normalized, saturated = _normalized_pd_ee_rotation_action(
        controller, desired
    )

    assert saturated
    assert np.linalg.norm(normalized) > 1.0

    # The trajectory-conversion caller owns clipping + residual retries.
    # Preserve the >1 norm signal until that boundary.
    clipped = normalized / np.linalg.norm(normalized)
    action = torch.zeros((1, 6), dtype=controller.action_space_low.dtype)
    action[0, 3:] = torch.as_tensor(clipped)
    realized = controller._clip_and_scale_action(action)[0, 3:].numpy()

    assert realized[0] > 0
    assert realized[1] == pytest.approx(0.0, abs=1e-12)
    assert realized[2] == pytest.approx(0.0, abs=1e-12)
    assert abs(realized[0]) == pytest.approx(2 * pi)


def test_converter_fails_closed_for_cross_coupled_rotation_mapping():
    controller = _controller()
    controller._clip_and_scale_action = MethodType(
        _cross_coupled_scale, controller
    )

    with pytest.raises(RuntimeError, match="not axis-separable"):
        _normalized_pd_ee_rotation_action(
            controller, np.array([0.1, 0.0, 0.0])
        )
