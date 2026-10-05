"""Validation-only 2x2 causal assay for ManiSkill PRs #1472 and #1495.

This file lives only on the validation branch.  It decomposes two independent
semantic faults:

- #1472: normalized rotation action is scaled by the negative bound.
- #1495: an inverse delta quaternion is encoded as axis-angle although the
  controller consumes XYZ Euler.

The production PR #1495 remains a one-commit/two-file representation-only fix.
"""

from math import pi
from types import SimpleNamespace

import numpy as np
import sapien
import torch
from transforms3d.quaternions import quat2axangle

from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory.utils.actions.conversion import delta_pose_to_pd_ee_delta
from mani_skill.utils import gym_utils
from mani_skill.utils.geometry import rotation_conversions


ROT_LOWER = -2 * pi
ROT_UPPER = 2 * pi


def _controller():
    controller = object.__new__(PDEEPoseController)
    controller.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
        rot_lower=ROT_LOWER,
        rot_upper=ROT_UPPER,
    )
    controller.action_space_low = torch.tensor(
        [-0.1] * 3 + [ROT_LOWER] * 3, dtype=torch.float64
    )
    controller.action_space_high = torch.tensor(
        [0.1] * 3 + [ROT_UPPER] * 3, dtype=torch.float64
    )
    return controller


def _old_converter_action(inverse_quat: np.ndarray, controller) -> np.ndarray:
    # Exact representation used by pre-#1495 conversion.py.
    axis, angle = quat2axangle(inverse_quat)
    if angle > np.pi:
        angle = angle - 2 * np.pi
    compact_axis_angle = angle * axis
    physical = np.r_[np.zeros(3), compact_axis_angle]
    return gym_utils.inv_scale_action(
        physical,
        controller.action_space_low.numpy(),
        controller.action_space_high.numpy(),
    )


def _old_controller_rotation(normalized_action: np.ndarray) -> torch.Tensor:
    # Exact rotation part of pre-#1472 _clip_and_scale_action.
    rot_action = torch.as_tensor(normalized_action[None, 3:], dtype=torch.float64).clone()
    rot_norm = torch.linalg.norm(rot_action, axis=1)
    rot_action[rot_norm > 1] = torch.mul(rot_action, 1 / rot_norm[:, None])[
        rot_norm > 1
    ]
    return rot_action * ROT_LOWER


def _new_controller_rotation(normalized_action: np.ndarray, controller) -> torch.Tensor:
    action = torch.as_tensor(normalized_action[None, :], dtype=torch.float64)
    return controller._clip_and_scale_action(action)[:, 3:]


def _angular_error_deg(euler_xyz: torch.Tensor, expected_matrix: torch.Tensor) -> float:
    actual = rotation_conversions.euler_angles_to_matrix(euler_xyz, "XYZ")
    rel = actual.transpose(-1, -2) @ expected_matrix
    trace = rel.diagonal(dim1=-2, dim2=-1).sum(-1)
    cos_theta = ((trace - 1.0) / 2.0).clamp(-1.0, 1.0)
    return float(torch.rad2deg(torch.acos(cos_theta)).max())


def test_pr1472_pr1495_factorial_closure():
    expected_euler = torch.tensor([0.31, -0.27, 0.42], dtype=torch.float64)
    expected_matrix = rotation_conversions.euler_angles_to_matrix(expected_euler, "XYZ")
    desired_quat = rotation_conversions.matrix_to_quaternion(expected_matrix)
    inverse_quat = rotation_conversions.quaternion_invert(desired_quat)

    controller = _controller()
    delta_pose = sapien.Pose(np.zeros(3), inverse_quat.numpy())

    old_action = _old_converter_action(inverse_quat.numpy(), controller)
    new_action = delta_pose_to_pd_ee_delta(controller, delta_pose)

    errors = {
        "old_converter_old_controller": _angular_error_deg(
            _old_controller_rotation(old_action), expected_matrix
        ),
        "old_converter_pr1472_controller": _angular_error_deg(
            _new_controller_rotation(old_action, controller), expected_matrix
        ),
        "pr1495_converter_old_controller": _angular_error_deg(
            _old_controller_rotation(new_action), expected_matrix
        ),
        "pr1495_converter_pr1472_controller": _angular_error_deg(
            _new_controller_rotation(new_action, controller), expected_matrix
        ),
    }

    print(errors)

    # Baseline's two sign inversions partially cancel, but axis-angle-as-Euler
    # remains a real non-commuting representation error.
    assert errors["old_converter_old_controller"] > 1.0

    # Fixing only one semantic boundary cannot close the composed path.
    assert errors["old_converter_pr1472_controller"] > 10.0
    assert errors["pr1495_converter_old_controller"] > 10.0

    # Both independent contracts repaired => physical orientation closes.
    assert errors["pr1495_converter_pr1472_controller"] < 1e-5
