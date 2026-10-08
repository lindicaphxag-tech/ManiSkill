"""Independent retrospective audit for ORIGINAL frozen two-unknown-ACK PhysX.

No physics replay, no posthoc threshold tuning. Count all seed/arm failures;
do not silently discard episodes with only one reached fault.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

NAMES=(
"source_no_fault","fault_oracle_private_target",
"fault_optimistic_unverified_ack","fault_strict_common_exact",
"fault_robust_two_history_without_query",
"fault_robust_then_single_privileged_query",
"fault_always_single_privileged_query"
)
TASKS={
"pull_cube":("PullCube-v1",230001,
"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
"stack_cube":("StackCube-v1",240001,
"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")
}
SELECTIVE="fault_robust_then_single_privileged_query"
MANDATORY="fault_always_single_privileged_query"


def audit(files:Path)->dict:
    report={"schema":"two_unknown_ack_original_all_seed_authority_audit",
    "original_unique_reset_states":16,
    "original_retrained_policy":False,
    "all_missing_two_fault_exposures_included":True,
    "third_party_external_reproduction":False,
    "by_task":{}}
    for task,(name,first,sha) in TASKS.items():
        path=files/f"two_ack_khistory_{task}_original8.json"
        raw=json.loads(path.read_text())
        if (raw.get("schema")!="two_unknown_ack_khistory_certify_query_physx_v1"
            or raw.get("task")!=name
            or raw.get("original_external_frozen_checkpoint_sha256")!=sha
            or raw.get("original_seed_population")!=list(range(first,first+8))
            or raw.get("frozen_model_retrained") is not False
            or raw.get("real_physx_simulator") is not True
            or raw.get("multi_target_unknown_fault_steps")!=[2,4]
            or raw.get("independent_external_reproduction") is not False
            or raw.get("no_claim_of_global_multi_rotation_optimality") is not True
            or raw.get("all_seven_actual_control_arms")!=list(NAMES)):
            raise ValueError(f"Original frozen source/model/benchmark identity mismatched: {task}")
        rows=raw.get("episodes")
        if not isinstance(rows,list) or len(rows)!=8:
            raise ValueError("All eight original task trials, including failures, required")
        success={n:0 for n in NAMES}
        faults_reached={n:0 for n in NAMES[1:]}
        all_fault_events={n:0 for n in NAMES[1:]}
        max_k=1
        reads={n:0 for n in (SELECTIVE,MANDATORY)}
        for i,row in enumerate(rows):
            if row.get("seed")!=first+i or row.get("task")!=name:
                raise ValueError("Original state missing, duplicated or out of order")
            outcomes=row.get("success_once")
            if not isinstance(outcomes,dict) or set(outcomes)!=set(NAMES) or any(type(x) is not bool for x in outcomes.values()):
                raise ValueError("Unreported/malformed official task outcomes")
            q=row.get("privileged_target_readback_decision_count",{})
            if (q.get("fault_oracle_private_target")!=-1
                or q.get(SELECTIVE) not in (0,1,2)
                or q.get(MANDATORY) not in (0,1,2)
                or q.get("fault_optimistic_unverified_ack")!=0
                or q.get("fault_robust_two_history_without_query")!=0):
                raise ValueError("Illegitimate or hidden privileged decision readback")
            for n in reads:reads[n]+=q[n]
            for n in NAMES:success[n]+=int(outcomes[n])
            for n in NAMES[1:]:
                events=row.get("faults",{}).get(n,[])
                if (not isinstance(events,list) or len(events)>2
                    or [e.get("step") for e in events] not in ([],[2],[2,4])
                    or any(e.get("controller_execution_ack_seen_by_adapter")!="unknown"
                        or e.get("actual_native_arm_command")!="all_zero_hold"
                        for e in events)):
                    raise ValueError("Fault/probe event attribution falsified")
                all_fault_events[n]+=len(events)
                faults_reached[n]+=int(len(events)==2)
            for n,events in row.get("certified_intent_suppressed_by_actual_fault",{}).items():
                if n not in NAMES[1:] or not isinstance(events,list):
                    raise ValueError("Certified intended-but-not-dispatched arm invalid")
                physically_held={f["step"] for f in row.get("faults",{}).get(n,[])}
                actually_audited={e.get("step") for e in
                    row.get("robust_native_target_bound_checks",{}).get(n,[])}
                for e in events:
                    step=e.get("step")
                    if (step not in (2,4) or step not in physically_held
                        or step in actually_audited
                        or e.get("certificate_was_for_requested_not_delivered_action") is not True
                        or e.get("must_not_claim_bound_was_physically_executed") is not True):
                        raise ValueError("False dispatched-certificate claim during actually suppressed physical command")
            for n,details in row.get("robust_native_target_bound_checks",{}).items():
                if n not in NAMES or not isinstance(details,list):
                    raise ValueError("Unknown claimed certificate arm")
                for e in details:
                    physically_held={v["step"] for v in row.get("faults",{}).get(n,[])}
                    if e.get("step") in physically_held:
                        raise ValueError("Attempt to certify an injected, intentionally NOT-delivered native command")
            for n,details in row.get("candidate_history_count",{}).items():
                if n not in NAMES or not isinstance(details,list):raise ValueError("Invalid belief history log")
                for entry in details:
                    k=entry.get("count",0)
                    if type(k) is not int or not 2<=k<=16:
                        raise ValueError("Invalid possible target history multiplicity")
                    max_k=max(k,max_k)
        if raw.get("success_counts")!=success:
            raise ValueError("Original success aggregate manipulated")
        if raw.get("fault_reached_counts")!=faults_reached:
            raise ValueError("Original second-fault exposure mismatch")
        if raw.get("max_hypotheses_observed")!=max_k:
            raise ValueError("Original belief multiplicity aggregate manipulated")
        report["by_task"][task]={
            "task":name,"first_seed":first,"eight_original_states":8,
            "native_task_success":success,
            "both_faults_reached":faults_reached,
            "total_actual_fault_events":all_fault_events,
            "maximum_logged_credible_histories":max_k,
            "selective_privileged_decision_reads":reads[SELECTIVE],
            "mandatory_privileged_decision_reads":reads[MANDATORY],
        }
    totals={}
    for n in NAMES:
        totals[n]=sum(report["by_task"][task]["native_task_success"][n] for task in TASKS)
    report["all16_task_success"]=totals
    report["all16_max_observed_K"]=max(z["maximum_logged_credible_histories"] for z in report["by_task"].values())
    report["readbacks_selective_total"]=sum(z["selective_privileged_decision_reads"] for z in report["by_task"].values())
    report["readbacks_mandatory_total"]=sum(z["mandatory_privileged_decision_reads"] for z in report["by_task"].values())
    report["both_faults_all_selective_cases"]=sum(z["both_faults_reached"][SELECTIVE] for z in report["by_task"].values())
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    out=audit(a.input_dir)
    a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("REAL_TWO_ACK_KHISTORY_ORIGINAL_AUDIT",json.dumps({
        "success":out["all16_task_success"],"max_K":out["all16_max_observed_K"],
        "selective_reads":out["readbacks_selective_total"],
        "mandatory_reads":out["readbacks_mandatory_total"],
        "second_fault_reached_selective":out["both_faults_all_selective_cases"]
    },sort_keys=True))
