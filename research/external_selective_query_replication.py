"""External fork owner-controlled replication of the ORIGINAL seven-arm robust/query method.

This is NOT a new algorithm, not independent lab results by itself, and not
a physical robotic packet-loss experiment. It executes unchanged
research/frozen_ppo_ack_bounded_query.py on eight independently chosen seeds.

The original method source, certifier and released PPO checkpoint hashes MUST
match the published 2026-10-09 discovery. No thresholds may be tuned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

SOURCE_METHOD_BLOB="1dc653cdc44e422c8340475ad00f828b3a41eb4f"
CERTIFIER_BLOB="bb5fd155b7291fb127f94138fca321201c8271c3"
SOURCE_METHOD_COMMIT="db4fe4dd9d09aaff67c5dcf12213ad737162282d"
ALLOWED=("pull_cube","stack_cube")
N=8


def validated(task:str, first_seed:int)->tuple[int,...]:
    if task not in ALLOWED:
        raise ValueError("Only released PullCube/StackCube frozen checkpoints supported")
    if not isinstance(first_seed,int) or not (200001<=first_seed<=9999992):
        raise ValueError("Use eight previously unpublished seeds >= 200001")
    return tuple(range(first_seed,first_seed+N))


def assert_blob_hashes(repo:Path)->dict:
    """Git object SHA1, not truncated content hashes, per original freeze."""
    import subprocess
    names={
        "method":"research/frozen_ppo_ack_bounded_query.py",
        "certifier":"research/two_history_se3_robust.py",
    }
    expected={"method":SOURCE_METHOD_BLOB,"certifier":CERTIFIER_BLOB}
    actual={}
    for key,path in names.items():
        out=subprocess.check_output(
            ["git","hash-object",path],cwd=repo,text=True).strip()
        if out!=expected[key]:
            raise RuntimeError(f"Source method/certifier changed: {key}: {out}")
        actual[key]=out
    return actual


def certify_rows(raw:dict, task:str, seed_ids:tuple[int,...])->dict:
    if (raw.get("schema")!="unknown_ack_bounded_or_query_physx_v1"
        or raw.get("task")!=("PullCube-v1" if task=="pull_cube" else "StackCube-v1")
        or raw.get("original_seed_population")!=list(seed_ids)
        or raw.get("frozen_model_retrained") is not False
        or raw.get("real_physx_simulator") is not True
        or raw.get("fault_is_native_target_hold_not_network_loss") is not True):
        raise ValueError("Unexpected original model/trial identity")
    episodes=raw.get("episodes")
    if not isinstance(episodes,list) or len(episodes)!=N:
        raise ValueError("Do not exclude failed episodes; all eight required")
    names=raw.get("all_seven_actual_control_arms")
    if not isinstance(names,list) or len(names)!=7 or len(set(names))!=7:
        raise ValueError("Original seven-arm denominator damaged")
    bounded="fault_robust_then_single_privileged_query"
    fixed="fault_always_single_privileged_query"
    zero="fault_robust_two_history_without_query"
    counts={n:0 for n in names}
    queries={bounded:0,fixed:0}
    for i,r in enumerate(episodes):
        if r.get("seed")!=seed_ids[i]:
            raise ValueError("Duplicate or missing original selected seed")
        if not all(isinstance(r.get("faults",{}).get(n),dict) for n in names if n!="source_no_fault"):
            raise ValueError("Simulated physical hold not reached for one or more arms")
        outcome=r.get("success_once",{})
        if set(outcome)!=set(names) or any(not isinstance(outcome[k],bool) for k in names):
            raise ValueError("Missing native ManiSkill task success outcome")
        q=r.get("privileged_target_readback_decision_count",{})
        if q.get(bounded) not in (0,1) or q.get(fixed)!=1 or q.get(zero)!=0:
            raise ValueError("Authoritative target readback budget violated")
        if q.get("fault_oracle_private_target")!=-1:
            raise ValueError("Oracle private access must never be displayed as zero")
        queries[bounded]+=q[bounded]
        queries[fixed]+=q[fixed]
        for n in names:
            counts[n]+=int(outcome[n])
    if counts!=raw.get("success_counts"):
        raise ValueError("Printed original aggregate conflicts with per-seed records")
    return {
        "task":task,"seeds":list(seed_ids),"official_native_task_success_counts":counts,
        "privileged_decision_readback_counts":queries,
        "all_original_8_failures_retained":True,
        "zero_readback_controller_info_not_equivalent_to_privileged_query":True,
    }


def self_test():
    assert validated("pull_cube",200001)==tuple(range(200001,200009))
    for task,seed in [("wrong",200001),("stack_cube",5),("pull_cube",10000000)]:
        try: validated(task,seed)
        except ValueError: pass
        else: raise AssertionError("Bad selection accepted")
    names=["source_no_fault","fault_oracle_private_target",
           "fault_optimistic_unverified_ack","fault_strict_common_exact",
           "fault_robust_two_history_without_query",
           "fault_robust_then_single_privileged_query",
           "fault_always_single_privileged_query"]
    proto={
        "schema":"unknown_ack_bounded_or_query_physx_v1",
        "task":"PullCube-v1","original_seed_population":list(range(200001,200009)),
        "frozen_model_retrained":False,"real_physx_simulator":True,
        "fault_is_native_target_hold_not_network_loss":True,
        "all_seven_actual_control_arms":names,
    }
    proto["episodes"]=[
        {"seed":i,
         "faults":{n:{"step":2} for n in names if n!="source_no_fault"},
         "success_once":{n:(n!="fault_strict_common_exact") for n in names},
         "privileged_target_readback_decision_count":{
             "fault_robust_then_single_privileged_query":0,
             "fault_always_single_privileged_query":1,
             "fault_robust_two_history_without_query":0,
             "fault_oracle_private_target":-1,
          }}
        for i in range(200001,200009)
    ]
    proto["success_counts"]={n:(0 if n=="fault_strict_common_exact" else 8) for n in names}
    good=certify_rows(proto,"pull_cube",tuple(range(200001,200009)))
    assert good["privileged_decision_readback_counts"]["fault_always_single_privileged_query"]==8
    import copy
    for mutate in [
        lambda x: x["episodes"].pop(),
        lambda x: x["episodes"][2].update(seed=200001),
        lambda x: x["episodes"][0]["faults"].pop("fault_always_single_privileged_query"),
        lambda x: x["episodes"][0]["privileged_target_readback_decision_count"].update(fault_robust_then_single_privileged_query=2),
        lambda x: x["episodes"][0]["success_once"].update(source_no_fault=7),
    ]:
        case=copy.deepcopy(proto)
        mutate(case)
        try:certify_rows(case,"pull_cube",tuple(range(200001,200009)))
        except ValueError:pass
        else:raise AssertionError("Evidence tampering was accepted")
    print("PASS eight fresh seed selection, seven-arm counts and five destructive corruption checks")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--task",choices=ALLOWED,default="pull_cube")
    parser.add_argument("--first-seed",type=int,default=200001)
    parser.add_argument("--output-dir",type=Path,default=Path("external_selective_artifacts"))
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        self_test()
        return
    seed_ids=validated(args.task,args.first_seed)
    root=Path(__file__).resolve().parents[1]
    blobs=assert_blob_hashes(root)
    import os
    os.environ["ABI_TASK"]=args.task
    # Exact published original algorithm imported only AFTER selecting its task
    # because it resolves TASK at module import. No changes to its source file.
    import frozen_ppo_ack_bounded_query as original
    if (original.TASK!=args.task
        or original.POS_BUDGET!=.05
        or original.ROT_BUDGET!=.05
        or original.FAULT_STEP!=2
        or original.HORIZON!=50):
        raise RuntimeError("Unfrozen experimental method parameters")
    assert tuple(original.NAMES)==(
        "source_no_fault","fault_oracle_private_target",
        "fault_optimistic_unverified_ack","fault_strict_common_exact",
        "fault_robust_two_history_without_query",
        "fault_robust_then_single_privileged_query",
        "fault_always_single_privileged_query"
    )
    original.SEEDS=seed_ids
    original.COHORT[args.task]=(original.TASK_NAME,seed_ids)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    original.main() # actually steps native ManiSkill PhysX for ALL selected 8 episodes
    original_json=root/f"unknown_ack_bounded_query_{args.task}_original8.json"
    if not original_json.exists():
        raise RuntimeError("Original method has not emitted an original JSON")
    raw_bytes=original_json.read_bytes()
    record=json.loads(raw_bytes)
    digest=hashlib.sha256(raw_bytes).hexdigest()
    summ=certify_rows(record,args.task,seed_ids)
    target=args.output_dir/f"external_selective_{args.task}_{args.first_seed}_8original.json"
    shutil.copyfile(original_json,target)  # original, byte-identical
    summ.update({
        "original_result_json_sha256":digest,
        "original_algo_commit":SOURCE_METHOD_COMMIT,
        "original_method_git_blobs":blobs,
        "created_by":"current fork workflow actor, must verify fork owner",
        "author_original_ci_not_independent_reproduction":True,
        "actual_network_packet_loss":False,
        "simulated_native_target_hold":True,
        "privileged_memory_reads_unavailable_in_real_robot_without_explicit_interface":True,
        "not_retrained":True,
    })
    (args.output_dir/"result_summary.json").write_text(
        json.dumps(summ,indent=2,sort_keys=True)+"\n")
    print("OUTSIDE_SELECTIVE_QUERY_RESULT",json.dumps(summ,sort_keys=True))


if __name__=="__main__":
    main()
