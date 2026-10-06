#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import h5py


FAIL_RE = re.compile(r"Episode (\d+) is not replayed successfully")


def summarize_budget(path: Path, expected: int) -> dict:
    output = path / "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
    log = (path / "replay.log").read_text(encoding="utf-8", errors="replace")
    failed = sorted({int(x) for x in FAIL_RE.findall(log)})

    episodes = 0
    steps = 0
    if output.exists():
        with h5py.File(output, "r") as f:
            keys = [key for key in f if key.startswith("traj_")]
            episodes = len(keys)
            steps = sum(len(f[key]["actions"]) for key in keys if "actions" in f[key])

    # The replay log is the source of original episode identity; HDF5 only
    # contains successful trajectories.
    expected_from_failures = expected - len(failed)
    if episodes != expected_from_failures:
        raise RuntimeError(
            f"{path.name}: HDF5 success count {episodes} disagrees with "
            f"log-derived count {expected_from_failures}"
        )

    return {
        "saved_episodes": episodes,
        "success_fraction": episodes / expected,
        "failed_episode_ids": failed,
        "steps": int(steps),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    budgets = [4, 6, 8, 12]
    rows = {
        str(budget): summarize_budget(args.root / f"budget-{budget}", args.expected)
        for budget in budgets
    }
    base_failed = set(rows["4"]["failed_episode_ids"])
    recovery = {}
    for budget in budgets[1:]:
        failed = set(rows[str(budget)]["failed_episode_ids"])
        recovery[str(budget)] = {
            "recovered_from_budget4": sorted(base_failed - failed),
            "new_failures_vs_budget4": sorted(failed - base_failed),
        }

    report = {
        "schema_version": 1,
        "experiment": "bounded_delta_temporal_horizon",
        "compiler": "deterministic_geodesic_ray_v2",
        "expected_episodes": args.expected,
        "retry_budgets": budgets,
        "results": rows,
        "causal_contrast_vs_budget4": recovery,
        "episode1_recovered": any(
            1 in recovery[str(budget)]["recovered_from_budget4"]
            for budget in budgets[1:]
        ),
        "claim_boundary": (
            "Same source, same official demonstrations, same bounded SO(3) "
            "compiler; only the per-target retry horizon changes. This is a "
            "temporal-decomposition diagnostic, not policy training."
        ),
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
