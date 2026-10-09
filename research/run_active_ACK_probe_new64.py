"""REAL pre-registered new64 frozen PPO PhysX: 11 separately-stepped matched
controller worlds/seed, exactly ONE native t4 probe action per active world.

This is NOT a faithful ActionShift baseline. Source method is an independently
physically realized finite-history target-memory probe with legitimate action
amplitude and cost, not offline model counterfactual interpolation.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,math,os,subprocess,sys
from pathlib import Path
PROTOCOL="research/ACTIVE_ACK_PROBE_NATIVE_NEW64_PREOUTCOME_V1.json"
PROTOCOL_BLOB="ddd392a31424d0d0067107ed314d76966c59eace"
SOURCE="research/frozen_ppo_costed_active_ACK_probe_physx_v5.py"
SOURCE_BLOB="1944d94bbde25397de5ec2b07910d2e210043bb9"
NATIVE_HISTORY="research/frozen_ppo_compound_ack_multi_belief.py"
NATIVE_HISTORY_BLOB="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
PLANNER="research/public_ack_costed_probe_planner.py"
PLANNER_BLOB="0aabc71e166fd515d9f7e58122bff7f913fc0cdb"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
FIRST={"pull_cube":980201,"stack_cube":990201}
CKPT={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
      "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
ZERO="fault_public_t4_zero_or_t5_query"
FIXED="fault_public_t4_fixed_pulse_or_t5_query"
ACTIVE="fault_public_t4_active_pulse_or_t5_query"
ARMS=(ZERO,FIXED,ACTIVE)
FROZEN_EPS={"pull_cube":.006944262561376447,"stack_cube":.00719087965534261}
EXPECTED=("source_no_fault","fault_oracle_private_target",
          "fault_optimistic_unverified_ack","fault_strict_common_exact",
          "fault_robust_two_history_without_query",
          "fault_robust_then_single_privileged_query",
          "fault_always_single_privileged_query",
          "fault_assume_held_without_query")+ARMS

def blob(path):
    return subprocess.check_output(["git","hash-object",path],text=True).strip()

def check_source():
    for path,pin in ((PROTOCOL,PROTOCOL_BLOB),(SOURCE,SOURCE_BLOB),
                     (NATIVE_HISTORY,NATIVE_HISTORY_BLOB),(PLANNER,PLANNER_BLOB)):
        if blob(path)!=pin:
            raise RuntimeError("Pre-outcome source code or registration CHANGED: "+path)
    protocol=json.loads(Path(PROTOCOL).read_text())
    if protocol["schema"]!="preoutcome_new64_true_PhysX_one_step_active_vs_fixed_vs_passive_ACK_probe_v1":
        raise ValueError("Not our frozen protocol")
    if protocol["physics"]["nMethods"]!=11 or protocol["physics"]["totalGenuineControllerWorlds"]!=704:
        raise ValueError("Population count changed after prospective source gate")

def original_seeds(task,chunk):
    if task not in TASKS or type(chunk)!=int or chunk not in range(4):
        raise ValueError("Bad declared task or chunk")
    return list(range(FIRST[task]+8*chunk,FIRST[task]+8*chunk+8))

def validate_original(obj,task,seeds):
    if (obj.get("schema")!="frozen_PPO_physical_costed_true_ACK_active_fixed_passive_probes_v5"
        or obj.get("preoutcome_protocol")!=PROTOCOL
        or obj.get("task")!=TASKS[task]
        or obj.get("original_seed_population")!=seeds
        or obj.get("real_physx_simulator") is not True
        or obj.get("frozen_model_retrained") is not False
        or obj.get("original_external_frozen_checkpoint_sha256")!=CKPT[task]
        or obj.get("all_eleven_actual_control_arms")!=list(EXPECTED)
        or len(obj.get("episodes",[]))!=8):
        raise ValueError("Not original 8 genuinely stepped source PPO physical worlds")

    rows=[]
    for seed,r in zip(seeds,obj["episodes"]):
        if r.get("seed")!=seed:raise ValueError("Wrong reset seed order in original PhysX trial")
        actual_t2=(seed%2==0)
        actual_t3=((seed//2)%2==0)
        if (r["original_precommitted_physical_t2_execution_truth"]!=("applied" if actual_t2 else "held")
            or r["original_precommitted_physical_t3_execution_truth"]!=("applied" if actual_t3 else "held")):
            raise ValueError("Actual physical fault scheduling was changed")
        info=r.get("known_delivered_zero_probe",{})
        successes=r.get("success_once",{})
        queries=r.get("privileged_target_readback_decision_count",{})
        if set(successes)!=set(EXPECTED) or set(queries)!=set(EXPECTED):
            raise ValueError("Missing independent real controller world")
        for name in EXPECTED:
            if type(successes[name]) is not bool or type(queries[name]) is not int:
                raise ValueError("Not genuine official task success Boolean / cost ledger")
            if name=="fault_oracle_private_target":
                if queries[name]!=-1:raise ValueError("Oracle privacy measurement changed")
            elif queries[name] not in (0,1):
                raise ValueError("Expected 0 or 1 privileged decision target reads")
        for name in ARMS:
            faults=r["faults"].get(name,[])
            if len(faults)!=2 or [z["step"] for z in faults]!=[2,3]:
                raise ValueError("Missing either actual native fault")
            if any(x["controller_execution_ack_seen_by_adapter"]!="unknown" for x in faults):
                raise ValueError("Hidden true ACK leaked into controller")
            if [x["actual_native_precommitted_execution_truth"] for x in faults]!=[
                    "applied" if actual_t2 else "held",
                    "applied" if actual_t3 else "held"]:
                raise ValueError("Actual applied-vs-held physical truth inconsistent")
            p=info.get(name)
            if p is None or p["step"]!=4 or p["acknowledgement"]!="known_applied":
                raise ValueError("Missing one exactly known-delivered real t4 probe")
            native=p["actual_native_6d_dispatched"]
            if not isinstance(native,list) or len(native)!=6 or any(
                    not math.isfinite(float(z)) or abs(float(z))>1.0001 for z in native):
                raise ValueError("Physical native probe command not a valid normalized 6d vector")
            norm=math.sqrt(sum(float(z)**2 for z in native[:3]))
            if (abs(norm-(0. if name==ZERO else .12))>1e-6 or native[3:]!=[0.]*3):
                raise ValueError("Native probe amplitude/rotation budget altered")
            if name==ZERO and (p["hypothesis_updated_for_known_t4"] is not False or
                               native!=[0.]*6):
                raise ValueError("Passive controller was secretly probed")
            if name in (FIXED,ACTIVE) and p["hypothesis_updated_for_known_t4"] is not True:
                raise ValueError("Pulse controller did not advance ALL native target-memory hypotheses")
            if name==FIXED and any(abs(a-b)>1e-6 for a,b in zip(native,[.12,0,0,0,0,0])):
                raise ValueError("Fixed-probe control not physically fixed")
            if name==ACTIVE and p["native_probe_selector"]!="min_directed_segment_maxmin":
                raise ValueError("Active probing selector violated preregistered public-only heuristic")
            ev=r["public_t4_evidence"][name]
            if ev["audit_only_hidden_target_was_NOT_decision_input"] is not True:
                raise ValueError("Actual private controller target leak")
            if ev["prior_training_epsilon_m"]!=FROZEN_EPS[task]:
                raise ValueError("Adaptive method tuned old native model on NEW outcomes")
            candidates=ev["candidate_residuals_m"]
            if not(2<=len(candidates)<=4) or ev["physical_candidate_count"]!=len(candidates):
                raise ValueError("Post-physical active belief candidate set invalid")
            fit=[i for i,x in enumerate(candidates) if x<=FROZEN_EPS[task]+1e-12]
            admit=bool(len(fit)==1 and all(x>FROZEN_EPS[task]+.002
                for i,x in enumerate(candidates) if i!=fit[0]))
            if ev["accepted_position_indices"]!=fit or ev["authorized"] is not admit:
                raise ValueError("Active public witness scoring not reproducible")
            audit_true=[i for i,(a,b) in enumerate(ev["after_physics_audit_pose_errors"])
                        if a<=1e-4 and b<=1e-3]
            if audit_true!=ev["audit_only_true_candidate_indices"] or len(audit_true)!=1:
                raise ValueError("Actual PhysX native remembered target not in hypothesis set")
            wrong=bool(admit and fit[0] not in audit_true)
            if ev["wrong_confident"] is not wrong:
                raise ValueError("False physical hidden target confidence scored incorrectly")
            pre=ev["before_xyz"];after=ev["after_xyz"]
            displacement=math.sqrt(sum((a-b)**2 for a,b in zip(pre,after)))
            if abs(displacement-ev["actual_public_xyz_displacement_m"])>1e-6:
                raise ValueError("Uncharged actual public robot movement")
            if r["public_motion_observation_cost_samples"][name]!=2:
                raise ValueError("Public sensing budget differs among probe families")
            if ev.get("resync_source")=="empirical_public_achieved_motion" and (
                not admit or queries[name]!=0):
                raise ValueError("Public guess silently used trusted hidden state")
            if ev.get("resync_source")=="one_counted_authoritative_controller_target_read" and (
                admit or queries[name]!=1):
                raise ValueError("Query not honestly paid for")
            if ev.get("resync_source") not in (
                    None,"empirical_public_achieved_motion","one_counted_authoritative_controller_target_read"):
                raise ValueError("Invented native-state evidence source")
        rows.append(dict(seed=seed,task=task,
            actual_joint_ACK=("A" if actual_t2 else "H")+("A" if actual_t3 else "H"),
            per_method={name:dict(success=successes[name],
                privileged_reads=queries[name],
                authorized=r["public_t4_evidence"][name]["authorized"],
                wrong_confident=r["public_t4_evidence"][name]["wrong_confident"],
                native_action=r["known_delivered_zero_probe"][name]["actual_native_6d_dispatched"],
                public_displacement_m=r["public_t4_evidence"][name]["actual_public_xyz_displacement_m"],
                public_samples=r["public_motion_observation_cost_samples"][name])
                for name in ARMS},
            task_gate_success=successes[
                "fault_robust_then_single_privileged_query" if task=="pull_cube"
                else "fault_always_single_privileged_query"],
            task_gate_reads=queries[
                "fault_robust_then_single_privileged_query" if task=="pull_cube"
                else "fault_always_single_privileged_query"]))
    return dict(schema="genuine_original_native_physx_active_fixed_passive_source_audit_v1",
                task=task,original_reset_states=seeds,
                actual_physically_stepped_independent_controller_worlds=88,
                source_original_8_episodes=rows,not_from_model_proxy=True,
                original_native_PPO_no_retraining=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--task",choices=tuple(TASKS),required=True)
    parser.add_argument("--chunk",type=int,choices=range(4),required=True)
    a=parser.parse_args()
    check_source()
    seeds=original_seeds(a.task,a.chunk)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_costed_active_ACK_probe_physx_v5")
    if (runner.TASK!=a.task or runner.PROTO!=PROTOCOL
        or len(runner.NAMES)!=11 or runner.PUBLIC_ARM!=ACTIVE
        or runner.FIXED_PULSE_ARM!=FIXED or runner.ZERO_PUBLIC_ARM!=ZERO
        or tuple(runner.FAULT_STEPS)!=(2,3)):
        raise RuntimeError("Source native robot/controller or code changed")
    runner.SEEDS=seeds
    runner.COHORT[a.task]=(TASKS[a.task],seeds)
    runner.main() # 8 ORIGINAL reset tasks × 11 independently stepped real PhysX worlds
    original=Path(f"active_probe_{a.task}_original8.json")
    raw=original.read_bytes()
    d=json.loads(raw)
    audit=validate_original(d,a.task,seeds)
    audit["source_original_JSON_sha256"]=hashlib.sha256(raw).hexdigest()
    audit["registered_before_physical_source_blob"]=SOURCE_BLOB
    (Path(f"active_probe_{a.task}_chunk{a.chunk}_audit.json")).write_text(
        json.dumps(audit,indent=2,sort_keys=True)+"\n")
    original.rename(f"active_probe_{a.task}_chunk{a.chunk}_original8.json")
    print("ORIGINAL_REAL_PHYXS_11_COSTED_PROBE_CONTROLLERS",json.dumps({
        "task":a.task,"chunk":a.chunk,
        "n_actual_physically_executed_original_state_worlds":88,
        "probe_successes":{n:sum(
          x["per_method"][n]["success"] for x in audit["source_original_8_episodes"])
          for n in ARMS},
        "probe_reads":{n:sum(
          x["per_method"][n]["privileged_reads"] for x in audit["source_original_8_episodes"])
          for n in ARMS},
        "wrong_native_targets":{n:sum(
          x["per_method"][n]["wrong_confident"] for x in audit["source_original_8_episodes"])
          for n in ARMS},
    },sort_keys=True))
if __name__=="__main__":main()
