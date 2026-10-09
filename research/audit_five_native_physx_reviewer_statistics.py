"""Reviewer-first source-locked paired statistics from FIVE *distinct* genuine PhysX
frozen-PPO reset populations. Uses ONLY Python stdlib; NO refits or simulations.

Confidence intervals: exact Clopper-Pearson under iid Bernoulli assumptions,
NOT causal/task/robot generalization or proof of task noninferiority.
Tests are EXPLORATORY; 64 seeds within only 2 tasks/one Panda robot.
Different cohorts have DIFFERENT perturbation/extra probe steps and MUST
NEVER be pooled into a headline claim.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT=Path("research/frozen_policy_transfer/evidence")
FILES={
    "first_mixed_t3_held":(
        "mixed_ack_truth_frozen_ppo_original64_860001_870032/"
        "ORIGINAL_MIXED_ACK_ALL64_FULL_AUDIT.json",
        "c86dce6fc381369817e97ef299cb3df2ca543374"),
    "four_joint_t4":(
        "four_joint_truths_first_physx64_880001_890032/"
        "ORIGINAL_FOUR_JOINT_TRUE_PHYSX_SOURCE_ONLY_AUDIT.json",
        "f93936be77ba8628a13c0aa937b8da793f1b67d1"),
    "one_v_two_t4_t5":(
        "dual_probe_vs_single_physx_original64_900001_910032/"
        "INDEPENDENT_DUAL_V_SINGLE_ORIGINAL64.json",
        "976f1b6dda5b0c9f453f4f86eaa8409158119f76"),
    "old_v_prior_score_radius":(
        "validity_first_prior32_new64_physx_original_940001_950032/"
        "INDEPENDENT_64_VALIDITY_FIRST_ORIGINAL_AUDIT.json",
        "76fc1f07aff16b1f96fdf34a3861d93ebe069afb"),
    "actual_joint_PD_shift_t1_anchor":(
        "ood_pd_drive_known_ack_anchor_original64_960101_970132/"
        "INDEPENDENT_PANDA_PHYSX_OOD_ANCHOR_REAL640.json",
        "2fbbd40b7a91a347fd7afa004a8b1c1c4042b749")
}
SRC_WORLD_COUNTS=(576,576,640,640,640)
CONFIDENCE_ALPHA=.05

def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def original_file(key):
    path,pin=FILES[key]
    source=ROOT/path
    raw=source.read_bytes()
    if blob(raw)!=pin:
        raise ValueError(f"Original PhysX SHA drift: {key} {source}")
    return json.loads(raw),hashlib.sha256(raw).hexdigest()

def _binom_le(x,n,p):
    # Exact ordinary binomial CDF, including x=0,n; n<=64.
    return sum(math.comb(n,k)*(p**k)*((1-p)**(n-k))
               for k in range(x+1))

def cp_interval(x,n,alpha=CONFIDENCE_ALPHA):
    """Two-sided Clopper-Pearson equal-tail binomial interval."""
    if not(0<=x<=n and n>=1):raise ValueError("invalid count")
    # Lower: solve Pr_{p}(X >= x) = alpha/2 (increasing in p)
    lo=0.0
    if x>0:
        a,b=0.,1.
        for _ in range(66):
            m=(a+b)/2
            sf=1-_binom_le(x-1,n,m)
            if sf<alpha/2: a=m
            else: b=m
        lo=(a+b)/2
    # Upper: solve Pr_{p}(X <= x) = alpha/2 (decreasing in p)
    hi=1.0
    if x<n:
        a,b=0.,1.
        for _ in range(66):
            m=(a+b)/2
            if _binom_le(x,n,m)>alpha/2:a=m
            else:b=m
        hi=(a+b)/2
    return {"numerator":x,"denominator":n,"estimate":x/n,
            "exact_two_sided_95pct_low":lo,"exact_two_sided_95pct_high":hi,
            "assumption":"independent exchangeable Bernoulli within declared population; NOT across tasks/physical regimes"}

def exact_two_sided_sign(positive,negative):
    if min(positive,negative)<0:raise ValueError("negative counts")
    n=positive+negative
    if n==0:return 1.
    lower=min(positive,negative)
    return min(1.,2*sum(math.comb(n,i) for i in range(lower+1))/2**n)

def _observe(seed,task,success_a,success_b,reads_a,reads_b,
             auth_a=None,wrong_a=None,auth_b=None,wrong_b=None,
             truth=None,gain=None):
    if any(type(z) is not bool for z in (success_a,success_b)):
        raise ValueError("Not actually observed paired task Boolean")
    if any(type(z) is not int or z not in (0,1) for z in (reads_a,reads_b)):
        raise ValueError("Missing decision-time target read ledger")
    if not isinstance(seed,int) or task not in ("pull_cube","stack_cube"):
        raise ValueError("Unknown reset state or task")
    for auth,wrong in ((auth_a,wrong_a),(auth_b,wrong_b)):
        if auth is not None and (type(auth) is not bool or type(wrong) is not bool
             or (wrong and not auth)):
            raise ValueError("Invalid actual confidence and hidden-target audit truth")
    return {"seed":seed,"task":task,"a_success":success_a,"b_success":success_b,
            "a_reads":reads_a,"b_reads":reads_b,"a_authorized":auth_a,
            "b_authorized":auth_b,"a_wrong":wrong_a,"b_wrong":wrong_b,
            "actual_ack_truth":truth,"physical_gain":gain}

def extract(key,data):
    raw=[]
    if key=="first_mixed_t3_held":
        assert data["genuine_source_physx_reset_states"]==64
        assert data["genuine_physics_controller_worlds"]==576
        for task,part in data["by_task"].items():
            for r in part["original_all_trial_rows"]:
                if [r["new_public_evidence"]["wrong_confident"],r["new_public_evidence"]["authorized"]]==[True,False]:
                    raise ValueError("Inconsistent latent history confidence")
                raw.append(_observe(r["seed"],task,r["new_success"],r["task_gate_success"],
                    r["new_reads"],r["task_gate_reads"],
                    r["new_public_evidence"]["authorized"],r["new_public_evidence"]["wrong_confident"],
                    truth="APPLIED" if r["seed"]%2==0 else "HELD"))
    elif key=="four_joint_t4":
        assert data["physical_reset_states"]==64 and data["actually_physics_controller_worlds"]==576
        for r in data["per_original_episode"]:
            raw.append(_observe(r["seed"],r["task"],r["new_success"],r["strong_success"],
                r["new_reads"],r["strong_reads"],r["public_unique"],r["wrong_confident"],
                truth=r["truth"]))
    elif key=="one_v_two_t4_t5":
        assert data["genuine_original_reset_states"]==64
        assert data["actual_independently_physically_stepped_policy_controller_worlds"]==640
        for r in data["all_original_source_episode_records"]:
            raw.append(_observe(r["seed"],r["task"],r["two_success"],r["one_success"],
                 r["two_reads"],r["one_reads"],r["two_confident"],r["two_wrong"],
                 r["one_confident"],r["one_wrong"],truth=r["combo"]))
    elif key=="old_v_prior_score_radius":
        assert data["genuine_source_physx_reset_states"]==64
        assert data["genuine_independently_stepped_native_controller_worlds"]==640
        for r in data["all_actual_original_source_episode_records"]:
            a,b=r["calibrated_public_evidence"],r["narrow_public_evidence"]
            raw.append(_observe(r["seed"],r["task"],r["calibrated_success"],r["narrow_success"],
                r["calibrated_reads"],r["narrow_reads"],
                a["authorized"],a["wrong_confident"],
                b["authorized"],b["wrong_confident"],truth=r["true_joint_ack"]))
    elif key=="actual_joint_PD_shift_t1_anchor":
        assert data["original_registered_source_reset_states"]==64
        assert data["source_original_native_physx_worlds"]==640
        for r in data["all_original_trial_rows"]:
            a,b=r["anchor_public_evidence"],r["narrow_public_evidence"]
            raw.append(_observe(r["seed"],r["task"],r["anchor_success"],r["narrow_success"],
               r["anchor_reads"],r["narrow_reads"],a["authorized"],a["wrong_confident"],
               b["authorized"],b["wrong_confident"],truth=r["true_joint_ack"],
               gain=r["physics_drive_mode"]))
    else:raise ValueError("invalid unique original cohort")
    if len(raw)!=64 or len({(r["task"],r["seed"]) for r in raw})!=64:
        raise ValueError(f"{key}: missing/duplicate original 64 reset states")
    for task in ("pull_cube","stack_cube"):
        if sum(z["task"]==task for z in raw)!=32:
            raise ValueError(f"{key}: original task stratum undercovered")
    return raw

def paired_stats(rows):
    n=len(rows)
    if n==0:return None
    both=sum(r["a_success"] and r["b_success"] for r in rows)
    a_only=sum(r["a_success"] and not r["b_success"] for r in rows)
    b_only=sum(not r["a_success"] and r["b_success"] for r in rows)
    neither=n-both-a_only-b_only
    less=sum(r["a_reads"]<r["b_reads"] for r in rows)
    more=sum(r["a_reads"]>r["b_reads"] for r in rows)
    same=n-less-more
    out={
        "genuinely_original_matched_reset_states":n,
        "controller_a_success":both+a_only,
        "controller_b_success":both+b_only,
        "controller_a_privileged_reads":sum(r["a_reads"] for r in rows),
        "controller_b_privileged_reads":sum(r["b_reads"] for r in rows),
        "observed_success_difference_a_minus_b_pct_points":100*(a_only-b_only)/n,
        "paired_success": {"both":both,"a_only":a_only,"b_only":b_only,"neither":neither},
        "paired_exact_mcnemar_two_sided_p_EXPLORATORY":exact_two_sided_sign(a_only,b_only),
        "paired_query": {"a_less":less,"a_more":more,"same":same},
        "exact_query_cost_sign_test_two_sided_p_EXPLORATORY":exact_two_sided_sign(less,more),
        "controller_a_task_success_cp_95pct_DESCRIPTIVE":cp_interval(both+a_only,n),
        "controller_b_task_success_cp_95pct_DESCRIPTIVE":cp_interval(both+b_only,n),
        "statistical_noninferiority_NOT_tested":True
    }
    for short,prefix in (("controller_a","a"),("controller_b","b")):
        subs=[r for r in rows if r[prefix+"_authorized"] is not None]
        if len(subs)==n:
            auth=sum(r[prefix+"_authorized"] for r in rows)
            wrong=sum(r[prefix+"_wrong"] for r in rows)
            out[short+"_confident_histories"]=auth
            out[short+"_wrong_confident_histories"]=wrong
            out[short+"_wrong_among_accepted_exact_CP_95pct_DESCRIPTIVE"]=(
                cp_interval(wrong,auth) if auth else None)
    return out

def report():
    result={}
    used={}
    for key in FILES:
        source,sha=original_file(key)
        rows=extract(key,source)
        ids={(r["task"],r["seed"]) for r in rows}
        for earlier,seen in used.items():
            if ids&seen:raise ValueError("Research cohorts share reset identities: "+earlier+" "+key)
        used[key]=ids
        main=paired_stats(rows)
        grouped={task:paired_stats([r for r in rows if r["task"]==task])
                 for task in ("pull_cube","stack_cube")}
        for truth in sorted(set(r["actual_ack_truth"] for r in rows)):
            grouped["ACK_"+str(truth)]=paired_stats(
                [r for r in rows if r["actual_ack_truth"]==truth])
        for gain in sorted(set(r["physical_gain"] for r in rows if r["physical_gain"])):
            grouped["physical_gain_"+gain]=paired_stats(
                [r for r in rows if r["physical_gain"]==gain])
        result[key]={"original_full_source_blob":FILES[key][1],
                     "original_full_source_sha256":sha,
                     "definition_of_a":{
                         "first_mixed_t3_held":"public complete-history or query",
                         "four_joint_t4":"public complete-history or query",
                         "one_v_two_t4_t5":"two correlated public probes",
                         "old_v_prior_score_radius":"conservatively calibrated radius",
                         "actual_joint_PD_shift_t1_anchor":"known pre-fault ACK motion model validity gate"}[key],
                     "definition_of_b":{
                         "first_mixed_t3_held":"predeclared task-selected strong query",
                         "four_joint_t4":"predeclared task-selected strong query",
                         "one_v_two_t4_t5":"single public probe, same TWO native neutral actions",
                         "old_v_prior_score_radius":"old narrow radius, same native action",
                         "actual_joint_PD_shift_t1_anchor":"old narrow public observer, same actual shifted native dynamics"}[key],
                     "real_physical_controller_worlds":SRC_WORLD_COUNTS[list(FILES).index(key)],
                     "all64_paired_analysis":main,"disaggregated":grouped}
    return {
        "schema":"five_original_true_physx_cohorts_exact_pairwise_source_locked_stats_v1",
        "independent_64_reset_populations":len(result),
        "total_distinct_registered_reset_states":sum(x["all64_paired_analysis"]["genuinely_original_matched_reset_states"] for x in result.values()),
        "cohorts_NOT_pooled_due_different_physics_and_probe_cost":True,
        "description":"Five source-authenticated original author-operated true ManiSkill CPU PhysX cohorts; source-only full JSON audits, no new simulation.",
        "stats_are_descriptive_and_exploratory_within_only_two_frozen_PPO_tasks":True,
        "95pct_exact_CP_requires_independent_bernoulli_trails":True,
        "no_statistical_noninferiority_claims":True,
        "no_external_third_party_robotics_method_adoption":True,
        "complete":result
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    x=report()
    a.output.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    for name,study in x["complete"].items():
        d=study["all64_paired_analysis"]
        print("REAL_NATIVE_PPO_SOURCE_PAIR",json.dumps({
            "cohort":name,"success_A":d["controller_a_success"],
            "success_B":d["controller_b_success"],
            "privileged_reads_A":d["controller_a_privileged_reads"],
            "privileged_reads_B":d["controller_b_privileged_reads"],
            "success_discordances":d["paired_success"],
            "read_cost_direction":d["paired_query"],
            "wrong_A":d.get("controller_a_wrong_confident_histories"),
            "wrong_B":d.get("controller_b_wrong_confident_histories"),
            "exact_p_success_exploratory":d["paired_exact_mcnemar_two_sided_p_EXPLORATORY"]
        },sort_keys=True))
if __name__=="__main__":
    main()
