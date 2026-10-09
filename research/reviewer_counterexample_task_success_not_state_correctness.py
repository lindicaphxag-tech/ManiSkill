"""Source-anchored latent target ERROR hidden by successful PullCube task.

The single seed is identified FROM an already archived complete 64-source
denominator; this is a diagnostic negative, NOT an after-outcome filtered
evaluation sample and not newly measured physics.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
F="fault_always_single_privileged_query"
ROOT=Path("research/frozen_policy_transfer/evidence/matched_same_public_bayes_original64_1760001_1770032")
SEED=1760020

def witness(folder):
    filename=folder/"bayes_same_public_pull_cube_chunk2_original8.json"
    original=json.loads(filename.read_text())
    assert original["original_seed_population"]==list(range(1760017,1760025))
    rows=[x for x in original["episodes"] if x["seed"]==SEED]
    assert len(rows)==1
    row=rows[0]
    assert row["task"]=="PullCube-v1"
    assert row["original_precommitted_physical_t2_execution_truth"]=="applied"
    assert row["original_precommitted_physical_t3_execution_truth"]=="applied"
    ev=row["public_t3_evidence"]
    posterior=row["same_sensor_posterior_evidence"]
    assert ev["authorized"] is True and ev["wrong_confident"] is True
    assert ev["selected_candidate_index"]==0
    assert ev["audit_only_true_candidate_indices"]==[3]
    assert row["success_once"][A] is True and row["success_once"][B] is True and row["success_once"][F] is True
    assert row["privileged_target_readback_decision_count"][A]==0
    assert row["privileged_target_readback_decision_count"][B]==1
    assert row["privileged_target_readback_decision_count"][F]==1
    assert posterior["authorized"] is False and posterior["wrong_confident"] is False
    assert ev["accepted_position_indices"]==[0]
    eps=float(ev["prior_training_epsilon_m"])
    residuals=[float(x) for x in ev["candidate_residuals_m"]]
    assert residuals[0]<=eps and all(r>eps+.002 for r in residuals[1:])
    assert residuals[3]>eps, "Actual true candidate predicted response invalid under trained envelope"
    error_pos,error_rot=ev["after_physics_audit_pose_errors"][0]
    assert error_pos>0.06 and error_rot>.05
    for key in ("matched_prefix_physical_audit","matched_posterior_prefix_audit"):
        pre=row[key]
        assert pre["valid_exact_prefix"] and pre["pre_t5_target_position_max_abs_m"]<5e-5
        assert pre["pre_t5_achieved_position_max_abs_m"]<5e-5
    first_complete=json.loads((folder/"first_original_full64_audit.json").read_text())
    assert first_complete["n_original_task_reset_states"]==64
    assert first_complete["total"][A]["wrong_confident"]==1
    return {
        "research_question":"Does successful closed-loop manipulation certify the adapter recovered true hidden target memory?",
        "answer":"NO. One original successfully completed PullCube task with a FALSE confident complete SE(3) target-history authorization.",
        "source_full_denominator":64,
        "original_frozen_physx_worlds":640,
        "task":"PullCube-v1","seed":SEED,
        "physical_truth":{"t2":"applied","t3":"applied"},
        "selected_wrong_complete_history_index":0,
        "actual_true_complete_history_index":3,
        "wrong_pose_error_position_m":error_pos,
        "wrong_pose_error_orientation_rad":error_rot,
        "public_residual_for_wrong_selected_m":residuals[0],
        "public_residual_for_true_m":residuals[3],
        "registered_empirical_epsilon_m":eps,
        "registered_nonwinner_gap_m":.002,
        "same_two_XYZ_observations_for_competing_methods":True,
        "identical_pre_t5_physically_executed_SE3_prefix":True,
        "public_set_method":{"confident":True,"wrong":True,"privileged_target_reads":0,"official_task_success":True},
        "same_public_normalized_residual_weight_method":{"confident":False,"privileged_target_reads":1,"official_task_success":True},
        "fixed_target_read":{"privileged_target_reads":1,"official_task_success":True},
        "limitation":"This falsifies source-empirical zero-error history certification, not the official task success rate. It is owner-operated PhysX, no real robot/hardware guarantee."
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--source-dir",type=Path,default=ROOT)
    p.add_argument("--output",type=Path);a=p.parse_args()
    z=witness(a.source_dir)
    if a.output:a.output.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
    print("ACTUAL_ONE_FALSE_CONFIDENT_HISTORY_SUCCESS_CASE",json.dumps(z,sort_keys=True))

if __name__=="__main__":main()
