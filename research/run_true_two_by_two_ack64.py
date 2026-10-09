"""True 2x2 physical execution truth; independently check all eight source trials.

Registration predates this source. Two unknown ACKs at t2/t3; t3 native
NONZERO pulse (0.4 axis0) has a physical effect when applied; known neutral
t4 observation costs one real native step for each faulted comparator.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path

REG="research/TWO_BY_TWO_REAL_NONZERO_ACK64_PREREG_V1.json"
REG_BLOB="9209ecbfb8129e15de9ffc7441e8a196f53acaf4"
PHYSICS_RUNNER="research/frozen_ppo_true_double_nonzero_ack_physx.py"
PHYSICS_BLOB="6188853f918bd338b289d771ebdd4d4c037e0a77"
CLASSIFIER_BLOB="064bb46831b61af73ad445bc836326837ec5468f"
TASK={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
START={"pull_cube":1340001,"stack_cube":1350001}
PUBLIC="fault_public_t3_fourhistory_or_t4_query"
FIXED="fault_always_single_privileged_query"
SELECTIVE="fault_robust_then_single_privileged_query"
HELD="fault_assume_held_without_query"
ARMS=("source_no_fault","fault_oracle_private_target",
      "fault_optimistic_unverified_ack","fault_strict_common_exact",
      "fault_robust_two_history_without_query",SELECTIVE,FIXED,HELD,PUBLIC)
CHECKPOINTS={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
            "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}

def gitblob(path):
    return subprocess.check_output(("git","hash-object",path),text=True).strip()

def frozen_sources():
    for path,sha in ((REG,REG_BLOB),(PHYSICS_RUNNER,PHYSICS_BLOB),
                     ("research/empirical_probe_response_classifier.py",CLASSIFIER_BLOB)):
        if gitblob(path)!=sha:
            raise ValueError("Frozen pre-outcome physical protocol or classifier changed: "+path)
    p=json.loads(Path(REG).read_text())
    assert p["n_reset_states"]==64 and p["planned_actual_native_physx_worlds"]==576

def seeds(task,chunk):
    if task not in TASK or type(chunk) is not int or not 0<=chunk<4:
        raise ValueError("Only two PPO tasks x four original eight-seed shards")
    first=START[task]+8*chunk
    return list(range(first,first+8))

def actual_truth(seed,step):
    if step==2:return seed%4 in (2,3)
    if step==3:return seed%4 in (1,3)
    raise ValueError("ACK truth only at t2/t3")

def audit_eight(record,task,chunk):
    pop=seeds(task,chunk)
    if not (record.get("schema")=="true_two_by_two_nonzero_second_ack_physx_v1"
            and record.get("original_seed_population")==pop
            and record.get("task")==TASK[task]
            and record.get("frozen_model_retrained") is False
            and record.get("real_physx_simulator") is True
            and record.get("all_nine_actual_control_arms")==list(ARMS)
            and record.get("original_external_frozen_checkpoint_sha256")==CHECKPOINTS[task]
            and record.get("neutral_observation_step")==4
            and record.get("controller_read_step")==5
            and record.get("second_pulse_native_action")==[.4,0.,0.,0.,0.,0.]
            and record.get("frozen_protocol")==REG):
        raise ValueError("Missing complete source native controller/4-pattern evidence")
    episodes=record.get("episodes",[])
    if len(episodes)!=8 or [x.get("seed") for x in episodes]!=pop:
        raise ValueError("Original physical denominator missing or re-ordered")
    totals={name:{"success":0,"reads":0} for name in ARMS}
    unique=wrong=full=neutral=0
    rows=[]
    for row in episodes:
        seed=row["seed"]
        t2,t3=actual_truth(seed,2),actual_truth(seed,3)
        if row.get("original_precommitted_physical_t2_execution_truth")!=("applied" if t2 else "held") or row.get("original_precommitted_physical_t3_execution_truth")!=("applied" if t3 else "held"):
            raise ValueError("Non-four-truth physical event ledger")
        successes,reads=row.get("success_once",{}),row.get("privileged_target_readback_decision_count",{})
        if set(successes)!=set(ARMS) or set(reads)!=set(ARMS):
            raise ValueError("Missing any original physical paired outcome")
        for name in ARMS:
            if type(successes[name]) is not bool or type(reads[name]) is not int:
                raise ValueError("Fabricated success or hidden target reads")
            if name=="fault_oracle_private_target":
                if reads[name]!=-1:raise ValueError("Oracle unlimited private getter not marked")
            elif not 0<=reads[name]<=1:
                raise ValueError("Unaccounted private target getter")
            totals[name]["success"]+=int(successes[name])
            totals[name]["reads"]+=max(0,reads[name])
        for name in (PUBLIC,FIXED,HELD):
            real=row.get("faults",{}).get(name,[])
            if len(real)!=2 or [e.get("step") for e in real]!=[2,3]:
                raise ValueError("One of two ACTUAL physical interventions missing")
            for step,entry in ((2,real[0]),(3,real[1])):
                expected=actual_truth(seed,step)
                if entry.get("actual_native_action_is_precommitted_applied") is not expected:
                    raise ValueError("Source physical applied/held truth mislabeled")
                native=entry.get("actual_native_6d_dispatched",[])
                if len(native)!=6:raise ValueError("Native physical 6D action missing")
                if step==3:
                    valid=[.4,0.,0.,0.,0.,0.] if expected else [0.]*6
                    if any(abs(float(x)-v)>1e-6 for x,v in zip(native,valid)):
                        raise ValueError("Declared nonzero second applied event NOT physically dispatched")
                    dp=float(entry.get("audit_only_after_real_step_target_delta_inf_m",0))
                    dr=float(entry.get("audit_only_after_real_step_target_rot_change_rad",0))
                    if expected and max(dp,dr)<=1e-4:
                        raise ValueError("A claimed second APPLIED native pulse did not change physical target")
                    if not expected and (dp>1e-4 or dr>1e-4):
                        raise ValueError("A claimed second HELD target actually changed")
            paid=row.get("paid_neutral_control_actions",{}).get(name,[])
            if len(paid)!=1 or paid[0].get("step")!=4 or paid[0].get("replaced_one_policy_action") is not True or any(abs(q)>1e-7 for q in paid[0].get("native_6d",[])):
                raise ValueError("t4 known-delivered neutral physically paid step is missing")
            neutral+=1
        ev=row.get("public_t4_neutral_evidence",{})
        if len(ev.get("candidate_residuals_m",[])) not in (1,2,3,4):
            raise ValueError("No public-t4 full-target history population")
        if type(ev.get("authorized")) is not bool or type(ev.get("wrong_confident")) is not bool:
            raise ValueError("Public confidence and truth audit must be explicit")
        if ev["authorized"] and reads[PUBLIC]!=0:
            raise ValueError("Public confident branch illegally billed/used a private read")
        if not ev["authorized"] and ev.get("resync_source")=="one_counted_authoritative_controller_target_read" and reads[PUBLIC]!=1:
            raise ValueError("Fallback t5 private read not actually billed")
        unique+=int(ev["authorized"]);wrong+=int(ev["wrong_confident"])
        full+=1
        rows.append({"task":task,"seed":seed,
                     "physical_t2_applied":t2,"physical_t3_applied":t3,
                     "public_task_success":successes[PUBLIC],
                     "strong_task_success":successes[SELECTIVE if task=="pull_cube" else FIXED],
                     "fixed_t5_success":successes[FIXED],
                     "assume_held_success":successes[HELD],
                     "public_private_reads":reads[PUBLIC],
                     "strong_private_reads":reads[SELECTIVE if task=="pull_cube" else FIXED],
                     "fixed_private_reads":reads[FIXED],
                     "public_unique":ev["authorized"],
                     "wrong_confident":ev["wrong_confident"],
                     "source_physical_faults":row.get("faults",{}).get(PUBLIC,[]),
                     "source_paid_neutral":row.get("paid_neutral_control_actions",{}).get(PUBLIC,[])})
    if record.get("success_counts")!={n:totals[n]["success"] for n in ARMS}:
        raise ValueError("Original raw physics source task success count inconsistent")
    if full!=8 or neutral<24:raise ValueError("No eight actual complete four-truth physical episodes")
    return {"task":task,"chunk":chunk,"seeds":pop,"real_native_controller_worlds":72,
            "task_success_by_arm":totals,"per_original_reset":rows,
            "public_confident":unique,"wrong_confident":wrong,
            "charged_known_neutral_control_steps":neutral,
            "true_two_by_two_faults_physically_verified":True}

def main():
    p=argparse.ArgumentParser();p.add_argument("--task",choices=tuple(TASK),required=True)
    p.add_argument("--chunk",type=int,choices=range(4),required=True);a=p.parse_args()
    frozen_sources()
    pop=seeds(a.task,a.chunk)
    os.environ["ABI_TASK"]=a.task
    m=importlib.import_module("research.frozen_ppo_true_double_nonzero_ack_physx")
    if tuple(m.FAULT_STEPS)!=(2,3) or m.NEUTRAL_PROBE_STEP!=4 or m.READBACK_STEP!=5 or len(m.NAMES)!=9:
        raise RuntimeError("New physically nonzero second ACK runner contract mutated")
    m.SEEDS=pop
    m.COHORT[a.task]=(TASK[a.task],pop)
    m.main()
    raw=Path(f"true_double_{a.task}_original8.json")
    result=audit_eight(json.loads(raw.read_text()),a.task,a.chunk)
    result.update(schema="actual_true_two_by_two_physx_shard_audit_v1",
                  exact_original_physics_source_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                  source_native_runner_blob=PHYSICS_BLOB,prereg_blob=REG_BLOB)
    raw.rename(f"true_double_{a.task}_chunk{a.chunk}_original8.json")
    Path(f"true_double_{a.task}_chunk{a.chunk}_audit.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PHYSICALLY_TRUE_TWO_BY_TWO_ACK_SHARD",json.dumps({
        "task":a.task,"chunk":a.chunk,"new_success":result["task_success_by_arm"][PUBLIC]["success"],
        "new_private_reads":result["task_success_by_arm"][PUBLIC]["reads"],
        "confident":result["public_confident"],"wrong_confident":result["wrong_confident"]},sort_keys=True))

if __name__=="__main__":main()
