"""CPU-only, dependency-free evidence audit for the frozen policy stateful action ABI study.

Usage: python research/frozen_policy_transfer/review/verify_stateful_abi.py
Verifies *published files*; does NOT rerun physics or count as third-party replication.
"""
from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"
OBSERVER = EVIDENCE / "independent_history_observer_64"
ACK = EVIDENCE / "physical_ack_loss_resync_16"
CHECKPOINT = {
    "pull_cube": "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
    "stack_cube": "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}
EXPECTED_64 = {
    "pull_cube": {"source": 30, "projected": 30, "observer": 30, "stateless": 11},
    "stack_cube": {"source": 27, "projected": 27, "observer": 27, "stateless": 0},
}
EXPECTED_16 = {
    "pull_cube": {"source": 8, "projected": 8, "observer": 8, "stateless": 5},
    "stack_cube": {"source": 8, "projected": 8, "observer": 8, "stateless": 0},
}


def must(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> dict:
    must(path.is_file(), f"Original evidence file absent: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hashes(directory: Path) -> int:
    entries = (directory / "source_sha256.txt").read_text().splitlines()
    expected = {}
    for line in entries:
        digest, filename = line.split(maxsplit=1)
        filename = filename.removeprefix("./")
        must(filename.endswith(".json"), "Unexpected hashed file")
        must(filename not in expected, "Duplicate manifest file")
        expected[filename] = digest
    actual = {p.name for p in directory.glob("*.json")}
    must(set(expected) == actual, f"Missing/extra original source JSON in {directory}")
    for name, digest in expected.items():
        data = (directory / name).read_bytes()
        must(hashlib.sha256(data).hexdigest() == digest, f"SHA256 mismatch: {name}")
    return len(expected)


def ok(row: dict, arm: str) -> bool:
    value = row.get("success_once", {}).get(arm, False)
    must(type(value) is bool, f"Non-boolean task success for {arm}")
    return value


def audit_observer() -> dict:
    agg = read(OBSERVER / "independent-history-64-aggregate.json")
    out = {}
    for task, first in (("pull_cube", 83001), ("stack_cube", 93001)):
        rows = []
        for chunk in range(4):
            shard = read(OBSERVER / f"independent_observer_{task}_{chunk}.json")
            seeds = list(range(first + chunk * 8, first + chunk * 8 + 8))
            must(shard["checkpoint_sha256"] == CHECKPOINT[task], "Wrong frozen checkpoint")
            must(shard["seed_list"] == seeds, "Preregistered seed mismatch")
            must([r["seed"] for r in shard["episodes"]] == seeds, "Incomplete shard")
            must(shard["training_performed"] is False, "Training provenance violated")
            rows.extend(shard["episodes"])
        must([r["seed"] for r in rows] == list(range(first, first + 32)), "Full denominator mismatch")
        counts = {arm: sum(ok(r, arm) for r in rows) for arm in EXPECTED_64[task]}
        must(counts == EXPECTED_64[task], f"Original 64-state counts changed: {task}")
        paired = agg["results"][task]
        must(paired["success"]["observer"] == counts["observer"], "Aggregate discrepancy")
        must(paired["observer_vs_live_outcome_agreement"] == 32, "Live/observer disagreement")
        must(paired["evidence_gate"] == "MATCHED", "Preregistered gate failed")
        must(max(r["observer_end_target_error"]["max_position_abs"] for r in rows) <= 3e-5,
             "Observer target-pose drift exceeds declared audit tolerance")
        nonexact = sum(len(r.get("approximations", {}).get("observer", [])) for r in rows)
        must(nonexact == paired["nonexact_projection_events"]["observer"], "Projection events mismatch")
        only = sum(ok(r, "observer") and not ok(r, "stateless") for r in rows)
        reverse = sum(ok(r, "stateless") and not ok(r, "observer") for r in rows)
        out[task] = {"n": 32, "success": counts, "observer_only": only,
                     "stateless_only": reverse, "nonexact_projected_steps": nonexact}
    return out


def audit_ack() -> dict:
    agg = read(ACK / "ack-loss-physx-full-aggregate.json")
    must(agg["full_denominator"] == 16, "Fault episode denominator changed")
    out = {}
    for task, first in (("pull_cube", 85001), ("stack_cube", 95001)):
        data = read(ACK / f"ack_loss_physx_resync_{task}_8.json")
        rows = data["episodes"]
        must(data["checkpoint_sha256"] == CHECKPOINT[task], "Wrong fault-study checkpoint")
        must([r["seed"] for r in rows] == list(range(first, first + 8)), "Fault seeds mismatch")
        must(data["training_performed"] is False, "Unexpected policy training")
        must(data["fault_triggered_episodes"] == 8, "Unreached faults")
        for r in rows:
            fault = r["ack_loss_fault"]
            must(fault["triggered"] is True and fault["action_index"] == 2,
                 "Unregistered or missed fault")
            must(fault["physical_env_step_completed"] is True, "No actual PhysX command")
            must(fault["further_action_was_refused"] is True, "Unsafe non-refusal")
            must(fault["authoritative_target_reads_for_recovery"] == 1,
                 "Unexpected privileged recovery read count")
        counts = {arm: sum(ok(r, arm) for r in rows) for arm in EXPECTED_16[task]}
        must(counts == EXPECTED_16[task], f"Fault success count changed: {task}")
        must(agg["results"][task]["predeclared_gate"] == "SUPPORTED_WITH_PRIVILEGED_RESYNC",
             "Fault-study gate not met")
        out[task] = {"n": 8, "success": counts, "triggered_faults": 8,
                     "privileged_resync_reads": 8}
    return out



def audit_robust_query_new64() -> dict:
    """Check eight immutable source files and rerun 64-state query-budget arithmetic.

    This is a CPU-only bookkeeping audit of the actual public original
    PhysX JSONs; it does NOT rerun the policy, reset simulator or prove
    independent adoption. Never treat these NEW64 states as additional
    training policies or relabel the earlier 16-state discovery cohort.
    """
    folder = EVIDENCE / "robust_query_new64_142001_152032"
    entries = (folder / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    expected = {}
    for line in entries:
        digest, filename = line.split(maxsplit=1)
        filename = filename.removeprefix("./")
        must(filename.endswith(".json"), "Only original new64 JSON is permitted")
        must(filename not in expected, "Duplicate new64 SHA256 entry")
        expected[filename] = digest
    must(len(expected) == 8, "Exactly eight new64 original task chunks required")
    actual = {f.name for f in folder.glob("*.json")}
    must(actual == set(expected), "Incomplete or extra original new64 JSONs")
    for name, digest in expected.items():
        must(hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest,
             f"New64 original source SHA256 mismatch: {name}")

    # Reuse the existing full-denominator, provenance, per-arm and
    # decision-query verifier; it imports only Python standard library.
    auditor_path = Path(__file__).resolve().parents[3] / "audit_new64_bounded_query.py"
    # __file__ .../research/frozen_policy_transfer/review/verify_stateful_abi.py
    # parents[3] is checkout root; source auditor lives under research/.
    if not auditor_path.is_file():
        auditor_path = Path(__file__).resolve().parents[2] / "audit_new64_bounded_query.py"
    audit = runpy.run_path(str(auditor_path))["audit"]
    out = audit(folder)
    must(out["unique_original_seed_states"] == 64, "New64 cohort incomplete")
    must(out["selective_privileged_readback_decisions"] == 15,
         "New64 selective privileged reads changed")
    must(out["mandatory_privileged_readback_decisions"] == 64,
         "New64 compulsory privileged reads changed")
    paired = out["selective_vs_comparators"]["fault_always_single_privileged_query"]
    must(paired == {"adaptive_only": 5, "comparator_only": 2},
         "New64 paired comparison changed")
    return {
        "original_sha256_verified_files": len(expected),
        "original_source_run": out["source_physx_run_id"],
        "unique_new_task_states": out["unique_original_seed_states"],
        "actual_success_counts": out["original_native_task_success"],
        "selective_vs_mandatory_paired": paired,
        "selective_privileged_decision_reads": out["selective_privileged_readback_decisions"],
        "compulsory_privileged_decision_reads": out["mandatory_privileged_readback_decisions"],
        "scope": "ORIGINAL AUTHOR-RUN PHYSX FILE AUDIT ONLY",
    }



def audit_strict_budget64_negative() -> dict:
    """Audit a failed original prospective inference gate WITHOUT suppressing it.

    All eight original source files, their eight complete terminal logs,
    and the full original aggregate have exact SHA-256 identities anchored
    to the already trusted-main-preserved manifest itself.
    """
    folder = EVIDENCE / "strict_shared_16read_quota_new64_negative"
    manifest = (folder / "SHA256SUMS").read_bytes()
    must(hashlib.sha256(manifest).hexdigest() ==
         "0bc758fad0a1c31288805fb504f280c9bbde2216f050262e9b4b208d878f2ca4",
         "Original failed-study pinned manifest itself was changed")
    entries = manifest.decode("utf-8").splitlines()
    expected = {}
    for row in entries:
        digest, filename = row.split(maxsplit=1)
        must(filename not in expected and "/" not in filename and len(digest) == 64,
             "Duplicate or malicious source entry")
        expected[filename] = digest
    must(len(expected) == 17, "Original negative-study 17 evidence objects missing")
    expected_files = set(expected)
    actual_files = {p.name for p in folder.iterdir()
                    if p.is_file() and p.name not in ("SHA256SUMS", "README.md")}
    must(actual_files == expected_files, "Extra or missing raw negative study evidence")
    for name, digest in expected.items():
        must(hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest,
             "Negative source evidence mutated: "+name)

    source_auditor = Path(__file__).resolve().parents[2] / "audit_query_strict_budget64.py"
    recomputed = runpy.run_path(str(source_auditor))["audit"](folder)
    original = read(folder / "strict_quota_new64_full_original_audit.json")
    must(recomputed == original, "First complete original PhysX negative auditor mismatch")
    must(recomputed["original_new_distinct_seeds"] == 64,
         "Original intention-to-test denominator changed")
    must(len(recomputed["pre_fault_controller_refusal_witnesses"]) == 7,
         "Original pre-fault impossibility was hidden")
    must({r["seed"] for r in recomputed["pre_fault_controller_refusal_witnesses"]}
         == {370029}, "Source-invalid StackCube state changed")
    must(recomputed["predeclared_primary_efficacy_inference_gate_PASSED"] is False,
         "Original scientific hard gate was relabelled PASSED")
    must(recomputed["capped_adaptive_target_decision_reads"] == 10
         and recomputed["periodic_nonadaptive_target_decision_reads"] == 16,
         "Original actual query spending mutated")
    must(recomputed["native_task_success"]["fault_robust_quota_two_per_eight"] == 50
         and recomputed["native_task_success"]["fault_precommitted_seed_schedule_query"] == 44,
         "Original per-trial task failure flags were changed")
    must(recomputed["capped_adaptive_vs_periodic"]["adaptive_only"] == 9
         and recomputed["capped_adaptive_vs_periodic"]["comparator_only"] == 3,
         "Paired original fault experiment diverged")
    return {
        "status": "NEGATIVE_PROTOCOL_FAILED_NOT_CONFIRMATORY",
        "sha256_pinned_unchanged_original_files": len(expected),
        "original_intention_to_test_states": 64,
        "actual_capped_target_reads": 10,
        "actual_fixed_target_reads": 16,
        "pre_fault_unrepresentable_native_action_refusals": 7,
        "affected_seed": 370029,
        "full_fault_exposure_hard_gate_passed": False,
        "success_capped": 50,
        "success_fixed": 44,
        "independent_external_replication": False,
    }


def main() -> None:
    manifest_counts = {"observer": verify_hashes(OBSERVER), "ack": verify_hashes(ACK)}
    result = {"scope": "HASH-PINNED OWNER-RUN EVIDENCE AUDIT; NOT NEW PHYSX REPLICATION",
              "sha256_file_counts": manifest_counts,
              "observer_64": audit_observer(), "ack_recovery_16": audit_ack(),
              "bounded_or_query_NEW64": audit_robust_query_new64(),
              "strict_shared_budget_NEW64_NEGATIVE": audit_strict_budget64_negative()}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: SHA-256 pinned 64 observer + 16 readback + 64 fresh query-cohort original states, paired outcomes and provenance limits")


if __name__ == "__main__":
    main()
