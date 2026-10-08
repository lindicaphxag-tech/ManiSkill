"""Exact *retrospective* fixed-budget query-allocation counterfactual.

Source: 8 publicly archived ORIGINAL paired ManiSkill PhysX 64-state JSONs,
same pretrained frozen ActionShift PPOs / same task-state reset seeds.
This DOES NOT rerun robotics, train a policy or prove new online optimality.

A fixed step-3 oracle-query vs no-query trajectory is empirically verified
against the actual precommitted 16/64 periodic queried world for EVERY state.
Conditional on that verified binary branch consistency, enumerate the exact
finite-population outcomes of uniform, seed-independent fixed-step-3 query
allocations of exactly B=17 episodes.

DO NOT splice the ADAPTIVE policy from mandatory/no-query arms: it can defer
a target read to step 5/6 and actually succeed when BOTH fixed-step-3 and
never-query fail. These are different trajectories and are reported as such.

The exact tail fraction below is a FINITE-COHORT COMBINATORIAL DESCRIPTION,
NOT a valid p-value for population-level adaptive-versus-random causal benefit,
not a preregistered benchmark and not an independent external rerun.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import defaultdict
from math import comb
from pathlib import Path

from research.audit_certify_query_periodic_placebo64 import (
    ARMS, ADAPTIVE, PLACEBO, ALWAYS, NOQUERY,
    BASES, TASKS, CHECKPOINTS, audit as original_audit,
)

ORIGINAL_MANIFEST_GIT_BLOB = "8acf77293b4b576517d4bc4c6aa576cf0efbe39e"
EXPECTED_FILES = tuple(
    f"query_placebo_{t}_chunk{idx}_original8.json"
    for t in BASES for idx in range(4)
)
FROZEN_ADAPTIVE_QUERY_TOTAL = 17


def ensure_original_source(directory: Path) -> dict[str,str]:
    manifest=(directory/"SHA256SUMS").read_bytes()
    computed=hashlib.sha1(
        b"blob "+str(len(manifest)).encode("ascii")+bytes([0])+manifest
    ).hexdigest()
    if computed != ORIGINAL_MANIFEST_GIT_BLOB:
        raise ValueError("Original published finite-population SHA manifest mutated")
    rows=manifest.decode("ascii").splitlines()
    if len(rows)!=8:
        raise ValueError("Original eight source hashes required")
    found={}
    for line in rows:
        pieces=line.split()
        if len(pieces)!=2 or len(pieces[0])!=64:
            raise ValueError("Malformed full-source SHA record")
        filename=pieces[1].removeprefix("./")
        if filename in found or filename not in EXPECTED_FILES:
            raise ValueError("Unregistered or duplicate original episode source")
        if any(c not in "0123456789abcdef" for c in pieces[0]):
            raise ValueError("Malformed 256-bit original data hash")
        found[filename]=pieces[0]
    if set(found)!=set(EXPECTED_FILES):
        raise ValueError("Partial or reordered original task source archive")
    for name,digest in found.items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:
            raise ValueError(f"Original raw PhysX task/source SHA mismatch: {name}")
    return dict(sorted(found.items()))


def exact_uniform_fixed_query_distribution(potential_gains: list[int], budget: int):
    """Count all C(N,B) fixed allocations exactly, no Monte Carlo/random seeds.

    Each original patient-free task-state has no-query potential binary task
    outcome z_i and step-3 fixed-query outcome q_i, difference d_i in
    {-1,0,1}. For random subset S of exactly B states, total outcome is
    Σ z_i + Σ_{i∈S} d_i. This can be computed exactly via coefficient DP.
    """
    n=len(potential_gains)
    if n==0 or type(budget) is not int or not 0<=budget<=n:
        raise ValueError("Finite independent task states and integer query budget required")
    if any(type(d) is not int or d not in (-1,0,1) for d in potential_gains):
        raise ValueError("Every paired intervention gain must be binary")
    dp=[defaultdict(int) for _ in range(budget+1)]
    dp[0][0]=1
    for i,d in enumerate(potential_gains):
        for b in range(min(budget,i+1),0,-1):
            for gain,num in list(dp[b-1].items()):
                dp[b][gain+d]+=num
    result=dict(sorted(dp[budget].items()))
    if sum(result.values())!=comb(n,budget):
        raise ValueError("Counterfactual fixed allocation denominator dropped")
    return result


def original_allocation_audit(directory:Path, *, budget=FROZEN_ADAPTIVE_QUERY_TOTAL):
    files=ensure_original_source(directory)
    original=original_audit(directory)
    if (original["original_source_task_states"]!=64
        or original["adaptive_target_decision_reads"]!=17
        or original["periodic_nonadaptive_target_decision_reads"]!=16):
        raise ValueError("Original preregistered source count/privileged reads changed")
    episodes=[]
    for task,start in BASES.items():
        for chunk in range(4):
            name=f"query_placebo_{task}_chunk{chunk}_original8.json"
            source=json.loads((directory/name).read_text("utf-8"))
            for row in source["episodes"]:
                seed=row["seed"]
                flags=row["success_once"]
                info=row["privileged_target_readback_decision_count"]
                if (flags[PLACEBO] != (flags[ALWAYS] if seed%4==0 else flags[NOQUERY])
                    or info[PLACEBO]!=int(seed%4==0)):
                    raise ValueError("Cannot splice fixed-step-3 query potential outcomes: "
                                     "actual periodic PhysX control differs")
                after=row.get("robust_common_action_refusals",{}).get(ADAPTIVE,[])
                if info[ADAPTIVE]==0 and after:
                    raise ValueError("Unaccounted attempted/denied target readback")
                if info[ADAPTIVE]==1 and len(after)!=1:
                    raise ValueError("Adaptive readback step not honestly recorded")
                episodes.append({
                    "task":task,"seed":seed,
                    "adaptive_success":flags[ADAPTIVE],
                    "never_query_success":flags[NOQUERY],
                    "fixed_step3_query_success":flags[ALWAYS],
                    "actual_periodic_control_success":flags[PLACEBO],
                    "adaptive_decision_reads":info[ADAPTIVE],
                    "adaptive_actual_query_step":after[0]["step"] if after else None,
                    "fixed_query_potential_gain":
                        int(flags[ALWAYS])-int(flags[NOQUERY]),
                })
    if len(episodes)!=64 or len({(e["task"],e["seed"]) for e in episodes})!=64:
        raise ValueError("Original subject-independent reset-state denominator corrupted")
    gains=[row["fixed_query_potential_gain"] for row in episodes]
    dist=exact_uniform_fixed_query_distribution(gains,budget)
    successes_zero=sum(x["never_query_success"] for x in episodes)
    successes_adaptive=sum(x["adaptive_success"] for x in episodes)
    queried_adaptive=[x for x in episodes if x["adaptive_decision_reads"]==1]
    mismatches=[
        x for x in episodes if x["adaptive_success"]!=(
            x["fixed_step3_query_success"] if x["adaptive_decision_reads"] else
            x["never_query_success"])
    ]
    # This is exactly the "action timing changes the actual policy rollout"
    # control: these mismatches are important, NOT to be discarded.
    if successes_adaptive!=58 or successes_zero!=41 or len(queried_adaptive)!=17:
        raise ValueError("Author-operated prospective PhysX original outcomes changed")
    favorable=sum(d==1 for d in gains)
    harmful=sum(d==-1 for d in gains)
    queried_success_outside_simple_binary_switch=[
        {"task":r["task"],"seed":r["seed"],
         "adaptive_query_step":r["adaptive_actual_query_step"],
         "adaptive_succeeded":r["adaptive_success"],
         "fixed_read_success":r["fixed_step3_query_success"],
         "never_read_success":r["never_query_success"]}
        for r in mismatches
    ]
    total=comb(len(episodes),budget)
    success_counts={
        str(successes_zero+gain): count for gain,count in dist.items()
    }
    numerator=sum(num for gain,num in dist.items()
        if successes_zero+gain>=successes_adaptive)
    expected_success=successes_zero+budget*(favorable-harmful)/len(episodes)
    return {
        "analysis":"retrospective exact finite-population fixed-schedule counterfactual",
        "original_2026_run_id":37833053629,
        "original_checkpoint_hash_and_all_64_source_audit":True,
        "original_checksum_manifest_git_blob":ORIGINAL_MANIFEST_GIT_BLOB,
        "original_eight_source_sha256":files,
        "n_independent_reset_states":64,
        "two_frozen_pretrained_PPO_models_not_64_models":True,
        "actually_executed_periodic_arm_matches_matched_step3_outcomes":True,
        "fixed_step3_readback_budget":budget,
        "adaptive_actually_used_readbacks":17,
        "never_query_observed_successes":successes_zero,
        "mandatory_fixed_step3_query_observed_successes":sum(
            x["fixed_step3_query_success"] for x in episodes),
        "adaptive_actual_successes":successes_adaptive,
        "conditional_fixed_step3_query_gain_histogram":{
            "-1":harmful,"0":sum(d==0 for d in gains),"1":favorable,
        },
        "uniform_random_fixed_schedule_expected_successes":expected_success,
        "uniform_random_fixed_schedule_success_distribution_exact_integer_counts":success_counts,
        "uniform_random_success_at_least_adaptive": {
            "numerator":str(numerator),"denominator":str(total),
            "decimal":numerator/total,
        },
        "selective_policy_depends_on_in_trajectory_query_timing_not_just_seed_switch":bool(mismatches),
        "adaptive_outcome_not_recoverable_by_fixed_query_or_never_query":queried_success_outside_simple_binary_switch,
        "all_original_cases_including_negative_preserved":True,
        "interpretation_boundary":(
            "This is a post-hoc finite-cohort allocation-combinatorics "
            "description validated against a real 16-case periodic baseline, "
            "NOT an independently randomized experiment, not an inferential "
            "p-value for adaptive method quality, not a prospective "
            "equal-information or robotics safety guarantee."
        ),
        "outcome_was_not_used_to_choose_controller_thresholds_in_source_run":True,
        "independent_external_reproduction":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=original_allocation_audit(a.input_dir)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "n":result["n_independent_reset_states"],
        "budget":result["fixed_step3_readback_budget"],
        "random_fixed_expected_success":result["uniform_random_fixed_schedule_expected_successes"],
        "observed_adaptive_success":result["adaptive_actual_successes"],
        "exact_fraction_of_random_fixed_allocations_at_least_as_good":
            result["uniform_random_success_at_least_adaptive"],
        "adaptive_not_binary_arm_splice_cases":
            result["adaptive_outcome_not_recoverable_by_fixed_query_or_never_query"]
    },sort_keys=True))


if __name__=="__main__":
    main()
