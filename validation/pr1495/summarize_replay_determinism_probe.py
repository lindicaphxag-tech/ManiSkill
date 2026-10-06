#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import h5py


REGIMES = ("default", "enhanced")


def read_success_ids(path: Path) -> list[int]:
    if not path.exists():
        return []
    with h5py.File(path, "r") as f:
        return sorted(
            int(k.split("_", 1)[1])
            for k in f.keys()
            if k.startswith("traj_")
        )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--repeats", type=int, required=True)
    p.add_argument("--expected", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    report = {
        "schema_version": 1,
        "frozen_main_sha": "107c9528b23b55bd276cf723c260a45ae7ce00ec",
        "expected_episodes": a.expected,
        "repeats": a.repeats,
        "claim_boundary": (
            "Technical repeatability probe for ManiSkill CPU action-conversion "
            "replay. This does not estimate policy quality. It tests whether a "
            "single replay success set can be treated as deterministic evidence."
        ),
        "regimes": {},
    }

    for regime in REGIMES:
        sets = []
        run_success_counts = []
        per_episode = Counter()
        for rep in range(a.repeats):
            path = (
                a.root
                / f"{regime}-r{rep}"
                / "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
            )
            ids = read_success_ids(path)
            sets.append(ids)
            run_success_counts.append(len(ids))
            per_episode.update(ids)

        unique_sets = sorted({tuple(x) for x in sets})
        exact_repeatability = len(unique_sets) == 1
        report["regimes"][regime] = {
            "success_ids_by_replicate": sets,
            "success_count_by_replicate": run_success_counts,
            "unique_success_sets": [list(x) for x in unique_sets],
            "unique_success_set_count": len(unique_sets),
            "exact_repeatability": exact_repeatability,
            "per_episode_success_frequency": {
                str(i): per_episode[i] / a.repeats for i in range(a.expected)
            },
            "mean_success_fraction": (
                sum(run_success_counts) / (a.repeats * a.expected)
            ),
            "min_success_count": min(run_success_counts),
            "max_success_count": max(run_success_counts),
        }

    default = report["regimes"]["default"]
    enhanced = report["regimes"]["enhanced"]

    report["decision"] = (
        "use_single_run_gate"
        if enhanced["exact_repeatability"]
        else "require_replicate_frequency_gate"
    )
    report["enhanced_reduces_unique_success_sets"] = (
        enhanced["unique_success_set_count"]
        < default["unique_success_set_count"]
    )
    report["decision_policy"] = (
        "A single-run execution gate is permitted only if the enhanced regime "
        "is exactly repeatable across all technical replicates. Otherwise future "
        "execution comparisons must retain replicate-level success frequencies."
    )

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
