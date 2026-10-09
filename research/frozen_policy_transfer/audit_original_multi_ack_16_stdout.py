"""Permanent source-authenticated ORIGINAL PhysX two-ACK stdout transcript audit.

This does not replay the simulator. The 16 complete per-episode JSON objects were
copied from the ORIGINAL GitHub Actions job logs run 37835549067 (see matching
public job IDs), *not* byte-identical original artifact ZIP member files.
Git blob hashes pin THIS published verbatim stdout transcript from PR review.
Both original raw ZIP and source command logs must be cited for independent QA.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE={
 "pull_cube":(230001,"PullCube-v1",113512231185,
    "5564cf40e2835ff43d13e4f9daccd9cb09cc5ded",
    "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
 "stack_cube":(240001,"StackCube-v1",113512231148,
    "4572f0112b28ec2f7441c79ae11bcb84077527e2",
    "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")
}
PREFIX="evidence/two_ack_khistory_new16_230001_240008"
ARMS=(
 "source_no_fault","fault_oracle_private_target",
 "fault_optimistic_unverified_ack","fault_strict_common_exact",
 "fault_robust_two_history_without_query",
 "fault_robust_then_single_privileged_query",
 "fault_always_single_privileged_query"
)
SELECTIVE=ARMS[5]
MANDATORY=ARMS[6]
NO_QUERY=ARMS[4]


def exact_git_blob(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+bytes([0])+raw).hexdigest()


def audit() -> dict:
    totals={name:0 for name in ARMS}
    total_reads={SELECTIVE:0,MANDATORY:0}
    task_reports={}
    all_cases=[]
    for task,(first,label,job,pinned_git_sha,checkpoint) in SOURCE.items():
        path=HERE/PREFIX/f"{task}_eight_true_physx_stdout_episodes.json"
        raw=path.read_bytes()
        if exact_git_blob(raw)!=pinned_git_sha:
            raise ValueError(f"Original transcribed GitHub job log Git blob mutated: {task}")
        entry=json.loads(raw)
        if (
            entry.get("provenance")!="TRANSCODING OF 8 ORIGINAL JSON STDOUT PER-EPISODE PAYLOADS; NOT byte-identical original artifact JSON"
            or entry.get("original_physx_ci_run_id")!=37835549067
            or entry.get("original_physx_ci_job_id")!=job
            or entry.get("pinned_pre_result_protocol_git_blob")!="4107c00a5359da78542bbaafa922e2f4196f11fd"
            or entry.get("task")!=task
            or entry.get("registered_source_seed_cohort")!=[first,first+7]
            or entry.get("n_distinct_actual_task_seed_records")!=8
            or entry.get("claimed_research_adoption_by_third_party") is not False
        ):
            raise ValueError("Original provenance identity mismatch")
        rows=entry.get("episodes")
        if not isinstance(rows,list) or len(rows)!=8:
            raise ValueError("All eight original source stdout cases including failures required")
        individual_success={name:0 for name in ARMS}
        faults={name:0 for name in ARMS[1:]}
        hist_k4_steps=0
        actual_executed_k4_certificates=0
        invalid_dispatch_certificates=0
        selected_queries=0
        task_data=[]
        for index,row in enumerate(rows):
            seed=first+index
            if row.get("seed")!=seed or row.get("task")!=label:
                raise ValueError("Registered original seed/physical task identity invalid")
            outcomes=row.get("success_once")
            if (not isinstance(outcomes,dict) or set(outcomes)!=set(ARMS)
                or any(type(z) is not bool for z in outcomes.values())):
                raise ValueError("Missing original native PhysX task outcomes")
            private=row.get("privileged_target_readback_decision_count")
            if (not isinstance(private,dict) or set(private)!=set(ARMS)
                or private[ARMS[1]]!=-1 or
                any(type(private[n]) is not int or private[n]<0 or private[n]>2
                    for n in ARMS if n!=ARMS[1])
                or any(private[n]!=0 for n in (ARMS[0],ARMS[2],ARMS[3],ARMS[4]))):
                raise ValueError("Unaccounted or hidden privileged target access")
            total_reads[SELECTIVE]+=private[SELECTIVE]
            total_reads[MANDATORY]+=private[MANDATORY]
            selected_queries+=private[SELECTIVE]
            for n in ARMS:individual_success[n]+=int(outcomes[n]);totals[n]+=int(outcomes[n])
            original_faults=row.get("faults",{})
            if not isinstance(original_faults,dict):
                raise ValueError("Missing genuine environment fault events")
            for n in ARMS[1:]:
                events=original_faults.get(n,[])
                if not isinstance(events,list):
                    raise ValueError("Missing per-controller actual fault list")
                if [e.get("step") for e in events] not in ([2,4],[2],[]):
                    raise ValueError("Unregistered, reordered or invented actual native fault steps")
                for e in events:
                    if (e.get("actual_native_arm_command")!="all_zero_hold"
                        or e.get("controller_execution_ack_seen_by_adapter")!="unknown"):
                        raise ValueError("Target hold not actually stepped")
                faults[n]+=int(len(events)==2)
            count_log=(row.get("candidate_history_count") or {}).get(SELECTIVE,[])
            k4=[e for e in count_log if e.get("count")==4]
            if any(e.get("count") not in (2,3,4) for e in count_log):
                raise ValueError("Corrupt K-history state count")
            k4steps={e["step"] for e in k4}
            if len(k4steps)!=len(k4):
                raise ValueError("Replayed duplicate belief timeline")
            hist_k4_steps+=len(k4)
            checks=row.get("robust_native_target_bound_checks",{}).get(SELECTIVE,[])
            executed_k4=[e for e in checks if e["step"] in k4steps]
            actual_executed_k4_certificates+=len(executed_k4)
            suppressed=row.get("certified_intent_suppressed_by_actual_fault",{}).get(SELECTIVE,[])
            physical_steps={e["step"] for e in original_faults.get(SELECTIVE,[])}
            for c in checks:
                if (c.get("only_audit_after_physical_dispatch") is not True
                    or c["step"] in physical_steps
                    or c["position_error_m"]>c["worst_case_position_limit_m"]+.0001
                    or c["rot_error_rad"]>c["worst_case_rot_limit_rad"]+.0001):
                    raise ValueError("Verified physical controller target violated claimed setpoint certificate")
            for c in suppressed:
                if (c["step"] not in physical_steps
                    or c["step"] in {x["step"] for x in checks}
                    or c.get("must_not_claim_bound_was_physically_executed") is not True):
                    invalid_dispatch_certificates+=1
            if invalid_dispatch_certificates:
                raise ValueError("Intent-only certificate incorrectly represented as physically executed")
            refused=(row.get("robust_common_action_refusals",{}).get(SELECTIVE) or [])
            if private[SELECTIVE]!=len(refused):
                raise ValueError("Declared private readings do not match actual refused certificate and query")
            task_data.append({
                "task":task,"seed":seed,"success_selective":outcomes[SELECTIVE],
                "success_always_read":outcomes[MANDATORY],"success_no_read":outcomes[NO_QUERY],
                "queries_selective":private[SELECTIVE],
                "queries_always_read":private[MANDATORY],
                "queries_at_steps":[q["step"] for q in refused],
                "two_physx_faults_selective_reached":len(original_faults.get(SELECTIVE,[]))==2,
                "K4_history_decisions":len(k4),
                "K4_real_dispatched_certificates":len(executed_k4),
            })
        task_reports[task]={
            "original_creator_GitHub_job":job,
            "complete_public_transcript_Git_blob":pinned_git_sha,
            "released_original_PPO_SHA256_from_public_protocol":checkpoint,
            "new_independent_reset_states":8,
            "native_success":individual_success,
            "two_fault_exposure_counts":faults,
            "selective_private_reads":selected_queries,
            "selective_K4_history_decisions":hist_k4_steps,
            "selective_K4_physically_executed_verified_target_certificates":actual_executed_k4_certificates,
        }
        all_cases+=task_data
    assert len(all_cases)==16 and len({(r["task"],r["seed"]) for r in all_cases})==16
    if not (totals[SELECTIVE]==15 and totals[MANDATORY]==15
            and totals[NO_QUERY]==7 and totals[ARMS[2]]==9
            and totals[ARMS[3]]==0
            and total_reads[SELECTIVE]==9 and total_reads[MANDATORY]==32):
        raise ValueError("Original fully matched 16-state physical evidence changed")
    actual_K4=sum(r["selective_K4_history_decisions"] for r in task_reports.values())
    K4executed=sum(r["selective_K4_physically_executed_verified_target_certificates"] for r in task_reports.values())
    if not (actual_K4==99 and K4executed==92
            and all(r["two_physx_faults_selective_reached"] for r in all_cases)):
        raise ValueError("Original K=4 and actually DISPATCHED source certificate evidence changed")
    return {
        "schema":"two_fault_native_physx_16_state_original_stdout_review",
        "original_public_actions_url":
         "https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835549067",
        "original_raw_complete_actions_artifact_id":11575139460,
        "source_stdout_archives_are_not_byte_identical_to_original_actions_zip":True,
        "original_16_physical_states":16,"two_separately_precommitted_real_native_held_arm_faults":[2,4],
        "all_original_method_success_counts":totals,
        "source_target_decision_readbacks":total_reads,
        "reduced_private_reads_vs_two_mandatory":
            1-total_reads[SELECTIVE]/total_reads[MANDATORY],
        "authentic_K4_history_decisions_selective":actual_K4,
        "authentic_K4_commanded_setpoints_physically_dispatched_and_audited":K4executed,
        "task_reports":task_reports,"all_source_episode_cases":all_cases,
        "underlying_controller_model":"known root-left Panda target controller, not new robot dynamics",
        "observer_source_hypotheses_completeness_externally_proven":False,
        "independent_external_replication":False,
        "hardware_robot_safety_or_collision_certification":False,
        "claimed_population_task_success_superiority":False
    }


if __name__=="__main__":
    result=audit()
    print(json.dumps({k:v for k,v in result.items() if k in (
        "original_16_physical_states",
        "all_original_method_success_counts","source_target_decision_readbacks",
        "authentic_K4_history_decisions_selective",
        "authentic_K4_commanded_setpoints_physically_dispatched_and_audited"
    )},sort_keys=True))
