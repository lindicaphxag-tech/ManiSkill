#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

from mani_skill.trajectory import replay_trajectory
from mani_skill.trajectory.utils.actions import conversion as conv
from mani_skill.utils import io_utils
from mani_skill.utils.geometry import rotation_conversions


def _jsonable(x):
    if isinstance(x, torch.Tensor):
        x = x.detach().cpu()
        if x.numel() == 1:
            return x.item()
        return x.numpy().tolist()
    if isinstance(x, np.ndarray):
        if x.size == 1:
            return x.reshape(-1)[0].item()
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (bool, int, float, str)) or x is None:
        return x
    return repr(x)


def _rotation_angle_deg(q) -> float:
    q = torch.as_tensor(q, dtype=torch.float64)
    if q.ndim > 1:
        q = q[0]
    q = q / torch.linalg.norm(q)
    matrix = rotation_conversions.quaternion_to_matrix(q)
    cosine = torch.clamp((torch.trace(matrix) - 1.0) / 2.0, -1.0, 1.0)
    return float(torch.rad2deg(torch.arccos(cosine)).item())


def _norm3(x) -> float:
    x = torch.as_tensor(x, dtype=torch.float64)
    return float(torch.linalg.norm(x.reshape(-1)[:3]).item())


def _success(info) -> bool:
    if "success" not in info:
        return False
    value = info["success"]
    if isinstance(value, torch.Tensor):
        return bool(value.detach().cpu().reshape(-1)[0].item())
    if isinstance(value, np.ndarray):
        return bool(value.reshape(-1)[0])
    return bool(value)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--traj-path", required=True)
    p.add_argument("--target-episode", type=int, required=True)
    p.add_argument("--variant", required=True)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    metadata = io_utils.load_json(args.traj_path.replace(".h5", ".json"))
    episodes = metadata["episodes"]
    target_ordinal = next(
        i for i, episode in enumerate(episodes)
        if int(episode["episode_id"]) == args.target_episode
    )
    count = target_ordinal + 1

    original = conv.from_pd_joint_pos_to_ee
    invocation = {"index": -1}
    records = []
    target_final = {}

    def traced_from_pd_joint_pos_to_ee(
        output_mode: str,
        ori_actions,
        ori_env,
        env,
        render=False,
        pbar=None,
        verbose=False,
    ):
        invocation["index"] += 1
        if invocation["index"] != target_ordinal:
            return original(
                output_mode,
                ori_actions,
                ori_env,
                env,
                render=render,
                pbar=pbar,
                verbose=verbose,
            )

        n = len(ori_actions)
        if pbar is not None:
            pbar.reset(total=n)

        ori_controller = ori_env.unwrapped.agent.controller
        controller = env.unwrapped.agent.controller
        ori_arm_controller = ori_controller.controllers["arm"]
        arm_controller = controller.controllers["arm"]
        target_controller_is_delta = arm_controller.config.use_delta

        ee_link = arm_controller.ee_link
        pos_only = arm_controller.config.frame == "root_translation"
        use_target = arm_controller.config.use_target is True
        pin_model = ori_controller.articulation.create_pinocchio_model()
        info = {}

        for t in range(n):
            if pbar is not None:
                pbar.update()

            ori_action = conv.common.to_tensor(
                ori_actions[t], device=env.unwrapped.device
            )
            ori_action_dict = conv.common.to_tensor(
                ori_controller.to_action_dict(ori_action),
                device=env.unwrapped.device,
            )
            output_action_dict = conv.common.to_tensor(
                ori_action_dict.copy(), device=env.unwrapped.device
            )
            ori_env.step(ori_action)

            full_qpos = ori_controller.articulation.get_qpos()
            full_qpos[:, ori_arm_controller.active_joint_indices] = (
                ori_arm_controller._target_qpos
            )
            pin_model.compute_forward_kinematics(full_qpos.cpu().numpy()[0])
            target_ee_pose_pin = conv.Pose.create(
                ori_controller.articulation.pose.sp
                * pin_model.get_link_pose(arm_controller.ee_link.index)
            )

            flag = True
            for inner in range(4):
                if not target_controller_is_delta:
                    raise RuntimeError(
                        "trace currently expects delta target controller"
                    )

                delta_q = [1, 0, 0, 0]
                if "root_translation" in arm_controller.config.frame:
                    if use_target:
                        delta_position = (
                            target_ee_pose_pin.p
                            - arm_controller._target_pose.p
                            - arm_controller.articulation.pose.p
                        )
                    else:
                        delta_position = target_ee_pose_pin.p - ee_link.pose.p

                if "root_aligned_body_rotation" in arm_controller.config.frame:
                    if use_target:
                        delta_q = (
                            arm_controller._target_pose.sp
                            * target_ee_pose_pin.sp.inv()
                        ).q
                    else:
                        delta_q = (
                            ee_link.pose.sp * target_ee_pose_pin.sp.inv()
                        ).q

                pre_pos_error = _norm3(delta_position)
                pre_rot_error = _rotation_angle_deg(delta_q)

                delta_pose = conv.sapien.Pose(
                    delta_position.cpu().numpy()[0], delta_q
                )
                arm_action = conv.delta_pose_to_pd_ee_delta(
                    arm_controller, delta_pose, pos_only=pos_only
                )
                raw_action = np.asarray(arm_action, dtype=np.float64).copy()
                raw_pos_max = float(np.abs(raw_action[:3]).max())
                raw_rot_norm = (
                    float(np.linalg.norm(raw_action[3:]))
                    if not pos_only else 0.0
                )

                pos_clipped = raw_pos_max > 1.0
                rot_clipped = (not pos_only) and raw_rot_norm > 1.0

                if pos_clipped:
                    arm_action[:3] = np.clip(arm_action[:3], -1, 1)
                    flag = False
                if rot_clipped:
                    arm_action[3:] = arm_action[3:] / np.linalg.norm(
                        arm_action[3:]
                    )
                    flag = False

                output_action_dict["arm"] = conv.common.to_tensor(
                    arm_action, device=env.unwrapped.device
                )
                output_action = controller.from_action_dict(output_action_dict)

                ee_before_p = _jsonable(ee_link.pose.p)
                ee_before_q = _jsonable(ee_link.pose.q)
                _, _, _, _, info = env.step(output_action)
                ee_after_p = _jsonable(ee_link.pose.p)
                ee_after_q = _jsonable(ee_link.pose.q)

                if use_target:
                    post_delta_position = (
                        target_ee_pose_pin.p
                        - arm_controller._target_pose.p
                        - arm_controller.articulation.pose.p
                    )
                    post_delta_q = (
                        arm_controller._target_pose.sp
                        * target_ee_pose_pin.sp.inv()
                    ).q
                else:
                    post_delta_position = target_ee_pose_pin.p - ee_link.pose.p
                    post_delta_q = (
                        ee_link.pose.sp * target_ee_pose_pin.sp.inv()
                    ).q

                record = {
                    "episode_id": args.target_episode,
                    "source_step": int(t),
                    "inner_iteration": int(inner),
                    "pre_position_error": pre_pos_error,
                    "pre_rotation_error_deg": pre_rot_error,
                    "raw_action": raw_action.tolist(),
                    "raw_position_max_abs": raw_pos_max,
                    "raw_rotation_norm": raw_rot_norm,
                    "position_clipped": bool(pos_clipped),
                    "rotation_clipped": bool(rot_clipped),
                    "applied_arm_action": np.asarray(
                        arm_action, dtype=np.float64
                    ).tolist(),
                    "retry_required": bool(not flag),
                    "ee_before_position": ee_before_p,
                    "ee_before_quaternion": ee_before_q,
                    "ee_after_position": ee_after_p,
                    "ee_after_quaternion": ee_after_q,
                    "post_position_error": _norm3(post_delta_position),
                    "post_rotation_error_deg": _rotation_angle_deg(
                        post_delta_q
                    ),
                    "task_success": _success(info),
                    "info": _jsonable(info),
                }
                records.append(record)

                if flag:
                    break

        target_final.update(
            {
                "success": _success(info),
                "final_info": _jsonable(info),
                "source_steps": int(n),
            }
        )
        return info

    conv.from_pd_joint_pos_to_ee = traced_from_pd_joint_pos_to_ee
    try:
        replay_args = replay_trajectory.Args(
            traj_path=args.traj_path,
            sim_backend="physx_cpu",
            obs_mode="state",
            target_control_mode="pd_ee_delta_pose",
            save_traj=False,
            use_first_env_state=True,
            count=count,
            num_envs=1,
        )
        replay_trajectory.main(replay_args)
    finally:
        conv.from_pd_joint_pos_to_ee = original

    iterations_by_step = {}
    for row in records:
        iterations_by_step.setdefault(str(row["source_step"]), 0)
        iterations_by_step[str(row["source_step"])] += 1

    report = {
        "schema_version": 1,
        "variant": args.variant,
        "source_sha": args.source_sha,
        "target_episode": args.target_episode,
        "target_ordinal": target_ordinal,
        "trace_record_count": len(records),
        "rotation_clip_events": sum(
            int(row["rotation_clipped"]) for row in records
        ),
        "position_clip_events": sum(
            int(row["position_clipped"]) for row in records
        ),
        "retried_source_steps": sum(
            int(v > 1) for v in iterations_by_step.values()
        ),
        "max_inner_iterations": max(iterations_by_step.values(), default=0),
        "iterations_by_source_step": iterations_by_step,
        "final": target_final,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
