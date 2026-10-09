"""Outside researcher: independent NEW actual Panda PhysX slow/fast target-memory
ACK evidence stress-test. This is an executable invitation, not a claim that
outside researchers have already performed the experiment.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess,sys
from pathlib import Path

METHOD_PATH="research/frozen_ppo_ood_known_anchor_physx_v6.py"
METHOD_GIT_BLOB="01663775035813e4f87f06171ff3cae0eaebc442"
NATIVE_ABI_PATH="research/frozen_ppo_compound_ack_multi_belief.py"
NATIVE_ABI_BLOB="ddfaf4522d49f73ce926e4c6d77c7ca755f8e1b6"
NARROW="fault_public_t4_original_eps_or_t5_query"
ANCHOR="fault_public_t4_known_ack_anchor_or_t5_query"
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}

def registered_unseen_seeds(first):
    if (type(first) is not int or first%8!=0 or
        not 980000<=first<=999992):
        raise ValueError("BEFORE ANY PHYSICS choose an aligned 8-seed cohort (first divisible by 8; 980000..999992)")
    out=list(range(first,first+8))
    def condition(i):
        return (("A" if i%2==0 else "H")+
                ("A" if (i//2)%2==0 else "H"),
                "slow" if (i//4)%2==0 else "fast")
    for truth in ("AA","AH","HA","HH"):
        for gain in ("slow","fast"):
            if sum(condition(s)==(truth,gain) for s in out)!=1:
                raise ValueError("Independent truly pre-selected 8 task seeds not balanced over joint ACK and physical gain")
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(TASKS),required=True)
    p.add_argument("--first-seed",type=int,required=True)
    p.add_argument("--output",type=Path,default=Path("outside_physx_gain_ood_new8"))
    a=p.parse_args()
    ids=registered_unseen_seeds(a.first_seed)
    for path,pin in ((METHOD_PATH,METHOD_GIT_BLOB),(NATIVE_ABI_PATH,NATIVE_ABI_BLOB)):
        actual=subprocess.check_output(["git","hash-object",path],text=True).strip()
        if actual!=pin:raise RuntimeError("Outside experiment method/target chart changed from original source: "+path)
    a.output.mkdir(parents=True,exist_ok=True)
    repo=os.environ.get("GITHUB_REPOSITORY","local-unidentified")
    actor=os.environ.get("GITHUB_ACTOR","local-unidentified")
    declared={
        "actual_operator_GitHub_repository":repo,"actual_operator_GitHub_actor":actor,
        "external_independent_account":repo not in ("local-unidentified","lindicaphxag-tech/ManiSkill"),
        "preselected_eight_genuinely_new_original_reset_seeds":ids,
        "task":a.task,"frozen_original_PhysX_policy_source_git_blob":METHOD_GIT_BLOB,
        "source_checkpoint_hash_checked_inside_original_physical_run":True,
        "actual_ood_Panda_PD_drive_stiffness_and_damping_per_seed":{
             str(s):{"stiffness":500. if (s//4)%2==0 else 1500.,
                     "damping":70. if (s//4)%2==0 else 130.} for s in ids},
        "two_physical_unknown_ACK_truths_by_seed":{
             str(s):{"t2":"APPLIED" if s%2==0 else "HELD",
                     "t3":"APPLIED" if (s//2)%2==0 else "HELD"} for s in ids},
        "precommitted_before_any_simulator_step":True,
        "this_source_is_not_accepted_publication_or_outside_validation":True
    }
    (a.output/"BEFORE_ANY_PHYSX_EXTERNAL_INVESTIGATOR_AND_8_NEW_SEEDS.json").write_text(
        json.dumps(declared,indent=2,sort_keys=True)+"\n")
    print("BEFORE_PHYSX_INDEPENDENT_OPERATOR_AND_8_SEED_COMMITMENT",
          json.dumps(declared,sort_keys=True),flush=True)
    os.environ["ABI_TASK"]=a.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    runner=importlib.import_module("frozen_ppo_ood_known_anchor_physx_v6")
    if (runner.TASK!=a.task or runner.PUBLIC_ARM!=ANCHOR or runner.NARROW_ARM!=NARROW
        or tuple(runner.FAULT_STEPS)!=(2,3) or len(runner.NAMES)!=10):
        raise RuntimeError("Unexpected source native control/physics/information privilege")
    runner.SEEDS=ids
    runner.COHORT[a.task]=(TASKS[a.task],ids)
    runner.main()   # TEN genuine independently physical controller worlds per new seed.
    original=Path(f"ood_anchor_{a.task}_original8.json")
    raw=original.read_bytes()
    data=json.loads(raw)
    if (data.get("original_seed_population")!=ids or
        data.get("real_physx_simulator") is not True or
        len(data.get("episodes",[]))!=8):
        raise RuntimeError("External original source PhysX evidence incomplete")
    rows=[]
    for r in data["episodes"]:
        if len(r["faults"].get(ANCHOR,[]))!=2:
            raise RuntimeError("Outside adapter missed real two-unknown-ACK controller interventions")
        if any(x not in r["domain_shift_actual_physx_readback_AUDIT_ONLY"]
               for x in (NARROW,ANCHOR)):
            raise RuntimeError("Actual physics-drive gain not independently applied/read back")
        rows.append({
            "seed":r["seed"],"original_source_official_frozen_policy_task_success":r["success_once"]["source_no_fault"],
            "narrow_public_official_task_success":r["success_once"][NARROW],
            "anchor_public_official_task_success":r["success_once"][ANCHOR],
            "old_privileged_target_getters":r["privileged_target_readback_decision_count"][NARROW],
            "anchor_privileged_target_getters":r["privileged_target_readback_decision_count"][ANCHOR],
            "old_wrong_confident_native_history":r["public_t4_evidence"][NARROW]["wrong_confident"],
            "anchor_wrong_confident_native_history":r["public_t4_evidence"][ANCHOR]["wrong_confident"],
            "known_t1_anchor_public_only_pass":r["known_t1_anchor_evidence"][ANCHOR]["passes"],
            "actual_physical_domain":r["actual_domain_mode_source_seed_assignment_AUDIT_ONLY"],
            "both_applied_held_unknown_native_faults_physically_executed":True})
    report={"operator_commitment":declared,
            "actual_physically_executed_native_controller_worlds":80,
            "original_physx_json_SHA256":hashlib.sha256(raw).hexdigest(),
            "all_original_eight_real_task_states":rows,
            "no_external_adoption_claim_unless_operator_truly_independent":True,
            "not_physical_robot_safety_or_true_network_loss":True}
    (a.output/"OUTSIDE_ACTUAL_8_STATE_NATIVE_PHYSX_ORIGINAL_SUMMARY.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    original.rename(a.output/original.name)
    print("OUTSIDE_ACTUAL_OOD_PANDA_REAL_PHYSX_ALL80",json.dumps(report,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
