#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

import mani_skill
from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory import replay_trajectory
from mani_skill.trajectory.utils.actions import conversion as action_conversion
from mani_skill.utils.geometry import rotation_conversions


def _summary(values):
    a = np.asarray(values, dtype=np.float64)
    if a.size == 0:
        return {"count": 0}
    return {
        "count": int(a.size),
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "p90": float(np.percentile(a, 90)),
        "p95": float(np.percentile(a, 95)),
        "p99": float(np.percentile(a, 99)),
        "max": float(a.max()),
    }


def _rotation_error_deg(desired_matrix, realized_matrix):
    rel = desired_matrix.transpose(-1, -2) @ realized_matrix
    trace = torch.diagonal(rel, dim1=-2, dim2=-1).sum(-1)
    cosine = torch.clamp((trace - 1.0) / 2.0, -1.0, 1.0)
    return float(torch.rad2deg(torch.acos(cosine)).item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--traj-path", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--expected-source-root", type=Path, required=True)
    args = parser.parse_args()

    actual = Path(mani_skill.__file__).resolve()
    expected = args.expected_source_root.resolve()
    if expected not in actual.parents:
        raise SystemExit(
            f"wrong ManiSkill source imported: {actual}; expected under {expected}"
        )

    original = action_conversion.delta_pose_to_pd_ee_delta
    records = []

    def instrumented(controller, delta_pose, pos_only=False):
        action = original(controller, delta_pose, pos_only=pos_only)
        if pos_only or not isinstance(controller, PDEEPoseController):
            return action

        tensor = torch.as_tensor(
            action,
            dtype=controller.action_space_low.dtype,
            device=controller.device,
        ).reshape(1, -1)
        physical = controller._clip_and_scale_action(tensor.clone())[0]

        inverse_input = torch.as_tensor(
            np.asarray(delta_pose.q),
            dtype=physical.dtype,
            device=physical.device,
        )
        desired_q = rotation_conversions.quaternion_invert(inverse_input)
        desired_matrix = rotation_conversions.quaternion_to_matrix(desired_q)
        realized_matrix = rotation_conversions.euler_angles_to_matrix(
            physical[3:6], "XYZ"
        )
        error = _rotation_error_deg(desired_matrix, realized_matrix)

        requested_norm = float(
            np.linalg.norm(np.asarray(action[3:], dtype=np.float64))
        )
        position_error = float(
            torch.linalg.norm(
                physical[:3]
                - torch.as_tensor(
                    np.asarray(delta_pose.p),
                    dtype=physical.dtype,
                    device=physical.device,
                )
            ).item()
        )
        records.append(
            {
                "rotation_error_deg": error,
                "normalized_rotation_norm": requested_norm,
                "rotation_clipped": requested_norm > 1.0 + 1e-6,
                "position_error": position_error,
            }
        )
        return action

    action_conversion.delta_pose_to_pd_ee_delta = instrumented
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
                count=args.count,
                num_envs=1,
            )
        )
    finally:
        action_conversion.delta_pose_to_pd_ee_delta = original

    all_rot = [r["rotation_error_deg"] for r in records]
    unclipped = [
        r["rotation_error_deg"] for r in records if not r["rotation_clipped"]
    ]
    clipped = [r["rotation_error_deg"] for r in records if r["rotation_clipped"]]
    pos = [r["position_error"] for r in records]
    report = {
        "schema_version": 1,
        "variant": args.variant,
        "source_root": str(expected),
        "mani_skill_import": str(actual),
        "claim_boundary": (
            "Local converter-to-controller target semantic fidelity on calls "
            "generated while replaying official PegInsertionSide demonstrations; "
            "not task success, learned-policy performance, or real-robot safety."
        ),
        "calls": len(records),
        "unclipped_calls": sum(not r["rotation_clipped"] for r in records),
        "clipped_calls": sum(r["rotation_clipped"] for r in records),
        "rotation_error_deg": _summary(all_rot),
        "rotation_error_deg_unclipped": _summary(unclipped),
        "rotation_error_deg_clipped": _summary(clipped),
        "position_error": _summary(pos),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
