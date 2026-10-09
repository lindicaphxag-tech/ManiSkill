"""Reproducible MAIN-conference evidence audit. EXACT ORIGINAL 640 PhysX source.

Paired binary outcomes, original source-locked information costs, true model
coverage, incorrect confident native target labels and exact sparse-sample
confidence bounds. All statistics are DESCRIPTIVE for two tasks / one robot;
no false across-domain iid confidence or post hoc noninferiority claims.

Stdlib only; source physical truth is an AUDIT LABEL, NEVER policy input.
"""
from __future__ import annotations
from collections import Counter
import hashlib,json,math
from pathlib import Path

FILE=Path("research/frozen_policy_transfer/evidence/ood_pd_drive_known_ack_anchor_original64_960101_970132/INDEPENDENT_PANDA_PHYSX_OOD_ANCHOR_REAL640.json")
PIN="2fbbd40b7a91a347fd7afa004a8b1c1c4042b749"

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\\x00"+raw).hexdigest()

def exact_binomial_two_sided_discordance(x_only,y_only):
    n=x_only+y_only
    if n==0:return 1.0
    k=min(x_only,y_only)
    return min(1.,2*sum(math.comb(n,i) for i in range(k+1))/(2**n))

def zero_wrong_upper_one_sided_95(n):
    """Clopper-Pearson 1-sided 95% upper for 0 wrong among n AUTHORIZATIONS."""
    return 1.0 if n==0 else 1-0.05**(1.0/n)

def order_stat_quantile(vals,q):
    if not vals:return None
    a=sorted(vals)
    return a[math.ceil((len(a)-1)*q)]

def bygroup(rows):
    n=len(rows)
    o={"registered_source_reset_states":n}
    for label in ("old","anchor"):
        pref="narrow" if label=="old" else "anchor"
        successes=[bool(r[pref+"_success"]) for r in rows]
        readings=[int(r[pref+"_reads"]) for r in rows]
        evs=[r[pref+"_public_evidence"] for r in rows]
        auth=[e for e in evs if e["authorized"]]
        wrong=sum(e["wrong_confident"] for e in auth)
        true_scores=[]
        uncovered=0
        for e in evs:
            true_idx=e["audit_only_true_candidate_indices"]
            if len(true_idx)!=1:raise ValueError("Actual poststep native target not unique in original complete full history")
            score=e["candidate_residuals_m"][true_idx[0]]
            true_scores.append(score)
            uncovered+=int(score>e["prior_training_epsilon_m"])
        o[label]={
            "actual_PhysX_task_successes":sum(successes),
            "actual_PhysX_task_failures":n-sum(successes),
            "private_target_decision_reads":sum(readings),
            "mean_reads_per_original_state":sum(readings)/n if n else None,
            "public_XYZ_sample_events":n*(4 if label=="anchor" else 2),
            "unique_full_target_history_authorized":len(auth),
            "wrong_confident_given_authorized":wrong,
            "wrong_confident_rate_given_authorized":wrong/len(auth) if auth else None,
            "ONE_SIDED_95_CP_upper_wrong_rate_given_authorized":zero_wrong_upper_one_sided_95(len(auth)) if wrong==0 else None,
            "true_response_residual_out_of_old_envelope":uncovered,
            "max_TRUE_target_residual_m":max(true_scores,default=None),
            "q90_TRUE_target_residual_m":order_stat_quantile(true_scores,.9)
        }
    both=sum(r["narrow_success"] and r["anchor_success"] for r in rows)
    aonly=sum(r["anchor_success"] and not r["narrow_success"] for r in rows)
    oonly=sum(r["narrow_success"] and not r["anchor_success"] for r in rows)
    neither=n-both-aonly-oonly
    cost_diffs=[r["anchor_reads"]-r["narrow_reads"] for r in rows]
    o["actual_task_paired_success"]={
        "both":both,"anchor_only":aonly,"old_only":oonly,"neither":neither,
        "two_sided_exact_McNemar_p_EXPLORATORY":exact_binomial_two_sided_discordance(aonly,oonly)}
    o["actual_private_read_paired_cost"]={
        "anchor_more":sum(d>0 for d in cost_diffs),
        "old_more":sum(d<0 for d in cost_diffs),
        "equal":sum(d==0 for d in cost_diffs),
        "net_anchor_extra_private_reads":sum(cost_diffs),
        "exact_discordant_sign_two_sided_p_EXPLORATORY":exact_binomial_two_sided_discordance(
            sum(d>0 for d in cost_diffs),sum(d<0 for d in cost_diffs))}
    o["strong_task_selected"]={
        "original_actual_PhysX_task_success":sum(r["strong_success"] for r in rows),
        "privileged_target_decision_reads":sum(r["strong_reads"] for r in rows)}
    return o

