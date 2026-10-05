from __future__ import annotations

import hashlib
import json
import math
import urllib.request
from collections import Counter
from pathlib import Path

import h5py
import numpy as np


URL = (
    "https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/"
    "resolve/main/demos/PickCube-v1/motionplanning/trajectory.h5"
)
DATA = Path("/tmp/maniskill_pickcube_motionplanning_trajectory.h5")
OUT = Path("/tmp/cst_official_pickcube_reachability_v0.json")
STEP_BOUND = 0.1
TOL = 1e-9
ARM = slice(0, 7)
ARM_QPOS = slice(13, 20)


def h_min(displacement: np.ndarray) -> np.ndarray:
    per_joint = np.ceil((np.abs(displacement) - TOL) / STEP_BOUND)
    per_joint = np.maximum(per_joint, 1.0)
    return np.max(per_joint, axis=1).astype(np.int64)


def h_hist(values: np.ndarray) -> dict[str, int]:
    bins = {
        "1": int(np.sum(values == 1)),
        "2": int(np.sum(values == 2)),
        "3": int(np.sum(values == 3)),
        "4": int(np.sum(values == 4)),
        "5": int(np.sum(values == 5)),
        "6-10": int(np.sum((values >= 6) & (values <= 10))),
        ">10": int(np.sum(values > 10)),
    }
    assert sum(bins.values()) == len(values)
    return bins


def quantiles(values: np.ndarray) -> dict[str, float]:
    return {
        "median": float(np.quantile(values, 0.50)),
        "p90": float(np.quantile(values, 0.90)),
        "p95": float(np.quantile(values, 0.95)),
        "p99": float(np.quantile(values, 0.99)),
        "max": int(np.max(values)),
    }


def per_joint_stats(displacements: np.ndarray) -> dict[str, list[float] | list[int]]:
    absolute = np.abs(displacements)
    bottleneck = np.argmax(absolute / STEP_BOUND, axis=1)
    counts = np.bincount(bottleneck, minlength=7)
    return {
        "bottleneck_argmax_count": counts.astype(int).tolist(),
        "p95_abs_displacement": np.quantile(absolute, 0.95, axis=0).tolist(),
        "max_abs_displacement": np.max(absolute, axis=0).tolist(),
    }


def main() -> None:
    print(f"DOWNLOAD={URL}")
    urllib.request.urlretrieve(URL, DATA)
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    print(f"DATA_BYTES={DATA.stat().st_size}")
    print(f"DATA_SHA256={digest}")

    current_displacements = []
    target_displacements = []
    current_horizons = []
    target_horizons = []
    per_traj = []
    total_actions = 0

    with h5py.File(DATA, "r") as f:
        keys = sorted(
            f.keys(),
            key=lambda x: int(x.split("_", 1)[1]),
        )
        if len(keys) != 1000:
            raise RuntimeError(f"expected 1000 trajectories, got {len(keys)}")

        for key in keys:
            traj = f[key]
            actions = np.asarray(traj["actions"], dtype=np.float64)
            panda = np.asarray(
                traj["env_states/articulations/panda"],
                dtype=np.float64,
            )
            if actions.ndim != 2 or actions.shape[1] != 8:
                raise RuntimeError(f"{key}: expected actions [T,8], got {actions.shape}")
            if panda.ndim != 2 or panda.shape[1] != 31:
                raise RuntimeError(f"{key}: expected Panda state [T+1,31], got {panda.shape}")
            if panda.shape[0] != actions.shape[0] + 1:
                raise RuntimeError(
                    f"{key}: expected state length T+1, got actions={actions.shape[0]} "
                    f"states={panda.shape[0]}"
                )
            if not np.all(np.isfinite(actions)) or not np.all(np.isfinite(panda)):
                raise RuntimeError(f"{key}: non-finite values")

            goals = actions[:, ARM]
            measured = panda[:-1, ARM_QPOS]

            # E1 semantic displacement for delta-current target.
            d_current = goals - measured

            # E1 semantic displacement for delta-target target.  At reset the
            # target reference is measured qpos; after each exact source goal,
            # the target reference becomes that goal.
            previous_target = np.vstack([measured[0], goals[:-1]])
            d_target = goals - previous_target

            hc = h_min(d_current)
            ht = h_min(d_target)

            current_displacements.append(d_current)
            target_displacements.append(d_target)
            current_horizons.append(hc)
            target_horizons.append(ht)
            total_actions += len(actions)

            per_traj.append(
                {
                    "trajectory": key,
                    "actions": int(len(actions)),
                    "delta_current_all_one_step_exact": bool(np.all(hc == 1)),
                    "delta_target_all_one_step_exact": bool(np.all(ht == 1)),
                    "delta_current_max_h_min": int(np.max(hc)),
                    "delta_target_max_h_min": int(np.max(ht)),
                }
            )

    dc = np.concatenate(current_displacements, axis=0)
    dt = np.concatenate(target_displacements, axis=0)
    hc = np.concatenate(current_horizons, axis=0)
    ht = np.concatenate(target_horizons, axis=0)

    if len(hc) != total_actions or len(ht) != total_actions:
        raise RuntimeError("action accounting mismatch")

    trajectory_current_max = np.asarray(
        [x["delta_current_max_h_min"] for x in per_traj], dtype=np.int64
    )
    trajectory_target_max = np.asarray(
        [x["delta_target_max_h_min"] for x in per_traj], dtype=np.int64
    )

    summary = {
        "protocol": "OFFICIAL_PICKCUBE_REACHABILITY_PROTOCOL_V0",
        "dataset": {
            "url": URL,
            "sha256": digest,
            "bytes": DATA.stat().st_size,
            "trajectories": len(per_traj),
            "total_actions": total_actions,
            "source_control_mode": "pd_joint_pos",
            "source_arm_normalized": False,
            "target_delta_bound_rad": STEP_BOUND,
            "numeric_tolerance": TOL,
        },
        "delta_current": {
            "one_step_exact_actions": int(np.sum(hc == 1)),
            "one_step_exact_fraction": float(np.mean(hc == 1)),
            "h_min_histogram": h_hist(hc),
            "h_min_quantiles": quantiles(hc),
            "per_joint": per_joint_stats(dc),
            "trajectories_all_one_step_exact": int(
                sum(x["delta_current_all_one_step_exact"] for x in per_traj)
            ),
            "trajectories_all_one_step_exact_fraction": float(
                np.mean([x["delta_current_all_one_step_exact"] for x in per_traj])
            ),
            "trajectory_max_h_min_quantiles": quantiles(trajectory_current_max),
            "requires_feedback_when_h_gt_1": True,
        },
        "delta_target": {
            "one_step_exact_actions": int(np.sum(ht == 1)),
            "one_step_exact_fraction": float(np.mean(ht == 1)),
            "h_min_histogram": h_hist(ht),
            "h_min_quantiles": quantiles(ht),
            "per_joint": per_joint_stats(dt),
            "trajectories_all_one_step_exact": int(
                sum(x["delta_target_all_one_step_exact"] for x in per_traj)
            ),
            "trajectories_all_one_step_exact_fraction": float(
                np.mean([x["delta_target_all_one_step_exact"] for x in per_traj])
            ),
            "trajectory_max_h_min_quantiles": quantiles(trajectory_target_max),
            "requires_feedback_when_h_gt_1": False,
        },
        "claim_boundary": {
            "equivalence_level": "E1 semantic command only",
            "e2_controller_reference": False,
            "e3_realized_trajectory": False,
            "e4_task_success": False,
        },
    }

    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("CST_OFFICIAL_PICKCUBE_REACHABILITY_V0")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
