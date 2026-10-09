"""Prospectively pre-registered 64 NEW native PhysX controller states.

Immutable v3 source and unchanged published third-party PPO models.
Runs exactly 8 physical reset states per (task, shard) and seven genuine worlds
per state; never splices counterfactual outcomes or skips failures.
This is experiment execution, NOT independent external-lab adoption.
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

BASES={"pull_cube":420001,"stack_cube":430001}
SOURCE_BLOB="99836af14205fe3e95e52a2e0d68237c7c8a9045"
MULTI_CERTIFIER_BLOB="36707a177549104ba5b4bd9bcebc76518f0d2840"
ORIGINAL_SOURCE_BLOB="1dc653cdc44e422c8340475ad00f828b3a41eb4f"
ORIGINAL_GEOMETRY_BLOB="bb5fd155b7291fb127f94138fca321201c8271c3"
PROTO="research/COMPOUND_ACK_NEW64_PROSPECTIVE_V1.md"
ARMS=("source_no_fault","fault_oracle_private_target",
      "fault_optimistic_unverified_ack","fault_strict_common_exact",
      "fault_robust_two_history_without_query",
      "fault_robust_then_single_privileged_query",
      "fault_always_single_privileged_query")
CHECKPOINT_SHA={
  "pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
  "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}


def validated(task,chunk):
    if task not in BASES or type(chunk) is not int or chunk not in (0,1,2,3):
        raise ValueError("Frozen prospective task and shard must be supported")
    start=BASES[task]+8*chunk
    return tuple(range(start,start+8))


def blob(path):
    return subprocess.check_output(["git","hash-object",path],text=True).strip()


def verify_source():
    expected={
      "research/frozen_ppo_compound_ack_multi_belief.py":SOURCE_BLOB,
      "research/multi_ack_se3_bounded.py":MULTI_CERTIFIER_BLOB,
      "research/frozen_ppo_ack_bounded_query.py":ORIGINAL_SOURCE_BLOB,
      "research/two_history_se3_robust.py":ORIGINAL_GEOMETRY_BLOB,
    }
    for path,sha in expected.items():
        if blob(path)!=sha:
            raise RuntimeError("Source drift from frozen multi-ACK physics: "+path)
    if not Path(PROTO).is_file():
        raise RuntimeError("Missing pre-outcome source protocol")
    return expected


def validate_result(r,task,chunk,seeds):
    if (r.get("schema")!="compound_two_unknown_ack_multihistory_physx_v1"
        or r.get("original_seed_population")!=list(seeds)
        or r.get("task")!=("PullCube-v1" if task=="pull_cube" else "StackCube-v1")
        or r.get("two_consecutive_unknown_ack_target_hold_steps")!=[2,3]
        or r.get("preoutcome_protocol")!=PROTO
        or r.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT_SHA[task]
        or r.get("frozen_model_retrained") is not False
        or r.get("real_physx_simulator") is not True
        or r.get("fault_is_native_target_hold_not_network_loss") is not True
        or tuple(r.get("all_seven_actual_control_arms",()))!=ARMS):
        raise ValueError("Changed original true PhysX method/protocol identity")
    rows=r.get("episodes")
    if not isinstance(rows,list) or len(rows)!=8 or [x["seed"] for x in rows]!=list(seeds):
        raise ValueError("Missing/reordered original full eight-state denominator")
    sums={n:0 for n in ARMS}
    reads={n:0 for n in ARMS if n!="fault_oracle_private_target"}
    physical_checks=0
    masked=0
    max_belief=0
    for row in rows:
        outcome=row.get("success_once")
        if (set(outcome)!=set(ARMS)
            or any(type(outcome[n]) is not bool for n in ARMS)):
            raise ValueError("Nonbinary or missing official simulator success outcomes")
        for n in ARMS:sums[n]+=int(outcome[n])
        q=row.get("privileged_target_readback_decision_count",{})
        if q.get("fault_oracle_private_target")!=-1:
            raise ValueError("Continuous oracle access falsely counted as free")
        for n in reads:
            if type(q.get(n)) is not int or q[n] not in (0,1):
                raise ValueError("Invalid per-arm private target read budget")
            if n in (ARMS[0],ARMS[2],ARMS[3],ARMS[4]) and q[n]!=0:
                raise ValueError("Unreported privileged query leaked into nonquery policy")
            reads[n]+=q[n]
        for n,width in row.get("max_belief_width",{}).items():
            if n not in ARMS or type(width) is not int or not 1<=width<=16:
                raise ValueError("Incomplete or invalid multi-ACK belief history")
            max_belief=max(max_belief,width)
        for n,arr in row.get("certified_action_masked_by_injected_fault",{}).items():
            for v in arr:
                masked+=1
                if (v["step"] not in (2,3)
                    or v["native_action_did_not_execute"] is not True
                    or v["claimed_physical_setpoint_certificate"] is not False):
                    raise ValueError("Masked command falsely treated as executed")
        for n,arr in row.get("robust_native_target_bound_checks",{}).items():
            for v in arr:
                physical_checks+=1
                if (v["step"] in (2,3)
                    or v["only_audit_after_physical_dispatch"] is not True
                    or v["position_error_m"]>v["worst_case_position_limit_m"]+1e-4+1e-10
                    or v["rot_error_rad"]>v["worst_case_rot_limit_rad"]+1e-4+1e-10):
                    raise ValueError("False bounded physical setpoint authorization")
    if sums!=r.get("success_counts"):
        raise ValueError("Whole-denominator official success totals do not reconcile")
    return {
        "task":task,"chunk":chunk,"seeds":list(seeds),
        "original_official_success_counts":sums,
        "privileged_decision_read_counts":reads,
        "genuine_afterdispatch_certified_setpoint_checks":physical_checks,
        "masked_commands_not_counted_as_dispatched":masked,
        "largest_actual_belief_width":max_belief,
        "no_source_training":True,
    }


def self_test():
    for task in BASES:
        starts=[validated(task,i) for i in range(4)]
        assert len({seed for tup in starts for seed in tup})==32
        for chunk, tup in enumerate(starts):
            assert tup[0]==BASES[task]+8*chunk and len(tup)==8
    for case in (("pull_cube",-1),("stack_cube",4),("unknown",0),
                 ("pull_cube",True)):
        try:validated(*case)
        except ValueError:pass
        else:raise AssertionError("Bad preoutcome cohort accepted")
    print("PASS frozen 64-seed two-task register, no overlap or hidden fallback")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=tuple(BASES),required=False)
    ap.add_argument("--chunk",type=int,required=False)
    ap.add_argument("--out",type=Path,default=Path("compound_new64_artifacts"))
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    self_test()
    if args.self_test:
        return
    task=args.task or os.getenv("ABI_TASK")
    chunk=args.chunk if args.chunk is not None else int(os.getenv("ABI_CHUNK","-1"))
    seeds=validated(task,chunk)
    hashes=verify_source()
    os.environ["ABI_TASK"]=task
    sys.path.insert(0,str(Path.cwd()/"research"))
    method=importlib.import_module("frozen_ppo_compound_ack_multi_belief")
    if (method.TASK!=task or method.FAULT_STEPS!=(2,3)
        or method.POS_BUDGET!=.05 or method.ROT_BUDGET!=.05
        or method.HORIZON!=50 or tuple(method.NAMES)!=ARMS):
        raise ValueError("Changed frozen native controller code or intervention")
    method.SEEDS=seeds
    method.COHORT[task]=(method.TASK_NAME,seeds)
    method.PROTO=PROTO
    args.out.mkdir(parents=True,exist_ok=True)
    # Actually launches all seven genuine PhysX worlds in all original seeds.
    method.main()
    source=Path(f"compound_multi_ack_{task}_original8.json")
    if not source.is_file():
        raise RuntimeError("Missing original PhysX source output; do not fabricate data")
    original=source.read_bytes()
    r=json.loads(original)
    summary=validate_result(r,task,chunk,seeds)
    target=args.out/f"compound_new64_{task}_chunk{chunk}_original8.json"
    target.write_bytes(original)
    summary.update({
        "original_json_sha256":hashlib.sha256(original).hexdigest(),
        "source_blobs":hashes,"original_released_checkpoint_sha256":CHECKPOINT_SHA[task],
        "protocol":PROTO,
        "single_panda_controller_family_only":True,
        "actual_network_packet_loss":False,
        "real_hardware_safety_certified":False,
        "outside_lab_replication":False,
    })
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("PROSPECTIVE_NEW64_8_NATIVE_PHYSX_SHARD",json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    main()
