import json
import sys

import gymnasium as gym
import numpy as np

import mani_skill.envs  # noqa: F401
from mani_skill.trajectory.utils.actions.conversion import from_pd_joint_delta_pos


def make_env(control_mode):
    env = gym.make(
        "PickCube-v1",
        obs_mode="state",
        control_mode=control_mode,
        sim_backend="physx_cpu",
        render_mode=None,
        robot_init_qpos_noise=0.0,
    )
    env.reset(seed=20261006)
    return env


def to_numpy(x):
    if hasattr(x, "detach"):
        x = x.detach()
    if hasattr(x, "cpu"):
        x = x.cpu()
    if hasattr(x, "numpy"):
        x = x.numpy()
    return np.asarray(x, dtype=float)


def main():
    source = make_env("pd_joint_delta_pos")
    target = make_env("pd_joint_pos")
    try:
        source.reset(seed=20261006)
        target.reset(seed=20261006)

        # Synchronize physical simulator state.  Neither of these controller
        # modes uses previous-target state for its arm semantics.
        state = source.unwrapped.get_state_dict()
        state = {k: v for k, v in state.items() if k != "controller"}
        target.unwrapped.set_state_dict(state)

        source_controller = source.unwrapped.agent.controller
        arm_start, arm_end = source_controller.action_mapping["arm"]
        action_dim = source_controller.single_action_space.shape[0]

        rng = np.random.default_rng(429)
        actions = []
        for _ in range(16):
            action = np.zeros(action_dim, dtype=np.float32)
            # Conservative normalized delta commands keep the target well within
            # normal Panda joint ranges while exercising both signs.
            action[arm_start:arm_end] = rng.uniform(
                -0.20, 0.20, size=arm_end - arm_start
            )
            actions.append(action)
        actions = np.asarray(actions, dtype=np.float32)

        from_pd_joint_delta_pos(
            output_mode="pd_joint_pos",
            ori_actions=actions,
            ori_env=source,
            env=target,
            verbose=False,
        )

        q_source = to_numpy(source.unwrapped.agent.robot.get_qpos()).reshape(-1)
        q_target = to_numpy(target.unwrapped.agent.robot.get_qpos()).reshape(-1)
        source_arm = source.unwrapped.agent.controller.controllers["arm"]
        target_arm = target.unwrapped.agent.controller.controllers["arm"]
        source_goal = to_numpy(source_arm._target_qpos).reshape(-1)
        target_goal = to_numpy(target_arm._target_qpos).reshape(-1)

        result = {
            "status": "completed",
            "steps": int(len(actions)),
            "max_abs_robot_qpos_error": float(np.max(np.abs(q_source - q_target))),
            "l2_robot_qpos_error": float(np.linalg.norm(q_source - q_target)),
            "max_abs_arm_target_error": float(
                np.max(np.abs(source_goal - target_goal))
            ),
            "l2_arm_target_error": float(np.linalg.norm(source_goal - target_goal)),
        }
        print("CST_ASSAY_JSON=" + json.dumps(result, sort_keys=True))
    except Exception as exc:
        result = {
            "status": "exception",
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }
        print("CST_ASSAY_JSON=" + json.dumps(result, sort_keys=True))
        raise
    finally:
        source.close()
        target.close()


if __name__ == "__main__":
    main()
