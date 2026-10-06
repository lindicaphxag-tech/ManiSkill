#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def key(row):
    return (int(row["source_action_step"]), int(row["retry"]))


def qdist(a, b):
    a=np.asarray(a,dtype=np.float64)
    b=np.asarray(b,dtype=np.float64)
    return float(min(np.linalg.norm(a-b),np.linalg.norm(a+b)))


def linf(a,b):
    return float(np.max(np.abs(np.asarray(a,dtype=np.float64)-np.asarray(b,dtype=np.float64))))


def pair_summary(a,b, tol=1e-6):
    am={key(r):r for r in a["rows"]}
    bm={key(r):r for r in b["rows"]}
    common=sorted(set(am)&set(bm))
    first_request_div=None
    first_action_div=None
    first_state_div=None
    prefix=[]
    for k in common:
        ra,rb=am[k],bm[k]
        request_diff=max(
            linf(ra["delta_position"],rb["delta_position"]),
            qdist(ra["delta_q_inverse_input"],rb["delta_q_inverse_input"]),
        )
        action_diff=linf(ra["executed_arm_action"],rb["executed_arm_action"])
        state_diff=max(
            linf(ra["ee_position_before"],rb["ee_position_before"]),
            qdist(ra["ee_quaternion_before"],rb["ee_quaternion_before"]),
        )
        if first_request_div is None and request_diff>tol:
            first_request_div={"key":list(k),"magnitude":request_diff}
        if first_action_div is None and action_diff>tol:
            first_action_div={"key":list(k),"magnitude":action_diff}
        if first_state_div is None and state_diff>tol:
            first_state_div={"key":list(k),"magnitude":state_diff}
        if request_diff<=tol and state_diff<=tol:
            prefix.append((ra,rb))
        else:
            break

    prefix_a=[x[0]["semantic_rotation_error_deg"] for x in prefix]
    prefix_b=[x[1]["semantic_rotation_error_deg"] for x in prefix]
    prefix_delta=[
        bb-aa for aa,bb in zip(prefix_a,prefix_b)
    ]
    return {
        "same_trace_keys": set(am)==set(bm),
        "a_only_keys":[list(x) for x in sorted(set(am)-set(bm))],
        "b_only_keys":[list(x) for x in sorted(set(bm)-set(am))],
        "first_request_divergence":first_request_div,
        "first_action_divergence":first_action_div,
        "first_state_divergence":first_state_div,
        "identical_request_state_prefix_calls":len(prefix),
        "prefix_mean_semantic_error_a_deg":(
            float(np.mean(prefix_a)) if prefix_a else None
        ),
        "prefix_mean_semantic_error_b_deg":(
            float(np.mean(prefix_b)) if prefix_b else None
        ),
        "prefix_mean_b_minus_a_deg":(
            float(np.mean(prefix_delta)) if prefix_delta else None
        ),
        "max_executed_action_linf_on_common_keys":(
            max(linf(am[k]["executed_arm_action"],bm[k]["executed_arm_action"]) for k in common)
            if common else None
        ),
        "max_physical_action_linf_on_common_keys":(
            max(linf(am[k]["physical_arm_action"],bm[k]["physical_arm_action"]) for k in common)
            if common else None
        ),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--main",required=True)
    p.add_argument("--candidate",required=True)
    p.add_argument("--candidate-fixed",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()

    main_r=load(a.main)
    cand=load(a.candidate)
    fixed=load(a.candidate_fixed)

    report={
        "schema_version":1,
        "episode_id":8,
        "variants":{
            name:{
                k:v for k,v in doc.items() if k!="rows"
            }
            for name,doc in (
                ("current_main",main_r),
                ("contract_adapter_v2",cand),
                ("contract_adapter_v2_controller_fixed",fixed),
            )
        },
        "comparisons":{
            "main_vs_candidate":pair_summary(main_r,cand),
            "candidate_vs_controller_fixed":pair_summary(cand,fixed),
        },
    }

    comp=report["comparisons"]["main_vs_candidate"]
    inv=report["comparisons"]["candidate_vs_controller_fixed"]
    report["certificates"]={
        "candidate_controller_invariant_trace":bool(
            inv["same_trace_keys"]
            and (inv["max_executed_action_linf_on_common_keys"] or 0.0)<=1e-6
            and (inv["max_physical_action_linf_on_common_keys"] or 0.0)<=1e-6
        ),
        "saturation_authority_was_insufficient":bool(
            (not cand["final_success"])
            and cand["retry_calls"]>0
        ),
        "candidate_locally_no_worse_on_identical_prefix":bool(
            comp["identical_request_state_prefix_calls"]>0
            and comp["prefix_mean_b_minus_a_deg"] is not None
            and comp["prefix_mean_b_minus_a_deg"]<=1e-6
        ),
        "execution_differs_despite_local_prefix_semantics":bool(
            main_r["final_success"]
            and not cand["final_success"]
            and comp["identical_request_state_prefix_calls"]>0
        ),
    }
    report["claim_boundary"]=(
        "Mechanistic trace of the single known execution-discordant episode. "
        "Paired local semantic error is compared only while request and pre-step "
        "EE state remain identical within tolerance; later divergent states are "
        "not treated as paired semantic observations."
    )

    Path(a.output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
