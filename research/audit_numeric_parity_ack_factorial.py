"""Independent source-file auditor for the prospective SAME RESET x FOUR execution truths.

NO PhyX import. Fails closed on any missing negative trial, altered source
shard, unmatched first physical observation, or wrong factorial truth.
This is an audit TOOL, not evidence that any trial has run.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

from research.run_numeric_parity_ack_factorial import (
    PUBLIC, STRONG, FIXED, HELD, select, truth, validate, assert_preoutcome, blob,
    PREREG, SOURCE, CLASSIFIER,
)

TASKS = ("pull_cube", "stack_cube")
CONDITIONS = tuple(range(4))
ARMS = ("public", "strong_task", "fixed_t5", "always_held")


def exact_cluster_swap_p(cluster_differences):
    """Exact two-sided seed-cluster method-label swap sensitivity calculation.

    Four outcomes for one seed are KEPT TOGETHER. Exact enumeration uses
    dynamic programming over success-count differences; 2**32 assignments
    are computed without drawing independent row-level permutations.
    Interpret only under a seed-cluster exchangeability assumption.
    """
    distribution = Counter({0: 1})
    for d in cluster_differences:
        if type(d) is not int or abs(d) > 4:
            raise ValueError("Invalid per-seed four-condition difference")
        nxt = Counter()
        for s, count in distribution.items():
            nxt[s + d] += count
            nxt[s - d] += count
        distribution = nxt
    observed = abs(sum(cluster_differences))
    extreme = sum(count for s, count in distribution.items() if abs(s) >= observed)
    denominator = 2 ** len(cluster_differences)
    if sum(distribution.values()) != denominator:
        raise ValueError("Exact cluster swap denominator changed")
    return extreme / denominator


def cluster_bootstrap_delta(cluster_scores, *, draws=10000, seed=20261009):
    """95% percentile interval for per-cell public vs strong success gap.

    Resample source reset IDs, each carrying all four truth conditions;
    do NOT bootstrap the 128 cells as iid observations.
    """
    if not cluster_scores:
        raise ValueError("No complete seed clusters")
    rng = random.Random(seed)
    vals = []
    n = len(cluster_scores)
    for _ in range(draws):
        vals.append(sum(cluster_scores[rng.randrange(n)] for __ in range(n)) / (4*n))
    vals.sort()
    return [vals[int(.025 * draws)], vals[int(.975 * draws)]]


def audit(folder: Path):
    assert_preoutcome()
    expected = {
        "factorial_%s_chunk%d_truth%d_%s.json" % (task, chunk, t, kind)
        for task in TASKS for chunk in range(2) for t in CONDITIONS
        for kind in ("original8", "audit")
    }
    actual = {p.name for p in folder.glob("factorial_*.json")}
    if actual != expected:
        raise ValueError("Missing/extra prospective physical evidence: missing=%s extra=%s"
                         % (sorted(expected - actual), sorted(actual - expected)))
    all_rows = []
    digests = {}
    for task in TASKS:
        for chunk in range(2):
            for t in CONDITIONS:
                prefix = "factorial_%s_chunk%d_truth%d" % (task, chunk, t)
                original = folder / (prefix + "_original8.json")
                raw = original.read_bytes()
                if not raw:
                    raise ValueError("Empty physically stepped source")
                evaluated = validate(json.loads(raw), task, chunk, t)
                evaluated.update(
                    schema="same_reset_factorial_true_2x2_shard_audit_v1",
                    physical_original_sha256=hashlib.sha256(raw).hexdigest(),
                    prereg_git_blob=blob(PREREG),
                    new_runner_git_blob=blob(SOURCE),
                    unchanged_response_model_git_blob=blob(CLASSIFIER),
                )
                ref_audit = folder / (prefix + "_audit.json")
                if json.loads(ref_audit.read_bytes()) != evaluated:
                    raise ValueError("Source-audited and independent shard outcomes differ: " + prefix)
                digests[original.name] = hashlib.sha256(raw).hexdigest()
                digests[ref_audit.name] = hashlib.sha256(ref_audit.read_bytes()).hexdigest()
                all_rows.extend(evaluated["rows"])

    if len(all_rows) != 128:
        raise ValueError("All 128 source cells are mandatory")
    indexed = {}
    by_seed = defaultdict(dict)
    for r in all_rows:
        key = (r["task"], r["seed"], r["truth_index"])
        if key in indexed or r["truth"] != "/".join(truth(r["truth_index"])):
            raise ValueError("Duplicate or wrong physical truth cell: %s" % (key,))
        indexed[key] = r
        by_seed[(r["task"], r["seed"])][r["truth_index"]] = r
    required = {
        (task, seed, t)
        for task in TASKS
        for chunk in range(2)
        for seed in select(task, chunk)
        for t in CONDITIONS
    }
    if set(indexed) != required or len(by_seed) != 32:
        raise ValueError("Original within-seed fully crossed denominator incomplete")

    # This is the central scientific gate missing from prior truth-stratified study:
    # physical initial observations MUST agree across all four condition worlds.
    for key, conditions in by_seed.items():
        if set(conditions) != set(CONDITIONS):
            raise ValueError("Incomplete same-seed matched block " + str(key))
        hashes = [conditions[t].get("initial_source_physical_obs_sha256") for t in CONDITIONS]
        if any(not isinstance(h, str) or len(h) != 64
               or any(c not in "0123456789abcdef" for c in h) for h in hashes):
            raise ValueError("Missing/verifiably malformed physical initial-observation hash " + str(key))
        if len(set(hashes)) != 1:
            raise ValueError("Four physical conditions DID NOT start from identical physical source observation " + str(key))

    totals = {a: {"official_task_success": 0, "decision_private_reads": 0} for a in ARMS}
    strata = {}
    for task in TASKS:
        for t in CONDITIONS:
            rows = [indexed[(task, seed, t)] for chunk in range(2) for seed in select(task, chunk)]
            if len(rows) != 16:
                raise ValueError("Wrong per-task/condition denominator")
            strata[task + "/" + "/".join(truth(t))] = {
                "source_seed_clusters": 16,
                "public_success": sum(r["new_success"] for r in rows),
                "strong_success": sum(r["strong_success"] for r in rows),
                "fixed_success": sum(r["fixed_success"] for r in rows),
                "held_success": sum(r["held_success"] for r in rows),
                "public_private_reads": sum(r["new_reads"] for r in rows),
                "strong_private_reads": sum(r["strong_reads"] for r in rows),
                "public_confident": sum(r["public_authorized"] is True for r in rows),
                "public_wrong_confident": sum(r["wrong_confident"] is True for r in rows),
                "public_exposed_both_physical_faults": sum(r["public_both_faults_exposed"] for r in rows),
                "all_faulted_arms_reached_neutral_probe": sum(r["all_faulted_arms_received_neutral_probe"] for r in rows),
            }
    pairing = Counter({"both": 0, "neither": 0, "public_only": 0, "strong_only": 0})
    public_samples = 0
    for r in all_rows:
        arm_outcomes = {
            "public": (r["new_success"], r["new_reads"]),
            "strong_task": (r["strong_success"], r["strong_reads"]),
            "fixed_t5": (r["fixed_success"], r["fixed_reads"]),
            "always_held": (r["held_success"], 0),
        }
        for a, (s, reads) in arm_outcomes.items():
            totals[a]["official_task_success"] += int(s)
            totals[a]["decision_private_reads"] += reads
        a, b = r["new_success"], r["strong_success"]
        pairing["both" if a and b else "public_only" if a else "strong_only" if b else "neither"] += 1
        public_samples += r["public_sample_events"]
    cluster_differences = [
        sum(int(by_seed[key][t]["new_success"]) - int(by_seed[key][t]["strong_success"]) for t in CONDITIONS)
        for key in sorted(by_seed)
    ]
    if sum(pairing.values()) != 128:
        raise ValueError("Paired method outcomes missing")
    saved = totals["strong_task"]["decision_private_reads"] - totals["public"]["decision_private_reads"]
    result = {
        "schema": "prospective_same_seed_four_physical_truths_full_independent_native_PhysX_audit_v1",
        "interpretation": "AUTHOR-RUN and SIMULATOR-ONLY; no claimed independent replication",
        "registered_source_reset_clusters": 32,
        "matched_physical_truth_conditions_per_cluster": 4,
        "registered_task_seed_truth_cells": 128,
        "separate_physx_worlds": 1152,
        "complete_16_shard_sha256": digests,
        "frozen_preoutcome_git_blob": blob(PREREG),
        "frozen_native_source_git_blob": blob(SOURCE),
        "same_initial_physical_source_observation_hash_per_truth_verified": True,
        "per_task_per_truth": strata,
        "primary_outcomes": totals,
        "paired_public_vs_strong": dict(pairing),
        "total_public_xyz_sample_events": public_samples,
        "private_read_break_even_equivalent_per_public_sample_if_positive": (
            saved / public_samples if saved >= 0 and public_samples else None
        ),
        "method_success_delta_public_minus_strong_per_cell": sum(cluster_differences) / 128,
        "seed_cluster_exact_swap_two_sided_sensitivity_p_not_randomized_proof": exact_cluster_swap_p(cluster_differences),
        "seed_cluster_bootstrap_95pct_public_minus_strong_success_gap": cluster_bootstrap_delta(cluster_differences),
        "public_wrong_confident_count": sum(int(r["wrong_confident"]) for r in all_rows),
        "incomplete_both_fault_exposure_count": sum(not r["public_both_faults_exposed"] for r in all_rows),
        "equal_neutral_probe_main_comparator_limit": "Arms refusing before t4 are not falsely described as probe-exposed",
        "claims_not_established": [
            "Task success superiority, noninferiority, zero-error certificate, matched-privacy active probing",
            "ActionShift reproduction, out-of-domain robot transfer, hardware safety or VLA benchmark",
            "Third-party original physical replication or physically calibrated XYZ/query exchange rate",
        ],
        "all_source_rows_retained": all_rows,
    }
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    out = audit(a.source_dir)
    a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print("SAME_SEED_PHYSICAL_FACTORIAL_ALL_POPULATION_INDEPENDENT_AUDIT",
          json.dumps({
              "clusters": out["registered_source_reset_clusters"],
              "cells": out["registered_task_seed_truth_cells"],
              "outcomes": out["primary_outcomes"],
              "paired": out["paired_public_vs_strong"],
              "swap_p": out["seed_cluster_exact_swap_two_sided_sensitivity_p_not_randomized_proof"],
          }, sort_keys=True))


if __name__ == "__main__":
    main()
