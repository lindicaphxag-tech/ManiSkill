"""Precommitted TASK-GATED one-private-read policy, independent 64-state holdout.

Source native PhysX PPO/controller unchanged, byte-locked to original
published successful v3 runner. The task gate is chosen BEFORE reset:
  PullCube => certificate-failure selective read
  StackCube => one fixed-t4 read
Every candidate controller arm is actually stepped in the simulator;
the gate selects ONE whole, already physically executed native trajectory,
never splices per-step counterfactual responses or queries test outcomes.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

PROTOCOL="research/TASK_GATED_MULTI_ACK_FRESH64_V1.json"
START={"pull_cube":520001,"stack_cube":530001}
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
ARMS=("source_no_fault","fault_oracle_private_target",
      "fault_optimistic_unverified_ack","fault_strict_common_exact",
      "fault_robust_two_history_without_query",
      "fault_robust_then_single_privileged_query",
      "fault_always_single_privileged_query")
SELECTIVE=ARMS[5]; FIXED=ARMS[6]; ZERO=ARMS[4]
ROUTE={"pull_cube":SELECTIVE,"stack_cube":FIXED}
ORIGINAL_SHA={
  "research/frozen_ppo_compound_ack_multi_belief.py":"99836af14205fe3e95e52a2e0d68237c7c8a9045",
  "research/multi_ack_se3_bounded.py":"36707a177549104ba5b4bd9bcebc76518f0d2840",
  "research/frozen_ppo_ack_bounded_query.py":"1dc653cdc44e422c8340475ad00f828b3a41eb4f",
  "research/two_history_se3_robust.py":"bb5fd155b7291fb127f94138fca321201c8271c3",
}
CHECKPOINT={
  "pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
  "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}

def accepted(task,chunk):
    if task not in TASKS or type(chunk) is not int or chunk not in range(4):
        raise ValueError("Only eight fixed unseen shard identities accepted")
    first=START[task]+8*chunk
    return tuple(range(first,first+8))

def check_git_source():
    for path,expected in ORIGINAL_SHA.items():
        actual=subprocess.check_output(["git","hash-object",path],text=True).strip()
        if actual!=expected:
            raise ValueError("Frozen original PhysX source drift: "+path)
    precommit=json.loads(Path(PROTOCOL).read_text("utf-8"))
    if (precommit.get("schema")!="preregistered_task_gated_multi_ack_frozen_PPO_20261009_v1"
        or precommit["precommitted_router"]["pull_cube"]!=SELECTIVE
        or precommit["precommitted_router"]["stack_cube"]!=FIXED):
        raise ValueError("Precommitted whole-trajectory task gate changed")
    return precommit

def summarize(original,task,chunk,seeds):
    if (original.get("schema")!="compound_two_unknown_ack_multihistory_physx_v1"
        or original.get("task")!=TASKS[task]
        or original.get("original_seed_population")!=list(seeds)
        or original.get("two_consecutive_unknown_ack_target_hold_steps")!=[2,3]
        or original.get("preoutcome_protocol")!=PROTOCOL
        or original.get("frozen_model_retrained") is not False
        or original.get("real_physx_simulator") is not True
        or original.get("fault_is_native_target_hold_not_network_loss") is not True
        or original.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT[task]
        or tuple(original.get("all_seven_actual_control_arms",()))!=ARMS):
        raise ValueError("Original seven-world source/native fault identity changed")
    rows=original.get("episodes")
    if (not isinstance(rows,list) or len(rows)!=8
        or [row.get("seed") for row in rows]!=list(seeds)):
        raise ValueError("Incomplete eight original source episodes")
    route=ROUTE[task]
    outcomes={n:0 for n in ARMS}
    reads={n:0 for n in ARMS if n!=ARMS[1]}
    actual_checks=masked_attempts=0
    all_rows=[]
    for row in rows:
        flags=row.get("success_once",{})
        q=row.get("privileged_target_readback_decision_count",{})
        if set(flags)!=set(ARMS) or any(type(flags[n]) is not bool for n in ARMS):
            raise ValueError("Incomplete or fabricated actual ManiSkill task flag")
        if q.get(ARMS[1])!=-1:
            raise ValueError("Privileged oracle is not a zero-cost policy")
        for n in ARMS:
            outcomes[n]+=int(flags[n])
            if n!=ARMS[1]:
                if type(q.get(n)) is not int or q[n] not in (0,1):
                    raise ValueError("Incorrect explicit true controller target read count")
                reads[n]+=q[n]
        if any(q[n] for n in (ARMS[0],ARMS[2],ARMS[3],ARMS[4])):
            raise ValueError("Unrecorded privileged query in an ostensibly query-free arm")
        if any(row.get("max_belief_width",{}).get(n,0)<4 for n in (ZERO,SELECTIVE,FIXED)):
            raise ValueError("No demonstrated four-state uncertain commanded target memory")
        for n in ARMS[1:]:
            actual_fault_steps=[f.get("step") for f in row.get("faults",{}).get(n,[])]
            if actual_fault_steps not in ([2,3],[2]) or (n!=ARMS[3] and actual_fault_steps!=[2,3]):
                raise ValueError("Double physical arm-target hold intervention not reached")
        auditors=row.get("robust_native_target_bound_checks",{})
        for n,arr in row.get("certified_action_masked_by_injected_fault",{}).items():
            for item in arr:
                masked_attempts+=1
                if (item.get("step") not in (2,3) or
                    item.get("native_action_did_not_execute") is not True or
                    item.get("claimed_physical_setpoint_certificate") is not False):
                    raise ValueError("Fault-masked action falsely described as physical achievement")
        for n,arr in auditors.items():
            for item in arr:
                actual_checks+=1
                if (item["step"] in (2,3) or
                    item["only_audit_after_physical_dispatch"] is not True or
                    item["position_error_m"]>item["worst_case_position_limit_m"]+1e-4+1e-10 or
                    item["rot_error_rad"]>item["worst_case_rot_limit_rad"]+1e-4+1e-10):
                    raise ValueError("Original physical dispatch invalidates setpoint certificate")
        # Select a whole physically executed comparator trajectory only.
        all_rows.append({
           "task":task,"seed":row["seed"],
           "routed_actual_physx_arm":route,
           "routed_success":int(flags[route]),
           "routed_privileged_reads":q[route],
           "fixed_actual_native_success":int(flags[FIXED]),
           "fixed_actual_privileged_reads":q[FIXED],
           "selective_actual_native_success":int(flags[SELECTIVE]),
           "selective_actual_privileged_reads":q[SELECTIVE],
           "zero_query_actual_native_success":int(flags[ZERO])
        })
    if original.get("success_counts")!=outcomes:
        raise ValueError("Per-episode and reported native task counts differ")
    return {
      "task":task,"chunk":chunk,"seed_register":list(seeds),
      "policy_decided_at_time":"before environment reset, task ID only",
      "precommitted_task_route":route,
      "source_full_original_native_success_counts":outcomes,
      "source_full_original_true_decision_read_counts":reads,
      "physical_after_dispatch_checks":actual_checks,
      "physically_masked_certificates_not_counted":masked_attempts,
      "routed_policy_complete_native_successes":sum(r["routed_success"] for r in all_rows),
      "routed_policy_true_privileged_reads":sum(r["routed_privileged_reads"] for r in all_rows),
      "all_original_eight_source_state_outcomes":all_rows,
      "not_independent_external_lab":True,
      "known_task_specialization_not_general_policy":True,
      "real_packet_loss_executed":False
    }

def self_test():
    assert len({(task,seed) for task in TASKS for c in range(4) for seed in accepted(task,c)})==64
    for task,chunk in (("pull_cube",-1),("stack_cube",4),("bad",0),("pull_cube",True)):
        try:accepted(task,chunk)
        except ValueError:pass
        else:raise AssertionError("Unexpected unfrozen original seed selection accepted")
    assert ROUTE=={"pull_cube":SELECTIVE,"stack_cube":FIXED}
    print("PASS frozen task-dependent query selection and eight disjoint native PhysX cohorts")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS),default="pull_cube")
    p.add_argument("--chunk",type=int,default=0)
    p.add_argument("--out",type=Path,default=Path("task_gated_physx_original_evidence"))
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    self_test()
    if args.self_test:return
    seeds=accepted(args.task,args.chunk)
    check_git_source()
    os.environ["ABI_TASK"]=args.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_compound_ack_multi_belief")
    if (runner.TASK!=args.task or runner.FAULT_STEPS!=(2,3)
        or runner.POS_BUDGET!=.05 or runner.ROT_BUDGET!=.05
        or runner.HORIZON!=50 or tuple(runner.NAMES)!=ARMS):
        raise ValueError("Frozen original physical controller method cannot be amended")
    runner.SEEDS=seeds
    runner.COHORT[args.task]=(TASKS[args.task],seeds)
    runner.PROTO=PROTOCOL
    # Call unchanged ORIGINAL controller executor on every paired physical world.
    runner.main()
    filename=Path(f"compound_multi_ack_{args.task}_original8.json")
    raw=filename.read_bytes()
    original=json.loads(raw)
    summary=summarize(original,args.task,args.chunk,seeds)
    args.out.mkdir(parents=True,exist_ok=True)
    name=f"task_gated_{args.task}_chunk{args.chunk}_original8.json"
    (args.out/name).write_bytes(raw)
    summary.update({"original_physx_raw_sha256":hashlib.sha256(raw).hexdigest(),
                    "source_git_blobs":ORIGINAL_SHA,
                    "frozen_preoutcome_task_rule":ROUTE,
                    "frozen_protocol":PROTOCOL})
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("FRESH_TASK_GATED_NATIVE_PHYSX_RESULT",json.dumps({
       "task":args.task,"chunk":args.chunk,"routed_succ":summary["routed_policy_complete_native_successes"],
       "routed_reads":summary["routed_policy_true_privileged_reads"],
       "fixed_succ":summary["source_full_original_native_success_counts"][FIXED],
       "fixed_reads":summary["source_full_original_true_decision_read_counts"][FIXED],
       "selective_succ":summary["source_full_original_native_success_counts"][SELECTIVE],
       "physical_checks":summary["physical_after_dispatch_checks"],
    },sort_keys=True))

if __name__=="__main__":
    main()
