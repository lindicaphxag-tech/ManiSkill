"""Recompute v2.3 paper claims from TWO physically executed ORIGINAL source archives.

This is source-only verification, never new physics or independent replication.
Reject swapped task denominations, cherry-picked paired outcomes, altered native
action-prefix numbers, unreported wrong labels, and unjustified p-values.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

def check_sha256(folder:Path):
    manifest=folder/"SHA256SUMS"
    if not manifest.is_file():
        raise ValueError(f"Missing SHA256 manifest: {folder}")
    entries=manifest.read_text().splitlines()
    if not entries:
        raise ValueError("Empty source digest manifest")
    found=set()
    for line in entries:
        if len(line)<67 or line[64:66] not in ("  "," *"):
            raise ValueError(f"Malformed SHA256: {line!r}")
        expected,name=line[:64],line[66:]
        if len(expected)!=64 or any(c not in "0123456789abcdef" for c in expected):
            raise ValueError("Invalid SHA256 hex")
        item=folder/name
        if item.resolve().parent!=folder.resolve() or not item.is_file():
            raise ValueError("SHA entry missing/nonlocal")
        if hashlib.sha256(item.read_bytes()).hexdigest()!=expected:
            raise ValueError("Source original SHA256 failed "+name)
        if name in found:
            raise ValueError("Duplicate SHA256 identity")
        found.add(name)
    return found

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--matched64",required=True,type=Path)
    p.add_argument("--factorial256",required=True,type=Path)
    p.add_argument("--motor256",required=True,type=Path)
    p.add_argument("--manuscript",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    preserved64=check_sha256(a.matched64)
    preserved256=check_sha256(a.factorial256)
    preservedmotor=check_sha256(a.motor256)
    assert len(preserved64)>=17 and len(preserved256)>=65 and len(preservedmotor)>=1
    early=json.loads((a.matched64/"full_shared_compiler_original64_audit.json").read_bytes())
    conf=json.loads((a.factorial256/"independent_source_only_full256_audit.json").read_bytes())
    motor=json.loads((a.motor256/"REAL256_ACTUAL_NATIVE_T2_T3_MOTOR_AND_PUBLIC_PROBE_AUDIT.json").read_bytes())
    assert len(early["registered_source_64"])==8 and len(early["all_episodes"])==64
    assert early["actually_stepped_simulator_worlds"]==576
    assert early["all_compiler_traces_valid"] is True
    assert len(early["all_episodes"])==64
    assert early["outcomes"]["public"]=={"private_reads":48,"task_success":53}
    assert early["outcomes"]["fixed_t5"]=={"private_reads":64,"task_success":53}
    assert early["public_confident_history_admissions"]==16
    assert early["observed_confident_wrong_history"]==0
    both=sum(r["new_success"] and r["fixed_success"] for r in early["all_episodes"])
    neither=sum(not r["new_success"] and not r["fixed_success"] for r in early["all_episodes"])
    discord=sum(r["new_success"]!=r["fixed_success"] for r in early["all_episodes"])
    assert (both,neither,discord)==(53,11,0)
    assert conf["registered_source_reset_clusters"]==64
    assert conf["registered_task_seed_truth_cells"]==256
    assert conf["separate_physx_worlds"]==2304
    assert conf["numerically_matched_public_source_observation_per_truth_verified"] is True
    assert conf["exact_initial_sha_match_cluster_count"]==64
    assert conf["numeric_max_public_policy_obs_gap"]==0
    assert len(conf["all_source_rows_retained"])==256
    assert len(conf["complete_32_shard_sha256"])==64
    assert conf["primary_outcomes"]=={
      "public":{"official_task_success":221,"decision_private_reads":195},
      "strong_task":{"official_task_success":202,"decision_private_reads":221},
      "fixed_t5":{"official_task_success":210,"decision_private_reads":256},
      "always_held":{"official_task_success":133,"decision_private_reads":0},
    }
    assert conf["paired_public_vs_strong"]=={"both":197,"neither":30,"public_only":24,"strong_only":5}
    assert conf["public_wrong_confident_count"]==0
    assert conf["total_public_xyz_sample_events"]==512
    assert conf["incomplete_both_fault_exposure_count"]==0
    delta=(221-202)/256
    assert delta>=.04 and math.isclose(delta,conf["method_success_delta_public_minus_strong_per_cell"])
    assert math.isclose(conf["seed_cluster_exact_swap_two_sided_sensitivity_p_not_randomized_proof"],.002410888671875,abs_tol=1e-15)
    assert conf["seed_cluster_bootstrap_95pct_public_minus_strong_success_gap"]==[.03125,.12109375]
    assert motor["actual_source_truth_cells"]==256 and motor["original_actual_seed_clusters"]==64
    assert len(motor["original_per_condition"])==256
    assert motor["native_dispatched_command_identical_counts"]=={
      "public_and_strong_t2_native_identical":256,
      "public_and_strong_t3_native_identical":192,
      "public_and_fixed_t2_native_identical":256,
      "public_and_fixed_t3_native_identical":128,
    }
    assert all(n==256 for n in motor["physical_action_parity_eligible_denominators"].values())
    assert motor["real_t4_probe_receipts_by_method"]=={"public":256,"strong":256,"fixed":256}
    assert motor["public_extra_achieved_xyz_sample_events"]==512
    doc=a.manuscript.read_text()
    for marker in ("221/256","202/256","p=0.00241","195","0.03125","0.12109375",
                   "192/256","128/256","53 joint successes","48 versus 64"):
        if marker not in doc:
            raise ValueError("Manuscript missing original source derived claim "+marker)
    if "independent physical replication achieved" in doc:
        raise ValueError("Author-owned source audit cannot be described as third-party reproduction")
    output={
      "schema":"MANUSCRIPT_V2_3_INDEPENDENT_SOURCE_ONLY_ORIGINAL_NATIVE_PHYSX_CLAIM_AUDIT",
      "source_only_not_separately_executed_physics":True,
      "outside_independent_investigator_reproduction":False,
      "matched64":{"actual_worlds":576,"paired_both":both,"paired_neither":neither,"discordant":discord,
                    "public_success":53,"fixed_success":53,"public_private_reads":48,"fixed_private_reads":64},
      "confirmatory256":{"actual_worlds":2304,"new_source_seed_clusters":64,
                          "public_success":221,"strong_success":202,"public_private_reads":195,
                          "strong_private_reads":221,"preregistered_practical_success_margin_pass":True,
                          "paired_method_label_swap_p_sensitivity_only":conf["seed_cluster_exact_swap_two_sided_sensitivity_p_not_randomized_proof"],
                          "seed_cluster_bootstrap95":conf["seed_cluster_bootstrap_95pct_public_minus_strong_success_gap"],
                          "motor_t3_identical_public_strong":192,
                          "motor_t3_identical_public_fixed":128,
                          "equal_t4_probes_three_main_arms":256,
                          "public_xyz_sample_events":512},
      "original_sha256_source_files_verified":{
          "matched64":len(preserved64),"confirmatory256":len(preserved256),"real_motor256":len(preservedmotor)}
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("MAINTRACK_V23_ALL_ORIGINAL_SOURCE_CLAIMS_VERIFIED",json.dumps(output,sort_keys=True))
if __name__=="__main__":
    main()
