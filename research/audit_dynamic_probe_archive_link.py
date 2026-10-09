"""Audit genuine archived Panda/xArm6 native action probe source as a
*limited intervention-contract witness*, NOT a dynamic safety certificate.

No new physics: reads 24 byte-preserved author-operated archive files, checks
SHA256 and every 2 robot x 8 heldout seed x 2 ACK truth x 3 probe outcomes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

ROBOTS=("panda","xarm6_robotiq")
PROBES=("zero","x","y")
TRUTHS=("applied","held")
START={"panda":700001,"xarm6_robotiq":710001}


def audit_archive(root: Path) -> dict:
    if not isinstance(root, Path):
        raise ValueError("source must be a Path")
    manifest=root/"FIRST_192_SHA256SUMS"
    if not manifest.is_file():
        raise ValueError("Missing immutable original SHA256 manifest")
    entries=manifest.read_text(encoding="utf-8").splitlines()
    if len(entries)!=24:
        raise ValueError("Expected 24 archived source file SHA256s")
    verified=set()
    for line in entries:
        parts=line.split(maxsplit=1)
        if len(parts)!=2:
            raise ValueError("Malformed checksum row")
        digest,name=parts
        name=name.lstrip("*").removeprefix("./")
        path=Path(name)
        if path.is_absolute() or ".." in path.parts or name in verified:
            raise ValueError("Malformed or duplicated manifest path")
        verified.add(name)
        file=root/path
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=digest:
            raise ValueError("Original source byte tampered or missing: "+name)
    reviewer=json.loads((root/"REVIEWER_PAIRED_RESET_AUDIT.json").read_bytes())
    if (reviewer["audit_status"]!="PASS_AUTHOR_OPERATED_192_ORIGINAL_NATIVE_PHYSX_WORLDS"
            or reviewer["heldout_distinct_independent_reset_seeds"]!=16
            or reviewer["all_heldout_physical_truth_probe_worlds"]!=96):
        raise ValueError("Archive reviewer summary identity inconsistent")
    groups=defaultdict(dict)
    all_rows=[]
    for robot in ROBOTS:
        for chunk in (0,1):
            f=root/f"low_signal_holdout_{robot}_chunk{chunk}.json"
            doc=json.loads(f.read_bytes())
            if (doc["robot"]!=robot or doc["chunk"]!=chunk or
                    doc["original_actual_native_physx_worlds"]!=24):
                raise ValueError("Wrong heldout source identity")
            for row in doc["original_rows"]:
                seed=row["seed"]
                if (row["robot"]!=robot or not START[robot] <= seed < START[robot]+8
                        or (seed-START[robot])//4!=chunk or
                        row["real_physx_cpu"] is not True or
                        row["private_target_reads_before_classification"]!=0 or
                        row["private_target_reads_before_correction"]!=0 or
                        row["known_delivered_native_probe_id"] not in PROBES or
                        row["hidden_physical_truth_posthoc_only"] not in TRUTHS):
                    raise ValueError("Bad real physics / no-privilege identity")
                key=(robot,seed,row["hidden_physical_truth_posthoc_only"])
                probe=row["known_delivered_native_probe_id"]
                if probe in groups[key]:
                    raise ValueError("Duplicate physical probe outcome")
                groups[key][probe]=row
                all_rows.append(row)
    if (len(groups)!=32 or len(all_rows)!=96
            or any(set(d)!=set(PROBES) for d in groups.values())):
        raise ValueError("Incomplete six-world-per-reset original source")
    shifted=0
    same_correction=0
    maxshift=0.
    for group,d in groups.items():
        reference=d["zero"]
        first_pos=reference["public_xyz_after_t1"]
        if any(math.dist(row["public_xyz_after_t1"],first_pos)>5e-5
               for row in d.values()):
            raise ValueError("Initial matched physical probe prefix invalid")
        if any(row["decision"]["label"]!=group[2] or
               row["target_restored_below_1e4_m"] is not True
               for row in d.values()):
            raise ValueError("Source wrong correction or failed target audit")
        if all(len(row["corrective_native_six"])==6 and
               math.dist(row["corrective_native_six"],
                         reference["corrective_native_six"])<=1e-9
               for row in d.values()):
            same_correction+=1
        for action in ("x","y"):
            row=d[action]
            delta=math.dist(row["public_xyz_after_t3"],
                            reference["public_xyz_after_t3"])
            if not math.isfinite(delta):
                raise ValueError("Invalid physical position")
            maxshift=max(maxshift,delta)
            shifted+=delta>0.0005
    return {
        "schema":"archived_original_physics_intervention_contract_audit_v1",
        "original_author_executed_source_only":True,
        "sha256_verified_original_files":len(verified),
        "heldout_independent_robot_reset_seeds":16,
        "heldout_robot_reset_ack_truth_groups":32,
        "physically_executed_probe_outcomes":len(all_rows),
        "nonzero_probe_outcomes_total":64,
        "nonzero_probe_achieved_shift_gt_0_5mm":shifted,
        "groups_with_same_commanded_native_repair_vector_across_zero_xy":same_correction,
        "max_observed_public_achieved_shift_m":maxshift,
        "real_transition_support_complete":False,
        "measured_action_work_or_contact_safety":False,
        "observed_repair_changing_probe_in_this_archive":same_correction!=32,
        "authoritative_read_required_for_uncovered_behavior":True,
        "claim_boundary":"correction vector and achieved XYZ differ from full hidden controller SE3, task validity and complete transition support",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=audit_archive(args.source)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("ARCHIVED_REAL_PHYSICS_CONTRACT_LIMITS",json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
