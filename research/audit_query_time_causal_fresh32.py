"""Independent full original source verifier for preregistered fixed query-time PhysX.
No simulator dependency. Does NOT validate physical safety or independent adoption.
"""
import argparse
import json
from pathlib import Path

TASKS={"pull_cube":("PullCube-v1",280001,"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
       "stack_cube":("StackCube-v1",290001,"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")}
ARMS=("source_no_fault","fault_oracle_private_target","fault_optimistic_unverified_ack",
      "fault_robust_two_history_without_query","fault_robust_then_single_privileged_query",
      "fault_fixed_query_t3","fault_fixed_query_t5","fault_fixed_query_t6")
TIMES={"fault_fixed_query_t3":3,"fault_fixed_query_t5":5,"fault_fixed_query_t6":6}
PROTO="research/QUERY_TIME_CAUSAL_FRESH32_PREOUTCOME_V1.json"

def validate(data,task,chunk):
    env,first,sha=TASKS[task]
    seeds=list(range(first+chunk*4,first+chunk*4+4))
    if (data.get("schema")!="query_time_causal_intervention_new32_real_physx_v1"
        or data.get("task")!=env or data.get("original_seed_population")!=seeds
        or data.get("original_external_frozen_checkpoint_sha256")!=sha
        or data.get("frozen_protocol")!=PROTO
        or data.get("original_source_method_git_blob")!="1dc653cdc44e422c8340475ad00f828b3a41eb4f"
        or data.get("original_robust_certifier_git_blob")!="bb5fd155b7291fb127f94138fca321201c8271c3"
        or data.get("all_eight_actual_control_arms")!=list(ARMS)
        or data.get("frozen_model_retrained") is not False
        or data.get("real_physx_simulator") is not True
        or data.get("privileged_readback_counts_are_decision_only_not_audit_reads") is not True
        or data.get("precommitted_query_times")!=TIMES):
        raise ValueError("Changed frozen controller, model, query timing or source provenance")
    rows=data.get("episodes")
    if not isinstance(rows,list) or len(rows)!=4 or [r.get("seed") for r in rows]!=seeds:
        raise ValueError("Original four consecutive source seeds/rows missing")
    totals={a:0 for a in ARMS}
    reads={a:0 for a in ARMS}
    pair={"adaptive_only":0,"fixed_t3_only":0,"both":0,"neither":0}
    late_cases=[]
    for row in rows:
        if row.get("task")!=env:
            raise ValueError("Unregistered original per-row task")
        flags=row.get("success_once")
        rr=row.get("privileged_target_readback_decision_count")
        timeline=row.get("private_readback_steps",{})
        if set(flags or {})!=set(ARMS) or set(rr or {})!=set(ARMS):
            raise ValueError("All eight native controller source outcome/read ledgers required")
        if any(type(flags[a]) is not bool for a in ARMS):
            raise ValueError("Task successes must be genuine official bools")
        if any(type(rr[a]) is not int for a in ARMS):
            raise ValueError("Privileged reads must be integer counts")
        for a in ARMS:
            totals[a]+=int(flags[a])
            reads[a]+=int(rr[a])
        if rr["fault_oracle_private_target"]!=-1 or any(rr[a]!=0 for a in
                   ("source_no_fault","fault_optimistic_unverified_ack",
                    "fault_robust_two_history_without_query")):
            raise ValueError("Forged oracle/zero-read information budget")
        for a,expected in TIMES.items():
            if rr[a] not in (0,1):
                raise ValueError("Fixed step3/5/6 arm may have at most one target read")
            if timeline.get(a,[])!=([expected] if rr[a] else []):
                raise ValueError("Privileged query occurred at wrong fixed time")
            if a in row.get("refusals",{}) and rr[a]==0:
                stop=row["refusals"][a].get("step")
                if type(stop) is not int or stop>expected:
                    raise ValueError("Unexpected fixed-arm refusal after its planned query")
        aa="fault_robust_then_single_privileged_query"
        if rr[aa] not in (0,1) or len(timeline.get(aa,[]))!=rr[aa]:
            raise ValueError("Invalid event-triggered target read count/timing")
        if rr[aa] and (type(timeline[aa][0]) is not int or timeline[aa][0]<3):
            raise ValueError("Adaptive read before ambiguity or invalid log")
        for a in ARMS[1:]:
            x=row.get("faults",{}).get(a)
            if not isinstance(x,dict) or x.get("step")!=2 or x.get("actual_native_arm_command")!="all_zero_hold":
                raise ValueError("Missing real native physical fault injection")
            delta=row.get("initial_obs_diff",{}).get(a)
            if not isinstance(delta,(float,int)) or not 0<=delta<=5e-4:
                raise ValueError("Matched initial paired policy state not established")
        for a in ARMS:
            if a not in row.get("steps",{}):
                raise ValueError("Missing actual simulator step count or source refusal record")
        for events in row.get("native_projection_NOT_EXACT",{}).values():
            if any(p.get("exactness")!="NOT_EXACT" for p in events):
                raise ValueError("Non-exact native action misrepresented as exact")
        ap=flags["fault_robust_then_single_privileged_query"]
        f3=flags["fault_fixed_query_t3"]
        pair["both" if ap and f3 else "adaptive_only" if ap else
             "fixed_t3_only" if f3 else "neither"]+=1
        if ap and not any(flags[x] for x in
             ("fault_fixed_query_t3","fault_fixed_query_t5",
              "fault_fixed_query_t6","fault_robust_two_history_without_query")):
            late_cases.append(row["seed"])
    if totals!=data.get("success_counts"):
        raise ValueError("Original official count summary mismatches source rows")
    if [r["privileged_target_readback_decision_count"][
        "fault_robust_then_single_privileged_query"] for r in rows]!=data.get("selective_readback_counts"):
        raise ValueError("Original selective target-read count vector mismatched")
    fixed=data.get("fixed_readback_counts",{})
    if set(fixed)!=set(TIMES) or any(fixed[a]!=[
        r["privileged_target_readback_decision_count"][a] for r in rows] for a in TIMES):
        raise ValueError("Fixed arm readback count inconsistent")
    return dict(n=4,success=totals,reads=reads,paired_adaptive_vs_fixed_t3=pair,
                adaptive_only_success_vs_all_fixed_times_and_noquery=late_cases)

def aggregate(folder):
    filenames={f"query_time_{task}_chunk{chunk}_original4.json" for task in TASKS for chunk in range(4)}
    actual=list(folder.glob("query_time_*_original4.json"))
    if len(actual)!=8 or {p.name for p in actual}!=filenames:
        raise ValueError("All 8 registered genuine simulator source JSONs required")
    output={}
    for task in TASKS:
        for chunk in range(4):
            k=f"{task}:chunk{chunk}"
            output[k]=validate(json.loads((folder/f"query_time_{task}_chunk{chunk}_original4.json").read_text()),task,chunk)
    return {"schema":"query_time_causal_fresh32_full_original_evidence_v1",
            "n_original_paired_native_physx_states":32,
            "external_independent_replication":False,
            "not_hardware_safety":True,"not_network_packet_loss":True,
            "outcomes":output}

def main():
    x=argparse.ArgumentParser()
    x.add_argument("--input-dir",type=Path,required=True)
    x.add_argument("--output",type=Path,required=True)
    a=x.parse_args()
    result=aggregate(a.input_dir)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("QUERY_TIME_CAUSAL_FULL_SOURCE_AUDIT",json.dumps({
        k:{"success":v["success"],"reads":v["reads"],
           "adaptive_only_late_cases":v["adaptive_only_success_vs_all_fixed_times_and_noquery"]}
        for k,v in result["outcomes"].items()},sort_keys=True))
if __name__=="__main__":
    main()
