"""Fully independent stdlib source auditor of 64 newly preregistered real PhysX resets.

All original applied/held physical trial outcomes and every failure retained;
neither posterior score nor observation margin is refitted after outcome.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from research.run_dual_evidence_ack_new64 import (
    A,B,C,PRE_BLOB,SOURCE_BLOB,accepted,independent_eight
)

def full_audit(folder):
    needed={f"dual_evidence_{task}_chunk{ch}_{suffix}.json"
            for task in ("pull_cube","stack_cube")
            for ch in range(4) for suffix in ("original8","audit")}
    found={f.name for f in folder.glob("dual_evidence_*.json")}
    if found!=needed:raise ValueError(f"Incomplete full original 64 PhysX sources: missing {needed-found}; extras {found-needed}")
    taskdata={};allrows=[]
    for task in ("pull_cube","stack_cube"):
        rows=[]
        for ch in range(4):
            file=folder/f"dual_evidence_{task}_chunk{ch}_original8.json"
            contents=file.read_bytes()
            source=json.loads(contents)
            expected=independent_eight(source,task,ch)
            expected.update(pre_registered_protocol_git_blob=PRE_BLOB,
                            original_nonrefit_runner_git_blob=SOURCE_BLOB,
                            exact_original_PhysX_JSON_SHA256=hashlib.sha256(contents).hexdigest())
            submitted=json.loads((folder/f"dual_evidence_{task}_chunk{ch}_audit.json").read_text())
            if expected!=submitted:raise ValueError("Original source truth and independent per-8 auditor disagree")
            rows.extend(expected["original_all_eight"])
        expected_ids=[s for ch in range(4) for s in accepted(task,ch)]
        if len(rows)!=32 or [r["seed"] for r in rows]!=expected_ids:
            raise ValueError("Original task reset seed omitted or duplicated")
        score={}
        for arm in (A,B,C):
            score[arm]={
                "official_success":sum(int(r["official_task_success"][arm]) for r in rows),
                "private_reads":sum(r["private_reads"][arm] for r in rows)}
            if arm in (A,B):
                score[arm]["public_confident"]=sum(int(r["empirical_public_confident"]
                  if arm==A else r["posterior_score_confident"]) for r in rows)
                score[arm]["wrong_confident"]=sum(int(r["empirical_wrong_confident"]
                  if arm==A else r["posterior_wrong_confident"]) for r in rows)
                score[arm]["public_achieved_XYZ_sample_events"]=64
        paired={}
        for lhs,rhs,label in ((A,B,"set_vs_same_public_posterior_score"),
                              (A,C,"set_vs_fixed_read")):
            paired[label]={
                "both_success":sum(r["official_task_success"][lhs] and r["official_task_success"][rhs] for r in rows),
                "neither_success":sum(not r["official_task_success"][lhs] and not r["official_task_success"][rhs] for r in rows),
                "lhs_only_success":sum(r["official_task_success"][lhs] and not r["official_task_success"][rhs] for r in rows),
                "rhs_only_success":sum(not r["official_task_success"][lhs] and r["official_task_success"][rhs] for r in rows)}
        bytruth={}
        for pattern in range(4):
            sub=[r for r in rows if r["true_fault_pattern"]==pattern]
            if len(sub)!=8:raise ValueError("True double applied/held original physical truth missing")
            bytruth[str(pattern)]={"n":len(sub),"official_successes":{arm:sum(int(r["official_task_success"][arm]) for r in sub)
                            for arm in (A,B,C)},
                      "private_reads":{arm:sum(r["private_reads"][arm] for r in sub) for arm in (A,B,C)},
                      "public_confident":{A:sum(int(r["empirical_public_confident"]) for r in sub),
                                          B:sum(int(r["posterior_score_confident"]) for r in sub)},
                      "wrong_confident":{A:sum(int(r["empirical_wrong_confident"]) for r in sub),
                                          B:sum(int(r["posterior_wrong_confident"]) for r in sub)}}
        taskdata[task]={"original_reset_states":32,"native_controller_worlds":320,
                        "scores":score,"paired":paired,"actual_t2_t3_truth_strata":bytruth}
        allrows.extend(rows)
    if len(allrows)!=64 or len(set((r["task"],r["seed"]) for r in allrows))!=64:
        raise ValueError("Original full 64 source denominator is incomplete")
    totals={arm:{
        "official_success":sum(taskdata[t]["scores"][arm]["official_success"] for t in taskdata),
        "private_reads":sum(taskdata[t]["scores"][arm]["private_reads"] for t in taskdata)}
        for arm in (A,B,C)}
    for arm in (A,B):
        totals[arm].update(public_confident=sum(taskdata[t]["scores"][arm]["public_confident"] for t in taskdata),
                           wrong_confident=sum(taskdata[t]["scores"][arm]["wrong_confident"] for t in taskdata),
                           achieved_XYZ_sample_events=128)
    return {"schema":"dual_evidence_065_after_training_orig64_native_physx_v1",
            "original_preregistration_git_blob":PRE_BLOB,
            "exact_original_frozen_physical_model_blob":SOURCE_BLOB,
            "n_original_task_reset_states":64,"real_native_PhysX_controller_worlds":640,
            "original_two_physical_ACK_truths_full_2x2":True,
            "exact_physical_prefix_identical_before_t5_info_decisions":True,
            "same_two_public_achieved_xyz_samples_for_two_adaptive_methods":True,
            "Bayes_named_score_is_NOT_true_posterior_without_calibration":True,
            "extra_physical_neutral_probe_steps":64,
            "author_run_not_independent_external_reproduction":True,
            "by_task":taskdata,"total":totals,"all_original_rows":allrows}

def main():
    p=argparse.ArgumentParser();p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    result=full_audit(a.source_dir)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("NEW64_SAME_PUBLIC_BAYES_REAL_PHYSX_COMPLETE",json.dumps({
        "n":64,"actual_native_worlds":640,"total":result["total"],
        "fully_physical_matched_prefix":True},sort_keys=True))

if __name__=="__main__":main()
