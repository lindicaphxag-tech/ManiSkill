"""Reproducible paired-binary and privileged-readback accounting for robot trials.

This is a descriptive/exact finite-sample audit, not a source of original
robotic method novelty or proof of population-level noninferiority.

Input is the full-denominator, independently replayable task-state aggregate.
Do not treat seven same-seed control arms as independent observations.
"""
from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path

PAIRS = (
    ("fault_robust_two_history_without_query",
     "fault_optimistic_unverified_ack"),
    ("fault_robust_then_single_privileged_query",
     "fault_always_single_privileged_query"),
    ("fault_robust_then_single_privileged_query",
     "fault_robust_two_history_without_query"),
)


def exact_paired_binary(a, b):
    """Two-sided exact McNemar sign test, conditional on discordant pairs.

    This tests equality of the two marginal binary success probabilities
    in the sampled paired experiment, under independent *task-state pair*
    observations. Does not establish a preregistered noninferiority margin,
    nor generalize a small sample of source seeds across robot platforms.
    """
    if len(a) != len(b) or not a:
        raise ValueError("Each matched task-state pair must exist")
    if any(type(x) is not bool or type(y) is not bool for x,y in zip(a,b)):
        raise ValueError("Only real paired boolean task-success flags allowed")
    left = sum(x and not y for x,y in zip(a,b))
    right = sum(y and not x for x,y in zip(a,b))
    agree = len(a)-left-right
    n=left+right
    p=1.0 if n==0 else min(
        1.0,2.0*sum(comb(n,k) for k in range(min(left,right)+1))/(2**n)
    )
    return {
        "n_original_paired_task_states":len(a),
        "a_success":sum(a),
        "b_success":sum(b),
        "a_only":left,
        "b_only":right,
        "binary_agreement":agree,
        "paired_success_difference":sum(a)-sum(b),
        "two_sided_exact_mcnemar_p_exploratory":p,
        "interpretation":"Exploratory exact paired-binary test; not evidence of noninferiority or safety."
    }


def audit_record(record):
    if record.get("independent_external_reproduction") is not False:
        raise ValueError("Unexpected or improperly relabelled independent-execution provenance")
    if record.get("original_task_state_count") not in (16,32):
        raise ValueError("Expected complete independently audited 16- or 32-state population")
    trials=[]
    strata={}
    for task_name,task in record.get("results",{}).items():
        rows=task.get("complete_original_rows")
        if not isinstance(rows,list) or len(rows) not in (8,16):
            raise ValueError("Missing complete original within-task paired source rows")
        seeds=task.get("original_seeds",[])
        if [r.get("seed") for r in rows]!=seeds:
            raise ValueError("Source trial ordering, denominator or identity changed")
        if len(set(seeds))!=len(seeds):
            raise ValueError("Duplicate physical reset seeds")
        if any(not isinstance(row.get("success_once"),dict) or
               any(type(row["success_once"].get(key)) is not bool
                   for pair in PAIRS for key in pair)
               for row in rows):
            raise ValueError("Missing real official paired success flags")
        if any(
            row["privileged_target_readback_decision_count"].get(
                "fault_oracle_private_target") != -1
            or row["privileged_target_readback_decision_count"].get(
                "fault_robust_two_history_without_query") != 0
            or not 0 <= row["privileged_target_readback_decision_count"].get(
                "fault_robust_then_single_privileged_query",-1) <= 1
            or row["privileged_target_readback_decision_count"].get(
                "fault_always_single_privileged_query") != 1
            for row in rows):
            raise ValueError("Information cost concealed or misrepresented")
        strata[task_name] = {
            f"{a}_vs_{b}":exact_paired_binary(
                [r["success_once"][a] for r in rows],
                [r["success_once"][b] for r in rows])
            for a,b in PAIRS
        }
        trials.extend(rows)
    if len(trials)!=record["original_task_state_count"] or len(strata)!=2:
        raise ValueError("Only a complete, two-task cohort can be reported")
    total={
        f"{a}_vs_{b}":exact_paired_binary(
            [r["success_once"][a] for r in trials],
            [r["success_once"][b] for r in trials])
        for a,b in PAIRS
    }
    queries_selective=sum(
        r["privileged_target_readback_decision_count"][
            "fault_robust_then_single_privileged_query"] for r in trials)
    queries_mandatory=sum(
        r["privileged_target_readback_decision_count"][
            "fault_always_single_privileged_query"] for r in trials)
    return {
        "analysis":"paired_task_state_not_independent_control_arms",
        "n_distinct_original_task_seeds":len(trials),
        "n_original_frozen_policies":len(strata),
        "paired_comparisons":total,
        "by_task":strata,
        "privileged_target_decision_reads_selective":queries_selective,
        "privileged_target_decision_reads_mandatory":queries_mandatory,
        "decision_read_fraction_saved":(
            (queries_mandatory-queries_selective)/queries_mandatory),
        "audit_only_privileged_readbacks_not_counted_as_free_hardware_measurement":True,
        "noninferiority_statistically_established":False,
        "external_reproduction":False,
        "not_hardware_or_collision_safety":True
    }


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--aggregate",required=True,type=Path)
    cli.add_argument("--output",type=Path)
    q=cli.parse_args()
    report=audit_record(json.loads(q.aggregate.read_text(encoding="utf-8")))
    s=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if q.output:
        q.output.write_text(s,encoding="utf-8")
    print(s)


if __name__=="__main__":
    main()
