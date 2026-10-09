"""Retrospective source-pinned cross-robot ACK-response portability falsifier.

NO new PhysX episodes. NO independent scientific reproduction. No trained PPO.
This analyzes two existing maintained native robot controllers (Panda and
xArm6 Robotiq), each with 8 paired prior CALIBRATION seeds and 8 disjoint
NEW PhysX test seeds. A target-domain "one shot" is TWO known-truth source
calibration episodes from one target robot reset state (applied and held).
That truth requires deliberate calibration, not unsupervised sensing.

We compare zero-shot unchanged OTHER-robot model to 1/2/4/8 target reset
calibration SEED PAIRS; this study and k grid were selected AFTER viewing
the entire original data. The outputs are DESCRIPTIVE, not prospective
sample-efficiency evidence. No task-success, hardware safety or cross-robot
frozen PPO transfer is claimed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

from research.audit_cross_robot_online_ack32 import audit as source_audit
from research.cross_robot_online_proprio_classifier import (
    LABELS, ADDITIVE_RADIUS_M, decide,
)

DATA = (Path(__file__).resolve().parent /
        "frozen_policy_transfer/evidence/cross_robot_online_public_proprio_new32_480001_490008")
ROBOTS = ("panda", "xarm6_robotiq")
CALIB_START = {"panda": 420001, "xarm6_robotiq": 430001}
TEST_START = {"panda": 480001, "xarm6_robotiq": 490001}
K = (0, 1, 2, 4, 8)
SOURCE_RUN = "https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37905560363"


def ensure(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def vecnorm(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((float(x)-float(y))**2 for x, y in zip(a, b)))


def immutable_source(folder: Path) -> dict[str, str]:
    manifest = folder/"SHA256SUMS"
    ensure(manifest.is_file(), "Missing original SHA256SUMS manifest")
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.removeprefix("./")
        ensure(name not in entries and len(digest)==64
               and all(c in "0123456789abcdef" for c in digest)
               and "/" not in name and "\\" not in name,
               "Original immutable source SHA256 manifest is malformed")
        entries[name] = digest
    expected = {f"cross_robot_proprio_calibration_{r}.json" for r in ROBOTS}
    expected.update(f"cross_robot_proprio_{r}_chunk{c}_original8.json"
                    for r in ROBOTS for c in (0, 1))
    expected.add("full_cross_robot_online_ack32_audit.json")
    ensure(set(entries)==expected, "Expected exactly six raw source files and original audit")
    ensure({f.name for f in folder.glob("*.json")}==expected,
           "Source added, omitted, duplicated or renamed")
    for name, digest in entries.items():
        ensure(hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest,
               "Original source SHA256 altered: "+name)
    return entries


def one_calibrated_model(source_model: dict, target_cal: dict, target_robot: str,
                         k: int) -> dict:
    """Frozen descriptive calibration formula, no NEW trial truth ever used.

    One paired reset seed supplies ONE 'applied' and ONE 'held' label.
    Recenter both motion prototypes on target-domain labelled calibration
    examples, retain as radius floor the full SOURCE-domain response
    envelope, and retain fixed original 2mm residual slack.
    """
    ensure(1 <= k <= 8, "Calibration requires 1 to 8 paired known-truth source seeds")
    ensure(target_cal["robot"]==target_robot,
           "Local target robot calibration provenance mismatched")
    output=copy.deepcopy(source_model)
    output["robot"]=target_robot
    out_rows = target_cal["calibration_source_rows"]
    need_seeds=list(range(CALIB_START[target_robot], CALIB_START[target_robot]+k))
    for truth in LABELS:
        selected=[row for row in out_rows if row["hidden_truth"]==truth
                  and row["seed"] in need_seeds]
        ensure(len(selected)==k and sorted(x["seed"] for x in selected)==need_seeds,
               "Missing complete labelled CALIBRATION paired reset seeds")
        mean=[sum(r["delta_public_xyz"][i] for r in selected)/k for i in range(3)]
        max_resid=max(vecnorm(r["delta_public_xyz"],mean) for r in selected)
        src=source_model["class_models"][truth]
        output["class_models"][truth]["mean_public_motion_m"]=mean
        output["class_models"][truth]["max_calibration_residual_m"]=max_resid
        output["class_models"][truth]["envelope_radius_m"]=max(
            float(src["envelope_radius_m"]), max_resid+ADDITIVE_RADIUS_M)
    return output


def evaluate(rows: list[dict], model: dict) -> dict:
    total={"n":len(rows),"correct_confident":0,
           "wrong_confident":0,"abstain":0,"by_truth":{}}
    for truth in LABELS:
        truth_rows=[r for r in rows if r["truth"]==truth]
        stats={"n":len(truth_rows),"correct":0,"wrong":0,"abstain":0}
        for row in truth_rows:
            original=row["independently_real_physx_stepped_arms"][0]
            ensure(original["control"]=="public_proprio_empirical" and
                   original["hidden_truth"]==truth and
                   original["seed"]==row["seed"],
                   "Original public-proprio source truth/order modified")
            decision=decide(original["delta_public_xyz"],model)
            label=decision["label"]
            stats["correct"]+=int(label==truth)
            stats["abstain"]+=int(label is None)
            stats["wrong"]+=int(label is not None and label!=truth)
        ensure(sum(stats[k] for k in ("correct","abstain","wrong"))==len(truth_rows),
               "Hidden/omitted physical trial case")
        total["correct_confident"]+=stats["correct"]
        total["wrong_confident"]+=stats["wrong"]
        total["abstain"]+=stats["abstain"]
        total["by_truth"][truth]=stats
    ensure(total["n"]==16 and
           total["correct_confident"]+total["wrong_confident"]+total["abstain"]==16,
           "Expected complete sixteen original physically stepped truth conditions")
    return total


def study(folder: Path=DATA) -> dict:
    hashes=immutable_source(folder)
    reaudited=source_audit(folder)
    recorded=json.loads((folder/"full_cross_robot_online_ack32_audit.json").read_text())
    ensure(reaudited==recorded, "Official source-auditor recomputation disagreed")
    ensure(reaudited["source_fresh_truth_conditions"]==32,
           "32 source actual PhysX truth cases required")
    calibration={}
    actual_rows={}
    for robot in ROBOTS:
        calibration[robot]=json.loads(
            (folder/f"cross_robot_proprio_calibration_{robot}.json").read_text())
        ensure(calibration[robot]["robot"]==robot and
               calibration[robot]["seed_range"]==
                   list(range(CALIB_START[robot],CALIB_START[robot]+8)),
               "Historical calibration source seed population changed")
        allrows=[]
        for chunk in (0,1):
            raw=json.loads((folder/f"cross_robot_proprio_{robot}_chunk{chunk}_original8.json").read_text())
            allrows.extend(raw["rows"])
        expected=[(seed,truth) for seed in
                  range(TEST_START[robot],TEST_START[robot]+8) for truth in LABELS]
        ensure([(row["seed"],row["truth"]) for row in allrows]==expected,
               "Post-calibration blind test denominator changed")
        ensure(set(calibration[robot]["seed_range"]).isdisjoint(
               {r["seed"] for r in allrows}),"Target calibration/test seed overlap")
        actual_rows[robot]=allrows
    per_robot={}
    for target in ROBOTS:
        source=next(x for x in ROBOTS if x!=target)
        foreign=calibration[source]["model"]
        self_model=calibration[target]["model"]
        source_means={truth:vecnorm(
            self_model["class_models"][truth]["mean_public_motion_m"],
            foreign["class_models"][truth]["mean_public_motion_m"])
            for truth in LABELS}
        rows=actual_rows[target]
        scores={}
        for k in K:
            model=(foreign if k==0 else one_calibrated_model(
                foreign,calibration[target],target,k))
            scores[str(k)]=evaluate(rows,model)
        native=evaluate(rows,self_model)
        ensure(native["correct_confident"]==16 and
               native["wrong_confident"]==0 and native["abstain"]==0,
               "Native original trained-source results unexpectedly changed")
        per_robot[target]={
            "source_robot_of_foreign_model":source,
            "new_seed_population":list(range(TEST_START[target],TEST_START[target]+8)),
            "new_truth_conditions":16,
            "foreign_native_model_mean_gap_m":source_means,
            "zero_to_eight_TARGET_labeled_reset_seed_PAIRS":scores,
            "independent_native_full_eight_seed_calibration_original":native
        }
    pooled={}
    for k in K:
        t=[per_robot[r]["zero_to_eight_TARGET_labeled_reset_seed_PAIRS"][str(k)]
           for r in ROBOTS]
        pooled[str(k)]={
            "n_physical_robot_truth_conditions":32,
            "distinct_target_robot_reset_seeds":16,
            "local_labeled_reset_seed_pairs_per_robot":k,
            "total_target_calibration_episodes_both_robots":4*k,
            "correct_confident":sum(x["correct_confident"] for x in t),
            "wrong_confident":sum(x["wrong_confident"] for x in t),
            "abstain":sum(x["abstain"] for x in t),
        }
    ensure((pooled["0"]["correct_confident"],pooled["0"]["wrong_confident"],
            pooled["0"]["abstain"])==(0,0,32),"Zero shot negative missing")
    ensure((pooled["1"]["correct_confident"],pooled["1"]["wrong_confident"],
            pooled["1"]["abstain"])==(32,0,0),"One labelled pair exploratory finding changed")
    return {
        "schema":"retrospective_original_cross_robot_ack_response_calibration_portability_v1",
        "research_status":"RETROSPECTIVE_HYPOTHESIS_GENERATING_ONLY",
        "new_physics_run_performed":False,
        "third_party_independent_replication":False,
        "real_robot_or_frozen_ppo_task_transfer":False,
        "original_physx_source_run":SOURCE_RUN,
        "source_original_SHA256_manifest":hashes,
        "test_design":"two native robot charts; all new test seeds fixed in BEFORE-outcome original PhysX source, but THIS zero/one-shot reanalysis was designed AFTER inspecting source outcomes",
        "per_target_robot":per_robot,
        "pooled":pooled,
        "limits":[
            "One shot is one target robot seed with TWO known delivery-truth calibration episodes, not unlabeled zero-cost transfer",
            "Re-centering a constant, fixed-command response prototype is not action-conditioned dynamics learning",
            "Calibration models were evaluated on already-generated test data and the k grid was selected post hoc",
            "Both robot/source/test controllers ran preprogrammed actions, NOT a cross-robot frozen PPO policy task",
            "No proof of 0 future false-label probability, task safety, VLA transfer or generic robot morphology generalization",
            "Existing xArm and Panda task data used a narrow fixed command, fixed controller gains and short probe window",
            "These paired execution truths are not 32 independent policies or robots"
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=DATA)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=study(args.source)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("CROSS_ROBOT_RETROSPECTIVE_ACK_CALIBRATION",
          json.dumps({"states":32,"zero":result["pooled"]["0"],
           "one_labelled_pair":result["pooled"]["1"],
           "not_new_physx":True,"not_ppo_transfer":True},sort_keys=True))


if __name__=="__main__":
    main()
