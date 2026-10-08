"""Read-only, Python standard-library integrity audit of eight ORIGINAL new64 PhysX JSONs.

THIS IS POST-OUTCOME SOURCE AUDITING, NOT A SECOND SIMULATOR REPLICATION.
The method and seed list were frozen before the source run. Expected task
totals below are original observed evidence-integrity digests, not pre-outcome
prediction thresholds.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

COUNTS = {
    "source_no_fault": 60,
    "fault_oracle_private_target": 58,
    "fault_optimistic_unverified_ack": 42,
    "fault_strict_common_exact": 0,
    "fault_robust_two_history_without_query": 47,
    "fault_robust_then_single_privileged_query": 60,
    "fault_always_single_privileged_query": 57,
}
MODELS = {
    "pull_cube":("PullCube-v1",142001,
        "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube":("StackCube-v1",152001,
        "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"),
}
METHOD_SHA="db4fe4dd9d09aaff67c5dcf12213ad737162282d"
ADAPTIVE="fault_robust_then_single_privileged_query"
MANDATORY="fault_always_single_privileged_query"

def audit(directory: Path) -> dict:
    all_rows=[]
    groups=[]
    for task,(task_name,first,ckpt) in MODELS.items():
        for chunk in range(4):
            file=directory/f"bounded_query_holdout_{task}_chunk{chunk}_original8.json"
            if not file.is_file() or not file.stat().st_size:
                raise ValueError(f"Missing original source: {file.name}")
            src=json.loads(file.read_text(encoding="utf-8"))
            expected=list(range(first+8*chunk,first+8*(chunk+1)))
            if (src.get("schema")!="unknown_ack_bounded_or_query_physx_v1"
                or src.get("task")!=task_name
                or src.get("original_seed_population")!=expected
                or src.get("original_external_frozen_checkpoint_sha256")!=ckpt
                or src.get("frozen_model_retrained") is not False
                or src.get("real_physx_simulator") is not True
                or src.get("fault_is_native_target_hold_not_network_loss") is not True):
                raise ValueError(f"Method, source or frozen population mismatch: {file.name}")
            trials=src.get("episodes",[])
            if len(trials)!=8:
                raise ValueError(f"Unexpected denominator in {file.name}: {len(trials)}")
            observed={k:0 for k in COUNTS}
            reads=0
            for i,r in enumerate(trials):
                if r.get("seed")!=expected[i] or r.get("task")!=task_name:
                    raise ValueError(f"Original source episode identity missing/duplicated: {file.name}")
                if set(r.get("success_once",{}))!=set(COUNTS) or not all(
                    isinstance(r["success_once"][n],bool) for n in COUNTS):
                    raise ValueError(f"Original task outcome absent/invalid: {file.name}")
                if not all(isinstance(r.get("faults",{}).get(n),dict)
                    for n in COUNTS if n!="source_no_fault"):
                    raise ValueError(f"Physics fault not reached in all arms: {file.name}")
                q=r.get("privileged_target_readback_decision_count",{})
                if (q.get("fault_robust_two_history_without_query")!=0
                    or q.get("fault_optimistic_unverified_ack")!=0
                    or q.get("fault_strict_common_exact")!=0
                    or q.get(ADAPTIVE) not in (0,1)
                    or q.get(MANDATORY)!=1
                    or q.get("fault_oracle_private_target")!=-1):
                    raise ValueError(f"Readback information budget corrupted: {file.name}")
                reads+=q[ADAPTIVE]
                for key in COUNTS:
                    observed[key]+=int(r["success_once"][key])
                all_rows.append({
                    "task":task,"seed":expected[i],
                    "success":{n:r["success_once"][n] for n in COUNTS},
                    "selective_readback":q[ADAPTIVE],
                    "bounded_authorizations":r.get("robust_common_action_authorizations",{}).get(ADAPTIVE,0),
                    "query_counterfactual":"mandatorily queried once",
                })
            if observed!=src.get("success_counts"):
                raise ValueError(f"Original per-state counts disagree with JSON summary: {file.name}")
            if reads!=sum(src.get("selective_readback_counts",[])):
                raise ValueError(f"Original per-state query counts disagree: {file.name}")
            groups.append({"task":task,"chunk":chunk,"seed_first":expected[0],
                "seed_last":expected[-1],"source_json":file.name,
                "task_success":observed,"selective_reads":reads})
    if len(all_rows)!=64 or len({(r["task"],r["seed"]) for r in all_rows})!=64:
        raise ValueError("Missing or duplicated preregistered unique holdout states")
    success={key:sum(int(r["success"][key]) for r in all_rows) for key in COUNTS}
    if success!=COUNTS:
        raise ValueError(f"Original frozen source outcome changed: {success}")
    total_q=sum(r["selective_readback"] for r in all_rows)
    if total_q!=15:
        raise ValueError(f"Original selective query count changed: {total_q}")
    paired={}
    for other in ["fault_optimistic_unverified_ack",
                  "fault_robust_two_history_without_query",MANDATORY]:
        paired[other]={
            "adaptive_only":sum(r["success"][ADAPTIVE] and not r["success"][other] for r in all_rows),
            "comparator_only":sum(not r["success"][ADAPTIVE] and r["success"][other] for r in all_rows)
        }
    return {
        "schema":"robust_query_new64_original_evidence_audit",
        "method_exact_original_head":METHOD_SHA,
        "source_physx_run_id":37828426195,
        "unique_original_seed_states":64,
        "eight_original_json_files":8,
        "original_native_task_success":success,
        "selective_privileged_readback_decisions":total_q,
        "mandatory_privileged_readback_decisions":64,
        "selective_vs_comparators":paired,
        "all_original_chunks":groups,
        "limitations":"contributor-operated source replay audit, not third-party physics execution, not hardware safety"
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.input_dir)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("NEW64_ORIGINAL_SOURCE_AUDIT",json.dumps({
        "seed_count":result["unique_original_seed_states"],
        "counts":result["original_native_task_success"],
        "selective_reads":result["selective_privileged_readback_decisions"],
        "mandatory_reads":result["mandatory_privileged_readback_decisions"]
    },sort_keys=True))
if __name__=="__main__":
    main()
