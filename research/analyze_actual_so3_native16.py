"""Original physically stepped 16 PPO tasks: new public SO3 signal feasibility diagnostic.

This is *observational only*, not an improved history-authorizing controller.
No hyperparameter selection, no threshold, no altered native simulator.
Original audit-only true target labels may be used solely for analysis.
"""
from __future__ import annotations
import argparse,hashlib,json,math,statistics
from pathlib import Path
from research.run_so3_public_signal_pilot import audit_raw,SEED_FIRST,A,B

def hash_bytes(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def study(path):
    original_files={}
    episodes=[]
    for task in SEED_FIRST:
        original=path/f"so3_physical_{task}_original8.json"
        orig_audit=path/f"so3_physical_{task}_audit.json"
        raw=json.loads(original.read_text())
        expected=audit_raw(raw,task)
        expected["original_native_physx_json_sha256"]=hash_bytes(original)
        if json.loads(orig_audit.read_text()) != expected:
            raise ValueError("Actual original per-task SO3 source differs from native runner auditor")
        original_files[original.name]=hash_bytes(original)
        original_files[orig_audit.name]=hash_bytes(orig_audit)
        for row in raw["episodes"]:
            signal={}
            for arm,key in [(A,"public_t3_evidence"),(B,"strong_score_060_evidence")]:
                ev=row.get(key,{})
                if ev.get("so3_public_samples_charged")!=2:
                    signal[arm]={"actual_public_so3_available":False}
                    continue
                scores=ev["so3_public_geodesic_to_candidate_arc_rad"]
                xyz=ev["candidate_residuals_m"]
                true=ev["audit_only_true_candidate_indices"]
                if not scores or len(scores)!=len(xyz) or not isinstance(true,list):
                    raise ValueError("Genuine physical candidate vectors/truth audit missing")
                best_so3=min(range(len(scores)),key=lambda i:scores[i])
                best_xyz=min(range(len(xyz)),key=lambda i:xyz[i])
                so3_sorted=sorted(scores)
                xyz_sorted=sorted(xyz)
                signal[arm]={
                    "actual_public_so3_available":True,
                    "candidate_count":len(scores),
                    "true_history_audit_only_indices":true,
                    "so3_best_candidate_index_DIAGNOSTIC_ONLY":best_so3,
                    "xyz_best_candidate_index_DIAGNOSTIC_ONLY":best_xyz,
                    "so3_argmin_matches_audited_true":best_so3 in true,
                    "xyz_argmin_matches_audited_true":best_xyz in true,
                    "so3_min_rad":so3_sorted[0],
                    "so3_first_second_gap_rad":so3_sorted[1]-so3_sorted[0] if len(scores)>1 else None,
                    "so3_true_min_rad":min((scores[i] for i in true),default=None),
                    "original_history_authorized":ev["authorized"],
                    "original_wrong_confident_AUDIT_ONLY":ev["wrong_confident"],
                    "original_first_source_quaternion_xyzw":ev["so3_public_before_quat_xyzw"],
                    "original_second_source_quaternion_xyzw":ev["so3_public_after_quat_xyzw"],
                    "actual_source_public_SO3_residuals_rad":scores,
                    "actual_source_public_XYZ_residuals_m":xyz,
                    "source_true_pose_is_AUDIT_ONLY":True,
                }
            episodes.append({
                "task":task,"seed":row["seed"],"physical_ACK_truth_index":(row["seed"]-1)%4,
                "original_official_success":{n:row["success_once"][n] for n in (A,B)},
                "original_actual_privileged_reads":{n:row["privileged_target_readback_decision_count"][n] for n in (A,B)},
                "public_orientation_channel":signal,
                "no_changes_to_source_method_or_control":True,
            })
    if len(episodes)!=16 or len({(e["task"],e["seed"]) for e in episodes})!=16:
        raise ValueError("True original 16 native physic state denominator mutated")
    counts={}
    for arm in (A,B):
        eligible=[e["public_orientation_channel"][arm] for e in episodes if e["public_orientation_channel"][arm]["actual_public_so3_available"]]
        true_available=[e for e in eligible if e["true_history_audit_only_indices"]]
        counts[arm]={
            "full_intention_to_treat_episodes":16,
            "actual_physical_public_quaternion_pairs":len(eligible),
            "public_quaternion_sample_events":2*len(eligible),
            "candidate_true_history_representable_in_original_belief":len(true_available),
            "so3_ARGMIN_true_selected_DIAGNOSTIC_ONLY":sum(e["so3_argmin_matches_audited_true"] for e in true_available),
            "xyz_ARGMIN_true_selected_DIAGNOSTIC_ONLY":sum(e["xyz_argmin_matches_audited_true"] for e in true_available),
            "best_so3_disagrees_with_best_xyz":sum(e["so3_best_candidate_index_DIAGNOSTIC_ONLY"]!=e["xyz_best_candidate_index_DIAGNOSTIC_ONLY"] for e in eligible),
            "SO3_candidate_gap_positive_count":sum((e["so3_first_second_gap_rad"] or 0)>1e-6 for e in eligible),
            "original_policy_task_success":sum(e["original_official_success"][arm] for e in episodes),
            "original_counted_private_target_reads":sum(e["original_actual_privileged_reads"][arm] for e in episodes),
            "original_wrong_confident":sum(e["original_wrong_confident_AUDIT_ONLY"] for e in eligible),
        }
    return {
        "schema":"genuine_original_physical_public_orientation_feasibility_v1",
        "actual_ManiSkill_CPU_PhysX_worlds":160,
        "frozen_original_task_reset_states":16,
        "all_four_true_ACK_physical_fault_patterns":True,
        "original_native_source_files_sha256":original_files,
        "per_original_competing_arm":counts,
        "all_original_16_intent_to_treat_rows":episodes,
        "new_SO3_sensor_is_actually_measured_public_proprioception":True,
        "NOT_statistically_independent_camera_or_sensor":True,
        "NO_SO3_based_history_selection_or_task_recovery_run":True,
        "NO_new_threshold_calibrated_on_original_pilot":True,
        "pilot_diagnostics_CANNOT_demonstrate_prospective_algorithm_superiority":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    report=study(args.source_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ACTUAL_NATIVE_PHYXS_PUBLIC_SO3_SIGNAL_FORENSIC",json.dumps({
        "states":report["frozen_original_task_reset_states"],"worlds":report["actual_ManiSkill_CPU_PhysX_worlds"],
        "by_arm":report["per_original_competing_arm"],
    },sort_keys=True))

if __name__=="__main__": main()
