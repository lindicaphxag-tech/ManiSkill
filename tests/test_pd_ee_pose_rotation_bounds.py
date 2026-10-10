"""Regression for documented scalar and per-axis PDEEPoseController rotation bounds.

The config type permits Sequence[float], but Tensor * Python list raised
TypeError in the production controller mapper. These tests exercise the
real method rather than mocking _clip_and_scale_action.
"""

from math import pi
from types import SimpleNamespace

import pytest
import torch

from mani_skill.agents.controllers import PDEEPoseController


@pytest.mark.parametrize(
    "rot_lower",
    [
        -2 * pi,
        [-2 * pi, -pi, -0.5 * pi],
        (-2 * pi, -pi, -0.5 * pi),
    ],
)
@pytest.mark.parametrize("dtype", [torch.float32, torch.float64])
def test_pd_ee_pose_rotation_scale_accepts_documented_bound_types(rot_lower, dtype):
    """Scalar, list and tuple scales reconstruct their expected axis values."""
    bounds = (
        [rot_lower] * 3
        if isinstance(rot_lower, (int, float))
        else list(rot_lower)
    )
    controller = object.__new__(PDEEPoseController)
    controller.config = SimpleNamespace(rot_lower=rot_lower)
    controller.action_space_low = torch.tensor(
        [-0.1, -0.1, -0.1, *bounds], dtype=dtype
    )
    controller.action_space_high = torch.tensor(
        [0.1, 0.1, 0.1, *(-v for v in bounds)], dtype=dtype
    )

    action = torch.tensor(
        [[0, 0, 0, 0.2, -0.1, 0.3], [0, 0, 0, 2, -1, 0.5]],
        dtype=dtype,
    )
    actual = controller._clip_and_scale_action(action)
    unit_ball_action = action[:, 3:] / torch.clamp(
        torch.linalg.norm(action[:, 3:], dim=1, keepdim=True), min=1.0
    )
    expected_rotation = unit_ball_action * controller.action_space_low[3:]

    torch.testing.assert_close(
        actual[:, 3:], expected_rotation, rtol=0, atol=5e-6
    )
    torch.testing.assert_close(
        actual[:, :3], torch.zeros_like(action[:, :3]), rtol=0, atol=1e-7
    )
    # The controller must not mutate the caller's normalized actions.
    torch.testing.assert_close(
        action[:, 3:],
        torch.tensor([[0.2, -0.1, 0.3], [2, -1, 0.5]], dtype=dtype),
    )
