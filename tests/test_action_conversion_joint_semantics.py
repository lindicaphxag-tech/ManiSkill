from types import SimpleNamespace

import numpy as np
import torch

from mani_skill.agents.controllers import PDJointPosController
from mani_skill.trajectory.utils.actions.conversion import (
    normalized_pd_joint_action_to_physical,
    qpos_to_pd_joint_pos,
)
from mani_skill.utils import gym_utils


def _controller(*, use_delta, low, high, normalize_action=True):
    controller = object.__new__(PDJointPosController)
    controller.config = SimpleNamespace(
        use_delta=use_delta,
        normalize_action=normalize_action,
    )
    controller.action_space_low = torch.tensor(low, dtype=torch.float64)
    controller.action_space_high = torch.tensor(high, dtype=torch.float64)
    return controller


def test_normalized_delta_action_decodes_in_physical_joint_units():
    controller = _controller(
        use_delta=True,
        low=[-0.2, -0.4],
        high=[0.2, 0.4],
    )
    physical = normalized_pd_joint_action_to_physical(
        controller,
        np.array([0.5, -0.5]),
    )
    np.testing.assert_allclose(physical, [0.1, -0.2], atol=1e-12)


def test_physical_joint_target_round_trips_through_normalized_target_controller():
    controller = _controller(
        use_delta=False,
        low=[-2.0, -1.0],
        high=[2.0, 3.0],
    )
    target_qpos = np.array([0.5, 2.0])
    native_action = qpos_to_pd_joint_pos(controller, target_qpos)

    reconstructed = gym_utils.clip_and_scale_action(
        torch.tensor(native_action, dtype=torch.float64),
        controller.action_space_low,
        controller.action_space_high,
    ).numpy()

    np.testing.assert_allclose(reconstructed, target_qpos, atol=1e-12)


def test_delta_to_absolute_semantic_composition_preserves_target_qpos():
    source = _controller(
        use_delta=True,
        low=[-0.1, -0.2],
        high=[0.1, 0.2],
    )
    target = _controller(
        use_delta=False,
        low=[-2.0, -2.0],
        high=[2.0, 2.0],
    )
    current_qpos = np.array([0.2, -0.3])
    source_action = np.array([0.5, -0.5])

    delta_qpos = normalized_pd_joint_action_to_physical(source, source_action)
    desired_qpos = current_qpos + delta_qpos
    target_action = qpos_to_pd_joint_pos(target, desired_qpos)
    target_physical = gym_utils.clip_and_scale_action(
        torch.tensor(target_action, dtype=torch.float64),
        target.action_space_low,
        target.action_space_high,
    ).numpy()

    np.testing.assert_allclose(target_physical, desired_qpos, atol=1e-12)


def test_source_normalized_action_is_clipped_before_physical_scaling():
    source = _controller(
        use_delta=True,
        low=[-0.1],
        high=[0.1],
    )
    physical = normalized_pd_joint_action_to_physical(
        source,
        np.array([3.0]),
    )
    np.testing.assert_allclose(physical, [0.1], atol=1e-12)


def test_unnormalized_target_controller_uses_physical_qpos_directly():
    controller = _controller(
        use_delta=False,
        low=[-1.0],
        high=[1.0],
        normalize_action=False,
    )
    target_qpos = np.array([0.35])
    np.testing.assert_allclose(
        qpos_to_pd_joint_pos(controller, target_qpos),
        target_qpos,
        atol=1e-12,
    )
