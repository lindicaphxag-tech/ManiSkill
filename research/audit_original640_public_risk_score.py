"""READ-ONLY bridge from first 640 actual PhysX worlds to future risk study.

This is a RETROSPECTIVE development diagnostic, NOT independent calibration.
It does NOT call calibrate_authority() or choose/tune an allegedly safe score.
The public reliability score was designed after the already published wrong
seed 1760020; only entirely NEW prospective task resets can validate it.
All original source JSONs are byte hash-checked by the strict source auditor.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from research.finite_risk_authority import (
    LabelledCalibration,native_public_score
)
from research.review_matched_public_bayes64_original import validate

EVIDENCE=(Path(__file__).resolve().parent/
  "frozen_policy_transfer/evidence/matched_public_bayes_original640_1760001_1770032")
TRUTHS=("held/held","held/applied","applied/held","applied/applied")
FROZEN_THRESHOLDS=(0.,.25,.5,1.)

def read_original_source_evidence(source:EVIDENCE.__class__=EVIDENCE):
    original=validate(source)  # verifies original task seeds, all source digests, physical prefix, and erroneous history
    rows=[]
    diagnostics={}
    for sourcefile in sorted(source.rglob("bayes_same_public_*_original8.json")):
        d=json.loads(sourcefile.read_text())
        task="pull_cube" if d["task"]=="PullCube-v1" else "stack_cube"
        for r in d["episodes"]:
            evidence=r.get("public_t3_evidence",{})
            allowed=evidence.get("authorized")
            if type(allowed) is not bool:
                raise ValueError("Missing original experimental public-authorization decision")
            residuals=evidence.get("candidate_residuals_m",[])
            eps=evidence.get("prior_training_epsilon_m")
            chosen=evidence.get("selected_candidate_index")
            if allowed and (type(chosen) is not int or chosen not in range(len(residuals))):
                raise ValueError("Original full controller history choice malformed")
            score=native_public_score(residuals,eps,.002,
                      chosen if allowed else 0,allowed)
            truth=(r["original_precommitted_physical_t2_execution_truth"]+
                   "/"+r["original_precommitted_physical_t3_execution_truth"])
            match=(chosen in evidence.get("audit_only_true_candidate_indices",[])) if allowed else True
            if allowed and (not match)!=evidence.get("wrong_confident"):
                raise ValueError("Confidence and privileged full target match disagree")
            rows.append(LabelledCalibration(task,r["seed"],score,allowed,match,truth))
            if allowed and not match:
                diagnostics[f"{task}:{r['seed']}"]={
                    "public_score_not_privileged_truth":score,
                    "actual_original_selected_index":chosen,
                    "actual_audit_only_true_history_indices":evidence["audit_only_true_candidate_indices"],
                    "original_full_pose_error":evidence["after_physics_audit_pose_errors"][chosen]
                }
    if len(rows)!=64 or len({(r.task,r.reset_id) for r in rows})!=64:
        raise ValueError("Lost duplicate or excluded original PhysX reset state")
    if len([r for r in rows if r.original_candidate_was_authorized])!=16:
        raise ValueError("First original source confident authorization count changed")
    if set(diagnostics)!={"pull_cube:1760020"}:
        raise ValueError("Previously documented wrong confidence witness was hidden")
    if sum(r.original_candidate_was_authorized and not r.true_history_matches_candidate for r in rows)!=1:
        raise ValueError("First original source wrong history count changed")
    return original,rows,diagnostics

def descriptive_only(source=EVIDENCE):
    original,rows,wrong=read_original_source_evidence(source)
    by_task={}
    for task in ("pull_cube","stack_cube"):
        rr=[r for r in rows if r.task==task]
        by_task[task]={}
        for threshold in FROZEN_THRESHOLDS:
            accepted=[r for r in rr if r.original_candidate_was_authorized and r.score>=threshold]
            by_task[task][str(threshold)]={
                "original_reset_states":len(rr),
                "would_still_authorize_if_used_retrospectively":len(accepted),
                "incorrect_history_in_these_old_seen_source_states":
                    sum(not r.true_history_matches_candidate for r in accepted)}
    return {
        "status":"RETROSPECTIVE_DEVELOPMENT_SANITY_CHECK__NOT_VALIDATION",
        "original_full_run_id":37924192162,
        "original_independent_zero_PyTorch_source_auditor_passed":True,
        "original_source_PhysX_worlds":640,
        "original_unique_task_reset_states":64,
        "original_public_admissions":16,
        "original_wrong_full_history_admissions":1,
        "risk_threshold_grid_selected_after_old_witness_was_known":True,
        "original_wrong_full_pose_witness":wrong,
        "descriptive_threshold_table_NOT_PROSPECTIVE":by_task,
        "future_fresh_risk_certificate_not_issued":True,
        "no_new_robot_task_success_claim":True
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,default=EVIDENCE)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    result=descriptive_only(args.source)
    doc=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output:args.output.write_text(doc)
    print("OLD_PHYSX_SCORE_COMPATIBILITY_NOT_NEW_CALIBRATION",doc)

if __name__=="__main__":main()
