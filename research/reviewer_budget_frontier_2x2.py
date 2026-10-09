"""Fail-closed budget/paired-outcome reviewer audit for ORIGINAL 2x2 PhysX.

Reads SHA-pinned author-operated *source-auditor output*; this is NOT a
new physical run, independent laboratory reproduction or ActionShift result.
No extra packages. Rejects incomplete denominators, nonboolean success,
invented zero-read claims, missing probe accounting and incorrect pairings.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path


METHOD = "public"
TASKS = ("pull_cube", "stack_cube")
TRUTHS = ("held/held", "applied/held", "held/applied", "applied/applied")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mcnemar_exact(a, b):
    """Two-sided exact discordant-pair sign test; no independent-arm test."""
    require(type(a) is int and type(b) is int and min(a, b) >= 0,
            "Bad paired discordant counts")
    n = a + b
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(a, b) + 1))
    return min(1.0, 2.0 * tail / (2**n))


def wilson(x, n, z=1.959963984540054):
    require(type(x) is int and type(n) is int and 0 <= x <= n and n > 0,
            "Bad binomial count")
    p = x / n
    den = 1 + z*z/n
    mid = (p + z*z/(2*n))/den
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return [0.0 if x == 0 else max(0.0, mid-half),
            1.0 if x == n else min(1.0, mid+half)]


def compute(audit, *, expected_n=64, expected_per_stratum=8):
    require(audit.get("schema") ==
            "both_true_unknown_ACKs_full_64_original_native_PhysX_audit_v1",
            "Wrong frozen source-audit schema")
    rows = audit.get("all_episodes")
    require(isinstance(rows, list) and len(rows) == expected_n,
            "Missing or extra original trial rows")
    counts = Counter()
    totals = Counter()
    seen = set()
    sample_audit = []
    for row in rows:
        task, truth, seed = row.get("task"), row.get("truth"), row.get("seed")
        require(task in TASKS and truth in TRUTHS and type(seed) is int,
                "Bad source task, actual fault truth or seed")
        require((task, seed) not in seen, "Duplicate original source reset")
        seen.add((task, seed))
        counts[f"{task}/{truth}"] += 1
        require(row.get("public_both_faults_exposed") is True,
                "Claimed task trial missing either real fault")
        require(row.get("public_sample_events") == 2,
                "Public motion observations omitted or not counted")
        require(type(row.get("public_authorized")) is bool and
                type(row.get("wrong_confident")) is bool,
                "Missing confident-decision provenance")
        for k in ("new_success", "strong_success", "fixed_success",
                  "held_success"):
            require(type(row.get(k)) is bool, "Task success is not boolean: " + k)
        for k in ("new_reads", "strong_reads", "fixed_reads"):
            require(type(row.get(k)) is int and row[k] in (0, 1),
                    "Decision-private read not 0/1: " + k)
        require(row["new_reads"] == int(not row["public_authorized"]),
                "Public history not equivalent to exactly one counted fallback")
        require(not row["wrong_confident"] or row["public_authorized"],
                "False-confident label on non-authorized history")
        for kind, ok in (("public", row["new_success"]),
                         ("strong_task", row["strong_success"]),
                         ("fixed_t5", row["fixed_success"]),
                         ("always_held", row["held_success"])):
            totals[kind + "_success"] += int(ok)
        totals["public_reads"] += row["new_reads"]
        totals["strong_task_reads"] += row["strong_reads"]
        totals["fixed_t5_reads"] += row["fixed_reads"]
        totals["public_samples"] += row["public_sample_events"]
        totals["confident"] += int(row["public_authorized"])
        totals["wrong_confident"] += int(row["wrong_confident"])
        if row["new_success"] and row["strong_success"]:
            totals["both"] += 1
        elif row["new_success"]:
            totals["new_only"] += 1
        elif row["strong_success"]:
            totals["strong_only"] += 1
        else:
            totals["neither"] += 1
        if not row["new_success"] or not row["strong_success"]:
            sample_audit.append({
                "task": task, "reset": seed, "actual_truth": truth,
                "public_success": row["new_success"],
                "strong_success": row["strong_success"],
                "history_selected": row["public_authorized"],
                "private_reads": row["new_reads"],
            })
    for task in TASKS:
        for truth in TRUTHS:
            require(counts[f"{task}/{truth}"] == expected_per_stratum,
                    "Unbalanced or selectively omitted actual ACK truth stratum")
    require(len(seen) == expected_n, "Original reset denominator drift")
    published = audit.get("outcomes", {})
    for key, stats in (
        ("public", ("public_success", "public_reads")),
        ("strong_task", ("strong_task_success", "strong_task_reads")),
        ("fixed_t5", ("fixed_t5_success", "fixed_t5_reads")),
        ("always_held", ("always_held_success", None)),
    ):
        original = published.get(key, {})
        assert_count = totals[stats[0]]
        require(original.get("task_success") == assert_count,
                "Original audit task-success aggregate changed: " + key)
        if stats[1] is not None:
            require(original.get("private_reads") == totals[stats[1]],
                    "Original audit private read count changed: " + key)
        else:
            require(original.get("private_reads") == 0,
                    "Always-held comparator wrongly credited with private reads")
    published_pairs = audit.get("paired_new_vs_task_aware_strong", {})
    for key in ("both", "neither", "new_only", "strong_only"):
        require(published_pairs.get(key) == totals[key],
                "Claimed paired result differs from original rows: " + key)
    require(audit.get("public_confident_history_admissions") == totals["confident"] and
            audit.get("observed_confident_wrong_history") == totals["wrong_confident"],
            "Public-history label source audit differs")
    require(totals["wrong_confident"] == 0 or
            totals["confident"] >= totals["wrong_confident"],
            "Wrong labels exceed confident assignments")
    saved_private = totals["strong_task_reads"] - totals["public_reads"]
    extra_public = totals["public_samples"]
    breakeven = saved_private / extra_public if extra_public else None
    report = {
        "evidence_type": "SECONDARY_OFFLINE_REAUDIT_OF_AUTHOR_RUN_REAL_PHYSX",
        "not_new_simulation": True,
        "not_external_replication": True,
        "sample_unit": "distinct task/reset for within-cohort comparisons",
        "actual_truth_strata": dict(sorted(counts.items())),
        "totals": dict(sorted(totals.items())),
        "exact_mcnemar_two_sided_unadjusted": mcnemar_exact(
            totals["new_only"], totals["strong_only"]),
        "observed_wrong_confident_rate": (
            totals["wrong_confident"] / totals["confident"]
            if totals["confident"] else None),
        "wilson_95_confident_mistake_interval": wilson(
            totals["wrong_confident"], totals["confident"])
            if totals["confident"] else None,
        "marginal_public_XYZ_samples_vs_task_aware": extra_public,
        "privileged_reads_saved_vs_task_aware": saved_private,
        "private_read_equivalent_break_even_per_XYZ_sample": breakeven,
        "cost_model": ("C_public = R_public*c_priv + N_publicXYZ*c_XYZ; "
                       "C_task = R_task*c_priv. Probe-actuation cost must "
                       "be charged separately if not shared."),
        "one_more_observed_failure_than_task_comparator":
            totals["public_success"] < totals["strong_task_success"],
        "no_statistical_noninferiority_claim": True,
        "nonidentical_reset_truth_conditions_not_paired": True,
        "paired_failures": sample_audit,
    }
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--output")
    args = p.parse_args()
    raw = json.loads(Path(args.source).read_text(encoding="utf-8"))
    out = compute(raw)
    data = json.dumps(out, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        Path(args.output).write_text(data, encoding="utf-8")
    print("TWO_ACK_2X2_REVIEWER_COST_FRONTIER", data)


if __name__ == "__main__":
    main()
