"""Full-denominator audit of PRE-REGISTERED typed native-source PhysX 16-state pilot.

Independent of real PhysX runner's aggregate; stdlib only. A bad source
controller action before t2 is a *failed primary exposure gate*, not a silently
removed cohort. Records exactly same nine physical arms and all failures.

Never treat a successful code test as external adoption or hardware safety.
"""
import argparse
import json
from pathlib import Path

FIRST={"pull_cube":380001,"stack_cube":390001}
NAMES=(
    "source_no_fault","fault_oracle_private_target",
    "fault_optimistic_unverified_ack","fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_robust_quota_two_per_eight",
    "fault_precommitted_seed_schedule_query",
    "fault_always_single_privileged_query",
)
CHECKPOINTS={
    "pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
    "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"
}
CAP=NAMES[6]
FIXED=NAMES[7]
UNCAPPED=NAMES[5]
HARD_FAULT_GATES=(NAMES[2],NAMES[4],NAMES[5],CAP,FIXED,NAMES[8])


def audit(directory:Path)->dict:
    report={"schema":"native_controller_typed_guard_new16_full_intention_to_test_audit",
            "full_registered_reset_states":16,
            "typed_guard_original_git_blob":"a0e46bc42fd0d8e33580e79dc94408ff301cae09",
            "predeclared_source_original_study_failed_370029_not_retroactively_reclassified":True,
            "original_robot_physical_simulator_run_independent_external":False,
            "predeclared_hard_fault_gate_requires_exposure_for_each_arm":True,
            "per_task":{}}
    total={name:0 for name in NAMES}
    reads={name:0 for name in NAMES if name!=NAMES[1]}
    corrected=0
    source_error_records=[]
    unexposed=[]
    matched=[]
    for task,seed_start in FIRST.items():
        file=directory/f"typed_gate_{task}_new8_original.json"
        obj=json.loads(file.read_text())
        seeds=list(range(seed_start,seed_start+8))
        if (obj.get("schema")!="typed_controller_authority_fresh16_real_physx_v1"
            or obj.get("typed_native_guard_git_blob")!=report["typed_guard_original_git_blob"]
            or obj.get("original_strict_nine_arm_source_git_blob")!="f3290b6a2d93d572c2ac73977044de1763a2ad0b"
            or obj.get("preoutcome_protocol_first_commit")!="c4bdbafcdee54dd538cb32754a58c09cc42b410c"
            or obj.get("frozen_protocol")!="research/TYPED_CONTROLLER_ADMISSION_NEW16_PREOUTCOME_V1.json"
            or obj.get("task")!=("PullCube-v1" if task=="pull_cube" else "StackCube-v1")
            or obj.get("original_seed_population")!=seeds
            or obj.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINTS[task]
            or obj.get("frozen_model_retrained") is not False
            or obj.get("real_physx_simulator") is not True
            or obj.get("all_nine_actual_control_arms")!=list(NAMES)
            or obj.get("fault_is_native_target_hold_not_network_loss") is not True):
            raise ValueError("Unregistered or modified source-model/robot-fault protocol")
        cases=obj.get("episodes")
        if not isinstance(cases,list) or len(cases)!=8:
            raise ValueError("Omitted original negative reset state / changed cohort")
        sumsuccess={name:0 for name in NAMES}
        targetreads={CAP:0,FIXED:0,UNCAPPED:0}
        per_case=[]
        for i,r in enumerate(cases):
            seed=seed_start+i
            if r.get("seed")!=seed or r.get("task")!=obj["task"]:
                raise ValueError("Original model seed identity changed")
            flags=r.get("success_once",{})
            if set(flags)!=set(NAMES) or any(type(x) is not bool for x in flags.values()):
                raise ValueError("Every original native task outcome must be exact boolean")
            qs=r.get("privileged_target_readback_decision_count",{})
            if set(qs)!=set(NAMES) or any(type(v) is not int for v in qs.values()):
                raise ValueError("Hidden, altered or missing private-controller target reads")
            if qs[NAMES[1]]!=-1:
                raise ValueError("Continuous oracle reads are not zero")
            if any(qs[n]!=0 for n in (NAMES[0],NAMES[2],NAMES[3],NAMES[4])):
                raise ValueError("Zero-information controller accessed private target")
            if qs[CAP] not in (0,1) or qs[FIXED] not in (0,1) or qs[UNCAPPED] not in (0,1):
                raise ValueError("Native episode read budget invalid")
            for name in NAMES:
                sumsuccess[name]+=int(flags[name])
                total[name]+=int(flags[name])
                if name!=NAMES[1]:
                    reads[name]+=qs[name]
            for arm in targetreads:
                targetreads[arm]+=qs[arm]
            f=r.get("faults",{})
            missing=[]
            for arm in HARD_FAULT_GATES:
                fault=f.get(arm)
                if fault is None:
                    missing.append(arm)
                    unexposed.append({"task":task,"seed":seed,"arm":arm,
                                      "failures":r.get("failure_causes",{}).get(arm),
                                      "refusal":r.get("refusals",{}).get(arm)})
                elif (fault.get("step")!=2
                      or fault.get("actual_native_arm_command")!="all_zero_hold"
                      or fault.get("controller_execution_ack_seen_by_adapter")!="unknown"):
                    raise ValueError("False native PhysX target hold / unknown ACK")
            for arm,events in r.get("typed_admission_corrected_actions",{}).items():
                if arm not in NAMES[1:] or not isinstance(events,list):
                    raise ValueError("Typed native action correction attributed to invalid arm")
                for event in events:
                    corrected+=1
                    if (event.get("did_not_claim_exact_desired_target_after_projection") is not True
                        or event.get("additional_position_target_error_m",99)>1e-5+1e-10
                        or event.get("additional_orientation_target_error_rad",99)>1e-5+1e-10
                        or event.get("actually_dispatched_native_rotation_l2",99)>=1):
                        raise ValueError("Native physical chart correction is not verified")
            for arm,events in r.get("typed_admission_refusals",{}).items():
                if arm not in NAMES[1:] or not isinstance(events,list):
                    raise ValueError("Missing typed action refusal provenance")
                for event in events:
                    source_error_records.append({
                        "task":task,"seed":seed,"arm":arm,"step":event.get("step"),
                        "reason":event.get("status")})
            # The original nine-arm quotalimit must reset ONLY between 8-state
            # shards and never borrow a future token within this shard.
            if r.get("quota_before_trial",99)-r.get("quota_after_trial",0)!=qs[CAP]:
                raise ValueError("Claimed query budget not consistent with original episode")
            per_case.append({"task":task,"seed":seed,"success_capped":flags[CAP],
                             "success_fixed":flags[FIXED],"capped_reads":qs[CAP],
                             "fixed_reads":qs[FIXED],"unexposed_primary_arms":missing})
            matched.append((flags[CAP],flags[FIXED]))
        if obj.get("success_counts")!=sumsuccess:
            raise ValueError("Fake original source task-success aggregate")
        if obj.get("quota_used_actual")!=targetreads[CAP] or targetreads[CAP]>2:
            raise ValueError("Shard original hard token budget exceeded")
        report["per_task"][task]={
            "unique_original_task_reset_states":8,
            "source_PPO_checkpoint_sha256":CHECKPOINTS[task],
            "original_native_task_success":sumsuccess,
            "actual_privileged_target_read_counts":targetreads,
            "every_registered_seed_including_early_failures":per_case}
    both=sum(a and b for a,b in matched)
    caponly=sum(a and not b for a,b in matched)
    fixedonly=sum(b and not a for a,b in matched)
    report["all16_original_native_success_counts"]=total
    report["all16_actual_controller_target_private_reads"]=reads
    report["all16_native_roundoff_canonicalizations"]=corrected
    report["all16_unrepresentable_native_refusal_details"]=source_error_records
    report["hard_original_full_fault_exposure_failed_conditions"]=unexposed
    report["original_predeclared_primary_inference_gate_PASSED"]=len(unexposed)==0
    report["capped_v_fixed_paired"]={
        "both":both,"capped_only":caponly,"fixed_only":fixedonly,
        "neither":16-both-caponly-fixedonly}
    report["not_retroactively_claimed_as_a_successful_original_strict_budget_370029_run"]=True
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=audit(a.input_dir)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("TYPED_NATIVE_PHYSX_FULL16_SOURCE_AUDIT",json.dumps({
        "successes":result["all16_original_native_success_counts"],
        "reads":result["all16_actual_controller_target_private_reads"],
        "typed_roundoff_repair_count":result["all16_native_roundoff_canonicalizations"],
        "fault_gate_passed":result["original_predeclared_primary_inference_gate_PASSED"],
        "fault_gate_failures":result["hard_original_full_fault_exposure_failed_conditions"],
    },sort_keys=True))
