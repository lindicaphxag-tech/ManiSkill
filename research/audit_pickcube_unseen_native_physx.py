"""Precommitted new TASK generalization audit, no retrospective arm selection."""
import json
from pathlib import Path
from math import comb

START=2026440001
ARMS=("source_no_fault","fault_oracle_private_target",
      "fault_robust_then_single_privileged_query",
      "fault_fixed_readback_canonical","fault_reachable_then_single_privileged_query")
SOURCE_SHAS={"pick_cube":"3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8"}
def sign_p(b,c):
    n=b+c
    return min(1.,2*sum(comb(n,i) for i in range(min(b,c)+1))/2**n) if n else 1.

def audit(directory):
    roots=Path(directory)
    files=[roots/f"pickcube_so3_pick_cube_chunk{s}_original8.json" for s in range(4)]
    if any(not p.is_file() for p in files):raise ValueError("missing predeclared real 32 shard")
    episodes=[]
    for shard,p in enumerate(files):
        r=json.loads(p.read_text())
        if (r.get("schema")!="pickcube_external_task_reachable_so3_5arm_v1"
            or r["task"]!="PickCube-v1"
            or r["original_external_frozen_checkpoint_sha256"]!=SOURCE_SHAS["pick_cube"]
            or tuple(r["all_five_actual_control_arms"])!=ARMS):
            raise ValueError("training model/task/comparator provenance changed")
        rows=r["episodes"]
        if len(rows)!=8 or [x["seed"] for x in rows]!=list(range(START+8*shard,START+8*shard+8)):
            raise ValueError("missing / repeated new state")
        for row in rows:
            if set(row["success_once"])!=set(ARMS):raise ValueError("wrong comparison")
        episodes+=rows
    if len(episodes)!=32 or len({r["seed"] for r in episodes})!=32:raise ValueError("bad denominator")
    out=dict(task="PickCube-v1",first_original_reset=START,clusters=32,
             genuine_physx_worlds=160,policy_frozen=True,not_new_robot_morphology=True,
             outside_lab_reproduction=False,has_test_outcome_hyperparameter_refit=False,
             arms={},pairwise={},precommitted_gate={})
    for arm in ARMS:
        reads=[r["privileged_target_readback_decision_count"][arm] for r in episodes]
        out["arms"][arm]={
            "success_count":sum(bool(r["success_once"][arm]) for r in episodes),
            "private_readbacks":("unbounded_privileged_oracle" if arm==ARMS[1] else sum(reads)),
            "two_source_native_faults_reached":(sum(len(r.get("faults",{}).get(arm,[]))==2
                for r in episodes) if arm!=ARMS[0] else None),
            "robust_authorized_actions":sum(r.get("robust_common_action_authorizations",{}).get(arm,0)
                for r in episodes),
        }
        if arm==ARMS[1] and any(x!=-1 for x in reads):
            raise ValueError("privileged oracle disguised as cost-free")
    newer=ARMS[-1]
    for arm in (ARMS[1],ARMS[2],ARMS[3]):
        a=sum(r["success_once"][newer] and not r["success_once"][arm] for r in episodes)
        b=sum(r["success_once"][arm] and not r["success_once"][newer] for r in episodes)
        out["pairwise"][arm]=dict(new_only=a,baseline_only=b,exact_exploratory_p=sign_p(a,b))
    a=out["arms"]
    out["precommitted_gate"]={
        "all_32_genuine_fault_exposures":all(a[arm]["two_source_native_faults_reached"]==32 for arm in ARMS[1:]),
        "not_below_correct_fixed_readback":a[newer]["success_count"]>=a[ARMS[3]]["success_count"],
        "at_least_four_reads_saved_vs_fixed":a[newer]["private_readbacks"]+4<=a[ARMS[3]]["private_readbacks"],
        "not_below_finite_midpoint_policy":a[newer]["success_count"]>=a[ARMS[2]]["success_count"],
        "at_least_two_reads_saved_vs_old":a[newer]["private_readbacks"]+2<=a[ARMS[2]]["private_readbacks"],
    }
    out["precommitted_gate"]["all_pass"]=all(out["precommitted_gate"].values())
    return out

if __name__=="__main__":
    import sys
    res=audit(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps(res,sort_keys=True))
