"""DEVELOPMENT-only matched ZERO vs simulator-internal native re-anchor PhysX pilot.

Genuinely executes original frozen PPO and each ACK truth per seed, both
original ZERO and proposed privileged-write target re-anchor, not replayed labels.
The attempted native setter is not a deployable robot command; count it.
No task-success number can be claimed from this script before CI audit.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,random,sys
from pathlib import Path

PRE="research/NATIVE_REANCHOR_DEV_PREOUTCOME_20261010.json"
REFERENCE_BLOB="2f2fc34f492bf6d2810b48193283e0347f6bdc93"
NATIVE_REANCHOR="fault_reanchor_public_achieved_target"
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
C="fault_always_single_privileged_query"
TASKS={"pull_cube":("PullCube-v1",tuple(range(4300001,4300005))),
       "stack_cube":("StackCube-v1",tuple(range(4400001,4400005)))}
ACK_TRUTHS=tuple(range(4))

def get_protocol():
    obj=json.loads(Path(PRE).read_text())
    if (obj.get("schema")!="native_target_reanchor_development_pilot_v1"
        or obj["independent_reset_clusters"]!=8
        or obj["paired_physical_ACK_contexts"]!=32
        or obj["base_runner_source_blob"]!=REFERENCE_BLOB
        or obj["four_physical_ack_truths"]!=list(ACK_TRUTHS)):
        raise RuntimeError("Prior registered pilot specification changed")
    for task,(env,seeds) in TASKS.items():
        info=obj["tasks"][task]
        if info["env"]!=env or tuple(info["reset_ids"])!=seeds:
            raise RuntimeError("Pilot environment/reset population drift")
    return obj

def trial_pair(task,seed,truth,policy,source,modified):
    import numpy as np,torch
    os.environ["ABI_TASK"]=task
    os.environ["ABI_TRUTH_INDEX"]=str(truth)
    random.seed(seed);np.random.seed(seed%(2**32));torch.manual_seed(seed)
    zero=source.trial(policy,seed)
    random.seed(seed);np.random.seed(seed%(2**32));torch.manual_seed(seed)
    proposal=modified.trial(policy,seed)
    for name,row in (("ZERO",zero),("REANCHOR",proposal)):
        if row["task"]!=TASKS[task][0] or row["seed"]!=seed:
            raise RuntimeError("Wrong frozen PPO environment or seed")
        if ((row["original_precommitted_physical_t2_execution_truth"]=="applied")!=(truth in(1,3))
           or (row["original_precommitted_physical_t3_execution_truth"]=="applied")!=(truth in(2,3))):
            raise RuntimeError("Different actual native ACK truth under comparator")
    if zero["initial_source_physical_obs_sha256"]!=proposal["initial_source_physical_obs_sha256"]:
        raise RuntimeError("Source policy differed at before-fault task state")
    rec=proposal.get("public_pose_reanchor_audit",{}).get(NATIVE_REANCHOR)
    if not rec or rec.get("native_controller_set_state_target_write") is not True:
        raise RuntimeError("Actual controller native target write was not completed")
    if (proposal.get("privileged_internal_target_write_count",{}).get(NATIVE_REANCHOR)!=1
        or proposal["privileged_target_readback_decision_count"][NATIVE_REANCHOR]!=0
        or proposal["public_motion_observation_cost_samples"][NATIVE_REANCHOR]!=1):
        raise RuntimeError("Unregistered privileged write, getter or public observation count")
    zfault=zero["faults"][A]
    rfault=proposal["faults"][NATIVE_REANCHOR]
    if len(zfault)!=2 or len(rfault)!=2:
        raise RuntimeError("Must physically reach both injected ACK faults")
    prefix=[]
    for z,r in zip(zfault,rfault):
        if z["step"]!=r["step"] or z["step"] not in (2,3):
            raise RuntimeError("Wrong fault timing")
        if z["actual_native_action_is_precommitted_applied"] != r["actual_native_action_is_precommitted_applied"]:
            raise RuntimeError("Fault delivery truth differs")
        diff=max(abs(float(a)-float(b)) for a,b in zip(
            z["actual_native_6d_dispatched"],r["actual_native_6d_dispatched"]))
        prefix.append(diff)
        if diff>1e-6:raise RuntimeError("Publicly dispatched controller action differs before intervention")
    origin=zero["public_t3_evidence"]
    before=rec["public_achieved_position_before_write_m"]
    if "before_xyz" not in origin or len(before)!=3:
        raise RuntimeError("Missing real pre-intervention achieved public pose")
    max_pre_action_obs_error=max(abs(float(a)-float(b)) for a,b in zip(
         before,origin["before_xyz"]))
    if max_pre_action_obs_error>5e-5:
        raise RuntimeError("Pre-intervention physical achieved state differs, cannot claim paired effect")
    zr=zero["shared_neutral_probe_step4"][A]["native_six_dim_arm"]
    rr=proposal["shared_neutral_probe_step4"][NATIVE_REANCHOR]["native_six_dim_arm"]
    if any(abs(float(a))>1e-6 for a in zr+rr):
        raise RuntimeError("t4 changed physical robot motion control request, NOT a ZERO probe")
    if (rec["target_write_audit_inf_m"]>1e-5 or rec["target_write_audit_rot_rad"]>1e-5):
        raise RuntimeError("Internal write did not provably reset target to publicly reached EE pose")
    return {
        "task":task,"seed":seed,"actual_ack_truth":truth,
        "source_reset_initial_sha":zero["initial_source_physical_obs_sha256"],
        "pre_t4_native_action_prefix_max_abs":max(prefix),
        "pre_t4_public_ee_xyz_max_abs_m":max_pre_action_obs_error,
        "source_baseline_zero_success":bool(zero["success_once"][A]),
        "source_baseline_matched_public_success":bool(zero["success_once"][B]),
        "source_baseline_privileged_getter_success":bool(zero["success_once"][C]),
        "proposed_reanchor_success":bool(proposal["success_once"][NATIVE_REANCHOR]),
        "privileged_getter_comparator_count":zero["privileged_target_readback_decision_count"][C],
        "privileged_internal_write_count":proposal["privileged_internal_target_write_count"][NATIVE_REANCHOR],
        "proposed_decision_getter_count":proposal["privileged_target_readback_decision_count"][NATIVE_REANCHOR],
        "proposed_public_achieved_pose_read_count":proposal["public_motion_observation_cost_samples"][NATIVE_REANCHOR],
        "target_memory_write_audit":rec,
        "baseline_ZERO_authority_wrong":bool(zero["public_t3_evidence"].get("wrong_confident",False)),
        "reanchor_no_confident_unknown_state_authorization":True,
        "source_original_full_runner_worlds":len(source.NAMES),
        "proposed_full_runner_worlds":len(modified.NAMES),
        "all_actual_PhysX_steps_completed":True
    }

def run(task):
    obj=get_protocol()
    if task not in TASKS:raise ValueError("Unregistered task")
    import numpy as np,torch
    from huggingface_hub import hf_hub_download
    sys.path.insert(0,str(Path.cwd()/"research"))
    os.environ["ABI_TASK"]=task
    source=importlib.import_module("research.frozen_ppo_matched_public_factorial128_physx")
    modified=importlib.import_module("research.frozen_ppo_native_reanchor_dev_physx")
    import frozen_ppo_action_history_observer as base
    if (source.PUBLIC_ARM!=A or modified.PUBLIC_ARM!=A
        or modified.REANCHOR!=NATIVE_REANCHOR or len(modified.NAMES)!=len(source.NAMES)+1
        or source.HORIZON!=modified.HORIZON or modified.HORIZON!=50):
        raise RuntimeError("Actual frozen controller comparator contract changed")
    env_name,path,sha,_=base.TASKS[task]
    if env_name!=TASKS[task][0]:raise RuntimeError("Wrong frozen source environment")
    checkpoint=Path(hf_hub_download(repo_id=base.REPO,filename=path,revision=base.PUBLISHED_MODEL_REVISION))
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest()!=sha:
        raise RuntimeError("Actual frozen third-party PPO weights changed")
    env=base.env("pd_ee_delta_pose")
    try:
        obs,_=env.reset(seed=TASKS[task][1][0])
        base.POLICY_OBS_DIM=int(obs.shape[-1])
        policy=base._actor(torch.load(checkpoint,map_location="cpu",weights_only=True),base.POLICY_OBS_DIM,7)
    finally:
        env.close()
    rows=[]
    for truth in ACK_TRUTHS:
        for seed in TASKS[task][1]:
            row=trial_pair(task,seed,truth,policy,source,modified)
            rows.append(row)
            print("NATIVE_REANCHOR_PHYSX_DEVELOPMENT_TASK_RESULT",json.dumps(row,sort_keys=True),flush=True)
    record=dict(schema="native_reanchor_development_frozen_ppo_physical_v1",task=task,
        first_run_source_commit=os.environ.get("GITHUB_SHA","locally-executed-without-ci-sha"),
        registered_development_protocol=PRE,
        registered_old_original_source_blob=REFERENCE_BLOB,
        actual_independent_reset_clusters=4,
        actual_correlated_ACK_task_pairs=16,
        actually_physical_native_controller_worlds=16*(len(source.NAMES)+len(modified.NAMES)),
        source_weight_sha256=sha,
        no_PPO_training=True,not_hardware_verified=True,
        cost_model_privileged_target_write_one=True,
        source_original_method="fully physically executed zero",
        proposed_method="fully physically executed simulator-internal reanchor plus ZERO t4",
        rows=rows)
    out=Path(f"native_reanchor_{task}_original.json")
    out.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("NATIVE_REANCHOR_DEVELOPMENT_COMPLETE",json.dumps({
        "task":task,"independent_resets":4,"paired_task_conditions":16,
        "real_native_PhysX_worlds":record["actually_physical_native_controller_worlds"],
        "zero_success":sum(r["source_baseline_zero_success"] for r in rows),
        "getter_success":sum(r["source_baseline_privileged_getter_success"] for r in rows),
        "reanchor_success":sum(r["proposed_reanchor_success"] for r in rows)},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS))
    p.add_argument("--mode",choices=("preflight","run"),default="preflight")
    args=p.parse_args()
    if args.mode=="preflight":print(json.dumps(get_protocol(),indent=2))
    else:
        if not args.task:p.error("Explicit named task required")
        run(args.task)
