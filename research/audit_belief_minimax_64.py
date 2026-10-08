"""Stdlib-only 64-case original frozen-PPO unknown-ACK evidence integrity audit.

Post-outcome source verifier: checks all eight predeclared task/fault/chunk files
and preserved failures without resampling or rerunning PhysX.
NOT independent execution, safety verification or a new statistical study.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BASES = {"pull_cube":96001,"stack_cube":97001}
FAULTS = ("applied_no_ack","neutral_arm_delta_no_ack")
ARMS = (
    "source","oracle_live_memory","recovered_one_readback",
    "optimistic_assume_applied","pessimistic_assume_neutral",
    "fail_closed_stop","belief_minimax_zero_readback"
)
PRECOMMITTED = "research/CST_BELIEF_MINIMAX_PROSPECTIVE_64_V1.json"
EXPECTED_SHA = {
    "pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
    "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"
}
# Post-outcome audit EXPECTATIONS, not a predeclared claim threshold.
KNOWN_COUNTS = {
    "source":60,"oracle_live_memory":61,
    "recovered_one_readback":62,
    "optimistic_assume_applied":48,
    "pessimistic_assume_neutral":43,
    "belief_minimax_zero_readback":43,
    "fail_closed_stop":0,
}

def audit(root:Path):
    records=[]
    groups=[]
    for task, first in BASES.items():
        for condition in FAULTS:
            for chunk in (0,1):
                name=f"belief_minimax_{task}_{condition}_chunk{chunk}_fresh8.json"
                path=root/name
                if not path.is_file() or not path.stat().st_size:
                    raise ValueError(f"Missing ORIGINAL source evidence: {name}")
                report=json.loads(path.read_text(encoding="utf-8"))
                seeds=list(range(first+8*chunk,first+8*(chunk+1)))
                if (report.get("schema")!="cst_belief_minimax_64_prospective_v1"
                    or report.get("preregistration")!=PRECOMMITTED
                    or report.get("chunk")!=chunk
                    or report.get("task")!=
                      ("PullCube-v1" if task=="pull_cube" else "StackCube-v1")
                    or report.get("fault")!=condition
                    or report.get("seeds")!=seeds
                    or report.get("checkpoint_sha256")!=EXPECTED_SHA[task]
                    or report.get("training_performed") is not False
                    or report.get("backend")!="physx_cpu"):
                    raise ValueError(f"Original method identity, model or 8 seeds mismatched: {name}")
                rows=report.get("rows")
                if not isinstance(rows,list) or len(rows)!=8:
                    raise ValueError(f"Wrong predeclared denominator: {name}")
                counts={n:0 for n in ARMS}
                for index,row in enumerate(rows):
                    if row.get("seed")!=seeds[index] or row.get("fault")!=condition:
                        raise ValueError(f"Duplicated or missing original seed: {name}")
                    if row.get("midpoint_belief_size_at_fault")!=2:
                        raise ValueError(f"Unobserved two-world ambiguity: {name}")
                    if row.get("readback_queries",{}).get("belief_minimax_zero_readback")!=0:
                        raise ValueError(f"Zero-readback research arm secretly used target readback: {name}")
                    if row.get("readback_queries",{}).get("recovered_one_readback")!=1:
                        raise ValueError(f"Recovery arm missing exactly one authoritative read: {name}")
                    if row.get("midpoint_final_target_hypothesis_error_m") is None or not (
                        0<=row["midpoint_final_target_hypothesis_error_m"]<0.0002
                    ):
                        raise ValueError(f"Unknown true target not in declared finite belief: {name}")
                    if not all(row.get("fault_reached",{}).get(n) is True for n in ARMS if n!="source"):
                        raise ValueError(f"Unreached fault contaminated success: {name}")
                    if not all(isinstance(row.get("success_once",{}).get(n),bool) for n in ARMS):
                        raise ValueError(f"Missing official per-arm native task result: {name}")
                    for n in ARMS:
                        counts[n]+=int(row["success_once"][n])
                    records.append({"task":task,"fault":condition,"seed":seeds[index],
                                    "success":{n:row["success_once"][n] for n in ARMS}})
                if report.get("success_count")!=counts:
                    raise ValueError(f"Original aggregate differs from per-seed rows: {name}")
                groups.append({"task":task,"fault":condition,"chunk":chunk,
                               "name":name,"success":counts})
    if len(records)!=64 or len({(x["task"],x["fault"],x["seed"]) for x in records})!=64:
        raise ValueError("Complete prespecified 64-source denominator absent")
    totals={n:sum(x["success"][n] for x in records) for n in ARMS}
    if totals!=KNOWN_COUNTS:
        raise ValueError(f"Original post-outcome source counts corrupted: {totals}")
    pair={}
    method="belief_minimax_zero_readback"
    for ref in ("optimistic_assume_applied","pessimistic_assume_neutral","recovered_one_readback"):
        pair[ref]={
            "robust_only":sum(x["success"][method] and not x["success"][ref] for x in records),
            "reference_only":sum(x["success"][ref] and not x["success"][method] for x in records)
        }
    result={
        "schema":"source_64_cst_minimax_integrity_audit_v1",
        "source_experiment_run_id":37825781536,
        "original_distinct_task_seed_states":32,
        "actual_task_seed_fault_conditions":64,
        "source_cases":len(records),
        "aggregated_native_task_success":totals,
        "paired_discordance":pair,
        "original_group_counts":groups,
        "provenance_boundary":"same-contributor source artifact audit, not independent PhysX reproduction",
        "known_negative_result":True,
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit(args.input_dir)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("BELIEF_MINIMAX_64_SOURCE_AUDIT",json.dumps({
        "cases":out["source_cases"],
        "unique_seed_states":out["original_distinct_task_seed_states"],
        "counts":out["aggregated_native_task_success"],
        "paired":out["paired_discordance"],
    },sort_keys=True))


if __name__=="__main__":
    main()
