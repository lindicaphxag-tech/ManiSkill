"""Recount FIRST 64 original real PhysX episodes in immutable failed-run logs.

The 64 episodes all completed before a post-run NameError. This is independent
ARITHMETIC on original logs, not repeated robot physics or external recognition.
"""
import hashlib,json
from pathlib import Path
from math import comb

LOG_SHA={
"pull_cube":[
"f628df9d901c17e7b15e865fbbe850c7475444f1e2275de5ee95319d76a88844",
"c29da9498e2d1af6763d8afc8e71ae73d8a7936f84448b2e16aa4de96a5e342b",
"97adf8b281250243e81e51f3a1973c5e13d1b8cc6846ffddf037cfcd73b4952e",
"cd671a6c3b016df6beb1916de4b943575ab02ea164b063bb1ed03698d50df3f"],
"stack_cube":[
"9df0a40fc708b5006a94111403c95e7adb773d9531c78e8765e2aa50cf9358e5",
"3d51e959ecd3e878151896f1fe2b60edbc7ea54f6387501a2e0321fbbc904109",
"c5145782c495b244c1766dc27a7e7386d7b5719b80547a01b9dad5729bcfb93a",
"476c6793cd7285c99a4a3608d5492800b1d962bb1de682cd2ebfff5f85f11d51"]}
ARMS=("source_no_fault","fault_robust_then_single_privileged_query",
"fault_fixed_readback_canonical","fault_reachable_then_single_privileged_query")
INFO={"pull_cube":(2026220001,"PullCube-v1"),"stack_cube":(2026230001,"StackCube-v1")}

def recount(root):
    root=Path(root);rows=[]
    for task in LOG_SHA:
        for shard,digest in enumerate(LOG_SHA[task]):
            p=root/f"reachable-so3-original-{task}-{shard}"/f"reachable_{task}_{shard}.log"
            raw=p.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError("ORIGINAL_SHA_DRIFT")
            s=raw.decode("utf-8")
            if s.count("NameError: name 'PROTO' is not defined")!=1:
                raise ValueError("FAILURE_STAGE_DIFFERENT")
            marker="REACHABLE_SO3_ORIGINAL_EPISODE "
            eight=[json.loads(line.split(marker,1)[1])
                   for line in s.splitlines() if marker in line]
            first,tname=INFO[task]
            if len(eight)!=8 or [r["seed"] for r in eight]!=list(range(first+shard*8,first+shard*8+8)):
                raise ValueError("MISSING_OR_DUPLICATE_FROZEN_SEEDS")
            for r in eight:
                if r["task"]!=tname or tuple(r["success_once"])!=ARMS:
                    raise ValueError("TASK_OR_ARM_MISMATCH")
            rows+=eight
    if len(rows)!=64 or len({r["seed"] for r in rows})!=64:raise ValueError("RESET_COUNT")
    result={"original_workflow":38546430880,"original_workflow_conclusion":"failure: post-episode NameError",
     "original_physx_reset_clusters":64,"actual_executed_matched_worlds":256,
     "no_physics_rerun":True,"not_outside_lab":True,
     "by_task":{},"overall":{},"paired":{}}
    for task,(_,name) in INFO.items():
        group=[r for r in rows if r["task"]==name]
        result["by_task"][name]={}
        for a in ARMS:
            result["by_task"][name][a]={
                "success":sum(int(r["success_once"][a]) for r in group),
                "readbacks":sum(r["privileged_target_readback_decision_count"][a] for r in group),
                "source_robust_authorizations":sum(r["robust_common_action_authorizations"].get(a,0) for r in group),
                "two_fault_exposures":sum(len(r.get("faults",{}).get(a,[]))==2 for r in group) if a!=ARMS[0] else None}
    for a in ARMS:
        result["overall"][a]={
            "success":sum(r["success_once"][a] for r in rows),
            "reads":sum(r["privileged_target_readback_decision_count"][a] for r in rows),
            "robust_authorizations":sum(r["robust_common_action_authorizations"].get(a,0) for r in rows),
            "two_fault_exposures":sum(len(r.get("faults",{}).get(a,[]))==2 for r in rows) if a!=ARMS[0] else None}
    for base in ARMS[1:3]:
        newer=ARMS[-1]
        plus=sum(r["success_once"][newer] and not r["success_once"][base] for r in rows)
        minus=sum(r["success_once"][base] and not r["success_once"][newer] for r in rows)
        n=plus+minus
        p=min(1,2*sum(comb(n,i) for i in range(min(plus,minus)+1))/2**n) if n else 1
        result["paired"][base]=dict(new_only=plus,baseline_only=minus,exploratory_p=p)
    z=result["overall"];old,fixed,new=ARMS[1:]
    result["precommitted_gate"]={
        "all_64_faults":all(z[a]["two_fault_exposures"]==64 for a in ARMS[1:]),
        "new_success_not_below_fixed":z[new]["success"]>=z[fixed]["success"],
        "save_at_least_4_reads_vs_old":z[new]["reads"]+4<=z[old]["reads"]}
    result["precommitted_gate"]["pass"]=all(result["precommitted_gate"].values())
    if [(z[a]["success"],z[a]["reads"]) for a in ARMS]!=[(59,0),(46,41),(55,64),(45,40)]:
        raise AssertionError("FIRST_OUTCOME_RECOUNT_DRIFT")
    if z[new]["robust_authorizations"]!=891 or z[old]["robust_authorizations"]!=865:
        raise AssertionError("AUTHORITY_RECOUNT_DRIFT")
    if result["precommitted_gate"]["pass"]:raise AssertionError("INVALID_POSITIVE_CLAIM")
    return result

if __name__=="__main__":
    import sys
    v=recount(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
    print(json.dumps(v,sort_keys=True))
