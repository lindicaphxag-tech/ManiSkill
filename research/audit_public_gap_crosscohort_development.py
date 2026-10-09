"""RESEARCH EXPLORATORY source-only cross-cohort audit, NOT an online policy or proof.

Reads immutable ORIGINAL native PhysX files from two distinct author-run source
cohorts. A counterfactual extra 4.5-mm public evidence gate can be diagnosed
for wrong histories / theoretical query requirements. It has NOT been actually
executed against these OLD physical task rollouts. Do not infer task outcomes
under a newly decided query from old trajectories.

Run with --cohort1 and --cohort2 paths and --out report.json.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

PUBLIC = "fault_public_t3_fourhistory_or_t4_query"
GAP_M = 0.0045
COHORTS = {
 "development_148_149": {
   "expected_seeds": {"PullCube-v1":(1480001,1480032),"StackCube-v1":(1490001,1490032)},
   "prefix":"sharedcompiler_","suffix":"_original8.json",
 },
 "challenge_172_173_already_seen_when_gate_chosen": {
   "expected_seeds": {"PullCube-v1":(1720001,1720032),"StackCube-v1":(1730001,1730032)},
   "prefix":"","suffix":"_original8.json",
 }
}

def truth_for(seed):
    i=(seed-1)%4
    return ("applied" if i in (1,3) else "held",
            "applied" if i in (2,3) else "held")

def source_rows(path,tag):
    cfg=COHORTS[tag]
    files=sorted(p for p in path.glob("*"+cfg["suffix"])
                 if p.name.startswith(cfg["prefix"]))
    if len(files)!=8:
        raise ValueError(f"{tag}: expected precisely 8 original source shards, found {len(files)}")
    sha=[]
    rows=[]
    for p in files:
        source=p.read_bytes()
        sha.append({"name":p.name,"sha256":hashlib.sha256(source).hexdigest()})
        d=json.loads(source) # Python explicitly retains NaN/Infinity from original simulation.
        if d["real_physx_simulator"] is not True or len(d["episodes"])!=8:
            raise ValueError("Not eight original native PhysX source episodes")
        for ep in d["episodes"]:
            seed=ep["seed"]
            task=ep["task"]
            if task not in cfg["expected_seeds"]:
                raise ValueError("Unknown task")
            t2,t3=truth_for(seed)
            if (ep["original_precommitted_physical_t2_execution_truth"],ep["original_precommitted_physical_t3_execution_truth"])!=(t2,t3):
                raise ValueError("Original physical truth drift")
            ev=ep["public_t3_evidence"]
            ds=[float(x) for x in ev["candidate_residuals_m"]]
            if len(ds) not in (2,3,4) or not all(math.isfinite(x) and x>=0 for x in ds):
                raise ValueError("Invalid observed candidate residual vector")
            eps=float(ev["prior_training_epsilon_m"])
            winners=[i for i,x in enumerate(ds) if x<=eps+1e-12]
            orig=bool(len(winners)==1 and all(
                x>eps+0.002 for i,x in enumerate(ds) if i!=winners[0]))
            if ev["authorized"] is not orig:
                raise ValueError("Original published residual admission rule mismatch")
            if (ev.get("wrong_confident") is True)!=(orig and ev.get("selected_candidate_index") not in ev["audit_only_true_candidate_indices"]):
                raise ValueError("Original wrong-confidence audit drift")
            gaps=sorted(ds)
            gap=gaps[1]-gaps[0]
            calibrated=orig and gap>=GAP_M
            reads=ep["privileged_target_readback_decision_count"][PUBLIC]
            if reads!=int(not orig):
                raise ValueError("Original charged source reads inconsistent")
            if ep["public_motion_observation_cost_samples"].get(PUBLIC)!=2:
                raise ValueError("Public signal budget diverged")
            if [f["step"] for f in ep["faults"][PUBLIC]]!=[2,3]:
                raise ValueError("Both physically injected unknown ACKs not reached")
            parity=ep["matched_prefix_physical_audit"]
            if not parity.get("valid_exact_prefix") or max(parity["native_fault_dispatch_linf_each"])>5e-5:
                raise ValueError("Not a matched-prefix physical source")
            rows.append({
                "task":task,"seed":seed,"t2_truth":t2,"t3_truth":t3,
                "source_public_authorized":orig,
                "source_public_wrong":bool(ev["wrong_confident"]),
                "public_residual_first_second_gap_m":gap,
                "gap_counterfactual_would_authorize":calibrated,
                "gap_counterfactual_wrong_if_authorized":bool(calibrated and ev["wrong_confident"]),
                "original_public_task_success":bool(ep["success_once"][PUBLIC]),
                "original_public_charged_private_reads":reads,
                "would_charge_private_read_IF_policy_actually_reexecuted":int(not calibrated),
                "counterfactual_task_success_UNKNOWN_no_world_stepped":True,
            })
    expected={(t,s) for t,(lo,hi) in cfg["expected_seeds"].items() for s in range(lo,hi+1)}
    actual={(r["task"],r["seed"]) for r in rows}
    if len(rows)!=64 or actual!=expected:
        raise ValueError(f"Incomplete original 64 source states; expected {len(expected)}, actual {len(actual)}")
    return rows,sha

def aggregate(rows):
    groups={"all_64":rows}
    for task in ("PullCube-v1","StackCube-v1"):
        groups[task]=[x for x in rows if x["task"]==task]
    result={}
    for name,rr in groups.items():
        result[name]={
            "n":len(rr),
            "original_public_admissions":sum(x["source_public_authorized"] for x in rr),
            "original_public_wrong":sum(x["source_public_wrong"] for x in rr),
            "counterfactual_gap_admissions":sum(x["gap_counterfactual_would_authorize"] for x in rr),
            "counterfactual_wrong":sum(x["gap_counterfactual_wrong_if_authorized"] for x in rr),
            "counterfactual_private_reads_IF_reexecuted":sum(x["would_charge_private_read_IF_policy_actually_reexecuted"] for x in rr),
            "actual_prior_public_task_success":sum(x["original_public_task_success"] for x in rr),
            "gap_rule_task_success":None,
        }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cohort1",type=Path,required=True)
    ap.add_argument("--cohort2",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    a,hash_a=source_rows(args.cohort1,"development_148_149")
    b,hash_b=source_rows(args.cohort2,"challenge_172_173_already_seen_when_gate_chosen")
    wrong=[r for r in b if r["source_public_wrong"]]
    if len(wrong)!=1 or wrong[0]["seed"]!=1730027:
        raise ValueError("Prior known wrong history must be retained as negative evidence")
    doc={
        "schema":"EXPLORATORY_ORIGINAL_PHYSX_CROSSCOHORT_PUBLIC_GAP_AUDIT_V1",
        "not_prospective_gate_validation":True,
        "not_online_policy_execution":True,
        "no_task_outcome_counterfactual_inference":True,
        "training_rule_posthoc_selected_after_second_cohort":True,
        "author_controlled_not_outside_lab":True,
        "gap_threshold_m":GAP_M,
        "physical_source_origins":{
            "cohort1_sha256":hash_a,
            "cohort2_sha256":hash_b,
        },
        "source_populations":{
           "development_148_149":aggregate(a),
           "challenge_172_173_already_seen_when_gate_chosen":aggregate(b),
        },
        "all_128_original_source_cases":a+b,
        "one_known_wrong_public_history":{
            "task":wrong[0]["task"],"seed":wrong[0]["seed"],
            "original_public_gap_m":wrong[0]["public_residual_first_second_gap_m"],
            "posthoc_gate_would_have_queried_instead":not wrong[0]["gap_counterfactual_would_authorize"],
        },
        "interpretation":"Retrospective feasibility only. Prove intervention through prospective exact frozen margin controller actual ManiSkill steps on seed-disjoint task states. No VLA or hardware safety claim."
    }
    args.out.write_text(json.dumps(doc,sort_keys=True,indent=2)+"\n")
    print("EXPLORATORY_CROSSCOHORT_ORIGINAL_SOURCE_PUBLIC_MARGIN_AUDIT",json.dumps({
       "cohort1":doc["source_populations"]["development_148_149"]["all_64"],
       "cohort2":doc["source_populations"]["challenge_172_173_already_seen_when_gate_chosen"]["all_64"],
       "wrong_seed":wrong[0]["seed"],
       "retro_falsified_zero_error":True,
    },sort_keys=True))

if __name__=="__main__":
    main()
