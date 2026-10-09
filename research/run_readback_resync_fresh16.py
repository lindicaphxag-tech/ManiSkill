"""Execute eight real native PhysX controller worlds per new seed.

Original frozen published PPOs and K-history action authorizer unchanged.
The eighth world is proactive TASK-BLIND certificate-slack query.
Strong task-ID route comparator uses one whole physically executed existing
control arm, selected before reset. Never mix counterfactual time steps.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path

PROTOCOL="research/READBACK_RESYNC_BELIEF_INVALIDATION_FRESH16_V1.json"
TASKS={"pull_cube":("PullCube-v1",920001),
       "stack_cube":("StackCube-v1",930001)}
ORIGINAL_SHA={
 "research/frozen_ppo_compound_ack_multi_belief.py":"99836af14205fe3e95e52a2e0d68237c7c8a9045",
 "research/multi_ack_se3_bounded.py":"36707a177549104ba5b4bd9bcebc76518f0d2840",
 "research/frozen_ppo_ack_bounded_query.py":"1dc653cdc44e422c8340475ad00f828b3a41eb4f",
}
PROACTIVE_RUNNER_BLOB="45784cf901e028ffc43c0e8cce58d8d89f431955"
ARMS=("source_no_fault","fault_oracle_private_target",
      "fault_optimistic_unverified_ack","fault_strict_common_exact",
      "fault_robust_two_history_without_query",
      "fault_robust_then_single_privileged_query",
      "fault_always_single_privileged_query",
      "fault_authority_slack_proactive_query",
      "fault_phase_value_query")
SELECTIVE=ARMS[5]
FIXED=ARMS[6]
PROACTIVE=ARMS[7]
PHASE=ARMS[8]
ROUTE={"pull_cube":SELECTIVE,"stack_cube":FIXED}
CHECKPOINTS={
 "pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
 "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}

def group(task,chunk):
    if task not in TASKS or type(chunk) is not int or chunk not in (0,):
        raise ValueError("Outside original preregistered 64-state population")
    start=TASKS[task][1]+8*chunk
    return tuple(range(start,start+8))

def frozen_source():
    expected={**ORIGINAL_SHA,"research/frozen_ppo_fixed_resync_corrected.py":PROACTIVE_RUNNER_BLOB}
    for path,sha in expected.items():
        h=subprocess.check_output(["git","hash-object",path],text=True).strip()
        if h!=sha:raise RuntimeError("Original method or pretrained controller code drift: "+path)
    proto=json.loads(Path(PROTOCOL).read_text("utf-8"))
    if (proto.get("schema")!="post_ack_readback_invalidated_cached_belief_fresh16_20261009_v1"
        or proto.get("unseen_cohort",{}).get("stack_cube")!=[930001,930008]
        or proto.get("unseen_cohort",{}).get("pull_cube")!=[920001,920008]):
        raise ValueError("Changed frozen preoutcome query/tolerance contract")
    return expected

def summarize(record,task,chunk,seeds):
    if (record.get("schema")!="fixed_readback_cached_belief_corrected_real_physx_v1"
      or record.get("task")!=TASKS[task][0]
      or record.get("original_seed_population")!=list(seeds)
      or record.get("preoutcome_protocol")!=PROTOCOL
      or record.get("frozen_model_retrained") is not False
      or record.get("real_physx_simulator") is not True
      or record.get("fault_is_native_target_hold_not_network_loss") is not True
      or record.get("two_consecutive_unknown_ack_target_hold_steps")!=[2,3]
      or tuple(record.get("all_seven_actual_control_arms",()))!=ARMS
      or record.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINTS[task]):
        raise ValueError("Source-or-physics controller contract changed")
    rows=record.get("episodes",[])
    if len(rows)!=8 or [r.get("seed") for r in rows]!=list(seeds):
        raise ValueError("Not all eight unaltered native PhysX state outcomes")
    successes={n:0 for n in ARMS}
    reads={n:0 for n in ARMS if n!=ARMS[1]}
    physical=masked=0
    per_seed=[]
    for row in rows:
        flags=row.get("success_once",{})
        q=row.get("privileged_target_readback_decision_count",{})
        if set(flags)!=set(ARMS) or any(type(flags[n]) is not bool for n in ARMS):
            raise ValueError("Missing official task success from actually stepped source")
        if task=="stack_cube":
            if flags[FIXED]!=flags[PHASE] or q[FIXED]!=q[PHASE]:
                raise ValueError("FAIR CONTROL FAILED: same post-readback corrected source action must give same real Stack task result")
            witness=row.get("fixed_readback_postquery_ambiguity_checks",{}).get(FIXED)
            if witness is None or witness.get("after_verified_read_hypotheses")!=1 or witness.get("postquery_maybe_two") is not False:
                raise ValueError("Fixed Stack native action kept stale ambiguous target-state flag")
        if q.get(ARMS[1])!=-1 or any(q.get(n)!=0 for n in (ARMS[0],ARMS[2],ARMS[3],ARMS[4])):
            raise ValueError("Unaccounted privileged controller-state exposure")
        for name in ARMS:
            successes[name]+=int(flags[name])
            if name!=ARMS[1]:
                if type(q.get(name)) is not int or q[name] not in (0,1):
                    raise ValueError("Private readback must be either none or one")
                reads[name]+=q[name]
        width=row.get("max_belief_width",{})
        if any(type(width.get(n)) is not int or width[n]<4 for n in (ARMS[4],ARMS[5],ARMS[6],ARMS[7])):
            raise ValueError("No actual complete double-ACK 4-state belief")
        for name in ARMS[1:]:
            steps=[z.get("step") for z in row.get("faults",{}).get(name,[])]
            if steps not in ([2],[2,3]) or (name!=ARMS[3] and steps!=[2,3]):
                raise ValueError("Missing actual two native arm command holds")
        decisions=row.get("proactive_authority_slack_decisions",{})
        if PROACTIVE in decisions:
            d=decisions[PROACTIVE]
            if (d.get("step")!=4 or d.get("uses_private_target_before_decision") is not False
                or d.get("was_common_action_authorized") not in (True,False)
                or type(d.get("queried_before_action")) is not bool):
                raise ValueError("Untrusted prospective timing or target provenance")
            risk=d.get("normalized_authority_risk")
            if (not isinstance(risk,(int,float)) or risk<0
                or d["queried_before_action"]!=(
                  not d["was_common_action_authorized"] or risk>=.75)):
                raise ValueError("Proactive readback evidence inconsistent with frozen query gate")
        phase_decisions=row.get("phase_information_prequery_decisions",{})
        if PHASE in phase_decisions:
            d=phase_decisions[PHASE]
            value=float(d.get("normalized_authority_ratio"))
            if d.get("step")!=4 or d.get("private_target_was_read_before_decision") is not False:
                raise ValueError("Phase decision used private target before selection")
            correct=(not d["was_common_action_authorized"] or
                     (task=="stack_cube") or value<.75)
            if type(d.get("queried")) is not bool or d["queried"]!=correct:
                raise ValueError("Frozen task-phase query contract violated")
        for name,a in row.get("certified_action_masked_by_injected_fault",{}).items():
            for v in a:
                masked+=1
                if (v["step"] not in (2,3)
                    or v["native_action_did_not_execute"] is not True
                    or v["claimed_physical_setpoint_certificate"] is not False):
                    raise ValueError("Fault-masked action falsely counted as executed")
        for name,a in row.get("robust_native_target_bound_checks",{}).items():
            for v in a:
                physical+=1
                if (v["step"] in (2,3)
                    or v["only_audit_after_physical_dispatch"] is not True
                    or v["position_error_m"]>v["worst_case_position_limit_m"]+1e-4+1e-10
                    or v["rot_error_rad"]>v["worst_case_rot_limit_rad"]+1e-4+1e-10):
                    raise ValueError("Actual simulated native target left certified residual envelope")
        chosen=ROUTE[task]
        per_seed.append({
           "task":task,"seed":row["seed"],
           "proactive_success":int(flags[PROACTIVE]),
           "proactive_read_count":q[PROACTIVE],
           "phase_success":int(flags[PHASE]),
           "phase_read_count":q[PHASE],
           "phase_prequery_decision":phase_decisions.get(PHASE),
           "prior_task_gated_success":int(flags[chosen]),
           "prior_task_gated_read_count":q[chosen],
           "fixed_success":int(flags[FIXED]),"fixed_read_count":q[FIXED],
           "reactive_success":int(flags[SELECTIVE]),"reactive_read_count":q[SELECTIVE],
           "proactive_prequery_decision":decisions.get(PROACTIVE),
        })
    if successes!=record.get("success_counts"):
        raise ValueError("Original task count differs from actually stepped trial outcomes")
    return {"task":task,"chunk":chunk,"source_seeds":list(seeds),
            "official_8_arm_success":successes,"decision_reads":reads,
            "after_actual_dispatch_checks":physical,
            "deliberately_masked_commands_excluded":masked,
            "per_seed_full_real_native_outcomes":per_seed}

def self_test():
    assert len({(t,s) for t in TASKS for c in (0,) for s in group(t,c)})==16
    for t,c in (("bad",0),("pull_cube",4),("stack_cube",-1),("pull_cube",True)):
        try:group(t,c)
        except ValueError:pass
        else:raise AssertionError("Unregistered cohort incorrectly accepted")
    print("PASS pre-committed 64 fresh native simulator states, no overlap")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=TASKS,default="pull_cube")
    p.add_argument("--chunk",type=int,default=0)
    p.add_argument("--out",type=Path,default=Path("authority_slack_originals"))
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    self_test()
    if a.self_test:return
    source=frozen_source()
    seeds=group(a.task,a.chunk)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    mod=importlib.import_module("frozen_ppo_fixed_resync_corrected")
    if (mod.TASK!=a.task or mod.FAULT_STEPS!=(2,3)
        or mod.POS_BUDGET!=.05 or mod.ROT_BUDGET!=.05
        or mod.HORIZON!=50 or tuple(mod.NAMES)!=ARMS):
        raise ValueError("Changed native fault/controller chart against preoutcome rule")
    mod.SEEDS=seeds
    mod.COHORT[a.task]=(TASKS[a.task][0],seeds)
    mod.main()  # genuinely step 8 matched controller worlds on 8 original seeds
    f=Path(f"fixed_resync_{a.task}_original8.json")
    original=f.read_bytes()
    report=summarize(json.loads(original),a.task,a.chunk,seeds)
    a.out.mkdir(parents=True,exist_ok=True)
    dest=a.out/f"fixed_resync_{a.task}_chunk{a.chunk}_original8.json"
    dest.write_bytes(original)
    report.update({"true_original_physx_sha256":hashlib.sha256(original).hexdigest(),
                  "frozen_source_git_blobs":source,
                  "preoutcome_protocol":PROTOCOL})
    (a.out/"summary.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("POST_READBACK_SINGLETON_NATIVE_PHYSX",json.dumps({
      "task":a.task,"chunk":a.chunk,"proactive_success":report["official_8_arm_success"][PROACTIVE],
      "task_gated_success":sum(z["prior_task_gated_success"] for z in report["per_seed_full_real_native_outcomes"]),
      "phase_success":report["official_8_arm_success"][PHASE],
      "phase_reads":report["decision_reads"][PHASE],
      "proactive_reads":report["decision_reads"][PROACTIVE],
      "fixed_success":report["official_8_arm_success"][FIXED],
      "physical_checks":report["after_actual_dispatch_checks"]
    },sort_keys=True))

if __name__=="__main__":main()
