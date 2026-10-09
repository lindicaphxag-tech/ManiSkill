"""Independently re-count ORIGINAL first-run PhysX provenance on 3 operating systems.

No ManiSkill, NumPy, SciPy, SAPIEN or GPU dependency. It checks source bytes,
full 128-world register, paired prefixes, and consistency of ORIGINAL recorded
physical residual fields. The raw pre/post correction controller quaternions
were not separately exported; no stronger physical remeasurement is claimed.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

FIRST=Path("research/frozen_policy_transfer/evidence/anchor_first128_first_physics_20261010")
ROBOTS={"panda":720001,"xarm6_robotiq":730001}
TRUTHS=("held","applied")
PROBES=("zero","rotation_z")
ARMS=("no_probe_transition_ablation","actual_transition_compensation")


def review(source:Path)->dict:
    manifest=source/"FIRST128_SHA256SUMS"
    lines=manifest.read_text(encoding="utf-8").splitlines()
    if len(lines)!=19:
        raise ValueError("Expected exactly 19 original archive files")
    files={}
    for line in lines:
        dig,name=line.split(maxsplit=1)
        name=name.lstrip("*").removeprefix("./")
        p=Path(name)
        if p.is_absolute() or ".." in p.parts or name in files:
            raise ValueError("Unsafe or duplicated archive path")
        payload=(source/p).read_bytes()
        if hashlib.sha256(payload).hexdigest()!=dig:
            raise ValueError("Original physical evidence checksum fails for "+name)
        files[name]=dig
    worlds={}
    groups=defaultdict(list)
    for robot,start in ROBOTS.items():
        for chunk in (0,1):
            name=f"anchor_repair_{robot}_chunk{chunk}.json"
            if name not in files:
                raise ValueError("Required original shard not checksum-registered")
            d=json.loads((source/name).read_bytes())
            if (d["schema"]!="original_anchor_repair_source_32_worlds_v1" or
                d["robot"]!=robot or d["chunk"]!=chunk or len(d["worlds"])!=32):
                raise ValueError("Missing or relabeled original physics trial shard")
            for w in d["worlds"]:
                key=(w["robot"],w["seed"],w["truth_oracle_known_to_both_repair_arms"],
                     w["known_delivered_probe"],w["repair_strategy"])
                if (key in worlds or key[0]!=robot or not start<=key[1]<=start+7 or
                    key[2] not in TRUTHS or key[3] not in PROBES or key[4] not in ARMS or
                    (key[1]-start)//4!=chunk or w["actual_physx_world"] is not True or
                    w["getter_not_input_to_repair"] is not True):
                    raise ValueError("Unregistered/duplicated physical source")
                err=w["real_t4_controller_target_restoration_error"]
                if (not all(isinstance(err[k],(int,float)) and math.isfinite(err[k]) and err[k]>=0
                            for k in ("linf_m","so3_rad")) or
                    w["native_target_restoration_pass"]!=
                    (err["linf_m"]<=1e-4 and err["so3_rad"]<=1e-3)):
                    raise ValueError("Falsified original physical SE3 residual/pass label")
                worlds[key]=w
                groups[(robot,w["seed"])].append(w)
    expected={(robot,seed,t,p,a)
              for robot,start in ROBOTS.items()
              for seed in range(start,start+8)
              for t in TRUTHS for p in PROBES for a in ARMS}
    if set(worlds)!=expected or len(groups)!=16:
        raise ValueError("Incomplete 16 independent resets by eight worlds")
    matched=0
    nonzero_target_rotated=0
    for robot,start in ROBOTS.items():
        for seed in range(start,start+8):
            reference=groups[(robot,seed)][0]
            for w in groups[(robot,seed)]:
                if w["predicted_anchor_pose"]!=reference["predicted_anchor_pose"]:
                    raise ValueError("Different registered same-reset target anchor")
            for truth in TRUTHS:
                for probe in PROBES:
                    a=worlds[robot,seed,truth,probe,ARMS[0]]
                    b=worlds[robot,seed,truth,probe,ARMS[1]]
                    for key in ("public_achieved_t1_xyz","public_achieved_t3_xyz",
                                "predicted_anchor_pose","actual_target_after_probe_drift"):
                        if a[key]!=b[key]:
                            raise ValueError("Non-identical physical prefix prior to different repairs")
                    matched+=1
                    if probe=="rotation_z" and a["actual_target_after_probe_drift"]["so3_rad"]>1e-3:
                        nonzero_target_rotated+=1
    table={}
    for robot in ROBOTS:
        table[robot]={}
        for probe in PROBES:
            for arm in ARMS:
                subset=[w for key,w in worlds.items()
                        if key[0]==robot and key[3]==probe and key[4]==arm]
                table[robot][f"{probe}/{arm}"]={
                    "total_correlated_truth_worlds":len(subset),
                    "recorded_fullSE3_target_restoration_passes":
                        sum(w["native_target_restoration_pass"] for w in subset),
                    "largest_recorded_SO3_residual_rad":
                        max(w["real_t4_controller_target_restoration_error"]["so3_rad"]
                            for w in subset)}
    original=json.loads((source/"ORIGINAL_FIRST_RUN_POST_DEPENDENCY_SOURCE_AUDIT.json").read_bytes())
    if original["original_heldout_each_robot"]!={
            r:{k:{"physical_worlds":v["total_correlated_truth_worlds"],
                  "full_se3_commanded_target_restorations":v["recorded_fullSE3_target_restoration_passes"],
                  "max_target_so3_error_rad":v["largest_recorded_SO3_residual_rad"]}
               for k,v in table[r].items()}
            for r in ROBOTS}:
        raise ValueError("Published source aggregate conflicts with original physical per-world fields")
    if (original["same_repair_prefix_matched_seed_truth_probe_groups"]!=matched or
        original["nonzero_rotation_known_delivered_target_drift_gt_0_001rad_groups"]!=nonzero_target_rotated):
        raise ValueError("Physical first-run aggregate source count conflict")
    return {
        "status":"VERIFIED_19_ORIGINAL_FILE_HASHES_AND_128_SOURCE_ROWS",
        "checked_files":len(files),"independent_robot_reset_seeds":len(groups),
        "original_physical_worlds":len(worlds),
        "matched_pair_prefixes":matched,
        "rotation_probe_changed_recorded_target_so3_gt_0_001rad":nonzero_target_rotated,
        "source_only_original_recorded_metrics_not_raw_quaternion_remeasurement":True,
        "by_robot_and_probe_repair":table,
        "no_third_party_physx_rerun_or_real_robot_safety":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=FIRST)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=review(a.source)
    a.output.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("ORIGINAL128_CROSS_PLATFORM_SOURCE_REAUDIT",json.dumps(d,sort_keys=True))


if __name__=="__main__":
    main()
