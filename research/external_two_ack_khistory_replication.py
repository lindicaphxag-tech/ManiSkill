"""Fork-owned NEW-SEED true PhysX reproduction of ORIGINAL double unknown-ACK study.

One-click wrapper only: imports unchanged frozen native task evaluator, overrides
the eight never-before-used seed IDs, checks complete original per-case outcome
records, and preserves exactly the original JSON bytes. This is not a new
controller algorithm, a second PPO, or independently validated real hardware.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

METHOD_BLOB="3b502befd8940da51506ae18ed474726642f1a6d"
PROTO_BLOB="4107c00a5359da78542bbaafa922e2f4196f11fd"
SOURCE_FROZEN_BLOB="1dc653cdc44e422c8340475ad00f828b3a41eb4f"
CERTIFIER_BLOB="bb5fd155b7291fb127f94138fca321201c8271c3"
# These are ACTUAL runtime dependencies of the frozen double-ACK method.
# Pinning only the outer experiment file does not pin the controller semantics.
MULTI_HISTORY_CERTIFIER_BLOB="b7103c05b073a161793b454087956eb7210e5a1b"
UNCERTAIN_DELIVERY_BELIEF_BLOB="e554f1897557075def1c871dfe0bc3c6ae58f676"
ACTION_HISTORY_OBSERVER_BLOB="2aa52e477c202386fb6a7e43586d246026b6041d"
ORIGINAL_POLICY_CONTROLLER_ADAPTER_BLOB="c0999d7a1da8e370f635a0d7bb8378e4a93020dd"
ARMS=(
"source_no_fault",
"fault_oracle_private_target",
"fault_optimistic_unverified_ack",
"fault_strict_common_exact",
"fault_robust_two_history_without_query",
"fault_robust_then_single_privileged_query",
"fault_always_single_privileged_query",
)
S="fault_robust_then_single_privileged_query"
A="fault_always_single_privileged_query"
N="fault_robust_two_history_without_query"
CHECKPOINT={
"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
"stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}
ENV={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}

def select(task,first):
    if task not in CHECKPOINT:raise ValueError("Only original frozen published PullCube/StackCube PPO models")
    if type(first) is not int or not 300001<=first<=9999992:
        raise ValueError("Pick eight previously unused FIRST seeds >= 300001 (and <=9999992)")
    return tuple(range(first,first+8))

def original_objects(repo):
    names={
        "frozen_double_ack_method":("research/frozen_ppo_multi_ack_khistory.py",METHOD_BLOB),
        "preoutcome_protocol":("research/MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json",PROTO_BLOB),
        "source_seven_arm_study":("research/frozen_ppo_ack_bounded_query.py",SOURCE_FROZEN_BLOB),
        "original_two_history_certificate":("research/two_history_se3_robust.py",CERTIFIER_BLOB),
        "actual_multi_history_certifier":("research/multi_history_authority.py",MULTI_HISTORY_CERTIFIER_BLOB),
        "uncertain_delivery_belief_recursion":("research/action_abi_uncertain_delivery_belief.py",UNCERTAIN_DELIVERY_BELIEF_BLOB),
        "physical_target_state_observer":("research/action_abi_history_observer.py",ACTION_HISTORY_OBSERVER_BLOB),
        "original_pretrained_policy_native_adapter":("research/frozen_ppo_action_history_observer.py",ORIGINAL_POLICY_CONTROLLER_ADAPTER_BLOB),
    }
    for name,(path,sha) in names.items():
        got=subprocess.check_output(["git","hash-object",path],text=True,cwd=repo).strip()
        if got!=sha:raise RuntimeError(f"Original method/model/protocol was changed: {name} {got}")
    return {name:sha for name,(_,sha) in names.items()}

def audit(data,task,seeds):
    if (data.get("schema")!="two_unknown_ack_khistory_certify_query_physx_v1"
        or data.get("task")!=ENV[task]
        or data.get("original_seed_population")!=list(seeds)
        or data.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT[task]
        or data.get("frozen_protocol")!="research/MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json"
        or data.get("real_physx_simulator") is not True
        or data.get("frozen_model_retrained") is not False
        or data.get("fault_is_native_target_hold_not_network_loss") is not True
        or data.get("multi_target_unknown_fault_steps")!=[2,4]
        or data.get("all_seven_actual_control_arms")!=list(ARMS)
        or data.get("no_claim_of_global_multi_rotation_optimality") is not True):
        raise ValueError("Wrong exact original frozen source/model/controller protocol")
    rows=data.get("episodes",[])
    if len(rows)!=8 or not isinstance(rows,list):
        raise ValueError("All eight original native PhysX source episodes REQUIRED, including failures")
    calc={a:0 for a in ARMS}
    reached={a:0 for a in ARMS[1:]}
    count_read={S:0,A:0}
    maxK=1
    for j,r in enumerate(rows):
        if r.get("seed")!=seeds[j] or r.get("task")!=ENV[task]:
            raise ValueError("Duplicated/out-of-cohort native reset seed")
        success=r.get("success_once",{})
        if set(success)!=set(ARMS) or any(type(v) is not bool for v in success.values()):
            raise ValueError("Must report official task outcomes including FALSE")
        for arm in ARMS:calc[arm]+=int(success[arm])
        ledger=r.get("privileged_target_readback_decision_count",{})
        if ledger.get("fault_oracle_private_target")!=-1:
            raise ValueError("Private continuous oracle MUST NOT count as zero reads")
        if ledger.get(S) not in (0,1,2) or ledger.get(A) not in (0,1,2):
            raise ValueError("Original ≤2 decision readback limit violated")
        if any(ledger.get(n)!=0 for n in (
            "source_no_fault","fault_optimistic_unverified_ack",
            "fault_strict_common_exact",N)):
            raise ValueError("One of zero-readback arms secretly consulted private memory")
        count_read[S]+=ledger[S];count_read[A]+=ledger[A]
        for a in ARMS[1:]:
            events=r.get("faults",{}).get(a)
            if not isinstance(events,list):
                raise ValueError("Fault not reported, including case of refusal-before-fault")
            if [e.get("step") for e in events] not in ([],[2],[2,4]):
                raise ValueError("False or unregistered native fault events")
            for e in events:
                if (e.get("actual_native_arm_command")!="all_zero_hold"
                    or e.get("controller_execution_ack_seen_by_adapter")!="unknown"):
                    raise ValueError("This must be actual physically executed zero target delta, unknown ACK")
            reached[a]+=int(len(events)==2)
        for arm,states in r.get("candidate_history_count",{}).items():
            if arm not in ARMS or not isinstance(states,list):
                raise ValueError("Unknown history set count")
            for state in states:
                k=state.get("count")
                if type(k) is not int or not 2<=k<=16:
                    raise ValueError("Untrusted/incomplete history count")
                maxK=max(maxK,k)
        for arm,events in r.get("certified_intent_suppressed_by_actual_fault",{}).items():
            delivered={q["step"] for q in r.get("faults",{}).get(arm,[])}
            for e in events:
                if (e.get("step") not in delivered
                    or e.get("certificate_was_for_requested_not_delivered_action") is not True
                    or e.get("must_not_claim_bound_was_physically_executed") is not True):
                    raise ValueError("Certified REQUEST was incorrectly presented as a delivered physical command")
        for arm,events in r.get("robust_native_target_bound_checks",{}).items():
            if arm not in ARMS:raise ValueError("Unknown physical command bound verifier")
            delivered={q["step"] for q in r.get("faults",{}).get(arm,[])}
            for e in events:
                if e.get("step") in delivered or e.get("only_audit_after_physical_dispatch") is not True:
                    raise ValueError("Rejected command incorrectly audited as actually dispatched")
                if (e["position_error_m"]>e["worst_case_position_limit_m"]+0.0001
                    or e["rot_error_rad"]>e["worst_case_rot_limit_rad"]+0.0001
                    or e["worst_case_position_limit_m"]>0.050001
                    or e["worst_case_rot_limit_rad"]>0.050001):
                    raise ValueError("Original audited physically dispatched controller target violates bounded certificate")
    if calc!=data.get("success_counts") or reached!=data.get("fault_reached_counts"):
        raise ValueError("Per-seed original native successes disagree with published aggregated flag")
    if maxK!=data.get("max_hypotheses_observed"):
        raise ValueError("Actual two-fault history witness count altered")
    return {"all_eight_original_trials":8,"task":task,
        "seeds":list(seeds),"native_task_success":calc,
        "fully_reached_two_physically_executed_native_faults_by_arm":reached,
        "privileged_target_decision_reads":count_read,
        "maximum_logged_candidate_goal_history_count":maxK,
        "source_is_author_fork_implementation_no_external_rewrite":True,
        "native_arm_target_hold_is_NOT_actual_packet_loss":True,
        "no_motor_safety_certification":True}

def self_test():
    assert len(select("pull_cube",300001))==8
    for args in (("bad",300001),("pull_cube",230001),("stack_cube",None)):
        try:select(*args)
        except ValueError:pass
        else:raise AssertionError("Illegitimate external new seed request accepted")
    print("PASS original study selection contracts and external minimum unseen first seed")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=list(CHECKPOINT),default="pull_cube")
    p.add_argument("--first-seed",type=int,default=300001)
    p.add_argument("--output-dir",type=Path,default=Path("outside_two_ack_physx"))
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:return self_test()
    repo=Path(__file__).resolve().parents[1]
    original_shas=original_objects(repo)
    seeds=select(args.task,args.first_seed)
    os.environ["ABI_TASK"]=args.task
    import frozen_ppo_multi_ack_khistory as original
    if (original.TASK!=args.task or original.FAULT_STEPS!=(2,4)
        or original.HORIZON!=50 or original.POS_BUDGET!=.05
        or original.ROT_BUDGET!=.05 or original.NAMES!=ARMS):
        raise RuntimeError("Main-controller experiment parameters were changed")
    # Changes SEED COHORT ONLY, after strict original *method* blob identity check.
    original.SEEDS=seeds
    original.COHORT[args.task]=(original.TASK_NAME,seeds)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    original.main()  # SEVEN physical robot-control worlds x ALL EIGHT original new seeds
    raw=repo/f"two_ack_khistory_{args.task}_original8.json"
    b=raw.read_bytes()
    record=json.loads(b)
    verified=audit(record,args.task,seeds)
    original_out=args.output_dir/f"outside_two_ack_{args.task}_{args.first_seed}_original8.json"
    shutil.copyfile(raw,original_out)
    verified.update({
        "full_original_result_sha256":hashlib.sha256(b).hexdigest(),
        "source_git_blobs":original_shas,
        "decision_time_privileged_getter_is_EXTRA_INFORMATION":True,
        "seed_selection_published_before_outcome":True,
        "outside_execution_requires_external_owner_fork":True,
        "these_results_are_NOT_independent_external_adoption_when_run_on_owner_fork":True})
    (args.output_dir/"exact_verified_summary.json").write_text(
        json.dumps(verified,sort_keys=True,indent=2)+"\n")
    print("OUTSIDE_DOUBLE_ACK_PHYSX_RESULT",json.dumps(verified,sort_keys=True))

if __name__=="__main__":
    main()
