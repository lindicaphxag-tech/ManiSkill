"""External researcher fork, eight NEW TRUE 2x2 nonzero ACK native PPO PhysX trials.

This executable entry does not claim outside reproduction: only a genuinely
independent person running their own fork/new original reset seeds and publishing
all source successes/failures can establish it. Source physics unchanged and
pinned to exact preregistered experiment.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path
SRC="research/frozen_ppo_true_double_nonzero_ack_physx.py"
SOURCE_BLOB="6188853f918bd338b289d771ebdd4d4c037e0a77"
PRE_REG="research/TWO_BY_TWO_REAL_NONZERO_ACK64_PREREG_V1.json"
REGISTERED_BLOB="9209ecbfb8129e15de9ffc7441e8a196f53acaf4"
PUBLIC="fault_public_t3_fourhistory_or_t4_query"
FIXED="fault_always_single_privileged_query"
SELECTIVE="fault_robust_then_single_privileged_query"
HELD="fault_assume_held_without_query"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}

def select(task,first_seed):
    if task not in TASKS or type(first_seed) is not int or not 1600000<=first_seed<=9999992:
        raise ValueError("Choose supported task and eight independently unused consecutive seeds between 1600000 and 9999999")
    return list(range(first_seed,first_seed+8))

def check(path,expected):
    return subprocess.check_output(["git","hash-object",path],text=True).strip()==expected

def audit(raw,task,seeds):
    r=json.loads(raw)
    if not (r.get("schema")=="true_two_by_two_nonzero_second_ack_physx_v1"
            and r.get("original_seed_population")==seeds
            and r.get("all_nine_actual_control_arms")==[
                "source_no_fault","fault_oracle_private_target",
                "fault_optimistic_unverified_ack","fault_strict_common_exact",
                "fault_robust_two_history_without_query",SELECTIVE,FIXED,HELD,PUBLIC]
            and r.get("real_physx_simulator") is True
            and r.get("frozen_model_retrained") is False
            and r.get("second_pulse_native_action")==[.4,0.,0.,0.,0.,0.]
            and r.get("neutral_observation_step")==4
            and r.get("controller_read_step")==5
            and r.get("frozen_protocol")==PRE_REG
            and len(r.get("episodes",[]))==8):
        raise ValueError("Missing native original source/physics/neutral-charge contract")
    pop={"n":8,"physically_stepped_worlds":72,
         "new_success":0,"strong_success":0,"fixed_success":0,
         "new_private_reads":0,"strong_private_reads":0,"fixed_private_reads":0,
         "confident_public":0,"wrong_confident":0,"physical_truth_pattern_counts":{},
         "original_per_episode":[]}
    strong=SELECTIVE if task=="pull_cube" else FIXED
    for row,seed in zip(r["episodes"],seeds):
        if row["seed"]!=seed:raise ValueError("Dropped/repeated original reset seed")
        t2=seed%4 in (2,3);t3=seed%4 in (1,3)
        truth=f"t2_{'A' if t2 else 'H'}_t3_{'A' if t3 else 'H'}"
        pop["physical_truth_pattern_counts"][truth]=pop["physical_truth_pattern_counts"].get(truth,0)+1
        if row.get("original_precommitted_physical_t2_execution_truth")!=("applied" if t2 else "held") or row.get("original_precommitted_physical_t3_execution_truth")!=("applied" if t3 else "held"):
            raise ValueError("Incorrect actual execution-truth state provenance")
        faults=row.get("faults",{}).get(PUBLIC,[])
        if len(faults)!=2 or [e["step"] for e in faults]!=[2,3]:
            raise ValueError("At least one ACTUAL physical ACK event was not exposed")
        step3=faults[1]
        if step3.get("actual_native_action_is_precommitted_applied") is not t3:
            raise ValueError("Fabricated physical second ACK truth")
        pulse=step3.get("actual_native_6d_dispatched",[])
        expected=[.4,0,0,0,0,0] if t3 else [0]*6
        if len(pulse)!=6 or any(abs(float(x)-y)>1e-6 for x,y in zip(pulse,expected)):
            raise ValueError("The second commanded increment is NOT the declared nonzero real one")
        pos=float(step3.get("audit_only_after_real_step_target_delta_inf_m",-1))
        rot=float(step3.get("audit_only_after_real_step_target_rot_change_rad",-1))
        if (t3 and max(pos,rot)<=1e-4) or (not t3 and (pos>1e-4 or rot>1e-4)):
            raise ValueError("Claimed native controller second physical applied/held truth not observed")
        neutral=row.get("paid_neutral_control_actions",{}).get(PUBLIC,[])
        if len(neutral)!=1 or neutral[0].get("step")!=4 or len(neutral[0].get("native_6d",[]))!=6 or any(abs(float(x))>1e-7 for x in neutral[0]["native_6d"]):
            raise ValueError("Previously declared neutral physical observation not paid")
        success=row.get("success_once",{})
        reads=row.get("privileged_target_readback_decision_count",{})
        for name in (PUBLIC,strong,FIXED):
            if type(success.get(name)) is not bool or type(reads.get(name)) is not int or not 0<=reads[name]<=1:
                raise ValueError("Missing actual paired outcome/readback ledger")
        ev=row.get("public_t4_neutral_evidence",{})
        if type(ev.get("authorized")) is not bool or type(ev.get("wrong_confident")) is not bool:
            raise ValueError("Missing authentic public candidate history identification")
        if ev["authorized"] and reads[PUBLIC]!=0:
            raise ValueError("Public private-read leakage")
        pop["new_success"]+=int(success[PUBLIC])
        pop["strong_success"]+=int(success[strong])
        pop["fixed_success"]+=int(success[FIXED])
        pop["new_private_reads"]+=reads[PUBLIC]
        pop["strong_private_reads"]+=reads[strong]
        pop["fixed_private_reads"]+=reads[FIXED]
        pop["confident_public"]+=int(ev["authorized"])
        pop["wrong_confident"]+=int(ev["wrong_confident"])
        pop["original_per_episode"].append({
            "seed":seed,"physical_truth":truth,
            "new_success":success[PUBLIC],"strong_success":success[strong],
            "new_reads":reads[PUBLIC],"strong_reads":reads[strong],
            "confidence":ev["authorized"],"wrong_confident":ev["wrong_confident"]})
    if sorted(pop["physical_truth_pattern_counts"].values())!=[2,2,2,2]:
        raise ValueError("All four actually realized physical truth patterns must occur twice in outsider eight-seed block")
    return pop

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS),required=True)
    p.add_argument("--first-seed",type=int,required=True)
    p.add_argument("--output",type=Path,default=Path("outside_true_two_ack"))
    a=p.parse_args()
    chosen=select(a.task,a.first_seed)
    if not check(SRC,SOURCE_BLOB) or not check(PRE_REG,REGISTERED_BLOB):
        raise RuntimeError("Author source or pre-run registration was edited")
    a.output.mkdir(parents=True,exist_ok=True)
    owner=os.getenv("GITHUB_REPOSITORY","unknown-local")
    actor=os.getenv("GITHUB_ACTOR","unknown-local")
    before=dict(operator_repo=owner,operator_actor=actor,unseen_seeds_declared_before_physics=chosen,
                source_sha=SOURCE_BLOB,preregistration_sha=REGISTERED_BLOB,
                true_independent_operator_not_verified_by_code=True,
                author_fork_is_not_outside_reproduction=(owner=="lindicaphxag-tech/ManiSkill"),
                actual_network_packets_lost=False,actual_collision_safety_proven=False)
    (a.output/"BEFORE_PHYSICS_OPERATOR_SEED_AND_SOURCE.json").write_text(json.dumps(before,indent=2,sort_keys=True)+"\n")
    print("EXTERNAL_FOUR_TRUTH_PRE_PHYSICS",json.dumps(before,sort_keys=True),flush=True)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    mod=importlib.import_module("frozen_ppo_true_double_nonzero_ack_physx")
    if tuple(mod.FAULT_STEPS)!=(2,3) or mod.NEUTRAL_PROBE_STEP!=4 or mod.READBACK_STEP!=5 or tuple(mod.SECOND_T3_NATIVE)!=(.4,0.,0.,0.,0.,0.):
        raise RuntimeError("Native original physical fault interpreter mutated")
    mod.SEEDS=chosen
    mod.COHORT[a.task]=(TASKS[a.task],chosen)
    mod.main()
    src=Path(f"true_double_{a.task}_original8.json")
    data=src.read_bytes()
    result=audit(data.decode(),a.task,chosen)
    result.update(schema="outside_2x2_native_new_eight_source_audit_v1",
                  outside_operator_provenance=before,
                  actual_native_original_sha256=hashlib.sha256(data).hexdigest(),
                  not_external_scientist_reproduced_until_verified=True)
    (a.output/"OUTSIDE_REAL_NATIVE_FOUR_TRUTH_EIGHT_AUDIT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    src.rename(a.output/src.name)
    print("OUTSIDE_REAL_NATIVE_FOUR_TRUTH_EIGHT_AUDIT",json.dumps({k:result[k] for k in (
        "n","physically_stepped_worlds","new_success","strong_success","new_private_reads","strong_private_reads","confident_public","wrong_confident","physical_truth_pattern_counts")},sort_keys=True))

if __name__=="__main__":main()
