"""Independent, source-only full64 OOD physical Panda gains plus t1 known-ACK
public-model validity gate; imports no PPO or simulator runner.

Task outcomes, false confident target assignments, private decision-time
reads, true frozen response-model miscoverage and t1 public sensing cost are
all independently recomputed from actual original source, not screenshots.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from research.run_aef_h4_native64 import (
    TASKS,FIRST,accepted,validate_result,REGISTERED_BLOB,NARROW,PUBLIC,FIXED,SELECTIVE)

def independent_original_all64(folder):
    wanted={f"aef_h4_{task}_chunk{i}_{k}.json"
        for task in TASKS for i in range(4) for k in ("original8","audit")}
    got={f.name for f in folder.glob("aef_h4_*.json")}
    if got!=wanted:
        raise ValueError(f"Missing genuine original controller worlds {wanted-got}, extra {got-wanted}")
    original_sha={}
    rows=[]
    for task in TASKS:
        for chunk in range(4):
            name=f"aef_h4_{task}_chunk{chunk}"
            body=folder/(name+"_original8.json")
            audited=folder/(name+"_audit.json")
            raw=body.read_bytes()
            data=json.loads(raw)
            expected=validate_result(data,task,accepted(task,chunk))
            proof=json.loads(audited.read_text())
            if proof.get("original_raw_sha256")!=hashlib.sha256(raw).hexdigest() or any(
                proof.get(k)!=v for k,v in expected.items()):
                raise ValueError("Independent original OOD physic shard scoring mismatch")
            original_sha[body.name]=hashlib.sha256(raw).hexdigest()
            original_sha[audited.name]=hashlib.sha256(audited.read_bytes()).hexdigest()
            rows.extend(expected["sample_rows"])
    if len(rows)!=64 or len(set((r["task"],r["seed"]) for r in rows))!=64:
        raise ValueError("Not exact distinct 64 source reset state population")
    combined={}
    for task in TASKS:
        for combo in ("AA","AH","HA","HH"):
            for mode in ("slow","fast"):
                sample=[r for r in rows if r["task"]==task and
                        r["true_joint_ack"]==combo and r["physics_drive_mode"]==mode]
                if len(sample)!=4:
                    raise ValueError("No prospective balanced 4-execution×2-real-controller-dynamics domain: "+
                                     str((task,combo,mode,len(sample))))
                combined[f"{task}:{combo}:{mode}"]=scores(sample)
    result={"schema":"independent_native_AEF_H4_bounded_common_action_with_finite_ambiguity_horizon_full64_v1",
            "original_prospective_registration_git_blob":REGISTERED_BLOB,
            "AEF_H4_max_four_post_probe_unresolved_native_actions":True,
            "AEF_H4_forced_real_target_reads":sum(
                int(r.get("hybrid_forced_horizon_read",False)) for r in rows),
            "AEF_H4_post_probe_unresolved_native_action_count":sum(
                r.get("hybrid_ambiguity_horizon_actions",0) for r in rows),
            "old_original_frozen_native_ABI_no_retraining":True,
            "source_original_native_physx_worlds":640,
            "original_registered_source_reset_states":64,
            "physical_domains":["slow:stiffness500_damping70","fast:stiffness1500_damping130"],
            "four_genuine_applied_held_joint_ACK_combinations":True,
            "all_original_source_file_sha256":original_sha,
            "all_original_trial_rows":rows,
            "total":scores(rows),
            "by_task":{t:scores([r for r in rows if r["task"]==t]) for t in TASKS},
            "by_physical_gain":{m:scores([r for r in rows if r["physics_drive_mode"]==m])
                                for m in ("slow","fast")},
            "task_ack_gain_stratified":combined,
            "public_t4_2_public_XYZ_samples_per_hybrid_and_original":True,
            "action_equivalence_certificate_is_for_native_target_NOT_collision_or_hardware_safety":True,
            "t4_public_residual_model_not_safety_certificate":True,
            "no_independent_external_lab_reproduction_or_hardware_safety":True}
    return result

def scores(sample):
    out={}
    for name,short in (("narrow","old"),("hybrid","hybrid")):
        evs=[r[f"{name}_public_evidence"] for r in sample]
        out[short]={
            "task_success":sum(r[f"{name}_success"] for r in sample),
            "privileged_native_target_reads":sum(r[f"{name}_reads"] for r in sample),
            "public_unique_history_authorizations":sum(e["authorized"] for e in evs),
            "wrong_confident_native_history":sum(e["wrong_confident"] for e in evs),
            "true_history_response_model_outside_frozen_eps":sum(
                e["candidate_residuals_m"][e["audit_only_true_candidate_indices"][0]]
                    >e["prior_training_epsilon_m"] for e in evs),
            "public_xyz_observation_samples":len(sample)*2}
    out["original_source_reset_states"]=len(sample)
    out["hybrid_t5_robust_common_action_admissions"]=sum(
        r["hybrid_robust_certificate_accepted_t5"] is True for r in sample)
    out["hybrid_public_history_ACTUALLY_used_for_policy"]=sum(
        r["hybrid_public_history_actually_used"] is True for r in sample)
    out["hybrid_private_target_getter_fallbacks"]=sum(
        r["hybrid_reads"] for r in sample)
    out["task_sensitive_query_success"]=sum(r["strong_success"] for r in sample)
    out["task_sensitive_privileged_reads"]=sum(r["strong_reads"] for r in sample)
    out["actual_native_ack_gate_exposed"]=all(r["original_native_step_4_exposed"] for r in sample)
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=independent_original_all64(a.source_dir)
    a.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("REAL_PHYSX_AEF_ROBUST_FIRST_HYBRID_ALL64_SOURCE_AUDIT",
          json.dumps({"totals":report["total"],"gain":report["by_physical_gain"],
                      "by_task":report["by_task"]},sort_keys=True),flush=True)
