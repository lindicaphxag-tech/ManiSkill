"""Independent outside-review, SHA-pinned original 32-state REAL PhysX task audit.

NO simulator/GPU required. Runs with Python stdlib. All filenames, hashes,
completed fault exposures, full SE3 wrong-confident labels, query budgets,
matched task successes AND uneven task-specific query costs are enforced.

Usage:
python -m research.frozen_policy_transfer.review.verify_survivor_fullpose \
    --output /tmp/survivor_reviewer_verify.json

Source data are author-operated physical simulation, not third-party adoption.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from research.audit_survivor_fullpose_new32 import original_complete_audit

SOURCE=Path("research/frozen_policy_transfer/evidence/survivor_fullpose_original32_860001_870016")


def require(ok,msg):
    if not ok:raise ValueError(msg)


def source_hashes(directory:Path)->dict[str,str]:
    name="SHA256SUMS"
    path=directory/name
    require(path.is_file(),"Original real PhysX SHA256 source manifest missing")
    hashes={}
    for line in path.read_text(encoding="utf-8").splitlines():
        pieces=line.split(maxsplit=1)
        require(len(pieces)==2,"Malformed provenance line")
        digest,filename=pieces
        filename=filename.removeprefix("./")
        require(len(digest)==64 and filename not in hashes
                and "/" not in filename and "\\" not in filename,
                "Malformed or duplicated source entry")
        hashes[filename]=digest
    expected={"full_original_survivor_fullpose_new32_audit.json"}
    for task in ("pull_cube","stack_cube"):
        for chunk in range(4):
            expected.update({
               f"survivor_fullpose_{task}_chunk{chunk}_original4.json",
               f"survivor_fullpose_{task}_chunk{chunk}_audit.json",
            })
    require(set(hashes)==expected,"Missing or extra source in SHA manifest")
    require({x.name for x in directory.glob("*.json")}==expected,
            "Actual archived source filenames do not match original full denominator")
    for filename,digest in hashes.items():
        require(hashlib.sha256((directory/filename).read_bytes()).hexdigest()==digest,
                "Unmodified original real PhysX source changed: "+filename)
    return hashes


def reviewer_recompute(source:Path):
    digests=source_hashes(source)
    report=original_complete_audit(source)
    original=json.loads((source/"full_original_survivor_fullpose_new32_audit.json").read_text())
    require(report==original,"Independent all-original per-seed re-audit disagrees with frozen source audit")
    require(report["genuine_source_physx_reset_states"]==32
            and report["genuine_physics_controller_worlds"]==256
            and report["complete_double_fault_gate_passes"] is True
            and report["double_fault_exposure_population"]==32,
            "Original real physical two-fault experiment incomplete")
    require(report["public_confident_authorizations"]==10
            and report["model_confident_wrong"]==0
            and report["paired_discordances"]=={
                "both":28,"neither":4,"new_only":0,"task_gate_only":0},
            "Previously observed confident-label or paired task outcomes altered")
    a=report["outcomes_total"]
    require(a["new_public"]=={"success":28,"privileged_reads":22}
            and a["task_preselected"]=={"success":28,"privileged_reads":27}
            and a["fixed_t4"]=={"success":28,"privileged_reads":32},
            "Original actual privileged controller-target reading ledger drifted")
    per_task={}
    for name,expected in [
       ("pull_cube",(16,3,16,13,16,11)),
       ("stack_cube",(16,7,12,9,12,16))
    ]:
        task=report["by_task"][name]
        q=task["outcomes"]["new_public"]
        baseline=task["outcomes"]["task_preselected"]
        observed=(task["reset_states"],task["public_confident_authorizations"],
                  q["success"],q["private_reads"],
                  baseline["success"],baseline["private_reads"])
        require(observed==expected,
                "Heterogeneous PullCube / StackCube readback performance hidden or altered")
        per_task[name]={"source_states":expected[0],"public_only_labels":expected[1],
                        "hybrid_success":expected[2],"hybrid_reads":expected[3],
                        "strong_task_gate_success":expected[4],
                        "strong_task_gate_reads":expected[5]}
    return {
        "schema":"outsider_standard_library_real_physx_survivor_verification_v1",
        "original_author_run":"https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914343195",
        "independent_third_party_execution":False,
        "real_hardware_proved_safe":False,
        "original_physx_controllers":256,
        "original_reset_states":32,
        "both_native_ACK_faults_reached":32,
        "public_only_full_pose_history_labels":10,
        "wrong_confident_full_pose_labels":0,
        "hybrid_vs_task_gate_paired_outcomes":{"both_success":28,"both_fail":4,
             "hybrid_only":0,"task_gate_only":0},
        "hybrid_privileged_reads":22,
        "task_aware_privileged_reads":27,
        "mandatory_privileged_reads":32,
        "explicit_new_public_xyz_samples":64,
        "hypothetical_public_sample_cost_break_even_relative_to_privileged_getter":5/64,
        "method_cost_advantage_not_uniform_across_tasks":True,
        "task_strata":per_task,
        "all_17_original_source_sha256":digests,
        "limitations":"Empirical response model untrusted outside calibration; paired task equality is not statistical population equivalence, real robot safety, or outside scientific acceptance"
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=SOURCE)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    q=reviewer_recompute(args.source)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(q,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("SOURCE_AUTHENTICATED_ORIGINAL_SURVIVOR_PPO32",
          json.dumps({k:q[k] for k in ("original_physx_controllers",
             "public_only_full_pose_history_labels","wrong_confident_full_pose_labels",
             "hybrid_privileged_reads","task_aware_privileged_reads",
             "mandatory_privileged_reads")},sort_keys=True))

if __name__=="__main__":main()
