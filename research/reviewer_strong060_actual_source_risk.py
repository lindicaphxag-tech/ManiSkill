"""Source-complete honest risk, physical-exposure and sensor-cost reviewer analysis.

Not a robot task experiment; recomputes only genuinely stepped ORIGINAL 64
frozen PPO source JSONs, and openly distinguishes intent-to-treat from fully
exposed both-ACK physical controller prefixes. Uses stdlib exact binomial
tail inversion and paired exact McNemar, never calls actual error rates zero.
"""
from __future__ import annotations
import argparse,json,math,random
from pathlib import Path
from research.audit_strong_score060_new64 import full_audit
from research.run_strong_score060_new64 import A,B,C

def tails_geq(k,n,p):
    """Pr[Binom(n,p)>=k]."""
    if k<=0:return 1.
    if k>n:return 0.
    return sum(math.comb(n,j)*p**j*(1-p)**(n-j) for j in range(k,n+1))

def cp_upper(observed_errors,n,confidence=.95):
    """One-sided EXACT Clopper-Pearson upper bound under iid Bernoulli ONLY."""
    if n==0:return None
    if observed_errors==n:return 1.
    if observed_errors==0:
        return 1-(1-confidence)**(1/n)
    lo,hi=0.,1.
    for _ in range(70):
        m=(lo+hi)*.5
        # Invert P[Binom(n,p)<=errors]=alpha.
        prob=1-tails_geq(observed_errors+1,n,m)
        if prob>1-confidence:lo=m
        else:hi=m
    return (lo+hi)*.5

def exact_mcnemar(discordant_A_only,discordant_B_only):
    n=discordant_A_only+discordant_B_only
    if n==0:return 1.
    k=min(discordant_A_only,discordant_B_only)
    return min(1.,2*sum(math.comb(n,i) for i in range(k+1))/2**n)

def score_rows(rows,left,right):
    no_L=sum(x["official_task_success"][left] and not x["official_task_success"][right] for x in rows)
    no_R=sum(x["official_task_success"][right] and not x["official_task_success"][left] for x in rows)
    return {
        "n_original":len(rows),
        "both_task_success":sum(x["official_task_success"][left] and x["official_task_success"][right] for x in rows),
        "neither_task_success":sum(not x["official_task_success"][left] and not x["official_task_success"][right] for x in rows),
        "left_only_task_success":no_L,"right_only_task_success":no_R,
        "exact_two_sided_mcnemar_p":exact_mcnemar(no_L,no_R),
        "private_reads_left":sum(x["private_reads"][left] for x in rows),
        "private_reads_right":sum(x["private_reads"][right] for x in rows),
        "left_private_read_savings":sum(x["private_reads"][right]-x["private_reads"][left] for x in rows)
    }

