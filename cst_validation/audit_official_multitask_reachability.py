from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import h5py
import numpy as np


BASE = "https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/resolve/main/demos"
TASKS = ("PickCube-v1", "StackCube-v1", "PegInsertionSide-v1", "PlugCharger-v1")
BOUND = 0.1
TOL = 1e-9
ARM = slice(0, 7)
ARM_QPOS = slice(13, 20)
OUT = Path("/tmp/cst_official_multitask_reachability_v0.json")


def download(url: str, path: Path) -> None:
    urllib.request.urlretrieve(url, path)


def horizon(d: np.ndarray) -> np.ndarray:
    per = np.maximum(np.ceil((np.abs(d) - TOL) / BOUND), 1.0)
    return np.max(per, axis=1).astype(np.int64)


def hist(h: np.ndarray) -> dict[str, int]:
    result = {
        "1": int(np.sum(h == 1)),
        "2": int(np.sum(h == 2)),
        "3": int(np.sum(h == 3)),
        "4": int(np.sum(h == 4)),
        "5": int(np.sum(h == 5)),
        "6-10": int(np.sum((h >= 6) & (h <= 10))),
        ">10": int(np.sum(h > 10)),
    }
    assert sum(result.values()) == len(h)
    return result


def q(h: np.ndarray) -> dict[str, float | int]:
    return {
        "median": float(np.quantile(h, 0.50)),
        "p90": float(np.quantile(h, 0.90)),
        "p95": float(np.quantile(h, 0.95)),
        "p99": float(np.quantile(h, 0.99)),
        "max": int(np.max(h)),
    }


def joint_stats(d: np.ndarray) -> dict:
    a = np.abs(d)
    bottleneck = np.argmax(a / BOUND, axis=1)
    return {
        "bottleneck_argmax_count": np.bincount(bottleneck, minlength=7).astype(int).tolist(),
        "p95_abs_displacement": np.quantile(a, 0.95, axis=0).tolist(),
        "max_abs_displacement": np.max(a, axis=0).tolist(),
    }


