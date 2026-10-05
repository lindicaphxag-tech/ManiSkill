import json
import os
import platform
from math import acos
from pathlib import Path

import gymnasium as gym
import numpy as np
import sapien
import torch
from transforms3d.quaternions import quat2axangle

import mani_skill.envs  # noqa: F401
from mani_skill.trajectory.utils.actions.conversion import delta_pose_to_pd_ee_delta
from mani_skill.utils.geometry import rotation_conversions


def _orientation_error(target: torch.Tensor, actual: torch.Tensor) -> float:
    relative = rotation_conversions.quaternion_multiply(
        target, rotation_conversions.quaternion_invert(actual)
    )
    return 2.0 * acos(min(1.0, abs(float(relative[0]))))


def _compact_axis_angle(quaternion: np.ndarray) -> np.ndarray:
    axis, angle = quat2axangle(quaternion)
    if angle > np.pi:
        angle -= 2 * np.pi
    return angle * axis


def _rollout_orientation_error(env, repaired: bool, steps: int) -> tuple[float, float, float]:
    env.reset(seed=2026)
    base_env = env.unwrapped
    combined = base_env.agent.controller
    arm = combined.controllers["arm"]
    start_pose = arm.ee_pose_at_base
    start_q = start_pose.q[0].clone()
    desired_delta = rotation_conversions.euler_angles_to_matrix(
        torch.tensor([0.55, -0.48, 0.62], dtype=start_q.dtype), "XYZ"
    )
    desired_delta_q = rotation_conversions.matrix_to_quaternion(desired_delta)
    target_q = rotation_conversions.quaternion_multiply(desired_delta_q, start_q)

    initial_error = _orientation_error(target_q, start_q)
    first_command_error = None
    for step in range(steps):
        current_q = arm.ee_pose_at_base.q[0]
        inverse_delta_q = rotation_conversions.quaternion_multiply(
            current_q, rotation_conversions.quaternion_invert(target_q)
        )
        delta_pose = sapien.Pose(q=inverse_delta_q.detach().cpu().numpy())
        if repaired:
            arm_action = delta_pose_to_pd_ee_delta(arm, delta_pose)
        else:
            compact_rot = _compact_axis_angle(inverse_delta_q.detach().cpu().numpy())
            full_delta = np.concatenate([np.zeros(3), compact_rot])
            arm_action = base_env.agent.controller.controllers["arm"].action_space_low
            arm_action = arm_action.detach().cpu().numpy()
            high = arm.action_space_high.detach().cpu().numpy()
            arm_action = (full_delta - 0.5 * (arm_action + high)) / (
                0.5 * (high - arm_action)
            )

        action_dict = combined.to_action_dict(combined.action_space.sample())
        action_dict = {
            key: torch.as_tensor(value, device=base_env.device)
            for key, value in action_dict.items()
        }
        action_dict["arm"] = torch.as_tensor(arm_action, device=base_env.device)
        action_dict["gripper"] = torch.zeros_like(action_dict["gripper"])
        action = combined.from_action_dict(action_dict)
        env.step(action)
        if step == 0:
            first_command_error = _orientation_error(target_q, arm._target_pose.q[0])

    final_error = _orientation_error(target_q, arm.ee_pose_at_base.q[0])
    return initial_error, first_command_error, final_error


def test_native_pickcube_controller_reconstructs_multiaxis_delta_rotation():
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
        horizons = {}
        for steps in (16, 64):
            before, legacy_target_error, legacy_error = _rollout_orientation_error(
                env, repaired=False, steps=steps
            )
            repaired_before, repaired_target_error, repaired_error = (
                _rollout_orientation_error(env, repaired=True, steps=steps)
            )
            horizons[str(steps)] = {
                "initial_error_rad": before,
                "legacy_first_command_error_rad": legacy_target_error,
                "repaired_first_command_error_rad": repaired_target_error,
                "legacy_final_error_rad": legacy_error,
                "repaired_final_error_rad": repaired_error,
            }
    finally:
        env.close()

    for values in horizons.values():
        assert 0.5 < values["initial_error_rad"] < np.pi
        assert values["repaired_first_command_error_rad"] < 1e-5
        assert (
            values["repaired_first_command_error_rad"]
            < values["legacy_first_command_error_rad"]
        )
        assert values["repaired_final_error_rad"] < values["initial_error_rad"]

    result_path = os.environ.get("MANISKILL_ASSAY_RESULT")
    if result_path:
        result = {
            "assay": "native-pickcube-multiaxis-delta-pose",
            "status": "passed",
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": torch.__version__,
            "sapien": getattr(sapien, "__version__", "unknown"),
            "torch_cuda_available": torch.cuda.is_available(),
            "render_backend": os.environ.get("MANISKILL_RENDER_BACKEND", "gpu"),
            "horizon_results": horizons,
            "steps": [16, 64],
            "seed": 2026,
            "target_delta_xyz_euler_rad": [0.55, -0.48, 0.62],
        }
        Path(result_path).write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
