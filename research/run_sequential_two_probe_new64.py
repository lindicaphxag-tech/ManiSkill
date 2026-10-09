"""Prospective new 64 actual CPU PhysX PPO states; SAME two known-delivered
native ZERO probe steps for every non-refused controller arm, 10 actual worlds.

No retrospective seed reuse, hidden-target leakage, or outcome splicing.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path

PROTOCOL="research/SEQUENTIAL_TWO_PUBLIC_PROBES_NEW64_PREOUTCOME_V1.json"
PROTOCOL_BLOB="2998c9312210a2c7b20d3d257153c9c08783032f"
SOURCE_BLOB="cd84a9fe091d19bd198292e4f54ee0f9bfd73858"
ORIGINAL_NATIVE_BLOB="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
START={"pull_cube":900001,"stack_cube":910001}
CHECKPOINT={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
            "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
SINGLE="fault_public_t4_fourhistory_or_t6_query"
DUAL="fault_dual_t4t5_fourhistory_or_t6_query"
FIXED="fault_always_single_privileged_query"
SELECTIVE="fault_robust_then_single_privileged_query"
HELD="fault_assume_held_without_query"

def blob(p):
    return subprocess.check_output(["git","hash-object",str(p)],text=True).strip()

def check_identity():
    if blob(PROTOCOL)!=PROTOCOL_BLOB:
        raise ValueError("Changed immutable before-outcome experimental seed registration")
    if blob("research/frozen_ppo_compound_ack_multi_belief.py")!=ORIGINAL_NATIVE_BLOB:
        raise ValueError("Original native translation and PPO control baseline changed")
    if blob("research/frozen_ppo_sequential_two_public_probes_physx_v5.py")!=SOURCE_BLOB:
        raise ValueError("Original registered simultaneous physical one-vs-two probe algorithms changed")
    if json.loads(Path(PROTOCOL).read_text())["schema"]!="prospective_dual_public_probe_true_four_joint_ACK_PPO_new64_v1":
        raise ValueError("Wrong original registered prospective physical experiment")

def seeds_for(task,chunk):
    if task not in TASKS or type(chunk) is not int or not 0<=chunk<4:
        raise ValueError("Expected exact task and 0..3 original physical shard")
    start=START[task]+8*chunk
    return list(range(start,start+8))

def validate_source(data,task,seeds):
    if (data.get("schema")!="frozen_ppo_dual_public_sequential_neutral_t4t5_v5" or
        data.get("original_seed_population")!=seeds or
        data.get("task")!=TASKS[task] or
        data.get("preoutcome_protocol")!=PROTOCOL or
        data.get("original_external_frozen_checkpoint_sha256")!=CHECKPOINT[task] or
        data.get("frozen_model_retrained") is not False or
        data.get("real_physx_simulator") is not True or
        len(data.get("episodes",[]))!=8):
        raise ValueError("Original physical PPO source not fully executed")
    names=data["all_ten_actual_control_arms"]
    if len(names)!=10 or len(set(names))!=10 or names[-2:]!=[SINGLE,DUAL]:
        raise ValueError("Missing actual ten source and task-control worlds")
    outputs=[]
    gate=SELECTIVE if task=="pull_cube" else FIXED
    totals={a:{"success":0,"reads":0} for a in (SINGLE,DUAL,FIXED,gate,HELD)}
    for seed,row in zip(seeds,data["episodes"]):
        if (row["seed"]!=seed or
            row["original_precommitted_physical_t2_execution_truth"]!=("applied" if seed%2==0 else "held") or
            row["original_precommitted_physical_t3_execution_truth"]!=("applied" if (seed//2)%2==0 else "held")):
            raise ValueError("Source seed/physical truth manipulated")
        success=row["success_once"];reads=row["privileged_target_readback_decision_count"]
        if set(success)!=set(names) or set(reads)!=set(names):
            raise ValueError("Missing real controller task evidence")
        for m in names:
            if type(success[m]) is not bool or type(reads[m]) is not int:
                raise ValueError("Not physical boolean success or integer query ledger")
            if m=="fault_oracle_private_target":
                if reads[m]!=-1: raise ValueError("Oracle getter improperly represented")
            elif reads[m] not in (0,1):
                raise ValueError("Unregistered repeated or omitted private reads")
        truth=[seed%2==0,(seed//2)%2==0]
        for m in (SINGLE,DUAL,FIXED,HELD,gate):
            faults=row["faults"].get(m,[])
            if [f.get("step") for f in faults]!=[2,3] or any(
                f.get("controller_execution_ack_seen_by_adapter")!="unknown"
                for f in faults):
                raise ValueError("Incomplete double native-ACK physical fault")
            for f,applied in zip(faults,truth):
                reported=f.get("actual_native_execution_truth" if m==FIXED and f["step"]==3
                               else "actual_native_precommitted_execution_truth")
                if reported!=("applied" if applied else "held"):
                    raise ValueError("Actually executed ACK truth mismatches seed prereg")
            probes=row["known_delivered_zero_probes"].get(m,[])
            if len(probes)!=2 or [p["step"] for p in probes]!=[4,5] or any(
                p.get("actual_native_6d_dispatched")!=[0.]*6 or
                p.get("acknowledgement")!="known_applied" or
                p.get("audit_only_target_unchanged") is not True for p in probes):
                raise ValueError("Unequal extra physical probe actuation cost")
        ev=row["public_motion_evidence"]
        if set(ev)!={SINGLE,DUAL}:
            raise ValueError("Must physically observe separate one vs dual algorithms")
        for m,number in ((SINGLE,1),(DUAL,2)):
            x=ev[m]
            if len(x["probes"])!=number or len(x.get("audit_only_hidden_target_errors",[]))!=4:
                raise ValueError("Incomplete physical public response observations")
            if [z["step"] for z in x["probes"]] != [4]+([5] if number==2 else []):
                raise ValueError("Wrong neutral observation schedule")
            if row["public_motion_observation_cost_samples"][m]!=2*number:
                raise ValueError("Uncounted public observation cost")
            if x.get("hidden_target_was_audit_only_NOT_decision_input") is not True:
                raise ValueError("Auditor target illegally used to decide")
            epsilon=x["probes"][0]["frozen_epsilon_m"]
            pred=[i for i in range(4)
                  if all(v["candidate_residuals_m"][i]<=epsilon+1e-12 for v in x["probes"])]
            authorized=bool(len(pred)==1 and all(
                any(v["candidate_residuals_m"][j]>epsilon+.002 for v in x["probes"])
                for j in range(4) if j!=pred[0]))
            if authorized is not x.get("authorized") or pred!=x.get("compatible_indices"):
                raise ValueError("Original method outcome not traceable to PUBLIC observations")
            real=[i for i,(pos,rot) in enumerate(x["audit_only_hidden_target_errors"])
                  if pos<=1e-4 and rot<=1e-3]
            wrong=bool(authorized and pred[0] not in real)
            if wrong is not x.get("wrong_confident"):
                raise ValueError("Wrong-confident scorer cannot independently reproduce")
            if x.get("resync_source")=="empirical_public_achieved_motion":
                if not authorized or reads[m]!=0:
                    raise ValueError("Method falsely claimed read-free recovery")
            elif x.get("resync_source")=="one_counted_authoritative_controller_target_read":
                if authorized or reads[m]!=1:
                    raise ValueError("Authoritative read not charged")
            elif x.get("resync_source") is not None or reads[m]!=0:
                raise ValueError("Unregistered control evidence source")
        for m in totals:
            totals[m]["success"]+=int(success[m])
            totals[m]["reads"]+=reads[m]
        outputs.append({"seed":seed,"task":task,"combo":("A" if truth[0] else "H")+("A" if truth[1] else "H"),
            "one_success":success[SINGLE],"two_success":success[DUAL],
            "gate_success":success[gate],"fixed_success":success[FIXED],
            "held_success":success[HELD],
            "one_reads":reads[SINGLE],"two_reads":reads[DUAL],
            "gate_reads":reads[gate],"fixed_reads":reads[FIXED],
            "one_confident":ev[SINGLE]["authorized"],"two_confident":ev[DUAL]["authorized"],
            "one_wrong":ev[SINGLE]["wrong_confident"],"two_wrong":ev[DUAL]["wrong_confident"],
            "one_public_samples":2,"two_public_samples":4})
    return {"schema":"prospective_sequential_two_probes_physx_shard_audit_v1",
            "task":task,"original_seed_population":seeds,"summary":totals,
            "original_task_rows":outputs,"source_protocol_git_blob":PROTOCOL_BLOB,
            "original_native_model_checkpoint_hash":CHECKPOINT[task],
            "real_natively_stepped_control_worlds":80,
            "all_original_physical_source_failures_preserved":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS),required=True)
    p.add_argument("--chunk",type=int,choices=range(4),required=True)
    a=p.parse_args()
    check_identity()
    seeds=seeds_for(a.task,a.chunk)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_sequential_two_public_probes_physx_v5")
    if (runner.TASK!=a.task or list(runner.FAULT_STEPS)!=[2,3] or
        runner.POS_BUDGET!=.05 or runner.ROT_BUDGET!=.05 or
        runner.SINGLE_ARM!=SINGLE or runner.PUBLIC_ARM!=DUAL or
        runner.PROTO!=PROTOCOL or len(runner.NAMES)!=10):
        raise RuntimeError("Original registered native action or selected policy changed")
    runner.SEEDS=seeds
    runner.COHORT[a.task]=(TASKS[a.task],seeds)
    runner.main() # ORIGINAL 10 simulator controller worlds for each seed.
    original=Path(f"sequential_two_probes_{a.task}_original8.json")
    raw=original.read_bytes()
    d=json.loads(raw)
    audit=validate_source(d,a.task,seeds)
    audit["actual_source_blob"]=SOURCE_BLOB
    audit["original_raw_sha256"]=hashlib.sha256(raw).hexdigest()
    (Path(f"sequential_two_probes_{a.task}_chunk{a.chunk}_audit.json")).write_text(
        json.dumps(audit,indent=2,sort_keys=True)+"\n")
    original.rename(f"sequential_two_probes_{a.task}_chunk{a.chunk}_original8.json")
    print("ACTUAL_SOURCE_PHYSX_DUAL_V_SINGLE",json.dumps({
        "task":a.task,"chunk":a.chunk,"totals":audit["summary"],
        "one_wrong":sum(r["one_wrong"] for r in audit["original_task_rows"]),
        "two_wrong":sum(r["two_wrong"] for r in audit["original_task_rows"])},
        sort_keys=True),flush=True)
if __name__=="__main__":main()
