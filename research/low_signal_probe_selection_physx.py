"""Prospectively frozen, genuinely physically executed Panda/xArm6 low-signal probe trial.

One independent calibration registry, one held-out registry. Readback of the
true controller target for audit is permitted ONLY after any issued correction.
All training uses labels ONLY on old calibration resets. Heldout labels are used
ONLY after public decisions. Not a trained-policy task-success experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

PROTO = Path("research/LOW_SIGNAL_PROBE_SELECTION_PREOUTCOME_V1.json")
PROTO_BLOB = "3f2fcd1f3fd40207431b58a105433f839add0ef2"
FROZEN = {
 "research/common_probe_zero_nonzero_cross_robot_physx.py":"ba4a28b0bb61db8814935a18e43f7153de582070",
 "research/cross_robot_ack_physics.py":"3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7",
 "research/cross_robot_online_proprio_classifier.py":"b0d7a767b93fb9f7cab2ba70494947ccb4027979",
}
ROBOTS=("panda","xarm6_robotiq")
TRUTHS=("applied","held")
PROBES={"zero":(0.,0.,0.,0.,0.,0.),
        "x":(.15,0.,0.,0.,0.,0.),
        "y":(0.,.15,0.,0.,0.,0.)}
CAL={"panda":680001,"xarm6_robotiq":690001}
TEST={"panda":700001,"xarm6_robotiq":710001}
SCALE=.08

def preflight():
    def sha(path):
        return subprocess.check_output(["git","hash-object",str(path)],text=True).strip()
    if sha(PROTO)!=PROTO_BLOB:
        raise ValueError("Protocol changed after pre-outcome freeze")
    for path,digest in FROZEN.items():
        if sha(path)!=digest:
            raise ValueError("Original physical semantics/classifier changed: "+path)
    d=json.loads(PROTO.read_text(encoding="utf-8"))
    if (d["fault_native_6d_scale"]!=SCALE
        or d["calibration_seed_ranges"]!={k:[v,v+7] for k,v in CAL.items()}
        or d["heldout_seed_ranges"]!={k:[v,v+7] for k,v in TEST.items()}
        or set(d["known_delivered_probes"])!=set(PROBES)
        or any(tuple(d["known_delivered_probes"][k])!=v for k,v in PROBES.items())
        or d["expected_world_counts"]!={"calibration":96,"holdout":96,
             "total":192,"independent_calibration_reset_seeds":16,
             "independent_heldout_reset_seeds":16}):
        raise ValueError("Predeclared physical truth/seed/budget altered")
    return d

def install_physics_intervention():
    import numpy as np
    import research.common_probe_zero_nonzero_cross_robot_physx as m
    original=m.requested_native
    def low_fault(step):
        a=np.asarray(original(step),dtype=np.float64).copy()
        if step==2:
            a*=SCALE
        return a
    m.requested_native=low_fault
    m.PROBES={name:np.asarray(vals,dtype=np.float64) for name,vals in PROBES.items()}
    return m

def _dist(v,w):
    return math.dist(v,w)

def calibration_selection(fitted):
    """Selected robot-specific candidate must be one of TWO equal-L2 nonzero actions."""
    scored={}
    for name in ("x","y"):
        model=fitted[name]
        p=model["class_models"]
        gap=_dist(p["applied"]["mean_public_motion_m"],
                  p["held"]["mean_public_motion_m"])
        separation=gap-p["applied"]["envelope_radius_m"]-p["held"]["envelope_radius_m"]
        scored[name]={"center_separation_m":gap,
                      "worst_response_ball_margin_m":separation}
    # Deterministic: threshold-independent, old-calibration-only, x on ties.
    selected=max(("x","y"),key=lambda a:(scored[a]["worst_response_ball_margin_m"],-("x","y").index(a)))
    return selected,scored

def calibration(robot):
    if robot not in ROBOTS:raise ValueError("Unsupported physical robot")
    preflight()
    import research.cross_robot_online_proprio_classifier as c
    m=install_physics_intervention()
    source=[m.original_trial(robot,seed,truth,probe)
            for seed in range(CAL[robot],CAL[robot]+8)
            for truth in TRUTHS for probe in PROBES]
    models={}
    for probe in PROBES:
        records=[dict(robot=row["robot"],seed=row["seed"],
                      truth=row["hidden_physical_truth_posthoc_only"],
                      delta_public_xyz=row["delta_public_xyz"])
                 for row in source if row["known_delivered_native_probe_id"]==probe]
        models[probe]=c.train(records,robot)
    selected,scores=calibration_selection(models)
    assert len(source)==48 and all(models[a]["training_seeds"]==list(range(CAL[robot],CAL[robot]+8)) for a in PROBES)
    return dict(schema="LOW_SIGNAL_CALIBRATION_V1",robot=robot,physical_worlds=48,
                protocol_blob=PROTO_BLOB,old_reset_seeds=list(range(CAL[robot],CAL[robot]+8)),
                actual_intervention_scale=SCALE,selected_nonzero_probe=selected,
                old_only_selection_scores=scores,models=models,physical_calibration_rows=source,
                no_model_safety_attestation=True)

def validate_calibration(model,robot):
    import research.cross_robot_online_proprio_classifier as c
    if (model.get("schema")!="LOW_SIGNAL_CALIBRATION_V1"
        or model.get("robot")!=robot or model.get("protocol_blob")!=PROTO_BLOB
        or model.get("old_reset_seeds")!=list(range(CAL[robot],CAL[robot]+8))
        or model.get("actual_intervention_scale")!=SCALE
        or model.get("physical_worlds")!=48
        or len(model.get("physical_calibration_rows",[]))!=48
        or set(model.get("models",{}))!=set(PROBES)):
        raise ValueError("Calibration population or model evidence changed")
    rows=model["physical_calibration_rows"]
    expected={(seed,truth,probe) for seed in range(CAL[robot],CAL[robot]+8)
              for truth in TRUTHS for probe in PROBES}
    observed={(r["seed"],r["hidden_physical_truth_posthoc_only"],
               r["known_delivered_native_probe_id"]) for r in rows}
    if observed!=expected or len(observed)!=len(rows):
        raise ValueError("Incomplete or duplicated training PhysX worlds")
    for probe in PROBES:
        records=[dict(robot=r["robot"],seed=r["seed"],
                      truth=r["hidden_physical_truth_posthoc_only"],
                      delta_public_xyz=r["delta_public_xyz"])
                 for r in rows if r["known_delivered_native_probe_id"]==probe]
        if c.train(records,robot)!=model["models"][probe]:
            raise ValueError("Calibration model does not reproduce actual original physics")
    selected,scores=calibration_selection(model["models"])
    if (model["selected_nonzero_probe"]!=selected
        or model["old_only_selection_scores"]!=scores):
        raise ValueError("Selection was modified after calibration")

def test(robot,chunk,cal):
    if robot not in ROBOTS or chunk not in (0,1):raise ValueError("Wrong heldout shard")
    preflight()
    validate_calibration(cal,robot)
    m=install_physics_intervention()
    seed_start=TEST[robot]+4*chunk
    cases=[]
    for seed in range(seed_start,seed_start+4):
        for truth in TRUTHS:
            for probe in PROBES:
                row=m.original_trial(robot,seed,truth,probe,model=cal["models"][probe])
                if (row["private_target_reads_before_classification"]!=0
                    or row["private_target_reads_before_correction"]!=0
                    or not row["real_physx_cpu"]
                    or row["actual_native_t3_probe_six"]!=list(PROBES[probe])):
                    raise ValueError("Actual physical/no-private-input contract false")
                cases.append(row)
    # Strict before-probe physical equality: identical seed and first two actions
    # across all *actually executed* candidate probe/truth worlds.
    for seed in range(seed_start,seed_start+4):
        subset=[r for r in cases if r["seed"]==seed]
        before=[r["public_xyz_after_t1"] for r in subset]
        if len(subset)!=6 or max(_dist(v,before[0]) for v in before)>5e-5:
            raise ValueError("Same-seed original physical before-probe state mismatched")
    return dict(schema="LOW_SIGNAL_HOLDOUT_V1",robot=robot,chunk=chunk,
                protocol_blob=PROTO_BLOB,seeds=list(range(seed_start,seed_start+4)),
                calibration_digest=hashlib.sha256(json.dumps(cal,sort_keys=True).encode()).hexdigest(),
                selected_nonzero_probe=cal["selected_nonzero_probe"],
                original_actual_native_physx_worlds=24,
                original_rows=cases,
                all_six_physical_truth_probe_worlds_per_seed=True,
                trained_on_heldout_labels=False,
                no_policy_task_success_claim=True)

def audit_root(folder):
    """Audits entire denominator and rederives training, decisions and correction labels."""
    import research.cross_robot_online_proprio_classifier as c
    preflight()
    by_robot={}
    for robot in ROBOTS:
        cal_path=folder/f"low_signal_calibration_{robot}.json"
        cal=json.loads(cal_path.read_text())
        validate_calibration(cal,robot)
        expected={(seed,truth,probe) for seed in range(TEST[robot],TEST[robot]+8)
                  for truth in TRUTHS for probe in PROBES}
        allrows=[]
        digest=hashlib.sha256(json.dumps(cal,sort_keys=True).encode()).hexdigest()
        for chunk in (0,1):
            p=folder/f"low_signal_holdout_{robot}_chunk{chunk}.json"
            d=json.loads(p.read_text())
            if (d.get("schema")!="LOW_SIGNAL_HOLDOUT_V1" or d.get("robot")!=robot
                or d.get("chunk")!=chunk or d.get("protocol_blob")!=PROTO_BLOB
                or d.get("calibration_digest")!=digest
                or d.get("selected_nonzero_probe")!=cal["selected_nonzero_probe"]
                or d.get("original_actual_native_physx_worlds")!=24):
                raise ValueError("Wrong original heldout source identity")
            allrows+=d["original_rows"]
        keys={(r["seed"],r["hidden_physical_truth_posthoc_only"],
               r["known_delivered_native_probe_id"]) for r in allrows}
        if len(allrows)!=48 or keys!=expected or len(keys)!=48:
            raise ValueError("Missing, duplicated, or extra heldout original PhysX")
        for r in allrows:
            probe=r["known_delivered_native_probe_id"]
            expected_decision=c.decide(r["delta_public_xyz"],cal["models"][probe])
            if (r["decision"]!=expected_decision or r["real_physx_cpu"] is not True
                or r["private_target_reads_before_classification"]!=0
                or r["private_target_reads_before_correction"]!=0
                or r["actual_native_t3_probe_six"]!=list(PROBES[probe])
                or r["wrong_confident_history"] != (
                    None if expected_decision["label"] is None else
                    expected_decision["label"]!=r["hidden_physical_truth_posthoc_only"])
                or r["target_correction_reached"]!=(expected_decision["label"] is not None)):
                raise ValueError("Original heldout decision, motion, or truth invalid")
            if r["target_correction_reached"]:
                value=r["commanded_target_post_correction_error_inf_m"]
                if (not isinstance(value,(int,float)) or not math.isfinite(value)
                    or r["target_restored_below_1e4_m"]!=(value<=1e-4)):
                    raise ValueError("Altered corrective actuation audit")
        gaps={}
        by_probe={}
        for probe in PROBES:
            rows=[r for r in allrows if r["known_delivered_native_probe_id"]==probe]
            pairs={}
            for seed in range(TEST[robot],TEST[robot]+8):
                applied=next(r for r in rows if r["seed"]==seed and r["hidden_physical_truth_posthoc_only"]=="applied")
                held=next(r for r in rows if r["seed"]==seed and r["hidden_physical_truth_posthoc_only"]=="held")
                pairs[seed]=_dist(applied["delta_public_xyz"],held["delta_public_xyz"])
            gaps[probe]={"mean_truth_separation_m":sum(pairs.values())/8,
                         "seed_count":len(pairs)}
            by_probe[probe]={
                "authorizations":sum(r["decision"]["label"] is not None for r in rows),
                "wrong":sum(r["wrong_confident_history"] is True for r in rows),
                "abstentions":sum(r["decision"]["label"] is None for r in rows),
                "native_target_corrections_within_1e4_m":sum(r["target_restored_below_1e4_m"] for r in rows),
                "physical_worlds":len(rows),
                "nominal_native6_probe_L2":math.sqrt(sum(v*v for v in PROBES[probe]))
            }
        by_robot[robot]={
            "calibration_selected_nonzero":cal["selected_nonzero_probe"],
            "frozen_calibration_probe_scores":cal["old_only_selection_scores"],
            "heldout_by_probe":by_probe,"real_physical_response_gaps":gaps,
            "independent_heldout_reset_seeds":8
        }
    return dict(schema="LOW_SIGNAL_SOURCE_VERIFIED_RESULT_V1",
                original_physics_worlds_calibration=96,original_physics_worlds_heldout=96,
                independent_heldout_reset_clusters=16,physically_stepped_robots=list(ROBOTS),
                result_by_robot=by_robot,
                no_safety_or_task_success_or_independent_lab_claim=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","calibration","heldout","audit"),required=True)
    parser.add_argument("--robot",choices=ROBOTS)
    parser.add_argument("--chunk",type=int,choices=(0,1))
    parser.add_argument("--calibration",type=Path)
    parser.add_argument("--folder",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.mode=="preflight":
        preflight()
        print("PASS PREOUTCOME SOURCE PROVENANCE AND LOW SIGNAL SEEDS")
    elif args.mode=="calibration":
        if args.robot is None:parser.error("--robot required")
        d=calibration(args.robot)
        name=args.output or Path(f"low_signal_calibration_{args.robot}.json")
        name.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
        print("ACTUAL_LOW_SIGNAL_PRIOR_PHYSX",args.robot,d["selected_nonzero_probe"],d["old_only_selection_scores"])
    elif args.mode=="heldout":
        if args.robot is None or args.chunk is None or args.calibration is None:
            parser.error("--robot, --chunk and --calibration required")
        d=test(args.robot,args.chunk,json.loads(args.calibration.read_text()))
        name=args.output or Path(f"low_signal_holdout_{args.robot}_chunk{args.chunk}.json")
        name.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
        print("ACTUAL_LOW_SIGNAL_UNSEEN_PHYSX",args.robot,args.chunk,len(d["original_rows"]))
    else:
        if args.folder is None or args.output is None:parser.error("--folder and --output required")
        d=audit_root(args.folder)
        args.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
        print("FULL_PHYSX_LOW_SIGNAL_AUDITED",json.dumps(d,sort_keys=True))

if __name__=="__main__":
    main()
