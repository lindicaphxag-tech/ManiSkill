"""Prospective SEED-DISJOINT replication of existing frozen mixed t2-ACK PhysX.

No method refit or fault schedule change. The previous 64 reset identities
overlapped earlier SE3 research; these 64 original resets do not.
The second t3 ACK remains physically HELD: NOT a 2x2 ACK study.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
import subprocess
from pathlib import Path

PROTOCOL="research/DISJOINT_MIXED_T2_PPO64_PREOUTCOME_V1.json"
PRECOMMITTED_BLOB="68443c6a0913f4b6a988e3a0cda74a650c86273f"
FROZEN_RUNNER_BLOB="36e672446407435e656cbf8aba6fa2de7c1e9d0e"
FROZEN_CLASSIFIER_BLOB="064bb46831b61af73ad445bc836326837ec5468f"
START={"pull_cube":1180001,"stack_cube":1190001}
TASK={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}

def blob(path):
    return subprocess.check_output(["git","hash-object",path],text=True).strip()

def assert_sources():
    for path,expected in (
        (PROTOCOL,PRECOMMITTED_BLOB),
        ("research/frozen_ppo_mixed_ack_truth_physx.py",FROZEN_RUNNER_BLOB),
        ("research/empirical_probe_response_classifier.py",FROZEN_CLASSIFIER_BLOB),
        ("research/frozen_ppo_compound_ack_multi_belief.py","ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"),
    ):
        if blob(path)!=expected:
            raise RuntimeError("FROZEN SOURCE OR PRECOMMITTED PROTOCOL CHANGED: "+path)
    p=json.loads(Path(PROTOCOL).read_text())
    if p["n_states"]!=64 or p["seed_populations"]["pull_cube"]!={"start":1180001,"end":1180032} or p["seed_populations"]["stack_cube"]!={"start":1190001,"end":1190032}:
        raise RuntimeError("New disjoint reset identity registration changed")

def select(task,chunk):
    if task not in START or type(chunk) is not int or chunk not in range(4):
        raise ValueError("Exactly four eight-state original shards per task")
    start=START[task]+8*chunk
    return list(range(start,start+8))

def validate(record,task,chunk):
    from research import run_mixed_ack_truth_new64 as reference
    reference.PREREG=PROTOCOL
    seeds=select(task,chunk)
    result=reference.validate_result(record,task,seeds)
    if result["public"]["t2_applied"]!=4 or result["public"]["t2_held"]!=4:
        raise ValueError("Unbalanced actually executed ACK truths in physical shard")
    if result["public"]["complete_fault_exposure"]!=8:
        raise ValueError("Not all original source tasks exposed both injections")
    for row in result["sample_rows"]:
        if row["seed"] < 1000000:
            raise ValueError("Reused previous exposure identity")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=tuple(START),required=True)
    ap.add_argument("--chunk",type=int,choices=range(4),required=True)
    args=ap.parse_args()
    assert_sources()
    seeds=select(args.task,args.chunk)
    # The immutable genuine PhysX source implementation is NOT modified:
    # only frozen NEW seed identities and source record provenance change.
    os.environ["ABI_TASK"]=args.task
    m=importlib.import_module("research.frozen_ppo_mixed_ack_truth_physx")
    assert m.FAULT_STEPS==(2,3) and m.HORIZON==50
    assert m.PUBLIC_ARM=="fault_public_t3_fourhistory_or_t4_query"
    assert len(m.NAMES)==9
    m.SEEDS=seeds
    m.COHORT[args.task]=(TASK[args.task],seeds)
    m.PROTO=PROTOCOL
    m.main()
    rawpath=Path(f"mixed_ack_{args.task}_original8.json")
    original=rawpath.read_bytes()
    record=json.loads(original)
    summary=validate(record,args.task,args.chunk)
    summary.update(schema="disjoint_mixed_ack_new64_shard_audit_v1",
                   frozen_protocol_blob=PRECOMMITTED_BLOB,
                   exact_original_physical_source_sha256=hashlib.sha256(original).hexdigest(),
                   original_physical_runner_blob=FROZEN_RUNNER_BLOB)
    rawpath.rename(f"disjoint_mixed_{args.task}_chunk{args.chunk}_original8.json")
    Path(f"disjoint_mixed_{args.task}_chunk{args.chunk}_audit.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("DISJOINT_ACTUAL_PHYSX_PPO_SHARD",json.dumps({
        "task":args.task,"chunk":args.chunk,"seeds":seeds,
        "public":summary["controls"]["fault_public_t3_fourhistory_or_t4_query"],
        "task_gated":summary["controls"]["fault_robust_then_single_privileged_query" if args.task=="pull_cube" else "fault_always_single_privileged_query"],
        "true_faults":summary["public"],
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
