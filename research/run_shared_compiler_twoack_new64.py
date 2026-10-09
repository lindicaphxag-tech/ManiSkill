"""Precommitted genuine PhysX per-shard execution and tamper-evident source audit.

Physically varied BOTH t2 and t3 under hidden ACK; all FAULTED comparators
physically receive same known-delivered neutral probe at t4. No retuning.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, os, subprocess, sys
from pathlib import Path

PREREG="research/SHARED_COMPILER_TWOACK_FROZEN_PPO64_PREOUTCOME_V1.json"
SOURCE="research/frozen_ppo_shared_compiler_twoack_2x2_physx.py"
OLD_SOURCE="research/frozen_ppo_mixed_ack_truth_physx.py"
CLASSIFIER="research/empirical_probe_response_classifier.py"
START={"pull_cube":1480001,"stack_cube":1490001}
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
CHECKPOINT={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
"stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
NAMES=("source_no_fault","fault_oracle_private_target",
"fault_optimistic_unverified_ack","fault_strict_common_exact",
"fault_robust_two_history_without_query",
"fault_robust_then_single_privileged_query",
"fault_public_t3_fourhistory_or_t4_query",
"fault_always_single_privileged_query",
"fault_assume_held_without_query")
PUBLIC="fault_public_t3_fourhistory_or_t4_query"
STRONG={"pull_cube":"fault_robust_then_single_privileged_query",
        "stack_cube":"fault_always_single_privileged_query"}
FIXED="fault_always_single_privileged_query"
HELD="fault_assume_held_without_query"

def blob(path):
    return subprocess.check_output(["git","hash-object",path],text=True).strip()

def select(task,chunk):
    if task not in START or type(chunk) is not int or chunk not in range(4):
        raise ValueError("Unexpected task/shard")
    return list(range(START[task]+8*chunk,START[task]+8*chunk+8))

def assert_preoutcome():
    p=json.loads(Path(PREREG).read_text())
    if p["schema"]!="prospective_shared_postquery_compiler_2x2_two_ACK_v1":
        raise ValueError("Wrong preregistration schema")
    if p["total_resets"]!=64 or p["physical_worlds"]!=576:
        raise ValueError("Original registered task denominator changed")
    if p["seeds"]!={"pull_cube":{"start":1480001,"end":1480032},
                     "stack_cube":{"start":1490001,"end":1490032}}:
        raise ValueError("Registered reset identities changed")
    if blob(OLD_SOURCE)!="36e672446407435e656cbf8aba6fa2de7c1e9d0e" or blob(CLASSIFIER)!="064bb46831b61af73ad445bc836326837ec5468f":
        raise ValueError("Previously frozen source/model changed")
    for task in START:
        assert len([s for chunk in range(4) for s in select(task,chunk)])==32

def truth(seed):
    i=(seed-1)%4
    return ("applied" if i in (1,3) else "held",
            "applied" if i in (2,3) else "held")

def validate(d,task,chunk):
    seeds=select(task,chunk)
    if (d.get("schema")!="frozen_ppo_shared_compiler_native_2x2_four_truth_v1"
        or d.get("preoutcome_protocol")!=PREREG
        or d.get("original_seed_population")!=seeds
        or d.get("task")!=TASKS[task]
        or d.get("all_nine_actual_control_arms")!=list(NAMES)
        or d.get("frozen_model_retrained") is not False
        or d.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT[task]
        or d.get("real_physx_simulator") is not True
        or d.get("two_consecutive_unknown_ack_command_steps")!=[2,3]
        or d.get("both_physical_ack_truths_balanced_over_seed_mod4") is not True
        or d.get("shared_known_delivered_neutral_probe_step4") is not True
        or len(d.get("episodes",[]))!=8):
        raise ValueError("Original native simulator run not complete/specified")
    outcomes={name:{"success":0,"reads":0} for name in NAMES if name!=NAMES[1]}
    rows=[]; coverage={}; wrong=0; confident=0
    for seed,r in zip(seeds,d["episodes"]):
        if r.get("seed")!=seed or r.get("task")!=TASKS[task]:
            raise ValueError("Wrong source seed or task")
        t2,t3=truth(seed)
        if [r.get("original_precommitted_physical_t2_execution_truth"),
            r.get("original_precommitted_physical_t3_execution_truth")]!=[t2,t3]:
            raise ValueError("Original physics truth not 2x2 precommitted")
        if r.get("physical_truth_index_seed_mod4_AUDIT_ONLY")!=(seed-1)%4:
            raise ValueError("Fault truth is not auditable")
        parity=r.get("matched_prefix_physical_audit")
        if not isinstance(parity,dict) or parity.get("valid_exact_prefix") is not True:
            raise ValueError("Missing identical full physical command prefix certificate")
        for field in ("pre_t5_achieved_position_max_abs_m",
                      "pre_t5_achieved_orientation_geodesic_rad",
                      "pre_t5_target_position_max_abs_m",
                      "pre_t5_target_orientation_geodesic_rad"):
            if parity.get(field) is None or parity[field]>5e-5:
                raise ValueError("Physical prefix mismatch invalidates query-only experiment")
        if len(parity.get("native_fault_dispatch_linf_each",[]))!=2 or any(
            v>5e-5 for v in parity["native_fault_dispatch_linf_each"]):
            raise ValueError("Native command dispatches differ before query")
        traces=r.get("postquery_shared_compiler_trace",{})
        compiled_steps={}
        for pname in (PUBLIC,FIXED):
            events=traces.get(pname,[])
            for e in events:
                if (e.get("step",0)<5
                    or e.get("compiler")!="base.normalized_target_delta:approximate=True:old_override=single_belief_pose"
                    or e.get("state_container")!="UncertainDeliveryBelief"
                    or e.get("acknowledge_path")!="prepare_acknowledge_common_for_all_postquery_steps"
                    or len(e.get("compiled_native_6d",[]))!=6
                    or len(e.get("source_policy_native",[]))!=7
                    or len(e.get("prior_belief_xyz",[]))!=3
                    or len(e.get("prior_belief_quaternion_xyzw",[]))!=4):
                    raise ValueError("Post-query algorithm was not on shared compiler")
            compiled_steps[pname]=len(events)
        flags=r.get("success_once",{}); reads=r.get("privileged_target_readback_decision_count",{})
        if set(flags)!=set(NAMES) or set(reads)!=set(NAMES):
            raise ValueError("Nine native controller arms not recorded")
        if reads[NAMES[1]]!=-1:
            raise ValueError("Unrestricted oracle misreported as zero-read")
        actual_faults=r.get("faults",{})
        physical_coverage={}
        applied_nonzero=0
        for name in NAMES[1:]:
            f=actual_faults.get(name,[])
            steps=[z.get("step") for z in f]
            if steps not in ([],[2],[2,3]):
                raise ValueError("Fault order altered or fabricated")
            physical_coverage[name]=steps==[2,3]
            for z in f:
                idx=int(z["step"])-2; required=(t2,t3)[idx]
                if z.get("actual_native_action_is_precommitted_applied") is not (required=="applied"):
                    raise ValueError("Native source truth mismatched dispatched arm")
                if z.get("actual_native_precommitted_execution_truth",required)!=required:
                    raise ValueError("Audit-only true fault inconsistent")
                if z.get("controller_execution_ack_seen_by_adapter")!="unknown":
                    raise ValueError("Private truth leaked into adapter ACK")
                if z.get("actual_native_arm_command")!=(
                    "native_intended_action_physically_applied" if required=="applied" else "all_zero_hold"):
                    raise ValueError("Native fault dispatch inconsistent")
                actual=z.get("actual_native_6d_dispatched")
                if not isinstance(actual,list) or len(actual)!=6:
                    raise ValueError("Physical six-axis command missing")
                if required=="held" and any(abs(float(a))>1e-12 for a in actual):
                    raise ValueError("Held command not actually zero")
                if required=="applied" and any(abs(float(a))>1e-12 for a in actual):
                    applied_nonzero+=1
            probe=r.get("shared_neutral_probe_step4",{}).get(name)
            if probe is not None:
                if (probe.get("step")!=4 or probe.get("physically_dispatched") is not True
                    or probe.get("known_delivered_no_new_unknown_ack") is not True
                    or probe.get("native_six_dim_arm")!=[0.0]*6
                    or probe.get("audit_only_target_position_delta_m",1)>1e-4
                    or probe.get("audit_only_target_orientation_delta_rad",1)>1e-4):
                    raise ValueError("Unequal, omitted or wrong common physical probe")
        for name in outcomes:
            if type(flags[name]) is not bool or type(reads[name]) is not int or not 0<=reads[name]<=1:
                raise ValueError("Invalid task success/private read budget")
            outcomes[name]["success"]+=int(flags[name])
            outcomes[name]["reads"]+=reads[name]
        ev=r.get("public_t3_evidence") or {}
        if ev:
            probe=r.get("shared_neutral_probe_step4",{}).get(PUBLIC)
            if probe is None or r.get("public_motion_observation_cost_samples",{}).get(PUBLIC)!=2:
                raise ValueError("Unobserved or hidden public probe measurement")
            if ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True:
                raise ValueError("Private state leaked into classifier")
            if ev.get("physical_candidate_count",0) not in (2,3,4):
                raise ValueError("Wrong finite full pose belief support")
            if ev.get("authorized") is True:
                if ev.get("resync_source") not in (None,"empirical_public_achieved_motion") or reads[PUBLIC]:
                    raise ValueError("Confident public branch used private target")
                confident+=1
                wrong+=int(ev.get("wrong_confident") is True)
            elif ev.get("authorized") is False:
                if ev.get("resync_source") not in (None,"one_counted_authoritative_controller_target_read"):
                    raise ValueError("Unaccounted fallback")
                if ev.get("resync_source") is None and reads[PUBLIC]!=0:
                    raise ValueError("Phantom authoritative query")
                if ev.get("resync_source") is not None and reads[PUBLIC]!=1:
                    raise ValueError("Uncharged authoritative query")
            else:
                raise ValueError("Missing explicit public admit/reject")
        rows.append({"task":task,"seed":seed,"truth":t2+"/"+t3,
                     "new_success":flags[PUBLIC],"strong_success":flags[STRONG[task]],
                     "fixed_success":flags[FIXED],"held_success":flags[HELD],
                     "new_reads":reads[PUBLIC],"strong_reads":reads[STRONG[task]],
                     "fixed_reads":reads[FIXED],
                     "public_authorized":ev.get("authorized"),
                     "wrong_confident":ev.get("wrong_confident",False),
                     "public_sample_events":r.get("public_motion_observation_cost_samples",{}).get(PUBLIC,0),
                     "all_faulted_arms_received_neutral_probe":len(r.get("shared_neutral_probe_step4",{}))==8,
                     "pre_t5_matched":True,
                     "postquery_shared_compiler_events":compiled_steps,
                     "postquery_shared_compiler_gate":True,
                     "public_both_faults_exposed":physical_coverage[PUBLIC],
                     "all_faulted_arms_both_exposed":all(physical_coverage.values()),
                     "applied_nonzero_native_dispatch_events_all_faulted_arms":applied_nonzero,
                     "failure_causes":r.get("failure_causes",{}),
                     "refusals":r.get("refusals",{})})
    if len(rows)!=8 or len({r["seed"] for r in rows})!=8:
        raise ValueError("Omitted source episode")
    return {"task":task,"seeds":seeds,"rows":rows,"outcomes":outcomes,
            "public_confident":confident,"public_wrong_confident":wrong,
            "public_both_faults_exposed":sum(int(r["public_both_faults_exposed"]) for r in rows),
            "all_faulted_arms_probed":sum(int(r["all_faulted_arms_received_neutral_probe"]) for r in rows)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=tuple(TASKS),required=True)
    ap.add_argument("--chunk",type=int,choices=range(4),required=True)
    args=ap.parse_args()
    assert_preoutcome()
    os.environ["ABI_TASK"]=args.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    m=importlib.import_module("frozen_ppo_shared_compiler_twoack_2x2_physx")
    if m.PROTO!=PREREG or m.FAULT_STEPS!=(2,3) or len(m.NAMES)!=9 or m.HORIZON!=50:
        raise ValueError("Native four-truth source mutated")
    m.SEEDS=select(args.task,args.chunk)
    m.COHORT[args.task]=(TASKS[args.task],m.SEEDS)
    m.main()
    original=Path(f"mixed_ack_{args.task}_original8.json")
    raw=original.read_bytes()
    summary=validate(json.loads(raw),args.task,args.chunk)
    summary.update(schema="shared_compiler_true_2x2_shard_source_audit_v1",
        physical_original_sha256=hashlib.sha256(raw).hexdigest(),
        prereg_git_blob=blob(PREREG),new_runner_git_blob=blob(SOURCE),
        unchanged_response_model_git_blob=blob(CLASSIFIER))
    original.rename(f"sharedcompiler_{args.task}_chunk{args.chunk}_original8.json")
    Path(f"sharedcompiler_{args.task}_chunk{args.chunk}_audit.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("MATCHED_PREFIX_2X2_NATIVE_PHYSX_SHARD",json.dumps({
        "task":args.task,"chunk":args.chunk,"truths":[r["truth"] for r in summary["rows"]],
        "new":summary["outcomes"][PUBLIC],
        "strong":summary["outcomes"][STRONG[args.task]],
        "readback":summary["outcomes"][FIXED],
        "wrong_confident":summary["public_wrong_confident"],
        "public_exposed":summary["public_both_faults_exposed"]
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
