"""FROZEN prospective full-task physical test of source-only ICERE vs original A.

NO weight fitting, threshold tuning or audit-truth online input. Same real
native CPU PhysX PPO and source world state. Four physical ACK truth cases and
two actually delivered probe actions per 32 NEW task reset clusters. Each
condition actually steps 2 methods x 10 native controller arms.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,random,subprocess,sys
from pathlib import Path
PRE="research/ICERE_UNSEEN_PPO_TASK_PREOUTCOME_20261010.json"
REG={"pull_cube":("PullCube-v1",4500001,"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
     "stack_cube":("StackCube-v1",4600001,"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")}
SOURCE_BLOB="2f2fc34f492bf6d2810b48193283e0347f6bdc93"
SOURCE_A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
C="fault_always_single_privileged_query"
ARMS=(SOURCE_A,B,C)
TRUTHS=(0,1,2,3)
PROBES=("zero","x")
KINDS=("original","icere")

def gitblob(path):
    return subprocess.check_output(("git","hash-object",path),text=True).strip()

def preflight():
    p=json.loads(Path(PRE).read_text())
    if (p["schema"]!="icere_unseen_physx_selective_authority_v1"
        or p["independent_reset_clusters"]!=32
        or p["registered_new_heldout_task_fault_probe_cells"]!=256
        or p["registered_full_task_physical_source_worlds"]!=5120
        or p["model_full_weights_sha256"]!="bb2790c2151ab908387e826aa8a5cb30bdc61a4fae4693df7f3ff8012262549c"
        or p["full_model_offline_thresholds"]!=
           {"pull_cube:zero":1,"pull_cube:x":.93,"stack_cube:zero":.5,"stack_cube:x":.99}
        or gitblob("research/frozen_ppo_matched_public_factorial128_physx.py")!=SOURCE_BLOB):
        raise ValueError("PhysX source, registered model, selection or heldout cohort changed")
    for task,(_,start,_) in REG.items():
        if p["true_independent_reset_ids"][task]!=[start,start+15]:
            raise ValueError("Retrospective changed heldout reset")
    chk=Path(os.environ.get("ICERE_FROZEN_MODEL_PT",""))
    if not chk.is_file() or hashlib.sha256(chk.read_bytes()).hexdigest()!=p["model_full_weights_sha256"]:
        raise ValueError("Missing/unfrozen prior source-only learned weights")
    return p

def selected(task,chunk):
    if task not in REG or type(chunk) is not int or chunk not in range(4):
        raise ValueError("Invalid preregistered physical task shard")
    start=REG[task][1]+chunk*4
    return tuple(range(start,start+4))

def run(task,chunk):
    p=preflight()
    import torch,numpy as np
    from huggingface_hub import hf_hub_download
    os.environ["ABI_TASK"]=task
    sys.path.insert(0,str(Path.cwd()/"research"))
    base=importlib.import_module("frozen_ppo_action_history_observer")
    modules={
        ("zero","original"):importlib.import_module("research.frozen_ppo_matched_public_factorial128_physx"),
        ("x","original"):importlib.import_module("research.frozen_ppo_known_x_probe_task_physx"),
        ("zero","icere"):importlib.import_module("research.icere_zero_frozen_ppo_task_physx"),
        ("x","icere"):importlib.import_module("research.icere_x_frozen_ppo_task_physx")}
    env_name,path,sha,_=base.TASKS[task]
    if (env_name,sha)!=(REG[task][0],REG[task][2]):raise ValueError("Published pretrained PPO identity drift")
    ckpt=Path(hf_hub_download(repo_id=base.REPO,filename=path,revision=base.PUBLISHED_MODEL_REVISION))
    if hashlib.sha256(ckpt.read_bytes()).hexdigest()!=sha:
        raise RuntimeError("External frozen policy weights changed")
    env=base.env("pd_ee_delta_pose")
    try:
        obs,_=env.reset(seed=selected(task,chunk)[0])
        base.POLICY_OBS_DIM=int(obs.shape[-1])
        policy=base._actor(torch.load(ckpt,map_location="cpu",weights_only=True),base.POLICY_OBS_DIM,7)
    finally:env.close()
    names=next(iter(modules.values())).NAMES
    if len(names)!=10 or any(m.NAMES!=names or m.HORIZON!=50 or tuple(m.FAULT_STEPS)!=(2,3)
                             for m in modules.values()):
        raise RuntimeError("Matched physically simulated method arms changed")
    all_rows={};rows=[]
    for truth in TRUTHS:
        os.environ["ABI_TRUTH_INDEX"]=str(truth)
        for probe in PROBES:
            for kind in KINDS:
                runner=modules[probe,kind]
                source=[]
                for seed in selected(task,chunk):
                    random.seed(seed);np.random.seed(seed%(2**32));torch.manual_seed(seed)
                    episode=runner.trial(policy,seed)
                    if (episode["task"]!=env_name or episode["seed"]!=seed or
                       (episode["original_precommitted_physical_t2_execution_truth"]=="applied")!=(truth in (1,3)) or
                       (episode["original_precommitted_physical_t3_execution_truth"]=="applied")!=(truth in (2,3))):
                        raise RuntimeError("Original native actual ACK delivery drift")
                    for arm in ARMS:
                        fault=episode["faults"].get(arm,[])
                        probe4=episode["shared_neutral_probe_step4"].get(arm,{})
                        expected=[.15,0.,0.,0.,0.,0.] if probe=="x" else [0.]*6
                        actual=probe4.get("native_six_dim_arm",[])
                        if (len(fault)!=2 or [x["step"] for x in fault]!=[2,3]
                            or len(actual)!=6
                            or max(abs(float(a)-b) for a,b in zip(actual,expected))>1e-6
                            or abs(probe4.get("audit_only_target_position_delta_m",999)-(.015 if probe=="x" else 0))>5e-5
                            or episode["public_motion_observation_cost_samples"].get(arm)!=(0 if arm==C else 2)
                            or type(episode["success_once"].get(arm)) is not bool):
                            raise RuntimeError("Physical source truth/probe/public observation budget not matched")
                    ev=episode["public_t3_evidence"]
                    if kind=="icere":
                        if (ev.get("icere_observation_action_identity")!=probe
                            or not ev.get("source_only_calibration_is_not_safety_certificate")
                            or ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True):
                            raise RuntimeError("Learned model did not actually control PUBLIC A branch")
                    else:
                        if "icere_frozen_calibrated_ranker_score" in ev:
                            raise RuntimeError("Previously validated baseline was silently replaced by ICERE")
                    source.append(episode)
                    all_rows[(task,seed,truth,probe,kind)]=episode
                    row=dict(task=task,seed=seed,truth=truth,probe=probe,kind=kind,
                             success_A=episode["success_once"][SOURCE_A],
                             success_B=episode["success_once"][B],
                             success_C=episode["success_once"][C],
                             reads_A=episode["privileged_target_readback_decision_count"][SOURCE_A],
                             reads_B=episode["privileged_target_readback_decision_count"][B],
                             reads_C=episode["privileged_target_readback_decision_count"][C],
                             authorized_A=bool(ev["authorized"]),
                             wrong_A=bool(ev["wrong_confident"]),
                             true_target_AUDIT_ONLY_NOT_DECISION=ev["audit_only_true_candidate_indices"])
                    rows.append(row)
                    print("ICERE_NEW_REAL_TASK_PHYSX",json.dumps(row,sort_keys=True),flush=True)
                filename=f"icere_task_{task}_chunk{chunk}_truth{truth}_{probe}_{kind}.json"
                Path(filename).write_text(json.dumps(dict(
                    schema="actual_heldout_icere_native_physx_original_v1",
                    task=task,chunk=chunk,truth=truth,probe=probe,kind=kind,
                    pretrained_PPO_checkpoint_sha256=sha,
                    freeze_source_file_commit=subprocess.check_output(("git","rev-parse","HEAD"),text=True).strip(),
                    actually_physically_executed_native_controller_worlds=len(source)*len(names),
                    icar_model_frozen_sha256=p["model_full_weights_sha256"],
                    no_retraining_on_heldout=True,
                    all_sensed_public_only_for_ICERE=True,
                    original_reset_ids=selected(task,chunk),episodes=source),
                    indent=2,sort_keys=True)+"\n")
        # Before task divergence, all 4 future policies see precisely same
        # native ACK execution and physical ZERO/X preintervention history.
        for seed in selected(task,chunk):
            entries=[all_rows[(task,seed,truth,a,k)] for a in PROBES for k in KINDS]
            if len({r["initial_source_physical_obs_sha256"] for r in entries})!=1:
                raise RuntimeError("Unmatched original physical task initial state")
            ref=entries[0]["faults"][SOURCE_A]
            for episode in entries[1:]:
                f=episode["faults"][SOURCE_A]
                if len(f)!=2 or any(max(abs(float(a)-float(b)) for a,b in zip(x["actual_native_6d_dispatched"],y["actual_native_6d_dispatched"]))>1e-6
                                    for x,y in zip(ref,f)):
                    raise RuntimeError("Original PhysX pre-t4 target command differs across comparators")
        # Closed-loop changes in A must not alter B or C physically separate
        # baseline worlds under identical probe/fault/trial initial state.
        for seed in selected(task,chunk):
            for probe in PROBES:
                base_r=all_rows[(task,seed,truth,probe,"original")]
                new_r=all_rows[(task,seed,truth,probe,"icere")]
                for arm in (B,C):
                    if (base_r["success_once"][arm]!=new_r["success_once"][arm]
                        or base_r["privileged_target_readback_decision_count"][arm]!=new_r["privileged_target_readback_decision_count"][arm]):
                        raise RuntimeError("ICERE control change leaked into its supposed B/C physically independent baselines")
    if len(rows)!=4*4*2*2:
        raise RuntimeError("Incomplete physical experiment shard")
    Path(f"icere_task_{task}_chunk{chunk}_provenance.json").write_text(json.dumps(dict(
        schema="registered_prospective_full_task_32_reset_icere_shard_v1",
        task=task,chunk=chunk,independent_reset_clusters=4,
        actually_executed_controller_worlds=len(rows)*10,
        source_only_frozen_model_sha256=p["model_full_weights_sha256"],
        original_model_heldout_training_labels_used_in_decision=False,
        results=rows),indent=2,sort_keys=True)+"\n")
    return rows

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--task",choices=tuple(REG))
    parser.add_argument("--chunk",choices=range(4),type=int)
    parser.add_argument("--mode",choices=("preflight","run"),required=True)
    arg=parser.parse_args()
    if arg.mode=="preflight":
        print(json.dumps(preflight(),indent=2))
    else:
        if arg.task is None or arg.chunk is None:parser.error("Must register task and chunk")
        rows=run(arg.task,arg.chunk)
        print("ICERE_SOURCE_ONLY_HELDOUT_SHARD_DONE",json.dumps(dict(
            task=arg.task,chunk=arg.chunk,actual_task_worlds=len(rows)*10,
            original_reset_clusters=len(set(r["seed"] for r in rows))),sort_keys=True))
