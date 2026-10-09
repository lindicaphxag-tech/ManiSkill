"""True OUTSIDE-investigator four-truth source-frozen two-vs-one public
motion PhysX test: 8 self-chosen fresh seeds, TEN separately stepped controllers.

Being fork-able does not count as externally performed replication.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path

SOURCE="research/frozen_ppo_sequential_two_public_probes_physx_v5.py"
PIN="cd84a9fe091d19bd198292e4f54ee0f9bfd73858"
OLD_OBSERVER="research/frozen_ppo_compound_ack_multi_belief.py"
OLD_PIN="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
SINGLE="fault_public_t4_fourhistory_or_t6_query"
DUAL="fault_dual_t4t5_fourhistory_or_t6_query"
STRONG={"pull_cube":"fault_robust_then_single_privileged_query",
        "stack_cube":"fault_always_single_privileged_query"}

def self_selected(task,first):
    if task not in TASKS or type(first) is not int or not 960001<=first<=989992:
        raise ValueError("Choose task and first of 8 new unexposed seeds between 960001 and 989992")
    return list(range(first,first+8))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS),required=True)
    p.add_argument("--first-seed",type=int,required=True)
    p.add_argument("--output",type=Path,default=Path("outside_dual_public_new8"))
    a=p.parse_args()
    seeds=self_selected(a.task,a.first_seed)
    for file,expected in ((SOURCE,PIN),(OLD_OBSERVER,OLD_PIN)):
        got=subprocess.check_output(["git","hash-object",file],text=True).strip()
        if got!=expected:
            raise RuntimeError("The immutable published REAL PhysX controller source has changed: "+file)
    a.output.mkdir(parents=True,exist_ok=True)
    author=os.environ.get("GITHUB_ACTOR","unknown-local")
    repo=os.environ.get("GITHUB_REPOSITORY","unknown-local")
    pre=dict(operator_actor=author,operator_repo=repo,
             external_independent_operator_not_proven=(
                repo=="unknown-local" or repo=="lindicaphxag-tech/ManiSkill"),
             task=a.task,preselected_original_seed_ids=seeds,
             original_full_dual_model_git_blob=PIN,
             actual_first_ack_by_seed={str(i):"APPLIED" if i%2==0 else "HELD" for i in seeds},
             actual_second_ack_by_seed={str(i):"APPLIED" if (i//2)%2==0 else "HELD" for i in seeds},
             physical_neutral_steps=[4,5],source_policy_unmodified=True,
             original_empty_model_training_or_calibration=False)
    (a.output/"BEFORE_PHYSICS_OUTSIDE_OPERATOR_AND_FRESH_SEEDS.json").write_text(
        json.dumps(pre,sort_keys=True,indent=2)+"\n")
    print("BEFORE_ACTUAL_PHYSX_OPERATOR_DECLARATION",json.dumps(pre,sort_keys=True),flush=True)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_sequential_two_public_probes_physx_v5")
    if (runner.TASK!=a.task or runner.SINGLE_ARM!=SINGLE or runner.PUBLIC_ARM!=DUAL
        or len(runner.NAMES)!=10 or tuple(runner.FAULT_STEPS)!=(2,3)):
        raise RuntimeError("Native source identity incorrect or unexpected controller contracts")
    runner.SEEDS=seeds
    runner.COHORT[a.task]=(TASKS[a.task],seeds)
    runner.main() # execute original 80 genuine native PhysX worlds
    rawfile=Path(f"sequential_two_probes_{a.task}_original8.json")
    original=json.loads(rawfile.read_text())
    if original["original_seed_population"]!=seeds or len(original["episodes"])!=8:
        raise RuntimeError("Missing genuine original source PhysX episodes")
    cohort=[]
    for row in original["episodes"]:
        if (row["seed"] not in seeds or len(row["faults"].get(DUAL,[]))!=2 or
            len(row["known_delivered_zero_probes"].get(DUAL,[]))!=2):
            raise RuntimeError("Full four-joint-truth physical fault or probe exposure missing")
        ev=row["public_motion_evidence"]
        cohort.append({
            "seed":row["seed"],
            "joint_true_ack":("A" if row["seed"]%2==0 else "H")+(
                "A" if (row["seed"]//2)%2==0 else "H"),
            "actual_one_probe_task_success":row["success_once"][SINGLE],
            "actual_two_probe_task_success":row["success_once"][DUAL],
            "strong_baseline_task_success":row["success_once"][STRONG[a.task]],
            "one_probe_privileged_reads":row["privileged_target_readback_decision_count"][SINGLE],
            "two_probe_privileged_reads":row["privileged_target_readback_decision_count"][DUAL],
            "one_probe_wrong_confident":ev[SINGLE]["wrong_confident"],
            "two_probe_wrong_confident":ev[DUAL]["wrong_confident"],
            "two_extra_native_probe_steps_applied_to_both_methods":True})
    report=dict(original_external_identity=pre,source_sha256=hashlib.sha256(
         rawfile.read_bytes()).hexdigest(),real_physx_worlds=80,
         original_source_8_complete_task_outcomes=cohort,
         this_is_not_automatically_an_independent_peer_review=True,
         model_not_externally_attested_or_deterministic=True,
         no_robot_hardware_or_network_loss_claim=True)
    (a.output/"EXTERNALLY_CHOOSABLE_EIGHT_PHYSX_REVIEW.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    rawfile.rename(a.output/rawfile.name)
    print("ACTUAL_OUTSIDE_OPERATOR_FROZEN_PPO_DUAL_V_SINGLE_PHYSX",
          json.dumps(report,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
