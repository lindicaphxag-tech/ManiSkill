"""Independent full-denominator audit of consecutively held unknown-ACK controller targets.

The original native PhysX simulation is separately executed. This module has
no torch/ManiSkill dependencies. It certifies *record/provenance consistency*,
NOT physical or trajectory safety and not independent lab replication.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

SCHEMA="compound_two_unknown_ack_actuation_authority_fresh16_v2"
PROTO="research/TWO_ACK_ACTUATION_AUTHORITY_FRESH16_PRECOMMIT_V2.json"
TASKS={
 "pull_cube":("PullCube-v1",430001,
 "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
 "stack_cube":("StackCube-v1",440001,
 "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")
}
NAMES=(
 "source_no_fault","fault_oracle_private_target",
 "fault_optimistic_unverified_ack","fault_strict_common_exact",
 "fault_robust_two_history_without_query",
 "fault_robust_then_single_privileged_query",
 "fault_always_single_privileged_query"
)
BELIEF=NAMES[3:6]
SELECTIVE="fault_robust_then_single_privileged_query"
MANDATORY="fault_always_single_privileged_query"


def need(condition,msg):
    if not condition:raise ValueError(msg)


def finite(x):
    return type(x) in (float,int) and math.isfinite(x)


def check_one(d,task):
    env,first,hash_weight=TASKS[task]
    need(d.get("schema")==SCHEMA and d.get("frozen_protocol")==PROTO,
         "Wrong pre-outcome source protocol/schema")
    need(d.get("task")==env and d.get("original_seed_population")==list(range(first,first+8)),
         "Task or preregistered reset denominator changed")
    need(d.get("original_external_frozen_checkpoint_sha256")==hash_weight and
         d.get("frozen_model_retrained") is False and
         d.get("real_physx_simulator") is True,
         "Changed third-party PPO checkpoint or imaginary simulation")
    need(d.get("two_consecutive_unknown_ack_target_hold_steps")==[2,3] and
         d.get("native_hold_step2_step3_target_reads_audit_only") is True and
         d.get("fault_is_native_target_hold_not_network_loss") is True and
         d.get("privileged_readback_counts_are_decision_only_not_audit_reads") is True,
         "Physical fault/readback disclosure removed")
    need(d.get("all_seven_actual_control_arms")==list(NAMES),
         "Missing or extra controller arms")
    rows=d.get("episodes")
    need(isinstance(rows,list) and len(rows)==8,
         "All eight original source seeds mandatory, including failures")
    successes={k:0 for k in NAMES}
    exposures={k:0 for k in NAMES[1:]}
    events={k:0 for k in NAMES[1:]}
    audit_reads_total=0
    absence=[]
    max_k=1
    private_reads={k:0 for k in (SELECTIVE,MANDATORY)}
    for idx,row in enumerate(rows):
        seed=first+idx
        need(row.get("task")==env and row.get("seed")==seed,
             "Original seed missing or out of register")
        flags=row.get("success_once")
        need(isinstance(flags,dict) and set(flags)==set(NAMES) and
             all(type(t) is bool for t in flags.values()),
             "Official real PhysX success flags incomplete")
        read=row.get("privileged_target_readback_decision_count")
        need(isinstance(read,dict) and set(read)==set(NAMES) and
             read["fault_oracle_private_target"]==-1 and
             all(read[k]==0 for k in ("source_no_fault","fault_optimistic_unverified_ack",
                  "fault_strict_common_exact","fault_robust_two_history_without_query")) and
             read[SELECTIVE] in (0,1) and read[MANDATORY] in (0,1),
             "Privileged decision read ledger incorrect")
        for k in successes:successes[k]+=int(flags[k])
        for k in private_reads:private_reads[k]+=read[k]
        fdict=row.get("faults",{})
        for arm in NAMES[1:]:
            fault=fdict.get(arm,[])
            need(isinstance(fault,list) and len(fault)<=2 and
                 [x.get("step") for x in fault] in ([],[2],[2,3]),
                 "Missing or non-consecutive two unknown ACK interventions")
            held=row.get("audit_only_native_hold_checks",{}).get(arm,[])
            need(isinstance(held,list) and len(held)==len(fault),
                 "No matching true native held-target audit")
            for i,e in enumerate(fault):
                need(e.get("controller_execution_ack_seen_by_adapter")=="unknown" and
                     e.get("actual_native_arm_command")=="all_zero_hold" and
                     e.get("actual_native_target_hold_verified") is True,
                     "Wrong actual fault or unverifiable physical target hold")
                v=held[i]
                need(e["step"]==v.get("step") and
                     v.get("target_reads_not_exposed_to_controller_decisions") is True and
                     v.get("private_target_getter_audit_only_count")==2,
                     "Fake physical hold or leaked decision state")
                for key in ("held_position_error_inf_m","held_rotation_error_rad"):
                    val=v.get(key)
                    need(finite(val) and 0<=val<=1e-4,
                         "Original native controller target did not hold")
                for key in ("actual_native_held_position_error_m",
                            "actual_native_held_rotation_error_rad"):
                    val=e.get(key)
                    need(finite(val) and val<=1e-4,
                         "Fault's true target state unverified")
                audit_reads_total+=2
            exposures[arm]+=int(len(fault)==2)
            events[arm]+=len(fault)
            if len(fault)!=2:
                absence.append({"task":task,"seed":seed,"arm":arm,
                                "events_reached":len(fault),
                                "counted_as_full_denominator_failure":True})
            intent=row.get("certified_action_masked_by_injected_fault",{}).get(arm,[])
            need(isinstance(intent,list),"Missing intentional suppression record")
            for h in intent:
                need(h.get("step") in [x["step"] for x in fault] and
                     h.get("claimed_physical_setpoint_certificate") is False and
                     h.get("native_action_did_not_execute") is True and
                     h.get("postdispatch_certificate_check_not_applicable") is True,
                     "Claiming impossible certificate on deliberately undelivered intent")
            audit_bound=row.get("robust_native_target_bound_checks",{}).get(arm,[])
            need(isinstance(audit_bound,list),"Malformed actual-setpoint audit")
            for q in audit_bound:
                need(q.get("step") not in [x["step"] for x in fault] and
                     q.get("only_audit_after_physical_dispatch") is True,
                     "Bounded authorization falsely audited as executed under a physical drop")
                pos=q.get("position_error_m")
                rot=q.get("rot_error_rad")
                maxpos=q.get("worst_case_position_limit_m")
                maxrot=q.get("worst_case_rot_limit_rad")
                need(all(finite(x) for x in (pos,rot,maxpos,maxrot)) and
                     min(pos,rot,maxpos,maxrot)>=0 and
                     maxpos<=.050001 and maxrot<=.050001 and
                     pos<=maxpos+1e-4 and rot<=maxrot+1e-4,
                     "Delivered native controller violated claimed setpoint certificate")
        widths=row.get("max_belief_width")
        need(isinstance(widths,dict) and set(widths)==set(BELIEF) and
             all(type(k) is int and 1<=k<=16 for k in widths.values()),
             "Improper 1-16 history confidence or missing logs")
        max_k=max(max_k,max(widths.values()))
    need(successes==d.get("success_counts"),
         "Reported task aggregate disagrees with original per-seed flags")
    need(exposures==d.get("fault_reached_counts"),
         "Second true physical hold was not disclosed")
    need(events==d.get("actual_native_hold_event_counts"),
         "Missing real individual two-ACK intervention count")
    need([r["privileged_target_readback_decision_count"][SELECTIVE] for r in rows]
         ==d.get("selective_readback_counts"),
         "Privileged decision-read counts changed")
    need(d.get("robust_no_query_authorization_count")==sum(
             r["robust_common_action_authorizations"].get(
                 "fault_robust_two_history_without_query",0) for r in rows),
         "Untrusted robust command count")
    return dict(task=task,n_original=8,success=successes,
                two_physical_holds_reached=exposures,
                actual_native_hold_fault_events=events,
                audit_only_native_target_getters=audit_reads_total,
                max_possible_hidden_targets=max_k,
                selective_true_target_reads=private_reads[SELECTIVE],
                mandatory_true_target_reads=private_reads[MANDATORY],
                unexposed_interventions=absence)


def audit(directory):
    expected={f"compound_multi_ack_{task}_original8.json" for task in TASKS}
    found={p.name for p in directory.glob("compound_multi_ack_*_original8.json")}
    need(found==expected, "Missing or extra source task experiment JSON")
    x={task:check_one(json.loads(
        (directory/f"compound_multi_ack_{task}_original8.json").read_text()),task)
        for task in TASKS}
    return {
        "schema":"strict_16_source_genuine_actuation_authority_double_ack_audit_v2",
        "source_original_reset_states":16,
        "two_ack_precommit":"research/TWO_ACK_ACTUATION_AUTHORITY_FRESH16_PRECOMMIT_V2.json",
        "original_owner_executed_physx_not_external_replication":True,
        "all_seven_arms_have_two_physical_faults_per_seed":all(
            x[t]["two_physical_holds_reached"][arm]==8
            for t in TASKS for arm in NAMES[1:]),
        "all_seed_denominator_reached":sum(t["n_original"] for t in x.values())==16,
        "success":{arm:sum(x[t]["success"][arm] for t in TASKS) for arm in NAMES},
        "reads_selective":sum(x[t]["selective_true_target_reads"] for t in TASKS),
        "reads_mandatory":sum(x[t]["mandatory_true_target_reads"] for t in TASKS),
        "max_belief_hypotheses":max(x[t]["max_possible_hidden_targets"] for t in TASKS),
        "unexposed_conditions":[e for t in TASKS for e in x[t]["unexposed_interventions"]],
        "groups":x,
        "claim_scope":"Native accumulated-target controller command-state assurance ONLY, not contact/hardware safety"
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=audit(a.input_dir)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("ORIGINAL_DOUBLE_UNKNOWN_ACK_ACTUATION_AUDIT",
          json.dumps({"n":16,"success":report["success"],
            "selective_reads":report["reads_selective"],
            "mandatory_reads":report["reads_mandatory"],
            "all_faults_reached":report["all_seven_arms_have_two_physical_faults_per_seed"],
            "max_possible_targets":report["max_belief_hypotheses"],
            "fault_unreached":report["unexposed_conditions"]},sort_keys=True))


if __name__=="__main__": main()
