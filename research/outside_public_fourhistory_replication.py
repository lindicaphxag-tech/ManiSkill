"""Actual one-click outsider fork PhysX rerun of original 8-world four-history method.

Does not produce scientific independent replication unless a genuinely separate
researcher physically runs this on THEIR OWN fork, with new predeclared seed
range and shares source artifacts. No retraining or after-result tuning.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, os, subprocess, sys
from pathlib import Path

CONTROL_SHA="00945e31902f33feac21edb88f135cbdff8426ae"
BASE_SHA="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
PROTO="research/EXTERNAL_PUBLIC_FOURHISTORY_REPLICATION_V1.json"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
PUBLIC="fault_public_t3_fourhistory_or_t4_query"
TASK_GATE={"pull_cube":"fault_robust_then_single_privileged_query",
           "stack_cube":"fault_always_single_privileged_query"}

def validate(task,first):
    if task not in TASKS or type(first) is not int or not 900001<=first<=999996:
        raise ValueError("Disjoint outsider first_seed must be integer 900001..999996 and task one of two approved PPOs")
    return list(range(first,first+4))

def source_check():
    for file,sha in (("research/frozen_ppo_public_fourhistory_task_level_physx.py",CONTROL_SHA),
                     ("research/frozen_ppo_compound_ack_multi_belief.py",BASE_SHA)):
        got=subprocess.check_output(["git","hash-object",file],text=True).strip()
        if got!=sha:
            raise ValueError("Published frozen controller changed: "+file)
    if json.loads(Path(PROTO).read_text())["schema"]!="external_frozen_ppo_public_fourhistory_replication_v1":
        raise ValueError("External method contract changed")

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--task",choices=tuple(TASKS),required=True)
    arg.add_argument("--first-seed",type=int,required=True)
    arg.add_argument("--out",type=Path,default=Path("outside_public_fourhistory"))
    a=arg.parse_args()
    seeds=validate(a.task,a.first_seed)
    source_check()
    a.out.mkdir(exist_ok=True,parents=True)
    op=os.environ.get("GITHUB_REPOSITORY","unknown-local-operator")
    actor=os.environ.get("GITHUB_ACTOR","unknown-local-actor")
    evidence={"operator_repo":op,"operator_actor":actor,
              "scientifically_independent_operator":op!="lindicaphxag-tech/ManiSkill" and op!="unknown-local-operator",
              "selection_before_simulation":{"task":a.task,"seeds":seeds},
              "method_blob":CONTROL_SHA,"original_baseline_blob":BASE_SHA,
              "is_publicly_frozen_ppo":True,
              "not_actual_network_packet_loss_or_hardware_safety":True}
    (a.out/"before_physics_operator_and_seeds.json").write_text(
        json.dumps(evidence,sort_keys=True,indent=2)+"\n")
    print("BEFORE_PHYsX_INDEPENDENT_OPERATOR_DECLARATION",json.dumps(evidence),flush=True)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_public_fourhistory_task_level_physx")
    if runner.PUBLIC_ARM!=PUBLIC or tuple(runner.FAULT_STEPS)!=(2,3) or len(runner.NAMES)!=8:
        raise RuntimeError("Unapproved controller method substitution")
    runner.SEEDS=seeds
    runner.COHORT[a.task]=(TASKS[a.task],seeds)
    runner.PROTO=PROTO
    runner.main()  # physically execute 8 real native controller arms
    file=Path(f"public_fourhistory_{a.task}_original4.json")
    d=json.loads(file.read_text())
    if (d["original_seed_population"]!=seeds or d["preoutcome_protocol"]!=PROTO
        or d["real_physx_simulator"] is not True or len(d["episodes"])!=4
        or d["all_eight_actual_control_arms"]!=list(runner.NAMES)):
        raise RuntimeError("Outside physical data not exact source frozen controller experiment")
    gate=TASK_GATE[a.task]
    source={"operator":evidence,"real_original_physx_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
            "trial_summaries":[{
                "seed":r["seed"],
                "new_method_success":r["success_once"][PUBLIC],
                "new_method_privileged_reads":r["privileged_target_readback_decision_count"][PUBLIC],
                "task_gate_actual_success":r["success_once"][gate],
                "task_gate_privileged_reads":r["privileged_target_readback_decision_count"][gate],
                "public_latent_history_evidence":r.get("public_t3_evidence",{}),
                "both_actual_hold_faults_reached":len(r["faults"].get(PUBLIC,[]))==2}
                for r in d["episodes"]]}
    (a.out/"source_verified_four_actual_task_states.json").write_text(
        json.dumps(source,indent=2,sort_keys=True)+"\n")
    file.rename(a.out/file.name)
    print("OUTSIDE_AUTHOR_SELECTABLE_PHYSX_SOURCE",json.dumps(source,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
