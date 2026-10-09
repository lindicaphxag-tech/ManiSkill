"""Genuine independently operator-owned PhysX new-seed replication; NEVER a self-lab claim.

On OWN fork checked out at our SOURCE-frozen research head:
    python research/outside_dual_public_probe_replication.py --task stack_cube --first-seed 940001

Before running any physics, write operator and exact 8 NEW seeds. Physically
step ten actual native controllers per state. Do not replace actual steps
with historical replay, do not refit a model, preserve ALL original failures.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path
FROZEN_METHOD="research/frozen_ppo_dual_public_neutral_physx_v5.py"
SOURCE_BLOB="fa7b5cbe15fa4406ffeeb3fd4a60e11d2bd35836"
BASE_BLOB="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
PROTO="research/SEQUENTIAL_TWO_PUBLIC_PROBES_NEW64_PREOUTCOME_V1.json"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
ONE="fault_public_single_t4_or_t6_query"
TWO="fault_public_two_t4t5_or_t6_query"
STRONG={"pull_cube":"fault_robust_then_single_privileged_query",
        "stack_cube":"fault_always_single_privileged_query"}
def commit(file):
    return subprocess.check_output(["git","hash-object",file],text=True).strip()
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS),required=True)
    p.add_argument("--first-seed",type=int,required=True)
    p.add_argument("--out",type=Path,default=Path("outside_real_dual_public_probe"))
    a=p.parse_args()
    if not 940001<=a.first_seed<=999992:
        raise ValueError("Choose an independently declared NEW first seed in 940001..999992")
    seeds=list(range(a.first_seed,a.first_seed+8))
    if commit(FROZEN_METHOD)!=SOURCE_BLOB or commit("research/frozen_ppo_compound_ack_multi_belief.py")!=BASE_BLOB:
        raise ValueError("Original method changed; independent comparison invalid")
    a.out.mkdir(exist_ok=True,parents=True)
    repo=os.environ.get("GITHUB_REPOSITORY","local-unattested")
    actor=os.environ.get("GITHUB_ACTOR","local-unattested")
    prereg=dict(actual_operator_repository=repo,github_actor=actor,
       author_owned_execution_NOT_independent=repo in ("local-unattested","lindicaphxag-tech/ManiSkill"),
       chosen_exactly_eight_seed_ids_BEFORE_simulation=seeds,task=a.task,
       source_native_PhysX_model_Git_blob=SOURCE_BLOB,
       no_checkpoint_retraining_or_fitted_parameters_changed=True,
       both_physical_ACK_events_balanced_by_declared_modulo_truth=True,
       independent_outside_lab_acceptance_NOT_assumed=True)
    (a.out/"BEFORE_PHYSICS_OPERATOR_SEED_IDENTITY.json").write_text(
        json.dumps(prereg,sort_keys=True,indent=2)+"\n")
    print("PRE_PHYSICS_OUTSIDE_FORK_DECLARATION",json.dumps(prereg,sort_keys=True),flush=True)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_dual_public_neutral_physx_v5")
    if runner.PUBLIC_ARM!=TWO or runner.SINGLE_ARM!=ONE or runner.TASK!=a.task or runner.FAULT_STEPS!=(2,3) or len(runner.NAMES)!=10 or runner.PROTO!=PROTO:
        raise ValueError("Unexpected native physics ABI or method/source")
    runner.SEEDS=seeds
    runner.COHORT[a.task]=(TASKS[a.task],seeds)
    runner.main()  # EVERY one of 80 ten-controller PhysX worlds ACTUALLY stepped
    orig=Path(f"dual_public_ack_{a.task}_original8.json")
    data=orig.read_bytes(); j=json.loads(data)
    if len(j["episodes"])!=8 or j["original_seed_population"]!=seeds or j["real_physx_simulator"] is not True:
        raise ValueError("No complete original physical worlds; retain original if invalid")
    each=[]
    for row in j["episodes"]:
        if [x.get("step") for x in row.get("faults",{}).get(TWO,[])]!=[2,3]:
            raise ValueError("A planned ACK physical intervention not reached")
        each.append(dict(seed=row["seed"],
           t2_truth=row["original_precommitted_physical_t2_execution_truth"],
           t3_truth=row["original_precommitted_physical_t3_execution_truth"],
           two_probes_success=row["success_once"][TWO],two_probes_reads=row["privileged_target_readback_decision_count"][TWO],
           one_probe_success=row["success_once"][ONE],one_probe_reads=row["privileged_target_readback_decision_count"][ONE],
           task_gated_success=row["success_once"][STRONG[a.task]],
           task_gated_reads=row["privileged_target_readback_decision_count"][STRONG[a.task]],
           two_probes_wrong_confident=row["public_t4_evidence"].get("wrong_confident"),
           one_probe_wrong_confident=row["public_t4_single_evidence"].get("wrong_confident"),
           physically_executed_neutral_probe_steps=list(row["known_delivered_zero_probe"].get(TWO,{})),
           two_extra_public_samples=row["public_motion_observation_cost_samples"][TWO]))
    (a.out/"OUTSIDE_SOURCE_DETERMINED_PAIRED_ORIGINAL_EIGHT.json").write_text(
         json.dumps(dict(operator=prereg,source_sha256=hashlib.sha256(data).hexdigest(),
           actual_native_controller_worlds=80,per_original_state=each,
           never_real_hardware_or_network_loss=True),indent=2,sort_keys=True)+"\n")
    orig.rename(a.out/orig.name)
    print("INDEPENDENT_OPERATOR_REAL_PHYSX_80_SOURCED_WORLDS",json.dumps(each,sort_keys=True),flush=True)
if __name__=="__main__":main()