def evaluate(source):
    rs=source["all_original_rows"]
    if source["n_original_task_reset_states"]!=64 or len(rs)!=64:
        raise ValueError("Do not report incomplete original source denominator")
    if len(set((x["task"],x["seed"]) for x in rs))!=64:
        raise ValueError("Source original seed repeat")
    all_roles=(A,B,C)
    exposed=[x for x in rs if x["valid_original_two_faults_and_matched_prefix"]]
    censored=[x for x in rs if not x["valid_original_two_faults_and_matched_prefix"]]
    if len(exposed)!=source["fully_exposed_physically_matched_original_states"]:
        raise ValueError("Tampered physical exposure population")
    groups={(t,p):[x for x in rs if x["task"]==t and x["true_fault_pattern"]==p]
        for t in ("pull_cube","stack_cube") for p in range(4)}
    if any(len(v)!=8 for v in groups.values()):
        raise ValueError("Invalid original physical truth/task balances")
    costs={}
    for name in all_roles:
        selected=[x for x in exposed if
                  (x["empirical_public_confident"] if name==A else
                   x["posterior_score_confident"] if name==B else False)]
        wrong=sum(x["empirical_wrong_confident"] if name==A
                  else x["posterior_wrong_confident"] if name==B
                  else False for x in exposed)
        if name!=C and len(selected)+sum(x["private_reads"][name] for x in exposed)!=len(exposed):
            raise ValueError("Exposed source private-read and public authority conservation violated")
        if name!=C and wrong>len(selected):raise ValueError("Wrong-authority exceeds authorizations")
        costs[name]={
            "original_intention_to_treat_task_successes":sum(x["official_task_success"][name] for x in rs),
            "fully_exposed_task_successes":sum(x["official_task_success"][name] for x in exposed),
            "ITT_private_reads":sum(x["private_reads"][name] for x in rs),
            "exposed_private_reads":sum(x["private_reads"][name] for x in exposed),
            "exposed_public_observed_XYZ_samples":2*len(exposed) if name in (A,B) else 0,
            "exposed_true_full_history_authorizations":len(selected),
            "exposed_wrong_confident_histories":wrong,
            "observed_wrong_given_authority":wrong/len(selected) if selected else None,
            "only_if_independent_bernoulli_assumption_one_sided_95pct_wrong_rate_upper":
                 cp_upper(wrong,len(selected)),
            "independence_assumption_not_verified":True}
    summary={
        "schema":"full_original_new64_060_challenger_source_paired_risk_and_sensing_review_v1",
        "original_reset_states":len(rs),
        "full_two_ACK_physically_exposed_SE3_matched_states":len(exposed),
        "preexposure_censored_original_states":len(censored),
        "preexposure_seeds":[{"task":x["task"],"seed":x["seed"]} for x in censored],
        "ITT_not_reported_as_all_physically_exposed":len(censored)>0,
        "strict_original_source_physical_world_assignments":640,
        "methods":costs,
        "paired_ITT":{
           "membership_vs_trained_score060":score_rows(rs,A,B),
           "membership_vs_fixed_state_read":score_rows(rs,A,C),
           "score060_vs_fixed_state_read":score_rows(rs,B,C)},
        "paired_full_physics_exposure":{
           "membership_vs_trained_score060":score_rows(exposed,A,B),
           "membership_vs_fixed_state_read":score_rows(exposed,A,C),
           "score060_vs_fixed_state_read":score_rows(exposed,B,C)},
        "truth_strata":{},
        "sensor_cost_note":"A,B share precisely two achieved XYZ public observation events per physically exposed episode and the same controller commands. A/B privilege reads cost their counts; C gets physically same neutral step but no inference use of public XYZ.",
        "risk_note":"Binomial upper values condition on iid Bernoulli. Same controller/frozen response envelope makes iid assumption unjustified. No deployed robot safety certificate. Confidently wrong latent target can coexist with task success.",
        "adversarial_baseline_note":"Score060 selected after inspecting different 176/177 DEVELOPMENT native PhysX. Its 194/195 heldout source successes/errors MUST be reported even if worse than original membership."}
    for key,group in groups.items():
        active=[x for x in group if x["valid_original_two_faults_and_matched_prefix"]]
        summary["truth_strata"][f"{key[0]}_true2bit_{key[1]}"]={
            "original_n":len(group),"full_physics_exposure_n":len(active),
            "censored_n":len(group)-len(active),
            "methods":{name:{
                "task_success_ITT":sum(x["official_task_success"][name] for x in group),
                "privileged_reads_ITT":sum(x["private_reads"][name] for x in group),
                "public_full_histories_exposed":sum(
                   x["empirical_public_confident"] if name==A else
                   x["posterior_score_confident"] if name==B else False for x in active),
                "confident_wrong_exposed":sum(
                   x["empirical_wrong_confident"] if name==A else
                   x["posterior_wrong_confident"] if name==B else False for x in active)
            } for name in all_roles}}
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path);args=p.parse_args()
    result=evaluate(full_audit(args.source_dir))
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("REAL_SOURCE_060_EXPOSURE_RISK_COST_REVIEW",
          json.dumps({k:result[k] for k in ("original_reset_states",
                    "full_two_ACK_physically_exposed_SE3_matched_states",
                    "preexposure_censored_original_states","methods",
                    "paired_ITT")},sort_keys=True))

if __name__=="__main__":main()
