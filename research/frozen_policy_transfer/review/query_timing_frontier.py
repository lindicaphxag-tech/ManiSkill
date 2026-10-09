"""Independent, stdlib-only, immutable-source audit of query timing / information frontier.

This REANALYZES the archived author-run 32-state native PhysX source cohort.
It is NOT a new policy experiment or an independently operated replication.

Usage:
  python -m research.frozen_policy_transfer.review.query_timing_frontier \
      --output /tmp/query_time_source_frontier.json

The original source-shard verifier is applied BEFORE computing any contrast.
Success rates and cost are not a certified hardware safety/objective theorem.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

from research.audit_query_time_causal_fresh32 import aggregate, ARMS, TASKS

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "query_timing_causal_new32_280001_290016"
ADAPTIVE = "fault_robust_then_single_privileged_query"
COMPARATORS = (
    "fault_fixed_query_t3", "fault_fixed_query_t5", "fault_fixed_query_t6",
    "fault_robust_two_history_without_query",
    "fault_optimistic_unverified_ack",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def source_hashes(folder: Path) -> dict[str, str]:
    """Fail closed on a missing, added, duplicated or changed original source file."""
    manifest = folder / "SHA256SUMS"
    require(manifest.is_file(), "Original SHA256 source manifest missing")
    entries: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.removeprefix("./")
        require(name not in entries and len(digest) == 64, "Repeated/malformed SHA manifest record")
        require("/" not in name and "\\" not in name, "Source manifest must name only local files")
        entries[name] = digest
    expected = {f"query_time_{task}_chunk{chunk}_original4.json"
                for task in TASKS for chunk in range(4)}
    expected.add("full_query_time_audit.json")
    require(set(entries) == expected, "Source files or archived complete audit missing in manifest")
    files = {p.name for p in folder.glob("*.json")}
    require(files == expected, "An expected source JSON was removed or an extra JSON was inserted")
    for name, digest in entries.items():
        require(hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest,
                "Original source SHA256 differs from archived manifest: " + name)
    return entries


def sign_test(first_only: int, second_only: int) -> float:
    """Exact two-sided sign test on the discordant paired *task* outcomes."""
    require(type(first_only) is int and first_only >= 0, "Invalid first-only count")
    require(type(second_only) is int and second_only >= 0, "Invalid second-only count")
    n = first_only + second_only
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(first_only, second_only) + 1))
    return min(1.0, 2.0 * tail / (2 ** n))


def paired(rows: list[dict], first: str, second: str) -> dict:
    wins = [r["seed"] for r in rows
            if r["success_once"][first] and not r["success_once"][second]]
    losses = [r["seed"] for r in rows
              if r["success_once"][second] and not r["success_once"][first]]
    both = sum(r["success_once"][first] and r["success_once"][second] for r in rows)
    neither = sum(not r["success_once"][first] and not r["success_once"][second] for r in rows)
    require(len(wins) + len(losses) + both + neither == len(rows), "Incomplete paired denominator")
    return {
        "first_only_seeds": wins,
        "second_only_seeds": losses,
        "both_succeed": both,
        "both_fail": neither,
        "two_sided_exact_p_exploratory_unadjusted": sign_test(len(wins), len(losses)),
    }


def study(folder: Path) -> dict:
    # The independent original audit validates exact policy, task, fault,
    # controller provenance, seed register, query STEP, refusal, and all rows.
    manifest = source_hashes(folder)
    fresh = aggregate(folder)
    archived = json.loads((folder / "full_query_time_audit.json").read_text(encoding="utf-8"))
    require(archived == fresh, "Independent re-audit differs from archived original 32-state aggregate")
    require(fresh["n_original_paired_native_physx_states"] == 32,
            "Expected exactly 32 original source task states")
    rows: list[dict] = []
    by_task = defaultdict(list)
    for task in TASKS:
        for chunk in range(4):
            trial = json.loads((folder/f"query_time_{task}_chunk{chunk}_original4.json").read_text())
            for row in trial["episodes"]:
                require(row["task"] == TASKS[task][0], "Task metadata does not match identity")
                by_task[task].append(row)
                rows.append(row)
    require(len(rows) == 32 and all(len(t) == 16 for t in by_task.values()),
            "Full denominator not preserved by task")
    require(len({(r["task"],r["seed"]) for r in rows}) == 32,
            "Duplicate registered reset state")

    arms = [
        "source_no_fault", "fault_oracle_private_target",
        "fault_optimistic_unverified_ack", "fault_robust_two_history_without_query",
        ADAPTIVE, "fault_fixed_query_t3", "fault_fixed_query_t5", "fault_fixed_query_t6"
    ]
    require(tuple(arms) == ARMS, "Frozen original source arm definitions changed")

    def scores(group: list[dict]) -> dict:
        return {a: {
            "task_success": sum(int(r["success_once"][a]) for r in group),
            "actual_target_decision_reads": sum(
                r["privileged_target_readback_decision_count"][a] for r in group),
        } for a in arms}

    def comparisons(group: list[dict]) -> dict:
        return {a: paired(group, ADAPTIVE, a) for a in COMPARATORS}

    pooled_scores = scores(rows)
    require(pooled_scores[ADAPTIVE] == {
        "task_success": 31, "actual_target_decision_reads": 7
    }, "Frozen event-triggered outcome has changed")
    require(pooled_scores["fault_fixed_query_t5"] == {
        "task_success": 32, "actual_target_decision_reads": 32
    }, "Frozen fixed-t5 physical result has changed")

    # This is a DESCRIPTIVE scoring convention, not a controller objective.
    # lambda is hypothetical utility cost per privileged controller read,
    # in units of one official task-success count. No lambda was tuned in
    # advance, and the optimizer is not the prospective trained method.
    thresholds = [0.0, 0.01, 0.025, 0.04, 0.05, 0.1, 0.2]
    frontier = [
        {
            "hypothetical_cost_per_target_read_in_success_equivalents": lam,
            "best_observed_arm_names": [
                name for name in arms[2:]
                if abs((pooled_scores[name]["task_success"] -
                        lam * pooled_scores[name]["actual_target_decision_reads"]) -
                        max(pooled_scores[x]["task_success"] -
                            lam * pooled_scores[x]["actual_target_decision_reads"]
                            for x in arms[2:])) < 1e-12],
            "per_arm_descriptive_utility": {
                name: pooled_scores[name]["task_success"] -
                      lam * pooled_scores[name]["actual_target_decision_reads"]
                for name in arms[2:]
            },
        }
        for lam in thresholds
    ]

    pair_t5 = paired(rows, ADAPTIVE, "fault_fixed_query_t5")
    require(pair_t5["first_only_seeds"] == [] and
            pair_t5["second_only_seeds"] == [290012],
            "The physical fixed-t5 counterexample is missing or altered")

    return {
        "schema": "independent_observed_information_cost_frontier_timing32_v1",
        "study_n_original_registered_reset_states": 32,
        "published_author_run_only": True,
        "physx_source_run": "https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37896223428",
        "original_source_sha256_manifest": manifest,
        "all_same_task_seed_separate_actual_simulator_worlds": True,
        "number_distinct_frozen_ppo_task_checkpoints": 2,
        "pooled_exact_task_success_and_query_read_counts": pooled_scores,
        "by_task": {
            t: {
                "n": len(by_task[t]),
                "scores": scores(by_task[t]),
                "paired_adaptive_vs_comparators": comparisons(by_task[t])
            } for t in TASKS
        },
        "paired_adaptive_vs_all_comparators": comparisons(rows),
        "t5_additional_success_seed": 290012,
        "fixed_t5_minus_adaptive_extra_privileged_reads": 25,
        "fixed_t5_minus_adaptive_additional_task_successes": 1,
        "descriptive_break_even_cost_per_target_read_success_equivalents": 1 / 25,
        "post_outcome_hypothetical_cost_frontier_NOT_prospective_policy_tuning": frontier,
        "limitations": [
            "Only author-operated ManiSkill CPU PhysX on two externally frozen PPO models",
            "All actual physical fault truths are a native arm zero delta, not dropped ROS packets",
            "The task outcome is the official simulator task success flag, not hardware safety",
            "Post-outcome cost frontier is descriptive and not evidence of optimal querying",
            "Exploratory sign-test p-values unadjusted for multiple comparator selection",
            "Read-budget treatments differ in actual reads, not an exact equal-information comparison",
            "No external independent lab has reproduced or accepted this result",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=EVIDENCE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = study(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("INDEPENDENT_QUERY_TIMING_PARETO_EVIDENCE", json.dumps({
        "n": result["study_n_original_registered_reset_states"],
        "adaptive": result["pooled_exact_task_success_and_query_read_counts"][ADAPTIVE],
        "fixed_t5": result["pooled_exact_task_success_and_query_read_counts"]["fault_fixed_query_t5"],
        "paired": result["paired_adaptive_vs_all_comparators"]["fault_fixed_query_t5"],
        "cost_break_even": result["descriptive_break_even_cost_per_target_read_success_equivalents"],
        "extra_fixed_t5_reads": result["fixed_t5_minus_adaptive_extra_privileged_reads"]
    }, sort_keys=True))


if __name__ == "__main__":
    main()
