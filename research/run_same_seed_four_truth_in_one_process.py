"""Source-replay same-PPO-reset factorial: four actual truths in one Python process.

AMENDED post-failure design. Do not describe as first prospective result.
Never change original frozen physical algorithm or delete failed episodes.
Exact identical initial source-policy observation SHA256 is mandatory.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,random,subprocess,sys
from pathlib import Path

PREREG="research/PAIRED_COUNTERFACTUAL_2X2_PPO128_PREOUTCOME_V1.json"
AMENDMENT="research/PAIRED_ACK_SINGLE_PROCESS_RESET_REPAIR_DISCLOSURE.json"
ORIGINAL_SOURCE="research/frozen_ppo_same_reset_factorial_physx.py"
SOURCE_FROZEN_BLOB="14882a4efcd36351f8cb5873e706488788446f32"
OLD_PHYSICS_SOURCE_BLOB="36e672446407435e656cbf8aba6fa2de7c1e9d0e"
MOTION_RESPONSE_BLOB="064bb46831b61af73ad445bc836326837ec5468f"

def hash_file(path):
    return subprocess.check_output(("git","hash-object",path),text=True).strip()

def audit_source_freeze():
    from research.run_same_reset_ack_factorial import assert_preoutcome,SOURCE,OLD_SOURCE,CLASSIFIER
    assert_preoutcome()
    got=hash_file(ORIGINAL_SOURCE)
    if got!=SOURCE_FROZEN_BLOB or SOURCE!=ORIGINAL_SOURCE:
        raise RuntimeError("Original physical runner source was changed: "+got)
    if hash_file(OLD_SOURCE)!=OLD_PHYSICS_SOURCE_BLOB or hash_file(CLASSIFIER)!=MOTION_RESPONSE_BLOB:
        raise RuntimeError("Changed previous true PhysX or trained response tolerance source")
    p=json.loads(Path(AMENDMENT).read_text())
    if p["schema"]!="amended_physics_same_seed_same_process_common_rng_four_truth_v1":
        raise RuntimeError("Unregistered post-failure amendment")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=("pull_cube","stack_cube"),required=True)
    ap.add_argument("--chunk",type=int,choices=(0,1),required=True)
    args=ap.parse_args()
    audit_source_freeze()
    os.environ["ABI_TASK"]=args.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    import numpy as np
    import torch
    from research.run_same_reset_ack_factorial import (
        select,TASKS,PREREG,SOURCE,CLASSIFIER,validate,blob)
    m=importlib.import_module("frozen_ppo_same_reset_factorial_physx")
    source_trial=m.trial
    source_seeds=select(args.task,args.chunk)
    if tuple(m.FAULT_STEPS)!=(2,3) or len(m.NAMES)!=9 or m.PROTO!=PREREG:
        raise RuntimeError("Source physics fault scheduling changed")
    m.SEEDS=source_seeds
    m.COHORT[args.task]=(TASKS[args.task],source_seeds)
    def common_random_numbers_trial(policy,seed):
        # Every actual truth is physically re-stepped from the exact same
        # source seed, not an observed log replay or fabricated counterfactual.
        random.seed(seed)
        np.random.seed(seed % (2**32))
        torch.manual_seed(seed)
        return source_trial(policy,seed)
    m.trial=common_random_numbers_trial

    pair={}
    all_original=[]
    for truth_index in range(4):
        os.environ["ABI_TRUTH_INDEX"]=str(truth_index)
        m.main()
        raw_path=Path(f"mixed_ack_{args.task}_original8.json")
        raw=raw_path.read_bytes()
        original=json.loads(raw)
        original_seeds=[r["seed"] for r in original["episodes"]]
        if original_seeds!=source_seeds:
            raise RuntimeError("Source episode omitted or reordered")
        summary=validate(original,args.task,args.chunk,truth_index)
        summary.update(
            schema="same_reset_factorial_true_2x2_shard_audit_v1",
            physical_original_sha256=hashlib.sha256(raw).hexdigest(),
            prereg_git_blob=blob(PREREG),
            new_runner_git_blob=blob(SOURCE),
            unchanged_response_model_git_blob=blob(CLASSIFIER)
        )
        prefix=f"factorial_{args.task}_chunk{args.chunk}_truth{truth_index}"
        raw_path.rename(prefix+"_original8.json")
        Path(prefix+"_audit.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
        all_original.append((prefix,hashlib.sha256(raw).hexdigest()))
        for row in original["episodes"]:
            pair.setdefault(row["seed"],{})[truth_index]=row["initial_source_physical_obs_sha256"]
        print("SAME_PROCESS_ACTUAL_PHYSX_FACTORED_SHARD",json.dumps({
            "task":args.task,"chunk":args.chunk,"truth":truth_index,
            "original_task_reset_seeds":original_seeds,
            "public_success":summary["outcomes"][m.NAMES[-1]]["success"],
            "source_sha256":hashlib.sha256(raw).hexdigest()
        },sort_keys=True),flush=True)
    mismatched={str(seed):hashes for seed,hashes in pair.items()
                if len(hashes)!=4 or len(set(hashes.values()))!=1}
    report={
        "schema":"same_source_seed_amended_one_process_four_real_physx_truths",
        "original_failed_first_trial_reference":"37930607707",
        "not_original_prospective_first_success":True,
        "task":args.task,"chunk":args.chunk,
        "full_source_reset_seeds":source_seeds,
        "original_physx_shard_sha256":all_original,
        "four_actual_PHYSX_truth_conditions_per_seed":True,
        "all_four_identical_original_initial_source_hashes":not mismatched,
        "same_seed_hashes":{str(seed):pair[seed] for seed in source_seeds},
        "initial_hash_mismatches":mismatched,
        "never_drop_or_rename_failed_source_reset":True
    }
    Path(f"sameprocess_{args.task}_chunk{args.chunk}_true4_hash_provenance.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("SAME_PROCESS_FULL_TRUTH_PHYSX_INITIAL_HASH_VALIDATION",json.dumps({
        "task":args.task,"chunk":args.chunk,
        "same_seed_initial_hash_mismatches":mismatched,
        "all_identical":not mismatched},sort_keys=True),flush=True)
    if mismatched:
        raise RuntimeError("Actual initially physical source poses still mismatch; do NOT promote causal matched factorial results.")

if __name__=="__main__":
    main()
