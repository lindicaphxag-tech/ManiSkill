"""Prospective pilot: 16 new real frozen PPO states per task, 11 true
independently PhysX-stepped native controller worlds per new seed.

PILOT is a method falsifier, NOT a positive confirmatory main-conference study.
Original physical source JSON is written BEFORE independent source audit.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,math,os,subprocess,sys
from pathlib import Path

TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
FIRST={"pull_cube":1200101,"stack_cube":1210101}
PREREG="research/CAUSAL_NONZERO_NATIVE_PROBE_PILOT32_PREOUTCOME_V1.json"
PREREG_BLOB="5ddc259ddebbc7d3a486c56bbf53d806f00de64b"
SOURCE="research/frozen_ppo_causal_nonzero_probe_pilot_v7.py"
SOURCE_BLOB="9cdb5e107ca2f6a60d447f0ec47fbc60047d868e"
BASELINE_SOURCE="research/frozen_ppo_compound_ack_multi_belief.py"
BASELINE_BLOB="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
CHECKPOINT={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
            "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
PASSIVE="fault_public_t4_zero_or_t5_query"
ACTIVE="fault_public_t4_nonzero_or_t5_query"
QUERY="fault_public_t4_nonzero_always_private_read_t5"
OTHER=("source_no_fault","fault_oracle_private_target",
       "fault_optimistic_unverified_ack","fault_strict_common_exact",
       "fault_robust_two_history_without_query",
       "fault_robust_then_single_privileged_query",
       "fault_always_single_privileged_query","fault_assume_held_without_query")
NAMES=OTHER+(PASSIVE,ACTIVE,QUERY)
EXPECTED_T4_NONZERO=(.12,-.09,.07,0.,0.,0.)
OLD_EPS={"pull_cube":.006944262561376447,"stack_cube":.00719087965534261}

def blob(p):
    return subprocess.check_output(["git","hash-object",str(p)],text=True).strip()

def check_sources():
    for path,expected in ((PREREG,PREREG_BLOB),(SOURCE,SOURCE_BLOB),
                          (BASELINE_SOURCE,BASELINE_BLOB)):
        got=blob(path)
        if got!=expected:
            raise RuntimeError("Registered PHYSICAL original source identity drift: "+path+
                               " expected="+expected+" actual="+got)
    j=json.loads(Path(PREREG).read_text())
    if j["schema"]!="prospective_32_state_active_native_nonzero_vs_passive_zero_ack_real_PPO_v1":
        raise RuntimeError("Registered prospective 32 source physical protocol changed")
    return j

def new_seeds(task,chunk):
    if task not in TASKS or type(chunk) is not int or chunk not in (0,1):
        raise ValueError("Exactly two 8-state pilot shards per frozen PPO task")
    a=FIRST[task]+chunk*8
    return list(range(a,a+8))

def audit_pilot_shard(data,task,seeds):
    if (data.get("schema")!="frozen_ppo_pilot_nonzero_native_probe_vs_zero_physx_v7" or
        data.get("preoutcome_protocol")!=PREREG or
        data.get("task")!=TASKS[task] or
        data.get("original_seed_population")!=seeds or
        data.get("all_eleven_actual_control_arms")!=list(NAMES) or
        data.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT[task] or
        data.get("frozen_model_retrained") is not False or
        data.get("real_physx_simulator") is not True or
        len(data.get("episodes",[]))!=8):
        raise ValueError("Real native original 11 method benchmark missing or false provenance")
    def close3(x,y):
        return math.dist(x,y)
    out=[]
    gate=("fault_robust_then_single_privileged_query" if task=="pull_cube"
          else "fault_always_single_privileged_query")
    for seed,row in zip(seeds,data["episodes"]):
        if (row.get("seed")!=seed or
            row.get("original_precommitted_physical_t2_execution_truth")!=(
                "applied" if seed%2==0 else "held") or
            row.get("original_precommitted_physical_t3_execution_truth")!=(
                "applied" if (seed//2)%2==0 else "held")):
            raise ValueError("Actual physics fault truth not committed before true rollouts")
        success=row.get("success_once",{})
        queries=row.get("privileged_target_readback_decision_count",{})
        if set(success)!=set(NAMES) or set(queries)!=set(NAMES):
            raise ValueError("Original physically stepped 11-method task outcome labels missing")
        for n in NAMES:
            if type(success[n]) is not bool or type(queries[n]) is not int:
                raise ValueError("Original source not binary official task success and integer query ledger")
            if n=="fault_oracle_private_target":
                if queries[n]!=-1:raise ValueError("Unrestricted oracle misreported")
            elif queries[n] not in (0,1):
                raise ValueError("No method may silently consume multiple private target reads")
        if queries[QUERY]!=1:
            raise ValueError("Physically matched nonzero t4 comparator must query ONCE at t5")
        neutral=row.get("known_delivered_t4_probe",{})
        for n in (PASSIVE,ACTIVE,QUERY,gate):
            e=neutral.get(n)
            if not e or e.get("step")!=4 or e.get("acknowledgement")!="known_applied":
                raise ValueError("Not physically matched t4 arm probe exposure")
            expected=list(EXPECTED_T4_NONZERO if n in (ACTIVE,QUERY) else (0.,)*6)
            actual=e.get("physically_sent_native_arm_6d")
            if (len(actual)!=6 or max(abs(x-y) for x,y in zip(actual,expected))>1e-6
                or e.get("is_actively_nonzero_native_arm_motion") is not (n in (ACTIVE,QUERY))):
                raise ValueError("Recorded native active probe does not match FROZEN original action contract")
            if (e.get("actual_physx_step_executed") is not True or
                e.get("no_hidden_target_getter_used_by_policy") is not True or
                not math.isfinite(e["actual_achieved_public_xyz_displacement_m"])):
                raise ValueError("Probe not physically executed or private state was used to choose it")
            if n in (ACTIVE,QUERY) and e.get("audit_only_actual_target_position_change_inf_m",0.)<1e-5:
                raise ValueError("Actual native t4 target did NOT move despite registered nonzero intervention")
        for n in (PASSIVE,ACTIVE,QUERY,gate):
            events=row.get("faults",{}).get(n,[])
            if [e.get("step") for e in events]!=[2,3]:
                raise ValueError("Unexposed double unknown ACK: "+n)
            if [e.get("actual_native_action_is_precommitted_applied") for e in events]!=[
                seed%2==0,(seed//2)%2==0]:
                raise ValueError("Fault executor peeked at/overrode wrong precommitted physical ACK")
            if any(e.get("controller_execution_ack_seen_by_adapter")!="unknown" for e in events):
                raise ValueError("Physical ACK truth LEAKED to public decision")
        evs=row["public_t4_evidence"]
        if set(evs)!={PASSIVE,ACTIVE}:
            raise ValueError("Missing true native public before/after tool observations")
        for n in (PASSIVE,ACTIVE):
            ev=evs[n]
            ds=ev.get("candidate_residuals_m",[])
            eps=OLD_EPS[task]
            if (len(ds) not in (2,3,4) or
                len(ev.get("after_physics_audit_pose_errors",[]))!=len(ds)
                or len(ev.get("accepted_position_indices",[]))>len(ds)
                or ev.get("prior_training_epsilon_m")!=eps
                or ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True
                or row["public_motion_observation_cost_samples"][n]!=2):
                raise ValueError("Public motion rule/hidden target provenance not auditable")
            if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in ds):
                raise ValueError("Nonfinite empirical physical response score")
            truth=[i for i,(p,r) in enumerate(ev["after_physics_audit_pose_errors"])
                   if p<=1e-4 and r<=1e-3]
            if len(truth)!=1 or truth!=ev["audit_only_true_candidate_indices"]:
                raise ValueError("Actual native postprobe target NOT among full target belief or corrupt audit")
            accepted=[i for i,d in enumerate(ds) if d<=eps+1e-12]
            authorize=bool(len(accepted)==1 and all(
                x>eps+.002 for i,x in enumerate(ds) if i!=accepted[0]))
            if accepted!=ev["accepted_position_indices"] or authorize is not ev["authorized"]:
                raise ValueError("Native public score did not determine accepted full history")
            wrong=bool(authorize and accepted[0] not in truth)
            if wrong is not ev["wrong_confident"]:
                raise ValueError("Hidden after-physics native target error dishonestly labeled")
            if ev.get("resync_source")=="empirical_public_achieved_motion":
                if not authorize or queries[n]!=0: raise ValueError("Public method hid getter")
            elif ev.get("resync_source")=="one_counted_authoritative_controller_target_read":
                if authorize or queries[n]!=1: raise ValueError("Public fallback getter not counted")
            else:raise ValueError("Public source incorrectly terminated or private getter mislabeled")
            before=ev["before_xyz"];after=ev["after_xyz"]
            if (len(before)!=3 or len(after)!=3 or
                abs(close3(before,after)-neutral[n]["actual_achieved_public_xyz_displacement_m"])>1e-6):
                raise ValueError("Actual PhysX achieved motion cost mismatches public trace")
        out.append({
            "seed":seed,"task":task,
            "truth":("A" if seed%2==0 else "H")+("A" if (seed//2)%2==0 else "H"),
            "passive_success":success[PASSIVE],"active_success":success[ACTIVE],
            "active_always_query_success":success[QUERY],
            "strong_task_gate_success":success[gate],
            "passive_private_reads":queries[PASSIVE],
            "active_private_reads":queries[ACTIVE],
            "active_always_query_private_reads":queries[QUERY],
            "strong_private_reads":queries[gate],
            "passive_authorized":evs[PASSIVE]["authorized"],
            "active_authorized":evs[ACTIVE]["authorized"],
            "passive_wrong_confident":evs[PASSIVE]["wrong_confident"],
            "active_wrong_confident":evs[ACTIVE]["wrong_confident"],
            "passive_public_tool_achieved_xyz_displacement_m":
                neutral[PASSIVE]["actual_achieved_public_xyz_displacement_m"],
            "active_public_tool_achieved_xyz_displacement_m":
                neutral[ACTIVE]["actual_achieved_public_xyz_displacement_m"],
            "active_native_target_probe_position_displacement_inf_m":
                neutral[ACTIVE]["audit_only_actual_target_position_change_inf_m"],
            "active_query_native_target_probe_position_displacement_inf_m":
                neutral[QUERY]["audit_only_actual_target_position_change_inf_m"]
        })
    if len(out)!=8:raise ValueError("Source physical eight episode shard missing")
    total={name:sum(int(row[name]) for row in out)
           for name in ("passive_success","active_success","active_always_query_success",
                        "strong_task_gate_success","passive_private_reads",
                        "active_private_reads","active_always_query_private_reads",
                        "passive_authorized","active_authorized",
                        "passive_wrong_confident","active_wrong_confident")}
    return {"schema":"prospective_nonzero_native_probe_physical_source_auditor_v1",
            "task":task,"seeds":seeds,"original_all_task_rows":out,
            "total":total,"actual_native_PHYSX_controller_worlds":88,
            "native_6d_nonzero_action_FROZEN_before_outcomes":list(EXPECTED_T4_NONZERO),
            "no_hardware_collision_or_force_safety_certificate":True,
            "original_source_independent_of_review_posthypothesis":True}

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--task",required=True,choices=tuple(TASKS))
    arg.add_argument("--chunk",type=int,required=True,choices=(0,1))
    a=arg.parse_args()
    check_sources()
    seeds=new_seeds(a.task,a.chunk)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    policy=importlib.import_module("frozen_ppo_causal_nonzero_probe_pilot_v7")
    if (policy.TASK!=a.task or list(policy.FAULT_STEPS)!=[2,3] or
        len(policy.NAMES)!=11 or policy.PROTO!=PREREG or
        policy.NARROW_ARM!=PASSIVE or policy.PUBLIC_ARM!=ACTIVE or
        policy.QUERY_ARM!=QUERY or
        tuple(policy.FIXED_ACTIVE_NORMALIZED_6D)!=EXPECTED_T4_NONZERO):
        raise RuntimeError("Method drift or incorrect original actual probe after preregistration")
    policy.SEEDS=seeds
    policy.COHORT[a.task]=(TASKS[a.task],seeds)
    policy.main()  # writes actual real unchanged source original PHYXS JSON
    filename=Path(f"active_nonzero_pilot_{a.task}_original8.json")
    raw=filename.read_bytes()
    source=json.loads(raw)
    out=audit_pilot_shard(source,a.task,seeds)
    out.update({
        "original_byte_identical_physics_source_sha256":hashlib.sha256(raw).hexdigest(),
        "method_native_git_blob":SOURCE_BLOB,
        "source_prereg_git_blob":PREREG_BLOB})
    Path(f"active_nonzero_pilot_{a.task}_chunk{a.chunk}_audit.json").write_text(
        json.dumps(out,sort_keys=True,indent=2)+"\n")
    filename.rename(f"active_nonzero_pilot_{a.task}_chunk{a.chunk}_original8.json")
    print("ACTUALLY_PHYSX_STEPPED_NONZERO_ACK_INTERVENTION_PILOT",
          json.dumps({"task":a.task,"chunk":a.chunk,"total":out["total"],
                      "source_seeds":seeds},sort_keys=True),flush=True)
if __name__=="__main__":
    main()
