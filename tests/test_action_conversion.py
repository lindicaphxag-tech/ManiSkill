from math import pi
from types import SimpleNamespace

import numpy as np
import pytest
import sapien
import torch

from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory.utils.actions.conversion import (
    delta_pose_to_pd_ee_delta,
    euler_xyz_from_quaternion,
)
from mani_skill.utils.geometry import rotation_conversions


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
    "expected_euler",
    [
        [0.31, -0.27, 0.42],
        [0.50, 0.50, 0.50],
        [-0.40, 0.20, 0.35],
        [0.00, 0.60, -0.45],
    ],
)
def test_delta_pose_conversion_reconstructs_target_with_legacy_controller_scale(
    expected_euler,
):
    expected_euler = torch.tensor(expected_euler)
    quaternion = rotation_conversions.matrix_to_quaternion(
        rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")
    )
    controller = object.__new__(PDEEPoseController)
    controller.config = SimpleNamespace(
        use_delta=True, normalize_action=True, rot_lower=-2 * pi, rot_upper=2 * pi
    )
    controller.action_space_low = torch.tensor([-0.1] * 3 + [-2 * pi] * 3)
    controller.action_space_high = torch.tensor([0.1] * 3 + [2 * pi] * 3)
    inverse_delta = rotation_conversions.quaternion_invert(quaternion)
    delta_pose = sapien.Pose(np.array([0.01, -0.02, 0.03]), inverse_delta.numpy())

    action = delta_pose_to_pd_ee_delta(controller, delta_pose)

    mapped_action = controller._clip_and_scale_action(
        torch.as_tensor(action, dtype=torch.float32)[None]
    )[0]
    np.testing.assert_allclose(
        mapped_action[:3].numpy(), [0.01, -0.02, 0.03], atol=1e-6
    )
    actual_rotation = rotation_conversions.euler_angles_to_matrix(
        mapped_action[3:], "XYZ"
    )
    expected_rotation = rotation_conversions.euler_angles_to_matrix(
        expected_euler, "XYZ"
    )
    torch.testing.assert_close(actual_rotation, expected_rotation, atol=1e-6, rtol=1e-6)


def test_delta_pose_conversion_tracks_positive_rot_upper_controller_scale():
    expected_euler = torch.tensor([0.31, -0.27, 0.42])
    quaternion = rotation_conversions.matrix_to_quaternion(
        rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")
    )
    controller = object.__new__(PDEEPoseController)
    controller.config = SimpleNamespace(
        use_delta=True, normalize_action=True, rot_lower=-2 * pi, rot_upper=2 * pi
    )
    controller.action_space_low = torch.tensor([-0.1] * 3 + [-2 * pi] * 3)
    controller.action_space_high = torch.tensor([0.1] * 3 + [2 * pi] * 3)
    # Model #1472's positive rot_upper mapping; the production converter probes
    # the active mapper instead of assuming which config field it uses.
    controller._clip_and_scale_action = lambda action: torch.cat(
        [action[:, :3], action[:, 3:] * (2 * pi)], dim=1
    )
    inverse_delta = rotation_conversions.quaternion_invert(quaternion)
    delta_pose = sapien.Pose(np.array([0.01, -0.02, 0.03]), inverse_delta.numpy())

    action = delta_pose_to_pd_ee_delta(controller, delta_pose)
    mapped_rotation = controller._clip_and_scale_action(
        torch.as_tensor(action, dtype=torch.float32)[None]
    )[0, 3:]
    actual_rotation = rotation_conversions.euler_angles_to_matrix(
        mapped_rotation, "XYZ"
    )
    expected_rotation = rotation_conversions.euler_angles_to_matrix(
        expected_euler, "XYZ"
    )
    torch.testing.assert_close(actual_rotation, expected_rotation, atol=1e-6, rtol=1e-6)
