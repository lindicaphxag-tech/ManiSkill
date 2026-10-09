"""Zero-simulator-dependency independent original full native PhysX source auditor.

Never substitutes a source of selected task outcomes for real physical runs.
Every original paired task, private target-read count and public history
decision is verified from every source JSON. No drops on pre-fault failure.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from research.run_full_joint_ack_new64 import (
    PUBLIC, SELECTIVE, FIXED, accepted, validate_result, PREREG,
    REGISTERED_BLOB, ORIGINAL_SOURCE_BLOB)

def original_complete_audit(folder:Path):
    expected={f"full_joint_ack_{task}_chunk{chunk}_{kind}.json"
              for task in ("pull_cube","stack_cube") for chunk in range(4)
              for kind in ("original8","audit")}
    if {p.name for p in folder.glob("full_joint_ack_*.json")}!=expected:
        raise ValueError("Missing actual original paired PhysX source shard/audit files")
    by_task={}
    all_pairs=[]
    for task in ("pull_cube","stack_cube"):
        stats={k:{"success":0,"private_reads":0} for k in
               ("new_public","task_preselected","fixed_t5","selective","zero_query","always_assume_held")}
        traces=[];n=0;full_faults=0;wrong=0;unique=0;query_fallback=0;sampled=0
        phys_truth={"t2_applied":0,"t2_held":0,"t3_applied":0,"t3_held":0}
        joint_truth={k:0 for k in ("AA","AH","HA","HH")}
        count_common_t4_probes=0
        strata={k:{"n":0,"new_success":0,"strong_success":0,"held_success":0,"new_reads":0,"strong_reads":0,"held_reads":0,
                   "unique":0,"wrong":0} for k in ("AA","AH","HA","HH")}
        for chunk in range(4):
            seeds=accepted(task,chunk)
            orig=folder/f"full_joint_ack_{task}_chunk{chunk}_original8.json"
            summary=folder/f"full_joint_ack_{task}_chunk{chunk}_audit.json"
            raw=orig.read_bytes()
            d=json.loads(raw)
            expected_summary=validate_result(d,task,seeds)
            stored=json.loads(summary.read_text())
            if (stored.get("schema")!="full_joint_ack_new64_shard_source_audit_v1"
                or stored.get("original_raw_sha256")!=hashlib.sha256(raw).hexdigest()
                or stored.get("frozen_prereg_blob")!=REGISTERED_BLOB
                or stored.get("source_runner_git_blob") is None
                or any(stored.get(k)!=v for k,v in expected_summary.items())):
                raise ValueError("Original physical shard and independent row audit disagree")
            gate=SELECTIVE if task=="pull_cube" else FIXED
            c=expected_summary["controls"]
            for name,control in (("new_public",PUBLIC),("task_preselected",gate),
                                 ("fixed_t5",FIXED),("selective",SELECTIVE),
                                 ("zero_query","fault_robust_two_history_without_query"),
                                 ("always_assume_held","fault_assume_held_without_query")):
                stats[name]["success"]+=c[control]["success"]
                stats[name]["private_reads"]+=c[control]["reads"]
            p=expected_summary["public"]
            n+=len(seeds)
            full_faults+=p["complete_fault_exposure"]
            wrong+=p["wrong_confident"]
            unique+=p["unique_history"]
            query_fallback+=p["fallback_authoritative"]
            sampled+=p["public_xyz_samples"]
            for axis in ("t2_applied","t2_held","t3_applied","t3_held"):
                phys_truth[axis]+=p[axis]
            for combo,n_combo in p["joint_truth_counts"].items():
                joint_truth[combo]+=n_combo
            count_common_t4_probes+=p["known_t4_zero_probe"]
            for row in expected_summary["sample_rows"]:
                traces.append(row)
                all_pairs.append(row)
                label=("A" if row["seed"]%2==0 else "H")+("A" if (row["seed"]//2)%2==0 else "H")
                st=strata[label]
                st["n"]+=1
                st["new_success"]+=int(row["new_success"])
                st["strong_success"]+=int(row["task_gate_success"])
                st["new_reads"]+=row["new_reads"]
                st["strong_reads"]+=row["task_gate_reads"]
                ev=row["new_public_evidence"]
                st["unique"]+=int(ev.get("authorized") is True)
                st["wrong"]+=int(ev.get("wrong_confident") is True)
                original_control=next(z for z in
                    json.loads((folder/f"full_joint_ack_{task}_chunk{chunk}_original8.json").read_text())["episodes"]
                    if z["seed"]==row["seed"])
                baseline="fault_assume_held_without_query"
                st["held_success"]+=int(original_control["success_once"][baseline])
                st["held_reads"]+=original_control["privileged_target_readback_decision_count"][baseline]
        if len(traces)!=32 or [r["seed"] for r in traces]!=list(range(
                880001 if task=="pull_cube" else 890001,
                880033 if task=="pull_cube" else 890033)):
            raise ValueError("Original 16 task seeds not complete in task stratum")
        pair=dict(new_only=sum(r["new_success"] and not r["task_gate_success"] for r in traces),
                  task_gate_only=sum(r["task_gate_success"] and not r["new_success"] for r in traces),
                  both=sum(r["new_success"] and r["task_gate_success"] for r in traces),
                  neither=sum(not r["new_success"] and not r["task_gate_success"] for r in traces))
        by_task[task]=dict(reset_states=n,actual_native_physx_control_worlds=n*9,
                           outcomes=stats,paired_new_vs_task_gated=pair,
                           public_confident_authorizations=unique,
                           public_wrong_confident_authorizations=wrong,
                           public_authoritative_fallbacks=query_fallback,
                           public_xyz_sample_cost=sampled,
                           intended_double_fault_exposed=full_faults,
                           original_all_trial_rows=traces,
                           physical_joint_truth_populations=joint_truth,
                           ack_truth_axis_counts=phys_truth,
                           common_known_t4_probe_exposures=count_common_t4_probes,
                           actual_joint_truth_stratified_results=strata)
    if len(all_pairs)!=64 or len({(z["task"],z["seed"]) for z in all_pairs})!=64:
        raise ValueError("Not 32 distinct source reset identities")
    totals={name:{
         "success":sum(by_task[t]["outcomes"][name]["success"] for t in by_task),
         "privileged_reads":sum(by_task[t]["outcomes"][name]["private_reads"] for t in by_task)}
         for name in by_task["pull_cube"]["outcomes"]}
    pair={k:sum(by_task[t]["paired_new_vs_task_gated"][k] for t in by_task)
          for k in ("new_only","task_gate_only","both","neither")}
    if sum(pair.values())!=64:raise ValueError("Paired task outcomes incomplete")
    discordant=pair["new_only"]+pair["task_gate_only"]
    if discordant:
        tail=sum(math.comb(discordant,j) for j in range(min(
           pair["new_only"],pair["task_gate_only"])+1))
        exploratory_p=min(1.0,2*tail/2**discordant)
    else:
        exploratory_p=1.0
    return dict(schema="original_both_ACK_joint_truth_new64_native_source_audit_v1",
                genuine_source_physx_reset_states=64,
                genuine_physics_controller_worlds=576,
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
                    by_task[t]["intended_double_fault_exposed"]==32 for t in by_task),
                model_confident_wrong=sum(by_task[t]["public_wrong_confident_authorizations"] for t in by_task),
                public_confident_authorizations=sum(by_task[t]["public_confident_authorizations"] for t in by_task),
                physical_joint_truth_counts={truth:sum(by_task[t]["physical_joint_truth_populations"][truth] for t in by_task) for truth in ("AA","AH","HA","HH")},
                physical_ack_axis_counts={truth:sum(by_task[t]["ack_truth_axis_counts"][truth] for t in by_task) for truth in ("t2_applied","t2_held","t3_applied","t3_held")},
                actual_per_task_joint_truth_stratified={t:by_task[t]["actual_joint_truth_stratified_results"] for t in by_task},
                additional_common_known_t4_neutral_probe_count=sum(by_task[t]["common_known_t4_probe_exposures"] for t in by_task),
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
    print("ALL_FOUR_ACK_TRUTHS_KNOWN_T4_PROBE_REAL_PHYSX_ALL64",json.dumps({
       "total":x["outcomes_total"],"public_identifications":x["public_confident_authorizations"],
       "wrong_confident":x["model_confident_wrong"],
       "full_double_faults":x["double_fault_exposure_population"],
       "paired":x["paired_discordances"],"paired_p":x["exploratory_unadjusted_exact_p"],
       "complete_gate":x["complete_double_fault_gate_passes"]},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
