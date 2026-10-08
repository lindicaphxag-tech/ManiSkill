"""POST-OUTCOME exact finite-population query-allocation distribution.

NOT preregistered inference. This is an EXPLORATORY retrospective sensitivity
analysis conditional on all 64 already-run original PhysX potential outcomes.

The original eight-arm genuine PhysX trial measured EACH seed under both
zero-readback robust refusal and mandatory immediate target read. In this
particular task/controller pipeline, the PREDECLARED seed-mod-4 arm matches
the appropriate measured potential outcome on all 64 states. This permits
exact enumeration of all 16- or 17-query fixed seed-selection schedules
without making up unmeasured physical outcomes.

The adaptive certificate-driven algorithm occasionally follows an entirely
different action/target trajectory, and must not be reduced to a simple
potential-outcome switch; disclose all such mismatches rather than hiding.
"""
from __future__ import annotations
import argparse
import json
import math
from collections import Counter
from pathlib import Path

FIRST={"pull_cube":260001,"stack_cube":270001}
SOURCE="source_no_fault"
NO="fault_robust_two_history_without_query"
YES="fault_always_single_privileged_query"
ADAPT="fault_robust_then_single_privileged_query"
PERIODIC="fault_precommitted_seed_schedule_query"

def load(folder:Path)->list[dict]:
    rows=[]
    for task,first in FIRST.items():
        for chunk in range(4):
            path=folder/f"query_placebo_{task}_chunk{chunk}_original8.json"
            if not path.exists():raise ValueError(f"Missing original untouched source {path.name}")
            report=json.loads(path.read_text(encoding="utf-8"))
            wanted=list(range(first+8*chunk,first+8*(chunk+1)))
            if (report.get("schema")!="certify_query_nonadaptive_budget_placebo_new64_v1"
                or report.get("original_seed_population")!=wanted
                or len(report.get("episodes",[]))!=8):
                raise ValueError("Original registered PhysX cohort identity corrupted")
            for k,row in enumerate(report["episodes"]):
                if row["seed"]!=wanted[k] or row["task"]!=("PullCube-v1" if task=="pull_cube" else "StackCube-v1"):
                    raise ValueError("Corrupted task/seed origin")
                r=row["success_once"]
                q=row["privileged_target_readback_decision_count"]
                if not all(type(r[a]) is bool for a in (NO,YES,ADAPT,PERIODIC)):
                    raise ValueError("Missing native success bool")
                if q[PERIODIC]!=int(row["seed"]%4==0) or q[YES]!=1 or q[NO]!=0:
                    raise ValueError("Changed preregistered query budget")
                periodic_measured=r[PERIODIC]
                periodic_reconstructed=r[YES] if q[PERIODIC]==1 else r[NO]
                if periodic_measured!=periodic_reconstructed:
                    raise ValueError("Measured periodic arm DOES NOT identify a valid within-seed potential-outcome combination")
                rows.append({
                    "task":task,"seed":wanted[k],
                    "no_read_success":int(r[NO]),
                    "immediate_read_success":int(r[YES]),
                    "actual_adaptive_success":int(r[ADAPT]),
                    "actual_periodic_success":int(r[PERIODIC]),
                    "adaptive_reads":q[ADAPT],
                    "periodic_reads":q[PERIODIC],
                })
    if len(rows)!=64 or len({(r["task"],r["seed"]) for r in rows})!=64:
        raise ValueError("Original 64 independent reset states not complete")
    return rows


def exact_distribution(rows:list[dict],k:int)->dict[int,int]:
    """DP coefficient of z^k u^success in product_i(u^no_i + z u^yes_i)."""
    if not 0<=k<=len(rows):raise ValueError("Invalid readback budget")
    # (number of target reads, number of successful native task states)
    coeff={(0,0):1}
    for r in rows:
        nextcoeff={}
        for (q,s),n in coeff.items():
            zero=(q,s+r["no_read_success"])
            nextcoeff[zero]=nextcoeff.get(zero,0)+n
            if q<k:
                one=(q+1,s+r["immediate_read_success"])
                nextcoeff[one]=nextcoeff.get(one,0)+n
        coeff=nextcoeff
    result={score:n for (q,score),n in coeff.items() if q==k}
    if sum(result.values())!=math.comb(len(rows),k):
        raise AssertionError("Exact conditional uniform schedule enumeration violated combinatorial mass")
    return result


def exact_summary(dist:dict[int,int],total:int,threshold:int)->dict:
    if total<1:raise ValueError("No finite schedule population")
    tail=sum(n for score,n in dist.items() if score>=threshold)
    moments=sum(score*n for score,n in dist.items())
    return {
        "selection_population_exact_integer":str(total),
        "success_distribution_integer_coefficients":{str(k):str(v) for k,v in sorted(dist.items())},
        "expected_success_given_uniform_fixed_budget":moments/total,
        "max_achievable_with_scheduled_readbacks":max(dist),
        "min_achievable_with_scheduled_readbacks":min(dist),
        "uniform_all_schedules_tail_ge_adaptive_count":tail/total,
        "tail_integer_numerator":str(tail),
        "tail_integer_denominator":str(total),
        "IMPORTANT":"Finite-cohort what-if allocation frequency, NOT a frequentist p-value for adaptive algorithm over unseen robot populations; analysis is POST-OUTCOME."
    }


