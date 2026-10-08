#!/usr/bin/env python3
"""Independent, stdlib-only audit of official four-cell ManiSkill replay results.

Evidence unit: a frozen source episode seed. Zero-success cells remain explicit.
This audits replay/data conversion, NOT trained-policy task success.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

ARMS = (
    "upstream_baseline",
    "converter_only_pr1495",
    "controller_only_pr1472",
    "combined_pr1495_pr1472",
)
BASE_SHA = "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERTER_SHA = "69facfaafaa0ef233d36ef19e6cd9a0f03532ee0"
CONTROLLER_SHA = "eed9be164797d41540421bda8adb3840377d7087"
DATASET_SHA256 = "7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c"
DATASET_REVISION = "d674485bbffdd533914e52d272fdda34c0515608"


def digest(seeds: list[int]) -> str:
    return hashlib.sha256(json.dumps(seeds, separators=(",", ":")).encode()).hexdigest()


def exact_mcnemar(a_only: int, b_only: int) -> float:
    """Two-sided exact conditional discordance test; descriptive only."""
    n = a_only + b_only
    if n == 0:
        return 1.0
    k = min(a_only, b_only)
    numerator = sum(math.comb(n, i) for i in range(k + 1))
    return float(min(Fraction(1), 2 * Fraction(numerator, 2 ** n)))


def audit(data: dict) -> dict:
    if data.get("schema_version") != 1 or data.get("status") != "factorial_replay_completed_not_policy_training":
        raise ValueError("not a completed factorial replay record")
    expected_hashes = {
        "baseline_code_sha": BASE_SHA,
        "converter_code_sha": CONVERTER_SHA,
        "controller_code_sha": CONTROLLER_SHA,
        "source_dataset_sha256": DATASET_SHA256,
        "source_dataset_revision": DATASET_REVISION,
    }
    for key, expected in expected_hashes.items():
        if data.get(key) != expected:
            raise ValueError(f"frozen code/data identity mismatch at {key}")

    rows = data["source_seed_matrix"]
    if not isinstance(rows, list) or not rows or len(rows) != data["sample_size"]:
        raise ValueError("sample size disagrees with per-seed matrix")
    if data["sample_size"] not in (8, 100):
        raise ValueError("unregistered source cohort; run a separately preregistered assay")
    seeds = []
    for row in rows:
        if set(row) != {"source_seed", *ARMS} or type(row["source_seed"]) is not int:
            raise ValueError("matrix has missing, extra or noninteger seed fields")
        if any(type(row[arm]) is not bool for arm in ARMS):
            raise ValueError("matrix has non-boolean replay outcome")
        seeds.append(row["source_seed"])
    if len(set(seeds)) != len(seeds):
        raise ValueError("source seeds not independent identifiers; duplicates in matrix")

    actual_counts = {arm: sum(int(row[arm]) for row in rows) for arm in ARMS}
    if actual_counts != data["per_arm_success_count"]:
        raise ValueError("summary success counts do not match original source-seed matrix")

    expected_pairs = {}
    discordance = {}
    for a, b in itertools.combinations(ARMS, 2):
        joint = [row["source_seed"] for row in rows if row[a] and row[b]]
        name = f"{a}|{b}"
        expected_pairs[name] = {
            "intersection_count": len(joint),
            "source_seed_sha256": digest(joint),
        }
        discordance[name] = {
            "a_only": sum(row[a] and not row[b] for row in rows),
            "b_only": sum(row[b] and not row[a] for row in rows),
        }
        discordance[name]["exact_mcnemar_p_descriptive"] = exact_mcnemar(
            discordance[name]["a_only"], discordance[name]["b_only"]
        )
    if expected_pairs != data.get("pairwise"):
        raise ValueError("pairwise source-seed intersections or hashes mismatch")

    shared = [row["source_seed"] for row in rows if all(row[arm] for arm in ARMS)]
    if (len(shared) != data["four_way_intersection_count"] or
            digest(shared) != data["four_way_intersection_source_seed_sha256"]):
        raise ValueError("four-way source-seed intersection or hash mismatch")

    minimum = 4  # the registered CPU factorial smoke's minimum paired demos
    if bool(data["trainable_four_way_factorial"]) != (len(shared) >= minimum):
        raise ValueError("frozen trainability flag inconsistent with matched intersection")

    # Per-source effect of converter x controller, an observed replay contrast.
    diff = [
        int(row["combined_pr1495_pr1472"])
        - int(row["converter_only_pr1495"])
        - int(row["controller_only_pr1472"])
        + int(row["upstream_baseline"])
        for row in rows
    ]
    contrast = Fraction(sum(diff), len(diff))
    # Bootstrap only as a within-prefix descriptive sensitivity interval, not
    # as an IID population confidence interval or a learned-policy effect.
    rng = random.Random(20261008)
    resamples = 10000
    draws = sorted(
        sum(diff[rng.randrange(len(diff))] for _ in diff) / len(diff)
        for _ in range(resamples)
    )
    low = draws[int(resamples * 0.025)]
    high = draws[int(resamples * 0.975)]
    return {
        "audit": "passed",
        "source_cohort": "first N episodes from fixed official demo archive, NOT a random population sample",
        "sample_size": len(rows),
        "success_counts": actual_counts,
        "success_rates": {k: count / len(rows) for k, count in actual_counts.items()},
        "source_matched_factorial_interaction_exact": str(contrast),
        "factorial_interaction_resampling_sensitivity": [low, high],
        "pairwise_discordance": discordance,
        "four_way_intersection": len(shared),
        "all_four_cells_trainable": len(shared) >= minimum,
        "method_boundary": (
            "Fixed-prefix native demonstration replay/convertibility only. "
            "Exact McNemar p-values and resampling intervals are sensitivity "
            "descriptors, NOT inferential evidence for a random task population "
            "or learned-policy performance. Nontrainable cells stay visible."
        ),
    }


def self_test() -> None:
    seeds = [100 + i for i in range(8)]
    a = [True, True, True, True, True, True, False, False]
    b = a[:]
    c = [False] * 8
    d = a[:]
    rows = [
        {"source_seed": seed, **dict(zip(ARMS, (a[i], b[i], c[i], d[i])))}
        for i, seed in enumerate(seeds)
    ]
    document = {
        "schema_version": 1,
        "status": "factorial_replay_completed_not_policy_training",
        "sample_size": 8,
        "source_seed_matrix": rows,
        "per_arm_success_count": {arm: sum(row[arm] for row in rows) for arm in ARMS},
        "four_way_intersection_count": 0,
        "four_way_intersection_source_seed_sha256": digest([]),
        "trainable_four_way_factorial": False,
        **{
            "baseline_code_sha": BASE_SHA,
            "converter_code_sha": CONVERTER_SHA,
            "controller_code_sha": CONTROLLER_SHA,
            "source_dataset_sha256": DATASET_SHA256,
            "source_dataset_revision": DATASET_REVISION,
        },
        "pairwise": {
            f"{x}|{y}": {
                "intersection_count": len(both := [row["source_seed"] for row in rows if row[x] and row[y]]),
                "source_seed_sha256": digest(both),
            }
            for x, y in itertools.combinations(ARMS, 2)
        },
    }
    out = audit(document)
    assert out["source_matched_factorial_interaction_exact"] == "3/4"
    assert out["four_way_intersection"] == 0
    assert not out["all_four_cells_trainable"]
    for mutate, error in [
        (lambda v: v["source_seed_matrix"][0].update({"controller_only_pr1472": True}), "summary"),
        (lambda v: v.update({"baseline_code_sha": "f" * 40}), "identity"),
        (lambda v: v.update({"four_way_intersection_count": 6}), "four-way"),
    ]:
        tainted = json.loads(json.dumps(document))
        mutate(tainted)
        try:
            audit(tainted)
        except ValueError as exc:
            if error not in str(exc):
                raise AssertionError(f"wrong rejection category: {exc}") from exc
        else:
            raise AssertionError("tampered native replay evidence was accepted")
    print("factorial audit self-test passed: synthetic 8-case witness + 3 tamper rejections")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("result", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    opts = parser.parse_args()
    if opts.self_test:
        self_test()
    elif opts.result:
        print(json.dumps(audit(json.loads(opts.result.read_text())), indent=2, sort_keys=True))
    else:
        parser.error("provide a factorial_replay.json path or --self-test")
