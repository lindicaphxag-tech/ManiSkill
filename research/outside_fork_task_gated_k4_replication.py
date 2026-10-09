"""Fork-owner-executable outside-seed seven-world PhysX K4 query benchmark.

This is a NEW execution on user-selected fresh seeds, NOT a reproduced
result until run in an independently controlled fork. Original source
blobs, methods, PPO checkpoints, fault semantics and task-only router
are unchanged. The fork operator declares task and first seed BEFORE
running the actual source policy. Selects an entire physically stepped
controller world, never splices outcomes or task action histories.

Scientific limitations: two released PPOs / one Panda control family,
native PhysX zero arm target holds not real lost network packets,
privileged target reads not free, no collision/contact safety proofs.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from math import comb

ORIGINAL_SHA={
    "research/frozen_sources/frozen_ppo_compound_ack_multi_belief_v3.py":
        "99836af14205fe3e95e52a2e0d68237c7c8a9045",
    "research/multi_ack_se3_bounded.py":
        "36707a177549104ba5b4bd9bcebc76518f0d2840",
    "research/frozen_ppo_ack_bounded_query.py":
        "1dc653cdc44e422c8340475ad00f828b3a41eb4f",
    "research/two_history_se3_robust.py":
        "bb5fd155b7291fb127f94138fca321201c8271c3",
}
MODELS={
    "pull_cube":("PullCube-v1","74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube":("StackCube-v1","e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"),
}
ALL_ARMS=(
    "source_no_fault",
    "fault_oracle_private_target",
    "fault_optimistic_unverified_ack",
    "fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query",
)
SELECTIVE=ALL_ARMS[5]
MANDATORY=ALL_ARMS[6]


def select(task, first):
    if task not in MODELS or type(first) is not int or not 600001<=first<=999992:
        raise ValueError("Independent original seeds MUST be 8 consecutive numbers in 600001..999999; select supported task")
    return tuple(range(first,first+8))


def source_contract(repo:Path)->dict:
    exact={}
    for path,expected in ORIGINAL_SHA.items():
        observed=subprocess.check_output(["git","hash-object",path],cwd=repo,text=True).strip()
        if observed!=expected:
            raise RuntimeError(f"Frozen algorithm git blob modified: {path}: {observed}")
        exact[path]=observed
    return exact


def count(raw:dict, task:str, seeds:tuple[int,...])->dict:
    if (
        raw.get("schema")!="compound_two_unknown_ack_multihistory_physx_v1"
        or raw.get("task")!=MODELS[task][0]
        or raw.get("original_seed_population")!=list(seeds)
        or raw.get("original_external_frozen_checkpoint_sha256")!=MODELS[task][1]
        or raw.get("frozen_model_retrained") is not False
        or raw.get("real_physx_simulator") is not True
        or raw.get("two_consecutive_unknown_ack_target_hold_steps")!=[2,3]
        or raw.get("fault_is_native_target_hold_not_network_loss") is not True
        or tuple(raw.get("all_seven_actual_control_arms",()))!=ALL_ARMS
    ):
        raise ValueError("Original source model task fault or unchanged seven-arm definition violated")
    rows=raw.get("episodes")
    if not isinstance(rows,list) or len(rows)!=8 or [r.get("seed") for r in rows]!=list(seeds):
        raise ValueError("Incomplete or duplicate selected independent original task resets")
    per_arm={a:0 for a in ALL_ARMS}
    reads={a:0 for a in ALL_ARMS if a!=ALL_ARMS[1]}
    local=[]
    for row in rows:
        flags=row.get("success_once",{})
        query=row.get("privileged_target_readback_decision_count",{})
        if set(flags)!=set(ALL_ARMS) or any(type(flags[a]) is not bool for a in ALL_ARMS):
            raise ValueError("Original binary official simulator outcome missing")
        if query.get(ALL_ARMS[1])!=-1:
            raise ValueError("Continuously privileged oracle incorrectly marked free")
        for a in ALL_ARMS:
            per_arm[a]+=int(flags[a])
            if a!=ALL_ARMS[1]:
                if type(query.get(a)) is not int or query[a] not in (0,1):
                    raise ValueError("Illegal or missing real private target read count")
                reads[a]+=query[a]
        for a in ALL_ARMS[1:]:
            injection=[f.get("step") for f in row.get("faults",{}).get(a,[])]
            if injection!=[2,3] and not (a==ALL_ARMS[3] and injection==[2]):
                raise ValueError("Missing physical fault exposure in original task trial")
        for a in (ALL_ARMS[4],SELECTIVE,MANDATORY):
            if row.get("max_belief_width",{}).get(a,0)<4:
                raise ValueError("Four original credible histories were not reached")
        if any(query[a]!=0 for a in (ALL_ARMS[0],ALL_ARMS[2],ALL_ARMS[3],ALL_ARMS[4])):
            raise ValueError("Hidden privileged read in no-query native arm")
        route=SELECTIVE if task=="pull_cube" else MANDATORY
        local.append({
            "seed":row["seed"],"task":task,
            "actual_whole_native_controller_arm":route,
            "routed_success":flags[route],
            "mandatory_success":flags[MANDATORY],
            "selective_success":flags[SELECTIVE],
            "routed_target_reads":query[route],
            "mandatory_target_reads":query[MANDATORY],
            "selective_target_reads":query[SELECTIVE],
        })
    if per_arm!=raw.get("success_counts"):
        raise ValueError("Unmodified full simulator success flags and original count differ")
    route=SELECTIVE if task=="pull_cube" else MANDATORY
    return {
        "task":task,"seeds":list(seeds),
        "routed_physical_controller_arm":route,
        "routed_success":per_arm[route],
        "routed_true_controller_target_reads":reads[route],
        "mandatory_success":per_arm[MANDATORY],
        "mandatory_true_controller_target_reads":reads[MANDATORY],
        "selective_success":per_arm[SELECTIVE],
        "selective_true_controller_target_reads":reads[SELECTIVE],
        "all_seven_physically_stepped_controller_successes":per_arm,
        "all_privileged_decision_readback_counts":reads,
        "routed_only_successes":sum(r["routed_success"] and not r["mandatory_success"] for r in local),
        "mandatory_only_successes":sum(r["mandatory_success"] and not r["routed_success"] for r in local),
        "complete_per_seed_results":local,
        "all_eight_source_state_failures_retained":True,
    }


def self_test():
    assert select("pull_cube",600001)==tuple(range(600001,600009))
    for a,b in [("pull_cube",5),("wrong",600001),("stack_cube",True),("pull_cube",999993)]:
        try:select(a,b)
        except ValueError:pass
        else:raise AssertionError("Invalid cohort accepted")
    assert SELECTIVE!=MANDATORY
    print("PASS: the fork controls genuinely new nondevelopment task seeds before native rollout")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",required=False,choices=tuple(MODELS),default="pull_cube")
    ap.add_argument("--first-seed",required=False,type=int,default=600001)
    ap.add_argument("--output-dir",type=Path,default=Path("outside_k4_task_gated_original"))
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:
        self_test()
        return
    seeds=select(args.task,args.first_seed)
    root=Path(__file__).resolve().parents[1]
    blobs=source_contract(root)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    frozen_inputs={
        "declared_before_any_new_physx_outcome":True,
        "task":args.task,"seeds":list(seeds),
        "routing":{"pull_cube":SELECTIVE,"stack_cube":MANDATORY},
        "original_published_source_git_blobs":blobs,
        "released_PPO_checkpoint_sha256":MODELS[args.task][1],
        "authored_main_repository":"lindicaphxag-tech/ManiSkill",
        "run_operator":os.environ.get("GITHUB_ACTOR","local-operator"),
        "operator_repo":os.environ.get("GITHUB_REPOSITORY","local-working-directory"),
        "operator_run_id":os.environ.get("GITHUB_RUN_ID","not-github-ci"),
        "external_independence_requires_different_account_and_frozen_own_execution":True,
        "actual_physical_fault":"two PhysX native zero-arm-delta holds, not real network packet drops",
        "no_hardware_safety_claim":True,
    }
    manifest=args.output_dir/"operator_declared_before_real_physx.json"
    if manifest.exists():
        raise RuntimeError("Refuse to overwrite an existing fork pre-result declaration")
    manifest.write_text(json.dumps(frozen_inputs,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTSIDE_DECLARED_BEFORE_PHYXS",json.dumps(frozen_inputs,sort_keys=True),flush=True)

    # Original PPO policy and seven physical actor worlds are run unchanged.
    os.environ["ABI_TASK"]=args.task
    sys.path.insert(0,str(root/"research"))
    # The mutable main-branch module advanced after the original study.
    # ALWAYS load the byte-identical frozen original runner from a separate
    # preserved file; never overwrite other studies' newer source.
    pinned_runner=root/"research/frozen_sources/frozen_ppo_compound_ack_multi_belief_v3.py"
    spec=importlib.util.spec_from_file_location("original_frozen_double_ack_controller_v3",str(pinned_runner))
    if spec is None or spec.loader is None:
        raise RuntimeError("Frozen original policy runner unavailable")
    runner=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    if (
        runner.TASK!=args.task or runner.FAULT_STEPS!=(2,3)
        or runner.POS_BUDGET!=.05 or runner.ROT_BUDGET!=.05
        or runner.HORIZON!=50 or tuple(runner.NAMES)!=ALL_ARMS
    ):
        raise RuntimeError("Unfrozen comparator controller action/physics interface")
    runner.SEEDS=seeds
    runner.COHORT[args.task]=(MODELS[args.task][0],seeds)
    runner.PROTO=str(manifest)
    runner.main()
    original=root/f"compound_multi_ack_{args.task}_original8.json"
    raw=original.read_bytes()
    q=json.loads(raw)
    if q.get("preoutcome_protocol")!=str(manifest):
        raise ValueError("Fork selected run protocol not embedded into actual original PhysX source")
    original_dest=args.output_dir/f"outside_{args.task}_{args.first_seed}_8_original_worlds.json"
    original_dest.write_bytes(raw)
    outcome=count(q,args.task,seeds)
    outcome.update({
        "native_PPO_and_controller_source_hashes":blobs,
        "raw_original_source_sha256":hashlib.sha256(raw).hexdigest(),
        "operator_manifest_sha256":hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "actor_verification_must_match_workflow_in_fork":True,
        "no_independent_algorithm_reimplementation":True,
        "not_real_TCP_ACK_loss":True,
        "not_physical_robot_safety":True,
    })
    (args.output_dir/"independently_recomputed_eight_worlds.json").write_text(
        json.dumps(outcome,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTSIDE_FORK_REAL_K4_PHYSX_RESULT",json.dumps({
        "task":args.task,"seeds":list(seeds),
        "routed_success":outcome["routed_success"],
        "routed_reads":outcome["routed_true_controller_target_reads"],
        "mandatory_success":outcome["mandatory_success"],
        "mandatory_reads":outcome["mandatory_true_controller_target_reads"],
    },sort_keys=True))


if __name__=="__main__":
    main()
