"""NO-simulator independent whole-population original 16 seed / 64 ACK cells.

Reject all causal claims if any initial source PPO input SHA is unequal across
four executed truths of one seed. Never omit failed task/early faults or count
64 cells as 64 independent seeds. Recalculate each shard from its ORIGINAL
native robot source JSON, not source-produced audit summaries alone.
"""
from __future__ import annotations
import argparse, collections, hashlib, json
from pathlib import Path
import research.run_same_reset_ack_factorial as old
from research.audit_same_reset_ack_factorial import exact_cluster_swap_p,cluster_bootstrap_delta

PROTO="research/SERIAL_SAME_PROCESS_FOUR_ACK_NEW64_PREOUTCOME_V1.json"
START={"pull_cube":1970001,"stack_cube":1980001}
N=8
SOURCE_SHA="14882a4efcd36351f8cb5873e706488788446f32"
RESP_SHA="064bb46831b61af73ad445bc836326837ec5468f"

def audit(folder:Path):
    proto=json.loads(Path(PROTO).read_text())
    if (proto["schema"]!="prospective_serial_single_process_matched_four_true_ack_new16clusters_v1"
        or old.blob("research/frozen_ppo_same_reset_factorial_physx.py")!=SOURCE_SHA
        or old.blob("research/empirical_probe_response_classifier.py")!=RESP_SHA):
        raise ValueError("Original model/physical source/protocol mutated")
    old.PREREG=PROTO
    old.START.update(START)
    required={f"serial_{task}_truth{t}_{kind}.json" for task in START
              for t in range(4) for kind in ("original8","audit")}
    required|={f"serial_{task}_all_truth_reset_authenticity.json" for task in START}
    found={p.name for p in folder.glob("serial_*.json")}
    if found!=required: raise ValueError(f"Absent/mutated original serial shards; missing={required-found}, extras={found-required}")
    sha={};rows={}
    per_truth={}
    for task in START:
        for t in range(4):
            prefix=f"serial_{task}_truth{t}"
            original=folder/f"{prefix}_original8.json"
            raw=original.read_bytes()
            if not raw: raise ValueError("Zero native physics source")
            original_shard=json.loads(raw)
            deriv=old.validate(original_shard,task,0,t)
            deriv.update({
                "schema":"prospective_serial_same_process_true2x2_physical_shard_audit_v1",
                "original_native_physics_file_sha256":hashlib.sha256(raw).hexdigest(),
                "new_registered_protocol_git_blob":old.blob(PROTO),
                "previous_unchanged_native_physics_source_git_blob":SOURCE_SHA,
                "previous_unchanged_empirical_model_git_blob":RESP_SHA,
                "genuinely_one_task_python_process_for_four_conditions":True,
                "global_rng_reseed_before_truth":20261009,
            })
            auditfile=folder/f"{prefix}_audit.json"
            if deriv!=json.loads(auditfile.read_text()):
                raise ValueError("Recorded per-task original physical auditor mismatch")
            sha[original.name]=hashlib.sha256(raw).hexdigest()
            sha[auditfile.name]=hashlib.sha256(auditfile.read_bytes()).hexdigest()
            per_truth[prefix]={
                "n_actual_physical_seed_truth_cells":len(deriv["rows"]),
                "public_success":deriv["outcomes"][old.PUBLIC]["success"],
                "task_aware_success":deriv["outcomes"][old.STRONG[task]]["success"],
                "fixed_success":deriv["outcomes"][old.FIXED]["success"],
                "public_target_reads":deriv["outcomes"][old.PUBLIC]["reads"],
                "task_aware_target_reads":deriv["outcomes"][old.STRONG[task]]["reads"],
                "wrong_confident":deriv["public_wrong_confident"],
                "public_second_fault_exposed":deriv["public_both_faults_exposed"],
            }
            for r in deriv["rows"]:
                rows[(task,r["seed"],t)]=r
    if len(rows)!=64: raise ValueError("Incomplete original 64 true physical condition rows")

    clusters=[]
    exact_match=True
    for task,start in START.items():
        original_task_summary=json.loads((folder/f"serial_{task}_all_truth_reset_authenticity.json").read_text())
        if (original_task_summary["task"]!=task or original_task_summary["native_PhysX_worlds"]!=288
            or original_task_summary["source_seed_count"]!=8
            or original_task_summary["physical_truth_conditions"]!=4):
            raise ValueError("Original native task/physical denominator drift")
        for seed in range(start,start+N):
            four=[rows[(task,seed,t)] for t in range(4)]
            hashes=[r["initial_source_physical_obs_sha256"] for r in four]
            passed=len(set(hashes))==1 and all(type(x) is str and len(x)==64 for x in hashes)
            if not passed: exact_match=False
            if bool(original_task_summary["all_task_initial_input_hash_match"]) != all(
                len({rows[(task,s,t)]["initial_source_physical_obs_sha256"] for t in range(4)})==1
                for s in range(start,start+N)
            ):
                raise ValueError("Original per-task serial matched-reset source gate contradicts physical rows")
            clusters.append({
                "task":task,"seed":seed,
                "initial_source_PPO_obs_bytes_identical_across_truth":passed,
                "per_true_fault_original_PPO_SHA256":hashes,
                "public_successes":[r["new_success"] for r in four],
                "strong_successes":[r["strong_success"] for r in four],
                "fixed_successes":[r["fixed_success"] for r in four],
                "public_private_reads":[r["new_reads"] for r in four],
                "strong_private_reads":[r["strong_reads"] for r in four],
                "public_wrong_confident":[r["wrong_confident"] for r in four],
                "public_physical_two_ACK_exposures":[r["public_both_faults_exposed"] for r in four],
                "public_XYZ_sensor_events":[r["public_sample_events"] for r in four],
            })
    if len(clusters)!=16:raise ValueError("Wrong unique seed cluster count")
    paired_diff=[sum(int(a)-int(b) for a,b in zip(c["public_successes"],c["strong_successes"]))
                 for c in clusters]
    results={
      "schema":"prospective_serial_real_physx_exact_4x_true_ACK_16_cluster_audit_v1",
      "original_seed_clusters":16,
      "all_original_true_physical_ACK_cells":64,
      "all_original_real_native_PhysX_worlds":576,
      "all_initial_policy_observation_sha_equal_by_seed_across_truth":exact_match,
      "matched_reset_clusters":sum(int(c["initial_source_PPO_obs_bytes_identical_across_truth"]) for c in clusters),
      "missing_or_failed_reset_identity_clusters":sum(int(not c["initial_source_PPO_obs_bytes_identical_across_truth"]) for c in clusters),
      "total_official_success_public":sum(sum(c["public_successes"]) for c in clusters),
      "total_official_success_task_aware":sum(sum(c["strong_successes"]) for c in clusters),
      "total_official_success_fixed":sum(sum(c["fixed_successes"]) for c in clusters),
      "total_private_reads_public":sum(sum(c["public_private_reads"]) for c in clusters),
      "total_private_reads_task_aware":sum(sum(c["strong_private_reads"]) for c in clusters),
      "total_wrong_confident":sum(sum(c["public_wrong_confident"]) for c in clusters),
      "all_results_grouped_by_eight_real_task_truth_combinations":per_truth,
      "public_positive_outcome_paired_with_strong_not_proven_significant":True,
      "exact_two_sided_seed_cluster_swap_exploratory_p":exact_cluster_swap_p(paired_diff),
      "seed_cluster_bootstrap95_per_condition_difference":cluster_bootstrap_delta(paired_diff),
      "original_all_clustering_and_initial_input_SHA":clusters,
      "source_physical_sha256_archive":sha,
      "source_frozen_original_git_blob":SOURCE_SHA,
      "registered_protocol_git_blob":old.blob(PROTO),
      "claim_limitations":{
          "identical_robot_PPO_initial_input_SHA_does_not_prove_all_unobserved_world_states_equal":True,
          "unknown_ACK_is_simulated_physical_native_action_hold_not_real_transport_packet_loss":True,
          "external_lab_independent_replication":False,
          "full_sensor_actuation_cost_parity_of_active_probe_methods":False,
          "hardware_force_or_collision_safety_certificate":False,
          "statistically_significant_task_success_superiority":False,
      }
    }
    return results

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    out=audit(a.source_dir)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_576_WORLD_SERIAL_FACTORED_SOURCE_AUDIT",json.dumps({
        k:v for k,v in out.items() if k in (
            "original_seed_clusters","all_original_true_physical_ACK_cells","all_original_real_native_PhysX_worlds",
            "matched_reset_clusters","missing_or_failed_reset_identity_clusters","total_official_success_public",
            "total_official_success_task_aware","total_official_success_fixed",
            "total_private_reads_public","total_private_reads_task_aware","total_wrong_confident",
            "exact_two_sided_seed_cluster_swap_exploratory_p",
            "seed_cluster_bootstrap95_per_condition_difference",
        )},sort_keys=True))
    if not out["all_initial_policy_observation_sha_equal_by_seed_across_truth"]:
        raise ValueError("NO PHYSICAL 4-TRUTH SAME-RESET CLAIM: original input digests differ; raw source saved.")

if __name__=="__main__":main()
