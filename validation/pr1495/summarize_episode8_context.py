#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from mani_skill.utils.geometry import rotation_conversions


def _arr(x):
    return np.asarray(x, dtype=np.float64)


def _quat_deg(q1, q2):
    a = torch.as_tensor(q1, dtype=torch.float64)
    b = torch.as_tensor(q2, dtype=torch.float64)
    ma = rotation_conversions.quaternion_to_matrix(a)
    mb = rotation_conversions.quaternion_to_matrix(b)
    rel = ma.transpose(-1, -2) @ mb
    trace = torch.diagonal(rel, dim1=-2, dim2=-1).sum(-1)
    cosine = torch.clamp((trace - 1.0) / 2.0, -1.0, 1.0)
    return float(torch.rad2deg(torch.acos(cosine)).item())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prefix", type=Path, required=True)
    p.add_argument("--isolated", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    prefix = json.loads(a.prefix.read_text())
    isolated = json.loads(a.isolated.read_text())
    pr = prefix["rows"]
    ir = isolated["rows"]
    n = min(len(pr), len(ir))

    rows = []
    first_request = None
    first_state = None
    first_action = None

    for i in range(n):
        x = pr[i]
        y = ir[i]
        req_pos = float(np.linalg.norm(_arr(x["delta_p"]) - _arr(y["delta_p"])))
        req_rot = _quat_deg(x["delta_q_inverse"], y["delta_q_inverse"])
        act = float(
            np.linalg.norm(
                _arr(x["physical_scaled_action"]) - _arr(y["physical_scaled_action"])
            )
        )

        ee_pos = float("nan")
        ee_rot = float("nan")
        if "ee_pose_p_before" in x and "ee_pose_p_before" in y:
            ee_pos = float(
                np.linalg.norm(
                    _arr(x["ee_pose_p_before"]) - _arr(y["ee_pose_p_before"])
                )
            )
        if "ee_pose_q_before" in x and "ee_pose_q_before" in y:
            ee_rot = _quat_deg(x["ee_pose_q_before"], y["ee_pose_q_before"])

        target_pos = float("nan")
        target_rot = float("nan")
        if "target_pose_p_before" in x and "target_pose_p_before" in y:
            target_pos = float(
                np.linalg.norm(
                    _arr(x["target_pose_p_before"])
                    - _arr(y["target_pose_p_before"])
                )
            )
        if "target_pose_q_before" in x and "target_pose_q_before" in y:
            target_rot = _quat_deg(
                x["target_pose_q_before"], y["target_pose_q_before"]
            )

        row = {
            "call_index": i,
            "request_position_delta_m": req_pos,
            "request_rotation_delta_deg": req_rot,
            "physical_action_l2": act,
            "ee_position_delta_m_before": ee_pos,
            "ee_rotation_delta_deg_before": ee_rot,
            "target_position_delta_m_before": target_pos,
            "target_rotation_delta_deg_before": target_rot,
            "prefix_would_clip": x["would_clip_rotation"],
            "isolated_would_clip": y["would_clip_rotation"],
        }
        rows.append(row)

        if first_request is None and (req_pos > 1e-7 or req_rot > 1e-5):
            first_request = i
        if first_action is None and act > 1e-7:
            first_action = i
        if first_state is None and (
            (np.isfinite(ee_pos) and ee_pos > 1e-7)
            or (np.isfinite(ee_rot) and ee_rot > 1e-5)
            or (np.isfinite(target_pos) and target_pos > 1e-7)
            or (np.isfinite(target_rot) and target_rot > 1e-5)
        ):
            first_state = i

    report = {
        "schema_version": 1,
        "episode_id": 8,
        "variant": prefix["variant"],
        "prefix_call_count": len(pr),
        "isolated_call_count": len(ir),
        "aligned_call_count": n,
        "first_request_divergence_call": first_request,
        "first_controller_state_divergence_call": first_state,
        "first_physical_action_divergence_call": first_action,
        "clip_schedule_identical_on_aligned_calls": all(
            bool(pr[i]["would_clip_rotation"]) == bool(ir[i]["would_clip_rotation"])
            for i in range(n)
        ),
        "prefix_clip_calls": [
            i for i, row in enumerate(pr) if row["would_clip_rotation"]
        ],
        "isolated_clip_calls": [
            i for i, row in enumerate(ir) if row["would_clip_rotation"]
        ],
        "max_request_position_delta_m": max(
            (row["request_position_delta_m"] for row in rows), default=0.0
        ),
        "max_request_rotation_delta_deg": max(
            (row["request_rotation_delta_deg"] for row in rows), default=0.0
        ),
        "max_physical_action_l2": max(
            (row["physical_action_l2"] for row in rows), default=0.0
        ),
        "call0": rows[0] if rows else None,
        "rows": rows,
        "claim_boundary": (
            "Compares the same candidate and same recorded episode under two replay "
            "contexts: after a serial prefix versus in a fresh isolated replay. "
            "Differences identify context dependence but do not by themselves locate "
            "unobserved simulator or controller state."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    compact = dict(report)
    compact.pop("rows")
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
