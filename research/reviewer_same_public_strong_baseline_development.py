"""Source-anchored same-information baseline strength audit, DEVELOPMENT ONLY.

Recompute candidate authorization and correctness using historical physical
candidate residuals and auditor-only true target indices. This does NOT rerun
the controller, does NOT infer counterfactual task success, and does not
provide prospective evidence for thresholds chosen from these same cases.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path

ROOT=Path("research/frozen_policy_transfer/evidence/matched_same_public_bayes_original64_1760001_1770032")
FULL_HISTORY="public_t3_evidence"
SCORE="same_sensor_posterior_evidence"
TASKS=("pull_cube","stack_cube")
THRESHOLDS=(0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95)
EXPECTED_ORIGINAL_SEEDS={"pull_cube":list(range(1760001,1760033)),
                         "stack_cube":list(range(1770001,1770033))}

def study(directory=ROOT):
    rows=[]
    original_file_digests={}
    for task in TASKS:
        actual=[]
        for chunk in range(4):
            name=f"bayes_same_public_{task}_chunk{chunk}_original8.json"
            path=directory/name
            raw=path.read_bytes()
            original_file_digests[name]=hashlib.sha256(raw).hexdigest()
            source=json.loads(raw)
            if source["task"]!=("PullCube-v1" if task=="pull_cube" else "StackCube-v1"):
                raise ValueError("Wrong original PPO task source")
            actual.extend(source["episodes"])
        if [q["seed"] for q in actual]!=EXPECTED_ORIGINAL_SEEDS[task]:
            raise ValueError("Missing/reused original training reset identity")
        for q in actual:
            unique=q[FULL_HISTORY]
            shape=q[SCORE]
            if len(shape["posterior_weights"])<1 or len(shape["posterior_weights"])!=len(shape["candidate_residuals_m"]):
                raise ValueError("Missing same-public original posterior-shaped evidence")
            weights=shape["posterior_weights"]
            k=max(range(len(weights)),key=lambda j:weights[j])
            eps=shape["prior_training_epsilon_m"]
            good=(shape["candidate_residuals_m"][k]<=eps and bool(shape["audit_only_true_candidate_indices"]))
            physical_truth=(k in shape["audit_only_true_candidate_indices"])
            margin=(len(unique["accepted_position_indices"])==1 and
                all(z>eps+.002 for i,z in enumerate(unique["candidate_residuals_m"])
                    if i!=unique["accepted_position_indices"][0]))
            if unique["authorized"] is not bool(margin):
                raise ValueError("Previous native set membership changed")
            if unique["wrong_confident"] is not bool(unique["authorized"] and not
                 unique["selected_candidate_index"] in unique["audit_only_true_candidate_indices"]):
                raise ValueError("Previous original wrong authority audit was edited")
            rows.append(dict(task=task,seed=q["seed"],weights=weights,winner=k,max_score=weights[k],
                             eps=eps,eligible_score_residual=good,physical_true_winner=physical_truth,
                             original_set_unique=unique["authorized"],
                             original_set_wrong=unique["wrong_confident"],
                             physical_truth_indices=shape["audit_only_true_candidate_indices"]))
    if len(rows)!=64:raise ValueError("Training denominator not 64")
    variants={}
    for threshold in THRESHOLDS:
        for rule in ("score_only","unique_plus_score"):
            selected=[r for r in rows if r["max_score"]+1e-12>=threshold and
                r["eligible_score_residual"] and (rule=="score_only" or
                (r["original_set_unique"] and r["winner"]==
                 next(iter(r["physical_truth_indices"]),-1) if False else
                 r["original_set_unique"] and r["winner"]==_original_set_winner(directory,r["task"],r["seed"])))]
            variants[f"{rule}_{threshold:.2f}"]={
                "source_training_score_threshold":threshold,
                "n_confident_histories":len(selected),
                "n_incorrect_confident_histories":sum(not r["physical_true_winner"] for r in selected),
                "number_privileged_reads_if_unchanged_single_gate_logic":64-len(selected),
                "NOT_executed_counterfactual_task_success":True,
                "per_task":{task:{"confident":sum(x["task"]==task for x in selected),
                                  "wrong":sum(x["task"]==task and not x["physical_true_winner"] for x in selected)}
                            for task in TASKS}}
    old=[r for r in rows if r["original_set_unique"]]
    return {"schema":"full_source_development_only_same_public_strong_score_comparator_v1",
            "independently_executed_baselines_at_each_threshold":False,
            "training_dataset_was_inspected_to_select_dual_0_65":True,
            "outside_new64_prospective_method_results_NOT_USED":True,
            "original_training_n":len(rows),"original_source_SHA256":original_file_digests,
            "original_set_confident":len(old),
            "original_set_wrong":sum(r["original_set_wrong"] for r in old),
            "threshold_sensitivity":variants,
            "interpretation":"A 0.60 source-trained SCORE-ONLY competitor already predicts 17 authorizations, 0 observed wrong on this training cohort. It must be physically stepped on independent held-out seeds before claiming task success/latency safety; the 0.95 comparator is intentionally conservative and NOT a strong calibrated Bayesian optimum."}

def _original_set_winner(folder,task,seed):
    chunk=(seed-(1760001 if task=="pull_cube" else 1770001))//8
    path=folder/f"bayes_same_public_{task}_chunk{chunk}_original8.json"
    d=json.loads(path.read_text())
    row=next(q for q in d["episodes"] if q["seed"]==seed)
    return row[FULL_HISTORY]["selected_candidate_index"]

def main():
    p=argparse.ArgumentParser();p.add_argument("--source-dir",type=Path,default=ROOT)
    p.add_argument("--output",type=Path);args=p.parse_args()
    x=study(args.source_dir)
    if args.output:args.output.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("STRONGER_DEVELOPMENT_BASELINE_NOT_FROZEN_PHYSX",json.dumps({
       "n":64,"source_score_only_at_060":x["threshold_sensitivity"]["score_only_0.60"],
       "unique_plus_score_065":x["threshold_sensitivity"]["unique_plus_score_0.65"],
       "original_set_wrong":x["original_set_wrong"]},sort_keys=True))
if __name__=="__main__":main()
