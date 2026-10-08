"""Exact-head production-controller parity on software-Vulkan CPU simulator.

This is NOT a trained policy test. It tests that #1495 emits a normalized
single-step action which a real initialized ManiSkill PDEEPoseController
maps back to the requested small XYZ Euler motion. Physical task success,
training, multi-step IK accuracy, and hardware safety remain unmeasured.
"""
from __future__ import annotations

import json
import os
import subprocess

import numpy as np
import torch


EXPECTED_HEAD = "69facfaafaa0ef233d36ef19e6cd9a0f03532ee0"


def main():
    actual_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"not the exact upstream #1495 head: {actual_head}")

    import gymnasium as gym
    import sapien
    import mani_skill.envs
    from mani_skill.agents.controllers import PDEEPoseController
    from mani_skill.trajectory.utils.actions.conversion import (
        delta_pose_to_pd_ee_delta,
        _get_controller_rotation_action_scale,
    )
    from mani_skill.utils.geometry import rotation_conversions as rot

    print("SAPIEN SOURCE SHA", actual_head, flush=True)
    env = gym.make(
        "PickCube-v1",
        obs_mode="state",
        control_mode="pd_ee_delta_pose",
        sim_backend="physx_cpu",
        render_mode=None,
        # Official ManiSkill API explicitly disables Vulkan RenderSystem.
        # State-only PhysX CPU control does not need a graphics device.
        render_backend="none",
    )
    try:
        env.reset(seed=1495)
        arm = env.unwrapped.agent.controller.controllers["arm"]
        if not isinstance(arm, PDEEPoseController):
            raise RuntimeError(f"unexpected native controller: {type(arm)}")
        scale = _get_controller_rotation_action_scale(arm)
        # Small unsaturated 3-axis compound XYZ Euler pose.
        expected = torch.tensor([0.051, -0.042, 0.063], dtype=torch.float64)
        quaternion = rot.matrix_to_quaternion(
            rot.euler_angles_to_matrix(expected, "XYZ")
        )
        target_inverse = rot.quaternion_invert(quaternion)
        delta = sapien.Pose(
            np.array([0.001, -0.002, 0.003], dtype=np.float64),
            target_inverse.numpy(),
        )
        normalized = delta_pose_to_pd_ee_delta(arm, delta)
        action = torch.as_tensor(
            normalized, dtype=arm.action_space_low.dtype,
            device=arm.action_space_low.device
        )[None, :]
        if action.shape != (1, 6):
            raise RuntimeError("unexpected production action shape")
        if torch.linalg.vector_norm(action[:, 3:]).item() >= 1.0:
            raise RuntimeError("smoke did not cover intended unsaturated chart")
        mapped = arm._clip_and_scale_action(action)[0, 3:]
        actual = rot.euler_angles_to_matrix(mapped.to(torch.float64), "XYZ")
        target = rot.euler_angles_to_matrix(expected, "XYZ")
        residual = float(torch.linalg.matrix_norm(actual - target).item())
        if residual > 1e-5:
            raise AssertionError(
                f"production controller and converter disagree: residual={residual}"
            )
        step_action = np.zeros(env.action_space.shape, dtype=np.float32)
        _, _, terminated, truncated, _ = env.step(step_action)
        result = {
            "status": "production_controller_native_cpu_parity_pass",
            "upstream_pr1495_head": actual_head,
            "python_env": "PickCube-v1/pd_ee_delta_pose/physx_cpu",
            "test": "one small non-saturated compound XYZ Euler rotation",
            "observed_signed_scale": [float(x) for x in scale],
            "controller_euler_rotation_matrix_residual": residual,
            "simulator_step_completed": True,
            "limitations": [
                "No learned-policy evaluation or PegInsertionSide training",
                "One deterministic source/pose/episode, no broad task performance",
                "Rendering is explicitly disabled; no Vulkan graphics path is tested",
            ],
        }
        text = json.dumps(result, sort_keys=True, indent=2)
        print(text, flush=True)
        with open("native_cpu_controller_parity.json", "w", encoding="utf-8") as out:
            out.write(text + "\n")
    finally:
        env.close()


if __name__ == "__main__":
    main()
