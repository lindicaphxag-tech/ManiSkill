#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

import mani_skill
from mani_skill.trajectory import replay_trajectory
from mani_skill.trajectory.utils.actions import conversion as conv
from mani_skill.utils.geometry import rotation_conversions


def _np(x):
    try:
        return conv.common.to_numpy(x)
    except Exception:
        return np.asarray(x)


def _bool(x):
    if isinstance(x, bool):
        return x
    try:
        return bool(_np(x).reshape(-1)[0])
    except Exception:
        return bool(x)


def _rotation_error_deg(inverse_q, physical_euler):
    inverse_q = torch.as_tensor(inverse_q, dtype=torch.float64)
    desired_q = rotation_conversions.quaternion_invert(inverse_q)
    desired = rotation_conversions.quaternion_to_matrix(desired_q)
    realized = rotation_conversions.euler_angles_to_matrix(
        torch.as_tensor(physical_euler, dtype=torch.float64), "XYZ"
    )
    rel = desired.transpose(-1, -2) @ realized
    trace = torch.diagonal(rel, dim1=-2, dim2=-1).sum(-1)
    cosine = torch.clamp((trace - 1.0) / 2.0, -1.0, 1.0)
    return float(torch.rad2deg(torch.acos(cosine)).item())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--traj-path", required=True)
    p.add_argument("--variant", required=True)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--expected-source-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    actual = Path(mani_skill.__file__).resolve()
    expected = args.expected_source_root.resolve()
    if expected not in actual.parents:
        raise SystemExit(f"wrong ManiSkill source imported: {actual}; expected {expected}")

    rows = []
    original = conv.from_pd_joint_pos_to_ee

    def traced(
        output_mode,
        ori_actions,
        ori_env,
        env,
        render=False,
        pbar=None,
        verbose=False,
    ):
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
        use_target = arm_controller.config.use_target == True
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
            for retry in range(4):
                if not target_controller_is_delta:
                    raise RuntimeError("episode-8 trace expects a delta target controller")

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

                delta_pose = conv.sapien.Pose(
                    delta_position.cpu().numpy()[0], delta_q
                )
                before_p = _np(ee_link.pose.p).reshape(-1, 3)[0].astype(float)
                before_q = _np(ee_link.pose.q).reshape(-1, 4)[0].astype(float)

                raw = np.asarray(
                    conv.delta_pose_to_pd_ee_delta(
                        arm_controller, delta_pose, pos_only=pos_only
                    ),
                    dtype=np.float64,
                )
                executed = raw.copy()
                pos_clipped = bool(np.max(np.abs(executed[:3])) > 1)
                if pos_clipped:
                    executed[:3] = np.clip(executed[:3], -1, 1)
                    flag = False

                raw_rot_norm = float(np.linalg.norm(executed[3:]))
                rot_clipped = bool((not pos_only) and raw_rot_norm > 1)
                if rot_clipped:
                    executed[3:] = executed[3:] / np.linalg.norm(executed[3:])
                    flag = False

                physical = arm_controller._clip_and_scale_action(
                    torch.as_tensor(
                        executed,
                        dtype=arm_controller.action_space_low.dtype,
                        device=arm_controller.action_space_low.device,
                    ).reshape(1, -1)
                )[0].detach().cpu().numpy()

                semantic_error = (
                    0.0
                    if pos_only
                    else _rotation_error_deg(delta_pose.q, physical[3:6])
                )

                output_action_dict["arm"] = conv.common.to_tensor(
                    executed, device=env.unwrapped.device
                )
                output_action = controller.from_action_dict(output_action_dict)
                _, _, _, _, info = env.step(output_action)

                after_p = _np(ee_link.pose.p).reshape(-1, 3)[0].astype(float)
                after_q = _np(ee_link.pose.q).reshape(-1, 4)[0].astype(float)
                rows.append(
                    {
                        "source_action_step": int(t),
                        "retry": int(retry),
                        "delta_position": np.asarray(
                            delta_pose.p, dtype=np.float64
                        ).tolist(),
                        "delta_q_inverse_input": np.asarray(
                            delta_pose.q, dtype=np.float64
                        ).tolist(),
                        "raw_arm_action": raw.tolist(),
                        "executed_arm_action": executed.tolist(),
                        "raw_rotation_norm": float(np.linalg.norm(raw[3:])),
                        "position_clipped": pos_clipped,
                        "rotation_clipped": rot_clipped,
                        "semantic_rotation_error_deg": semantic_error,
                        "physical_arm_action": physical.astype(float).tolist(),
                        "ee_position_before": before_p.tolist(),
                        "ee_quaternion_before": before_q.tolist(),
                        "ee_position_after": after_p.tolist(),
                        "ee_quaternion_after": after_q.tolist(),
                        "success_after_step": _bool(info.get("success", False)),
                        "would_retry": bool(not flag),
                    }
                )

                if render:
                    env.render_human()
                if flag:
                    break
        return info

    conv.from_pd_joint_pos_to_ee = traced
    try:
        replay_trajectory.main(
            replay_trajectory.Args(
                traj_path=args.traj_path,
                sim_backend="physx_cpu",
                obs_mode="state",
                target_control_mode="pd_ee_delta_pose",
                save_traj=False,
                save_video=False,
                use_first_env_state=True,
                count=1,
                num_envs=1,
                verbose=False,
            )
        )
    finally:
        conv.from_pd_joint_pos_to_ee = original

    if not rows:
        raise SystemExit("no episode-8 conversion trace rows captured")

    errors = np.asarray(
        [r["semantic_rotation_error_deg"] for r in rows], dtype=np.float64
    )
    report = {
        "schema_version": 1,
        "variant": args.variant,
        "source_sha": args.source_sha,
        "mani_skill_import": str(actual),
        "task": "PegInsertionSide-v1",
        "episode_id": 8,
        "conversion_calls": len(rows),
        "source_action_steps": len(set(r["source_action_step"] for r in rows)),
        "retry_calls": sum(r["retry"] > 0 for r in rows),
        "rotation_clipped_calls": sum(r["rotation_clipped"] for r in rows),
        "position_clipped_calls": sum(r["position_clipped"] for r in rows),
        "mean_semantic_rotation_error_deg": float(errors.mean()),
        "max_semantic_rotation_error_deg": float(errors.max()),
        "final_success": bool(rows[-1]["success_after_step"]),
        "rows": rows,
        "claim_boundary": (
            "Single-episode execution trace for the known episode-8 discordance. "
            "The trace records converter outputs, caller clipping/retry decisions, "
            "controller physical rotation inputs, local SO(3) error, and EE pose. "
            "It is a diagnostic witness, not a population performance estimate."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
