"""Native PhysX: zero vs fixed nonzero *known-delivered* probe under missing ACK.

SEPARATE scripted (not PPO) Panda and xArm6 PhysX controller worlds.
The common-gain additive observation model predicts no dependence of
between-history *center separation* on a shared native target increment:
 y_h = x + alpha (M_h + u - x) + e;
 y_A - y_H = alpha (M_A - M_H).
This elementary conditional invariance can fail physically when alpha,
contacts, tracking, or residuals depend on the probe. The experiment
measures rather than asserts a nonzero information benefit.

The independent original protocol was committed BEFORE this runner:
  commit 84c0968d26d939c6b758e3cc769613afc9d3e92f
No private controller target getter is called before the observer has
selected its hidden execution-history label and dispatched correction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import gymnasium as gym
import mani_skill.envs
import numpy as np

from research.action_abi_history_observer import TargetPose
from research.cross_robot_ack_physics import (
    ARM_MODE, TASK, actual_target_after_physics, get_arm,
    observer_for, requested_native, stepping,
)
from research.cross_robot_online_proprio_classifier import LABELS, train, decide
from research.cross_robot_online_proprio_physx import _arm_inverse_for_desired_held

PROTO="research/COMMON_PROBE_ZERO_NONZERO_CROSS_ROBOT_PREREG_V1.json"
PROTO_BLOB="c03e7c6d2343ec6fcfe1824d4f4b76f5df00b755"
SRC_BLOBS={
    "research/cross_robot_ack_physics.py":"3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7",
    "research/cross_robot_online_proprio_classifier.py":"b0d7a767b93fb9f7cab2ba70494947ccb4027979",
}
OLD={"panda":420001,"xarm6_robotiq":430001}
FRESH={"panda":660001,"xarm6_robotiq":670001}
PROBES={
    "zero":np.array([0.,0.,0.,0.,0.,0.],dtype=np.float64),
    "nonzero_x":np.array([.15,0.,0.,0.,0.,0.],dtype=np.float64),
}


def check_preoutcome():
    protocol=json.loads(Path(PROTO).read_text("utf-8"))
    def blob(path):
        return subprocess.check_output(["git","hash-object",path],text=True).strip()
    if blob(PROTO)!=PROTO_BLOB:
        raise ValueError("Pre-outcome protocol changed after source freeze")
    for path,expected in SRC_BLOBS.items():
        if blob(path)!=expected:
            raise ValueError("Source robot semantics or classifier changed: "+path)
    if (protocol["probes"]["intervention_nonzero_native6"]!=PROBES["nonzero_x"].tolist()
        or protocol["new_original_blind_seeds"]!={"panda":[660001,660008],"xarm6_robotiq":[670001,670008]}
        or protocol["calibration"]["panda"]!=[420001,420008]
        or protocol["calibration"]["xarm6_robotiq"]!=[430001,430008]
        or protocol["original_trial_structure"]["total_new_physx_truth_probe_worlds"]!=64):
        raise ValueError("Physical probe magnitude, source seeds or matrix changed")
    return protocol


def _pose_xyz(arm):
    return np.asarray(arm.ee_pose_at_base.p.detach().cpu(),dtype=float).reshape(-1,3)[0].copy()


def _possible_targets_after_common_probe(arm,probe):
    """Both prior target memories are computed ONLY from submitted source actions."""
    known=observer_for(arm)
    for t in (0,1):
        ticket=known.prepare(requested_native(t))
        known.acknowledge(ticket.ticket,applied=True)
    before_fault=known.pose
    hypotheses={}
    for history in LABELS:
        observer=observer_for(arm)
        observer.reset(before_fault)
        fault_action=requested_native(2) if history=="applied" else np.zeros(6)
        for action in (fault_action,probe):
            ticket=observer.prepare(action)
            observer.acknowledge(ticket.ticket,applied=True)
        hypotheses[history]=observer.pose
    return hypotheses


def original_trial(robot,seed,truth,probe_id,*,model=None):
    if robot not in OLD or truth not in LABELS or probe_id not in PROBES:
        raise ValueError("Unknown physical robot/fault/probe identity")
    probe=PROBES[probe_id]
    env=gym.make(TASK,robot_uids=robot,num_envs=1,obs_mode="state",
                 sim_backend="physx_cpu",reconfiguration_freq=1,
                 control_mode=ARM_MODE,disable_env_checker=True)
    try:
        env.reset(seed=int(seed))
        ctrl,arm=get_arm(env)
        hypotheses=_possible_targets_after_common_probe(arm,probe)
        physical_before=physical_after=None
        for t in range(4):
            actual=(np.zeros(6) if (t==2 and truth=="held")
                    else probe if t==3 else requested_native(t))
            stepping(env,ctrl,actual)
            if t==1:
                physical_before=_pose_xyz(arm)
            if t==3:
                physical_after=_pose_xyz(arm)
        public_delta=physical_after-physical_before
        row={
            "robot":robot,"seed":int(seed),"hidden_physical_truth_posthoc_only":truth,
            "known_delivered_native_probe_id":probe_id,
            "actual_native_t3_probe_six":probe.tolist(),
            "public_xyz_after_t1":physical_before.tolist(),
            "public_xyz_after_t3":physical_after.tolist(),
            "delta_public_xyz":public_delta.tolist(),
            "real_physx_cpu":True,
            "command_execution_ack_hidden_from_classifier":True,
            "private_target_reads_before_classification":0,
            "private_target_reads_before_correction":0,
            "robot_native_controller_keys":list(ctrl.controllers),
            "scripted_native_no_policy_training":True,
        }
        if model is None:
            return row
        decision=decide(row["delta_public_xyz"],model)
        history=decision["label"]
        row["decision"]=decision
        row["wrong_confident_history"]=None if history is None else history!=truth
        row["refusal"]=history is None
        row["target_correction_reached"]=False
        row["commanded_target_post_correction_error_inf_m"]=None
        row["target_restored_below_1e4_m"]=False
        if history is not None:
            native=_arm_inverse_for_desired_held(
                arm,hypotheses[history],hypotheses["held"])
            stepping(env,ctrl,native)
            # Private oracle is AUDIT-ONLY AFTER the decision and
            # corrective physical step. Never supply it to the observer.
            true_target=actual_target_after_physics(arm)
            error=float(np.max(np.abs(
                np.asarray(true_target.position,dtype=float)-
                np.asarray(hypotheses["held"].position,dtype=float)
            )))
            row["corrective_native_six"]=native.tolist()
            row["target_correction_reached"]=True
            row["commanded_target_post_correction_error_inf_m"]=error
            row["target_restored_below_1e4_m"]=error<=1e-4
            row["private_target_reads_post_dispatch_audit_only"]=1
        else:
            row["private_target_reads_post_dispatch_audit_only"]=0
        return row
    finally:
        env.close()


def original_calibration(robot):
    check_preoutcome()
    rows=[original_trial(robot,seed,truth,probe_id)
          for seed in range(OLD[robot],OLD[robot]+8)
          for truth in LABELS for probe_id in PROBES]
    fitted={}
    for probe_id in PROBES:
        chosen=[dict(robot=r["robot"],seed=r["seed"],
                     truth=r["hidden_physical_truth_posthoc_only"],
                     delta_public_xyz=r["delta_public_xyz"])
                for r in rows if r["known_delivered_native_probe_id"]==probe_id]
        fitted[probe_id]=train(chosen,robot)
    return {
        "schema":"original_dual_robot_two_probe_physical_calibration_v1",
        "robot":robot,"prior_source_seeds":list(range(OLD[robot],OLD[robot]+8)),
        "both_truths":list(LABELS),"both_physical_probes":list(PROBES),
        "preoutcome_proto_blob":PROTO_BLOB,
        "empirical_envelopes_by_probe":fitted,
        "physical_calibration_source_rows":rows,
        "no_independently_attested_response_noise_bound":True,
        "scripted_native_no_policy_transfer":True,
    }


def validate_calibration(cal,robot):
    if (cal.get("schema")!="original_dual_robot_two_probe_physical_calibration_v1"
        or cal.get("robot")!=robot
        or cal.get("prior_source_seeds")!=list(range(OLD[robot],OLD[robot]+8))
        or cal.get("both_truths")!=list(LABELS)
        or cal.get("both_physical_probes")!=list(PROBES)
        or cal.get("preoutcome_proto_blob")!=PROTO_BLOB):
        raise ValueError("Calibration source protocol or robot is wrong")
    all_rows=cal["physical_calibration_source_rows"]
    if len(all_rows)!=32:
        raise ValueError("One actual physical calibration arm missing")
    seen=set()
    for row in all_rows:
        k=(row["seed"],row["hidden_physical_truth_posthoc_only"],row["known_delivered_native_probe_id"])
        if k in seen or row["seed"] not in range(OLD[robot],OLD[robot]+8):
            raise ValueError("Duplicate or nontraining calibration seed/truth/probe")
        seen.add(k)
    for probe_id in PROBES:
        chosen=[dict(robot=r["robot"],seed=r["seed"],
                     truth=r["hidden_physical_truth_posthoc_only"],
                     delta_public_xyz=r["delta_public_xyz"])
                for r in all_rows if r["known_delivered_native_probe_id"]==probe_id]
        if train(chosen,robot)!=cal["empirical_envelopes_by_probe"][probe_id]:
            raise ValueError("Claimed trained response envelope does not match actual calibrations")
    return True


def original_test(robot,chunk,cal):
    check_preoutcome()
    validate_calibration(cal,robot)
    if type(chunk) is not int or chunk not in (0,1):
        raise ValueError("Only two predeclared 4-seed original shards accepted")
    seeds=list(range(FRESH[robot]+4*chunk,FRESH[robot]+4*chunk+4))
    original=[]
    models=cal["empirical_envelopes_by_probe"]
    for seed in seeds:
        for truth in LABELS:
            trials=[original_trial(robot,seed,truth,probe_id,model=models[probe_id])
                    for probe_id in PROBES]
            row={"robot":robot,"seed":seed,
                 "actual_execution_truth_score_only":truth,
                 "original_two_physically_stepped_probe_worlds":trials}
            original.append(row)
            print("NATIVE_TWO_PROBE_FRESH_BLIND_PHYSX",json.dumps(row,sort_keys=True),flush=True)
    stats={}
    for probe_id in PROBES:
        rows=[next(x for x in z["original_two_physically_stepped_probe_worlds"]
                   if x["known_delivered_native_probe_id"]==probe_id) for z in original]
        stats[probe_id]={
            "confidence_coverage":sum(not x["refusal"] for x in rows),
            "wrong_confident_label_count":sum(x["wrong_confident_history"] is True for x in rows),
            "abstentions":sum(x["refusal"] for x in rows),
            "actual_held_commanded_XYZ_corrected":sum(x["target_restored_below_1e4_m"] for x in rows),
            "private_decision_target_reads":sum(x["private_target_reads_before_classification"] for x in rows),
        }
    result={
        "schema":"zero_nonzero_common_probe_cross_robot_fresh16_truth_probes_v1",
        "robot":robot,"chunk":chunk,"original_seed_register":seeds,
        "preoutcome_proto_blob":PROTO_BLOB,
        "calibration_sha256":hashlib.sha256(json.dumps(cal,sort_keys=True).encode()).hexdigest(),
        "source_chart_git_blobs":SRC_BLOBS,
        "test_worlds_actual_native_PhysX":16,
        "both_actuation_truths_and_actual_probes":True,
        "private_target_getter_never_used_in_decision":True,
        "truth_used_only_for_actuation_and_posthoc_score":True,
        "full_task_success_not_tested":True,
        "not_independent_external_research":True,
        "statistics":stats,"rows":original,
    }
    file=Path(f"native_two_probes_{robot}_chunk{chunk}_original16.json")
    file.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("NATIVE_TWO_PROBE_ORIGINAL_SUMMARY",json.dumps(
        {"robot":robot,"chunk":chunk,"stats":stats},sort_keys=True),flush=True)
    return result


def self_test():
    assert FRESH=={"panda":660001,"xarm6_robotiq":670001}
    assert set(PROBES)=={"zero","nonzero_x"}
    assert PROBES["nonzero_x"].tolist()==[0.15,0,0,0,0,0]
    assert all(np.linalg.norm(v[3:])<=1 and np.max(np.abs(v))<=1 for v in PROBES.values())
    # The common-gain model's observable history CENTER separation is
    # independent of the SHARED common native probe translation.
    x=np.array([0.0,.12,-.1]); a=np.array([.03,.01,.16]); b=np.array([-.02,.01,.16])
    for alpha in (.1,.35,.9):
        baseline=alpha*(a-b)
        for u in PROBES.values():
            diff=(x+alpha*(a+u[:3]-x))-(x+alpha*(b+u[:3]-x))
            assert np.allclose(diff,baseline,atol=1e-14)
    print("PASS frozen dualrobot 64 new PhysX source worlds and conditional common-input invariance")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--robot",choices=list(OLD),required=True)
    parser.add_argument("--mode",choices=("self-test","calibrate","test"),required=True)
    parser.add_argument("--chunk",type=int,choices=(0,1),default=0)
    parser.add_argument("--calibration-file",type=Path)
    args=parser.parse_args()
    if args.mode=="self-test":
        self_test()
        check_preoutcome()
        return
    if args.mode=="calibrate":
        cal=original_calibration(args.robot)
        out=Path(f"two_probe_prior_calibration_{args.robot}.json")
        out.write_text(json.dumps(cal,indent=2,sort_keys=True)+"\n")
        print("NATIVE_TWO_PROBE_CALIBRATION",json.dumps({
            "robot":args.robot,
            "probe_empirical_class_models":cal["empirical_envelopes_by_probe"]
        },sort_keys=True),flush=True)
        return
    if args.calibration_file is None:
        parser.error("--calibration-file required for blind original new seeds")
    original_test(args.robot,args.chunk,json.loads(args.calibration_file.read_text()))


if __name__=="__main__":
    main()
