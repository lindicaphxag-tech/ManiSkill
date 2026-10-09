"""Falsifiable 32-seed-cluster difference-in-differences and exact paired audit.

Data are ORIGINAL amended physical source rows; no trial filtering, no
treating 128 correlated seed/truth cells as 128 iid samples, no calibrated
robot safety or formal superiority claims.
"""
from __future__ import annotations
import argparse,json,random
from pathlib import Path
from research.audit_same_reset_ack_factorial import audit, exact_cluster_swap_p
from research.run_same_reset_ack_factorial import truth

METHODS=("public","strong_task","fixed_t5","always_held")

def percentile(xs,q):
    s=sorted(xs)
    k=(len(s)-1)*q
    lo=int(k);lam=k-lo
    return (1-lam)*s[lo]+lam*s[min(lo+1,len(s)-1)]

def method_value(row,method):
    return bool(row[{"public":"new_success","strong_task":"strong_success",
                     "fixed_t5":"fixed_success","always_held":"held_success"}[method]])

def source_analysis(sources, draws=5000):
    orig=audit(sources)  # FIRST still-fail-on-hash strict source auditor
    rows=orig["all_source_rows_retained"]
    grouped={}
    for row in rows:
        key=(row["task"],row["seed"])
        grouped.setdefault(key,{})[row["truth_index"]]=row
    if len(grouped)!=32 or any(set(c)!=set(range(4)) for c in grouped.values()):
        raise ValueError("Full 32 x four genuine native source conditions required")
    keys=sorted(grouped)
    diff={key:sum(int(method_value(grouped[key][t],"public"))-
                      int(method_value(grouped[key][t],"strong_task"))
                      for t in range(4)) for key in keys}
    if sum(diff.values())!=7 or orig["primary_outcomes"]["public"]["official_task_success"]!=111:
        raise ValueError("Observed original evidence unexpected; do not rewrite proven outcomes")
    rand=random.Random(20261009)
    cluster_delta=[]
    public_did=[]
    strong_did=[]
    for _ in range(draws):
        sampled=[keys[rand.randrange(len(keys))] for __ in keys]
        cluster_delta.append(sum(diff[x] for x in sampled)/(4*len(sampled)))
        public_did.append(sum(
           int(method_value(grouped[k][3],"public"))-
           int(method_value(grouped[k][1],"public"))-
           int(method_value(grouped[k][2],"public"))+
           int(method_value(grouped[k][0],"public"))
           for k in sampled)/len(sampled))
        strong_did.append(sum(
           int(method_value(grouped[k][3],"strong_task"))-
           int(method_value(grouped[k][1],"strong_task"))-
           int(method_value(grouped[k][2],"strong_task"))+
           int(method_value(grouped[k][0],"strong_task"))
           for k in sampled)/len(sampled))
    true_strata={}
    for task in ("pull_cube","stack_cube"):
        for t in range(4):
            part=[grouped[k][t] for k in keys if k[0]==task]
            if len(part)!=16:raise ValueError("Incomplete same initial reset task/truth group")
            true_strata[f"{task}/{'/'.join(truth(t))}"]={
              "original_n":16,
              "public_success":sum(method_value(r,"public") for r in part),
              "strong_success":sum(method_value(r,"strong_task") for r in part),
              "fixed_success":sum(method_value(r,"fixed_t5") for r in part),
              "public_minus_strong_success":sum(
                  int(method_value(r,"public"))-int(method_value(r,"strong_task"))
                  for r in part),
              "public_private_reads":sum(r["new_reads"] for r in part),
              "strong_private_reads":sum(r["strong_reads"] for r in part),
              "public_confident":sum(r["public_authorized"] is True for r in part),
              "public_confident_wrong":sum(r["wrong_confident"] is True for r in part),
              "actually_exposed_both_unknown_ACKs":sum(r["public_both_faults_exposed"] for r in part),
              "all_faulted_comparators_stepped_paid_neutral":sum(
                   r["all_faulted_arms_received_neutral_probe"] for r in part)
            }
    interaction={}
    for method in ("public","strong_task"):
        vals={key:int(method_value(grouped[key][3],method))-
                 int(method_value(grouped[key][1],method))-
                 int(method_value(grouped[key][2],method))+
                 int(method_value(grouped[key][0],method))
              for key in keys}
        sims=public_did if method=="public" else strong_did
        interaction[method]={
             "four_truth_interaction_mean_per_seed":sum(vals.values())/len(vals),
             "exploratory_seed_cluster_bootstrap_95pct_interval":[percentile(sims,.025),percentile(sims,.975)],
             "not_a_causal_interaction_claim_without_consistent_native_policy_post_fault":True}
    return {
      "schema":"honest_amended_32_seed_physical_2x2_factorial_reviewer_v1",
      "original_failure_run":"37930607707",
      "source_amended_physics_run":"37931800065",
      "source_first_attempt_failures_publicly_preserved":True,
      "original_true_source_seed_clusters":32,
      "original_physical_reset_condition_cells":128,
      "true_actual_native_PhysX_controller_world_instances":1152,
      "four_truths_each_same_initial_physical_source_observation_hash_verified":True,
      "all_128_states_kept_including_early_failure":True,
      "primary":orig["primary_outcomes"],
      "paired":orig["paired_public_vs_strong"],
      "original_actual_public_xyz_sample_events":orig["total_public_xyz_sample_events"],
      "observed_confidently_wrong":orig["public_wrong_confident_count"],
      "fully_double_fault_exposure_ITT_count":128-orig["incomplete_both_fault_exposure_count"],
      "nonfully_exposed_retain_in_ITT":orig["incomplete_both_fault_exposure_count"],
      "observed_public_minus_strong_per_cell_success_delta":sum(diff.values())/128,
      "exact_seed_cluster_label_swap_two_sided_sensitivity_p":exact_cluster_swap_p(list(diff.values())),
      "exploratory_32_cluster_bootstrap_public_minus_strong_success_gap_95pct":[
           percentile(cluster_delta,.025),percentile(cluster_delta,.975)],
      "task_by_true_execution_strata":true_strata,
      "within_seed_four_truth_interaction":interaction,
      "claims_not_established":["Formal statistical superiority","Genuine unchanged first preregistration",
                                "Robot controller safe to act","VLA task level success","External independent experiment",
                                "All native fault-arm probes actually reached if early failure"],
      "original_sha256_source_files":orig["complete_16_shard_sha256"]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    q=source_analysis(a.source_dir)
    a.output.write_text(json.dumps(q,sort_keys=True,indent=2)+"\n")
    print("HONEST_NATIVE_FACTORIAL_32_SEED_CLUSTER_REVIEW",json.dumps({
        "successes":q["primary"],
        "confident_wrong":q["observed_confidently_wrong"],
        "paired":q["paired"],
        "cluster_p":q["exact_seed_cluster_label_swap_two_sided_sensitivity_p"],
        "ITT_both_fault_exposed":q["fully_double_fault_exposure_ITT_count"],
        "bootstrap_success_diff95":q["exploratory_32_cluster_bootstrap_public_minus_strong_success_gap_95pct"],
        "interaction":q["within_seed_four_truth_interaction"]},sort_keys=True))
if __name__=="__main__":main()
