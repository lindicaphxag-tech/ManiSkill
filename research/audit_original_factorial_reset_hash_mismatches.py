"""Audit ALL ORIGINAL 128 physical cells without pretending seed=identical reset.

This is a FORENSIC descriptive reanalysis, not a repaired factorial claim.
Exact preregistration, source, and all 16 original per-shard audits must pass.
DO NOT edit the original failed full-population auditor or physics.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, random
from pathlib import Path
from research.run_same_reset_ack_factorial import (
    PREREG,SOURCE,CLASSIFIER,blob,select,validate,assert_preoutcome
)
from research.audit_same_reset_ack_factorial import (
    TASKS,CONDITIONS,ARMS,exact_cluster_swap_p,cluster_bootstrap_delta,
)

def audit(src:Path):
    assert_preoutcome()
    required={
        f"factorial_{task}_chunk{chunk}_truth{t}_{kind}.json"
        for task in TASKS for chunk in range(2) for t in CONDITIONS
        for kind in ("original8","audit")
    }
    found={p.name for p in src.glob("factorial_*.json")}
    if found!=required:
        raise ValueError(f"Original physical shards incomplete: missing={sorted(required-found)} extra={sorted(found-required)}")
    rows=[];original_sha={}
    for task in TASKS:
        for chunk in range(2):
            for t in CONDITIONS:
                prefix=f"factorial_{task}_chunk{chunk}_truth{t}"
                original=src/f"{prefix}_original8.json"
                stored=src/f"{prefix}_audit.json"
                original_raw=original.read_bytes()
                # Recalculate every source-level truth, fault, success,
                # probe and private read ledger; reject forged shard audits.
                expected=validate(json.loads(original_raw),task,chunk,t)
                expected.update(schema="same_reset_factorial_true_2x2_shard_audit_v1",
                                physical_original_sha256=hashlib.sha256(original_raw).hexdigest(),
                                prereg_git_blob=blob(PREREG),new_runner_git_blob=blob(SOURCE),
                                unchanged_response_model_git_blob=blob(CLASSIFIER))
                if json.loads(stored.read_text())!=expected:
                    raise ValueError("Inconsistent original independent per-shard audit: "+prefix)
                original_sha[original.name]=hashlib.sha256(original_raw).hexdigest()
                original_sha[stored.name]=hashlib.sha256(stored.read_bytes()).hexdigest()
                rows.extend(expected["rows"])
    if len(rows)!=128: raise ValueError("Original 128 physical cells not complete")
    byseed=collections.defaultdict(dict)
    for r in rows:
        key=(r["task"],r["seed"])
        t=r["truth_index"]
        if t in byseed[key]:
            raise ValueError("Duplicate original truth+seed cell: "+str((key,t)))
        byseed[key][t]=r
    if len(byseed)!=32: raise ValueError("Original 32 seed clusters not present")
    expected_keys={(task,seed) for task in TASKS for ch in range(2) for seed in select(task,ch)}
    if set(byseed)!=expected_keys: raise ValueError("Original seeds not as frozen")
    matched=[];mismatched=[];mismatches_by_task=collections.Counter()
    all_cells=collections.Counter()
    pertruth={}
    for task in TASKS:
        for t in CONDITIONS:
            source=[r for r in rows if r["task"]==task and r["truth_index"]==t]
            if len(source)!=16: raise ValueError("Unbalanced original true physical stratum")
            pertruth[f"{task}/truth{t}"]={
                "n_actual_physical_seed_truth_cells":16,
                "public_official_task_success":sum(int(r["new_success"]) for r in source),
                "strong_official_task_success":sum(int(r["strong_success"]) for r in source),
                "public_private_reads":sum(r["new_reads"] for r in source),
                "strong_private_reads":sum(r["strong_reads"] for r in source),
                "public_observed_wrong_confident":sum(int(r["wrong_confident"]) for r in source),
                "public_sensor_sample_events":sum(r["public_sample_events"] for r in source),
            }
    for key, four in sorted(byseed.items()):
        if set(four)!=set(CONDITIONS):
            raise ValueError("Incomplete physical factorial seed block: "+str(key))
        hashes=[four[t]["initial_source_physical_obs_sha256"] for t in CONDITIONS]
        if any(type(x) is not str or len(x)!=64 or any(c not in "0123456789abcdef" for c in x)
               for x in hashes):
            raise ValueError("Invalid original initial policy input source sha256")
        item={
            "task":key[0],"seed":key[1],
            "initial_observation_SHA256_exact_match_all_four":len(set(hashes))==1,
            "four_initial_policy_observation_SHA256":hashes,
            "distinct_initial_observation_hashes":len(set(hashes)),
            "four_truth_methods":[
                {"truth_index":t,"public_success":four[t]["new_success"],
                 "strong_success":four[t]["strong_success"],
                 "public_private_reads":four[t]["new_reads"],
                 "strong_private_reads":four[t]["strong_reads"],
                 "both_faults_actually_exposed":four[t]["public_both_faults_exposed"],
                 "public_confident":four[t]["public_authorized"],
                 "wrong_confident":four[t]["wrong_confident"]}
                for t in CONDITIONS
            ]
        }
        (matched if item["initial_observation_SHA256_exact_match_all_four"] else mismatched).append(item)
        if not item["initial_observation_SHA256_exact_match_all_four"]:
            mismatches_by_task[key[0]]+=1
        for t in CONDITIONS:
            row=four[t]
            all_cells["public_success"]+=int(row["new_success"])
            all_cells["strong_success"]+=int(row["strong_success"])
            all_cells["fixed_success"]+=int(row["fixed_success"])
            all_cells["held_success"]+=int(row["held_success"])
            all_cells["public_reads"]+=row["new_reads"]
            all_cells["strong_reads"]+=row["strong_reads"]
            all_cells["fixed_reads"]+=row["fixed_reads"]
            all_cells["wrong_confident"]+=int(row["wrong_confident"])
            all_cells["public_confident"]+=int(row["public_authorized"] is True)
            all_cells["public_sensor_events"]+=row["public_sample_events"]
            all_cells["public_both_fault_exposed"]+=int(row["public_both_faults_exposed"])
    def subset_summary(items):
        diffs=[sum(int(row["public_success"])-int(row["strong_success"]) for row in item["four_truth_methods"]) for item in items]
        if not items: return {
            "n_clusters":0,"n_cells":0,"status":"NO EXACT MATCHED INPUT OBSERVATION CLUSTERS",
            "effect_not_estimable":True}
        return {
            "n_clusters":len(items),"n_cells":len(items)*4,
            "public_success":sum(int(r["public_success"]) for x in items for r in x["four_truth_methods"]),
            "strong_success":sum(int(r["strong_success"]) for x in items for r in x["four_truth_methods"]),
            "public_private_reads":sum(r["public_private_reads"] for x in items for r in x["four_truth_methods"]),
            "strong_private_reads":sum(r["strong_private_reads"] for x in items for r in x["four_truth_methods"]),
            "descriptive_public_minus_strong_task_difference_per_cell":sum(diffs)/(4*len(items)),
            "exploratory_seed_cluster_signswap_p_not_randomized_causal_proof":exact_cluster_swap_p(diffs),
            "descriptive_seed_cluster_bootstrap95":cluster_bootstrap_delta(diffs),
            "NOT_a_prospective_success_analysis":True,
        }
    return {
        "schema":"Genuine_same_seed_not_necessarily_same_reset_forensics_intent_to_treat_v1",
        "source_origin_original_failure":"https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37930607707",
        "source_shard_original_SHA256":original_sha,
        "original_complete_physical_shards":16,
        "original_unique_seeds":32,
        "physical_truth_conditions_per_seed":4,
        "all_original_truth_cells_including_bad_matches":128,
        "all_genuine_native_physx_worlds_not_rerun":1152,
        "exact_original_precommitted_protocol_git_blob":blob(PREREG),
        "original_physics_source_git_blob":blob(SOURCE),
        "exact_input_observation_hash_all_4_conditions":
            len(mismatched)==0,
        "initial_observation_exact_hash_matched_clusters":len(matched),
        "initial_observation_hash_mismatched_clusters":len(mismatched),
        "mismatched_clusters_by_task":dict(sorted(mismatches_by_task.items())),
        "all_original_intent_to_treat_method_results":dict(sorted(all_cells.items())),
        "by_original_task_and_actual_fault_truth":pertruth,
        "matched_input_SHA_subgroup_exploratory_only":subset_summary(matched),
        "mismatched_input_SHA_subgroup_descriptive_only":subset_summary(mismatched),
        "all_exact_hash_matched_cluster_identifiers": [
             {"task":x["task"],"seed":x["seed"]} for x in matched],
        "all_original_hash_mismatches_retained_with_success_failures":mismatched,
        "strict_reviewer_conclusion":(
            "FOUR-TRUTH RANDOM-SEED DESIGN IS NOT A COMPLETE MATCHED-PHYSICAL-STATE "
            "FACTORIAL: ORIGINAL FULL AUDIT MUST REMAIN FAILED"
            if mismatched else "Original input observation hashes agree, no broader native state equality certified"
        ),
        "hash_difference_magnitude_NOT_available_in_original_archive":True,
        "avoid_causal_label_for_nonmatched_clusters":True,
        "author_operated_simulator_not_external_replication":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.source_dir)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("FORENSIC_ORIGINAL_PHYSX_RESET_HASH_COHORT",json.dumps({
        "all_cells":result["all_original_truth_cells_including_bad_matches"],
        "all_worlds":result["all_genuine_native_physx_worlds_not_rerun"],
        "matching_clusters":result["initial_observation_exact_hash_matched_clusters"],
        "mismatched_clusters":result["initial_observation_hash_mismatched_clusters"],
        "mismatched_by_task":result["mismatched_clusters_by_task"],
        "all_original_results":result["all_original_intent_to_treat_method_results"],
        "match_subgroup":result["matched_input_SHA_subgroup_exploratory_only"],
        "mismatch_subgroup":result["mismatched_input_SHA_subgroup_descriptive_only"],
    },sort_keys=True))

if __name__=="__main__":main()
