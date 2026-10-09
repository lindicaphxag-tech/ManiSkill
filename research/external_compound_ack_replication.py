"""Genuinely executable outside-account native PhysX Multi-ACK seven-world reproduction.

Third-party reviewer selects EIGHT new task seeds in a fork. Original PPO
weights and exact v3 algorithm/certifier Git blobs are pinned; the complete
original simulator rollout is executed rather than splicing author outcomes.
This script run by original author does NOT count as independent replication.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

METHOD_BLOB="99836af14205fe3e95e52a2e0d68237c7c8a9045"
BOUND_BLOB="36707a177549104ba5b4bd9bcebc76518f0d2840"
ORIGINAL_BLOB="1dc653cdc44e422c8340475ad00f828b3a41eb4f"
TWO_BLOB="bb5fd155b7291fb127f94138fca321201c8271c3"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
START_SEED=500001
ARMS=("source_no_fault","fault_oracle_private_target",
      "fault_optimistic_unverified_ack","fault_strict_common_exact",
      "fault_robust_two_history_without_query",
      "fault_robust_then_single_privileged_query",
      "fault_always_single_privileged_query")

def select(task,first):
    if task not in TASKS or type(first) is not int or first<START_SEED or first>2147483600:
        raise ValueError("Require official task and 8 integer seeds starting at >=500001")
    return tuple(range(first,first+8))

def verify_git_blobs():
    expected={
      "research/frozen_ppo_compound_ack_multi_belief.py":METHOD_BLOB,
      "research/multi_ack_se3_bounded.py":BOUND_BLOB,
      "research/frozen_ppo_ack_bounded_query.py":ORIGINAL_BLOB,
      "research/two_history_se3_robust.py":TWO_BLOB,
    }
    for path,h in expected.items():
        digest=subprocess.check_output(["git","hash-object",path],text=True).strip()
        if digest!=h:
            raise RuntimeError("Research algorithm source not byte-identical to original: "+path)
    return expected

def check_raw(raw,task,seeds):
    if (raw.get("schema")!="compound_two_unknown_ack_multihistory_physx_v1"
        or raw.get("task")!=TASKS[task]
        or raw.get("original_seed_population")!=list(seeds)
        or raw.get("two_consecutive_unknown_ack_target_hold_steps")!=[2,3]
        or tuple(raw.get("all_seven_actual_control_arms",()))!=ARMS
        or raw.get("frozen_model_retrained") is not False
        or raw.get("real_physx_simulator") is not True
        or raw.get("fault_is_native_target_hold_not_network_loss") is not True):
        raise ValueError("Not the original unchanged multi-ACK native experiment")
    rows=raw.get("episodes")
    if not isinstance(rows,list) or len(rows)!=8 or [r.get("seed") for r in rows]!=list(seeds):
        raise ValueError("All eight original source-state task outcomes are mandatory")
    successes={a:0 for a in ARMS}
    reads={a:0 for a in ARMS if a!="fault_oracle_private_target"}
    checked=masked=0
    max_width=0
    for row in rows:
        flags=row.get("success_once",{})
        q=row.get("privileged_target_readback_decision_count",{})
        if set(flags)!=set(ARMS) or any(type(flags[a]) is not bool for a in ARMS):
            raise ValueError("Official native PhysX task success flag missing/non-binary")
        if q.get("fault_oracle_private_target")!=-1:
            raise ValueError("Privileged continuous oracle access cannot be represented as free")
        for arm in ARMS:
            successes[arm]+=int(flags[arm])
            if arm!="fault_oracle_private_target":
                if type(q.get(arm)) is not int or q[arm] not in (0,1):
                    raise ValueError("Invalid real authoritative controller target read count")
                reads[arm]+=q[arm]
        if any(q[n] for n in (ARMS[0],ARMS[2],ARMS[3],ARMS[4])):
            raise ValueError("Private target read leaked to zero-read arm")
        for arm in ARMS[1:]:
            steps=[z.get("step") for z in row.get("faults",{}).get(arm,[])]
            if steps not in ([2,3],[2]) or (arm!=ARMS[3] and steps!=[2,3]):
                raise ValueError("Original double native target-hold intervention incomplete")
        belief=row.get("max_belief_width",{})
        if any(type(belief.get(arm)) is not int or belief[arm]<4 for arm in (ARMS[4],ARMS[5],ARMS[6])):
            raise ValueError("Four target-memory hypotheses not actually realized")
        max_width=max(max_width,max(belief.values()))
        audits=row.get("robust_native_target_bound_checks",{})
        for arm,items in row.get("certified_action_masked_by_injected_fault",{}).items():
            for z in items:
                masked+=1
                if (z.get("step") not in (2,3)
                    or z.get("native_action_did_not_execute") is not True
                    or z.get("claimed_physical_setpoint_certificate") is not False):
                    raise ValueError("Masked command must never be claimed physically certified")
        for arm,items in audits.items():
            for z in items:
                checked+=1
                if (z["step"] in (2,3)
                    or z["only_audit_after_physical_dispatch"] is not True
                    or z["position_error_m"]>z["worst_case_position_limit_m"]+1e-4+1e-10
                    or z["rot_error_rad"]>z["worst_case_rot_limit_rad"]+1e-4+1e-10):
                    raise ValueError("Dispatched commanded target violated claimed certificate")
    if successes!=raw.get("success_counts"):
        raise ValueError("Original full-denominator result tally mismatch")
    return {"all_8_states":list(seeds),"task":task,
            "source_true_native_successes":successes,
            "privileged_decision_reads":reads,
            "physically_dispatched_setpoint_checks":checked,
            "fault_masked_action_attempts_NOT_dispatched":masked,
            "max_actual_belief_width":max_width,
            "7_original_native_worlds_per_state":True,
            "not_externally_reproduced_until_an_actual_independent_fork_runs_it":True}

def selftest():
    assert select("pull_cube",500001)==tuple(range(500001,500009))
    for case in [("other",500001),("stack_cube",400001),("pull_cube",True),
                 ("pull_cube",2147483640)]:
        try:select(*case)
        except ValueError:pass
        else:raise AssertionError("Invalid externally chosen seed accepted")
    print("PASS externally selected new-seed/7-world strict input checks")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=TASKS,default="pull_cube")
    ap.add_argument("--first-seed",type=int,default=500001)
    ap.add_argument("--out",type=Path,default=Path("external_multi_ack_artifacts"))
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    selftest()
    if args.self_test:return
    seeds=select(args.task,args.first_seed)
    blobs=verify_git_blobs()
    os.environ["ABI_TASK"]=args.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    method=importlib.import_module("frozen_ppo_compound_ack_multi_belief")
    if (method.TASK!=args.task or method.FAULT_STEPS!=(2,3)
        or method.POS_BUDGET!=.05 or method.ROT_BUDGET!=.05
        or method.HORIZON!=50 or tuple(method.NAMES)!=ARMS):
        raise RuntimeError("Original research action or fault model mutated")
    method.SEEDS=seeds
    method.COHORT[args.task]=(method.TASK_NAME,seeds)
    args.out.mkdir(parents=True,exist_ok=True)
    method.main()  # actually executes all seven original paired ManiSkill PhysX worlds
    original=Path(f"compound_multi_ack_{args.task}_original8.json")
    if not original.is_file():
        raise RuntimeError("Genuine PhysX never produced original source JSON")
    original_bytes=original.read_bytes()
    original_raw=json.loads(original_bytes)
    summary=check_raw(original_raw,args.task,seeds)
    copy=args.out/f"outside_multi_ack_{args.task}_{seeds[0]}_8original.json"
    copy.write_bytes(original_bytes)
    summary.update({
       "original_native_physx_json_sha256":hashlib.sha256(original_bytes).hexdigest(),
       "original_method_git_blobs":blobs,
       "fork_actor":os.getenv("GITHUB_ACTOR","unknown"),
       "fork_repository":os.getenv("GITHUB_REPOSITORY","unknown"),
       "original_experiment_method_changed":False,
       "privileged_target_readback_is_not_public_kinematic_observation":True,
       "no_real_network_packet_loss":True,
       "real_hardware_safety":False,
       "independent_validation_requires_non_author_account_and_source_check":True,
    })
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("OUTSIDE_MULTI_ACK_REAL_PHYSX_RESULT",json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    main()
