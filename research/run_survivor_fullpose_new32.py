"""Frozen public four-history UNKNOWN ACK PPO, actual 8-world real PhysX.

All original query comparators are separately actually executed; no
outcome-based splicing, test-time calibration, replay pretending to be PhysX,
or hidden target getter in new decision is allowed.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, os, subprocess, sys
from pathlib import Path

REGISTERED_BLOB="a51b01d66e2211058854015a31138f6a838eec71"
ORIGINAL_SOURCE_BLOB="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
FIRST={"pull_cube":860001,"stack_cube":870001}
PUBLIC="fault_public_t3_fourhistory_or_t4_query"
SELECTIVE="fault_robust_then_single_privileged_query"
FIXED="fault_always_single_privileged_query"
PREREG="research/SURVIVOR_CONDITIONED_SO3_NEW32_PRECOMMIT_V1.json"
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
    if p.get("schema")!="surviving_history_conditioned_full_pose_recovery_new32_v1":
        raise ValueError("Not original registered experiment identity")
    return p

def accepted(task,chunk):
    if task not in TASKS or type(chunk) is not int or chunk not in range(4):
        raise ValueError("Exactly 8 source-frozen 4-seed task shards required")
    return list(range(FIRST[task]+4*chunk,FIRST[task]+4*chunk+4))

def validate_result(d,task,seeds):
    expected=("source_no_fault","fault_oracle_private_target",
       "fault_optimistic_unverified_ack","fault_strict_common_exact",
       "fault_robust_two_history_without_query",
       "fault_robust_then_single_privileged_query",
       "fault_always_single_privileged_query",PUBLIC)
    if (d.get("schema")!="frozen_ppo_survivor_fullpose_t3_fourhistory_physx_v1"
        or d.get("preoutcome_protocol")!=PREREG
        or d.get("original_seed_population")!=seeds
        or d.get("task")!=TASKS[task]
        or d.get("all_eight_actual_control_arms")!=list(expected)
        or d.get("frozen_model_retrained") is not False
        or d.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT[task]
        or d.get("real_physx_simulator") is not True
        or d.get("two_consecutive_unknown_ack_target_hold_steps")!=[2,3]
        or len(d.get("episodes",[]))!=4):
        raise ValueError("Source run missing actual frozen PPO native controller worlds")
    routed=SELECTIVE if task=="pull_cube" else FIXED
    results={m:{"success":0,"reads":0} for m in expected if m!="fault_oracle_private_target"}
    confidence={"public_t3_exposure":0,"unique_history":0,
                "wrong_confident":0,"fallback_authoritative":0,
                "public_xyz_samples":0,"four_candidate_states":0,
                "complete_fault_exposure":0}
    rawrows=[]
    for seed,r in zip(seeds,d["episodes"]):
        if r.get("seed")!=seed:
            raise ValueError("Missing or reordered source native PPO PhysX seed")
        flags=r["success_once"]; reads=r["privileged_target_readback_decision_count"]
        if set(flags)!=set(expected) or set(reads)!=set(expected):
            raise ValueError("Missing original method paired PhysX task flags/reads")
        for m in results:
            if type(flags[m]) is not bool or type(reads[m]) is not int or not 0<=reads[m]<=1:
                raise ValueError("Wrong native task outcome or unlogged private controller reads")
            results[m]["success"]+=int(flags[m]);results[m]["reads"]+=reads[m]
        if reads["fault_oracle_private_target"]!=-1:
            raise ValueError("Unlimited oracle falsely counted as zero-read")
        ev=r.get("public_t3_evidence") or {}
        if ev:
            from research.survivor_full_pose_public_gate import (
                choose_full_pose_history_from_public_xyz)
            quats=ev.get("candidate_full_pose_quaternion_xyzw_from_ACTION_HISTORY")
            if not isinstance(quats,list):
                raise ValueError("Missing complete public action-history target rotations")
            selected=choose_full_pose_history_from_public_xyz(
                ev["candidate_residuals_m"],quats,ev["prior_training_epsilon_m"],
                historical_margin_m=.002,
                histories_complete=True,provenance_trusted=True,
                action_chart_verified=True)
            if selected!=ev.get("selection"):
                raise ValueError("Public-only FULL pose selection differs from frozen audited helper")
            if (ev.get("authorized") is not selected["authorized"]
                or ev.get("selected_candidate_index")!=selected["index"]
                or ev.get("position_identifies_ONE_complete_SE3_history_not_SO3_sensor") is not True):
                raise ValueError("Public winner or provenance changed")
            if selected["authorized"] and ev.get("wrong_confident") is None:
                raise ValueError("Missing independent after-physics full pose truth label")
        physical=r.get("faults",{}).get(PUBLIC,[])
        complete=len(physical)==2 and [z.get("step") for z in physical]==[2,3]
        confidence["complete_fault_exposure"]+=int(complete)
        if ev:
            if not complete:
                raise ValueError("Public read claimed but registered physical fault did not execute")
            if ev.get("physical_candidate_count") not in (2,3,4):
                raise ValueError("Incomplete post-native fault candidate set")
            if ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True:
                raise ValueError("Hidden controller target truth exposed to decision")
            if len(ev.get("candidate_residuals_m",[]))!=ev["physical_candidate_count"]:
                raise ValueError("Missing original source model residuals")
            authorized=ev.get("authorized")
            if type(authorized) is not bool:
                raise ValueError("Invalid original public decision")
            if authorized:
                if ev.get("resync_source") not in (None,"empirical_public_achieved_motion") or reads[PUBLIC]!=0:
                    raise ValueError("Public authorization falsely used private read")
            elif ev.get("resync_source")!= "one_counted_authoritative_controller_target_read" or reads[PUBLIC]!=1:
                # A trial can end after probe without reaching resync: do not
                # fabricate readback, score this as original stopped/unfinished.
                if ev.get("resync_source") is not None or reads[PUBLIC]!=0:
                    raise ValueError("Mismatched physical private readback ledger")
            confidence["public_t3_exposure"]+=1
            confidence["unique_history"]+=int(authorized)
            confidence["wrong_confident"]+=int(ev.get("wrong_confident") is True)
            confidence["fallback_authoritative"]+=int(ev.get("resync_source")=="one_counted_authoritative_controller_target_read")
            confidence["four_candidate_states"]+=int(ev.get("physical_candidate_count")==4)
        confidence["public_xyz_samples"]+=r.get("public_motion_observation_cost_samples",{}).get(PUBLIC,0)
        rawrows.append({"seed":seed,"task":task,"new_success":flags[PUBLIC],
                        "new_reads":reads[PUBLIC],
                        "task_gate_actual_world":routed,
                        "task_gate_success":flags[routed],
                        "task_gate_reads":reads[routed],
                        "fixed_success":flags[FIXED],
                        "fixed_reads":reads[FIXED],
                        "new_public_evidence":ev,
                        "new_public_fault_steps":[z.get("step") for z in physical]})
    return dict(task=task,seeds=seeds,controls=results,public=confidence,
                sample_rows=rawrows,expected_double_fault_in_all_new_arm_trials=
                confidence["complete_fault_exposure"]==4,
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
    runner=importlib.import_module("frozen_ppo_survivor_full_pose_new32")
    if (runner.TASK!=a.task or runner.TASK_NAME!=TASKS[a.task] or
        runner.FAULT_STEPS!=(2,3) or runner.HORIZON!=50 or
        runner.POS_BUDGET!=.05 or runner.ROT_BUDGET!=.05 or
        runner.PUBLIC_ARM!=PUBLIC or runner.PROTO!=PREREG or
        len(runner.NAMES)!=8):
        raise RuntimeError("Frozen real PhysX source/chart/query contract changed")
    runner.SEEDS=seeds
    runner.COHORT[a.task]=(TASKS[a.task],seeds)
    runner.main()  # Every one of 8 native PhysX comparators REALLY executes.
    path=Path(f"public_fourhistory_{a.task}_original4.json")
    raw=path.read_bytes()
    d=json.loads(raw)
    s=validate_result(d,a.task,seeds)
    s.update(schema="public_fourhistory_new32_shard_audit_v1",
             original_raw_sha256=hashlib.sha256(raw).hexdigest(),
             frozen_prereg_blob=REGISTERED_BLOB,
             source_runner_git_blob=blob("research/frozen_ppo_survivor_full_pose_new32.py"))
    Path(f"survivor_fullpose_{a.task}_chunk{a.chunk}_audit.json").write_text(
        json.dumps(s,indent=2,sort_keys=True)+"\n")
    path.rename(f"survivor_fullpose_{a.task}_chunk{a.chunk}_original4.json")
    print("TRUE_NATIVE_PPO_SURVIVOR_FULLPOSE_SHARD",json.dumps({
        "task":a.task,"chunk":a.chunk,"new":s["controls"][PUBLIC],
        "strong_task_gate":s["controls"][SELECTIVE if a.task=="pull_cube" else FIXED],
        "public":s["public"],"source_seeds":seeds},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
