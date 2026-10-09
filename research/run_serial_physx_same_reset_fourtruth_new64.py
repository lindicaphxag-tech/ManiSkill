"""Genuine new PhysX experiment: FOUR ACK truths serially under ONE task process.

No editing original policy/method code. Eight NEW seeds per task, each run under
all four actual applied/held execution combinations. Original native method
simulation is called directly, and the global RNG is reset to a registered
value before each independent truth condition. All outcomes, exact pre-fault
PPO observation bytes SHA, refusals and faults must pass the original per-shard
physical auditor; cross-truth hash mismatch refuses paired causal claims.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
import random
import sys
from pathlib import Path
import numpy as np
import torch

import research.run_same_reset_ack_factorial as frozen_original_audit

PROTO="research/SERIAL_SAME_PROCESS_FOUR_ACK_NEW64_PREOUTCOME_V1.json"
SHA_OLD_NATIVE="14882a4efcd36351f8cb5873e706488788446f32"
SHA_OLD_RESP="064bb46831b61af73ad445bc836326837ec5468f"
TASK_SEEDS={"pull_cube":1970001,"stack_cube":1980001}
N=8

def source_blob(path):
    import subprocess
    return subprocess.check_output(["git","hash-object",path],text=True).strip()

def run(task,outdir):
    protocol=json.loads(Path(PROTO).read_text())
    if protocol["schema"]!="prospective_serial_single_process_matched_four_true_ack_new16clusters_v1":
        raise ValueError("No prospectively registered native source")
    if source_blob("research/frozen_ppo_same_reset_factorial_physx.py")!=SHA_OLD_NATIVE:
        raise ValueError("Previously tested native physical method changed")
    if source_blob("research/empirical_probe_response_classifier.py")!=SHA_OLD_RESP:
        raise ValueError("Previously calibrated empirical model changed")
    if task not in TASK_SEEDS:
        raise ValueError("Unknown frozen task")
    start=TASK_SEEDS[task]
    expected=list(range(start,start+N))
    if (protocol["task_seeds"][task]["start"]!=start or
        protocol["task_seeds"][task]["end"]!=start+N-1):
        raise ValueError("Changed frozen future reset IDs")
    if protocol["physically_stepped_worlds_if_complete"]!=576:
        raise ValueError("Altered registered physical denominator")

    os.environ["ABI_TASK"]=task
    sys.path.insert(0,str(Path.cwd()/"research"))
    mod=importlib.import_module("frozen_ppo_same_reset_factorial_physx")
    if (mod.TASK!=task or tuple(mod.FAULT_STEPS)!=(2,3) or
        len(mod.NAMES)!=9 or mod.HORIZON!=50):
        raise ValueError("Unrecognized original frozen controller mechanism")
    mod.PROTO=PROTO
    mod.SEEDS=expected
    mod.COHORT[task]=(frozen_original_audit.TASKS[task],expected)
    frozen_original_audit.START[task]=start
    frozen_original_audit.PREREG=PROTO

    outdir.mkdir(parents=True,exist_ok=True)
    rows={}
    audits={}
    for truth in range(4):
        os.environ["ABI_TRUTH_INDEX"]=str(truth)
        random.seed(20261009)
        np.random.seed(20261009)
        torch.manual_seed(20261009)
        mod.main()    # ACTUAL official frozen PPO + 8×9 genuine native PhysX
        generated=Path(f"mixed_ack_{task}_original8.json")
        raw=generated.read_bytes()
        data=json.loads(raw)
        original=outdir/f"serial_{task}_truth{truth}_original8.json"
        generated.replace(original)  # do not change or reserialize physics JSON
        audit=frozen_original_audit.validate(data,task,0,truth)
        audit.update({
            "schema":"prospective_serial_same_process_true2x2_physical_shard_audit_v1",
            "original_native_physics_file_sha256":hashlib.sha256(raw).hexdigest(),
            "new_registered_protocol_git_blob":source_blob(PROTO),
            "previous_unchanged_native_physics_source_git_blob":SHA_OLD_NATIVE,
            "previous_unchanged_empirical_model_git_blob":SHA_OLD_RESP,
            "genuinely_one_task_python_process_for_four_conditions":True,
            "global_rng_reseed_before_truth":20261009,
        })
        (outdir/f"serial_{task}_truth{truth}_audit.json").write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
        rows[truth]=audit["rows"]
        audits[truth]=audit
        print("AUTHENTIC_ORIGINAL_NATIVE_SERIAL_ACK_PHYSX_TRUTH",json.dumps({
             "task":task,"truth":truth,
             "native_worlds":8*9,
             "actual_controller_fault_exposure":audit["public_both_faults_exposed"],
             "task_success_public":audit["outcomes"][frozen_original_audit.PUBLIC]["success"],
             "task_success_strong":audit["outcomes"][frozen_original_audit.STRONG[task]]["success"],
             "private_read_public":audit["outcomes"][frozen_original_audit.PUBLIC]["reads"],
             "private_read_strong":audit["outcomes"][frozen_original_audit.STRONG[task]]["reads"],
        },sort_keys=True),flush=True)

    if len(rows)!=4 or any(len(x)!=8 for x in rows.values()):
        raise ValueError("Missing original four true fault physical worlds")
    matching=[];mismatch=[]
    for n,seed in enumerate(expected):
        hashes=[rows[t][n]["initial_source_physical_obs_sha256"] for t in range(4)]
        entry={"task":task,"seed":seed,"four_input_sha256":hashes}
        if len(set(hashes))==1: matching.append(entry)
        else: mismatch.append(entry)
    result={
        "schema":"prospective_true2x2_PHYSICALLY_STEPPED_SERIAL_SAME_PROCESS_TASK_SHARD_v1",
        "task":task,"source_seed_count":N,
        "physical_truth_conditions":4,
        "native_PhysX_worlds":4*N*9,
        "all_task_initial_input_hash_match":len(mismatch)==0,
        "input_matched_original_reset_clusters":len(matching),
        "original_input_sha_mismatch_clusters":mismatch,
        "exact_matched_input_seed_details":matching,
        "by_truth":{str(t):{
             "public_success":audits[t]["outcomes"][frozen_original_audit.PUBLIC]["success"],
             "strong_success":audits[t]["outcomes"][frozen_original_audit.STRONG[task]]["success"],
             "public_reads":audits[t]["outcomes"][frozen_original_audit.PUBLIC]["reads"],
             "strong_reads":audits[t]["outcomes"][frozen_original_audit.STRONG[task]]["reads"],
        } for t in range(4)},
        "no_counterfactual_claim_when_input_mismatch":True,
        "not_independent_third_party_reproduction":True,
    }
    (outdir/f"serial_{task}_all_truth_reset_authenticity.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("SERIAL_PHYSX_TRUE_FACTORIAL_RESET_IDENTITY_GATE",json.dumps({
        "task":task,"matched":len(matching),"mismatch":len(mismatch),
        "genuine_worlds":result["native_PhysX_worlds"],
    },sort_keys=True))
    if mismatch:
        raise ValueError("REAL PHYSX SOURCE INITIAL POLICY INPUT SHA MISMATCH: task "+task+
                         " refuses full matched-factorial causal comparison")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",required=True,choices=tuple(TASK_SEEDS))
    p.add_argument("--output-dir",required=True,type=Path)
    args=p.parse_args()
    run(args.task,args.output_dir)

if __name__=="__main__":main()
