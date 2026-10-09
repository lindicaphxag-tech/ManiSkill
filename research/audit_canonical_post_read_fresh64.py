"""Prospective canonical post-read equality control for actual 10-world PhysX.

Audits every full original 8-seed source shard. Does not execute simulations.
A corrected fixed query at t=4 and a StackCube phase query at t=4
MUST have the same actual dispatched native controller actions at every
step if physical/observation state and frozen PPO/controller are identical.

This is an implementation-confound falsifier, not evidence of task-level
novelty. A mismatch is reported as a FAILED gate, never omitted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter
from math import comb

NAMES=(
    "source_no_fault","fault_oracle_private_target",
    "fault_optimistic_unverified_ack","fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query",
    "fault_authority_slack_proactive_query",
    "fault_phase_value_query",
    "fault_fixed_readback_canonical",
)
PHASE="fault_phase_value_query"
FIXED="fault_always_single_privileged_query"
CORRECTED="fault_fixed_readback_canonical"
TASKS={"pull_cube":("PullCube-v1",970001,
        "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
       "stack_cube":("StackCube-v1",980001,
        "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")}
PROTOCOL="research/CANONICAL_POST_READ_FRESH64_PREREG_V1.json"
SOURCE_BLOB="7de4ef9be172c2e4e63bd043318f53e9e2ede688"
PRECOMMIT="d664ec2fe4bb3a5d86ff4de3b1e7797c199f3037"


def require(cond, msg):
    if not cond:
        raise ValueError(msg)


def p_exact(win:int,loss:int)->float:
    n=win+loss
    return 1. if n==0 else min(1.,2*sum(comb(n,k) for k in range(min(win,loss)+1))/2**n)


def audit(root:Path)->dict:
    files=sorted(root.rglob("canonical_post_read_*_original8.json"))
    require(len(files)==8,"Exactly eight original eight-seed native PhysX shards required")
    seen=set()
    pooled={n:0 for n in NAMES}
    priv={n:0 for n in NAMES if n!="fault_oracle_private_target"}
    cases=[]
    bytask={}
    for task,(env,first,model_hash) in TASKS.items():
        local=[]
        for chunk in range(4):
            filename=f"canonical_post_read_{task}_chunk{chunk}_original8.json"
            named=[p for p in files if p.name==filename]
            require(len(named)==1,"Missing original physical shard "+filename)
            q=json.loads(named[0].read_bytes())
            target=list(range(first+8*chunk,first+8*chunk+8))
            require(q.get("schema")=="canonical_post_readback_10arm_fresh64_v1"
                and q.get("original_seed_population")==target
                and q.get("original_external_frozen_checkpoint_sha256")==model_hash
                and q.get("task")==env
                and q.get("frozen_protocol")==PROTOCOL
                and q.get("precommitted_protocol_commit")==PRECOMMIT
                and q.get("original_frozen_runner_blob")==SOURCE_BLOB
                and q.get("frozen_model_retrained") is False
                and q.get("real_physx_simulator") is True
                and q.get("two_consecutive_unknown_ack_target_hold_steps")==[2,3]
                and q.get("fault_is_native_target_hold_not_network_loss") is True
                and tuple(q.get("all_ten_actual_control_arms",()))==NAMES,
                "Original preregistration/third-party PPO/controller/ten arms differ")
            rows=q.get("episodes")
            require(isinstance(rows,list) and len(rows)==8 and
                    [r.get("seed") for r in rows]==target,
                    "Original eight-seed trial full denominator missing")
            group_success={n:0 for n in NAMES}
            for row in rows:
                key=(task,row["seed"])
                require(key not in seen,"Repeated source seed")
                seen.add(key)
                success=row.get("success_once",{})
                read=row.get("privileged_target_readback_decision_count",{})
                require(set(success)==set(NAMES)
                        and all(type(success.get(n)) is bool for n in NAMES),
                        "Raw official task success matrix absent or changed")
                require(read.get("fault_oracle_private_target")==-1,
                        "Continuously private oracle falsely free")
                for n in NAMES:
                    group_success[n]+=int(success[n])
                    pooled[n]+=int(success[n])
                    if n!="fault_oracle_private_target":
                        require(type(read.get(n)) is int and read[n] in (0,1),
                                "Incorrect decision-time true target read ledger")
                        priv[n]+=read[n]
                # DO NOT drop a pre-fault failure. Retain true fault
                # coverage per actual comparator source world.
                fired={n:[f.get("step") for f in row.get("faults",{}).get(n,[])]
                       for n in NAMES[1:]}
                traces=row.get("actual_step_action_trace",{})
                require(set(traces)==set([PHASE,FIXED,CORRECTED]),
                        "Missing one physical comparator controller step trace")
                for n,t in traces.items():
                    require(isinstance(t,list) and
                            all("source_policy_native_action" in e and
                                "dispatched_native_controller_action" in e and
                                len(e["dispatched_native_controller_action"])==7
                                for e in t),"Native 7D action trace was not retained")
                a=traces[PHASE]
                b=traces[CORRECTED]
                max_native=0.
                matching=(len(a)==len(b))
                if matching:
                    for left,right in zip(a,b):
                        require(left["step"]==right["step"],
                                "Two canonical 10-arm comparators used different time indexing")
                        diff=max(abs(float(u)-float(v))
                                 for u,v in zip(left["dispatched_native_controller_action"],
                                                right["dispatched_native_controller_action"]))
                        max_native=max(max_native,diff)
                        if diff>1e-6:matching=False
                invariant=row.get("stack_post_readback_canonical_invariant",{})
                if task=="stack_cube":
                    require(invariant.get("applicable") is True,
                            "Expected true StackCube canonical comparison")
                    # This checks IMPLEMENTATION CONSISTENCY, not success. If
                    # a native physics discrepancy occurs, mark FAILED rather
                    # than hide the trial or rewrite selected outputs.
                    passed=bool(matching and
                        success[PHASE]==success[CORRECTED] and
                        read[PHASE]==read[CORRECTED])
                    require(invariant.get("passed") is passed,
                            "Original Stack result misreported invariant status")
                    require(invariant.get("same_controller_action_every_executed_step") is matching,
                            "Original source mismatched direct native-action replay")
                else:
                    passed=None
                result={
                    "task":task,"seed":row["seed"],
                    "physical_fault_exposure_by_arm":fired,
                    "phase_success":success[PHASE],
                    "legacy_fixed_success":success[FIXED],
                    "corrected_fixed_success":success[CORRECTED],
                    "phase_privileged_reads":read[PHASE],
                    "legacy_fixed_privileged_reads":read[FIXED],
                    "corrected_fixed_privileged_reads":read[CORRECTED],
                    "stack_corrected_controller_equivalence_pass":passed,
                    "stack_max_native_7d_action_abs_difference":max_native,
                    "canonical_comparator_steps":len(b),
                    "phase_comparator_steps":len(a),
                }
                local.append(result)
                cases.append(result)
            require(q.get("success_counts")==group_success,
                    "Original source summaries diverge from per-trial task success")
        bytask[task]={
            "original_states":len(local),
            "phase_success":sum(int(x["phase_success"]) for x in local),
            "legacy_fixed_success":sum(int(x["legacy_fixed_success"]) for x in local),
            "corrected_fixed_success":sum(int(x["corrected_fixed_success"]) for x in local),
            "phase_reads":sum(x["phase_privileged_reads"] for x in local),
            "legacy_fixed_reads":sum(x["legacy_fixed_privileged_reads"] for x in local),
            "corrected_fixed_reads":sum(x["corrected_fixed_privileged_reads"] for x in local),
            "stack_invariant_pass":(
                all(x["stack_corrected_controller_equivalence_pass"] is True for x in local)
                if task=="stack_cube" else None),
        }
    require(len(seen)==64,"The full 64 original samples are missing")
    paired={
        label:{
            "phase_only":sum(x["phase_success"] and not x[field] for x in cases),
            "other_only":sum(x[field] and not x["phase_success"] for x in cases),
        }
        for label,field in (("legacy_fixed","legacy_fixed_success"),
                            ("corrected_fixed","corrected_fixed_success"))
    }
    for v in paired.values():
        v["exact_two_sided_p_exploratory"]=p_exact(v["phase_only"],v["other_only"])
    return {
        "schema":"prospective_canonical_post_true_read_original64_integrity_v1",
        "research_status":"ORIGINAL_OWNER_RUN_SIMULATION_NOT_EXTERNAL_ACCEPTANCE",
        "states":64,"tasks":2,"native_stepped_controller_worlds":640,
        "primary_stack_same_information_same_action_invariant":
            bytask["stack_cube"]["stack_invariant_pass"],
        "overall_success_by_arm":pooled,
        "actual_decision_privileged_reads_by_arm":priv,
        "by_task":bytask,
        "paired":paired,
        "all_original_seed_results_and_fault_exposure":cases,
        "scope":["old fixed stale maybe_two is preserved and identified as confounded",
                 "corrected fixed arm differs ONLY by cache invalidation after true target read",
                 "target-setpoint guarantees do not imply grasp/contact task success",
                 "only two released PPOs on native Panda simulator",
                 "actual wired ACK loss, independent laboratory reproduction and hardware safety are not demonstrated"]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    out=audit(a.input_dir)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("CANONICAL_POST_READ_ORIGINAL64_AUDIT",json.dumps({
        "source_states":out["states"],
        "physical_native_controller_worlds":out["native_stepped_controller_worlds"],
        "stack_exact_information_action_invariant":out["primary_stack_same_information_same_action_invariant"],
        "by_task":out["by_task"],
        "paired":out["paired"],
    },sort_keys=True))


if __name__=="__main__":
    main()
