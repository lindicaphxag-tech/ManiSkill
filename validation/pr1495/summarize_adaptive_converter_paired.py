#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import h5py


def stats(path: Path, expected: int) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "episodes": 0,
            "steps": 0,
            "success_fraction": 0.0,
            "episode_ids": [],
        }
    with h5py.File(path, "r") as f:
        keys = sorted(
            (k for k in f.keys() if k.startswith("traj_")),
            key=lambda k: int(k.split("_", 1)[1]),
        )
        steps = sum(len(f[k]["actions"]) for k in keys if "actions" in f[k])
    ids = [int(k.split("_", 1)[1]) for k in keys]
    return {
        "exists": True,
        "episodes": len(ids),
        "steps": int(steps),
        "success_fraction": len(ids) / expected if expected else 0.0,
        "episode_ids": ids,
    }


def exact_mcnemar_two_sided(main_only: int, adaptive_only: int) -> float:
    n = main_only + adaptive_only
    if n == 0:
        return 1.0
    k = min(main_only, adaptive_only)
    lower = sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * lower)


def pair(a: dict, b: dict, expected: int) -> dict:
    sa = set(a["episode_ids"])
    sb = set(b["episode_ids"])
    main_only = sorted(sa - sb)
    adaptive_only = sorted(sb - sa)
    both_success = len(sa & sb)
    return {
        "both_success": both_success,
        "both_fail": expected - both_success - len(main_only) - len(adaptive_only),
        "main_only_success_ids": main_only,
        "adaptive_only_success_ids": adaptive_only,
        "main_only_success": len(main_only),
        "adaptive_only_success": len(adaptive_only),
        "success_rate_delta": b["success_fraction"] - a["success_fraction"],
        "mcnemar_exact_two_sided_p": exact_mcnemar_two_sided(
            len(main_only), len(adaptive_only)
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected", type=int, default=100)
    a = p.parse_args()

    variants = {}
    for name in ["main", "adaptive_current", "adaptive_controller_fixed"]:
        path = (
            a.root
            / f"demos-{name}"
            / "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        )
        variants[name] = stats(path, a.expected)

    main_stats = variants["main"]
    current = variants["adaptive_current"]
    fixed = variants["adaptive_controller_fixed"]

    report = {
        "schema_version": 1,
        "claim_boundary": (
            "Paired replay of the same first official PegInsertionSide "
            "demonstrations. This estimates trajectory-conversion behavior; "
            "it is not learned-policy performance."
        ),
        "expected_episodes": a.expected,
        "frozen_shas": {
            "main": "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3",
            "adaptive_converter": "80bd0fb678fd9534830dac18418c777b7ed1a2a3",
            "controller_fix": "eed9be164797d41540421bda8adb3840377d7087",
        },
        "variants": variants,
        "paired": {
            "main_vs_adaptive_current": pair(main_stats, current, a.expected),
            "main_vs_adaptive_controller_fixed": pair(main_stats, fixed, a.expected),
            "adaptive_current_vs_controller_fixed": pair(current, fixed, a.expected),
        },
        "decision_policy": (
            "Report paired discordances and exact McNemar evidence. Do not tune "
            "the converter from this 100-demo audit."
        ),
    }

    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
