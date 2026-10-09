"""Source-verified evidence audit: where geometry-triggered unknown-ACK recovery fails.

Pure Python stdlib. Reads the BYTE-UNMODIFIED eight original genuine ManiSkill
PhysX shard JSONs under public main, hashes every original file with its own
archive manifest, and cross-checks the separately frozen full-64 audit.

This is an OBSERVATIONAL post-outcome analysis, not a new physically executed
robot experiment, a causal contact explanation, a predeclared subgroup
confirmation, or an external independent lab replication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
ARCHIVE=ROOT/"evidence"/"compound_ack_64_original_native_physx_420001_430032"
ADAPTIVE="fault_robust_then_single_privileged_query"
FIXED="fault_always_single_privileged_query"
EXPECTED_RUN_ID=37900209486
TASKS={"pull_cube":420001,"stack_cube":430001}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read_exact_shard(folder, task, chunk):
    name=f"compound_new64_{task}_chunk{chunk}_original8.json"
    require(folder.is_dir(), "Missing original shard folder")
    manifest=folder/"SHA256SUMS"
    require(manifest.is_file(), "Original per-shard SHA256 manifest absent")
    pinned={}
    for row in manifest.read_text(encoding="utf-8").splitlines():
        digest, filename=row.split(maxsplit=1)
        filename=filename.removeprefix("./")
        require(filename not in pinned and "/" not in filename
                and "\\" not in filename and len(digest)==64,
                "Illegal source manifest item")
        pinned[filename]=digest
    require(name in pinned and "summary.json" in pinned,
            "Original raw observations or original summary not pinned")
    for filename,digest in pinned.items():
        p=folder/filename
        require(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==digest,
                "Altered or missing original physical evidence: "+filename)
    d=json.loads((folder/name).read_text(encoding="utf-8"))
    rows=d["episodes"]
    require(len(rows)==8,"Original source shard must preserve eight distinct outcomes")
    seeds=list(range(TASKS[task]+8*chunk,TASKS[task]+8*chunk+8))
    require([x["seed"] for x in rows]==seeds,
            "Original source seed identity must be complete and in order")
    require(d["original_seed_population"]==seeds,
            "Original run source declared different trial denominator")
    require(d["task"]==("PullCube-v1" if task=="pull_cube" else "StackCube-v1"),
            "Original frozen task identity changed")
    return rows, pinned[name]


def validate_row(row, task):
    for arm in (ADAPTIVE,FIXED):
        require(type(row["success_once"].get(arm)) is bool,
                "Missing original official task success outcome")
        reads=row["privileged_target_readback_decision_count"].get(arm)
        require(type(reads) is int and 0<=reads<=1,
                "Hidden/malformed decision readback")
        require(type(row["steps"].get(arm)) is int and
                0<=row["steps"][arm]<=50,
                "Missing original robot control horizon")
        assert_not_source=row.get("faults",{}).get(arm,[])
        require([e["step"] for e in assert_not_source]==[2,3],
                "Original paired method did not undergo both actual held commands")
        require(all(e["actual_native_arm_command"]=="all_zero_hold" and
                    e["controller_execution_ack_seen_by_adapter"]=="unknown"
                    for e in assert_not_source),
                "Source physical fault truth not disclosed")
    authorizations=row.get("robust_common_action_authorizations",{}).get(ADAPTIVE,0)
    require(type(authorizations) is int and authorizations>=0,
            "No trustworthy bounded native action count")
    physical_checks=row.get("robust_native_target_bound_checks",{}).get(ADAPTIVE,[])
    require(isinstance(physical_checks,list),
            "No actually dispatched certificate witness list")
    for check in physical_checks:
        require(check["step"] not in (2,3) and
                check.get("only_audit_after_physical_dispatch") is True,
                "Claiming an intended-but-undelivered physical geometry certificate")
        for error,bound in (("position_error_m","worst_case_position_limit_m"),
                            ("rot_error_rad","worst_case_rot_limit_rad")):
            e=check.get(error); v=check.get(bound)
            require(type(e) in (int,float) and type(v) in (int,float)
                    and math.isfinite(e) and math.isfinite(v) and
                    e>=0 and v>=0 and e<=v+1e-4,
                    "Physical setpoint audit witness invalid")
    require(authorizations>=len(physical_checks),
            "Physically checked actions exceed algorithm certificate count")
    return {
      "task":task,
      "seed":row["seed"],
      "selective_task_success":row["success_once"][ADAPTIVE],
      "fixed_early_task_success":row["success_once"][FIXED],
      "selective_private_target_reads":row["privileged_target_readback_decision_count"][ADAPTIVE],
      "fixed_private_target_reads":row["privileged_target_readback_decision_count"][FIXED],
      "selective_native_steps":row["steps"][ADAPTIVE],
      "fixed_early_native_steps":row["steps"][FIXED],
      "selective_bounded_action_authorizations":authorizations,
      "selective_physically_dispatched_certificates":len(physical_checks),
      "selective_refusal":row.get("refusals",{}).get(ADAPTIVE),
      "selective_internal_failure_reason":row.get("failure_causes",{}).get(ADAPTIVE),
      "source_no_fault_success":row["success_once"]["source_no_fault"],
    }


def exact_two_sided_discordant_p(first_only,second_only):
    n=first_only+second_only
    if n==0:return 1.
    tail=sum(math.comb(n,k) for k in range(min(first_only,second_only)+1))
    return min(1.,2.*tail/(2**n))


def analyze(folder=ARCHIVE):
    original=json.loads((folder/"ORIGINAL_ALL64_INDEPENDENT_SOURCE_AUDIT.json").read_text())
    require(original["original_run_id"]==EXPECTED_RUN_ID and
            original["n_source_states"]==64 and
            original["n_genuine_matched_worlds"]==448,
            "Changed original full-denominator source audit identity")
    rows=[]
    raw_shard_sha={}
    for task in TASKS:
        for chunk in range(4):
            sub=folder/f"multiack-prospective-{task}-chunk{chunk}-{EXPECTED_RUN_ID}"
            gathered,digest=read_exact_shard(sub,task,chunk)
            raw_shard_sha[f"{task}_chunk{chunk}"]=digest
            rows.extend(validate_row(row,task) for row in gathered)
    require(len(rows)==64 and
            len({(r["task"],r["seed"]) for r in rows})==64,
            "Incomplete original physical register")

    def group(group):
        both=[r["seed"] for r in group if
              r["selective_task_success"] and r["fixed_early_task_success"]]
        selective_only=[r for r in group if
              r["selective_task_success"] and not r["fixed_early_task_success"]]
        fixed_only=[r for r in group if
              not r["selective_task_success"] and r["fixed_early_task_success"]]
        neither=[r["seed"] for r in group if
              not r["selective_task_success"] and not r["fixed_early_task_success"]]
        successes=dict(
            selective=sum(r["selective_task_success"] for r in group),
            fixed=sum(r["fixed_early_task_success"] for r in group))
        reads=dict(selective=sum(r["selective_private_target_reads"] for r in group),
                   fixed=sum(r["fixed_private_target_reads"] for r in group))
        return dict(
            task_states=len(group),
            official_task_successes=successes,
            actual_private_reads=reads,
            paired_outcomes=dict(
                both_success=len(both),
                selective_only=[r["seed"] for r in selective_only],
                fixed_early_only=[r["seed"] for r in fixed_only],
                neither_success=len(neither)),
            unadjusted_exploratory_two_sided_p=exact_two_sided_discordant_p(
                len(selective_only),len(fixed_only)),
            fixed_only_breakdown={
                "no_private_target_read":[r["seed"] for r in fixed_only
                                           if r["selective_private_target_reads"]==0],
                "one_private_target_read_but_failed":[r["seed"] for r in fixed_only
                                           if r["selective_private_target_reads"]==1],
                "source_original_no_fault_succeeded":[r["seed"] for r in fixed_only
                                           if r["source_no_fault_success"]],
                "all_failed_selective_horizon_50":all(
                    r["selective_native_steps"]==50 for r in fixed_only),
                "each_original_failure_witness":fixed_only,
            },
        )
    overall=group(rows)
    subtotals={task:group([r for r in rows if r["task"]==task]) for task in TASKS}
    require(overall["official_task_successes"]=={
        "selective":45,"fixed":55},"Original recorded total binary outcomes changed")
    require(overall["actual_private_reads"]=={
        "selective":44,"fixed":64},"Original query decision budget changed")
    require(overall["paired_outcomes"]["both_success"]==42 and
            len(overall["paired_outcomes"]["selective_only"])==3 and
            len(overall["paired_outcomes"]["fixed_early_only"])==13 and
            overall["paired_outcomes"]["neither_success"]==6,
            "Original paired truth mismatch")
    failed=subtotals["stack_cube"]["fixed_only_breakdown"]
    require(len(failed["no_private_target_read"])==8 and
            len(failed["one_private_target_read_but_failed"])==5 and
            failed["all_failed_selective_horizon_50"] is True,
            "StackCube 13 important failures or readback timing were hidden")
    orig=original["overall"]
    require(orig["official_successes"][ADAPTIVE]==45 and
            orig["official_successes"][FIXED]==55 and
            orig["decision_privileged_queries"][ADAPTIVE]==44 and
            orig["decision_privileged_queries"][FIXED]==64,
            "Separate original all-64 published audit contradicts raw evidence")
    return {
        "schema":"original64_prospective_double_ack_task_authority_failure_witness_audit_v1",
        "data_origin":"byte-unchanged eight 2026-10-09 original ManiSkill CPU PhysX chunks, author-executed",
        "experiment_run":"https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900209486",
        "strict_original_source_hashes":raw_shard_sha,
        "full_denominator":64,
        "task_groups":subtotals,
        "all_states":overall,
        "no_hidden_subgroup_or_seed_exclusion":True,
        "scientific_nonclaims":[
            "Failure correlation with delayed/no query is not a proved contact-causation mechanism",
            "Post-outcome 8/5 subgroup is descriptive, not a preregistered treatment comparison",
            "Task-ID prior was selected after this study, not a physically executed new method",
            "Observed geometry-command bound cannot establish contact/trajectory/task safety",
            "Privileged controller target getter during audit is not available to policy",
            "No outside scientific group has independently adopted these owner-run results",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=ARCHIVE)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyze(a.source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    stack=result["task_groups"]["stack_cube"]["fixed_only_breakdown"]
    print("STACK_FAILURE_CAUSAL_HINT_NOT_CAUSAL_PROOF",json.dumps({
      "n_original_trials":64,
      "task_success":result["all_states"]["official_task_successes"],
      "privileged_reads":result["all_states"]["actual_private_reads"],
      "stack_fixed_exclusive_success_n":len(
          result["task_groups"]["stack_cube"]["paired_outcomes"]["fixed_early_only"]),
      "stack_fixed_only_without_query":len(stack["no_private_target_read"]),
      "stack_fixed_only_with_query_but_failed":len(
          stack["one_private_target_read_but_failed"]),
      "all_such_stopped_at_50":stack["all_failed_selective_horizon_50"],
      "exploratory_unadjusted_p":
          result["all_states"]["unadjusted_exploratory_two_sided_p"],
    },sort_keys=True))


if __name__=="__main__":
    main()