def main():
    raw=FILE.read_bytes()
    actual=git_blob(raw)
    if actual!=PIN:
        raise ValueError(f"Immutable raw original 640 physical source Git blob mismatch: {actual}")
    data=json.loads(raw)
    assert data["source_original_native_physx_worlds"]==640
    rows=data["all_original_trial_rows"]
    assert len(rows)==64 and len({(r["task"],r["seed"]) for r in rows})==64
    for row in rows:
        if row["physics_drive_mode"] not in ("slow","fast") or row["true_joint_ack"] not in ("AA","AH","HA","HH"):
            raise ValueError("Unknown physical regime or actual two-command execution history")
        if row["anchor_known_t1_evidence"].get("native_private_target_getter_NOT_USED_in_anchor") is not True:
            raise ValueError("Possible privileged data leakage in t1 known ACK model witness")
    result={
        "schema":"main_conference_640_original_native_PhysX_paired_claim_audit_v1",
        "original_real_physx_git_blob":PIN,
        "not_novel_statistical_theory":True,
        "no_independent_laboratory_or_hardware":True,
        "DO_NOT_ASSERT_statistical_task_noninferiority_from_matching_success_totals":True,
        "DO_NOT_ASSERT_physical_safety_from_zero_observed_wrong_history":True,
        "source_based_fixed_population_results":bygroup(rows),
        "by_task":{t:bygroup([r for r in rows if r["task"]==t]) for t in ("pull_cube","stack_cube")},
        "by_PHYSICALLY_INJECTED_Panda_gain":{
            g:bygroup([r for r in rows if r["physics_drive_mode"]==g]) for g in ("slow","fast")},
        "by_task_gain_and_joint_true_ACK":{
            f"{t}/{g}/{h}":bygroup([r for r in rows if r["task"]==t and r["physics_drive_mode"]==g and r["true_joint_ack"]==h])
            for t in ("pull_cube","stack_cube") for g in ("slow","fast") for h in ("AA","AH","HA","HH")}
    }
    t=result["source_based_fixed_population_results"]
    assert (t["old"]["actual_PhysX_task_successes"],t["anchor"]["actual_PhysX_task_successes"])==(56,56)
    assert (t["old"]["private_target_decision_reads"],t["anchor"]["private_target_decision_reads"])==(56,62)
    assert (t["old"]["unique_full_target_history_authorized"],t["anchor"]["unique_full_target_history_authorized"])==(8,2)
    assert t["old"]["wrong_confident_given_authorized"]==0==t["anchor"]["wrong_confident_given_authorized"]
    assert t["old"]["true_response_residual_out_of_old_envelope"]==8
    assert t["strong_task_selected"]=={"original_actual_PhysX_task_success":55,"privileged_target_decision_reads":50}
    assert t["actual_task_paired_success"]=={"both":56,"anchor_only":0,"old_only":0,"neither":8,
                                           "two_sided_exact_McNemar_p_EXPLORATORY":1.}
    print("SOURCE_PINNED_MAIN_CONF_OOD_REAL_PHYSX_PAIRED_AND_SPARSE_RISK_AUDIT",json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":main()
