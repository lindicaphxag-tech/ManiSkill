"""Actually run 8 untouched frozen PPO ManiSkill PhysX resets and independently
audit ALL task failures/true native ACKs, public quaternion+XYZ inputs and
complete SE3 hidden-controller target authority. No post-outcome threshold fit.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,math,os,subprocess,sys
from pathlib import Path
PROTO="research/JOINT_PUBLIC_SO3_XYZ_FROZEN_NEW64_PREOUTCOME_V1.json"
SOURCE="research/frozen_ppo_joint_public_SE3_new64_physx.py"
PROTO_BLOB="88adbc25f0435f8c452e988891f3745e49afea08"
SOURCE_BLOB="8969e86867568b2ef7ebcef4883361b0eb1f4033"
TASKS={"pull_cube":("PullCube-v1",3310001,"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
       "stack_cube":("StackCube-v1",3320001,"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")}
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_joint_public_SE3_arc020_or_query"
C="fault_always_single_privileged_query"
def blob(path):return subprocess.check_output(("git","hash-object",path),text=True).strip()
def freeze():
    if blob(PROTO)!=PROTO_BLOB or blob(SOURCE)!=SOURCE_BLOB:
        raise ValueError("New unseen policy or preoutcome joint-source SHA drift")
    p=json.loads(Path(PROTO).read_text())
    if p.get("schema")!="prospective_frozen_PPO_native_joint_public_SE3_ack_history_new64_v1":
        raise ValueError("Wrong before-new-PhysX protocol")
    if p["n_original_reset_states"]!=64 or p["preregistered_real_physics_worlds"]!=640:
        raise ValueError("Protocol target denominator changed")
def seeds(task,ch):
    if task not in TASKS or type(ch)!=int or ch not in range(4):
        raise ValueError("Unregistered task/chunk")
    return list(range(TASKS[task][1]+8*ch,TASKS[task][1]+8*(ch+1)))
def expose(e,arm):
    return sorted(f["step"] for f in e.get("faults",{}).get(arm,[]))
def valid_pose_audit(e,key):
    d=e.get(key,{})
    if d.get("valid_exact_prefix") is not True:return False
    if len(d.get("native_fault_dispatch_linf_each",[]))!=2:return False
    for v in list(d["native_fault_dispatch_linf_each"])+[
      d.get("pre_t5_achieved_position_max_abs_m"),d.get("pre_t5_achieved_orientation_geodesic_rad"),
      d.get("pre_t5_target_position_max_abs_m"),d.get("pre_t5_target_orientation_geodesic_rad")]:
        if not isinstance(v,(float,int)) or not math.isfinite(v) or v>5e-5:return False
    return True
def original_eight(source,task,ch):
    wanted=seeds(task,ch)
    if (source.get("schema")!="frozen_PPO_joint_public_SE3_new64_real_PhysX_v1" or
        source.get("task")!=TASKS[task][0] or source.get("original_seed_population")!=wanted or
        source.get("original_external_frozen_checkpoint_sha256")!=TASKS[task][2] or
        source.get("real_physx_simulator") is not True or
        source.get("frozen_model_retrained") is not False or
        source.get("preoutcome_protocol")!=PROTO or
        len(source.get("episodes",[]))!=8):
        raise ValueError("Invalid physically stepped original complete 8 source")
    rows=[]
    for seed,e in zip(wanted,source["episodes"]):
        if e.get("seed")!=seed:raise ValueError("Original episode dropped/changed")
        f=(seed-1)%4
        expected=("applied" if f in (1,3) else "held",
                  "applied" if f in (2,3) else "held")
        if (e.get("original_precommitted_physical_t2_execution_truth"),
            e.get("original_precommitted_physical_t3_execution_truth"))!=expected:
            raise ValueError("Physical ACK truth mismatch")
        outcome=e.get("success_once",{});read=e.get("privileged_target_readback_decision_count",{})
        for name in (A,B,C):
            if type(outcome.get(name)) is not bool or type(read.get(name)) is not int or read[name] not in (0,1):
                raise ValueError("Original task-success / target reads wrong")
        fa,fb,fc=(expose(e,n) for n in (A,B,C))
        full=(fa==fb==fc==[2,3])
        if full:
            if not (valid_pose_audit(e,"matched_prefix_physical_audit") and
                    valid_pose_audit(e,"matched_joint_SE3_prefix_audit")):
                raise ValueError("Native physical predecision SE3 mismatch")
            orig=e["public_t3_evidence"];new=e["joint_public_SE3_evidence"]
            if orig.get("so3_only_feasibility_no_decision_use") is not True:
                raise ValueError("XYZ baseline illegally consumed SO3")
            if new.get("so3_only_feasibility_no_decision_use") is not False or new.get("SO3_actual_decision_input_in_joint_arm") is not True:
                raise ValueError("SO3 arm did not actually use measured orientation for decision")
            if orig.get("SO3_actual_decision_input_in_joint_arm") is not False:
                raise ValueError("Original public method was not XYZ-only")
            if any(v.get("so3_public_samples_charged")!=2 for v in (orig,new)):
                raise ValueError("Missing two true public SO3 pose samples")
            if e["public_motion_observation_cost_samples"][A]!=2 or e["public_motion_observation_cost_samples"][B]!=2:
                raise ValueError("Unequal achieved XYZ sample cost")
            for x in (orig,new):
                if x.get("audit_only_hidden_target_was_NOT_decision_input") is not True:
                    raise ValueError("Private controller truth leaked into algorithmic decision")
                if len(x.get("candidate_residuals_m",[]))!=x.get("physical_candidate_count"):
                    raise ValueError("Native hypothesis XYZ missing")
                if len(x.get("so3_public_geodesic_to_candidate_arc_rad",[]))!=x["physical_candidate_count"]:
                    raise ValueError("Native hypothesis actual quaternion observation missing")
                if len(x.get("audit_only_true_candidate_indices",[]))!=1:
                    raise ValueError("Physical true hidden target missing from provenance")
            winners=[i for i,(px,theta) in enumerate(zip(
                new["candidate_residuals_m"],new["so3_public_geodesic_to_candidate_arc_rad"]))
                if px<=new["prior_training_epsilon_m"]+1e-12 and theta<=.02+1e-12]
            if new.get("joint_public_SO3_radius_train_selected_rad")!=.02 or
                    new.get("joint_public_SO3_threshold_NOT_calibrated_risk") is not True:
                raise ValueError("Post-outcome joint SO3 radius tuning detected")
            if new.get("joint_public_full_SE3_feasible_history_indices")!=winners:
                raise ValueError("Joint history set used nonpublic private state")
            if new.get("authorized") is not (len(winners)==1):
                raise ValueError("Original joint gate not followed")
            if new.get("selected_candidate_index")!=(winners[0] if len(winners)==1 else None):
                raise ValueError("Incomplete whole SE3 candidate or confidence index mismatch")
            for ev in (orig,new):
                wrong=bool(ev["authorized"] and
                           ev["selected_candidate_index"] not in ev["audit_only_true_candidate_indices"])
                if ev["wrong_confident"] is not wrong:
                    raise ValueError("False-confidence error illegally hidden")
            for name in (A,B,C):
                probe=e.get("shared_neutral_probe_step4",{}).get(name,{})
                if (probe.get("physically_dispatched") is not True or
                    probe.get("known_delivered_no_new_unknown_ack") is not True):
                    raise ValueError("Missing same known-delivered native neutral")
        else:
            # A premature frozen-PPO refusal must remain in original 64 ITT.
            if not (fa in ([],[2]) and fb in ([],[2]) and fc in ([],[2])):
                raise ValueError("Cannot claim invalid full 2x2 physical exposure")
            orig=e.get("public_t3_evidence",{});new=e.get("joint_public_SE3_evidence",{})
        rows.append({
            "task":task,"seed":seed,"true_ACK_pattern":f,"actual_2x2_physically_exposed_pre_t5_matched":full,
            "original_actual_fault_steps":{n:expose(e,n) for n in (A,B,C)},
            "official_task_success":{n:outcome[n] for n in (A,B,C)},
            "true_private_target_register_reads":{n:read[n] for n in (A,B,C)},
            "public_XYZ_pose_events":{n:e.get("public_motion_observation_cost_samples",{}).get(n,0) for n in (A,B)},
            "actual_public_SO3_pose_events":{n:(e.get("public_t3_evidence",{}) if n==A else e.get("joint_public_SE3_evidence",{})).get("so3_public_samples_charged",0) for n in (A,B)},
            "confident_complete_histories":{A:bool(orig.get("authorized",False)) if full else False,B:bool(new.get("authorized",False)) if full else False},
            "wrong_confident_complete_history":{A:bool(orig.get("wrong_confident",False)) if full else False,B:bool(new.get("wrong_confident",False)) if full else False},
            "source_original_hash_only_truth_after_real_physics":True})
    return {"schema":"genuine_joint_public_SE3_8_physx_native_frozen_PPO_v1",
            "task":task,"chunk":ch,"original_seed_ids":wanted,
            "native_PhysX_controller_world_instances":80,
            "full_double_ACK_physically_exposed":sum(r["actual_2x2_physically_exposed_pre_t5_matched"] for r in rows),
            "original_all_8":rows}
def main():
    a=argparse.ArgumentParser();a.add_argument("--task",choices=tuple(TASKS),required=True)
    a.add_argument("--chunk",type=int,choices=range(4),required=True);x=a.parse_args()
    freeze()
    os.environ["ABI_TASK"]=x.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    m=importlib.import_module("frozen_ppo_joint_public_SE3_new64_physx")
    expected=seeds(x.task,x.chunk)
    m.SEEDS=range(expected[0],expected[-1]+1)
    m.COHORT[x.task]=(TASKS[x.task][0],m.SEEDS)
    m.main()
    file=Path(f"jointse3_{x.task}_original8.json")
    raw=file.read_bytes()
    original=json.loads(raw)
    audit=original_eight(original,x.task,x.chunk)
    audit["exact_unmodified_physx_original_SHA256"]=hashlib.sha256(raw).hexdigest()
    prefix=f"jointse3_{x.task}_chunk{x.chunk}"
    file.rename(prefix+"_original8.json")
    Path(prefix+"_audit.json").write_text(json.dumps(audit,sort_keys=True,indent=2)+"\n")
    print("JOINT_PUBLIC_SE3_NEW_PHYSX_8",json.dumps({
        "task":x.task,"chunk":x.chunk,"n":8,"full_exposed":audit["full_double_ACK_physically_exposed"],
        "success":{n:sum(r["official_task_success"][n] for r in audit["original_all_8"]) for n in (A,B,C)},
        "private_reads":{n:sum(r["true_private_target_register_reads"][n] for r in audit["original_all_8"]) for n in (A,B,C)},
        "wrong_confident":{n:sum(r["wrong_confident_complete_history"][n] for r in audit["original_all_8"]) for n in (A,B)}},sort_keys=True))
if __name__=="__main__":main()
