"""Independent full-denominator, two-world prospective frozen PPO PhysX source audit.

This audits all 4 source artifacts, never selects seeds by outcome and preserves
all original negatives. Readback counts refer to decisions, NOT endpoint audit.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

SPECS={
    "pull_cube":("PullCube-v1",list(range(142001,142009)),
        "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube":("StackCube-v1",list(range(152001,152009)),
        "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"),
}
TRUTHS=("applied_no_ack","neutral_arm_delta_no_ack")
ARMS=(
    "source_no_fault","fault_oracle_private_target",
    "fault_optimistic_unverified_ack","fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query",
)
PROTO="research/ACK_BOUNDED_QUERY_TWO_TRUTH_32_PRECOMMIT_V1.json"
EXPECTED_REV="6bdeb28810330ab5425ccd629bb561c58a56ff85"
SELECT="fault_robust_then_single_privileged_query"
MANDATORY="fault_always_single_privileged_query"
NOQUERY="fault_robust_two_history_without_query"
OPT="fault_optimistic_unverified_ack"


def need(ok,msg):
    if not ok: raise ValueError(msg)


def tally(rows):
    return {a:sum(int(r["success_once"][a]) for r in rows) for a in ARMS}


def compare(rows,first,second):
    return {
      "first_only":sum(r["success_once"][first] and not r["success_once"][second] for r in rows),
      "second_only":sum(r["success_once"][second] and not r["success_once"][first] for r in rows),
      "both":sum(r["success_once"][first] and r["success_once"][second] for r in rows),
      "neither":sum(not r["success_once"][first] and not r["success_once"][second] for r in rows)
    }


def run(dir):
    files=list(dir.rglob("two_truth_bounded_query_*_original8.json"))
    need(len(files)==4,"Missing or extra physical cohort/source result files")
    all_rows=[]
    groups={}
    for task,(task_id,seeds,checkpoint) in SPECS.items():
      for truth in TRUTHS:
        file=next((f for f in files if f.name==f"two_truth_bounded_query_{task}_{truth}_original8.json"),None)
        need(file is not None,f"Missing task/fault: {task}/{truth}")
        data=json.loads(file.read_text(encoding="utf-8"))
        need(data.get("schema")=="unknown_ack_bounded_or_query_two_truth_32_physx_v1","Schema mismatch")
        need(data.get("task")==task_id and data.get("fault_truth")==truth,"Condition mislabelled")
        need(data.get("original_seed_population")==seeds,"Source seeds changed")
        need(data.get("original_external_frozen_checkpoint_sha256")==checkpoint,"PPO weights changed")
        need(data.get("frozen_model_retrained") is False and data.get("real_physx_simulator") is True,"Not a frozen policy real simulator result")
        need(data.get("frozen_protocol")==PROTO,"Unregistered protocol")
        need(data.get("fault_is_command_delivery_truth_not_network_loss") is True,"Fault semantic mismatch")
        need(data.get("all_seven_actual_control_arms")==list(ARMS),"Baseline missing")
        rows=data.get("episodes",[])
        need(len(rows)==8 and [r.get("seed") for r in rows]==seeds,"Incomplete, duplicate or reordered episodes")
        totals=tally(rows)
        need(data.get("success_counts")==totals,"Incorrect aggregate task success")
        queries={}
        authorized=0
        for row in rows:
          need(row.get("fault_truth")==truth and row.get("task")==task_id,"Episode condition mismatch")
          need(set(row.get("success_once",{}))==set(ARMS) and all(type(v) is bool for v in row["success_once"].values()),"Missing or invalid native success flag")
          need(set(row.get("initial_obs_diff",{}))==set(ARMS[1:]),"Initial world pairing missing")
          need(all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=5e-4 for v in row["initial_obs_diff"].values()),"Initial world pairing violated")
          for arm in ARMS[1:]:
            event=row.get("faults",{}).get(arm)
            need(isinstance(event,dict) and event.get("step")==2,"Physical actual intervention absent")
            need(event.get("controller_execution_ack_seen_by_adapter")=="unknown","ACK not masked")
            native="intended_native_arm_delivered" if truth=="applied_no_ack" else "all_zero_hold"
            need(event.get("actual_native_arm_command")==native,"Wrong actual dispatch")
          q=row.get("privileged_target_readback_decision_count",{})
          need(set(q)==set(ARMS),"Decision read disclosure incomplete")
          need(q["fault_oracle_private_target"]==-1,"Unbounded oracle not declared")
          need(q[MANDATORY]==1 and q[SELECT] in (0,1),"One-read information budget violation")
          for arm in ("source_no_fault",OPT,"fault_strict_common_exact",NOQUERY):
            need(q[arm]==0,"Claimed zero-readback arm accessed private goal")
          need(row.get("refusals",{}).get("fault_strict_common_exact") is not None,"Exact guard incorrectly proceeded")
          checks=row.get("robust_native_target_bound_checks",{})
          for key,cases in checks.items():
            need(key in (SELECT,NOQUERY),"Unknown target-state authorization source")
            for v in cases:
              need(v.get("only_audit_after_physical_dispatch") is True,"Certificate leak through online controller private state")
              need(all(type(v.get(field)) in (int,float) and math.isfinite(v[field]) and v[field]>=0 for field in (
                  "position_error_m","rot_error_rad","worst_case_position_limit_m","worst_case_rot_limit_rad")),"Nonfinite geometric certificate")
              need(v["position_error_m"]<=v["worst_case_position_limit_m"]+1e-4 and
                   v["rot_error_rad"]<=v["worst_case_rot_limit_rad"]+1e-4,"Actual controller invalidated prospective target certificate")
          authorized+=row.get("robust_common_action_authorizations",{}).get(NOQUERY,0)
          for projections in row.get("native_projection_NOT_EXACT",{}).values():
            need(all(v.get("exactness")=="NOT_EXACT" for v in projections),"Clipped action misrepresented as exact")
          queries[row["seed"]]={"selective":q[SELECT],"mandatory":q[MANDATORY]}
        need(data.get("selective_readback_counts")==[queries[s]["selective"] for s in seeds],"Changed per-seed query declaration")
        need(data.get("robust_no_query_authorization_count")==authorized,"Robust authorization count drift")
        need(all(data.get("fault_reached_counts",{}).get(a)==8 for a in ARMS[1:]),"Fault failed to reach all eight episodes")
        groups[f"{task}/{truth}"]={
          "n":8,"frozen_seed_population":seeds,
          "success_counts":totals,
          "reads_selective":sum(q["selective"] for q in queries.values()),
          "reads_mandatory":sum(q["mandatory"] for q in queries.values()),
          "robust_no_query_authorized_steps":authorized,
          "selective_vs_always":compare(rows,SELECT,MANDATORY),
          "selective_vs_no_query":compare(rows,SELECT,NOQUERY),
          "selective_vs_optimistic":compare(rows,SELECT,OPT),
          "all_original_rows":rows
        }
        all_rows.extend(rows)
    out={
      "schema":"bounded_or_query_two_truth_32_complete_audit_v1",
      "protocol":PROTO,"n_original_task_truth_conditions":32,
      "n_unique_reset_seeds":16,"n_task_families":2,
      "published_external_model_revision":EXPECTED_REV,
      "total_reads_selective":sum(v["reads_selective"] for v in groups.values()),
      "total_reads_mandatory":sum(v["reads_mandatory"] for v in groups.values()),
      "total_success":tally(all_rows),
      "overall_selective_vs_always":compare(all_rows,SELECT,MANDATORY),
      "overall_selective_vs_no_query":compare(all_rows,SELECT,NOQUERY),
      "overall_selective_vs_optimistic":compare(all_rows,SELECT,OPT),
      "groups":groups,
      "limitations":"Owner-run PhysX conditional target-setpoint error, not hardware safety, real dropped network commands, no third-party replication, no new theorem",
    }
    return out


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    result=run(args.input_dir)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("TWO_TRUTH_BOUNDED_QUERY_COMPLETE",json.dumps({
      "n":32,"success":result["total_success"],
      "selective_reads":result["total_reads_selective"],
      "mandatory_reads":result["total_reads_mandatory"],
      "selective_vs_always":result["overall_selective_vs_always"],
      "by_world":{k:{"success":v["success_counts"],"selective_reads":v["reads_selective"],
        "mandatory_reads":v["reads_mandatory"]} for k,v in result["groups"].items()}
    },sort_keys=True))
