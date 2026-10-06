#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _quat_distance_deg(a, b) -> float:
    a = np.asarray(a, dtype=np.float64).reshape(-1)[:4]
    b = np.asarray(b, dtype=np.float64).reshape(-1)[:4]
    a /= np.linalg.norm(a)
    b /= np.linalg.norm(b)
    dot = float(np.clip(abs(np.dot(a, b)), 0.0, 1.0))
    return math.degrees(2.0 * math.acos(dot))


def _step_end_records(report: dict) -> dict[int, dict]:
    end = {}
    for row in report["records"]:
        step = int(row["source_step"])
        if step not in end or int(row["inner_iteration"]) > int(
            end[step]["inner_iteration"]
        ):
            end[step] = row
    return end


def _iteration_counts(report: dict) -> dict[int, int]:
    return {
        int(k): int(v)
        for k, v in report["iterations_by_source_step"].items()
    }


def _compare(a: dict, b: dict) -> dict:
    a_end = _step_end_records(a)
    b_end = _step_end_records(b)
    a_counts = _iteration_counts(a)
    b_counts = _iteration_counts(b)
    common_steps = sorted(set(a_end) & set(b_end))

    first_retry_mismatch = None
    for step in sorted(set(a_counts) | set(b_counts)):
        if a_counts.get(step) != b_counts.get(step):
            first_retry_mismatch = {
                "source_step": step,
                "a_iterations": a_counts.get(step),
                "b_iterations": b_counts.get(step),
            }
            break

    first_physical = None
    max_position_delta = {"value": -1.0, "source_step": None}
    max_rotation_delta = {"value": -1.0, "source_step": None}
    max_post_rot_residual_delta = {"value": -1.0, "source_step": None}

    per_step = []
    for step in common_steps:
        ra = a_end[step]
        rb = b_end[step]
        pos_a = np.asarray(ra["ee_after_position"], dtype=np.float64).reshape(-1)[:3]
        pos_b = np.asarray(rb["ee_after_position"], dtype=np.float64).reshape(-1)[:3]
        position_delta = float(np.linalg.norm(pos_a - pos_b))
        rotation_delta = _quat_distance_deg(
            ra["ee_after_quaternion"], rb["ee_after_quaternion"]
        )
        residual_delta = abs(
            float(ra["post_rotation_error_deg"])
            - float(rb["post_rotation_error_deg"])
        )
        entry = {
            "source_step": step,
            "a_iterations": a_counts.get(step),
            "b_iterations": b_counts.get(step),
            "ee_position_delta": position_delta,
            "ee_rotation_delta_deg": rotation_delta,
            "post_rotation_residual_delta_deg": residual_delta,
            "a_rotation_clipped_at_end": bool(ra["rotation_clipped"]),
            "b_rotation_clipped_at_end": bool(rb["rotation_clipped"]),
            "a_task_success": bool(ra["task_success"]),
            "b_task_success": bool(rb["task_success"]),
        }
        per_step.append(entry)

        if position_delta > max_position_delta["value"]:
            max_position_delta = {"value": position_delta, "source_step": step}
        if rotation_delta > max_rotation_delta["value"]:
            max_rotation_delta = {"value": rotation_delta, "source_step": step}
        if residual_delta > max_post_rot_residual_delta["value"]:
            max_post_rot_residual_delta = {
                "value": residual_delta,
                "source_step": step,
            }

        if (
            first_physical is None
            and (
                position_delta > 1e-6
                or rotation_delta > 1e-4
                or ra["task_success"] != rb["task_success"]
            )
        ):
            first_physical = entry

    return {
        "a_variant": a["variant"],
        "b_variant": b["variant"],
        "a_source_sha": a["source_sha"],
        "b_source_sha": b["source_sha"],
        "a_final_success": bool(a["final"].get("success", False)),
        "b_final_success": bool(b["final"].get("success", False)),
        "a_trace_record_count": int(a["trace_record_count"]),
        "b_trace_record_count": int(b["trace_record_count"]),
        "a_rotation_clip_events": int(a["rotation_clip_events"]),
        "b_rotation_clip_events": int(b["rotation_clip_events"]),
        "a_retried_source_steps": int(a["retried_source_steps"]),
        "b_retried_source_steps": int(b["retried_source_steps"]),
        "first_retry_count_mismatch": first_retry_mismatch,
        "first_post_step_physical_divergence": first_physical,
        "max_ee_position_delta": max_position_delta,
        "max_ee_rotation_delta_deg": max_rotation_delta,
        "max_post_rotation_residual_delta_deg": max_post_rot_residual_delta,
        "per_step": per_step,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--main", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--candidate-fixed", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    main_report = _load(a.main)
    candidate = _load(a.candidate)
    candidate_fixed = _load(a.candidate_fixed)

    result = {
        "schema_version": 1,
        "claim_boundary": (
            "Single-episode execution trace used to localize the first "
            "post-step physical/protocol divergence. This is diagnostic "
            "mechanism evidence, not a population success estimate."
        ),
        "target_episode": main_report["target_episode"],
        "comparisons": {
            "main_vs_candidate": _compare(main_report, candidate),
            "candidate_vs_controller_fixed": _compare(
                candidate, candidate_fixed
            ),
        },
    }

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    compact = {
        "schema_version": result["schema_version"],
        "target_episode": result["target_episode"],
        "comparisons": {},
    }
    for name, comp in result["comparisons"].items():
        compact["comparisons"][name] = {
            k: v for k, v in comp.items()
            if k != "per_step"
        }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
