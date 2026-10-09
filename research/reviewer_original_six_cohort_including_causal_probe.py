"""Audit SIX ORIGINAL DIFFERENT original PhysX source populations, never pool
as one confirmatory experiment. The newest original causal true-native
nonzero probe pilot has only n=32, not "64 unseen" or a safety proof.
"""
from __future__ import annotations
import json,math
from pathlib import Path
from research.reviewer_independent_original_5cohort_stats import (
    report as existing5,analyze,git_blob)
ORIGINAL=Path(
"research/frozen_policy_transfer/evidence/causal_nonzero_active_vs_passive_original32_1200101_1210116/ORIGINAL_PHYSX_ACTIVE_PROBE_PILOT32_AUDIT.json")
PIN="e08883c1831bd621dd8231bbf49759cb0e05be57"

def six_cohort_review():
    prior=existing5()
    raw=ORIGINAL.read_bytes()
    if git_blob(raw)!=PIN:
        raise ValueError("Causal active positive native PhysX pilot source has CHANGED")
    original=json.loads(raw)
    if original.get("real_separately_physically_stepped_controller_worlds")!=352:
        raise ValueError("Not actually original 352 real PhysX controller worlds")
    data=original.get("all_original_task_truth_and_probe_evidence",[])
    if len(data)!=32 or len(set((r["task"],r["seed"]) for r in data))!=32:
        raise ValueError("Missing true physical source tasks")
    rows=[]
    for r in data:
        if r["task"] not in ("pull_cube","stack_cube"):
            raise ValueError("Invalid policy checkpoint task")
        if r["seed"] in set(range(1200101,1200117)) and r["task"]!="pull_cube":
            raise ValueError("Original physical ACK source seed has wrong frozen task")
        if r["seed"] in set(range(1210101,1210117)) and r["task"]!="stack_cube":
            raise ValueError("Original physical ACK source seed has wrong frozen task")
        if not(1200101<=r["seed"]<=1200116 or
               1210101<=r["seed"]<=1210116):
            raise ValueError("Unexpected source seed accidentally overlaps prior cohort")
        if r["true_joint_ack"] if "true_joint_ack" in r else False:
            raise ValueError("Wrong source schema")
        if r["truth"] not in ("AA","AH","HA","HH"):
            raise ValueError("Original true physical double ACK source missing")
        if any(not isinstance(r[k],(float,int)) or not math.isfinite(r[k]) for k in
               ("passive_public_tool_achieved_xyz_displacement_m",
                "active_public_tool_achieved_xyz_displacement_m",
                "active_native_target_probe_position_displacement_inf_m")):
            raise ValueError("Source physical real displacement evidence missing")
        if r["active_native_target_probe_position_displacement_inf_m"]<=1e-5:
            raise ValueError("Source alleged nonzero native probe was not physically enacted")
        if r["active_always_query_private_reads"]!=1:
            raise ValueError("Same nonzero probe always-read comparator did not pay real privileged getter")
        rows.append({
            "task":r["task"],"seed":r["seed"],"stratum":r["truth"],
            "active":(r["active_success"],r["active_private_reads"],
                      r["active_authorized"],r["active_wrong_confident"]),
            "passive":(r["passive_success"],r["passive_private_reads"],
                      r["passive_authorized"],r["passive_wrong_confident"])})
    old_seeds=set()
    for k,v in prior["cohorts"].items():
        parent=json.loads(Path(v["source_file"]).read_bytes())
        orig=(parent.get("all_original_trial_rows")
              or parent.get("all_original_source_episode_records")
              or parent.get("all_actual_original_source_episode_records")
              or parent.get("per_original_episode"))
        if orig is None and "by_task" in parent:
            orig=[r for p in parent["by_task"].values() for r in p["original_all_trial_rows"]]
        old_seeds.update((r["task"],r["seed"]) for r in orig)
    if any((r["task"],r["seed"]) in old_seeds for r in rows):
        raise ValueError("Causal native nonzero pilot new state contaminated previous actual PhysX cohorts")
    c={
        "primary_model":"fixed_nonzero_t4_active_full_history_observer",
        "secondary_model":"native_t4_zero_passive_full_history_observer",
        "original_full_audit_git_blob":PIN,
        "overall":analyze(rows,"active","passive"),
        "by_task":{task:analyze([r for r in rows if r["task"]==task],"active","passive")
                   for task in ("pull_cube","stack_cube")},
        "per_physical_joint_ACK_truth":{
            k:analyze([r for r in rows if r["stratum"]==k],"active","passive")
            for k in ("AA","AH","HA","HH")},
        "genuine_original_native_worlds":352,
        "native_zero_vs_nonzero_causal_displacement_is_COST_NOT_MATCHED":True,
        "same_NONZERO_probe_always_query_control_actual_success":
            sum(r["active_always_query_success"] for r in data),
        "same_NONZERO_probe_always_query_privileged_reads":
            sum(r["active_always_query_private_reads"] for r in data),
        "mean_real_native_target_perturbation_inf_m":
            sum(r["active_native_target_probe_position_displacement_inf_m"]
                for r in data)/32,
        "mean_real_public_tool_achieved_displacement_m_active":
            sum(r["active_public_tool_achieved_xyz_displacement_m"]
                for r in data)/32,
        "mean_real_public_tool_achieved_displacement_m_passive":
            sum(r["passive_public_tool_achieved_xyz_displacement_m"]
                for r in data)/32,
        "a_fixed_probe_is_not_an_optimized_action_selection_policy":True
    }
    z=c["overall"]
    assert z["primary"]["original_physical_task_success"]==28
    assert z["secondary"]["original_physical_task_success"]==28
    assert z["primary"]["original_native_privileged_reads"]==28
    assert z["secondary"]["original_native_privileged_reads"]==26
    assert z["primary"]["unique_full_target_history_authorizations"]==4
    assert z["secondary"]["unique_full_target_history_authorizations"]==6
    assert c["same_NONZERO_probe_always_query_control_actual_success"]==28
    assert c["same_NONZERO_probe_always_query_privileged_reads"]==32
    assert z["paired_task_outcomes"]=={
        "both_real_task_success":28,"primary_only_real_task_success":0,
        "secondary_only_real_task_success":0,"neither_real_task_success":4}
    return {
        "schema":"SIX_DISTINCT_REAL_PHYSX_ORIGINAL_POPULATIONS_5x64_PLUS_NONZERO_PILOT32_SOURCE_AUDIT_v1",
        "prior_five_cohorts":prior["cohorts"],
        "sixth_pilot":c,
        "all_original_6_cohort_reset_state_ids_are_separate":True,
        "total_origins_across_distinct_episodes":352,
        "this_DID_NOT_EXECUTE_A_NEW_SIMULATION":True,
        "pilot_is_only_32_not_64_original_resets":True,
        "no_cross_study_pooled_success_or_safety_claim":True,
        "true_PPO_VLA_robot_safety_or_real_packet_loss":False,
        "genuinely_external_independent_scientific_replication":False
    }
if __name__=="__main__":
    x=six_cohort_review()
    a=x["sixth_pilot"]
    print("SIX_SEPARATE_AUTHENTIC_PHYSX_REVIEWER_RISK_AND_CAUSAL_PROBE_AUDITS",
          json.dumps({
             "original_independent_reset_state_populations":x["total_origins_across_distinct_episodes"],
             "actual_nonzero_original_352_PhysX":a["genuine_original_native_worlds"],
             "new_study_exact_stats":a["overall"],
             "realized_physical_displacement_costs":{
                 k:a[k] for k in ("mean_real_native_target_perturbation_inf_m",
                      "mean_real_public_tool_achieved_displacement_m_active",
                      "mean_real_public_tool_achieved_displacement_m_passive")}
          },sort_keys=True))