def analysis(rows:list[dict])->dict:
    original=sum(r["actual_adaptive_success"] for r in rows)
    reads=sum(r["adaptive_reads"] for r in rows)
    periodic=sum(r["actual_periodic_success"] for r in rows)
    periodic_reads=sum(r["periodic_reads"] for r in rows)
    if original!=58 or reads!=17 or periodic!=47 or periodic_reads!=16:
        raise ValueError("Published initial source original PhysX numbers changed")
    mix_violations=[]
    for r in rows:
        inferred=r["immediate_read_success"] if r["adaptive_reads"] else r["no_read_success"]
        if inferred!=r["actual_adaptive_success"]:
            mix_violations.append({"task":r["task"],"seed":r["seed"],
                                   "measured_adaptive":r["actual_adaptive_success"],
                                   "naive_binary_mix_outcome":inferred})
    bytask={t:[r for r in rows if r["task"]==t] for t in FIRST}
    if any(len(q)!=32 for q in bytask.values()):raise ValueError("Wrong independent task denominators")
    kpull=sum(x["adaptive_reads"] for x in bytask["pull_cube"])
    kstack=sum(x["adaptive_reads"] for x in bytask["stack_cube"])
    global_random=exact_distribution(rows,reads)
    pull_dist=exact_distribution(bytask["pull_cube"],kpull)
    stack_dist=exact_distribution(bytask["stack_cube"],kstack)
    stratified=Counter()
    for p,cn in pull_dist.items():
        for s,cm in stack_dist.items():
            stratified[p+s]+=cn*cm
    total_strat=math.comb(32,kpull)*math.comb(32,kstack)
    if sum(stratified.values())!=total_strat:
        raise ValueError("Failed to enumerate exact balanced task strata")
    categories={}
    for task,subset in bytask.items():
        categories[task]={
            "no_read_success":sum(x["no_read_success"] for x in subset),
            "always_immediate_read_success":sum(x["immediate_read_success"] for x in subset),
            "positive_read_effect":sum(x["immediate_read_success"]>x["no_read_success"] for x in subset),
            "negative_read_effect":sum(x["immediate_read_success"]<x["no_read_success"] for x in subset),
            "no_effect_success":sum(x["immediate_read_success"]==x["no_read_success"]==1 for x in subset),
            "no_effect_failure":sum(x["immediate_read_success"]==x["no_read_success"]==0 for x in subset),
            "actual_adaptive_queries":sum(x["adaptive_reads"] for x in subset),
            "actual_adaptive_task_success":sum(x["actual_adaptive_success"] for x in subset),
        }
    return {
        "schema":"posthoc_complete_potential_outcomes_query_allocation64_v1",
        "original_8_arm_physx_run":37833053629,
        "actual_unique_reset_states":64,
        "all_64_periodic_arm_reconstructed_correctly_from_two_physically_measured_potential_outcomes":True,
        "actual_adaptive_task_success":original,
        "actual_adaptive_query_reads":reads,
        "original_periodic_success":periodic,
        "original_periodic_queries":periodic_reads,
        "original_17_read_trajectory_mismatches_with_simple_immediate_read_or_no_read_mixture":mix_violations,
        "original_trajectory_mixture_NOT_sufficient_for_adaptive":bool(mix_violations),
        "actual_original_policy_arms_have_simulated_native_target_hold_not_network_loss":True,
        "by_task_observed_potential_outcome_categories":categories,
        "retrospective_uniform_fixed_17_read_all64_schedule_distribution":
            exact_summary(global_random,math.comb(64,reads),original),
        "retrospective_uniform_fixed_17_read_TASK_STRATIFIED_3pull_14stack_schedule_distribution":
            exact_summary(dict(stratified),total_strat,original),
        "interpretation_limit":"Neither distribution is a prospective randomized trial; it enumerates only preexisting real PhysX counterfactual arms on the very same cohort. No third-party adoption, safety or external population significance.",
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=analysis(load(args.input_dir))
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("EXACT_QUERY_SCHEDULE_ALLOCATION_ENUMERATION",json.dumps({
        "unique_seed_count":result["actual_unique_reset_states"],
        "original_adaptive_success":result["actual_adaptive_task_success"],
        "source_binary_mix_counterexamples":result["original_17_read_trajectory_mismatches_with_simple_immediate_read_or_no_read_mixture"],
        "uniform_17_reads_tail":result["retrospective_uniform_fixed_17_read_all64_schedule_distribution"]["uniform_all_schedules_tail_ge_adaptive_count"],
        "stratified_3pull_14stack_tail":result["retrospective_uniform_fixed_17_read_TASK_STRATIFIED_3pull_14stack_schedule_distribution"]["uniform_all_schedules_tail_ge_adaptive_count"]
    },sort_keys=True))

if __name__=="__main__":
    main()
