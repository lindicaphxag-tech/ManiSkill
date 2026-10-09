"""Outside-operator new-seed real PhysX replication of the MIXED-TRUTH ACK falsifier.

This is a runnable review ENTRY, not a claim of independent adoption. Source
must match published native physical policy/fault generator Git object. The 8 seeds must be independently declared unused and are committed to run artifacts before first physics action.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path
SOURCE="research/frozen_ppo_mixed_ack_truth_physx.py"
ORIGINAL_SOURCE_BLOB="36e672446407435e656cbf8aba6fa2de7c1e9d0e"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
PUBLIC="fault_public_t3_fourhistory_or_t4_query"
ZERO="fault_assume_held_without_query"
TASK_ROUTE={"pull_cube":"fault_robust_then_single_privileged_query",
            "stack_cube":"fault_always_single_privileged_query"}
def validate(task,first):
    if task not in TASKS or type(first)!=int or not 1200001<=first<=2099992:
        raise ValueError("Select an independently unused block of 8 reset IDs in 1200001..2099992 before any execution")
    return list(range(first,first+8))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS),required=True)
    p.add_argument("--first-seed",type=int,required=True)
    p.add_argument("--output",type=Path,default=Path("outside_mixed_ack_original"))
    a=p.parse_args()
    ids=validate(a.task,a.first_seed)
    got=subprocess.check_output(["git","hash-object",SOURCE],text=True).strip()
    if got!=ORIGINAL_SOURCE_BLOB:
        raise RuntimeError("Original approved mixed-ACK PhysX method/source changed")
    a.output.mkdir(parents=True,exist_ok=True)
    repo=os.environ.get("GITHUB_REPOSITORY","local-unknown")
    actor=os.environ.get("GITHUB_ACTOR","local-unknown")
    pre=dict(external_operator_repository=repo,operator_actor=actor,
             external_user_operated_repo=(repo not in
                 ("lindicaphxag-tech/ManiSkill","local-unknown")),
             exact_method_git_blob=got,
             task=a.task,source_model_retrained=False,
             eight_preselected_seeds=ids,
             t2_actual_execution_truth_by_seed={
                 str(seed):("APPLIED" if seed%2==0 else "HELD") for seed in ids},
             second_actual_native_ack_truth="HELD for all",
             no_celebration_of_author_owned_fork_as_external_replication=True,
             source_check_before_any_physx_step=True)
    (a.output/"BEFORE_ANY_PHYSX_ORIGINAL_OPERATOR_AND_SEED_COMMITMENT.json").write_text(
         json.dumps(pre,indent=2,sort_keys=True)+"\n")
    print("EXTERNAL_OPERATOR_BEFORE_REAL_PHYSX",json.dumps(pre,sort_keys=True),flush=True)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_mixed_ack_truth_physx")
    if runner.TASK!=a.task or tuple(runner.FAULT_STEPS)!=(2,3) or len(runner.NAMES)!=9:
        raise RuntimeError("Original mixed-ACK native frozen method mutated")
    runner.SEEDS=ids
    runner.COHORT[a.task]=(TASKS[a.task],ids)
    runner.main()
    orig=Path(f"mixed_ack_{a.task}_original8.json")
    d=json.loads(orig.read_text())
    if d.get("original_seed_population")!=ids or d.get("real_physx_simulator") is not True:
        raise RuntimeError("No original genuine native PhysX model execution")
    records=[]
    for r in d["episodes"]:
        if len(r.get("faults",{}).get(PUBLIC,[]))!=2:
            raise RuntimeError("Fault exposure missing; source preserved but NOT a complete replicate")
        records.append(dict(seed=r["seed"],
            physical_t2_truth=r["original_precommitted_physical_t2_execution_truth"],
            new_policy_success=r["success_once"][PUBLIC],
            new_policy_privileged_reads=r["privileged_target_readback_decision_count"][PUBLIC],
            task_route_policy_success=r["success_once"][TASK_ROUTE[a.task]],
            task_route_privileged_reads=r["privileged_target_readback_decision_count"][TASK_ROUTE[a.task]],
            always_held_policy_success=r["success_once"][ZERO],
            always_held_privileged_reads=r["privileged_target_readback_decision_count"][ZERO],
            public_correct_confident=r.get("public_t3_evidence",{}).get("authorized"),
            public_wrong_confident=r.get("public_t3_evidence",{}).get("wrong_confident")))
    report=dict(original_operator_identity=pre,real_native_PhysX_worlds=72,
                actual_original_raw_sha256=hashlib.sha256(orig.read_bytes()).hexdigest(),
                all_eight_original_seed_truth_task_comparisons=records,
                no_real_packet_loss_or_hardware_safety=True,
                not_upstream_accepted_or_third_party_replicated_without_outside_fork=True)
    (a.output/"INDEPENDENT_ORIGINAL_MIXED_ACK_REVIEWER_SUMMARY.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    orig.rename(a.output/orig.name)
    print("FULL_EIGHT_NEW_SEED_REAL_PHYSX_MIXED_ACK",json.dumps(report,sort_keys=True),flush=True)
if __name__=="__main__":main()
