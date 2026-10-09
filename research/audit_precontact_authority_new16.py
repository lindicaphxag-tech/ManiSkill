"""Independent complete-source audit for prospective 16 original PhysX precontact trials.

Uses only original two 8-state JSON source files. No torch, ManiSkill, policy,
fitting, controller targets or posthoc threshold changes.
"""
import argparse
import json
import math
from pathlib import Path

BASE={"pull_cube":470001,"stack_cube":480001}
TASK_LABEL={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
NAMES=(
    "source_no_fault","fault_oracle_private_target",
    "fault_optimistic_unverified_ack","fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query",
    "fault_precontact_authority","fault_task_id_prior"
)
PRECONTACT="fault_precontact_authority"
TASK_PRIOR="fault_task_id_prior"
MANDATORY="fault_always_single_privileged_query"
ADAPTIVE="fault_robust_then_single_privileged_query"
PROTOCOL="research/PRECONTACT_AUTHORITY_NEW16_PRECOMMIT_V1.md"
SHA={
"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
"stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}


def need(ok,msg):
    if not ok:raise ValueError(msg)


def audit(folder:Path):
    filenames={p.name for p in folder.glob("precontact_new16_*_original8.json")}
    need(filenames=={f"precontact_new16_{task}_original8.json" for task in BASE},
         "Missing or extra original eight-state full denominator")
    summaries={}
    allrows=[]
    for task,first in BASE.items():
        r=json.loads((folder/f"precontact_new16_{task}_original8.json").read_text())
        need(r.get("schema")=="prospective_precontact_authority_task_prior_new16_physx_v1"
             and r.get("task")==TASK_LABEL[task] and
             r.get("original_seed_population")==list(range(first,first+8)) and
             r.get("original_external_frozen_checkpoint_sha256")==SHA[task] and
             r.get("real_physx_simulator") is True and
             r.get("frozen_model_retrained") is False and
             r.get("two_consecutive_unknown_ack_target_hold_steps")==[2,3] and
             r.get("frozen_protocol")==PROTOCOL and
             r.get("all_seven_actual_control_arms")==list(NAMES),
             "Changed source task/truth/model/controller protocol")
        episodes=r.get("episodes",[])
        need(len(episodes)==8,"Incomplete physical seed denominator")
        score={n:0 for n in NAMES}
        query={n:0 for n in NAMES if n!="fault_oracle_private_target"}
        both_faults={n:0 for n in NAMES[1:]}
        violated=[]
        pair=[]
        for i,row in enumerate(episodes):
            seed=first+i
            need(row.get("seed")==seed,"Reordered or omitted original PhysX seed")
            succ=row.get("success_once",{})
            counts=row.get("privileged_target_readback_decision_count",{})
            need(set(succ)==set(NAMES) and
                 all(type(succ[n]) is bool for n in NAMES),
                 "Missing actual official task outcomes")
            need(set(counts)==set(NAMES) and
                 counts["fault_oracle_private_target"]==-1 and
                 all(type(counts[n]) is int and counts[n] in (0,1)
                     for n in query),
                 "Unreported privileged decision target-state read")
            for name in NAMES:
                score[name]+=int(succ[name])
                if name in query:query[name]+=counts[name]
            need(all(counts[n]==0 for n in ("source_no_fault",
                "fault_optimistic_unverified_ack","fault_strict_common_exact",
                "fault_robust_two_history_without_query")),
                 "Hidden target memory used in a purported no-query baseline")
            fault=row.get("faults",{})
            for name in NAMES[1:]:
                interventions=fault.get(name,[])
                need(isinstance(interventions,list) and len(interventions)<=2 and
                     [v.get("step") for v in interventions] in ([],[2],[2,3]),
                     "Missing/invalid two sequential real native target holds")
                need(all(v.get("actual_native_arm_command")=="all_zero_hold" and
                         v.get("controller_execution_ack_seen_by_adapter")=="unknown"
                         for v in interventions),
                     "Actual simulated command delivery is not unknown ACK native hold")
                both_faults[name]+=int(len(interventions)==2)
                if len(interventions)!=2:
                    violated.append({"task":task,"seed":seed,
                                     "arm":name,"physical_faults_reached":len(interventions)})
            signals=row.get("public_precontact_signals",{}).get(PRECONTACT,[])
            need(isinstance(signals,list),"Absent public state risk evidence")
            for v in signals:
                distance=v.get("object_center_proximity_m")
                need(type(distance) in (int,float) and math.isfinite(distance) and distance>=0
                     and v.get("threshold_m")==0.10 and v.get("public_full_state_not_camera") is True
                     and v.get("no_native_private_target_read_for_observation") is True,
                     "Task proximity may be nonfinite, post-tuned or privileged")
            events=row.get("authorization_query_steps",{})
            for name in (PRECONTACT,TASK_PRIOR,MANDATORY,ADAPTIVE):
                entries=events.get(name,[])
                need(isinstance(entries,list) and len(entries)<=1 and
                     len(entries)==counts[name],"Missing, repeated or fake trusted target getter event")
                for v in entries:
                    need(v.get("uses_private_target") is True and
                         type(v.get("step")) is int and 4<=v["step"]<50,
                         "Unauthorized trusted target query before two physical faults")
                    reason=v.get("reason")
                    if name==PRECONTACT:
                        need(reason in ("OBSERVED_PRECONTACT_PROXIMITY",
                                        "GEOMETRY_CERTIFICATE_REFUSED"),
                             "Precontact query did not follow agreed evidence")
                        if reason=="OBSERVED_PRECONTACT_PROXIMITY":
                            need(any(s["step"]==v["step"] and
                                     s["object_center_proximity_m"]<=0.10
                                     for s in signals),
                                 "Fake public precontact threshold crossing")
                    elif name==TASK_PRIOR:
                        need(reason in ("STRONG_TRIVIAL_TASK_ID_PRIOR",
                                        "GEOMETRY_CERTIFICATE_REFUSED"),
                             "Task-ID baseline query omitted its declared reason")
                        if reason=="STRONG_TRIVIAL_TASK_ID_PRIOR":
                            need(task=="stack_cube" and v["step"]==4,
                                 "Task-ID prior learned a secret condition")
                    elif name==MANDATORY:
                        need(reason=="MANDATORY_FIXED_T4" and v["step"]==4,
                             "Unfaithful mandatory early read")
                    else:
                        need(reason=="GEOMETRY_CERTIFICATE_REFUSED",
                             "Original geometric control did not trigger query")
            pair.append({
                "seed":seed,
                "task":task,
                "success":{n:succ[n] for n in NAMES},
                "reads":{n:counts[n] for n in query},
                "precontact_signals":signals,
                "precontact_query_events":events.get(PRECONTACT,[]),
            })
        need(score==r.get("success_counts"),
             "Original aggregate success differs from each actual task outcome")
        summaries[task]=dict(n=8,success=score,reads=query,
                             full_double_faults_by_arm=both_faults,
                             missing_fault_exposures=violated,
                             outcomes=pair)
        allrows.extend(pair)
    return dict(schema="prospective_public_precontact_16_genuine_physx_full_original_audit",
                preregistered_original_states=16,
                retained_registered_episodes=len(allrows),
                operational_fault_reached_all=all(
                  summaries[t]["full_double_faults_by_arm"][n]==8
                  for t in BASE for n in (ADAPTIVE,PRECONTACT,TASK_PRIOR,MANDATORY)),
                all_seven_plus_two_comparator_faults_reached=all(
                  summaries[t]["full_double_faults_by_arm"][n]==8
                  for t in BASE for n in NAMES[1:]),
                all_source_originals_owner_run_no_external_approval=True,
                task_groups=summaries,
                total_success={n:sum(summaries[t]["success"][n] for t in BASE)
                               for n in NAMES},
                total_decision_target_reads={n:sum(summaries[t]["reads"][n] for t in BASE)
                      for n in NAMES if n!="fault_oracle_private_target"},
                paired_outcomes=allrows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    v=p.parse_args()
    y=audit(v.input_dir)
    v.output.parent.mkdir(parents=True,exist_ok=True)
    v.output.write_text(json.dumps(y,indent=2,sort_keys=True)+"\n")
    print("PROSPECTIVE_PRECONTACT_TASK_ID_STRONG_BASELINE",json.dumps({
      "n":16,"success":y["total_success"],"reads":y["total_decision_target_reads"],
      "operational_double_faults_reached":y["operational_fault_reached_all"],
      "all_arms_double_faults_reached":y["all_seven_plus_two_comparator_faults_reached"]
    },sort_keys=True))


if __name__=="__main__":main()
