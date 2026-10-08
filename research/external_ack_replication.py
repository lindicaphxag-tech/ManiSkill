"""Outside-investigator selectable-seed native PhysX ACK-fault replication.

This is a *new*, investigator-selected follow-up cohort, NEVER an original
preregistered or independent team result by virtue of running this script.
Source experiment and reader privilege contracts are unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys

TASKS=("pull_cube", "stack_cube")
FAULTS=("applied_no_ack", "neutral_arm_delta_no_ack")
ORIGINAL_SOURCE_FREEZE="3ead83ecbb68eb6a405cdf768a42c617f649ddc4"
SOURCE_METHOD_PATH=Path("research/frozen_ppo_unknown_ack_recovery.py")
DEFAULT_SEED_MIN=120001


def validate_inputs(task: str, fault: str, first_seed: int, count: int):
    if task not in TASKS or fault not in FAULTS:
        raise ValueError("Unknown task or missing/changed delivery-fault truth")
    if type(first_seed) is not int or not DEFAULT_SEED_MIN <= first_seed <= 2147483000:
        raise ValueError("Fresh seed must be an integer >= 120001 and < 2**31")
    if type(count) is not int or count not in (1,8):
        raise ValueError("One original CI integration seed or eight researcher-selected seeds only")
    if first_seed+count-1 >= 2147483647:
        raise ValueError("Seed interval integer overflow")
    return list(range(first_seed,first_seed+count))


def validate_output(raw, task, fault, expected_seeds):
    # A CI exit=0 without all simulator flags is NOT a scientific result.
    if (raw.get("schema")!="action_abi_unknown_arm_command_ack_prospective_physx_v1"
        or raw.get("task")!=("PullCube-v1" if task=="pull_cube" else "StackCube-v1")
        or raw.get("fault")!=fault
        or raw.get("seeds")!=expected_seeds
        or raw.get("real_physx") is not True
        or raw.get("training_performed") is not False):
        raise ValueError("Source provenance is not the published frozen PPO PhysX runner")
    rows=raw.get("rows")
    if not isinstance(rows,list) or len(rows)!=len(expected_seeds) or [r.get("seed") for r in rows]!=expected_seeds:
        raise ValueError("Missing/reordered/fabricated real source seed denominator")
    arms=("source","oracle_live_memory","recovered_one_readback",
          "optimistic_assume_applied","pessimistic_assume_neutral","fail_closed_stop")
    scores={a:0 for a in arms}
    for r in rows:
        vals=r.get("success_once",{})
        if set(vals)!=set(arms) or any(type(vals[a]) is not bool for a in arms):
            raise ValueError("Missing or invalid native success flag")
        for a in arms:
            scores[a]+=int(vals[a])
        reached=r.get("fault_reached",{})
        reads=r.get("readback_queries",{})
        for a in arms[1:]:
            if type(reached.get(a)) is not bool:
                raise ValueError("Fault-injection outcome must be explicitly True/False")
            expected=(-1 if a=="oracle_live_memory" else
                      1 if a=="recovered_one_readback" and reached[a] else 0)
            if reads.get(a)!=expected:
                raise ValueError("Target-read budget is inconsistent with actual fault exposure")
        # A fresh independent seed may terminate BEFORE step 2. This is an
        # INJECTION FAILURE, never a method success/failure. Retain the row,
        # label the non-exposure and keep it in the complete trial denominator.
        recovery_reached=reached["recovered_one_readback"]
        err=r.get("resync_position_error_m")
        if recovery_reached:
            if not isinstance(err,(int,float)) or not math.isfinite(err) or err>3e-5 or err<0:
                raise ValueError("Attested single target readback invalid")
        elif err is not None:
            raise ValueError("Pretend resync measured despite no injected fault")
        if reached["fail_closed_stop"]:
            if (r.get("steps",{}).get("fail_closed_stop")!=3
                or "fail_closed_stop" not in r.get("refusals",{})):
                raise ValueError("Fail-stop controller improperly continued after ACK loss")
        elif "fail_closed_stop" in r.get("refusals",{}):
            raise ValueError("Stop arm claims ACK refusal before ACK loss")
    if scores!=raw.get("success_count"):
        raise ValueError("Summary does not match the full actual seed rows")
    return scores


def run(task: str, fault: str, first_seed: int, count: int, output_dir: Path):
    seeds=validate_inputs(task,fault,first_seed,count)
    if not SOURCE_METHOD_PATH.is_file():
        raise RuntimeError("Run from the ManiSkill repository root (pinned source tree)")
    source_sha=hashlib.sha256(SOURCE_METHOD_PATH.read_bytes()).hexdigest()
    os.environ["ABI_TASK"]=task
    os.environ["ABI_FAULT"]=fault
    # Original source scripts use explicit research/ direct script imports.
    sys.path.insert(0,str(Path.cwd()/"research"))
    base=importlib.import_module("frozen_ppo_unknown_ack_recovery")
    if base.SOURCE_SHA!=ORIGINAL_SOURCE_FREEZE:
        raise RuntimeError("Unexpected original PRE-OUTCOME method identity")
    base.SEEDS=tuple(seeds)
    # Run genuine frozen PPO / six matched real physics controllers; the
    # original runner writes a temporary file with its original schema.
    base.main()
    source_output=Path(f"ack_loss_{task}_{fault}_fresh8.json")
    if not source_output.is_file():
        raise RuntimeError("Simulator did not generate its actual source trials")
    original=json.loads(source_output.read_text())
    counts=validate_output(original,task,fault,seeds)
    original_protocol=original.pop("preregistration")
    original_frozen_commit=original.pop("frozen_prereg_commit")
    if original_frozen_commit!=ORIGINAL_SOURCE_FREEZE:
        raise RuntimeError("Original runner protocol changed")
    original["schema"]="external_selectable_seed_followup_physx_v1"
    original["original_method_protocol"]=original_protocol
    original["original_method_preoutcome_freeze"]=original_frozen_commit
    original["sample_provenance"]="researcher-selected AFTER original pre-registration; NOT original frozen cohorts"
    original["new_seed_selection"]=dict(first_seed=first_seed,n=count,source="GitHub Actions workflow_dispatch user inputs")
    original["injection_exposure_by_arm"]={
        a:sum(int(r["fault_reached"][a]) for r in original["rows"])
        for a in ("oracle_live_memory","recovered_one_readback","optimistic_assume_applied",
                  "pessimistic_assume_neutral","fail_closed_stop")
    }
    original["injection_failure_definition"]="preplanned step 2 not reached due task termination; preserve entire row and do NOT count it as evidence of a recovery method failing"
    original["method_runner_sha256"]=source_sha
    original["execution"]=dict(
        gh_repository=os.environ.get("GITHUB_REPOSITORY"),
        gh_run_id=os.environ.get("GITHUB_RUN_ID"),
        gh_exact_head_sha=os.environ.get("GITHUB_SHA"),
        who_executed=os.environ.get("GITHUB_ACTOR"),
        research_independent_team_verified=False)
    original["task_success_means"]="official ManiSkill simulator success flag, NOT collision/physical safety"
    original["readback_information_gap"]="recovered has one privileged target read; optimistic/pessimistic have zero; oracle ongoing privileged"
    output_dir.mkdir(parents=True,exist_ok=True)
    out=output_dir/f"external_ack_{task}_{fault}_{first_seed}_{first_seed+count-1}.json"
    out.write_text(json.dumps(original,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    source_output.unlink()
    print("EXTERNAL_USER_SELECTED_NATIVE_PHYSX",json.dumps({
        "output":str(out),"seed_range":[first_seed,first_seed+count-1],
        "task":task,"fault":fault,"per_arm_success":counts,
        "not_pre_registered_original":True,
        "not_external_lab_without_independent_runner":True
    },sort_keys=True))
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--task",choices=TASKS,required=True)
    p.add_argument("--fault",choices=FAULTS,required=True)
    p.add_argument("--first-seed",type=int,required=True)
    p.add_argument("--count",type=int,default=8,choices=(1,8))
    p.add_argument("--output-dir",type=Path,default=Path("replication_artifacts"))
    a=p.parse_args()
    run(a.task,a.fault,a.first_seed,a.count,a.output_dir)


if __name__=="__main__":
    main()
