"""True native PhysX one seed x FOUR executed ACK truth conditions with matched query-time motor compiler.

The original source model/physical method is frozen. This wrapper changes
only the actual ACK intervention truth at t2/t3 and preserves original
preintervention numeric physical initial state for same-seed causal auditing.
Never call this source a new VLA, network-loss, or independent external study.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, math, os, random, subprocess, sys
from pathlib import Path
import numpy as np
import torch
from huggingface_hub import hf_hub_download

PROTOCOL="research/SAME_COMPILER_CROSSED_4ACK_FRESH32_PREOUTCOME_V1.json"
SOURCE="research/frozen_ppo_samecompiler_crossed_four_truth_physx.py"
TASKS={"pull_cube":("PullCube-v1",3710001),"stack_cube":("StackCube-v1",3720001)}
CHECKPOINTS={
    "pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
    "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_always_single_privileged_query"
TRUTHS={0:("held","held"),1:("applied","held"),2:("held","applied"),3:("applied","applied")}

def git_blob(path):
    return subprocess.check_output(["git","hash-object",path],text=True).strip()

def check_preoutcome(task:str,chunk:int):
    protocol=json.loads(Path(PROTOCOL).read_bytes())
    if (protocol.get("schema")!="fresh32_same_source_seed_crossed_4_true_ACK_matched_motor_compiler_preoutcome_v1"
        or protocol.get("status")!="PRE_OUTCOME_FROZEN_RESEARCH_PROTOCOL"
        or protocol["population"]["source_seed_clusters"]!=32
        or protocol["population"]["physical_truth_cells"]!=128
        or protocol["population"]["total_true_native_PhysX_worlds"]!=1152
        or task not in TASKS or type(chunk) is not int or chunk not in range(4)):
        raise RuntimeError("PREOUTCOME_32_SEED_FULL_FACTORIAL_REGISTRY_DRIFT")
    name,start=TASKS[task]
    d=protocol["population"][task]
    if d["start"]!=start or d["end"]!=start+15 or d["shards"]!=[start+4*i for i in range(4)]:
        raise RuntimeError("Registered fresh truth cell selection differs")
    if (protocol["physical_contract"]["initial_obs_max_abs"]!=5e-5
        or protocol["physical_contract"]["matched_two_actual_fault_command_vectors_max_abs"]!=5e-5):
        raise RuntimeError("Numeric physical prefix threshold retuned")
    # Source PPC model identity is verified against exact third-party SHA256
    # in run(), BEFORE any native physical world is stepped.
    return list(range(start+4*chunk,start+4*chunk+4))

def trial_complete(policy,module,task,seed,truth):
    # Reset the identical physical source distribution BEFORE independently
    # executing a different true ACK pattern. Do not infer the truth from seed.
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    os.environ["ACK_TRUTH_INDEX"]=str(truth)
    r=module.trial(policy,int(seed))
    if (r["seed"]!=seed or r["physical_truth_index_forced_AUDIT_ONLY"]!=truth
        or (r["original_precommitted_physical_t2_execution_truth"],
            r["original_precommitted_physical_t3_execution_truth"])!=TRUTHS[truth]):
        raise RuntimeError("TRUTH_INTERVENTION_SOURCE_INVALID")
    return r

def report_partial(path,rows,task,ids,sha,complete,exception=None):
    obj={
      "schema":"full_4_true_ack_same_source_seed_shared_compiler_physx_v1",
      "real_physx_simulator":True,
      "source_method":"previous proven matched-prefix shared-compiler frozen PPO with new audit-only forced physical ACK truth and initial numeric state",
      "preoutcome_protocol":PROTOCOL,
      "task":TASKS[task][0],
      "original_reset_seed_population":ids,
      "frozen_model_retrained":False,
      "original_external_frozen_checkpoint_sha256":sha,
      "nine_original_physically_stepped_controller_worlds_per_registered_cell":9,
      "full_shard_expected_physical_worlds":144,
      "registered_truths":[TRUTHS[k] for k in range(4)],
      "physically_completed_trial_count":len(rows),
      "complete":bool(complete),
      "original_episode_fail_closed_error":exception,
      "episodes":rows
    }
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    return obj

def run(task,chunk):
    ids=check_preoutcome(task,chunk)
    os.environ["ABI_TASK"]=task
    os.environ["ACK_TRUTH_INDEX"]="0"
    sys.path.insert(0,str(Path.cwd()/"research"))
    m=importlib.import_module("frozen_ppo_samecompiler_crossed_four_truth_physx")
    if (m.TASK!=task or m.PROTO!=PROTOCOL or
        m.TASK_NAME!=TASKS[task][0] or len(m.NAMES)!=9 or
        m.PUBLIC_ARM!=A or m.FAULT_STEPS!=(2,3)):
        raise RuntimeError("Frozen native method changed")
    source_task,model_path,sha,_=m.base.TASKS[task]
    if source_task!=TASKS[task][0] or sha!=CHECKPOINTS[task]:
        raise RuntimeError("Frozen third-party policy source drift")
    model=Path(hf_hub_download(
      repo_id=m.base.REPO,filename=model_path,
      revision=m.base.PUBLISHED_MODEL_REVISION))
    digest=hashlib.sha256(model.read_bytes()).hexdigest()
    if digest!=sha:
        raise RuntimeError("FROZEN_RELEASED_PPO_CHECKPOINT_SHA256_CHANGED")
    w=m.base.env("pd_ee_delta_pose")
    try:
        obs,_=w.reset(seed=ids[0])
        m.base.POLICY_OBS_DIM=int(obs.shape[-1])
        policy=m.base._actor(
            torch.load(model,map_location="cpu",weights_only=True),
            m.base.POLICY_OBS_DIM,7)
    finally:
        w.close()
    file=Path(f"samecompiler_crossed_{task}_chunk{chunk}_original16.json")
    rows=[]
    try:
        for seed in ids:
            group=[]
            for truth in range(4):
                result=trial_complete(policy,m,task,seed,truth)
                rows.append(result)
                group.append(result)
                # Immediately byte-preserve each actual completed physical
                # task/truth condition even if later physics throws.
                report_partial(file,rows,task,ids,digest,complete=False)
            num=np.asarray([r["initial_source_public_observation_f32"] for r in group],dtype=np.float64)
            pose=np.asarray([r["initial_source_ee_pose7_xyz_xyzw"] for r in group],dtype=np.float64)
            if num.ndim!=2 or num.shape[0]!=4 or pose.shape!=(4,7) or not np.isfinite(num).all() or not np.isfinite(pose).all():
                raise RuntimeError("NONFINITE_OR_MISSING_REGISTERED_INITIAL_PHYSICS")
            public_err=float(np.max(np.abs(num-num[0])))
            pose_err=float(np.max(np.abs(pose-pose[0])))
            if public_err>5e-5 or pose_err>5e-5:
                raise RuntimeError(
                    f"WITHIN_SEED_FOUR_TRUTH_NUMERIC_RESET_NOT_PAIRED seed={seed} public={public_err} achieved={pose_err}")
        if len(rows)!=16 or {r["seed"] for r in rows}!=set(ids):
            raise RuntimeError("NOT_FULL_PHYSICALLY_STEPPED_FOUR_ACK_TRUTHS")
        record=report_partial(file,rows,task,ids,digest,complete=True)
        assert record["physically_completed_trial_count"]==16
        print("REAL_MATCHED_SAMECOMPILER_FULL_4TRUTH_SHARD",json.dumps({
          "task":task,"chunk":chunk,"four_physically_executed_truths_per_seed":True,
          "actual_native_worlds":144,"source_seed_clusters":4,
          "public_success":sum(x["success_once"][A] for x in rows),
          "fixed_success":sum(x["success_once"][B] for x in rows),
          "public_reads":sum(x["privileged_target_readback_decision_count"][A] for x in rows),
          "fixed_reads":sum(x["privileged_target_readback_decision_count"][B] for x in rows),
        },sort_keys=True))
    except BaseException as exc:
        report_partial(file,rows,task,ids,digest,complete=False,
                       exception={"class":type(exc).__name__,"message":str(exc)})
        raise

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=tuple(TASKS),required=True)
    ap.add_argument("--chunk",type=int,choices=range(4),required=True)
    args=ap.parse_args()
    run(args.task,args.chunk)
