#!/usr/bin/env python3
"""Frozen source-seed paired 2x2 replay assay auditor.

The first 8 source episodes are development-exposed; only the next 24 are
the locked replication slice. No model or reward-success assertion is inferred.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

CELLS = (
    "upstream_baseline",
    "converter_only_pr1495",
    "controller_only_pr1472",
    "combined_pr1495_pr1472",
)
COMPARISONS = (
    ("controller_only_pr1472", "upstream_baseline"),
    ("controller_only_pr1472", "combined_pr1495_pr1472"),
    ("converter_only_pr1495", "combined_pr1495_pr1472"),
)


def paired(rows: list[dict], a: str, b: str) -> dict:
    n01 = sum((not r[a]) and r[b] for r in rows)
    n10 = sum(r[a] and (not r[b]) for r in rows)
    disc = n01 + n10
    if disc:
        # Exact two-sided binomial sign test on *discordant* matched episodes.
        lo = min(n01, n10)
        pval = min(1.0, 2 * sum(math.comb(disc, k) for k in range(lo + 1)) / 2**disc)
    else:
        pval = 1.0
    return {
        "a": a, "b": b, "n": len(rows),
        "a_only": n10, "b_only": n01,
        "discordant_total": disc, "exact_two_sided_p_descriptive": pval,
        "success_rate_a": sum(bool(r[a]) for r in rows) / len(rows),
        "success_rate_b": sum(bool(r[b]) for r in rows) / len(rows),
    }


def audit(report: dict) -> dict:
    if report["source_dataset_sha256"] != "7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c":
        raise ValueError("wrong frozen source dataset hash")
    if report["converter_code_sha"] != "69facfaafaa0ef233d36ef19e6cd9a0f03532ee0":
        raise ValueError("wrong converter source")
    if report["controller_code_sha"] != "eed9be164797d41540421bda8adb3840377d7087":
        raise ValueError("wrong controller source")
    if report["baseline_code_sha"] != "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3":
        raise ValueError("wrong baseline source")
    rows = report["source_seed_matrix"]
    if len(rows) != 32 or report["sample_size"] != 32:
        raise ValueError("32-case frozen sample denominator violated")
    seeds = [r["source_seed"] for r in rows]
    if len(set(seeds)) != 32:
        raise ValueError("duplicate source episode seed")
    for r in rows:
        if set(r) != set(CELLS) | {"source_seed"} or any(type(r[k]) is not bool for k in CELLS):
            raise ValueError("missing/invalid factorial cell evidence")
    for cell in CELLS:
        if sum(r[cell] for r in rows) != report["per_arm_success_count"][cell]:
            raise ValueError(f"{cell}: declared and observed count disagree")
    dev, unseen = rows[:8], rows[8:]
    for subset in (dev, unseen, rows):
        assert subset

    def summarize(name, subset):
        by_cell = {cell: sum(r[cell] for r in subset) for cell in CELLS}
        interaction = (
            (by_cell["combined_pr1495_pr1472"] - by_cell["controller_only_pr1472"])
            - (by_cell["converter_only_pr1495"] - by_cell["upstream_baseline"])
        )
        return {
            "slice": name,
            "n": len(subset),
            "seed_set_sha256": hashlib.sha256(json.dumps(
                [r["source_seed"] for r in subset], separators=(",", ":")
            ).encode()).hexdigest(),
            "success_counts": by_cell,
            "paired_tests": [paired(subset, a, b) for a, b in COMPARISONS],
            "factorial_interaction_success_rate": interaction / len(subset),
            "full_four_way_successful_intersection": sum(all(r[c] for c in CELLS) for r in subset),
        }

    out = {
        "schema_version": 1,
        "protocol_path": "research/kaggle_diffusion_policy_peg/FACTORIAL_32_PROTOCOL.md",
        "frozen_run_mode": "32-source-demo / first 8 exposed / next 24 held out",
        "overall": summarize("all_32", rows),
        "development_exposed": summarize("first_8", dev),
        "replication_holdout": summarize("next_24", unseen),
        "primary_outcome": "source-seed paired official demonstration conversion success",
        "claim_boundary": "Not learned-policy task success, not statistical independence across episodes, not upstream maintained adoption.",
    }
    return out


def self_test():
    rows = [{
        "source_seed": i,
        **{c: i % 5 != 0 if c != "controller_only_pr1472" else False for c in CELLS},
    } for i in range(32)]
    fake = {
        "source_dataset_sha256": "7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c",
        "converter_code_sha": "69facfaafaa0ef233d36ef19e6cd9a0f03532ee0",
        "controller_code_sha": "eed9be164797d41540421bda8adb3840377d7087",
        "baseline_code_sha": "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3",
        "source_seed_matrix": rows, "sample_size": len(rows),
        "per_arm_success_count": {c: sum(r[c] for r in rows) for c in CELLS}
    }
    result = audit(fake)
    assert result["replication_holdout"]["n"] == 24
    assert result["development_exposed"]["n"] == 8
    for mutated in (
        {**fake, "sample_size": 31},
        {**fake, "source_seed_matrix": rows[:31]},
        {**fake, "per_arm_success_count": {**fake["per_arm_success_count"], "controller_only_pr1472": 5}},
        {**fake, "source_seed_matrix": [rows[0], *rows[:31]]},
    ):
        try:
            audit(mutated)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted corrupted factorial denominator or provenance")
    assert paired([{"a": False, "b": True}] * 6, "a", "b")["exact_two_sided_p_descriptive"] == 0.03125
    print("frozen 32-case audit self-test passed")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", nargs="?", type=Path)
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
        return
    if a.input is None:
        p.error("pass factorial_replay.json, or --self-test")
    source = json.loads(a.input.read_text(encoding="utf-8"))
    result = audit(source)
    target = a.input.with_name("factorial_32_audit.json")
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
