"""Reviewer's source-only full-cost, matched-pair and uncertainty calculator.

Runs on the unchanged original 64 PhysX JSONs and independently reconstructed
64-row complete denominator. Original threshold decisions are NOT refitted.
Bayes-shaped residual weights are heuristic, NOT calibrated posterior truth.
"""
from __future__ import annotations
import argparse,json,math,random
from pathlib import Path
from research.audit_matched_public_bayes_new64 import full_audit
from research.run_matched_public_bayes_new64 import A,B,C

def exact_two_sided_discordance(only_left,only_right):
    n=only_left+only_right
    if not n:return 1.0
    k=min(only_left,only_right)
    return min(1.,2*sum(math.comb(n,i) for i in range(k+1))/(2**n))

def quantiles(values,ps=(.025,.975)):
    nums=sorted(values)
    vals=[]
    for p in ps:
        v=(len(nums)-1)*p
        k=int(v);f=v-k
        vals.append(nums[k]*(1-f)+nums[min(k+1,len(nums)-1)]*f)
    return vals

def analyze(original,bootstrap=10000):
    rows=original["all_original_rows"]
    if len(rows)!=64 or original["real_native_PhysX_controller_worlds"]!=640:
        raise ValueError("Refuse incomplete physically stepped original paired source")
    strata={}
    for r in rows:
        key=(r["task"],r["true_fault_pattern"])
        strata.setdefault(key,[]).append(r)
    if len(strata)!=8 or any(len(group)!=8 for group in strata.values()):
        raise ValueError("Require exactly 8 source resets per each task/truth stratum")

    def score(group,left,right):
        diffs=[x["private_reads"][right]-x["private_reads"][left] for x in group]
        suc=[int(x["official_task_success"][left])-int(x["official_task_success"][right]) for x in group]
        only_left=sum(s==1 for s in suc)
        only_right=sum(s==-1 for s in suc)
        return {"private_read_savings":sum(diffs),
                "private_reads_left":sum(x["private_reads"][left] for x in group),
                "private_reads_right":sum(x["private_reads"][right] for x in group),
                "read_savings_per_original_task":sum(diffs)/len(group),
                "left_only_task_success":only_left,
                "right_only_task_success":only_right,
                "paired_task_success_difference":sum(suc),
                "exact_mcnemar_discordance_p_two_sided":
                    exact_two_sided_discordance(only_left,only_right),
                "positive_read_saving_seed_count":sum(x>0 for x in diffs),
                "zero_read_difference_seed_count":sum(x==0 for x in diffs),
                "negative_read_saving_seed_count":sum(x<0 for x in diffs)}

    pairs={}
    rnd=random.Random(20261009)
    for opponent,title in ((B,"full_history_vs_same_public_residual_weight"),
                           (C,"full_history_vs_fixed_private_read")):
        s=score(rows,A,opponent)
        vals=[];taskd=[]
        for _ in range(bootstrap):
            sampled=[]
            for key in sorted(strata):
                sampled.extend(rnd.choices(strata[key],k=8))
            got=score(sampled,A,opponent)
            vals.append(got["private_read_savings"])
            taskd.append(got["paired_task_success_difference"])
        s["stratified_bootstrap_source_resample_seed"]=20261009
        s["stratified_bootstrap_original_sample_count"]=bootstrap
        s["stratified_bootstrap_savings_95pct_interval"]=quantiles(vals)
        s["stratified_bootstrap_task_success_difference_95pct_interval"]=quantiles(taskd)
        s["matched_physical_neutral_probe_extra_actions_are_shared_for_both_arms"]=True
        s["status"]="Exploratory uncertainty interval, not guarantee of future model distribution"
        pairs[title]=s

    nidentified=sum(int(r["empirical_public_confident"]) for r in rows)
    nwrong=sum(int(r["empirical_wrong_confident"]) for r in rows)
    base=original["total"]
    costs={
        "same_public_methods_actual_two_XYZ_events_each":{A:128,B:128},
        "private_state_decision_reads":{arm:base[arm]["private_reads"] for arm in (A,B,C)},
        "fixed_reader_achieved_XYZ_events_as_decision_inputs":0,
        "physical_probe_native_actions_per_faulted_arm":64,
        "public_XYZ_to_private_read_break_even_for_A_over_fixed_if_same_physical_prefix":
            (base[C]["private_reads"]-base[A]["private_reads"])/128,
        "A_vs_B_equal_public_information":True,
        "posterior_B_is_UNCALIBRATED_Gaussian_residual_shape_NOT_true_Bayesian_posterior":True
    }
    risk={
        "observed_full_history_confident":nidentified,
        "observed_full_history_confident_wrong":nwrong,
        "observed_error_rate_given_confident":nwrong/nidentified if nidentified else None,
        "zero_wrong_ideal_iid_binomial_one_sided_95pct_upper_only_if_zero_errors":
            1-.05**(1/nidentified) if nidentified and nwrong==0 else None,
        "critical_caveat":"The binomial number is ONLY an ideal iid descriptive reference; actual trials share controllers and calibrated dynamics, so NOT physical risk certification, distribution-shift guarantee or false-authorization bound."
    }
    return {"schema":"source_complete_matched_public_64_paired_costs_v1",
            "source_frozen_prospective_runner_blob":original["exact_original_frozen_physical_model_blob"],
            "complete_original_n":64,"physically_stepped_native_worlds":640,
            "comparison_uses_original_exact_64_rows_NOT_640_independent_samples":True,
            "comparisons":pairs,"costs":costs,"confidence_risk":risk,
            "no_post_outcome_policy_or_threshold_tuning":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    source=full_audit(a.source_dir)
    out=analyze(source)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("MATCHED_PUBLIC_READ_COST_SOURCE_STATS",json.dumps({
        "n":out["complete_original_n"],"comparisons":out["comparisons"],
        "risk":out["confidence_risk"]},sort_keys=True))

if __name__=="__main__":main()
