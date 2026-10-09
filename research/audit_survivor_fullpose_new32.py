"""Zero-simulator-dependency independent original full native PhysX source auditor.

Never substitutes a source of selected task outcomes for real physical runs.
Every original paired task, private target-read count and public history
decision is verified from every source JSON. No drops on pre-fault failure.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from research.run_survivor_fullpose_new32 import (
    PUBLIC, SELECTIVE, FIXED, accepted, validate_result, PREREG,
    REGISTERED_BLOB, ORIGINAL_SOURCE_BLOB)

def original_complete_audit(folder:Path):
    expected={f"survivor_fullpose_{task}_chunk{chunk}_{kind}.json"
              for task in ("pull_cube","stack_cube") for chunk in range(4)
              for kind in ("original4","audit")}
    if {p.name for p in folder.glob("survivor_fullpose_*.json")}!=expected:
        raise ValueError("Missing actual original paired PhysX source shard/audit files")
    by_task={}
    all_pairs=[]
    for task in ("pull_cube","stack_cube"):
        stats={k:{"success":0,"private_reads":0} for k in
               ("new_public","task_preselected","fixed_t4","selective","zero_query")}
        traces=[];n=0;full_faults=0;wrong=0;unique=0;query_fallback=0;sampled=0
        for chunk in range(4):
            seeds=accepted(task,chunk)
            orig=folder/f"survivor_fullpose_{task}_chunk{chunk}_original4.json"
            summary=folder/f"survivor_fullpose_{task}_chunk{chunk}_audit.json"
            raw=orig.read_bytes()
            d=json.loads(raw)
            expected_summary=validate_result(d,task,seeds)
            stored=json.loads(summary.read_text())
            if (stored.get("schema")!="public_fourhistory_new32_shard_audit_v1"
                or stored.get("original_raw_sha256")!=hashlib.sha256(raw).hexdigest()
                or stored.get("frozen_prereg_blob")!=REGISTERED_BLOB
                or stored.get("source_runner_git_blob") is None
                or any(stored.get(k)!=v for k,v in expected_summary.items())):
                raise ValueError("Original physical shard and independent row audit disagree")
            gate=SELECTIVE if task=="pull_cube" else FIXED
            c=expected_summary["controls"]
            for name,control in (("new_public",PUBLIC),("task_preselected",gate),
                                 ("fixed_t4",FIXED),("selective",SELECTIVE),
                                 ("zero_query","fault_robust_two_history_without_query")):
                stats[name]["success"]+=c[control]["success"]
                stats[name]["private_reads"]+=c[control]["reads"]
            p=expected_summary["public"]
            n+=len(seeds)
            full_faults+=p["complete_fault_exposure"]
            wrong+=p["wrong_confident"]
            unique+=p["unique_history"]
            query_fallback+=p["fallback_authoritative"]
            sampled+=p["public_xyz_samples"]
            for row in expected_summary["sample_rows"]:
                traces.append(row)
                all_pairs.append(row)
        if len(traces)!=16 or [r["seed"] for r in traces]!=list(range(
                860001 if task=="pull_cube" else 870001,
                860017 if task=="pull_cube" else 870017)):
            raise ValueError("Original 16 task seeds not complete in task stratum")
        pair=dict(new_only=sum(r["new_success"] and not r["task_gate_success"] for r in traces),
                  task_gate_only=sum(r["task_gate_success"] and not r["new_success"] for r in traces),
                  both=sum(r["new_success"] and r["task_gate_success"] for r in traces),
                  neither=sum(not r["new_success"] and not r["task_gate_success"] for r in traces))
        by_task[task]=dict(reset_states=n,actual_native_physx_control_worlds=n*8,
                           outcomes=stats,paired_new_vs_task_gated=pair,
                           public_confident_authorizations=unique,
                           public_wrong_confident_authorizations=wrong,
                           public_authoritative_fallbacks=query_fallback,
                           public_xyz_sample_cost=sampled,
                           intended_double_fault_exposed=full_faults,
                           original_all_trial_rows=traces)
    if len(all_pairs)!=32 or len({(z["task"],z["seed"]) for z in all_pairs})!=32:
        raise ValueError("Not 32 distinct source reset identities")
    totals={name:{
         "success":sum(by_task[t]["outcomes"][name]["success"] for t in by_task),
         "privileged_reads":sum(by_task[t]["outcomes"][name]["private_reads"] for t in by_task)}
         for name in by_task["pull_cube"]["outcomes"]}
    pair={k:sum(by_task[t]["paired_new_vs_task_gated"][k] for t in by_task)
          for k in ("new_only","task_gate_only","both","neither")}
    if sum(pair.values())!=32:raise ValueError("Paired task outcomes incomplete")
    discordant=pair["new_only"]+pair["task_gate_only"]
    if discordant:
        tail=sum(math.comb(discordant,j) for j in range(min(
           pair["new_only"],pair["task_gate_only"])+1))
        exploratory_p=min(1.0,2*tail/2**discordant)
    else:
        exploratory_p=1.0
    return dict(schema="original_survivor_fullpose_new32_all_native_worlds_source_audit_v1",
                genuine_source_physx_reset_states=32,
                genuine_physics_controller_worlds=256,
                original_actual_frozen_ppo_policy_task_evaluation=True,
                matched_task_gated_baseline_physically_executed=True,
                published_PPO_unchanged=True,
                no_test_time_parameter_tuning=True,
                no_external_independent_lab_reproduction=True,
                unknown_ack_is_simulated_native_hold_not_network_packet=True,
                native_setpoint_certificate_not_collision_safety=True,
                prior_empirical_public_model_NOT_physical_guarantee=True,
                preregistration_sha=REGISTERED_BLOB,
                prior_original_source_blob=ORIGINAL_SOURCE_BLOB,
                double_fault_exposure_population=sum(
                    by_task[t]["intended_double_fault_exposed"] for t in by_task),
                complete_double_fault_gate_passes=all(
                    by_task[t]["intended_double_fault_exposed"]==16 for t in by_task),
                model_confident_wrong=sum(by_task[t]["public_wrong_confident_authorizations"] for t in by_task),
                public_confident_authorizations=sum(by_task[t]["public_confident_authorizations"] for t in by_task),
                public_observation_samples=sum(by_task[t]["public_xyz_sample_cost"] for t in by_task),
                paired_discordances=pair,
                exploratory_unadjusted_exact_p=exploratory_p,
                outcomes_total=totals,
                by_task=by_task)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    x=original_complete_audit(a.source_dir)
    a.output.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("SURVIVOR_FULLPOSE_REAL_PPO_ALL32_AUDIT",json.dumps({
       "total":x["outcomes_total"],"public_identifications":x["public_confident_authorizations"],
       "wrong_confident":x["model_confident_wrong"],
       "full_double_faults":x["double_fault_exposure_population"],
       "paired":x["paired_discordances"],"paired_p":x["exploratory_unadjusted_exact_p"],
       "complete_gate":x["complete_double_fault_gate_passes"]},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
