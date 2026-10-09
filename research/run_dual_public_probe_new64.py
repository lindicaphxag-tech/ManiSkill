"""Only frozen-native PhysX execution runner. No posthoc outcome filtering."""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
FIRST={"pull_cube":900001,"stack_cube":910001}
PREREG="research/SEQUENTIAL_TWO_PUBLIC_PROBES_NEW64_PREOUTCOME_V1.json"
PREREG_BLOB="2998c9312210a2c7b20d3d257153c9c08783032f"
PHYSX_SRC="research/frozen_ppo_dual_public_neutral_physx_v5.py"
PHYSX_BLOB="fa7b5cbe15fa4406ffeeb3fd4a60e11d2bd35836"
OLD_CONTROLLER_BLOB="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
PPO_SHA={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
         "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
SINGLE="fault_public_single_t4_or_t6_query"
DOUBLE="fault_public_two_t4t5_or_t6_query"
STRONG={"pull_cube":"fault_robust_then_single_privileged_query",
        "stack_cube":"fault_always_single_privileged_query"}
def blob(file):
    return subprocess.check_output(["git","hash-object",str(file)],text=True).strip()
def seed_bank(task,chunk):
    if task not in TASKS or type(chunk) is not int or chunk not in range(4):
        raise ValueError("Unregistered task or chunk")
    return list(range(FIRST[task]+8*chunk,FIRST[task]+8*chunk+8))
def verify_source():
    if blob(PREREG)!=PREREG_BLOB or blob(PHYSX_SRC)!=PHYSX_BLOB or blob("research/frozen_ppo_compound_ack_multi_belief.py")!=OLD_CONTROLLER_BLOB:
        raise ValueError("SOURCE DRIFT: original before-outcome study is invalid")
    p=json.loads(Path(PREREG).read_text())
    if p["schema"]!="prospective_dual_public_probe_true_four_joint_ACK_PPO_new64_v1":
        raise ValueError("Wrong source fixed preregistration")
def main():
    args=argparse.ArgumentParser()
    args.add_argument("--task",choices=tuple(TASKS),required=True)
    args.add_argument("--chunk",type=int,choices=range(4),required=True)
    v=args.parse_args()
    verify_source()
    seed=seed_bank(v.task,v.chunk)
    os.environ["ABI_TASK"]=v.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    model=importlib.import_module("frozen_ppo_dual_public_neutral_physx_v5")
    if (model.TASK!=v.task or model.TASK_NAME!=TASKS[v.task]
        or model.FAULT_STEPS!=(2,3) or model.HORIZON!=50
        or model.POS_BUDGET!=.05 or model.ROT_BUDGET!=.05
        or model.PUBLIC_ARM!=DOUBLE or model.SINGLE_ARM!=SINGLE
        or model.PROTO!=PREREG or len(model.NAMES)!=10):
        raise ValueError("Changed model/task/native action contract")
    model.SEEDS=seed
    model.COHORT[v.task]=(TASKS[v.task],seed)
    model.main()  # all ten paired original REAL native PhysX controllers run
    original=Path(f"dual_public_ack_{v.task}_original8.json")
    data=original.read_bytes()
    d=json.loads(data)
    if (d.get("schema")!="frozen_ppo_full_joint_dual_public_neutral_t4t5_physx_v5"
        or d.get("task")!=TASKS[v.task]
        or d.get("original_seed_population")!=seed
        or d.get("original_external_frozen_checkpoint_sha256")!=PPO_SHA[v.task]
        or len(d.get("episodes",[]))!=8 or len(d.get("all_ten_actual_control_arms",[]))!=10
        or d.get("real_physx_simulator") is not True):
        raise ValueError("Physically executed source artifact is invalid; retain bytes for independent analysis")
    source_id=dict(schema="original_dual_public_physx_source_shard_v1",
                   task=v.task,chunk=v.chunk,seeds=seed,original_sha256=hashlib.sha256(data).hexdigest(),
                   executed_method_git_blob=PHYSX_BLOB,preoutcome_protocol_git_blob=PREREG_BLOB,
                   original_genuine_physics_worlds=80,
                   actual_physx_data_written_before_source_sha_check=True,
                   no_test_seed_refitting_or_prestated_positive_outcome=True)
    Path(f"dual_public_ack_{v.task}_chunk{v.chunk}_manifest.json").write_text(json.dumps(source_id,sort_keys=True,indent=2)+"\n")
    original.rename(f"dual_public_ack_{v.task}_chunk{v.chunk}_original8.json")
    print("ORIGINAL_DUAL_PROBE_PHYSX_SOURCE_SHARD",json.dumps(source_id,sort_keys=True),flush=True)
if __name__=="__main__":main()
