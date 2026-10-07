"""Sidecar native rollout for exact ManiSkill PR #1495 source validation."""

import json
import os
import platform
from math import atan2
from pathlib import Path

import gymnasium as gym
import numpy as np
import sapien
import torch
from transforms3d.quaternions import quat2axangle

import mani_skill.envs  # noqa: F401
from mani_skill.trajectory.utils.actions.conversion import delta_pose_to_pd_ee_delta
from mani_skill.utils.geometry import rotation_conversions
from mani_skill.utils.gym_utils import inv_scale_action


def _orientation_error(target: torch.Tensor, actual: torch.Tensor) -> float:
    relative = rotation_conversions.quaternion_multiply(
        target, rotation_conversions.quaternion_invert(actual)
    )
    relative = relative / torch.linalg.norm(relative)
    return 2 * atan2(float(torch.linalg.norm(relative[1:])), abs(float(relative[0])))


def _legacy_axis_angle(quaternion: np.ndarray) -> np.ndarray:
    axis, angle = quat2axangle(quaternion)
    if angle > np.pi:
        angle -= 2 * np.pi
    return angle * axis


def _rollout(env, candidate: bool, steps: int, target_euler: list[float]) -> dict:
    env.reset(seed=2026)
    base = env.unwrapped
    combined = base.agent.controller
    arm = combined.controllers["arm"]
    start_q = arm.ee_pose_at_base.q[0].clone()
    target_delta = rotation_conversions.matrix_to_quaternion(
        rotation_conversions.euler_angles_to_matrix(
            torch.tensor(target_euler, dtype=start_q.dtype), "XYZ"
        )
    )
    target_q = rotation_conversions.quaternion_multiply(target_delta, start_q)
    first_command_error = None

    for step in range(steps):
        current_q = arm.ee_pose_at_base.q[0]
        inverse_delta = rotation_conversions.quaternion_multiply(
            current_q, rotation_conversions.quaternion_invert(target_q)
        )
        delta_pose = sapien.Pose(q=inverse_delta.detach().cpu().numpy())
        if candidate:
            arm_action = delta_pose_to_pd_ee_delta(arm, delta_pose)
        else:
            physical_delta = np.r_[
                np.zeros(3), _legacy_axis_angle(inverse_delta.detach().cpu().numpy())
            ]
            low = arm.action_space_low.detach().cpu().numpy()
            high = arm.action_space_high.detach().cpu().numpy()
            arm_action = inv_scale_action(physical_delta, low, high)

        action_dict = combined.to_action_dict(combined.action_space.sample())
        action_dict = {
            key: torch.as_tensor(value, device=base.device)
            for key, value in action_dict.items()
        }
        action_dict["arm"] = torch.as_tensor(arm_action, device=base.device)
        action_dict["gripper"] = torch.zeros_like(action_dict["gripper"])
        env.step(combined.from_action_dict(action_dict))
        if step == 0:
            first_command_error = _orientation_error(target_q, arm._target_pose.q[0])

    return {
        "first_command_error_rad": first_command_error,
        "final_orientation_error_rad": _orientation_error(
            target_q, arm.ee_pose_at_base.q[0]
        ),
    }


def test_pr1495_native_controller_rollout():
    env = gym.make(
        "PickCube-v1",
        obs_mode="state",
        control_mode="pd_ee_delta_pose",
        sim_backend="physx_cpu",
        render_backend=os.environ.get("MANISKILL_RENDER_BACKEND", "gpu"),
        render_mode=None,
        robot_init_qpos_noise=0.0,
    )
    try:
        cases = {
            "unsaturated_xyz": {"target": [0.035, -0.028, 0.042], "horizons": [1, 16]},
            "composed_saturated_xyz": {"target": [0.55, -0.48, 0.62], "horizons": [16, 64]},
        }
        results = {}
        for name, case in cases.items():
            results[name] = {}
            for horizon in case["horizons"]:
                results[name][str(horizon)] = {
                    "legacy": _rollout(env, False, horizon, case["target"]),
                    "pr1495": _rollout(env, True, horizon, case["target"]),
                }
    finally:
        env.close()

    one_step = results["unsaturated_xyz"]["1"]
    assert one_step["pr1495"]["first_command_error_rad"] < 1e-5
    assert one_step["pr1495"]["first_command_error_rad"] < one_step["legacy"]["first_command_error_rad"]
    assert results["unsaturated_xyz"]["16"]["pr1495"]["final_orientation_error_rad"] < 1e-3
    assert results["composed_saturated_xyz"]["64"]["pr1495"]["final_orientation_error_rad"] < 1e-3

    result = {
        "assay": "native-pickcube-pr1495-exact-head",
        "status": "passed",
        "platform": platform.platform(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "sapien": getattr(sapien, "__version__", "unknown"),
        "cuda_available": torch.cuda.is_available(),
        "render_backend": os.environ.get("MANISKILL_RENDER_BACKEND", "gpu"),
        "seed": 2026,
        "results": results,
    }
    result_path = os.environ.get("MANISKILL_ASSAY_RESULT")
    if result_path:
        Path(result_path).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
