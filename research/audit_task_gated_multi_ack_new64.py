"""Third-party-friendly independent auditor for prospectively frozen task-gated K=4 ACK study.

Reads all eight physical original source JSONs and the eight associated
summary.json files emitted by an author-operated original PhysX run.
No ManiSkill, torch, weights, GPU, model prediction or network required.

A task-level route selected BEFORE episode reset can choose an entire
already executed comparator trajectory; it cannot splice actions or
outcome-selected portions of two counterfactual physical worlds.

An output from this auditor is a source-data recomputation, not an
independent research lab's policy/physics reexecution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from math import comb
from pathlib import Path

PROTO_BLOB = "b4dbd98d73d2a22d9960c5b510e09f3927d63c0d"
SOURCE_HASHES = {
    "research/frozen_ppo_compound_ack_multi_belief.py":
        "99836af14205fe3e95e52a2e0d68237c7c8a9045",
    "research/multi_ack_se3_bounded.py":
        "36707a177549104ba5b4bd9bcebc76518f0d2840",
    "research/frozen_ppo_ack_bounded_query.py":
        "1dc653cdc44e422c8340475ad00f828b3a41eb4f",
    "research/two_history_se3_robust.py":
        "bb5fd155b7291fb127f94138fca321201c8271c3",
}
ARMS = (
    "source_no_fault",
    "fault_oracle_private_target",
    "fault_optimistic_unverified_ack",
    "fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query",
)
SELECTIVE, MANDATORY, ZERO = ARMS[5], ARMS[6], ARMS[4]
TASKS = {
    "pull_cube": dict(first=520001, label="PullCube-v1", selected=SELECTIVE,
                      checkpoint="74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube": dict(first=530001, label="StackCube-v1", selected=MANDATORY,
                       checkpoint="e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"),
}


def exact_two_sided_discordance(wins: int, losses: int) -> float:
    """Conditional exact binomial McNemar test, no normal approximation."""
    if type(wins) is not int or type(losses) is not int or wins < 0 or losses < 0:
        raise ValueError("Nonnegative integer paired discordance required")
    n = wins + losses
    if not n:
        return 1.0
    return min(1.0, 2 * sum(comb(n, j) for j in range(min(wins, losses)+1))/2**n)


def _verify_source_file(raw: Path, summary: dict, task: str, chunk: int):
    data = raw.read_bytes()
    identity = hashlib.sha256(data).hexdigest()
    if summary.get("original_physx_raw_sha256") != identity:
        raise ValueError("A real original PhysX trial source JSON was changed")
    o = json.loads(data)
    spec = TASKS[task]
    seeds = list(range(spec["first"]+8*chunk, spec["first"]+8*chunk+8))
    if (
        o.get("schema") != "compound_two_unknown_ack_multihistory_physx_v1"
        or o.get("task") != spec["label"]
        or o.get("original_seed_population") != seeds
        or o.get("two_consecutive_unknown_ack_target_hold_steps") != [2, 3]
        or o.get("preoutcome_protocol") != "research/TASK_GATED_MULTI_ACK_FRESH64_V1.json"
        or o.get("original_external_frozen_checkpoint_sha256") != spec["checkpoint"]
        or o.get("frozen_model_retrained") is not False
        or o.get("real_physx_simulator") is not True
        or o.get("fault_is_native_target_hold_not_network_loss") is not True
        or tuple(o.get("all_seven_actual_control_arms", [])) != ARMS
    ):
        raise ValueError("Original native PPO/controller/seeds/fault source changed")
    rows = o.get("episodes")
    if not isinstance(rows, list) or len(rows) != 8 or [r.get("seed") for r in rows] != seeds:
        raise ValueError("Missing or reordered original physical trial")
    return o, rows


def audit(source_dir: Path) -> dict:
    # Original matrix job artifacts have nested task-specific directories.
    named = list(source_dir.rglob("task_gated_*_chunk*_original8.json"))
    summaries = list(source_dir.rglob("summary.json"))
    if len(named) != 8 or len(summaries) != 8:
        raise ValueError("All eight original task shards and per-shard ledgers required")
    if len({f.resolve() for f in named}) != 8:
        raise ValueError("Duplicated source file")
    total = Counter()
    private = Counter()
    per_task = {}
    all_pairs = []
    hash_ledger = {}
    for task, spec in TASKS.items():
        task_rows = []
        for chunk in range(4):
            basename = f"task_gated_{task}_chunk{chunk}_original8.json"
            matching = [p for p in named if p.name == basename]
            if len(matching) != 1:
                raise ValueError("Missing or duplicate registered task/shard: "+basename)
            source = matching[0]
            expected_summary = source.parent / "summary.json"
            if not expected_summary.is_file():
                raise ValueError("Original task-shard controller audit ledger absent")
            q = json.loads(expected_summary.read_text(encoding="utf-8"))
            if (
                q.get("task") != task
                or q.get("chunk") != chunk
                or q.get("seed_register") != list(range(spec["first"]+8*chunk,spec["first"]+8*chunk+8))
                or q.get("precommitted_task_route") != spec["selected"]
                or q.get("source_git_blobs") != SOURCE_HASHES
                or q.get("frozen_protocol") != "research/TASK_GATED_MULTI_ACK_FRESH64_V1.json"
                or q.get("policy_decided_at_time") != "before environment reset, task ID only"
                or q.get("not_independent_external_lab") is not True
            ):
                raise ValueError("Preregistered routing, cohort, or frozen method source mismatch")
            original, rows = _verify_source_file(source,q,task,chunk)
            sums = Counter()
            reads = Counter()
            rerouted=[]
            for row in rows:
                flags = row.get("success_once",{})
                query = row.get("privileged_target_readback_decision_count",{})
                if (
                    set(flags) != set(ARMS) or
                    any(type(flags[k]) is not bool for k in ARMS)
                    or query.get(ARMS[1]) != -1
                    or any(type(query.get(k)) is not int or query[k] not in (0,1)
                           for k in ARMS if k!=ARMS[1])
                ):
                    raise ValueError("Original official outcome or read ledger corrupted")
                if any(query[n] for n in (ARMS[0], ARMS[2], ARMS[3], ARMS[4])):
                    raise ValueError("Unauthorized private memory read in no-query arm")
                for arm in ARMS[1:]:
                    actual=[v.get("step") for v in row.get("faults",{}).get(arm,[])]
                    # Only exact-only refusal may legitimately stop after
                    # the first unknown ACK due to known impossibility.
                    if actual not in ([2,3],[2]) or (arm!=ARMS[3] and actual!=[2,3]):
                        raise ValueError("Actual two physical holds or early exact refusal misrepresented")
                if any(row.get("max_belief_width",{}).get(n,0)<4 for n in (SELECTIVE, MANDATORY, ZERO)):
                    raise ValueError("Four actual controller histories were not observed")
                for arm in ARMS:
                    sums[arm]+=int(flags[arm])
                    if arm!=ARMS[1]:
                        reads[arm]+=query[arm]
                routed = {
                    "task":task,"seed":row["seed"],
                    "routed_actual_physx_arm":spec["selected"],
                    "routed_success":int(flags[spec["selected"]]),
                    "routed_privileged_reads":query[spec["selected"]],
                    "fixed_actual_native_success":int(flags[MANDATORY]),
                    "fixed_actual_privileged_reads":query[MANDATORY],
                    "selective_actual_native_success":int(flags[SELECTIVE]),
                    "selective_actual_privileged_reads":query[SELECTIVE],
                    "zero_query_actual_native_success":int(flags[ZERO]),
                }
                rerouted.append(routed)
                task_rows.append(routed)
            if original.get("success_counts") != dict(sums):
                raise ValueError("Real PhysX original native success counts do not match per-seed flags")
            if (
                q.get("source_full_original_native_success_counts") != dict(sums)
                or q.get("source_full_original_true_decision_read_counts") !=
                    {k:reads[k] for k in ARMS if k!=ARMS[1]}
                or q.get("all_original_eight_source_state_outcomes") != rerouted
                or q.get("routed_policy_complete_native_successes") !=
                    sum(z["routed_success"] for z in rerouted)
                or q.get("routed_policy_true_privileged_reads") !=
                    sum(z["routed_privileged_reads"] for z in rerouted)
            ):
                raise ValueError("Task-conditioned output was outcome-selected or mistranscribed")
            for arm in ARMS:
                total[arm] += sums[arm]
                if arm != ARMS[1]:
                    private[arm] += reads[arm]
            hash_ledger[basename] = q["original_physx_raw_sha256"]
        if len(task_rows)!=32:
            raise ValueError("Incomplete task stratum")
        per_task[task]={
            "n":32,
            "routed_task_success":sum(r["routed_success"] for r in task_rows),
            "routed_privileged_reads":sum(r["routed_privileged_reads"] for r in task_rows),
            "selective_success":sum(r["selective_actual_native_success"] for r in task_rows),
            "fixed_success":sum(r["fixed_actual_native_success"] for r in task_rows),
        }
        all_pairs += task_rows
    if len(all_pairs)!=64 or len({(r["task"],r["seed"]) for r in all_pairs})!=64:
        raise ValueError("Unmatched or missing original registered state")
    routed_succ=sum(r["routed_success"] for r in all_pairs)
    routed_reads=sum(r["routed_privileged_reads"] for r in all_pairs)
    discordance={
        "routed_only":sum(r["routed_success"] and not r["fixed_actual_native_success"] for r in all_pairs),
        "mandatory_only":sum(r["fixed_actual_native_success"] and not r["routed_success"] for r in all_pairs),
    }
    discordance["conditional_exact_two_sided_p_unadjusted"]=exact_two_sided_discordance(
        discordance["routed_only"],discordance["mandatory_only"])
    return {
        "schema":"task_gated_multi_ack_64_prespecified_original_audit_v1",
        "status":"SOURCE_ONLY_OWNER_RUN_PHYSX_NOT_EXTERNAL_REPRODUCTION",
        "task_only_router": {k:v["selected"] for k,v in TASKS.items()},
        "distinct_original_reset_states":64,
        "genuine_native_7_arm_stepped_worlds_if_source_trusted":448,
        "original_double_fault_steps":[2,3],
        "four_target_memory_hypotheses_verified_in_all_relevant_trials":True,
        "original_sha256_8_full_shards":hash_ledger,
        "per_task":per_task,
        "source_native_arm_success":dict(total),
        "source_native_private_reads":dict(private),
        "routed_success_total":routed_succ,
        "routed_true_private_reads_total":routed_reads,
        "mandatory_success_total":total[MANDATORY],
        "mandatory_true_private_reads_total":private[MANDATORY],
        "routed_vs_mandatory_paired":discordance,
        "inference_limits":[
            "No independently controlled third-party lab reproduction; source-only replay of owner-run artifacts.",
            "Task-only route chosen using previously observed 64-state DEVELOPMENT results; this is a new test of the route, not a newly learned policy.",
            "Two task policies on one Panda controller family, 64 reset states not 64 independent robots.",
            "Exact discordance p is descriptive/exploratory unless sampling and multiple-testing assumptions are predeclared.",
            "After-the-fact task selection was disallowed, but the selected whole trajectory is the already ACTUALLY stepped comparator world, not a newly executed eighth control world.",
            "Privileged readback counts are decision-only; audits are separately recorded, oracle is not free.",
            "Actual physical intervention is simulated native arm target hold, not TCP packet loss or robot hardware safety.",
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    q=audit(args.input_dir)
    args.output.write_text(json.dumps(q,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("FRESH64_TASK_GATED_COMPLETE_SOURCE_AUDIT",json.dumps({
        "tasks":q["per_task"],
        "routed":q["routed_success_total"],
        "routed_reads":q["routed_true_private_reads_total"],
        "mandatory":q["mandatory_success_total"],
        "mandatory_reads":q["mandatory_true_private_reads_total"],
        "paired":q["routed_vs_mandatory_paired"],
    },sort_keys=True))


if __name__=="__main__":
    main()
