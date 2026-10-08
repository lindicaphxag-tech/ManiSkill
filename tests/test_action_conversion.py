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
from mani_skill.utils import gym_utils
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
def test_delta_pose_conversion_encodes_xyz_euler_independent_of_controller_scaling(
    expected_euler,
):
    expected_euler = torch.tensor(expected_euler)
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

    physical_delta = np.r_[
        [0.01, -0.02, 0.03],
        expected_euler.numpy(),
    ]
    expected_action = gym_utils.inv_scale_action(
        physical_delta,
        controller.action_space_low.numpy(),
        controller.action_space_high.numpy(),
    )

    # This PR only fixes the converter's representation contract. The separate
    # controller sign bug is tracked by upstream PR #1472.
    np.testing.assert_allclose(action, expected_action, atol=1e-6)
