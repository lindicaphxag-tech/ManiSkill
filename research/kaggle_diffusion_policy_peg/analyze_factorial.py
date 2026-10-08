#!/usr/bin/env python3
"""Fail-closed paired factorial audit of official ManiSkill replay observations.

All computations are deterministic source-seed paired *descriptive* effects.
This is NOT a learned-policy experiment, a statistical population claim, or
evidence of maintainer adoption. Zero-success cells remain in the denominator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ARM00 = "upstream_baseline"
ARM10 = "converter_only_pr1495"
ARM01 = "controller_only_pr1472"
ARM11 = "combined_pr1495_pr1472"
ARMS = (ARM00, ARM10, ARM01, ARM11)
COMMITS = {
    "baseline_code_sha": "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3",
    "converter_code_sha": "69facfaafaa0ef233d36ef19e6cd9a0f03532ee0",
    "controller_code_sha": "eed9be164797d41540421bda8adb3840377d7087",
}
SOURCE_DATASET_SHA = "7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c"


def sha_seeds(seeds: list[int]) -> str:
    return hashlib.sha256(
        json.dumps(seeds, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def analyze(document: dict, expected_n: int) -> dict:
    if document.get("schema_version") != 1:
        raise ValueError("unsupported factorial schema")
    if document.get("status") != "factorial_replay_completed_not_policy_training":
        raise ValueError("not a completed replay-only factorial")
    if document.get("sample_size") != expected_n or expected_n <= 0:
        raise ValueError("sample size differs from predeclared source prefix")
    if document.get("source_dataset_sha256") != SOURCE_DATASET_SHA:
        raise ValueError("public official demo archive hash mismatch")
    for key, commit in COMMITS.items():
        if document.get(key) != commit:
            raise ValueError(f"{key}: source code identity drift")

    rows = document.get("source_seed_matrix")
    if not isinstance(rows, list) or len(rows) != expected_n:
        raise ValueError("missing or selected source-seed rows")
    seeds: list[int] = []
    for i, row in enumerate(rows):
        if set(row) != {"source_seed", *ARMS}:
            raise ValueError(f"row {i}: missing/extra experiment fields")
        seed = row["source_seed"]
        if type(seed) is not int:
            raise ValueError(f"row {i}: invalid stable source seed")
        seeds.append(seed)
        for arm in ARMS:
            if type(row[arm]) is not bool:
                raise ValueError(f"row {i}, {arm}: expected observed boolean")
    if len(set(seeds)) != expected_n:
        raise ValueError("repeated source episode seed")

    totals = {arm: sum(row[arm] for row in rows) for arm in ARMS}
    if document.get("per_arm_success_count") != totals:
        raise ValueError("reported cell success count differs from source-seed matrix")

    common = [row["source_seed"] for row in rows if all(row[arm] for arm in ARMS)]
    if document.get("four_way_intersection_count") != len(common):
        raise ValueError("reported four-way intersection count mismatch")
    if document.get("four_way_intersection_source_seed_sha256") != sha_seeds(common):
        raise ValueError("four-way intersection source-seed hash mismatch")

    pairs = document.get("pairwise")
    expected_pairs = {
        f"{left}|{right}": (
            [row["source_seed"] for row in rows if row[left] and row[right]]
        )
        for i, left in enumerate(ARMS)
        for right in ARMS[i+1:]
    }
    if set(pairs or {}) != set(expected_pairs):
        raise ValueError("pairwise evidence matrix missing or expanded")
    for name, selected in expected_pairs.items():
        record = pairs[name]
        if record.get("intersection_count") != len(selected):
            raise ValueError(f"{name}: intersection count mismatch")
        if record.get("source_seed_sha256") != sha_seeds(selected):
            raise ValueError(f"{name}: source-seed membership hash mismatch")

    # Paired, per-source binary potential-outcome contrasts. No assumption of
    # independent cells: the same source seeds are evaluated in all four arms.
    # Interaction: [converter effect with controller fixed] minus
    #              [converter effect without controller fix].
    deltas = [
        int(row[ARM11]) - int(row[ARM01]) - int(row[ARM10]) + int(row[ARM00])
        for row in rows
    ]
    discordance = {}
    for a, b in ((ARM00, ARM01), (ARM10, ARM11), (ARM00, ARM10), (ARM01, ARM11)):
        discordance[f"{a}|{b}"] = {
            "left_pass_right_fail": sum(row[a] and not row[b] for row in rows),
            "left_fail_right_pass": sum(not row[a] and row[b] for row in rows),
            "both_pass": sum(row[a] and row[b] for row in rows),
            "both_fail": sum(not row[a] and not row[b] for row in rows),
        }
    return {
        "schema_version": 1,
        "status": "audited",
        "source_seed_n": expected_n,
        "source_seed_membership_sha256": sha_seeds(seeds),
        "source_archive_sha256": SOURCE_DATASET_SHA,
        "code_commits": COMMITS,
        "success_count": totals,
        "success_fraction": {arm: [totals[arm], expected_n] for arm in ARMS},
        "paired_factor_interaction_sum": sum(deltas),
        "paired_factor_interaction_fraction": [sum(deltas), expected_n],
        "paired_factor_interaction_histogram": {
            str(v): deltas.count(v) for v in sorted(set(deltas))
        },
        "baseline_success_lost_under_controller_only": sum(
            row[ARM00] and not row[ARM01] for row in rows
        ),
        "controller_only_failure_restored_by_joint_patch": sum(
            not row[ARM01] and row[ARM11] for row in rows
        ),
        "per_pair_discordance": discordance,
        "four_way_trainable_count": len(common),
        "no_cross_cell_imputation": True,
        "interpretation": (
            "Observed native replay of independently re-encoded public demos. "
            "Each source-seed is one paired observation. Nonrandom first-prefix "
            "sample; interaction is descriptive, not an iid population estimate."
        ),
        "limits": (
            "NOT trained policy task success; NOT evidence that #1495 alone "
            "improves behavior; NOT upstream maintainer adoption; NOT a "
            "semantic-repair paper acceptance. Do not exclude zero-success cells."
        ),
    }


def synthetic_document(n: int = 8) -> dict:
    rows = []
    for seed in range(n):
        ok = seed < 6
        rows.append({
            "source_seed": seed,
            ARM00: ok,
            ARM10: ok,
            ARM01: False,
            ARM11: ok,
        })
    common = [row["source_seed"] for row in rows if all(row[a] for a in ARMS)]
    pairs = {}
    for i, a in enumerate(ARMS):
        for b in ARMS[i + 1:]:
            ss = [row["source_seed"] for row in rows if row[a] and row[b]]
            pairs[f"{a}|{b}"] = {
                "intersection_count": len(ss),
                "source_seed_sha256": sha_seeds(ss),
            }
    return {
        "schema_version": 1,
        "status": "factorial_replay_completed_not_policy_training",
        "sample_size": n,
        "source_dataset_sha256": SOURCE_DATASET_SHA,
        **COMMITS,
        "source_seed_matrix": rows,
        "per_arm_success_count": {a: sum(row[a] for row in rows) for a in ARMS},
        "four_way_intersection_count": len(common),
        "four_way_intersection_source_seed_sha256": sha_seeds(common),
        "pairwise": pairs,
    }


def self_test() -> None:
    baseline = synthetic_document()
    result = analyze(baseline, 8)
    assert result["success_count"] == {
        ARM00: 6, ARM10: 6, ARM01: 0, ARM11: 6
    }
    assert result["paired_factor_interaction_fraction"] == [6, 8]
    assert result["four_way_trainable_count"] == 0
    assert result["baseline_success_lost_under_controller_only"] == 6
    assert result["controller_only_failure_restored_by_joint_patch"] == 6

    for mutation in ("count", "seed", "pairwise_hash", "source_identity", "late_field"):
        attacked = json.loads(json.dumps(baseline))
        if mutation == "count":
            attacked["per_arm_success_count"][ARM01] = 1
        elif mutation == "seed":
            attacked["source_seed_matrix"][0]["source_seed"] = 1
        elif mutation == "pairwise_hash":
            attacked["pairwise"][f"{ARM00}|{ARM11}"]["source_seed_sha256"] = "0" * 64
        elif mutation == "source_identity":
            attacked["converter_code_sha"] = "tampered"
        elif mutation == "late_field":
            attacked["source_seed_matrix"][0]["posthoc_label"] = "drop"
        try:
            analyze(attacked, 8)
        except ValueError:
            pass
        else:
            raise AssertionError(f"evidence tampering accepted: {mutation}")
    print("factorial 2x2 auditor: 5/5 tamper attacks rejected, 8-row pilot test passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--expected-n", type=int, default=48)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.path is None:
        parser.error("factorial replay JSON is required unless --self-test")
    result = analyze(json.loads(args.path.read_text(encoding="utf-8")), args.expected_n)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
