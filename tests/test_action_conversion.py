from math import pi
from types import MethodType, SimpleNamespace

import numpy as np
import pytest
import sapien
import torch

from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory.utils.actions.conversion import (
    delta_pose_to_pd_ee_delta,
    euler_xyz_from_quaternion,
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
    controller.action_space_low = torch.tensor([-0.1] * 3 + [-2 * pi] * 3)
    controller.action_space_high = torch.tensor([0.1] * 3 + [2 * pi] * 3)
    return controller


def _sign_preserving_scale(self, action):
    pos_action = gym_utils.clip_and_scale_action(
        action[:, :3], self.action_space_low[:3], self.action_space_high[:3]
    )
    rot_action = action[:, 3:].clone()
    rot_norm = torch.linalg.norm(rot_action, axis=1)
    rot_action[rot_norm > 1] = torch.mul(rot_action, 1 / rot_norm[:, None])[
        rot_norm > 1
    ]
    rot_action = rot_action * self.config.rot_upper
    return torch.hstack([pos_action, rot_action])


def _inverse_delta_pose(expected_euler):
    expected_euler = torch.tensor(expected_euler)
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


@pytest.mark.parametrize(
    "expected_euler",
    [
        [0.31, -0.27, 0.42],
        [0.50, 0.50, 0.50],
        [-0.40, 0.20, 0.35],
        [0.00, 0.60, -0.45],
    ],
)
def test_quaternion_conversion_matches_pd_ee_xyz_euler_contract(expected_euler):
    expected_euler = torch.tensor(expected_euler)
    quaternion = rotation_conversions.matrix_to_quaternion(
        rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")
    )

    actual_euler = euler_xyz_from_quaternion(quaternion.numpy())
    actual_matrix = rotation_conversions.euler_angles_to_matrix(
        torch.from_numpy(actual_euler), "XYZ"
    )
    expected_matrix = rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")

    torch.testing.assert_close(actual_matrix, expected_matrix, atol=1e-6, rtol=1e-6)


@pytest.mark.parametrize(
    "sign_preserving_controller",
    [False, True],
)
@pytest.mark.parametrize(
    "expected_euler",
    [
        [0.08, -0.06, 0.05],
        [-0.04, 0.07, -0.03],
    ],
)
def test_delta_pose_conversion_inverts_actual_controller_rotation_mapping(
    sign_preserving_controller, expected_euler
):
    controller = _controller()
    if sign_preserving_controller:
        controller._clip_and_scale_action = MethodType(
            _sign_preserving_scale,
            controller,
        )

    expected_euler, delta_pose = _inverse_delta_pose(expected_euler)
    action = delta_pose_to_pd_ee_delta(controller, delta_pose)
    realized = controller._clip_and_scale_action(
        torch.as_tensor(action, dtype=controller.action_space_low.dtype)[None, :]
    )[0]

    np.testing.assert_allclose(
        realized[:3].cpu().numpy(),
        delta_pose.p,
        atol=1e-6,
    )
    np.testing.assert_allclose(
        realized[3:].cpu().numpy(),
        expected_euler.numpy(),
        atol=1e-6,
    )


def test_current_negative_rotation_gain_requires_negative_normalized_action():
    controller = _controller()
    expected_euler, delta_pose = _inverse_delta_pose([0.08, 0.0, 0.0])

    action = delta_pose_to_pd_ee_delta(controller, delta_pose)

    assert action[3] < 0
    realized = controller._clip_and_scale_action(
        torch.as_tensor(action, dtype=controller.action_space_low.dtype)[None, :]
    )[0, 3:]
    np.testing.assert_allclose(realized.cpu().numpy(), expected_euler.numpy(), atol=1e-6)
