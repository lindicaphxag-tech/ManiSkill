"""Paired ZERO/X hindsight-portfolio bound from externally SHA-audited PhysX.
Descriptive ONLY: impossible online oracle; not a prospective policy gain.
"""
import argparse,json
from pathlib import Path
from collections import defaultdict

TASKS={"pull_cube":4100001,"stack_cube":4200001}
ARMS=("fault_public_t3_fourhistory_or_t4_query","fault_same_public_posterior_or_query","fault_always_single_privileged_query")

def audit_ceiling(source):
    if not (source.get("status")=="REAL_COMPLETED_NEW_FREEZE_PPO_TASK_SOURCE_AUDITED"
        and source.get("physically_executed_original_controller_worlds")==2560
        and source.get("new_independent_reset_clusters")==32
        and source.get("matched_original_PPO_task_cells")==256
        and len(source.get("original_shard_file_sha256",{}))==72):
        raise ValueError("Wrong/missing SHA-reviewed original source")
    rows=source.get("all_full_actual_PPO_task_outcomes",[])
    if len(rows)!=384:raise ValueError("Missing original A/B/C source denominator")
    items={}
    for r in rows:
        task,arm,reset,truth=(r.get(k) for k in ("task","arm","seed","truth"))
        if (task not in TASKS or arm not in ARMS or type(reset)!=int
            or reset not in range(TASKS[task],TASKS[task]+16)
            or type(truth)!=int or truth not in range(4)):
            raise ValueError("Unexpected task/arm/reset/physical ACK truth")
        key=(task,arm,reset,truth)
        if key in items:raise ValueError("Duplicate physical cell")
        if any(type(r.get(k))!=bool for k in ("zero_success","x_success","zero_wrong","x_wrong")):
            raise ValueError("Invalid observed success/authority")
        if any(type(r.get(k))!=int or r[k] not in (0,1)
               for k in ("zero_privileged_reads","x_privileged_reads")):
            raise ValueError("Invalid getter costs")
        items[key]=r
    expected={(task,arm,reset,truth) for task,first in TASKS.items()
              for arm in ARMS for reset in range(first,first+16) for truth in range(4)}
    if set(items)!=expected:raise ValueError("Incomplete factorial")
    by_task={};pooled={}
    for arm in ARMS:
        pooled[arm]=defaultdict(int)
        for task,first in TASKS.items():
            rows=[items[task,arm,reset,truth] for reset in range(first,first+16) for truth in range(4)]
            zero=sum(r["zero_success"] for r in rows)
            x=sum(r["x_success"] for r in rows)
            both=sum(r["zero_success"] and r["x_success"] for r in rows)
            only_z=sum(r["zero_success"] and not r["x_success"] for r in rows)
            only_x=sum(r["x_success"] and not r["zero_success"] for r in rows)
            neither=sum(not r["zero_success"] and not r["x_success"] for r in rows)
            if not (both+only_z+only_x+neither==64 and zero==both+only_z and x==both+only_x):
                raise ValueError("Pair partition mismatch")
            clean_zero=sum(r["zero_success"] and not r["zero_wrong"] for r in rows)
            clean_oracle=sum((r["zero_success"] and not r["zero_wrong"])
                             or (r["x_success"] and not r["x_wrong"]) for r in rows)
            d=dict(independent_resets=16,correlated_ack_cells=64,zero_success=zero,
                   x_success=x,both_success=both,zero_only=only_z,x_only=only_x,
                   both_fail=neither,hindsight_oracle_success=64-neither,
                   hindsight_oracle_extra_success=only_x,clean_zero_success=clean_zero,
                   clean_hindsight_oracle_success=clean_oracle,
                   clean_hindsight_oracle_extra_success=clean_oracle-clean_zero,
                   wrong_authority_zero=sum(r["zero_wrong"] for r in rows),
                   wrong_authority_x=sum(r["x_wrong"] for r in rows),
                   independent_resets_containing_both_failure=sum(
                       any(not items[task,arm,reset,t]["zero_success"] and
                           not items[task,arm,reset,t]["x_success"] for t in range(4))
                       for reset in range(first,first+16)))
            by_task[f"{task}:{arm}"]=d
            for k,v in d.items():pooled[arm][k]+=v
        pooled[arm]=dict(pooled[arm])
    return dict(status="RETROSPECTIVE_ZERO_X_PORTFOLIO_BOUND_ONLY",
                old_physx_run=38014679801,independent_source_review=38015149933,
                historical_original_independent_resets=32,
                hindsight_oracle_not_deployable=True,
                not_a_population_upper_bound=True,
                only_two_fixed_native_actions=True,
                no_new_physx_task_outcomes=True,
                by_task=by_task,pooled=pooled)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source_audit");p.add_argument("output")
    a=p.parse_args()
    res=audit_ceiling(json.loads(Path(a.source_audit).read_text()))
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print("OBSERVED_ACTION_PORTFOLIO_CEILING_NOT_A_LEARNED_POLICY",
          json.dumps(res["pooled"],sort_keys=True))

if __name__=="__main__":main()
