"""Independently runnable ORIGINAL frozen 2-ACK / K=4 ManiSkill PhysX source.

This wrapper changes ONLY the independent fork reviewer's task seed population.
It imports the unchanged, content-pinned original third-party pretrained PPO
experiment and never trains an agent or changes a method hyperparameter.

No successful or failed episode may be discarded. Physical native command
holds are not real ROS/network packet loss, and physical trajectory safety is
not established. Running this in the author's fork does not constitute outside
independent reproduction; inspect the GITHUB_REPOSITORY and GITHUB_ACTOR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

RUNNER_BLOB = "3b502befd8940da51506ae18ed474726642f1a6d"
CERTIFIER_BLOB = "b7103c05b073a161793b454087956eb7210e5a1b"
BELIEF_BLOB = "e554f1897557075def1c871dfe0bc3c6ae58f676"
PREDECLARED_PROTOCOL_BLOB = "4107c00a5359da78542bbaafa922e2f4196f11fd"
N=8
NATIVE_ARMS=(
    "source_no_fault","fault_oracle_private_target",
    "fault_optimistic_unverified_ack","fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query"
)
ADAPTIVE=NATIVE_ARMS[5]
MANDATORY=NATIVE_ARMS[6]
ZERO=NATIVE_ARMS[4]
CHECKPOINTS={
    "pull_cube":("PullCube-v1","74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube":("StackCube-v1","e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")
}


def registered_seeds(task: str, first_seed: int) -> tuple[int,...]:
    if task not in CHECKPOINTS:
        raise ValueError("Only original published PullCube and StackCube frozen PPOs")
    if type(first_seed) is not int or not 300001<=first_seed<=9999992:
        raise ValueError("Choose eight independent source reset seeds >= 300001")
    return tuple(range(first_seed,first_seed+N))


def source_git_blobs(repo: Path) -> dict[str,str]:
    expected={
        "true_original_dual_ACK_PPO_runner":("research/frozen_ppo_multi_ack_khistory.py",RUNNER_BLOB),
        "full_history_SO3_setpoint_certifier":("research/multi_history_authority.py",CERTIFIER_BLOB),
        "command_uncertainty_belief":("research/action_abi_uncertain_delivery_belief.py",BELIEF_BLOB),
        "original_before_outcome_protocol":("research/MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json",PREDECLARED_PROTOCOL_BLOB)
    }
    seen={}
    for name,(path,pinned) in expected.items():
        got=subprocess.check_output(["git","hash-object",path],cwd=repo,text=True).strip()
        if got!=pinned:
            raise RuntimeError(f"Original published experiment source has changed at {name}: {got}")
        seen[name]=got
    return seen


def count_original_true_physx_episodes(raw:dict, task:str, seeds:tuple[int,...])->dict:
    name,model_hash=CHECKPOINTS[task]
    if (
        raw.get("schema")!="two_unknown_ack_khistory_certify_query_physx_v1"
        or raw.get("original_seed_population")!=list(seeds)
        or raw.get("task")!=name
        or raw.get("original_external_frozen_checkpoint_sha256")!=model_hash
        or raw.get("frozen_protocol")!="research/MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json"
        or raw.get("all_seven_actual_control_arms")!=list(NATIVE_ARMS)
        or raw.get("multi_target_unknown_fault_steps")!=[2,4]
        or raw.get("maximum_selective_privileged_reads_per_episode")!=2
        or raw.get("frozen_model_retrained") is not False
        or raw.get("real_physx_simulator") is not True
        or raw.get("fault_is_native_target_hold_not_network_loss") is not True
        or raw.get("physical_robot_safety_certified") is not False
    ):
        raise ValueError("Original native frozen policy/source, fault, model or protocol identity mismatch")
    episodes=raw.get("episodes")
    if not isinstance(episodes,list) or len(episodes)!=8:
        raise ValueError("ALL eight actual registered episodes including original failures required")
    counts={n:0 for n in NATIVE_ARMS}
    reads={ADAPTIVE:0,MANDATORY:0}
    second_fault_exposure={n:0 for n in NATIVE_ARMS[1:]}
    K4=0
    physically_verified_K4=0
    action_suppression_exposures=0
    rows=[]
    for idx,r in enumerate(episodes):
        if r.get("seed")!=seeds[idx] or r.get("task")!=name:
            raise ValueError("Missing, duplicated, shuffled or injected task reset seed")
        successes=r.get("success_once")
        if (not isinstance(successes,dict) or set(successes)!=set(NATIVE_ARMS)
            or any(type(v) is not bool for v in successes.values())):
            raise ValueError("Every official native ManiSkill task outcome must be Boolean")
        queries=r.get("privileged_target_readback_decision_count")
        if (not isinstance(queries,dict) or set(queries)!=set(NATIVE_ARMS)
            or queries[NATIVE_ARMS[1]]!=-1
            or any(type(queries[n]) is not int or queries[n] not in (0,1,2) for n in NATIVE_ARMS if n!=NATIVE_ARMS[1])
            or any(queries[n] for n in (NATIVE_ARMS[0],NATIVE_ARMS[2],NATIVE_ARMS[3],ZERO))):
            raise ValueError("Missing or over-budget privileged target-memory readbacks")
        for n in NATIVE_ARMS:
            counts[n]+=int(successes[n])
        for n in reads: reads[n]+=queries[n]
        original_faults=r.get("faults",{})
        if not isinstance(original_faults,dict):
            raise ValueError("True native PhysX target-hold exposures missing")
        for n in NATIVE_ARMS[1:]:
            events=original_faults.get(n,[])
            if not isinstance(events,list) or [e.get("step") for e in events] not in ([],[2],[2,4]):
                raise ValueError("Missing, fabricated or out-of-order native physical fault")
            if any(e.get("actual_native_arm_command")!="all_zero_hold" or
                   e.get("controller_execution_ack_seen_by_adapter")!="unknown" for e in events):
                raise ValueError("Fault was not a real held target with unknown ACK")
            second_fault_exposure[n]+=int(len(events)==2)
        live_truth_steps={event["step"] for event in original_faults.get(ADAPTIVE,[])}
        hlog=(r.get("candidate_history_count",{}) or {}).get(ADAPTIVE,[])
        K4steps=[x["step"] for x in hlog if x.get("count")==4]
        K4+=len(K4steps)
        if any(type(x.get("count")) is not int or x.get("count") not in (2,3,4)
               for x in hlog):
            raise ValueError("Unknown-source candidate histories ignored")
        verified=r.get("robust_native_target_bound_checks",{}).get(ADAPTIVE,[])
        for check in verified:
            if (check["step"] in live_truth_steps
                or check.get("only_audit_after_physical_dispatch") is not True
                or check["position_error_m"]>check["worst_case_position_limit_m"]+0.0001
                or check["rot_error_rad"]>check["worst_case_rot_limit_rad"]+0.0001
                or check["worst_case_position_limit_m"]>0.0500001
                or check["worst_case_rot_limit_rad"]>0.0500001):
                raise ValueError("Certified native target actually violated or wrongly audited during deliberately suppressed action")
        physically_verified_K4+=sum(check["step"] in K4steps for check in verified)
        suppressed=(r.get("certified_intent_suppressed_by_actual_fault",{}) or {}).get(ADAPTIVE,[])
        for x in suppressed:
            if (x["step"] not in live_truth_steps
                or x.get("certificate_was_for_requested_not_delivered_action") is not True
                or x.get("must_not_claim_bound_was_physically_executed") is not True):
                raise ValueError("Actual injected, suppressed command falsely passed physical certificate")
        action_suppression_exposures+=len(suppressed)
        refusals=(r.get("robust_common_action_refusals",{}) or {}).get(ADAPTIVE,[])
        if len(refusals)!=queries[ADAPTIVE]:
            raise ValueError("Privileged query must be individually justified and logged")
        rows.append({
            "seed":seeds[idx],"official_native_successes":{n:successes[n] for n in NATIVE_ARMS},
            "privileged_target_reads":{n:queries[n] for n in (ADAPTIVE,MANDATORY,ZERO)},
            "faults_actually_seen":{n:len(original_faults.get(n,[])) for n in NATIVE_ARMS[1:]},
            "K4_belief_decision_steps":K4steps,
            "source_target_verified_dispatched_K4_count":sum(check["step"] in K4steps for check in verified),
            "selective_query_authorized_by_refusal_steps":[q.get("step") for q in refusals]
        })
    if counts!=raw.get("success_counts") or second_fault_exposure!=raw.get("fault_reached_counts"):
        raise ValueError("Source native task or native fault denominator silently altered")
    if raw.get("selective_readback_counts")!=[r["privileged_target_readback_decision_count"][ADAPTIVE] for r in episodes]:
        raise ValueError("Original true privileged target readback vector changed")
    observed_max=max([x["count"] for r in episodes for z in r.get("candidate_history_count",{}).values() for x in z]+[1])
    if raw.get("max_hypotheses_observed")!=observed_max:
        raise ValueError("Actual multihistory multiplicity not audited")
    return {
        "task":task,"source_model_public_checkpoint_sha256":model_hash,
        "selected_exact_eight_reset_seeds":list(seeds),
        "source_original_native_task_successes":counts,
        "privileged_controller_target_decision_reads":reads,
        "actual_second_native_fault_reach_count":second_fault_exposure,
        "max_actually_observed_plausible_target_histories":observed_max,
        "source_original_K4_candidate_history_decision_steps":K4,
        "actually_dispatched_audited_K4_setpoint_certificates":physically_verified_K4,
        "separate_recorded_intended_certificates_suppressed_by_fault":action_suppression_exposures,
        "every_actual_separate_physx_trial_including_failure":rows,
        "no_claim_of_belief_source_truth_or_collision_safety":True,
    }


def built_in_negative_tests():
    from copy import deepcopy
    seeds=registered_seeds("pull_cube",300001)
    names=list(NATIVE_ARMS)
    base={
        "schema":"two_unknown_ack_khistory_certify_query_physx_v1",
        "task":"PullCube-v1",
        "original_seed_population":list(seeds),
        "original_external_frozen_checkpoint_sha256":CHECKPOINTS["pull_cube"][1],
        "frozen_protocol":"research/MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json",
        "all_seven_actual_control_arms":names,
        "multi_target_unknown_fault_steps":[2,4],
        "maximum_selective_privileged_reads_per_episode":2,
        "frozen_model_retrained":False,"real_physx_simulator":True,
        "fault_is_native_target_hold_not_network_loss":True,
        "physical_robot_safety_certified":False
    }
    arm=lambda:{"step":2,"actual_native_arm_command":"all_zero_hold",
                   "controller_execution_ack_seen_by_adapter":"unknown"}
    step4=lambda:{"step":4,"actual_native_arm_command":"all_zero_hold",
                   "controller_execution_ack_seen_by_adapter":"unknown"}
    base["episodes"]=[{
        "seed":v,"task":"PullCube-v1",
        "success_once":{n:n!="fault_strict_common_exact" for n in names},
        "privileged_target_readback_decision_count":{
            n:(-1 if n==names[1] else 2 if n==MANDATORY else 0) for n in names},
        "faults":{n:[arm(),step4()] for n in names[1:]},
        "candidate_history_count":{ADAPTIVE:[{"step":5,"count":4}]},
        "robust_native_target_bound_checks":{},
        "robust_common_action_refusals":{},
    } for v in seeds]
    base["success_counts"]={n:0 if n=="fault_strict_common_exact" else 8 for n in names}
    base["fault_reached_counts"]={n:8 for n in names[1:]}
    base["selective_readback_counts"]=[0]*8
    base["max_hypotheses_observed"]=4
    validated=count_original_true_physx_episodes(base,"pull_cube",seeds)
    assert validated["actual_second_native_fault_reach_count"][ADAPTIVE]==8
    for mutation in [
        lambda x:x["episodes"].pop(),
        lambda x:x["episodes"][2].update(seed=300001),
        lambda x:x["episodes"][3]["success_once"].update(source_no_fault="yes"),
        lambda x:x["episodes"][0]["faults"][ADAPTIVE][1].update(step=9),
        lambda x:x["episodes"][0]["privileged_target_readback_decision_count"].update(**{ADAPTIVE:3}),
        lambda x:x["episodes"][0]["robust_native_target_bound_checks"].update(**{
            ADAPTIVE:[{"step":2,"only_audit_after_physical_dispatch":True,
                       "position_error_m":0.0,"worst_case_position_limit_m":0.02,
                       "rot_error_rad":0.0,"worst_case_rot_limit_rad":0.02}]
        }),
    ]:
        bad=deepcopy(base);mutation(bad)
        try:count_original_true_physx_episodes(bad,"pull_cube",seeds)
        except (ValueError,KeyError):pass
        else:raise AssertionError("Unsafe source data mutation escaped original-source reviewer audit")
    for task,s in [("wrong",300001),("stack_cube",100),("pull_cube",9999996)]:
        try:registered_seeds(task,s)
        except ValueError:pass
        else:raise AssertionError("Invalid or previously registered seed selection accepted")
    print("PASS original source/checkpoint/fault identities, 16+ robust evidence conditions and six adversarial source mutations")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(CHECKPOINTS),default="pull_cube")
    p.add_argument("--first-seed",type=int,default=300001)
    p.add_argument("--output-dir",type=Path,default=Path("external_multi_ack_artifacts"))
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        built_in_negative_tests()
        return
    seed_ids=registered_seeds(args.task,args.first_seed)
    repo=Path(__file__).resolve().parents[1]
    exact_blobs=source_git_blobs(repo)
    import os
    os.environ["ABI_TASK"]=args.task
    import frozen_ppo_multi_ack_khistory as original
    if (
        original.TASK!=args.task or tuple(original.FAULT_STEPS)!=(2,4)
        or original.HORIZON!=50 or original.POS_BUDGET!=.05
        or original.ROT_BUDGET!=.05 or original.PROTO!="research/MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json"
        or original.TASK_NAME!=CHECKPOINTS[args.task][0]
        or len(original.NAMES)!=7
    ):
        raise RuntimeError("Original frozen dual-ACK method semantics or budgets have changed")
    original.SEEDS=seed_ids
    original.COHORT[args.task]=(original.TASK_NAME,seed_ids)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    original.main()  # TRUE native simulation all seven arms × eight actual tasks.
    source=repo/f"two_ack_khistory_{args.task}_original8.json"
    if not source.is_file():
        raise RuntimeError("Original native PhysX runner did not produce its original task source file")
    unmodified=source.read_bytes()
    record=json.loads(unmodified)
    summary=count_original_true_physx_episodes(record,args.task,seed_ids)
    summary.update({
        "unmodified_original_native_json_sha256":hashlib.sha256(unmodified).hexdigest(),
        "original_released_method_git_blobs":exact_blobs,
        "executing_github_repository":os.environ.get("GITHUB_REPOSITORY"),
        "executing_github_actor":os.environ.get("GITHUB_ACTOR"),
        "outsider_replication_requires_executing_repo_not_original_author_fork":True,
        "claimed_external_reproduction":False,
        "actually_dropped_network_packets":False,
        "safe_physical_robot_collisions_certified":False
    })
    dest=args.output_dir/f"two_unknown_ACK_original_{args.task}_{args.first_seed}_8cases.json"
    shutil.copyfile(source,dest)  # BYTE-IDENTICAL original predeclared runner output
    (args.output_dir/"reviewer_summary.json").write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("EXTERNAL_MULTI_ACK_ORIGINAL_PHYSX_REVIEW",json.dumps({
        "task":args.task,"seeds":list(seed_ids),
        "success":summary["source_original_native_task_successes"],
        "reads":summary["privileged_controller_target_decision_reads"],
        "K4":summary["source_original_K4_candidate_history_decision_steps"],
        "dispatched_K4":summary["actually_dispatched_audited_K4_setpoint_certificates"],
        "gh_repo":os.environ.get("GITHUB_REPOSITORY"),
        "original_physx_source_sha256":summary["unmodified_original_native_json_sha256"],
    },sort_keys=True))


if __name__=="__main__":
    main()
