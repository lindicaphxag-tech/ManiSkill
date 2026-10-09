"""Independent, stdlib-only audit of the FIRST four-joint-ACK original PhysX artifacts.

Important source provenance: original native execution job archive was produced
by GH Actions run 37917629944, whose jobs FAILED only after physically writing
the complete source JSON because the original per-shard AUDITOR wrongly required
an already-refused strict comparator to execute an impossible later probe.

This script NEVER runs/manipulates a simulator or source PPO; it accepts every
byte-identical original JSON, checks all primary controller arms, full t2/t3
physical truth, and preserves stopped early negative baselines. It reports
source-run outcome as failed, independently validated physical data separately.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
RUN_ID=37917629944
SOURCE_EXECUTED_COMMIT="96e3dfc30bd48b4a288cc07a6952a75f387c5e27"
REGISTERED_PROTOCOL_GIT_BLOB="d848b24945b15470e843bb71998a893fbb6fe4ce"
FROZEN_RUNNER_GIT_BLOB="918aa573eee3313886d5609f671c3ee599561e52"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
START={"pull_cube":880001,"stack_cube":890001}
CHECKPOINT={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
            "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
EPS={"pull_cube":.006944262561376447,"stack_cube":.00719087965534261}
NAMES=("source_no_fault","fault_oracle_private_target",
       "fault_optimistic_unverified_ack","fault_strict_common_exact",
       "fault_robust_two_history_without_query",
       "fault_robust_then_single_privileged_query",
       "fault_always_single_privileged_query",
       "fault_assume_held_without_query",
       "fault_public_t4_fourhistory_or_t5_query")
PUBLIC=NAMES[-1]
STRONG={"pull_cube":"fault_robust_then_single_privileged_query",
        "stack_cube":"fault_always_single_privileged_query"}
FIXED="fault_always_single_privileged_query"
HELD="fault_assume_held_without_query"

def truth(seed,step):
    if step==2:
        return (seed%2==0)
    if step==3:
        return ((seed//2)%2==0)
    raise ValueError("Unexpected physical fault step")

def external_original_source_audit(folder):
    required={f"full_joint_ack_{task}_chunk{chunk}_original8.json"
              for task in TASKS for chunk in range(4)}
    actual={p.name for p in folder.glob("full_joint_ack_*_original8.json")}
    if actual!=required:
        raise ValueError(f"Incomplete physical source shards. missing={required-actual}, unexpected={actual-required}")
    rows=[]
    manifest={}
    for task in TASKS:
        for chunk in range(4):
            file=folder/f"full_joint_ack_{task}_chunk{chunk}_original8.json"
            raw=file.read_bytes()
            manifest[file.name]=hashlib.sha256(raw).hexdigest()
            j=json.loads(raw)
            expected=list(range(START[task]+chunk*8,START[task]+chunk*8+8))
            if (j.get("schema")!="frozen_ppo_full_joint_ACK_truths_neutral_t4_physx_v4"
                or j.get("original_seed_population")!=expected
                or j.get("task")!=TASKS[task]
                or j.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT[task]
                or j.get("all_nine_actual_control_arms")!=list(NAMES)
                or j.get("preoutcome_protocol")!="research/ALL_FOUR_ACK_JOINT_TRUTH_PPO_NEW64_PREOUTCOME_V1.json"
                or j.get("real_physx_simulator") is not True
                or j.get("frozen_model_retrained") is not False
                or len(j.get("episodes",[]))!=8):
                raise ValueError(f"Native original PhysX experiment/source identity drift: {file}")
            for seed,row in zip(expected,j["episodes"]):
                if row.get("seed")!=seed or row.get("original_precommitted_physical_t2_execution_truth")!=("applied" if truth(seed,2) else "held") or row.get("original_precommitted_physical_t3_execution_truth")!=("applied" if truth(seed,3) else "held"):
                    raise ValueError("Physical experiment omitted/misreported a frozen seed or ACK truth")
                tasks=row.get("success_once",{})
                priv=row.get("privileged_target_readback_decision_count",{})
                if set(tasks)!=set(NAMES) or set(priv)!=set(NAMES):
                    raise ValueError("Nine true controllers not independently accounted for")
                for name in NAMES:
                    if type(tasks[name]) is not bool:
                        raise ValueError("Nonphysical task success flag")
                    if type(priv[name]) is not int or (priv[name] not in (0,1) and not (name==NAMES[1] and priv[name]==-1)):
                        raise ValueError("Nonphysical private-target read count")
                # The three KEY competing algorithms MUST physically encounter
                # BOTH ACK truth steps and the known t4 neutral probe.
                for name in (PUBLIC,FIXED,STRONG[task],HELD):
                    events=row.get("faults",{}).get(name,[])
                    if len(events)!=2 or [x.get("step") for x in events]!=[2,3]:
                        raise ValueError("Primary real controller failed two prescribed native faults")
                    for e in events:
                        if (e.get("controller_execution_ack_seen_by_adapter")!="unknown"):
                            raise ValueError("Method was given secretly known physical delivery truth")
                        # FIXED special branch explicitly stores different
                        # postphysical audit keys for t3, never use either as
                        # policy input.
                        if name==FIXED and e["step"]==3:
                            matched=e.get("actual_native_execution_truth")==("applied" if truth(seed,3) else "held")
                        else:
                            matched=e.get("actual_native_precommitted_execution_truth")==("applied" if truth(seed,e["step"]) else "held")
                        if not matched:
                            raise ValueError("Original native executed/held physical step mismatches prereg")
                    neutral=row.get("known_delivered_zero_probe",{}).get(name)
                    if not neutral:
                        raise ValueError("Primary physical comparator missing known-delivered t4 public probe")
                # Other methods CAN terminate/refuse at t3; do not invent
                # t4 execution after episode termination. Original audit bug
                # rejected these physically legitimate failed methods.
                for name,probe in row["known_delivered_zero_probe"].items():
                    if name not in NAMES or probe.get("step")!=4 or probe.get("actual_native_6d_dispatched")!=[0.]*6 or probe.get("acknowledgement")!="known_applied" or probe.get("is_extra_common_physical_action") is not True or (name!="source_no_fault" and probe.get("audit_only_native_target_unchanged") is not True):
                        raise ValueError("Source attests an invalid extra physical probe")
                omitted=set(NAMES)-set(row["known_delivered_zero_probe"])
                for name in omitted:
                    if name in (PUBLIC,FIXED,STRONG[task],HELD):
                        raise ValueError("Primary method omitted added common probe")
                    fail=row.get("refusals",{}).get(name)
                    if (not fail or type(fail.get("step")) is not int or fail["step"]>4):
                        # An early official SUCCESS may terminate the source
                        # no-fault trajectory before t4 without a refusal.
                        if not (tasks[name] is True and row.get("steps",{}).get(name,50)<=4):
                            raise ValueError("Unexplained missing t4 probe: "+name)
                ev=row.get("public_t4_evidence",{})
                res=ev.get("candidate_residuals_m")
                accepted=ev.get("accepted_position_indices")
                if (type(res) is not list or type(accepted) is not list
                    or ev.get("physical_candidate_count")!=len(res)
                    or len(res) not in (2,3,4)
                    or ev.get("prior_training_epsilon_m")!=EPS[task]
                    or ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True
                    or any(type(x) not in (float,int) or not math.isfinite(x) or x<0 for x in res)):
                    raise ValueError("Missing full source public-only model/physics evidence")
                predicted=[i for i,z in enumerate(res) if z<=EPS[task]+1e-12]
                if accepted!=predicted:
                    raise ValueError("Original motion evidence inclusion changed")
                authorized=bool(len(predicted)==1 and all(d>EPS[task]+.002 for i,d in enumerate(res) if i!=predicted[0]))
                if ev.get("authorized") is not authorized:
                    raise ValueError("Original confident public motion authorization not reproducible")
                true=[i for i,(p,r) in enumerate(ev.get("after_physics_audit_pose_errors",[])) if p<=1e-4 and r<=1e-3]
                if true!=ev.get("audit_only_true_candidate_indices"):
                    raise ValueError("Original hidden-target audit truth changed")
                wrong=bool(authorized and predicted[0] not in true)
                if ev.get("wrong_confident") is not wrong:
                    raise ValueError("Hidden target truth score falsified")
                if row.get("public_motion_observation_cost_samples",{}).get(PUBLIC)!=2:
                    raise ValueError("Hidden missing public observation sample cost")
                if ev.get("resync_source")=="empirical_public_achieved_motion":
                    if not authorized or priv[PUBLIC]!=0:
                        raise ValueError("Public authorization spent hidden target getter")
                elif ev.get("resync_source")=="one_counted_authoritative_controller_target_read":
                    if authorized or priv[PUBLIC]!=1:
                        raise ValueError("Authoritative query not counted")
                elif ev.get("resync_source") is None:
                    if priv[PUBLIC]!=0:
                        raise ValueError("Unexecuted action/query fabricated")
                else:
                    raise ValueError("Invalid unknown native evidence source")
                rows.append(dict(seed=seed,task=task,
                    truth=("A" if truth(seed,2) else "H")+("A" if truth(seed,3) else "H"),
                    new_success=tasks[PUBLIC],strong_success=tasks[STRONG[task]],
                    fixed_success=tasks[FIXED],held_success=tasks[HELD],
                    new_reads=priv[PUBLIC],strong_reads=priv[STRONG[task]],
                    fixed_reads=priv[FIXED],held_reads=priv[HELD],
                    public_unique=authorized,wrong_confident=wrong,
                    nr_neutral_arms=len(row["known_delivered_zero_probe"]),
                    early_refusals=list(sorted(omitted))))
    if len(rows)!=64 or len({(x["task"],x["seed"]) for x in rows})!=64:
        raise ValueError("Not exactly 64 distinct precommitted source states")
    report={}
    for task in TASKS:
        for combo in ("AA","AH","HA","HH"):
            r=[x for x in rows if x["task"]==task and x["truth"]==combo]
            if len(r)!=8:
                raise ValueError("Joint truth population is incomplete/unbalanced")
            report[f"{task}:{combo}"]={
                "n":len(r),
                "new_success":sum(x["new_success"] for x in r),
                "strong_success":sum(x["strong_success"] for x in r),
                "fixed_success":sum(x["fixed_success"] for x in r),
                "zero_read_always_held_success":sum(x["held_success"] for x in r),
                "new_private_reads":sum(x["new_reads"] for x in r),
                "strong_private_reads":sum(x["strong_reads"] for x in r),
                "public_unique_full_history":sum(x["public_unique"] for x in r),
                "wrong_confident":sum(x["wrong_confident"] for x in r)}
    main={key:sum(r[key] for r in rows) for key in
          ("new_success","strong_success","fixed_success","held_success",
           "new_reads","strong_reads","fixed_reads","held_reads",
           "public_unique","wrong_confident")}
    pair={key:0 for key in ("both","new_only","strong_only","neither")}
    for r in rows:
        key="both" if r["new_success"] and r["strong_success"] else "new_only" if r["new_success"] else "strong_only" if r["strong_success"] else "neither"
        pair[key]+=1
    return {
        "schema":"independent_original_failed_CI_physx_source_only_four_joint_ACK_audit_v1",
        "original_physical_run_id":RUN_ID,
        "original_producer_CI_status":"failed ONLY after physical output, per-shard auditor refused legitimate early-stopped comparator",
        "original_executed_source_commit":SOURCE_EXECUTED_COMMIT,
        "protocol_git_blob":REGISTERED_PROTOCOL_GIT_BLOB,
        "method_git_blob":FROZEN_RUNNER_GIT_BLOB,
        "source_json_exact_sha256_manifest":manifest,
        "per_original_episode":rows,
        "per_task_four_physical_truth_strata":report,
        "total":main,
        "paired_success":pair,
        "physical_reset_states":64,
        "actually_physics_controller_worlds":576,
        "public_two_xyz_samples_per_new_trial":True,
        "known_t4_actuation_common_to_still_active_primary_controls":True,
        "literal_all_nine_t4_probes_not_met_due_to_early_refusals":True,
        "no_retraining_or_new_physx_after_original_source":True,
        "outside_replication":False,
        "not_hardware_or_collision_safety":True}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    data=external_original_source_audit(args.input)
    args.output.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("INDEPENDENT_SOURCE_AUDIT_FOUR_JOINT_ACK_64_PHYSICAL_PPO",json.dumps(
        {"total":data["total"],"paired":data["paired_success"],
         "strata":data["per_task_four_physical_truth_strata"],
         "failed_original_CI_but_original_physics_retained":True},sort_keys=True),flush=True)
if __name__=="__main__":
    main()
