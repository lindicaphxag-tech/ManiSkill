"""First prospective paired full-task Zero-vs-X native PhysX frozen-PPO run.

This script PHYSICALLY steps each registered world, including ALL faults and all
controller arms, not an offline splice, retrospective model, or replay summary.
Source policy/zero arm is never modified or retrained. Active arm is a source
copy with predeclared t4 X action, mandatory causal post-action belief propagation.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,random,subprocess,sys
from pathlib import Path

PRE="research/ACTIVE_PROBE_TASK_ZERO_X_PREOUTCOME_20261010.json"
SOURCE="research/frozen_ppo_matched_public_factorial128_physx.py"
ACTIVE="research/frozen_ppo_known_x_probe_task_physx.py"
SOURCE_SHA="2f2fc34f492bf6d2810b48193283e0347f6bdc93"
REGISTER={"pull_cube":("PullCube-v1",4100001,"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
          "stack_cube":("StackCube-v1",4200001,"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")}
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
C="fault_always_single_privileged_query"
ARMS=(A,B,C)
PROBES=("zero","x")
TRUTHS=(0,1,2,3)

def git_blob(path):
    return subprocess.check_output(["git","hash-object",path],text=True).strip()

def preflight():
    obj=json.loads(Path(PRE).read_text())
    if obj["schema"]!="active_probe_task_first_preoutcome_v1" or obj["independent_reset_clusters"]!=32 or obj["expected_truth_probe_task_cells"]!=256 or obj["total_expected_actually_stepped_physx_worlds"]!=2560:
        raise RuntimeError("registered cohort denominator drift")
    if git_blob(SOURCE)!=SOURCE_SHA:
        raise RuntimeError("published original matched-action true PhysX controller source changed")
    # Only fixed active action and its new post-action controller-state propagation
    # may differ from the old source; the complete textual transform is reviewed.
    if obj["base_native_ppo_source_blob"]!=SOURCE_SHA or obj["probe_type_order"]!=list(PROBES):
        raise RuntimeError("source identity / registered probe order drift")
    for task,(name,start,model_sha) in REGISTER.items():
        p=obj["tasks"][task]
        if (p["environment"]!=name or p["original_reset_range"]!=[start,start+15]
            or p["published_policy_checkpoint_sha256"]!=model_sha):
            raise RuntimeError("original external PPO or pilot seed range altered")
    return obj

def selected(task,chunk):
    if task not in REGISTER or type(chunk) is not int or chunk not in (0,1,2,3):
        raise ValueError("Only 2 named tasks x 4 registered shards")
    return list(range(REGISTER[task][1]+4*chunk, REGISTER[task][1]+4*(chunk+1)))

def full_task_shard(task,chunk):
    frozen=preflight()
    import numpy as np
    import torch
    from huggingface_hub import hf_hub_download
    sys.path.insert(0,str(Path.cwd()/"research"))
    os.environ["ABI_TASK"]=task
    source=importlib.import_module("research.frozen_ppo_matched_public_factorial128_physx")
    active=importlib.import_module("research.frozen_ppo_known_x_probe_task_physx")
    import frozen_ppo_action_history_observer as base
    if (source.NAMES!=active.NAMES or source.NAMES[6:9]!=(A,B,C)
        or tuple(source.FAULT_STEPS)!=(2,3) or source.HORIZON!=50
        or active.HORIZON!=source.HORIZON
        or source.TASK_NAME!=REGISTER[task][0] or active.TASK_NAME!=source.TASK_NAME):
        raise RuntimeError("different method/control/physical episode families")
    _,path,registered_sha,_=base.TASKS[task]
    if registered_sha!=REGISTER[task][2]:
        raise RuntimeError("source third-party PPO registry changed")
    weights=Path(hf_hub_download(repo_id=base.REPO,filename=path,
                                 revision=base.PUBLISHED_MODEL_REVISION))
    weight_sha=hashlib.sha256(weights.read_bytes()).hexdigest()
    if weight_sha!=registered_sha:
        raise RuntimeError("third-party frozen policy checksum mismatch")
    env=base.env("pd_ee_delta_pose")
    try:
        obs,_=env.reset(seed=selected(task,chunk)[0])
        base.POLICY_OBS_DIM=int(obs.shape[-1])
        policy=base._actor(torch.load(weights,map_location="cpu",weights_only=True),
                           base.POLICY_OBS_DIM,7)
    finally:env.close()

    src_rows={}
    arm_diffs=[]
    for truth in TRUTHS:
        os.environ["ABI_TRUTH_INDEX"]=str(truth)
        for probe,runner in (("zero",source),("x",active)):
            records=[]
            for seed in selected(task,chunk):
                # Original source physical actions and seed identically reinitialized.
                random.seed(seed);np.random.seed(seed%(2**32));torch.manual_seed(seed)
                r=runner.trial(policy,seed)
                if (r["seed"]!=seed or r["task"]!=REGISTER[task][0]
                    or (r["original_precommitted_physical_t2_execution_truth"]=="applied")!=(truth in (1,3))
                    or (r["original_precommitted_physical_t3_execution_truth"]=="applied")!=(truth in (2,3))):
                    raise RuntimeError("wrong physically executed trial/fault truth")
                for arm in ARMS:
                    fault=r["faults"].get(arm,[])
                    t4=r["shared_neutral_probe_step4"].get(arm,{})
                    if ([x["step"] for x in fault]!=[2,3] or t4.get("physically_dispatched") is not True
                        or r["public_motion_observation_cost_samples"].get(arm)!=(0 if arm==C else 2)
                        or type(r["success_once"].get(arm)) is not bool
                        or r["privileged_target_readback_decision_count"].get(arm) not in (0,1)):
                        raise RuntimeError("fault exposure / public sample cost / native task result corrupt")
                    actual=t4["native_six_dim_arm"]
                    if actual!=([.15,0.,0.,0.,0.,0.] if probe=="x" else [0.]*6):
                        raise RuntimeError("known-delivered native t4 physical probe not as registered")
                    pos=t4["audit_only_target_position_delta_m"]
                    if abs(pos-(.015 if probe=="x" else 0))>5e-5 or t4["audit_only_target_orientation_delta_rad"]>1e-4:
                        raise RuntimeError("native controller target did not match probe/action")
                for key in ("matched_prefix_physical_audit","matched_posterior_prefix_audit"):
                    check=r.get(key,{})
                    if check.get("valid_exact_prefix") is not True:
                        raise RuntimeError("Strong A/B/C mismatched prefix before t5")
                    metrics=[*check.get("native_fault_dispatch_linf_each",[])]
                    metrics += [check.get(k,999.) for k in (
                        "pre_t5_achieved_position_max_abs_m",
                        "pre_t5_achieved_orientation_geodesic_rad",
                        "pre_t5_target_position_max_abs_m",
                        "pre_t5_target_orientation_geodesic_rad")]
                    if len(metrics)!=6 or max(metrics)>5e-5:
                        raise RuntimeError("A/B/C actual native prefix diverged before deciding")
                records.append(r)
                src_rows[task,seed,truth,probe]=r
                print("ORIGINAL_FULL_TASK_PHYSX",json.dumps({
                    "task":task,"seed":seed,"fault_truth":truth,"probe":probe,
                    "success":{a:r["success_once"][a] for a in ARMS},
                    "private_reads":{a:r["privileged_target_readback_decision_count"][a] for a in ARMS},
                    "public_xyz_events":{a:r["public_motion_observation_cost_samples"][a] for a in ARMS},
                    "confidence":{a:(r["public_t3_evidence"] if a==A else
                                      r["same_sensor_posterior_evidence"]).get("authorized")
                                  for a in (A,B)},
                    "probe_physically_dispatched":True
                },sort_keys=True),flush=True)
            filename=f"physx_probe_{task}_chunk{chunk}_truth{truth}_{probe}.json"
            content=dict(schema="new_frozen_task_zero_v_x_true_physx_v1",
                task=task,chunk=chunk,fault_truth_index=truth,probe=probe,
                original_source_git_blob=SOURCE_SHA,
                preoutcome_protocol=PRE,
                frozen_original_source_PPO_sha256=registered_sha,
                world_count=len(records)*len(source.NAMES),
                source_original_reset_ids=selected(task,chunk),
                actually_physical_native_arm_probes=True,
                no_policy_retraining=True,episodes=records)
            Path(filename).write_text(json.dumps(content,indent=2,sort_keys=True)+"\n")
        for seed in selected(task,chunk):
            zero=src_rows[task,seed,truth,"zero"]
            x=src_rows[task,seed,truth,"x"]
            if zero["initial_source_physical_obs_sha256"]!=x["initial_source_physical_obs_sha256"]:
                raise RuntimeError("paired world reset different before t4")
            for arm in ARMS:
                zero_faults=zero["faults"][arm]
                x_faults=x["faults"][arm]
                diffs=[max(abs(float(u)-float(v)) for u,v in zip(z["actual_native_6d_dispatched"],
                                                                 a["actual_native_6d_dispatched"]))
                       for z,a in zip(zero_faults,x_faults)]
                if len(diffs)!=2 or max(diffs)>1e-6:
                    raise RuntimeError("same random seed/truth physically DIFFERENT before t4")
                arm_diffs.append(dict(task=task,seed=seed,truth=truth,arm=arm,
                    active_minus_neutral_task_success=int(x["success_once"][arm])-int(zero["success_once"][arm]),
                    zero_success=zero["success_once"][arm],x_success=x["success_once"][arm],
                    zero_reads=zero["privileged_target_readback_decision_count"][arm],
                    x_reads=x["privileged_target_readback_decision_count"][arm],
                    zero_wrong=bool((zero["public_t3_evidence"] if arm==A else
                                     zero["same_sensor_posterior_evidence"]).get("wrong_confident",False)) if arm!=C else False,
                    x_wrong=bool((x["public_t3_evidence"] if arm==A else
                                  x["same_sensor_posterior_evidence"]).get("wrong_confident",False)) if arm!=C else False,
                    before_probe_physical_action_diff_linf=max(diffs)))
    expected=4*len(selected(task,chunk))*len(ARMS)
    if len(arm_diffs)!=expected:
        raise RuntimeError("Incomplete all truth + active/neutral task matrix")
    report=dict(schema="new_active_probe_task_shard_provenance_v1",task=task,chunk=chunk,
        independent_reset_clusters=4,original_task_cells=4*4*2,
        all_native_robot_controller_worlds=4*4*2*len(source.NAMES),
        all_same_reset_true_ack_A_B_C_action_prefixes_confirmed=True,
        arm_paired_outcomes=arm_diffs,
        git_source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip())
    Path(f"physx_probe_{task}_chunk{chunk}_provenance.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=tuple(REGISTER))
    ap.add_argument("--chunk",type=int,choices=(0,1,2,3))
    ap.add_argument("--mode",choices=("preflight","run"),default="preflight")
    args=ap.parse_args()
    if args.mode=="preflight":
        print(json.dumps(preflight(),indent=2))
    else:
        if args.task is None or args.chunk is None:ap.error("run requires task and chunk")
        x=full_task_shard(args.task,args.chunk)
        print("NEW_ACTIVE_PROBE_TASK_SHARD_DONE",json.dumps({
            "task":x["task"],"chunk":x["chunk"],"actual_worlds":x["all_native_robot_controller_worlds"],
            "provenance_equal":x["all_same_reset_true_ack_A_B_C_action_prefixes_confirmed"]},sort_keys=True))
