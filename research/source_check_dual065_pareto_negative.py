"""Source-audited decision rule DOMINANCE of a new same-residual confidence gate.

Does NOT claim an improved algorithm, independent model-trust evidence, new
physical experiments, general error-free recovery or statistically valid
equivalence. It is a *negative* exact paired analysis on original author-run
native PhysX source rows.
"""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path

ROOT=Path("research/frozen_policy_transfer/evidence/dual065_observer_negative_original64_1820001_1830032")
SOURCE=ROOT/"original_all64_independent_audit.json"
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_dual_evidence_065_or_query"
FIXED="fault_always_single_privileged_query"

def check_source():
    checksum=ROOT/"ORIGINAL_SHA256SUMS"
    wanted=[v for v in checksum.read_text().splitlines() if v.endswith("  original_all64_independent_audit.json")]
    if len(wanted)!=1: raise ValueError("missing original locked full physical audit hash")
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if wanted[0].split("  ")[0]!=sha: raise ValueError("underlying original audit SHA differs")
    d=json.loads(SOURCE.read_text())
    if d.get("n_original_task_reset_states")!=64 or d.get("real_native_PhysX_controller_worlds")!=640:
        raise ValueError("wrong genuine native source population")
    rows=d["all_original_rows"]
    if len(rows)!=64: raise ValueError("original physical task denominator censored")
    ids={(r["task"],r["seed"]) for r in rows}
    if ids!={(task,i) for task,s in (("pull_cube",1820001),("stack_cube",1830001)) for i in range(s,s+32)}:
        raise ValueError("original precommitted seed identities differ")
    across=Counter()
    bytruth={}
    for r in rows:
        for method in (A,B,FIXED):
            if type(r["official_task_success"][method]) is not bool: raise ValueError("nonboolean physical success")
            x=r["private_reads"][method]
            if type(x) is not int or x not in (0,1): raise ValueError("nonphysical privileged query count")
        for key in ("empirical_public_confident","posterior_score_confident","empirical_wrong_confident",
                    "posterior_wrong_confident","valid_original_two_faults_and_matched_prefix","same_public_samples"):
            if type(r[key]) is not bool: raise ValueError("malformed original public history admission/exposure")
        if r["posterior_score_confident"] and not r["empirical_public_confident"]:
            raise ValueError("same-XYZ 0.65 gate fabricates a new history acceptance")
        if r["private_reads"][B]<r["private_reads"][A]:
            raise ValueError("add-on score unexpectedly uses fewer private reads on a physical source")
        if r["official_task_success"][A] != r["official_task_success"][B]:
            across["actual_task_success_discordant"]+=1
        if r["private_reads"][B]>r["private_reads"][A]:
            across["add_on_queries_more"]+=1
        if r["empirical_public_confident"] and not r["posterior_score_confident"]:
            across["rejected_prior_confident_history"]+=1
        if r["valid_original_two_faults_and_matched_prefix"]:
            if r["same_public_samples"] is not True:
                raise ValueError("valid real physical comparison did not have equal public observations")
            across["physically_matched_probe"]+=1
        else:
            if r["empirical_public_confident"] or r["posterior_score_confident"]:
                raise ValueError("censored original trial rebranded as sensor-supported history")
            across["censored_intent_to_treat"]+=1
        across["successful_A"]+=int(r["official_task_success"][A])
        across["successful_B"]+=int(r["official_task_success"][B])
        across["successful_fixed"]+=int(r["official_task_success"][FIXED])
        across["private_A"]+=r["private_reads"][A]
        across["private_B"]+=r["private_reads"][B]
        across["private_fixed"]+=r["private_reads"][FIXED]
        across["confident_A"]+=int(r["empirical_public_confident"])
        across["confident_B"]+=int(r["posterior_score_confident"])
        across["wrong_A"]+=int(r["empirical_wrong_confident"])
        across["wrong_B"]+=int(r["posterior_wrong_confident"])
        key=(r["task"],r["true_fault_pattern"])
        bytruth[key]=bytruth.get(key,0)+1
    expected={"successful_A":54,"successful_B":54,"successful_fixed":55,
            "private_A":41,"private_B":45,"private_fixed":62,
            "confident_A":21,"confident_B":17,"wrong_A":0,"wrong_B":0,
            "censored_intent_to_treat":2,"physically_matched_probe":62,
            "add_on_queries_more":4,"rejected_prior_confident_history":4,
            "actual_task_success_discordant":0}
    for k,v in expected.items():
        if across[k]!=v: raise ValueError(f"original method effect/scope changed {k}: {across[k]} != {v}")
    if set(bytruth.values())!={8} or len(bytruth)!=8:
        raise ValueError("original four physical ACK truth strata not balanced per task")
    if d["total"][A]["achieved_XYZ_sample_events"]!=124 or d["total"][B]["achieved_XYZ_sample_events"]!=124:
        raise ValueError("original actually acquired public sensor events changed")
    return {
        "evidence_type":"SOURCE_AUDITED_NEGATIVE_SAME_XYZ_WEIGHT_GATE_DOMINATED_ON_THIS_PHYSX_COHORT",
        "original_full_source_sha256":sha,
        "original_physical_reset_states":64,
        "actually_physically_stepped_controller_worlds":640,
        "all_original_64_task_outcomes_retained":True,
        "fully_matched_public_probe_exposures":62,
        "censored_original_intent_to_treat_rows":2,
        "original_public_sensor_events_per_method":124,
        "public_method_A":{"task_success":54,"privileged_reads":41,"history_admitted":21,"wrong_confident":0},
        "same_residual_additional_065_gate_B":{"task_success":54,"privileged_reads":45,"history_admitted":17,"wrong_confident":0},
        "fixed_private":{"task_success":55,"privileged_reads":62},
        "per_reset_task_outcome_discordance_A_B":0,
        "per_reset_additional_privileged_reads_B_over_A":4,
        "exactly_four_previously_admitted_histories_now_rejected":True,
        "per_original_trial_private_read_B_ge_A":True,
        "both_methods_no_observed_wrong_confident_in_this_cohort":True,
        "B_strictly_sample_dominated_by_A_in_observed_task_read_error_metrics":True,
        "not_a_statistical_global_reliability_proof":True,
        "no_new_sensor_information_in_the_same_residual_softmax":True,
        "no_external_investigator_reproduction":True,
    }

def _tests():
    d=check_source()
    assert d["per_reset_additional_privileged_reads_B_over_A"]==4
    assert d["fully_matched_public_probe_exposures"]==62
    assert d["per_reset_task_outcome_discordance_A_B"]==0

if __name__=="__main__":
    print("STRICT_UNMODIFIED_NATIVE_PHYXS_NEGATIVE_GATE_AUDIT",json.dumps(check_source(),sort_keys=True))
    _tests()
