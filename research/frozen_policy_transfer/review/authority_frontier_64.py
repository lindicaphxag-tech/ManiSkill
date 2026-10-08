"""Read-only, exact paired-success / privileged-authorization frontier for 64 REAL PhysX states.

No simulator, no retraining and NO second replication. Validates byte SHA-256
of all eight original creator artifacts and reuses the exact original cohort
auditor before any statistical or utility computation.

This is post-outcome descriptive/exploratory analysis. Not pre-registered
non-inferiority, not a general safety/cost certificate or outside adoption.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import comb, sqrt
from pathlib import Path

from research.audit_new64_bounded_query import ADAPTIVE, MANDATORY, MODELS, audit

NO_QUERY = "fault_robust_two_history_without_query"
OPTIMISTIC = "fault_optimistic_unverified_ack"
COMPARATORS = (MANDATORY, NO_QUERY, OPTIMISTIC)
EXPECTED_SHA_FILE = "SHA256SUMS"
# Pre-existing, already-public original source SHA256SUMS Git blob (not a new
# manifest fingerprint calculated after these audit results were viewed).
# Replacing BOTH the original result JSON and its manifest must fail closed.
ORIGINAL_SOURCE_MANIFEST_GIT_BLOB = "64c3b913a9afbdfbcd374f176c484ee7b6576f93"
EXPECTED_FILES = tuple(
    f"bounded_query_holdout_{task}_chunk{chunk}_original8.json"
    for task in MODELS for chunk in range(4)
)


def verify_original_sha256(directory: Path) -> dict[str, str]:
    manifest = (directory / EXPECTED_SHA_FILE).read_bytes()
    original_blob = hashlib.sha1(
        b"blob " + str(len(manifest)).encode("ascii") + b"\\0" + manifest
    ).hexdigest()
    if original_blob != ORIGINAL_SOURCE_MANIFEST_GIT_BLOB:
        raise ValueError("Pinned original experiment SHA256SUMS manifest changed")
    raw = manifest.decode("ascii").splitlines()
    if len(raw) != len(EXPECTED_FILES):
        raise ValueError("Eight unmodified source SHA-256 entries required")
    found = {}
    for line in raw:
        parts = line.split()
        if len(parts) != 2 or len(parts[0]) != 64 or parts[1] in found:
            raise ValueError("Malformed, duplicate or missing original SHA-256 record")
        name = parts[1]
        if name not in EXPECTED_FILES or any(c not in "0123456789abcdef" for c in parts[0]):
            raise ValueError("Unexpected original file or invalid SHA-256")
        found[name] = parts[0]
    if set(found) != set(EXPECTED_FILES):
        raise ValueError("Original source bank incomplete")
    for name, digest in found.items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Original source artifact hash mismatch: {name}")
    return dict(sorted(found.items()))


def exact_matched_success(a: list[bool], b: list[bool]) -> dict:
    """Two-sided conditional discordant-pair test; no iid-arm assumption."""
    if len(a) != len(b) or len(a) == 0:
        raise ValueError("Missing or unequal paired task-state sample")
    if any(type(x) is not bool or type(y) is not bool for x, y in zip(a, b)):
        raise ValueError("Paired success must be exact booleans")
    exclusive_a = sum(x and not y for x, y in zip(a, b))
    exclusive_b = sum(y and not x for x, y in zip(a, b))
    discordant = exclusive_a + exclusive_b
    # This is an exploratory exact McNemar-style conditional statistic, not
    # evidence of a preregistered task-success noninferiority margin.
    numerator = sum(comb(discordant, i) for i in range(min(exclusive_a, exclusive_b) + 1))
    p = min(1., (2 * numerator) / (2 ** discordant))
    return {
        "matched_task_reset_states": len(a),
        "adaptive_successes": sum(a),
        "comparison_successes": sum(b),
        "adaptive_only": exclusive_a,
        "comparison_only": exclusive_b,
        "both_succeed": sum(x and y for x, y in zip(a, b)),
        "both_fail": sum(not x and not y for x, y in zip(a, b)),
        "two_sided_exploratory_exact_p": p,
        "delta_success_count": sum(a) - sum(b),
        "delta_success_per_original_state": (sum(a) - sum(b)) / len(a),
    }


def wilson_interval(k: int, n: int, z: float = 1.959963984540054):
    """Descriptive binomial Wilson interval; zero guarantees on new tasks."""
    if type(k) is not int or type(n) is not int or not 0 <= k <= n or n == 0:
        raise ValueError("Invalid Wilson interval count")
    phat = k / n
    denom = 1 + z * z / n
    center = (phat + z*z/(2*n)) / denom
    h = z / denom * sqrt(phat*(1-phat)/n + z*z/(4*n*n))
    return [max(0., center-h), min(1., center+h)]


def _expected_readbacks(method: str, rows: list) -> int:
    if method == ADAPTIVE:
        reads = [x["selective_readback"] for x in rows]
        if any(type(v) is not int or v not in (0, 1) for v in reads):
            raise ValueError("Invalid selective privileged readback")
        return sum(reads)
    if method == MANDATORY:
        return len(rows)
    if method in (NO_QUERY, OPTIMISTIC):
        return 0
    raise ValueError("Unknown method or hidden information-cost assumption")


def compute_frontier(rows: list[dict]) -> dict:
    if not rows or len({(r["task"],r["seed"]) for r in rows}) != len(rows):
        raise ValueError("Original state identity duplicated or absent")
    for r in rows:
        if any(type(r["success"].get(m)) is not bool for m in (ADAPTIVE, *COMPARATORS)):
            raise ValueError("Method outcome missing or fabricated")
    arms = (ADAPTIVE, *COMPARATORS)
    successes = {m: sum(r["success"][m] for r in rows) for m in arms}
    reads = {m: _expected_readbacks(m, rows) for m in arms}
    # λ means one privileged controller readback costs λ units of ONE binary
    # task success. These crossing values are DESCRIPTIVE, determined after
    # outcomes, not empirically optimized or a learned control policy.
    crossings = {}
    for comparator in COMPARATORS:
        dq = reads[ADAPTIVE] - reads[comparator]
        ds = successes[ADAPTIVE] - successes[comparator]
        crossings[comparator] = {
            "delta_successes": ds,
            "delta_privileged_target_reads": dq,
            "equal_empirical_aggregate_utility_lambda": (
                ds/dq if dq else None
            ),
            "interpretation": (
                "U=sum_success-lambda*decision_reads; crossing only if nonzero dq, "
                "not a population optimum or precommitted clinical cost"
            ),
        }
    return {
        "original_state_count": len(rows),
        "sources_are_frozen_policy_seeds_not_different_learned_models": True,
        "arm_success_counts": successes,
        "privileged_decision_readbacks": reads,
        "selective_read_fraction": reads[ADAPTIVE]/len(rows),
        "selective_read_fraction_wilson95_descriptive": wilson_interval(reads[ADAPTIVE],len(rows)),
        "relative_target_query_reduction_vs_mandatory": 1-reads[ADAPTIVE]/reads[MANDATORY],
        "exact_paired_outcomes": {
            comparator: exact_matched_success(
                [r["success"][ADAPTIVE] for r in rows],
                [r["success"][comparator] for r in rows])
            for comparator in COMPARATORS
        },
        "observed_success_vs_privileged_read_cost_crossings": crossings,
        "noninferiority_statistically_established": False,
        "causal_information_equivalence_with_mandatory_or_zero_query": False,
        "external_replication": False,
        "robot_hardware_safety_certified": False,
    }


def audit_authority_frontier(directory: Path) -> dict:
    expected_files = verify_original_sha256(directory)
    original = audit(directory)  # full frozen provenance, all 64 state rows,
                                 # matched seven arms, simulated fault, info budget
    by_task = {}
    for task, (_, first, _) in MODELS.items():
        rows = []
        for chunk in range(4):
            name = f"bounded_query_holdout_{task}_chunk{chunk}_original8.json"
            source = json.loads((directory / name).read_text("utf-8"))
            for case in source["episodes"]:
                rows.append({
                    "task": task, "seed": case["seed"],
                    "success": case["success_once"],
                    "selective_readback": case["privileged_target_readback_decision_count"][ADAPTIVE],
                })
        if len(rows) != 32 or [r["seed"] for r in rows] != list(range(first, first+32)):
            raise ValueError("Original two pretrained policies' 32-state strata not preserved")
        by_task[task] = rows
    all_rows = by_task["pull_cube"] + by_task["stack_cube"]
    total = compute_frontier(all_rows)
    task_reports = {k: compute_frontier(v) for k,v in by_task.items()}
    if total["original_state_count"] != original["unique_original_seed_states"]:
        raise ValueError("Independent original cohort auditor and frontier disagree")
    if total["arm_success_counts"][ADAPTIVE] != original["original_native_task_success"][ADAPTIVE]:
        raise ValueError("Original frozen task-success mismatch")
    if total["privileged_decision_readbacks"][ADAPTIVE] != original["selective_privileged_readback_decisions"]:
        raise ValueError("Original frozen information use mismatch")
    return {
        "analysis": "post-outcome descriptive evidence-limited cost/benefit frontier",
        "source_original_8_files_sha256": expected_files,
        "official_original_real_physx_producer_run": 37828426195,
        "underlying_source_frozen_before_64_new_seeds": True,
        "original_model_checkpoint_verification": "independent source-level seven-arm auditor, both task checkpoint SHA",
        "two_actual_frozen_ppo_task_families": list(MODELS),
        "original_audit": original,
        "pooled_64_state_descriptive": total,
        "per_frozen_policy_task_stratum": task_reports,
        "pre_result_statistics_design_frozen": False,
        "any_new_physx_trials_run_by_this_audit": False,
        "external_investigator_has_reproduced_physics": False,
        "statistical_noninferiority_or_safety_guarantee": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = audit_authority_frontier(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    select = result["pooled_64_state_descriptive"]
    print(json.dumps({
        "original_physx_states": select["original_state_count"],
        "task_success": select["arm_success_counts"],
        "decision_readbacks": select["privileged_decision_readbacks"],
        "matched_selective_vs_mandatory": select["exact_paired_outcomes"][MANDATORY],
        "matched_selective_vs_zero_readback": select["exact_paired_outcomes"][NO_QUERY],
    },sort_keys=True))


if __name__ == "__main__":
    main()
