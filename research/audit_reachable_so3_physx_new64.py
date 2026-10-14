"""Count complete original PhysX task outcomes without imputation or arm selection."""
import json
from collections import defaultdict
from pathlib import Path
from math import comb

ARMS=("source_no_fault","fault_robust_then_single_privileged_query",
      "fault_fixed_readback_canonical","fault_reachable_then_single_privileged_query")
BASE={"PullCube-v1":2026220001,"StackCube-v1":2026230001}

def exact_p_value(b,c):
    n=b+c
    if n==0:return 1.
    lo=min(b,c)
    return min(1.,2*sum(comb(n,i) for i in range(lo+1))/2**n)

def audit(folder):
    allrows=[]
    for task,first in BASE.items():
        paths=sorted(Path(folder).glob("reachable_so3_"+("pull_cube" if "Pull" in task else "stack_cube")+"_chunk*_original8.json"))
        if len(paths)!=4:raise ValueError("Missing original 8-person task shards")
        rows=[]
        for p in paths:
            d=json.loads(p.read_text())
            if d["task"]!=task or d["schema"]!="reachable_native_so3_4arm_fresh64_v1":
                raise ValueError("Wrong protocol, model or task")
            if tuple(d["all_four_actual_control_arms"])!=ARMS:
                raise ValueError("Comparator substitution")
            if d["original_external_frozen_checkpoint_sha256"] not in (
                "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
                "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"
            ):
                raise ValueError("Published actor weight digest drift")
            rows+=d["episodes"]
        if len(rows)!=32 or {r["seed"] for r in rows}!=set(range(first,first+32)):
            raise ValueError("Missing or duplicate genuinely new reset")
        if {r["task"] for r in rows}!={task}:raise ValueError("Incorrect public task")
        allrows+=rows
    out=dict(original_reset_clusters=64,paired_native_controller_worlds=256,
             newly_trained_models=0,external_independent_lab=False,
             raw_executed_worlds_not_outcome_imputations=True,
             per_task={},overall={},gate={})
    for task in BASE:
        rows=[r for r in allrows if r["task"]==task]
        out["per_task"][task]={}
        for arm in ARMS:
            out["per_task"][task][arm]={
                "n":len(rows),
                "task_success":sum(bool(r["success_once"][arm]) for r in rows),
                "readbacks":sum(r["privileged_target_readback_decision_count"][arm] for r in rows),
                "injection_steps_seen":sum(len(r["faults"].get(arm,[])) for r in rows) if arm!="source_no_fault" else 0,
                "authorized_common_actions":sum(r["robust_common_action_authorizations"].get(arm,0) for r in rows),
                "refused_episodes":sum(arm in r["refusals"] for r in rows)
            }
    for arm in ARMS:
        out["overall"][arm]={
            "task_success":sum(bool(r["success_once"][arm]) for r in allrows),
            "readbacks":sum(r["privileged_target_readback_decision_count"][arm] for r in allrows),
            "full_fault_exposure":sum(len(r["faults"].get(arm,[]))==2 for r in allrows) if arm!="source_no_fault" else None}
    new=ARMS[-1];old=ARMS[1];fixed=ARMS[2]
    out["paired"]={}
    for control in (old,fixed):
        both=sum(bool(r["success_once"][new]) and bool(r["success_once"][control]) for r in allrows)
        only_new=sum(bool(r["success_once"][new]) and not bool(r["success_once"][control]) for r in allrows)
        only_control=sum(not bool(r["success_once"][new]) and bool(r["success_once"][control]) for r in allrows)
        out["paired"][control]=dict(both=both,only_new=only_new,only_control=only_control,
                                   both_failed=len(allrows)-both-only_new-only_control,
                                   exact_two_sided_mcnemar_exploratory=exact_p_value(only_new,only_control))
    out["gate"]={
        "full_64_fault_exposure":all(out["overall"][arm]["full_fault_exposure"]==64 for arm in ARMS[1:]),
        "not_worse_task_success_than_fixed":out["overall"][new]["task_success"]>=out["overall"][fixed]["task_success"],
        "saves_4_or_more_reads_vs_old":out["overall"][new]["readbacks"]+4<=out["overall"][old]["readbacks"],
        "passes_original_preoutcome_joint_gate":False}
    out["gate"]["passes_original_preoutcome_joint_gate"]=all(
        out["gate"][k] for k in ("full_64_fault_exposure","not_worse_task_success_than_fixed","saves_4_or_more_reads_vs_old"))
    return out

if __name__=="__main__":
    import sys
    x=audit(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
    print(json.dumps(x,sort_keys=True))
