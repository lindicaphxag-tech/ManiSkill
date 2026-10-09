"""Cluster-correct selective history-risk + cost accounting for original 2x2 PhysX.

32 independent task-reset clusters, EACH expanded into four correlated
genuinely stepped ACK physical truths. Accepted EVENT count is not an
independent statistical sample count. The 0-error risk bound is reported
over cluster-wise ANY-WRONG among reset IDs with >=1 admission; this is
a different estimand from per-authorized-decision risk.

Original data: first true source run 37944800521. Auditor verifies all
original SHA/provenance, 128 condition cells, 1280 actual robot-controller
worlds and exact paired physical prefix before any descriptive analysis.
No claim of independent third-party physics execution or hardware safety.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from math import comb, isfinite
from pathlib import Path

from research.audit_query_isolated_same_reset_factorial128 import analyze
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
C="fault_always_single_privileged_query"
ARMS=(A,B,C)
EVIDENCE=Path(__file__).resolve().parent/"frozen_policy_transfer/evidence/isolated_query_factorial128_first_3010001_3020016"

def _cdf_le(k:int,n:int,p:float)->float:
    if k<0:return 0.
    if k>=n:return 1.
    return sum(comb(n,j)*p**j*(1-p)**(n-j) for j in range(k+1))

def exact_one_sided_upper(k:int,n:int,tail:float=.05)->float:
    if not (type(k) is int and type(n) is int and 0<=k<=n and 0<tail<1):
        raise ValueError("Invalid group-correct binomial count or error budget")
    if n==0 or k==n:return 1.
    lo,hi=0.,1.
    for _ in range(65):
        mid=(lo+hi)/2
        if _cdf_le(k,n,mid)>tail:lo=mid
        else:hi=mid
    return hi

def analyze_clustering(source:EVIDENCE.__class__=EVIDENCE):
    original=analyze(source)  # physical source, 16 SHA256s, four-truth native prefixes
    cells=original["all_orig_source_seed_cell_vectors"]
    if len(cells)!=128:raise ValueError("Original 128 factual ACK cells missing")
    clusters=defaultdict(list)
    for x in cells:
        clusters[(x["task"],x["seed"])].append(x)
    if (len(clusters)!=32 or
        any(len(rows)!=4 or {x["truth"] for x in rows}!={0,1,2,3}
            for rows in clusters.values())):
        raise ValueError("Cannot treat a partial four-truth cluster as full scientific evidence")
    per_task={}
    for task in ("pull_cube","stack_cube"):
        cases=[x for (t,_),x in clusters.items() if t==task]
        if len(cases)!=16:raise ValueError("Pre-registered task reset denominator changed")
        per_task[task]=_stats(cases)
    allcases=list(clusters.values())
    pooled=_stats(allcases)
    original_all=original["all_cells"]
    for arm in ARMS:
        if (pooled["strategy"][arm]["official_successes"] != original_all[arm]["success"]
            or pooled["strategy"][arm]["true_target_reads"] != original_all[arm]["private_reads"]
            or pooled["strategy"][arm]["accepted_events"] != original_all[arm]["total_authorizations"]
            or pooled["strategy"][arm]["wrong_events"] != original_all[arm]["wrong_confident_authorizations"]):
            raise ValueError("Original independently audited factored PhysX source mutated")
    if not (
      pooled["strategy"][A]["accepted_events"]==26
      and pooled["strategy"][A]["accepted_clusters"]==20
      and pooled["strategy"][A]["wrong_clusters"]==0
      and pooled["strategy"][C]["true_target_reads"]==127
      and per_task["pull_cube"]["strategy"][A]["accepted_clusters"]==10
      and per_task["stack_cube"]["strategy"][A]["accepted_clusters"]==10
    ):raise ValueError("Original facts/source reset clustering changed")
    return {
       "status":"FIRST_SOURCE_VERIFIED_DESCRIPTIVE_CLUSTER_RISK_NOT_INDEPENDENT_PHYSX_REPLAY",
       "original_run_id":37944800521,
       "real_task_reset_independent_sample_units":32,
       "correlated_physical_ACK_truth_cells":128,
       "actual_native_PhysX_controller_worlds":1280,
       "pooled":pooled,
       "per_task":per_task,
       "error_statement":"CP risk estimand = P(at least one wrongly authorized full target history among FOUR ACK truth conditions | this independent reset has >=1 authorized condition); NOT P(wrong | event authorized) nor hardware risk.",
       "assumptions":["Original reset clusters IID within fixed task under stable physical/sensor model; four condition outcomes allowed arbitrary within-cluster dependence.",
                      "The admitted cluster subset must be exchangeable as selected draws from the same frozen source distribution.",
                      "CP bounds are descriptive/post-hoc and do not guarantee validity after new model selection, contact shift or multiple-comparison tuning."],
       "native_task_paired_differences_A_vs_C":{
          "A_only":original["exact_CLUSTER_level_pairwise_exploratory"][C]["A_only"],
          "fixed_only":original["exact_CLUSTER_level_pairwise_exploratory"][C]["control_only"],
          "cluster_exact_sign_flip_p_exploratory":original["exact_CLUSTER_level_pairwise_exploratory"][C]["exact_cluster_method_label_swap_p_EXPLORATORY"]
       },
       "strict_claim_vetoes":[
           "128 independent reset states or 1280 independent robots",
           "Safety guarantee from zero wrong public authorizations in 26 correlated decisions",
           "Confident incorrect-history risk below 10% at confidence 95% for A",
           "Official ActionShift DualABI or calibrated Bayesian posterior SOTA",
           "Task success improvement despite exactly identical per-cell task outcomes",
           "Third party independent actual PhysX execution",
       ],
    }

def _stats(cases):
    out={}
    for arm in ARMS:
        allrows=[r for rr in cases for r in rr]
        wrong_events=sum(bool(x["wrong"].get(arm,False)) for x in allrows)
        accept_events=sum(bool(x["confidence"].get(arm,False)) for x in allrows)
        authorized_clusters=[rr for rr in cases if any(x["confidence"].get(arm,False) for x in rr)]
        wrong_cluster=sum(any(x["wrong"].get(arm,False) for x in rr) for rr in authorized_clusters)
        if any(x["wrong"].get(arm,False) and not x["confidence"].get(arm,False) for x in allrows):
            raise ValueError("Source wrong without any confidence authorization")
        out[arm]={
          "original_reset_clusters":len(cases),
          "correlated_truth_cells":len(allrows),
          "official_successes":sum(x["success"][arm] for x in allrows),
          "true_target_reads":sum(x["reads"][arm] for x in allrows),
          "public_xyz_observation_events":sum(x["public_xyz"][arm] for x in allrows),
          "accepted_events":accept_events,
          "wrong_events":wrong_events,
          "accepted_clusters":len(authorized_clusters),
          "wrong_clusters":wrong_cluster,
          "exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid":
                exact_one_sided_upper(wrong_cluster,len(authorized_clusters)),
          "naive_per_decision_iid_95pct_upper_NOT_JUSTIFIED":
                exact_one_sided_upper(wrong_events,accept_events)
        }
    return {"strategy":out}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=EVIDENCE)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyze_clustering(a.source)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    v=result["pooled"]["strategy"]
    print("FIRST_128_CLUSTER_RISK",json.dumps({
      "n_reset_clusters":32,"n_truth_cells":128,
      "accepted_reset_clusters":v[A]["accepted_clusters"],
      "accepted_events":v[A]["accepted_events"],
      "wrong_confident_events":v[A]["wrong_events"],
      "upper_any_wrong_per_authorized_reset":v[A]["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],
      "A_reads":v[A]["true_target_reads"],
      "B_reads":v[B]["true_target_reads"],
      "C_reads":v[C]["true_target_reads"],
      "original_successes":[v[z]["official_successes"] for z in ARMS]
    },sort_keys=True))

if __name__=="__main__":main()