def audit_task(task: str) -> dict:
    prefix = f"{BASE}/{task}/motionplanning"
    json_path = Path(f"/tmp/{task}.json")
    h5_path = Path(f"/tmp/{task}.h5")
    download(f"{prefix}/trajectory.json", json_path)
    meta = json.loads(json_path.read_text())
    mode = meta["env_info"]["env_kwargs"]["control_mode"]
    if mode != "pd_joint_pos":
        raise RuntimeError(f"{task}: expected pd_joint_pos, got {mode}")
    download(f"{prefix}/trajectory.h5", h5_path)
    sha = hashlib.sha256(h5_path.read_bytes()).hexdigest()

    dc_all, dt_all, hc_all, ht_all, traj_rows = [], [], [], [], []
    articulation_keys = set()
    with h5py.File(h5_path, "r") as f:
        keys = sorted(f.keys(), key=lambda x: int(x.split("_", 1)[1]))
        for key in keys:
            g = f[key]
            actions = np.asarray(g["actions"], dtype=np.float64)
            articulations = g["env_states/articulations"]
            candidates = [
                name
                for name in articulations.keys()
                if isinstance(articulations[name], h5py.Dataset)
                and articulations[name].ndim == 2
                and articulations[name].shape[1] == 31
            ]
            if len(candidates) != 1:
                raise RuntimeError(
                    f"{task}/{key}: expected exactly one 31D Panda articulation, "
                    f"found {candidates} among {list(articulations.keys())}"
                )
            articulation_key = candidates[0]
            articulation_keys.add(articulation_key)
            panda = np.asarray(articulations[articulation_key], dtype=np.float64)
            if actions.ndim != 2 or actions.shape[1] != 8:
                raise RuntimeError(f"{task}/{key}: actions shape {actions.shape}")
            if panda.ndim != 2 or panda.shape[1] != 31:
                raise RuntimeError(f"{task}/{key}: Panda state shape {panda.shape}")
            if panda.shape[0] != actions.shape[0] + 1:
                raise RuntimeError(f"{task}/{key}: state/action length mismatch")
            if not np.all(np.isfinite(actions)) or not np.all(np.isfinite(panda)):
                raise RuntimeError(f"{task}/{key}: non-finite values")

            goals = actions[:, ARM]
            measured = panda[:-1, ARM_QPOS]
            dc = goals - measured
            previous_target = np.vstack([measured[0], goals[:-1]])
            dt = goals - previous_target
            hc, ht = horizon(dc), horizon(dt)

            dc_all.append(dc); dt_all.append(dt); hc_all.append(hc); ht_all.append(ht)
            traj_rows.append((bool(np.all(hc == 1)), bool(np.all(ht == 1)), int(np.max(hc)), int(np.max(ht))))

    dc = np.concatenate(dc_all); dt = np.concatenate(dt_all)
    hc = np.concatenate(hc_all); ht = np.concatenate(ht_all)
    def surface(h, d, index):
        all_exact = np.asarray([row[index] for row in traj_rows], dtype=bool)
        maxima = np.asarray([row[index + 2] for row in traj_rows], dtype=np.int64)
        return {
            "one_step_exact_actions": int(np.sum(h == 1)),
            "one_step_exact_fraction": float(np.mean(h == 1)),
            "actions_requiring_h_gt_1": int(np.sum(h > 1)),
            "h_min_histogram": hist(h),
            "h_min_quantiles": q(h),
            "trajectories_all_one_step_exact": int(np.sum(all_exact)),
            "trajectories_all_one_step_exact_fraction": float(np.mean(all_exact)),
            "trajectory_max_h_min_quantiles": q(maxima),
            "per_joint": joint_stats(d),
        }
    return {
        "task": task,
        "control_mode": mode,
        "h5_sha256": sha,
        "h5_bytes": h5_path.stat().st_size,
        "trajectories": len(traj_rows),
        "total_actions": int(len(hc)),
        "articulation_keys": sorted(articulation_keys),
        "delta_current": surface(hc, dc, 0),
        "delta_target": surface(ht, dt, 1),
    }


def main() -> None:
    results = [audit_task(task) for task in TASKS]
    total_actions = sum(x["total_actions"] for x in results)
    dc_exact = sum(x["delta_current"]["one_step_exact_actions"] for x in results)
    dt_exact = sum(x["delta_target"]["one_step_exact_actions"] for x in results)
    summary = {
        "protocol": "OFFICIAL_MULTITASK_REACHABILITY_PROTOCOL_V0",
        "tasks": results,
        "aggregate": {
            "tasks": len(results),
            "trajectories": sum(x["trajectories"] for x in results),
            "total_actions": total_actions,
            "delta_current_micro_one_step_exact_fraction": dc_exact / total_actions,
            "delta_target_micro_one_step_exact_fraction": dt_exact / total_actions,
            "delta_current_macro_one_step_exact_fraction": float(np.mean([x["delta_current"]["one_step_exact_fraction"] for x in results])),
            "delta_target_macro_one_step_exact_fraction": float(np.mean([x["delta_target"]["one_step_exact_fraction"] for x in results])),
            "delta_current_tasks_100pct_exact": int(sum(x["delta_current"]["one_step_exact_fraction"] == 1.0 for x in results)),
            "delta_target_tasks_100pct_exact": int(sum(x["delta_target"]["one_step_exact_fraction"] == 1.0 for x in results)),
            "delta_current_actions_requiring_h_gt_1": int(sum(x["delta_current"]["actions_requiring_h_gt_1"] for x in results)),
            "delta_target_actions_requiring_h_gt_1": int(sum(x["delta_target"]["actions_requiring_h_gt_1"] for x in results)),
            "delta_current_max_h_min": int(max(x["delta_current"]["h_min_quantiles"]["max"] for x in results)),
            "delta_target_max_h_min": int(max(x["delta_target"]["h_min_quantiles"]["max"] for x in results)),
        },
        "claim_boundary": "E1 semantic-command reachability only",
    }
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("CST_OFFICIAL_MULTITASK_REACHABILITY_V0")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
