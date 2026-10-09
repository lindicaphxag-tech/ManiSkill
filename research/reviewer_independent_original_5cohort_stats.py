"""Reviewer-grade immutable-source paired evidence report for 4 DISJOINT original
ManiSkill/PhysX experiments.

All calculations are pure stdlib and directly re-read the PRIMARY immutable
64-source per-episode/full-audit JSONs. No physical simulation, PPO training
or statistical test-set threshold fitting. Physical trajectories within a
task/domain may be dependent; p-values and binomial upper confidence bounds
are descriptive/illustrative without exchangeability/independence.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path

ROOT=Path("research/frozen_policy_transfer/evidence")
COHORT={
 "first_mixed":{
    "file":ROOT/"mixed_ack_truth_frozen_ppo_original64_860001_870032/ORIGINAL_MIXED_ACK_ALL64_FULL_AUDIT.json",
    "git_blob":"c86dce6fc381369817e97ef299cb3df2ca543374",
    "primary":"public",
    "secondary":"task_gate"},
 "double_truth":{
    "file":ROOT/"four_joint_truths_first_physx64_880001_890032/ORIGINAL_FOUR_JOINT_TRUE_PHYSX_SOURCE_ONLY_AUDIT.json",
    "git_blob":"f93936be77ba8628a13c0aa937b8da793f1b67d1",
    "primary":"public",
    "secondary":"task_gate"},
 "two_probes":{
    "file":ROOT/"dual_probe_vs_single_physx_original64_900001_910032/INDEPENDENT_DUAL_V_SINGLE_ORIGINAL64.json",
    "git_blob":"976f1b6dda5b0c9f453f4f86eaa8409158119f76",
    "primary":"dual",
    "secondary":"single"},
 "calibrated":{
    "file":ROOT/"validity_first_prior32_new64_physx_original_940001_950032/INDEPENDENT_64_VALIDITY_FIRST_ORIGINAL_AUDIT.json",
    "git_blob":"76fc1f07aff16b1f96fdf34a3861d93ebe069afb",
    "primary":"calibrated",
    "secondary":"narrow"},
 "dynamics_ood":{
    "file":ROOT/"ood_pd_drive_known_ack_anchor_original64_960101_970132/INDEPENDENT_PANDA_PHYSX_OOD_ANCHOR_REAL640.json",
    "git_blob":"2fbbd40b7a91a347fd7afa004a8b1c1c4042b749",
    "primary":"anchor",
    "secondary":"narrow"}
}
def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def exact_one_sided_clopper_upper(k,n,alpha=.05):
    """Upper U satisfies Pr_{Bin(n,U)}[X<=k]=alpha."""
    if not (0<=k<=n) or n<1: raise ValueError("Invalid event/denominator")
    if k==n: return 1.
    left,right=0.,1.
    for _ in range(105):
        p=(left+right)/2
        cdf=sum(math.comb(n,i)*p**i*(1-p)**(n-i) for i in range(k+1))
        if cdf>alpha: left=p
        else: right=p
    return (left+right)/2

def two_sided_exact_sign(plus,minus):
    n=plus+minus
    if not n: return 1.
    return min(1.,2*sum(math.comb(n,i) for i in range(min(plus,minus)+1))/2**n)

def paired_rows(raw,label):
    a=json.loads(raw)
    z=[]
    if label=="first_mixed":
        for task,item in a["by_task"].items():
            for r in item["original_all_trial_rows"]:
                z.append(dict(task=task,seed=r["seed"],stratum="first_ACK_mixed_second_HELD",
                              public=(r["new_success"],r["new_reads"],
                                  bool(r["new_public_evidence"].get("authorized",False)),
                                  bool(r["new_public_evidence"].get("wrong_confident",False))),
                              task_gate=(r["task_gate_success"],r["task_gate_reads"],False,False)))
        assert a["genuine_source_physx_reset_states"]==64
    elif label=="double_truth":
        for r in a["per_original_episode"]:
            z.append(dict(task=r["task"],seed=r["seed"],stratum=r["truth"],
                          public=(r["new_success"],r["new_reads"],r["public_unique"],r["wrong_confident"]),
                          task_gate=(r["strong_success"],r["strong_reads"],False,False)))
        assert a["physical_reset_states"]==64
    elif label=="two_probes":
        for r in a["all_original_source_episode_records"]:
            z.append(dict(task=r["task"],seed=r["seed"],stratum=r["combo"],
                          dual=(r["two_success"],r["two_reads"],r["two_confident"],r["two_wrong"]),
                          single=(r["one_success"],r["one_reads"],r["one_confident"],r["one_wrong"])))
        assert a["genuine_original_reset_states"]==64
    elif label=="calibrated":
        for r in a["all_actual_original_source_episode_records"]:
            z.append(dict(task=r["task"],seed=r["seed"],stratum=r["true_joint_ack"],
                          calibrated=(r["calibrated_success"],r["calibrated_reads"],
                                      r["calibrated_public_evidence"]["authorized"],
                                      r["calibrated_public_evidence"]["wrong_confident"]),
                          narrow=(r["narrow_success"],r["narrow_reads"],
                                  r["narrow_public_evidence"]["authorized"],
                                  r["narrow_public_evidence"]["wrong_confident"])))
        assert a["genuine_source_physx_reset_states"]==64
    elif label=="dynamics_ood":
        for r in a["all_original_trial_rows"]:
            z.append(dict(task=r["task"],seed=r["seed"],stratum=r["true_joint_ack"],
                          physical_gain=r["physics_drive_mode"],
                          anchor=(r["anchor_success"],r["anchor_reads"],
                                  r["anchor_public_evidence"]["authorized"],
                                  r["anchor_public_evidence"]["wrong_confident"]),
                          narrow=(r["narrow_success"],r["narrow_reads"],
                                  r["narrow_public_evidence"]["authorized"],
                                  r["narrow_public_evidence"]["wrong_confident"])))
        assert a["original_registered_source_reset_states"]==64
    else: raise ValueError(label)
    if len(z)!=64 or len(set((r["task"],r["seed"]) for r in z))!=64:
        raise ValueError("Not complete 64 original task-matched real PhysX pairings")
    return z

def analyze(rows,primary,secondary):
    if not rows: return None
    for r in rows:
        for m in (primary,secondary):
            a=r[m]
            if len(a)!=4 or type(a[0]) is not bool or type(a[1]) is not int or a[1]<0:
                raise ValueError("Mismatched original binary physical success / real native getter cost")
            if type(a[2]) is not bool or type(a[3]) is not bool or (a[3] and not a[2]):
                raise ValueError("Impossible confidence-scoring source data")
    cases=len(rows)
    a=[r[primary] for r in rows];b=[r[secondary] for r in rows]
    paired={
        "both_real_task_success":sum(x[0] and y[0] for x,y in zip(a,b)),
        "primary_only_real_task_success":sum(x[0] and not y[0] for x,y in zip(a,b)),
        "secondary_only_real_task_success":sum(y[0] and not x[0] for x,y in zip(a,b)),
        "neither_real_task_success":sum(not x[0] and not y[0] for x,y in zip(a,b)),
    }
    cost_d=[y[1]-x[1] for x,y in zip(a,b)] # >0 = primary SAVES true native getter
    ppos=sum(d>0 for d in cost_d);pneg=sum(d<0 for d in cost_d)
    def one(g):
        good=sum(z[0] for z in g)
        reads=sum(z[1] for z in g)
        accepted=sum(z[2] for z in g)
        wrong=sum(z[3] for z in g)
        return {
            "original_physical_task_success":good,
            "original_native_privileged_reads":reads,
            "unique_full_target_history_authorizations":accepted,
            "wrong_confident_native_histories":wrong,
            "one_sided_95pc_binomial_upper_wrong_per_ACCEPTED_IF_iid":
              exact_one_sided_clopper_upper(wrong,accepted) if accepted else None,
            "one_sided_95pc_binomial_upper_wrong_per_RESET_IF_iid":
              exact_one_sided_clopper_upper(wrong,cases)}
    return {"n":cases,"primary":one(a),"secondary":one(b),
            "paired_task_outcomes":paired,
            "paired_success_exact_two_sided_McNemar_p_EXPLORATORY":
              two_sided_exact_sign(paired["primary_only_real_task_success"],
                                   paired["secondary_only_real_task_success"]),
            "paired_query_savings_primary_more_saves":ppos,
            "paired_query_savings_secondary_more_saves":pneg,
            "paired_equal_query_cost":sum(d==0 for d in cost_d),
            "mean_real_privileged_reads_saved_per_reset_PRIMARY":sum(cost_d)/cases,
            "exact_two_sided_read_savings_sign_test_p_EXPLORATORY":
              two_sided_exact_sign(ppos,pneg),
            "zero_wrong_not_a_safety_certificate":True,
            "paired_success_equality_not_task_nontinferiority":True}

def report():
    cohorts={}
    global_seeds=set()
    for label,params in COHORT.items():
        data=params["file"].read_bytes()
        if git_blob(data)!=params["git_blob"]:
            raise ValueError("Original physical source audit SHA mismatches: "+label)
        rows=paired_rows(data,label)
        keys={(r["task"],r["seed"]) for r in rows}
        if global_seeds.intersection(keys):
            raise ValueError("Contaminated non-disjoint physical reset states across original cohorts")
        global_seeds.update(keys)
        base=analyze(rows,params["primary"],params["secondary"])
        per_task={t:analyze([r for r in rows if r["task"]==t],
                            params["primary"],params["secondary"])
                     for t in ("pull_cube","stack_cube")}
        by_domain={}
        if label=="dynamics_ood":
            by_domain={mode:analyze([r for r in rows if r["physical_gain"]==mode],
                                    params["primary"],params["secondary"])
                       for mode in ("slow","fast")}
        cohorts[label]={
            "primary_model":params["primary"],"secondary_model":params["secondary"],
            "original_git_blob":params["git_blob"],
            "overall":base,"by_task":per_task,"by_physical_gain":by_domain,
            "source_file":str(params["file"]),
            "NOTE_different_original_physics_cohorts_must_NOT_be_pooled":True}
    assert len(global_seeds)==320 # FIVE actually independent source populations; never pretend 320 worlds same treatment.
    p=cohorts
    assert (p["first_mixed"]["overall"]["primary"]["original_physical_task_success"],
            p["first_mixed"]["overall"]["secondary"]["original_physical_task_success"]) == (58,58)
    assert p["first_mixed"]["overall"]["primary"]["original_native_privileged_reads"]==31
    assert p["first_mixed"]["overall"]["secondary"]["original_native_privileged_reads"]==58
    assert p["double_truth"]["overall"]["primary"]["wrong_confident_native_histories"]==2
    assert (p["two_probes"]["overall"]["primary"]["original_physical_task_success"],
            p["two_probes"]["overall"]["secondary"]["original_physical_task_success"]) == (48,48)
    assert (p["calibrated"]["overall"]["primary"]["original_native_privileged_reads"],
            p["calibrated"]["overall"]["secondary"]["original_native_privileged_reads"]) == (53,51)
    assert (p["dynamics_ood"]["overall"]["primary"]["original_native_privileged_reads"],
            p["dynamics_ood"]["overall"]["secondary"]["original_native_privileged_reads"]) == (62,56)
    assert (p["dynamics_ood"]["overall"]["primary"]["unique_full_target_history_authorizations"],
            p["dynamics_ood"]["overall"]["secondary"]["unique_full_target_history_authorizations"]) == (2,8)
    return {
        "schema":"5_separate_original_native_PhysX_cohorts_review_statistics_NO_POOLED_CAUSAL_INFERENCE_v1",
        "cohorts":cohorts,"separate_original_reset_state_population_count":320,
        "all_original_policy_trials_author_operated_only":True,
        "none_of_these_paired_task_successes_prove_task_nontinferiority":True,
        "exact_p_values_unadjusted_exploratory_and_reset_sample_independence_not_guaranteed":True,
        "one_sided_95pc_binomial_error_upper_ONLY_if_independent_event_sampling":True,
        "primary_CIs_condition_on_small_authorized_denominator_NOT_all_physical_worlds":True,
        "claim_main_conference_paper_accepted_or_independent_external_adoption":False,
        "not_robot_hardware_safety_or_real_network_packet_loss":True}
if __name__=="__main__":
    ans=report()
    print("FIVE_UNPOOLED_REAL_PHYSX_REVIEWER_GRADE_ORIGINAL_STATS",json.dumps({
        "study":{k:{"primary":v["primary_model"],"secondary":v["secondary_model"],
                     "overall":v["overall"]}
                 for k,v in ans["cohorts"].items()},
        "all_original_reset_states_across_separate_cohorts":ans["separate_original_reset_state_population_count"]
    },sort_keys=True))
