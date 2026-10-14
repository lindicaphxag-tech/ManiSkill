"""Exact full-denominator posthoc readback-switching frontier.

Only the original two *physically executed* policy arms (fixed t4 target read
vs finite-history certify-or-query) are allowed. This oracle conditions on
FUTURE TASK SUCCESS for each original reset and is NOT a deployable policy,
nor a bound on newly synthesized actions or all possible controllers.
"""
import argparse, hashlib, json
from itertools import product
from pathlib import Path
from research.audit_reachable_first_run_crash_logs import LOG_SHA

OLD="fault_robust_then_single_privileged_query"
FIXED="fault_fixed_readback_canonical"
SOURCE_TASK={"pull_cube":("PullCube-v1",2026220001),
             "stack_cube":("StackCube-v1",2026230001),
             "pick_cube":("PickCube-v1",2026440001)}

def frontier(rows):
    """DP: D_i(b)=max_{arm}[D_{i-1}(b-reads_arm)+success_arm]."""
    states={0:0}
    for r in rows:
        next_states={}
        for b,success in states.items():
            for name in (FIXED,OLD):
                if type(r["success_once"][name]) is not bool:
                    raise ValueError("Official task outcome must be Boolean")
                reads=r["privileged_target_readback_decision_count"][name]
                if type(reads) is not int or reads<0:raise ValueError("Invalid real read count")
                key=b+reads
                next_states[key]=max(next_states.get(key,-1),success+int(r["success_once"][name]))
        states=next_states
    return dict(sorted(states.items()))

def brute_force(rows):
    if len(rows)>10:raise ValueError("Only test small N exhaustively")
    best={}
    for pattern in product((FIXED,OLD),repeat=len(rows)):
        reads=sum(r["privileged_target_readback_decision_count"][a] for r,a in zip(rows,pattern))
        success=sum(int(r["success_once"][a]) for r,a in zip(rows,pattern))
        best[reads]=max(best.get(reads,-1),success)
    return dict(sorted(best.items()))

def receipt_rows(root):
    """Read original owner-operated Actions run artifacts; never sim/replay."""
    root=Path(root)
    out={}
    sha={}
    for slug,(task,first) in SOURCE_TASK.items():
        values=[]
        for shard in range(4):
            if slug=="pick_cube":
                filename=f"pickcube_so3_pick_cube_chunk{shard}_original8.json"
                p=root/"pick_cube"/filename
                raw=p.read_bytes()
                d=json.loads(raw)
                if d.get("schema")!="pickcube_external_task_reachable_so3_5arm_v1":
                    raise ValueError("Wrong prospective PickCube source cohort")
                rec=d["episodes"]
            else:
                p=root/slug/f"reachable_{slug}_{shard}.log"
                raw=p.read_bytes()
                actual=hashlib.sha256(raw).hexdigest()
                if actual!=LOG_SHA[slug][shard]:
                    raise ValueError("Development first-run source SHA changed")
                blob=raw.decode("utf-8")
                marker="REACHABLE_SO3_ORIGINAL_EPISODE "
                rec=[json.loads(line.split(marker,1)[1])
                     for line in blob.splitlines() if marker in line]
                if blob.count("NameError: name 'PROTO' is not defined")!=1:
                    raise ValueError("Original run failure provenance changed")
            if len(rec)!=8 or [q["seed"] for q in rec]!=list(range(first+8*shard,first+8*shard+8)):
                raise ValueError("Original frozen reset denominator changed")
            if any(q["task"]!=task for q in rec):
                raise ValueError("Task was replaced")
            sha[str(p.name)]=hashlib.sha256(raw).hexdigest()
            values+=rec
        if len(values)!=32 or len({r["seed"] for r in values})!=32:
            raise ValueError("Not 32 unique reset clusters")
        out[task]=values
    return out,sha

def summarize(rows):
    if len(rows)!=32:raise ValueError("Expected 32 matched resets per task")
    optimal=frontier(rows)
    fixed_success=sum(r["success_once"][FIXED] for r in rows)
    fixed_reads=sum(r["privileged_target_readback_decision_count"][FIXED] for r in rows)
    old_success=sum(r["success_once"][OLD] for r in rows)
    old_reads=sum(r["privileged_target_readback_decision_count"][OLD] for r in rows)
    choices=[budget for budget,s in optimal.items() if s>=fixed_success]
    pointwise=sum(r["privileged_target_readback_decision_count"][FIXED]-
                r["privileged_target_readback_decision_count"][OLD]
                  for r in rows if (r["success_once"][OLD]>=r["success_once"][FIXED]
                  and r["privileged_target_readback_decision_count"][OLD]<
                      r["privileged_target_readback_decision_count"][FIXED]))
    return dict(n_reset_clusters=len(rows),fixed_success=fixed_success,
       fixed_readbacks=fixed_reads,old_success=old_success,
       old_readbacks=old_reads,
       posthoc_best_reads_for_at_least_fixed_success=min(choices),
       posthoc_max_savings_without_aggregate_success_loss=fixed_reads-min(choices),
       posthoc_max_savings_without_ANY_state_level_success_loss=pointwise,
       oracle_max_success_with_at_most_fixed_reads_minus_four=max(
           (s for b,s in optimal.items() if b<=fixed_reads-4),default=None),
       exact_read_budget_to_success_frontier={str(k):v for k,v in optimal.items()},
       counterfactual_uses_observed_future_success_not_available_to_robot=True,
       only_two_actually_executed_source_controller_arms=True,
       not_bound_for_new_native_actions=True)

def main(root,out):
    taskrows,sha=receipt_rows(root)
    analysis={task:summarize(rows) for task,rows in taskrows.items()}
    if ({k:z["posthoc_max_savings_without_aggregate_success_loss"]
         for k,z in analysis.items()}
        !={"PullCube-v1":11,"StackCube-v1":5,"PickCube-v1":2}):
        raise RuntimeError("Original negative hard-bound audit did not replicate")
    answer=dict(
      original_development_run="38546430880 (failed ONLY in after-episode summary)",
      original_independent_development_log_audit="38547796024 (success)",
      original_new_task_run="38550286593 (all shards + audit success)",
      source_artifact_sha256=sha,exact_unique_reset_clusters=96,
      actual_source_episode_controller_arms=192,
      no_new_physx_rollouts=True,
      has_posthoc_outcome_information_leakage_to_oracle=True,
      outside_research_lab_replication=False,
      general_robot_action_impossibility_theorem=False,
      by_task=analysis)
    Path(out).write_text(json.dumps(answer,sort_keys=True,indent=2)+"\n")
    print(json.dumps({t:{k:z[k] for k in
      ("fixed_success","old_success",
       "posthoc_max_savings_without_aggregate_success_loss",
       "oracle_max_success_with_at_most_fixed_reads_minus_four")}
       for t,z in analysis.items()},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("original_artifact_directory",type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    main(a.original_artifact_directory,a.out)
