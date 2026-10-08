"""Fail-closed audit of 32 source-frozen seven-arm genuine PhysX ACK-fault rows.

No cherry-picked seeds; original source policy competence and all faults
are reported separately, including incomplete / refused target episodes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ARMS=(
    "source_no_fault",
    "fault_oracle_private_target",
    "fault_optimistic_unverified_ack",
    "fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query"
)
SPECS={
    "pull_cube":("PullCube-v1",list(range(142001,142017)),
                 "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube":("StackCube-v1",list(range(152001,152017)),
                  "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")
}
PROTOCOL="research/UNKNOWN_ACK_BOUNDED_QUERY_CONFIRMATORY_32_FROZEN_V1.json"
INTERVENED=ARMS[1:]


def inspect(originals: Path):
    found=sorted(originals.rglob("unknown_ack_bounded_query_confirm32_*_original16.json"))
    if len(found)!=2:
        raise ValueError(f"Expected exactly two original, full 16-seed task files; got {len(found)}")
    task_results={}
    for task,(env,seeds,sha) in SPECS.items():
        file=next((p for p in found if p.name==f"unknown_ack_bounded_query_confirm32_{task}_original16.json"),None)
        if file is None:
            raise ValueError(f"Missing original {task}")
        q=json.loads(file.read_text(encoding="utf-8"))
        if (q.get("schema")!="unknown_ack_bounded_query_confirmatory_32_v1"
            or q.get("task")!=env
            or q.get("original_seed_population")!=seeds
            or q.get("frozen_protocol")!=PROTOCOL
            or q.get("original_external_frozen_checkpoint_sha256")!=sha
            or q.get("frozen_model_retrained") is not False
            or q.get("real_physx_simulator") is not True
            or q.get("fault_is_native_target_hold_not_network_loss") is not True):
            raise ValueError("Protocol, model or physical-fault provenance altered")
        rows=q.get("episodes")
        if not isinstance(rows,list) or len(rows)!=16:
            raise ValueError("Incomplete original PhysX cohort")
        if [x.get("seed") for x in rows]!=seeds or len(set(seeds))!=16:
            raise ValueError("Missing, reordered or duplicated original seed")
        if q.get("all_seven_actual_control_arms")!=list(ARMS):
            raise ValueError("Changed comparator/denominator")
        calc={arm:0 for arm in ARMS}
        faulted={arm:0 for arm in INTERVENED}
        query_counts={}
        robust_step_count=0
        for row in rows:
            if row.get("task")!=env:
                raise ValueError("Task label drift")
            obs=row.get("initial_obs_diff",{})
            if set(obs)!=set(INTERVENED) or any(
                not isinstance(obs.get(a),(int,float)) or
                not 0<=obs[a]<=0.0005 for a in INTERVENED
            ):
                raise ValueError("Nonidentical source observation at initial physical state")
            succ=row.get("success_once")
            if set(succ or {})!=set(ARMS) or any(type(v) is not bool for v in succ.values()):
                raise ValueError("Missing or invalid official success indicator")
            for a in ARMS:
                calc[a]+=int(succ[a])
                steps=row.get("steps",{}).get(a)
                if a not in row.get("refusals",{}) and (
                    not isinstance(steps,int) or not 1<=steps<=50
                ):
                    raise ValueError(f"Missing original physical rollout {a}")
            for a in INTERVENED:
                injected=row.get("faults",{}).get(a)
                if injected is not None:
                    if (injected.get("step")!=2 or
                        injected.get("actual_native_arm_command")!="all_zero_hold"):
                        raise ValueError("Mismatch in physical fault injection")
                    faulted[a]+=1
            decision_reads=row.get("privileged_target_readback_decision_count",{})
            for a in ARMS:
                count=decision_reads.get(a)
                if type(count) is not int:
                    raise ValueError("Missing target readback count")
                if a=="fault_oracle_private_target":
                    if count!=-1:
                        raise ValueError("Unrestricted private target reads MUST be labelled -1")
                    continue
                if count<0:
                    raise ValueError("Missing authoritatively declared target readback count")
                if a in ("fault_robust_then_single_privileged_query",
                         "fault_always_single_privileged_query") and count>1:
                    raise ValueError("Exceeded frozen per-episode one-query budget")
                if a in ("fault_optimistic_unverified_ack",
                         "fault_strict_common_exact",
                         "fault_robust_two_history_without_query",
                         "source_no_fault") and count!=0:
                    raise ValueError("Claimed no-query arm used privileged readback")
            robust_step_count+=row.get("robust_common_action_authorizations",{}).get(
                "fault_robust_two_history_without_query",0)
            for arm,steps in row.get("robust_native_target_bound_checks",{}).items():
                if arm not in ("fault_robust_two_history_without_query",
                               "fault_robust_then_single_privileged_query"):
                    raise ValueError("Unauthorized common bounded controller audit")
                for v in steps:
                    if (v["position_error_m"]>v["worst_case_position_limit_m"]+0.0001
                        or v["rot_error_rad"]>v["worst_case_rot_limit_rad"]+0.0001
                        or v["only_audit_after_physical_dispatch"] is not True):
                        raise ValueError("Actual original controller contradicted robust claimed bound")
            for arm,projections in row.get("native_projection_NOT_EXACT",{}).items():
                if arm not in INTERVENED or any(
                    x.get("exactness")!="NOT_EXACT" for x in projections):
                    raise ValueError("Approximate physical command falsely exact")
            seed=row["seed"]
            query_counts[seed]={
                "selective":decision_reads["fault_robust_then_single_privileged_query"],
                "always":decision_reads["fault_always_single_privileged_query"]
            }
        if q.get("success_counts")!=calc or q.get("fault_reached_counts")!=faulted:
            raise ValueError("Published summary changed from original complete rows")
        if q.get("selective_readback_counts")!=[
            query_counts[s]["selective"] for s in seeds]:
            raise ValueError("Selective information budget changed")
        if q.get("robust_no_query_authorization_count")!=robust_step_count:
            raise ValueError("Published robust-only step count changed")
        task_results[task]={
            "task":env,"original_seeds":seeds,"source_competent_min_10":calc[ARMS[0]]>=10,
            "task_success_by_arm":calc,"actual_fault_injections":faulted,
            "selective_privileged_readback_total":sum(x["selective"] for x in query_counts.values()),
            "mandatory_privileged_readback_total":sum(x["always"] for x in query_counts.values()),
            "no_query_robust_authorized_native_steps":robust_step_count,
            "complete_original_rows":rows
        }
    return {
        "schema":"unknown_ack_bounded_query_confirmatory_32_v1",
        "source_preregistration":PROTOCOL,
        "original_task_state_count":32,
        "n_independently_pretrained_policies":2,
        "simulator":"official ManiSkill PhysX CPU",
        "physical_fault":"single native arm target-hold, not network loss",
        "independent_external_reproduction":False,
        "robot_hardware_safety_certified":False,
        "results":task_results,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=inspect(a.input_dir)
    a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ACK_BOUNDED_QUERY_FINAL",json.dumps({
        k:{"counts":v["task_success_by_arm"],
           "source_competent":v["source_competent_min_10"],
           "queries_selective":v["selective_privileged_readback_total"],
           "queries_mandatory":v["mandatory_privileged_readback_total"],
           "bounded_steps":v["no_query_robust_authorized_native_steps"]}
        for k,v in r["results"].items()},sort_keys=True))


if __name__=="__main__":
    main()
