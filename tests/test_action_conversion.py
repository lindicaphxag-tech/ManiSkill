from math import pi
from types import SimpleNamespace

import numpy as np
import sapien
import torch

from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory.utils.actions.conversion import (
    delta_pose_to_pd_ee_delta,
    euler_xyz_from_quaternion,
)
from mani_skill.utils.geometry import rotation_conversions


def test_quaternion_conversion_matches_pd_ee_xyz_euler_contract():
    expected_euler = torch.tensor([0.31, -0.27, 0.42])
    quaternion = rotation_conversions.matrix_to_quaternion(
        rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")
    )

    actual_euler = euler_xyz_from_quaternion(quaternion.numpy())
    actual_matrix = rotation_conversions.euler_angles_to_matrix(
        torch.from_numpy(actual_euler), "XYZ"
    )
    expected_matrix = rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")

    torch.testing.assert_close(actual_matrix, expected_matrix, atol=1e-6, rtol=1e-6)


def test_delta_pose_conversion_emits_normalized_xyz_euler_for_pose_controller():
    expected_euler = torch.tensor([0.31, -0.27, 0.42])
    quaternion = rotation_conversions.matrix_to_quaternion(
        rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")
    )
    controller = object.__new__(PDEEPoseController)
    controller.config = SimpleNamespace(use_delta=True, normalize_action=True)
    controller.action_space_low = torch.tensor([-0.1] * 3 + [-2 * pi] * 3)
    controller.action_space_high = torch.tensor([0.1] * 3 + [2 * pi] * 3)
    inverse_delta = rotation_conversions.quaternion_invert(quaternion)
    delta_pose = sapien.Pose(np.array([0.01, -0.02, 0.03]), inverse_delta.numpy())

    action = delta_pose_to_pd_ee_delta(controller, delta_pose)

    np.testing.assert_allclose(action[:3], [0.1, -0.2, 0.3], atol=1e-6)
    controller_euler = action[3:] * (-2 * pi)
    actual_rotation = rotation_conversions.euler_angles_to_matrix(
        torch.from_numpy(controller_euler), "XYZ"
    )
    expected_rotation = rotation_conversions.euler_angles_to_matrix(
        expected_euler, "XYZ"
    )
    torch.testing.assert_close(actual_rotation, expected_rotation, atol=1e-6, rtol=1e-6)
