"""RECONSTRUCTION ONLY: re-audit 32 ALREADY EXPOSED original PhysX states.

No new PPO policy runs, and NO prospective new-method claim. The purpose
is to falsify why an earlier all-candidates-SO3-equality gate rejected
otherwise uniquely-position-identifiable COMPLETE target-pose histories.

Runs with stdlib only:
python -m research.review_old_survivor32 --output /tmp/retrospective.json
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

BASE=Path("research/frozen_policy_transfer/evidence/public_fourhistory_frozen_ppo_original32_780001_790016")
BASELINE_TASKS={"pull_cube":780001,"stack_cube":790001}
MARGIN=0.002

def require(cond,msg):
    if not cond:raise ValueError(msg)

def source_provenance(directory):
    pairs={}
    for row in (directory/"SHA256SUMS").read_text().splitlines():
        digest,name=row.split(maxsplit=1)
        require(name not in pairs and len(digest)==64,"Bad/duplicated source hash")
        pairs[name]=digest
    names={"full_original_new32_task_ack_public_audit.json"}
    for task in BASELINE_TASKS:
        for c in range(4):
            names.update({f"public_fourhistory_{task}_chunk{c}_{kind}.json"
                          for kind in ("audit","original4")})
    require(set(pairs)==names,"Archive full denominator/manifest mismatch")
    for path,digest in pairs.items():
        require(hashlib.sha256((directory/path).read_bytes()).hexdigest()==digest,
                "Original study bytes changed "+path)
    return pairs

def evaluate(directory):
    sha=source_provenance(directory)
    result={}
    all_retro=[]
    for task,first in BASELINE_TASKS.items():
        rows=[]
        for chunk in range(4):
            d=json.loads((directory/f"public_fourhistory_{task}_chunk{chunk}_audit.json").read_text())
            require(len(d["sample_rows"])==4 and d["seeds"]==list(range(first+4*chunk,first+4*chunk+4)),
                    "Missing original paired source reset")
            rows.extend(d["sample_rows"])
        require(len(rows)==16 and [x["seed"] for x in rows]==list(range(first,first+16)),
                "Changed full task seed population")
        cnt={"n":16,"original_public_labels":0,"retrospective_singletons":0,
             "retrospective_with_two_mm_clearance":0,
             "after_audit_true_full_pose_matches":0,"posthoc_wrong":0,
             "full_fixed_query":0,"accepted_explanatory_records":[]}
        for row in rows:
            ev=row["new_public_evidence"]
            epsilon=ev["prior_training_epsilon_m"]
            residuals=ev["candidate_residuals_m"]
            need=ev["accepted_position_indices"]
            require(all(isinstance(x,(int,float)) and math.isfinite(x) and x>=0 for x in residuals),
                    "Invalid old original physical residual")
            recomputed=[i for i,x in enumerate(residuals) if x<=epsilon+1e-12]
            require(recomputed==need and ev["physical_candidate_count"]==len(residuals),
                    "Old source compatible indices do not match fixed model")
            cnt["original_public_labels"]+=int(ev["authorized"])
            cnt["full_fixed_query"]+=row["new_reads"]
            if len(need)==1:
                cnt["retrospective_singletons"]+=1
                index=need[0]
                if all(x>epsilon+MARGIN for i,x in enumerate(residuals) if i!=index):
                    cnt["retrospective_with_two_mm_clearance"]+=1
                    match=index in ev["audit_only_true_candidate_indices"]
                    cnt["after_audit_true_full_pose_matches"]+=int(match)
                    cnt["posthoc_wrong"]+=int(not match)
                    cnt["accepted_explanatory_records"].append({
                        "seed":row["seed"],"winner":index,
                        "posthoc_audit_true_pose_match":match,
                        "original_rotational_disagreement_rad":
                         ev["max_hypothetical_rotation_spread_rad"],
                        "ALL_ABLATION_RESULTS_ARE_POST_HOC":True})
        result[task]=cnt
        all_retro.extend(cnt["accepted_explanatory_records"])
    totals={
        "full_original_states":32,
        "old_confident":sum(x["original_public_labels"] for x in result.values()),
        "retrospective_unique_position_indices":sum(x["retrospective_with_two_mm_clearance"] for x in result.values()),
        "posthoc_true_full_pose_matches":sum(x["after_audit_true_full_pose_matches"] for x in result.values()),
        "posthoc_wrong_full_pose":sum(x["posthoc_wrong"] for x in result.values()),
        "original_privileged_reads":sum(x["full_fixed_query"] for x in result.values()),
    }
    require(totals=={
        "full_original_states":32,"old_confident":0,
        "retrospective_unique_position_indices":12,
        "posthoc_true_full_pose_matches":12,
        "posthoc_wrong_full_pose":0,"original_privileged_reads":32
    },"Original 32-state retrospective source result changed")
    return {"schema":"retrospective_exposed_fourhistory_fullpose_reanalysis_v1",
            "prospective_method_result":False,
            "source_hashes":sha,"tasks":result,"totals":totals,
            "limitations":[
                "Already observed original 32 task seeds; CANNOT establish new-policy prospective benefit",
                "Ground-truth pose used ONLY to retrospectively grade candidates",
                "No SO3 observation was generated: complete target orientation inherited from known candidate",
                "Historical error envelope not physically guaranteed",
                "No new native PhysX episode/third-party external reproduction"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=BASE)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    q=evaluate(args.source)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(q,sort_keys=True,indent=2)+"\n")
    print("HISTORICAL_FOURHISTORY_POSITION_SURVIVOR_SOURCE_AUDIT",
          json.dumps(q["totals"],sort_keys=True))

if __name__=="__main__":main()
