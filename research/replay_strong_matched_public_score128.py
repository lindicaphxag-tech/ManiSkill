"""Retrospective SAME-PUBLIC scorer reanalysis on the immutable 128-cell PhysX archive.

This does NOT rerun physics, evaluate downstream commands, or demonstrate task
success with the new threshold. It only replays authorized-history labels and
hypothetical decision-time target getter requests on already recorded observations.
The 0.60 cutoff was previously tuned on a different experiment, but is not a
preregistered comparator of the 128-cell source-frozen cohort.

Importantly, validate the entire archive with the independent physical-prefix
auditor BEFORE selecting any scored subset.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

from research.audit_query_isolated_same_reset_factorial128 import analyze
from research.run_query_isolated_factorial128 import A, B, C
from research.review_original_factorial128_cluster_risk import EVIDENCE, exact_one_sided_upper


def score_from_residuals(residuals, epsilon):
    """Compute exactly the normalized residual weights from the existing source."""
    if len(residuals) != 4 or epsilon <= 0 or not math.isfinite(epsilon):
        raise ValueError("Invalid source residual array or response scale")
    if any(not math.isfinite(x) or x < 0 for x in residuals):
        raise ValueError("Invalid physical residual")
    raw = [math.exp(-0.5 * (float(x) / epsilon) ** 2) for x in residuals]
    z = sum(raw)
    if z <= 0:
        raise ValueError("Underflowed scorer")
    return [x / z for x in raw]


def decide_score(row, threshold):
    e = row["same_sensor_posterior_evidence"]
    residuals = e["candidate_residuals_m"]
    epsilon = e["prior_training_epsilon_m"]
    weights = score_from_residuals(residuals, epsilon)
    saved = e["posterior_weights"]
    if len(saved) != 4 or max(abs(a - b) for a, b in zip(weights, saved)) > 1e-9:
        raise ValueError("Recorded source weights disagree with source residuals")
    best = max(range(4), key=lambda i: weights[i])
    accept = bool(weights[best] >= threshold and residuals[best] <= epsilon)
    truth = e["audit_only_true_candidate_indices"]
    if not isinstance(truth, list) or not truth:
        raise ValueError("Missing complete physical target history ground truth")
    return accept, bool(accept and best not in truth), best, weights[best]


def replay(source_dir: Path):
    # Fails closed on incomplete provenance, same-reset hashes, actual native
    # pre-decision action/pose mismatch, and unexpected sample populations.
    original = analyze(source_dir)
    files = sorted(source_dir.rglob("query_isolated_*_truth*_original8.json"))
    if len(files) != 16:
        raise ValueError("Expected all 16 original 8-reset physical shards")
    rows = []
    for path in files:
        d = json.loads(path.read_bytes())
        if len(d["episodes"]) != 8:
            raise ValueError("Unexpected source shard trial count")
        match = re.search(r"_truth([0-3])_original8[.]json$", path.name)
        if match is None:
            raise ValueError("Source shard truth filename is invalid")
        truth = int(match.group(1))
        for row in d["episodes"]:
            before = row["same_sensor_posterior_evidence"]
            at95, wrong95, idx95, _ = decide_score(row, 0.95)
            if at95 != before["authorized"]:
                raise ValueError("Cannot reproduce the original precommitted 0.95 decision")
            if wrong95 != before["wrong_confident"]:
                raise ValueError("Cannot reproduce the original 0.95 false-label audit")
            if at95 and idx95 != before["selected_candidate_index"]:
                raise ValueError("Recorded selected history differs from replay")
            rows.append((d["task"], truth, row))
    if len(rows) != 128 or len({(task, r["seed"], truth) for task, truth, r in rows}) != 128:
        raise ValueError("Incomplete or duplicate 128-cell cohort")
    results = {}
    for t in (0.60, 0.95):
        count = wrong = 0
        accepted_by_cluster = defaultdict(list)
        accepted_by_task = defaultdict(int)
        wrong_by_task = defaultdict(int)
        for task, truth, row in rows:
            accept, is_wrong, _, _ = decide_score(row, t)
            count += int(accept)
            wrong += int(is_wrong)
            accepted_by_task[task] += int(accept)
            wrong_by_task[task] += int(is_wrong)
            accepted_by_cluster[(task, row["seed"])].append((accept, is_wrong))
        selected = [v for v in accepted_by_cluster.values() if any(x[0] for x in v)]
        wrong_clusters = sum(any(x[1] for x in v) for v in selected)
        results[f"{t:.2f}"] = {
            "type": "POST_HOC_FIXED_OBSERVATIONS_NOT_NEW_PHYSX",
            "threshold": t,
            "all_physical_cells": 128,
            "hypothetical_authorizations": count,
            "hypothetical_incorrect_authorizations": wrong,
            "hypothetical_target_reads_if_each_nonadmission_queries": 128 - count,
            "authorizing_distinct_reset_clusters": len(selected),
            "wrong_authorizing_reset_clusters": wrong_clusters,
            "cluster_iid_one_sided_95pct_upper_any_wrong_if_applicable":
                exact_one_sided_upper(wrong_clusters, len(selected)),
            "by_task_authorizations": dict(accepted_by_task),
            "by_task_wrong_authorizations": dict(wrong_by_task),
        }
    paired = {
        "both_A_and_posthoc_060_authorize": 0,
        "A_only_authorizes": 0,
        "posthoc_060_only_authorizes": 0,
        "neither_authorizes": 0,
    }
    by_task_pairing = defaultdict(lambda: {k: 0 for k in paired})
    for task, truth, row in rows:
        a = bool(row["public_t3_evidence"]["authorized"])
        b60, _, _, _ = decide_score(row, 0.60)
        key = ("both_A_and_posthoc_060_authorize" if a and b60
               else "A_only_authorizes" if a
               else "posthoc_060_only_authorizes" if b60
               else "neither_authorizes")
        paired[key] += 1
        by_task_pairing[task][key] += 1
    if sum(paired.values()) != 128 or (
        paired["both_A_and_posthoc_060_authorize"] + paired["A_only_authorizes"] !=
        original["all_cells"][A]["total_authorizations"]
    ):
        raise ValueError("Paired authorized-state counts disagree with original source")
    b = original["all_cells"][B]
    if (results["0.95"]["hypothetical_authorizations"] != b["total_authorizations"]
        or results["0.95"]["hypothetical_incorrect_authorizations"] != b["wrong_confident_authorizations"]
        or results["0.95"]["hypothetical_target_reads_if_each_nonadmission_queries"] != b["private_reads"]):
        raise ValueError("0.95 replay fails to reproduce actually executed comparator")
    return {
        "original_causal_prefix_audited": True,
        "source_distinct_reset_clusters": 32,
        "source_correlated_physical_cells": 128,
        "actual_orig_task_success_for_A_B_C": {
            x: original["all_cells"][x]["success"] for x in (A, B, C)
        },
        "actual_original_A_read_and_authorization": {
            "private_reads": original["all_cells"][A]["private_reads"],
            "authorizations": original["all_cells"][A]["total_authorizations"],
            "wrong": original["all_cells"][A]["wrong_confident_authorizations"]
        },
        "replayed_strong_and_original_scorer": results,
        "paired_A_vs_posthoc_060_decision_table": paired,
        "paired_A_vs_posthoc_060_by_task": dict(by_task_pairing),
        "not_evaluated": [
            "0.60 downstream task success",
            "0.60 physically executed native commands",
            "0.60 policy-level value or total sensing/actuation cost",
            "new pre-registered independent holdout",
            "independent third-party reexecution"
        ]
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=EVIDENCE)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = replay(args.source)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("MATCHED_PUBLIC_STRONG_SCORER_RETROSPECTIVE", json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
