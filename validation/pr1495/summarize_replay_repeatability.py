#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from itertools import combinations
from pathlib import Path


FAIL_RE = re.compile(r"Episode\s+(\d+)\s+is not replayed successfully")
SUMMARY_RE = re.compile(
    r"Replayed\s+(\d+)\s+episodes,\s+(\d+)/(\d+)=([0-9.]+)% demos saved"
)


def parse_log(path: Path, expected: int) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    failed = sorted({int(x) for x in FAIL_RE.findall(text)})
    all_ids = list(range(expected))
    success = [i for i in all_ids if i not in set(failed)]
    summaries = SUMMARY_RE.findall(text)
    if not summaries:
        raise RuntimeError(f"missing replay summary in {path}")
    replayed, saved, denom, pct = summaries[-1]
    if int(replayed) != expected or int(denom) != expected:
        raise RuntimeError(
            f"unexpected replay denominator in {path}: {summaries[-1]}"
        )
    if int(saved) != len(success):
        raise RuntimeError(
            f"log-derived success set {success} disagrees with summary saved={saved}"
        )
    return {
        "log": path.name,
        "failed_episode_ids": failed,
        "success_episode_ids": success,
        "success_count": len(success),
        "success_fraction": len(success) / expected,
        "summary_percent": float(pct),
    }


def jaccard(a, b):
    a, b = set(a), set(b)
    union = a | b
    return 1.0 if not union else len(a & b) / len(union)


def variant_summary(root: Path, name: str, repeats: int, expected: int) -> dict:
    runs = [
        parse_log(root / name / f"repeat_{i}.log", expected)
        for i in range(repeats)
    ]
    counts = [run["success_count"] for run in runs]
    pairwise = [
        jaccard(runs[i]["success_episode_ids"], runs[j]["success_episode_ids"])
        for i, j in combinations(range(repeats), 2)
    ]
    episode_frequency = {
        str(ep): sum(ep in run["success_episode_ids"] for run in runs) / repeats
        for ep in range(expected)
    }
    distinct_sets = sorted(
        {
            tuple(run["success_episode_ids"])
            for run in runs
        }
    )
    mean = sum(counts) / len(counts)
    variance = sum((x - mean) ** 2 for x in counts) / len(counts)
    return {
        "runs": runs,
        "repeat_count": repeats,
        "success_counts": counts,
        "mean_success_count": mean,
        "population_variance_success_count": variance,
        "min_success_count": min(counts),
        "max_success_count": max(counts),
        "distinct_success_sets": [list(x) for x in distinct_sets],
        "distinct_success_set_count": len(distinct_sets),
        "episode_success_frequency": episode_frequency,
        "pairwise_success_set_jaccard": pairwise,
        "min_pairwise_jaccard": min(pairwise) if pairwise else 1.0,
        "mean_pairwise_jaccard": (
            sum(pairwise) / len(pairwise) if pairwise else 1.0
        ),
        "exactly_repeatable": len(distinct_sets) == 1,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--expected", type=int, default=10)
    a = p.parse_args()

    report = {
        "schema_version": 1,
        "protocol": {
            "repeats": a.repeats,
            "expected_episodes_per_repeat": a.expected,
            "fresh_python_process_per_repeat": True,
            "sim_backend": "physx_cpu",
            "target_control_mode": "pd_ee_delta_pose",
            "use_first_env_state": True,
            "num_envs": 1,
        },
        "variants": {
            "current_main": variant_summary(
                a.root, "current_main", a.repeats, a.expected
            ),
            "contract_adapter_v2": variant_summary(
                a.root, "contract_adapter_v2", a.repeats, a.expected
            ),
        },
        "claim_boundary": (
            "Measures repeatability of the replay measurement itself under repeated "
            "fresh-process executions. It does not identify the source of any "
            "nondeterminism and is not a policy-training result."
        ),
    }
    report["repeatability_gate"] = {
        "current_main_exact": report["variants"]["current_main"][
            "exactly_repeatable"
        ],
        "candidate_exact": report["variants"]["contract_adapter_v2"][
            "exactly_repeatable"
        ],
        "pass": (
            report["variants"]["current_main"]["exactly_repeatable"]
            and report["variants"]["contract_adapter_v2"]["exactly_repeatable"]
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
