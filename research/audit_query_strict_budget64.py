"""Audit untouched original 64 PhysX paired selective-vs-periodic-query trials.

This is a POST-RUN evidence integrity check, not an independent reimplementation.
All seed IDs, method identity, fault, comparator arms and placebo schedule
were prospectively frozen in CERTIFY_QUERY_PERIODIC_PLACEBO_64_PREDECLARED_V1.
Never exclude failures or post-hoc alter the placebo quota.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

BASES={"pull_cube":360001,"stack_cube":370001}
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
CHECKPOINTS={
"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
"stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
PROTO="research/QUERY_STRICT_SHARED_BUDGET16_NEW64_PREREG_V1.json"
ORIGINAL_PRECOMMIT="a47fb2b7eedcb90803bebe4845d47082b1a279da"
ARMS=(
"source_no_fault",
"fault_oracle_private_target",
"fault_optimistic_unverified_ack",
"fault_strict_common_exact",
"fault_robust_two_history_without_query",
"fault_robust_then_single_privileged_query",
"fault_robust_quota_two_per_eight",
"fault_precommitted_seed_schedule_query",
"fault_always_single_privileged_query",
)
ADAPTIVE="fault_robust_then_single_privileged_query"
CAPPED="fault_robust_quota_two_per_eight"
PLACEBO="fault_precommitted_seed_schedule_query"
ALWAYS="fault_always_single_privileged_query"
NOQUERY="fault_robust_two_history_without_query"

def paired(a,b):
    up=sum(bool(x["success_once"][a]) and not x["success_once"][b] for x in ROWS)
    down=sum(not x["success_once"][a] and bool(x["success_once"][b]) for x in ROWS)
    n=up+down
    if not n:
        p=1.0
    else:
        p=min(1.0,2*sum(math.comb(n,k) for k in range(min(up,down)+1))/(2**n))
    return {"adaptive_only":up,"comparator_only":down,
            "exact_two_sided_p_unadjusted_exploratory":p}

ROWS=[]

def audit(directory:Path)->dict:
    global ROWS
    ROWS=[]
    groups=[]
    unexposed_faults=[]
    fault_exposure_counts={a:0 for a in ARMS[1:]}
    for task,first in BASES.items():
        for chunk in range(4):
            seeds=list(range(first+8*chunk,first+8*chunk+8))
            filename=f"strict_quota_{task}_chunk{chunk}_original8.json"
            file=directory/filename
            if not file.is_file() or not file.stat().st_size:
                raise ValueError("Missing ORIGINAL prespecified eight native PhysX episodes "+filename)
            original=json.loads(file.read_text(encoding="utf-8"))
            if (original.get("schema")!="certify_query_strict_2per8_target_read_budget_new64_v1"
                or original.get("preoutcome_protocol_first_commit")!=ORIGINAL_PRECOMMIT
                or original.get("frozen_protocol")!=PROTO
                or original.get("task")!=TASKS[task]
                or original.get("original_seed_population")!=seeds
                or original.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINTS[task]
                or original.get("all_nine_actual_control_arms")!=list(ARMS)
                or original.get("original_source_method_git_blob")!="1dc653cdc44e422c8340475ad00f828b3a41eb4f"
                or original.get("original_robust_certifier_git_blob")!="bb5fd155b7291fb127f94138fca321201c8271c3"
                or original.get("real_physx_simulator") is not True
                or original.get("frozen_model_retrained") is not False
                or original.get("fault_is_native_target_hold_not_network_loss") is not True):
                raise ValueError("Original source/model/seed/controller mismatch in "+filename)
            trials=original.get("episodes")
            if not isinstance(trials,list) or len(trials)!=8:
                raise ValueError("Incomplete original 8 episodes: "+filename)
            observed={k:0 for k in ARMS}
            query_adaptive=query_placebo=query_cap=0
            quota_remaining=2
            for i,row in enumerate(trials):
                if row.get("seed")!=seeds[i] or row.get("task")!=TASKS[task]:
                    raise ValueError("Seed or task changed in original source "+filename)
                diffs=row.get("initial_obs_diff",{})
                if (set(diffs)!=set(ARMS[1:]) or any(
                    not isinstance(v,(float,int)) or not 0<=v<=.0005
                    for v in diffs.values())):
                    raise ValueError("Initial paired physical observations not equal")
                flags=row.get("success_once",{})
                if set(flags)!=set(ARMS) or any(type(x) is not bool for x in flags.values()):
                    raise ValueError("Missing official native success flags, including failures")
                reads=row.get("privileged_target_readback_decision_count",{})
                if set(reads)!=set(ARMS) or any(type(x) is not int for x in reads.values()):
                    raise ValueError("Missing honest privileged decision readback ledger")
                if reads["fault_oracle_private_target"]!=-1:
                    raise ValueError("Continuous oracle private target getter falsely counted")
                if reads[ALWAYS] not in (0,1):
                    raise ValueError("Invalid mandatory private target read count")
                for name in ("source_no_fault","fault_optimistic_unverified_ack",
                             "fault_strict_common_exact",NOQUERY):
                    if reads[name]!=0:
                        raise ValueError("Zero-readback control accessed hidden memory")
                scheduled=int(seeds[i]%4==0)
                if reads[PLACEBO]!=scheduled:
                    raise ValueError("NON-ADAPTIVE PLACEBO quota leaked task difficulty")
                if reads[ADAPTIVE] not in (0,1):
                    raise ValueError("Adaptive illegal >one decision read")
                if reads[CAPPED] not in (0,1):
                    raise ValueError("Quota arm read count nonbinary")
                if row.get("quota_before_trial")!=quota_remaining:
                    raise ValueError("Shared quota before this trial inconsistent")
                quota_remaining-=reads[CAPPED]
                if row.get("quota_after_trial")!=quota_remaining or quota_remaining<0:
                    raise ValueError("Quota exceeded or replenished after task outcome")
                query_cap+=reads[CAPPED]
                query_adaptive+=reads[ADAPTIVE]
                query_placebo+=reads[PLACEBO]
                for name in ARMS[1:]:
                    inj=row.get("faults",{}).get(name)
                    if isinstance(inj,dict) and inj.get("step")==2 and inj.get("actual_native_arm_command")=="all_zero_hold":
                        fault_exposure_counts[name]+=1
                        if name==ALWAYS and reads[name]!=1:
                            raise ValueError("Fault was injected but mandatory target read is missing")
                        continue
                    # The predeclared full-fault-exposure scientific gate
                    # really FAILED for a first-rollout StackCube case.
                    # Keep its original failed control row and mark the
                    # primary study INVALID for all-64-fault inference.
                    refused=row.get("refusals",{}).get(name)
                    if not (inj is None and isinstance(refused,dict)
                            and refused.get("reason")=="HISTORY_OBSERVER_REJECTS_UNREPRESENTABLE_NATIVE_ACTION"
                            and type(refused.get("step")) is int and 0<=refused["step"]<2
                            and refused.get("original_task_outcome_counted_as_failure") is True
                            and flags[name] is False and reads[name]==0):
                        raise ValueError("Missing planned physical fault without a fully accounted pre-fault fail-closed refusal")
                    unexposed_faults.append({"task":task,"seed":seeds[i],
                        "arm":name,"pre_fault_step":refused["step"],
                        "physical_fault_injected":False,"official_task_success":False,
                        "failed_preauthorized_native_action":refused["actual_exception"]})
                for name,recs in row.get("robust_native_target_bound_checks",{}).items():
                    if name not in (NOQUERY,ADAPTIVE,CAPPED,PLACEBO):
                        raise ValueError("Audit allowed unrelated controller")
                    for c in recs:
                        if (c.get("only_audit_after_physical_dispatch") is not True
                            or c["position_error_m"]>c["worst_case_position_limit_m"]+.0001
                            or c["rot_error_rad"]>c["worst_case_rot_limit_rad"]+.0001
                            or c["worst_case_position_limit_m"]>.0500001
                            or c["worst_case_rot_limit_rad"]>.0500001):
                            raise ValueError("Real commanded-target pose violates claimed budget")
                for name,events in row.get("native_projection_NOT_EXACT",{}).items():
                    if name not in ARMS[1:] or any(
                            e.get("exactness")!="NOT_EXACT" for e in events):
                        raise ValueError("A projected native action was declared exact")
                for arm in ARMS:
                    observed[arm]+=int(flags[arm])
                ROWS.append({"task":task,"seed":seeds[i],
                             "success_once":dict(flags),
                             "reads_adaptive":reads[ADAPTIVE],
                             "reads_quota":reads[CAPPED],
                             "reads_placebo":reads[PLACEBO],
                             "reads_mandatory":reads[ALWAYS]})
            if observed!=original.get("success_counts"):
                raise ValueError("Original episode flags contradict summary "+filename)
            if original.get("periodic_readback_counts")!=[
                r["privileged_target_readback_decision_count"][PLACEBO] for r in trials]:
                raise ValueError("Original placebo readback vector silently modified")
            if original.get("selective_readback_counts")!=[
                r["privileged_target_readback_decision_count"][ADAPTIVE] for r in trials]:
                raise ValueError("Original adaptive readback vector silently modified")
            if original.get("quota_token_count_at_start")!=2 or original.get("quota_token_count_end")!=quota_remaining or original.get("quota_used_actual")!=query_cap or query_cap>2:
                raise ValueError("Predeclared per-shard query quota violated")
            groups.append({"task":task,"chunk":chunk,
              "first_seed":seeds[0],"last_seed":seeds[-1],
              "success":observed,"adaptive_reads":query_adaptive,"quota_reads":query_cap,
              "quota_unused":quota_remaining,
              "placebo_reads":query_placebo,"original_file":filename})
    if len(ROWS)!=64 or len({(r["task"],r["seed"]) for r in ROWS})!=64:
        raise ValueError("This is NOT the complete preregistered 64 NEW reset-state denominator")
    count={arm:sum(r["success_once"][arm] for r in ROWS) for arm in ARMS}
    aq=sum(r["reads_adaptive"] for r in ROWS)
    pq=sum(r["reads_placebo"] for r in ROWS)
    cq=sum(r["reads_quota"] for r in ROWS)
    if cq>16 or any(x["quota_reads"]>2 for x in groups):
        raise ValueError("STRICT per-shard capped 16 reads violated")
    if pq!=16:
        raise ValueError("Broken EXACT fixed 16-of-64 original placebo budget")
    if sum(len([x for x in unexposed_faults if x["arm"]==a]) for a in ARMS[1:])!=len(unexposed_faults):
        raise ValueError("Unaccounted injection failure")
    fault_gate_passed=all(fault_exposure_counts[a]==64 for a in ARMS[1:])
    if not fault_gate_passed and not unexposed_faults:
        raise ValueError("Failed fault-exposure gate without preserved witnesses")
    return {
        "schema":"strict_16_read_cap_nine_arm_placebo64_source_integrity_v1",
        "original_source_task_states":64,
        "original_new_distinct_seeds":64,
        "physical_fault":"native arm target hold at step 2, no real network packet loss",
        "source_repository_ownership":"same contributor not independent third-party execution",
        "frozen_seven_arm_method_git_blob":"1dc653cdc44e422c8340475ad00f828b3a41eb4f",
        "native_task_success":count,
        "physical_fault_exposure_by_arm":fault_exposure_counts,
        "pre_fault_controller_refusal_witnesses":unexposed_faults,
        "all_64_predeclared_fault_exposures_satisfied":fault_gate_passed,
        "predeclared_primary_efficacy_inference_gate_PASSED":fault_gate_passed,
        "descriptive_comparisons_only_if_gate_failed":not fault_gate_passed,
        "adaptive_target_decision_reads":aq,
        "capped_adaptive_target_decision_reads":cq,
        "capped_adaptive_uses_exactly_16":cq==16,
        "shared_8seed_query_tokens":2,
        "periodic_nonadaptive_target_decision_reads":pq,
        "always_target_decision_reads":64,
        "adaptive_vs_periodic":paired(ADAPTIVE,PLACEBO),
        "capped_adaptive_vs_periodic":paired(CAPPED,PLACEBO),
        "capped_adaptive_vs_uncapped":paired(CAPPED,ADAPTIVE),
        "adaptive_vs_always":paired(ADAPTIVE,ALWAYS),
        "adaptive_vs_no_query":paired(ADAPTIVE,NOQUERY),
        "eight_original_source_groups":groups,
        "note":"Exploratory exact paired tests are NOT independent multiple-test corrected nor proof of general causal superiority; source audit is not a separate simulation."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    p=ap.parse_args()
    z=audit(p.input_dir)
    p.output.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
    print("STRICT_QUOTA64_COMPLETE_AUDIT",json.dumps({
        "cases":z["original_source_task_states"],
        "success":z["native_task_success"],
        "query_adaptive":z["adaptive_target_decision_reads"],
        "query_periodic":z["periodic_nonadaptive_target_decision_reads"],
        "query_capped":z["capped_adaptive_target_decision_reads"],
        "paired_capped":z["capped_adaptive_vs_periodic"],
        "hard_fault_exposure_gate_passed":z["all_64_predeclared_fault_exposures_satisfied"],
        "unexposed_faults":z["pre_fault_controller_refusal_witnesses"],
        "paired":z["adaptive_vs_periodic"]
    },sort_keys=True))

if __name__=="__main__":
    main()
