"""Frozen public four-history UNKNOWN ACK PPO, actual 8-world real PhysX.

All original query comparators are separately actually executed; no
outcome-based splicing, test-time calibration, replay pretending to be PhysX,
or hidden target getter in new decision is allowed.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, os, subprocess, sys
from pathlib import Path

REGISTERED_BLOB="6e7db0a6af7dd4e6f33f7119ca0ae30f6fcbfd3b"
ORIGINAL_SOURCE_BLOB="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
FIRST={"pull_cube":1000101,"stack_cube":1010101}
PUBLIC="fault_robust_first_public_second_or_query"
NARROW="fault_public_t4_original_eps_or_t5_query"
PUBLIC_ARMS=(NARROW,PUBLIC)
SELECTIVE="fault_robust_then_single_privileged_query"
FIXED="fault_always_single_privileged_query"
PREREG="research/ACTION_EQUIVALENCE_FIRST_OOD_NEW64_PREOUTCOME_V1.json"
CHECKPOINT={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
            "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}

def blob(path):
    return subprocess.check_output(["git","hash-object",str(path)],text=True).strip()

def check_sources():
    if blob(PREREG)!=REGISTERED_BLOB:
        raise ValueError("Prospective registration changed AFTER being frozen")
    if blob("research/frozen_ppo_compound_ack_multi_belief.py")!=ORIGINAL_SOURCE_BLOB:
        raise ValueError("Original independently source-frozen controller baseline drift")
    p=json.loads(Path(PREREG).read_text())
    if p.get("schema")!="preoutcome_ood_robust_action_equivalence_first_public_evidence_second_new64_v1":
        raise ValueError("Not original registered experiment identity")
    return p

def accepted(task,chunk):
    if task not in TASKS or type(chunk) is not int or chunk not in range(4):
        raise ValueError("Exactly 8 source-frozen 4-seed task shards required")
    return list(range(FIRST[task]+8*chunk,FIRST[task]+8*chunk+8))

def validate_result(d,task,seeds):
    expected=("source_no_fault","fault_oracle_private_target",
       "fault_optimistic_unverified_ack","fault_strict_common_exact",
       "fault_robust_two_history_without_query",
       "fault_robust_then_single_privileged_query",
       "fault_always_single_privileged_query",
       "fault_assume_held_without_query",NARROW,PUBLIC)
    if (d.get("schema")!="frozen_ppo_AEF_robust_native_target_common_action_before_public_history_ood_physx_v7"
        or d.get("preoutcome_protocol")!=PREREG
        or d.get("original_seed_population")!=seeds
        or d.get("task")!=TASKS[task]
        or d.get("all_ten_actual_control_arms")!=list(expected)
        or d.get("frozen_model_retrained") is not False
        or d.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT[task]
        or d.get("real_physx_simulator") is not True
        or d.get("two_consecutive_unknown_ack_target_hold_steps")!=[2,3]
        or len(d.get("episodes",[]))!=8):
        raise ValueError("Source run missing actual frozen PPO native controller worlds")
    routed=SELECTIVE if task=="pull_cube" else FIXED
    results={m:{"success":0,"reads":0} for m in expected if m!="fault_oracle_private_target"}
    confidence={n:{"unique":0,"wrong":0,"reads":0,"success":0,"public_samples":0,
                   "complete_fault_exposure":0} for n in PUBLIC_ARMS}
    rawrows=[]
    for seed,r in zip(seeds,d["episodes"]):
        if r.get("seed")!=seed:
            raise ValueError("Missing or reordered source native PPO PhysX seed")
        if (r.get("original_precommitted_physical_t2_execution_truth")
            !=("applied" if seed%2==0 else "held")
            or r.get("original_precommitted_physical_t3_execution_truth")!=("applied" if (seed//2)%2==0 else "held")):
            raise ValueError("Actual applied/held truth not precommitted or missing")
        for control in ("fault_always_single_privileged_query",
                        "fault_assume_held_without_query",NARROW,PUBLIC):
            f=r.get("faults",{}).get(control,[])
            if len(f)!=2 or [x.get("step") for x in f]!=[2,3]:
                raise ValueError("Missing both physical native ACK interventions for "+control)
            if control=="fault_always_single_privileged_query":
                if f[0].get("actual_native_action_is_precommitted_applied") is not (seed%2==0):
                    raise ValueError("Wrong t2 native applied execution for fixed comparator")
                if f[1].get("actual_native_action_is_precommitted_applied") is not ((seed//2)%2==0):
                    raise ValueError("Fixed comparator t3 truth mismatched source protocol")
            else:
                if [x.get("actual_native_action_is_precommitted_applied") for x in f]!=[seed%2==0,(seed//2)%2==0]:
                    raise ValueError("Fault generator not executing declared native truth")
        original_mode="slow" if (seed//4)%2==0 else "fast"
        if r.get("actual_domain_mode_source_seed_assignment_AUDIT_ONLY")!=original_mode:
            raise ValueError("Original physical gain regime not precommitted")
        diag=r.get("domain_shift_actual_physx_readback_AUDIT_ONLY",{})
        if set(diag)!=set(expected):
            raise ValueError("Physical drive-shift not applied to all separate source and destination worlds")
        req={"slow":(500.,70.),"fast":(1500.,130.)}[original_mode]
        for n,rec in diag.items():
            if rec.get("domain_mode_injector_AUDIT_ONLY")!=original_mode:
                raise ValueError("Physical gain condition leaked or wrong physical domain")
            if rec.get("all_seven_physical_Panda_joint_drives_modified_and_read_back") is not True:
                raise ValueError("Panda physical gain domain alteration NOT executed")
            if len(rec.get("verified_arm_joints",[]))!=7:
                raise ValueError("Missing real individual 7 arm PD drives")
            q=rec["actual_joint_parameters_after_setter"]
            if (q.get("stiffness"),q.get("damping"),q.get("force_limit"))!=(req[0],req[1],100.):
                raise ValueError("Actual physical domain gain not verified")
        hybrid_trace=r.get("hybrid_authority_trace",{})
        if set(hybrid_trace)!={PUBLIC}:
            raise ValueError("Missing original hybrid robust-action provenance slot")
        flags=r["success_once"]; reads=r["privileged_target_readback_decision_count"]
        if set(flags)!=set(expected) or set(reads)!=set(expected):
            raise ValueError("Missing original method paired PhysX task flags/reads")
        for m in results:
            if type(flags[m]) is not bool or type(reads[m]) is not int or not 0<=reads[m]<=1:
                raise ValueError("Wrong native task outcome or unlogged private controller reads")
            results[m]["success"]+=int(flags[m]);results[m]["reads"]+=reads[m]
        if reads["fault_oracle_private_target"]!=-1:
            raise ValueError("Unlimited oracle falsely counted as zero-read")
        neutral=r.get("known_delivered_zero_probe",{})
        # The old strict controller can refuse at step 3. Do not fabricate
        # a later physical t4 step on an already completed/failed controller.
        required=(PUBLIC,NARROW,FIXED,SELECTIVE,"fault_assume_held_without_query")
        if any(n not in neutral for n in required):
            raise ValueError("One relevant physical comparator omitted t4 neutral step")
        omitted=set(expected)-set(neutral)
        for n in omitted:
            pre=r.get("refusals",{}).get(n)
            if not pre or type(pre.get("step")) is not int or pre["step"]>4:
                if not (r["success_once"][n] and r.get("steps",{}).get(n,50)<=4):
                    raise ValueError("Unjustified missing native common t4 physical step")
        for arm_name,record in neutral.items():
            if (record.get("step")!=4
                or record.get("actual_native_6d_dispatched")!=[0.]*6
                or record.get("acknowledgement")!="known_applied"
                or record.get("is_extra_common_physical_action") is not True
                or record.get("public_before_after_xyz_used_by_policy") is not (arm_name in PUBLIC_ARMS)
                or (arm_name!="source_no_fault" and
                    record.get("audit_only_native_target_unchanged") is not True)):
                raise ValueError("Real physical common known-delivered t4 zero probe invalid")
        if any(n not in neutral for n in (PUBLIC,NARROW)):
            raise ValueError("The two actually stepped public controllers did not both experience the t4 probe")
        assert set(r.get("public_t4_evidence",{}))==set(PUBLIC_ARMS)
        for observed in PUBLIC_ARMS:
            ev=r["public_t4_evidence"][observed]
            physical=r.get("faults",{}).get(observed,[])
            complete=len(physical)==2 and [z.get("step") for z in physical]==[2,3]
            if not complete or ev.get("physical_candidate_count")!=4:
                raise ValueError("Missing four true native execution hypotheses")
            if ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True:
                raise ValueError("Private native controller target used to decide action")
            distances=ev.get("candidate_residuals_m",[])
            eps=(.00719087965534261 if task=="stack_cube" else .006944262561376447)
            if len(distances)!=4 or ev["prior_training_epsilon_m"]!=eps:
                raise ValueError("Calibration threshold changed after preregistration")
            winning=[i for i,d in enumerate(distances) if d<=eps+1e-12]
            geometric=bool(len(winning)==1 and
                all(d>eps+.002 for i,d in enumerate(distances) if i!=winning[0]))
            authorized=geometric
            if (ev.get("authorized") is not authorized or
                ev.get("ungated_public_compatibility_authorization") is not geometric or
                ev.get("accepted_position_indices")!=winning):

                raise ValueError("Original public native history authorization not reproducible")
            truth=[i for i,(p,q) in enumerate(ev.get("after_physics_audit_pose_errors",[])) if p<=1e-4 and q<=1e-3]
            if truth!=ev.get("audit_only_true_candidate_indices"):
                raise ValueError("Original audit-only actual commanded target truth changed")
            wrong=bool(authorized and winning[0] not in truth)
            if ev.get("wrong_confident") is not wrong:
                raise ValueError("Wrong confident target history labels untrusted")
            if observed==PUBLIC:
                robust=ev.get("robust_first_step5_certificate_authorized",None)
                if robust is not None and type(robust) is not bool:
                    raise ValueError("Hybrid has invalid real source robust certificate admission")
                actual_use=ev.get("public_unique_history_used_for_policy")
                if actual_use is not None and type(actual_use) is not bool:
                    raise ValueError("Hybrid source public-index USED flag not boolean")
                if actual_use is True and not authorized:
                    raise ValueError("Hybrid used unauthorized public native memory index")
                if robust is True and actual_use is True:
                    raise ValueError("Hybrid made private public-history selection despite successful common bounded command")
            if observed==NARROW and authorized and ev.get("resync_source") not in (None,"empirical_public_achieved_motion"):
                raise ValueError("Observed target history silently triggered private read")
            if ev.get("resync_source")=="empirical_public_achieved_motion" and reads[observed]!=0:
                raise ValueError("Uncounted authoritative native read")
            if ev.get("resync_source")=="one_counted_authoritative_controller_target_read" and (
                (observed==NARROW and authorized) or reads[observed]!=1):
                raise ValueError("Unjustified source privileged read")
            elif ev.get("resync_source") is None and reads[observed]!=0:
                raise ValueError("Native read without recorded evidence")
            samples=r.get("public_motion_observation_cost_samples",{}).get(observed,0)
            if samples!=2:
                raise ValueError("Fair paired original and hybrid public t4 XYZ sensor cost mismatch")
            confidence[observed]["unique"]+=int(authorized)
            confidence[observed]["wrong"]+=int(wrong)
            confidence[observed]["reads"]+=reads[observed]
            confidence[observed]["success"]+=int(flags[observed])
            confidence[observed]["public_samples"]+=samples
            confidence[observed]["complete_fault_exposure"]+=int(complete)
        rawrows.append({
            "seed":seed,"task":task,
            "narrow_success":flags[NARROW],
            "hybrid_success":flags[PUBLIC],
            "strong_success":flags[routed],
            "fixed_success":flags[FIXED],
            "narrow_reads":reads[NARROW],
            "hybrid_reads":reads[PUBLIC],
            "strong_reads":reads[routed],
            "narrow_public_evidence":r["public_t4_evidence"][NARROW],
            "hybrid_public_evidence":r["public_t4_evidence"][PUBLIC],
            "hybrid_robust_certificate_accepted_t5":r["public_t4_evidence"][PUBLIC].get("robust_first_step5_certificate_authorized"),
            "hybrid_public_history_actually_used":r["public_t4_evidence"][PUBLIC].get("public_unique_history_used_for_policy"),
            "physics_drive_mode":original_mode,
            "original_native_step_4_exposed":all(name in neutral for name in (NARROW,PUBLIC,routed)),
            "true_joint_ack":("A" if seed%2==0 else "H")+("A" if (seed//2)%2==0 else "H")
        })
    return dict(task=task,seeds=seeds,controls=results,public=confidence,
                sample_rows=rawrows,expected_double_fault_in_all_new_arm_trials=
                all(confidence[n]["complete_fault_exposure"]==8 for n in PUBLIC_ARMS),
                not_robot_collision_safety_or_real_transport_loss=True,
                no_external_lab_replication=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS),required=True)
    p.add_argument("--chunk",type=int,choices=range(4),required=True)
    a=p.parse_args()
    check_sources()
    seeds=accepted(a.task,a.chunk)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_aef_hybrid_ood_physx_v7")
    if (runner.TASK!=a.task or runner.TASK_NAME!=TASKS[a.task] or
        runner.FAULT_STEPS!=(2,3) or runner.HORIZON!=50 or
        runner.POS_BUDGET!=.05 or runner.ROT_BUDGET!=.05 or
        runner.PUBLIC_ARM!=PUBLIC or runner.NARROW_ARM!=NARROW or runner.PROTO!=PREREG or
        len(runner.NAMES)!=10):
        raise RuntimeError("Frozen real PhysX source/chart/query contract changed")
    runner.SEEDS=seeds
    runner.COHORT[a.task]=(TASKS[a.task],seeds)
    runner.main()  # Every one of 8 native PhysX comparators REALLY executes.
    path=Path(f"aef_hybrid_{a.task}_original8.json")
    raw=path.read_bytes()
    d=json.loads(raw)
    s=validate_result(d,a.task,seeds)
    s.update(schema="aef_hybrid_native_action_OOD_new64_shard_audit_v1",
             original_raw_sha256=hashlib.sha256(raw).hexdigest(),
             frozen_prereg_blob=REGISTERED_BLOB,
             source_runner_git_blob=blob("research/frozen_ppo_aef_hybrid_ood_physx_v7.py"))
    Path(f"aef_hybrid_{a.task}_chunk{a.chunk}_audit.json").write_text(
        json.dumps(s,indent=2,sort_keys=True)+"\n")
    path.rename(f"aef_hybrid_{a.task}_chunk{a.chunk}_original8.json")
    print("TRUE_NATIVE_PPO_AEF_HYBRID_SHARD",json.dumps({
        "task":a.task,"chunk":a.chunk,"hybrid":s["controls"][PUBLIC],"old_narrow":s["controls"][NARROW],
        "strong_task_gate":s["controls"][SELECTIVE if a.task=="pull_cube" else FIXED],
        "public":s["public"],"source_seeds":seeds},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
