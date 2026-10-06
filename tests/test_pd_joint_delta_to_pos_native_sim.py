import numpy as np
import pytest
import torch
import gymnasium as gym

import mani_skill.envs  # noqa: F401
from mani_skill.trajectory.utils.actions.conversion import (
    from_pd_joint_delta_pos,
)
from mani_skill.utils import gym_utils


def _deterministic_source_action(env):
    controller = env.unwrapped.agent.controller
    action = np.zeros(env.action_space.shape, dtype=np.float32)
    action_dict = controller.to_action_dict(action)

    arm = np.asarray(action_dict["arm"], dtype=np.float32)
    # Nontrivial, well-inside-range deltas.  Values are normalized source
    # commands, not physical qpos deltas.
    pattern = np.array([0.35, -0.25, 0.20, -0.15, 0.10, -0.08, 0.05], dtype=np.float32)
    arm[...] = pattern[: arm.shape[0]]
    action_dict["arm"] = arm

    # Preserve the gripper action at zero so both control modes issue the same
    # non-arm command.
    flat = controller.from_action_dict(
        {key: torch.as_tensor(value, device=env.unwrapped.device)
         for key, value in action_dict.items()}
    )
    return flat.detach().cpu().numpy()


@pytest.mark.parametrize("seed", [7, 29])
def test_native_panda_delta_to_absolute_replay_preserves_controller_target(seed):
    """The converted absolute command must drive the same native Panda target.

    This is an actual ManiSkill PickCube CPU-simulator assay, not a controller
    mock.  Both environments start from the exact same simulator state.
    """
    source = gym.make(
        "PickCube-v1",
        obs_mode="state",
        control_mode="pd_joint_delta_pos",
        sim_backend="cpu",
    )
    target = gym.make(
        "PickCube-v1",
        obs_mode="state",
        control_mode="pd_joint_pos",
        sim_backend="cpu",
    )
    try:
        source.reset(seed=seed)
        target.reset(seed=seed)
        target.unwrapped.set_state_dict(source.unwrapped.get_state_dict())

        source_controller = source.unwrapped.agent.controller
        source_arm = source_controller.controllers["arm"]
        target_arm = target.unwrapped.agent.controller.controllers["arm"]

        action = _deterministic_source_action(source)
        source_action_dict = source_controller.to_action_dict(action)

        # Reproduce the old conversion boundary: trajectory rows are NumPy,
        # while gym_utils.clip_and_scale_action is tensor-only.  This is the
        # concrete upstream failure mode that the patched decode/encode path
        # removes.
        with pytest.raises(TypeError):
            gym_utils.clip_and_scale_action(
                source_action_dict["arm"],
                source_arm.config.lower,
                source_arm.config.upper,
            )

        qpos_before = source_arm.qpos.detach().cpu().numpy().copy()

        from_pd_joint_delta_pos(
            output_mode="pd_joint_pos",
            ori_actions=np.asarray([action]),
            ori_env=source,
            env=target,
        )

        source_target = source_arm._target_qpos.detach().cpu().numpy()
        target_target = target_arm._target_qpos.detach().cpu().numpy()
        np.testing.assert_allclose(target_target, source_target, atol=1e-7, rtol=1e-7)

        # Both controllers ultimately issue the same physical arm target and
        # have identical PD gains, so one native control step from an identical
        # simulator state should remain state-equivalent up to simulator noise.
        source_qpos = source_arm.qpos.detach().cpu().numpy()
        target_qpos = target_arm.qpos.detach().cpu().numpy()
        np.testing.assert_allclose(target_qpos, source_qpos, atol=1e-6, rtol=1e-6)

        # Ensure the assay was not vacuous.
        assert np.linalg.norm(source_target - qpos_before) > 1e-5
    finally:
        source.close()
        target.close()
