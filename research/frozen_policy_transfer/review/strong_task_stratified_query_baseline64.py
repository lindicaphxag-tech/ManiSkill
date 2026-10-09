"""A deliberately simple STRONG opponent to multi-ACK "query only when needed".

Conditional ON already-completed original 64-state PhysX results, select
the actual adaptive branch for all PullCube task episodes, and the actual
pre-committed t=4 target-query branch for all StackCube episodes.

This is a valid DEFINITION of a possible task-conditioned controller because
task ID is known before policy rollout. However it was CHOSEN AFTER REVIEWING
these results, so the observed combination is NOT a prospective third policy,
not a randomized causal comparison or another executed controller. It is a
retrospective per-task arm composition, and needs a FRESH independent cohort.
Original source actual 7-arm PhysX trials and job logs are linked in JSON.
"""
from __future__ import annotations
from collections import defaultdict
import argparse
import json
from pathlib import Path

SEL="fault_robust_then_single_privileged_query"
FIX="fault_always_single_privileged_query"
ZERO="fault_robust_two_history_without_query"
PROVENANCE="Parsed once from original source job output line COMPOUND_MULTI_ACK_REAL_PHYSX; DERIVED summary transcription, NOT byte-identical source 8-episode JSON"
EXPECTED_JOBS={
 ("pull_cube",420001):113720807286,
 ("pull_cube",420009):113720807290,
 ("pull_cube",420017):113720807296,
 ("pull_cube",420025):113720807480,
 ("stack_cube",430001):113720807284,
 ("stack_cube",430009):113720807391,
 ("stack_cube",430017):113720807275,
 ("stack_cube",430025):113720807362
}

def audit_and_compare(pack: dict) -> dict:
    if (pack.get("schema")!="original_64_double_ACK_physical_task_shard_summary_transcription_v1"
        or pack.get("source_data_note") is None):
        raise ValueError("Original provenance and explicit non-byte-identical transcribed data scope required")
    rows=pack.get("rows")
    if not isinstance(rows,list) or len(rows)!=8:
        raise ValueError("Eight original untouched eight-seed source cohorts required")
    s=defaultdict(lambda:{"states":0,"selective_success":0,"fixed_success":0,
                          "no_query_success":0,"selective_reads":0,"fixed_reads":0})
    seen=set()
    for row in rows:
        task=row.get("task")
        first=row.get("registered_seed_start")
        signature=(task,first)
        if signature in seen or signature not in EXPECTED_JOBS:
            raise ValueError("Source task / genuine eight-shard identities cannot be duplicated or substituted")
        seen.add(signature)
        if (row.get("registered_seed_end")!=first+7
            or row.get("original_github_actions_job_id")!=EXPECTED_JOBS[signature]
            or row.get("original_github_actions_run_id")!=37900209486
            or row.get("provenance")!=PROVENANCE):
            raise ValueError("All source seed ranges, original run and original job log identity must match")
        success=row.get("native_task_success_counts",{})
        if (not isinstance(success,dict) or any(type(success.get(k)) is not int or
              success[k]<0 or success[k]>8 for k in (SEL,FIX,ZERO))):
            raise ValueError("Every original true PhysX task success count required")
        reads=row.get("evidence_triggered_readbacks_per_original_seed",[])
        if len(reads)!=8 or any(type(q) is not int or q not in (0,1) for q in reads):
            raise ValueError("Every true separate decision readback must be accounted for")
        exposed=row.get("all_target_controller_faults_physically_reached_after_double_native_hold",{})
        if any(exposed.get(k)!=8 for k in (SEL,FIX,ZERO)):
            raise ValueError("Original native two-fault exposure incomplete")
        if row.get("maximum_actual_candidate_previous_targets")!=4:
            raise ValueError("A claimed K=4 physical source missing in logged results")
        q=s[task];q["states"]+=8
        for k,v in (("selective_success",success[SEL]),("fixed_success",success[FIX]),
                    ("no_query_success",success[ZERO]),
                    ("selective_reads",sum(reads)),("fixed_reads",8)):
            q[k]+=v
    if set(seen)!=set(EXPECTED_JOBS):
        raise ValueError("Incomplete original signed external source job coverage")
    expected={
      "pull_cube":{"states":32,"selective_success":32,"fixed_success":32,
                   "no_query_success":9,"selective_reads":23,"fixed_reads":32},
      "stack_cube":{"states":32,"selective_success":13,"fixed_success":23,
                    "no_query_success":2,"selective_reads":21,"fixed_reads":32}
    }
    if dict(s)!=expected:
        raise ValueError("Logged original source 64-state figures disagree with the independently source-audited report")
    pooled={k:sum(s[t][k] for t in s) for k in expected["pull_cube"]}
    hybrid_success=s["pull_cube"]["selective_success"]+s["stack_cube"]["fixed_success"]
    hybrid_reads=s["pull_cube"]["selective_reads"]+s["stack_cube"]["fixed_reads"]
    assert hybrid_success==55 and hybrid_reads==55
    assert pooled["selective_success"]==45 and pooled["fixed_success"]==55
    assert pooled["selective_reads"]==44 and pooled["fixed_reads"]==64
    assert pooled["no_query_success"]==11
    # All 32 Pull resets were successes in both SELECTIVE and FIXED arms.
    # Stack hybrid is literally the FIXED arm. The per-state success-vector
    # agrees with fixed for all 64 original states. There is no empirical
    # task-success advantage from this retrospective task switch.
    return {
       "observational_analysis":"posthoc simple task-conditioned arm composition, NOT genuinely executed as a third PhysX method",
       "registered_original_64_physx_data_run_id":37900209486,
       "original_source_independent_audit_run_id":37900694213,
       "original_8_actual_job_ids":[EXPECTED_JOBS[k] for k in sorted(EXPECTED_JOBS)],
       "actual_native_physx_distinct_state_count":64,
       "frozen_policy_architectures":2,
       "physical_controller_families":1,
       "source_task_strata":dict(s),
       "actually_run_evidence_triggered":{"native_task_successes":45,"privileged_target_reads":44},
       "actually_run_fixed_step4":{"native_task_successes":55,"privileged_target_reads":64},
       "posthoc_task_conditioned_not_executed":{
            "decision_known_before_first_action":"if task is PullCube select original reactive branch; if StackCube choose original fixed-t4 read branch",
            "native_task_successes_composed_from_original_results":hybrid_success,
            "privileged_reads_composed_from_original_results":hybrid_reads,
            "original_state_success_vector_identical_to_fixed_step4":True,
            "fewer_privileged_reads_than_original_fixed":64-hybrid_reads,
            "NOT_prospectively_tested_as_single_controller":True,
            "NOT_a_new_64_seed_simulation_or_independent_external_replication":True,
        },
        "observed_aggregate_query_cost_crossover_lambda_vs_reactive":(55-45)/(55-44),
        "method_claim":"Existing K-history certifier alone does not demonstrate superior query timing; a trivial task-stratified readback choice already sets a higher and more defensible control baseline.",
        "precommitted_go_nogo":"Require an independent new native PhysX cohort, a matched or cheaper privileged-read budget, honest fault exposure, and outperforming simple task-conditioned and fixed-t4 baselines before claiming original query-timing superiority.",
        "independent_external_reproduction":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    obj=audit_and_compare(json.loads(args.input.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "reactive":obj["actually_run_evidence_triggered"],
        "fixed":obj["actually_run_fixed_step4"],
        "retrospective_unrun_strong_baseline":obj["posthoc_task_conditioned_not_executed"],
        "no_sota_claim":True
    },sort_keys=True))

if __name__=="__main__":
    main()
