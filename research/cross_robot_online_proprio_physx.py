"""Real PhysX blind-online physical ACK observer, prospective Panda/xArm6 holdout.

Calibration uses labelled EARLIER physics seeds 8 per robot × two truths.
Test uses 8 completely new unseen reset states per robot × two truths ×
three ACTUALLY stepped policy arms. No policy weights. No private target getter
until AFTER the optional real t4 native corrective action has executed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import mani_skill.envs
import numpy as np

from research.cross_robot_ack_physics import (
    ARM_MODE,TASK,actual_target_after_physics,get_arm,observer_for,
    requested_native,stepping)
from research.action_abi_history_observer import ActionHistoryObserver
from research.cross_robot_online_proprio_classifier import LABELS,train,decide

PROTO="research/CROSS_ROBOT_ONLINE_PROPRIO_ACK_PREOUTCOME_V1.json"
PROTO_SHA="0cb66afc8a9c362ee764a83b7e558069ef6bd09c"
OLD={"panda":420001,"xarm6_robotiq":430001}
FRESH={"panda":480001,"xarm6_robotiq":490001}
CONTROLS=("public_proprio_empirical","blind_optimistic","blind_pessimistic")


def _public_xyz(arm):
    return np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                      dtype=np.float64).reshape(-1,3)[0].copy()


def _candidate_target(arm):
    o=observer_for(arm)
    for t in (0,1):
        ticket=o.prepare(requested_native(t))
        o.acknowledge(ticket.ticket,applied=True)
    held=o.pose
    clone=observer_for(arm)
    clone.reset(held)
    ticket=clone.prepare(requested_native(2))
    clone.acknowledge(ticket.ticket,applied=True)
    return {"held":held,"applied":clone.pose}


def _arm_inverse_for_desired_held(arm,candidate,held):
    c=arm.config
    if not (c.frame==ActionHistoryObserver.FRAME and c.use_delta
            and c.use_target and c.normalize_action):
        raise RuntimeError("Unsupported native target controller chart")
    p=np.asarray(candidate.position,dtype=np.float64)
    want=np.asarray(held.position,dtype=np.float64)
    lo=np.asarray(c.pos_lower,dtype=float).reshape(-1)
    hi=np.asarray(c.pos_upper,dtype=float).reshape(-1)
    if lo.size==1:lo=np.repeat(lo,3)
    if hi.size==1:hi=np.repeat(hi,3)
    if not (lo.size==3 and hi.size==3 and np.all(lo<0) and np.all(hi>0)):
        raise RuntimeError("Unverified destination native position chart")
    delta=want-p
    # ManiSkill standard normalized Cartesian native range: positive and
    # negative scales can differ; use the actual one-sided controller bound.
    norm=delta/np.where(delta>=0,hi,-lo)
    if np.max(np.abs(norm))>1+1e-6:
        raise RuntimeError("Corrective action not representable in native chart")
    return np.r_[norm,[0.,0.,0.]].clip(-1,1)


def _sim(robot,seed,truth,*,control=None,model=None):
    if robot not in OLD or truth not in LABELS:
        raise ValueError("Unregistered robot or hidden delivery")
    env=gym.make(TASK,robot_uids=robot,num_envs=1,obs_mode="state",
                 sim_backend="physx_cpu",reconfiguration_freq=1,
                 control_mode=ARM_MODE,disable_env_checker=True)
    try:
        env.reset(seed=seed)
        ctrl,arm=get_arm(env)
        target_hypotheses=_candidate_target(arm)
        public_before=None
        public_after=None
        for t in range(4):
            applied=(t!=2 or truth=="applied")
            action=requested_native(t) if applied else np.zeros(6)
            stepping(env,ctrl,action)
            if t==1:
                public_before=_public_xyz(arm)
            if t==3:
                public_after=_public_xyz(arm)
        d=(public_after-public_before).tolist()
        output=dict(robot=robot,seed=seed,hidden_truth=truth,
                    true_delivery_used_only_to_execute_and_audit=True,
                    public_t1_xyz=public_before.tolist(),
                    public_t3_xyz=public_after.tolist(),
                    delta_public_xyz=d,
                    native_controller_keys=list(ctrl.controllers),
                    unchanged_zero_native_probe_step=3,
                    private_target_read_calls_before_decision=0,
                    correction_reached=False,
                    corrective_target_position_error_m=None)
        if control is None:
            return output
        if control=="public_proprio_empirical":
            decision=decide(d,model)
            guessed=decision["label"]
        elif control=="blind_optimistic":
            decision={"label":"applied","status":"NO_PHYSICAL_RESPONSE_USED",
                      "private_target_getter_calls_at_decision":0}
            guessed="applied"
        elif control=="blind_pessimistic":
            decision={"label":"held","status":"NO_PHYSICAL_RESPONSE_USED",
                      "private_target_getter_calls_at_decision":0}
            guessed="held"
        else:
            raise RuntimeError("Unregistered physical control comparator")
        output["control"]=control
        output["decision"]=decision
        output["wrong_history_authorization"]=(None if guessed is None
            else guessed!=truth)
        output["corrective_refusal"]=guessed is None
        if guessed is not None:
            native=_arm_inverse_for_desired_held(
                arm,target_hypotheses[guessed],target_hypotheses["held"])
            stepping(env,ctrl,native)
            output["corrective_native_six"]=native.tolist()
            output["correction_reached"]=True
            # Only AFTER all decision and corrective actuation. Private
            # target data is used for independent scoring, NEVER feedback.
            actual=actual_target_after_physics(arm)
            achieved=np.asarray(actual.position,dtype=np.float64)
            held=np.asarray(target_hypotheses["held"].position,dtype=np.float64)
            error=float(np.max(np.abs(achieved-held)))
            output["corrective_target_position_error_m"]=error
            output["corrective_commanded_target_within_1e4_m"]=error<=1e-4
        else:
            output["corrective_commanded_target_within_1e4_m"]=False
        return output
    finally:
        env.close()


def verify_proto():
    f=Path(PROTO).read_bytes()
    h=hashlib.sha1(b"blob "+str(len(f)).encode()+b"\0"+f).hexdigest()
    if h!=PROTO_SHA:
        raise RuntimeError("Prospectively frozen protocol Git blob changed")


def calibrate(robot):
    verify_proto()
    rows=[_sim(robot,s,t) for s in range(OLD[robot],OLD[robot]+8)
          for t in LABELS]
    training=[dict(robot=x["robot"],seed=x["seed"],truth=x["hidden_truth"],
                   delta_public_xyz=x["delta_public_xyz"]) for x in rows]
    model=train(training,robot)
    return {"schema":"cross_robot_online_ack_calibration_original16_v1",
            "robot":robot,"seed_range":list(range(OLD[robot],OLD[robot]+8)),
            "truths":list(LABELS),"source_original_method":"cross_robot_ack_physics",
            "original_preoutcome_protocol_git_blob":PROTO_SHA,
            "model":model,"calibration_source_rows":rows,
            "labels_only_from_prior_calibration_known_physics":True,
            "not_outside_independent_replication":True}


def test(robot,chunk,calibration):
    verify_proto()
    if chunk not in (0,1):
        raise ValueError("Test chunk 0 or 1 only")
    if (calibration.get("schema")!="cross_robot_online_ack_calibration_original16_v1"
        or calibration.get("robot")!=robot
        or calibration.get("original_preoutcome_protocol_git_blob")!=PROTO_SHA):
        raise RuntimeError("Untrusted or mismatched model calibration source")
    records=calibration.get("calibration_source_rows",[])
    again=[dict(robot=x["robot"],seed=x["seed"],truth=x["hidden_truth"],
                delta_public_xyz=x["delta_public_xyz"]) for x in records]
    if (len(records)!=16 or train(again,robot)!=calibration.get("model")
        or calibration.get("seed_range")!=list(range(OLD[robot],OLD[robot]+8))):
        raise RuntimeError("Calibration model changed or fabricated")
    model=calibration["model"]
    rows=[]
    seeds=list(range(FRESH[robot]+chunk*4,FRESH[robot]+chunk*4+4))
    for seed in seeds:
        for truth in LABELS:
            trial=[_sim(robot,seed,truth,control=ctrl,model=model)
                   for ctrl in CONTROLS]
            signatures=[r["delta_public_xyz"] for r in trial]
            if max(np.max(np.abs(np.asarray(x)-np.asarray(signatures[0])))
                   for x in signatures)>1e-4:
                raise RuntimeError("Paired native physical probe response changed across comparator reset")
            rows.append(dict(robot=robot,seed=seed,truth=truth,
                             independently_real_physx_stepped_arms=trial,
                             one_online_public_measurement_per_arm=True))
            print("CROSS_ROBOT_PROPRIO_BLIND_EPISODE",
                  json.dumps(rows[-1],sort_keys=True),flush=True)
    totals={c:{
        "confident":sum(not r["independently_real_physx_stepped_arms"][i]["corrective_refusal"] for r in rows),
        "wrong":sum(r["independently_real_physx_stepped_arms"][i]["wrong_history_authorization"] is True for r in rows),
        "actual_held_target_position_restored":sum(r["independently_real_physx_stepped_arms"][i]["corrective_commanded_target_within_1e4_m"] for r in rows)}
        for i,c in enumerate(CONTROLS)}
    result={"schema":"cross_robot_online_unknown_ack_proprio_prospective_v1",
            "robot":robot,"chunk":chunk,"test_seeds":seeds,
            "physical_trial_truth_cases":8,"source_protocol_git_blob":PROTO_SHA,
            "calibration_model_hash":hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest(),
            "model":model,"original_frozen_checkpoint_used":False,
            "scripted_native_control_not_policy_transfer":True,
            "real_cpu_physx":True,
            "private_target_getter_only_after_corrective_action":True,
            "no_actual_network_packet_loss":True,
            "not_robot_collision_force_safety":True,
            "not_independent_outside_lab":True,
            "totals":totals,"rows":rows}
    path=Path(f"cross_robot_proprio_{robot}_chunk{chunk}_original8.json")
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("CROSS_ROBOT_PROPRIO_BLIND_PROSPECTIVE_SUMMARY",
          json.dumps({"robot":robot,"chunk":chunk,"totals":totals},sort_keys=True),
          flush=True)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--robot",choices=list(OLD),required=True)
    p.add_argument("--mode",choices=("calibrate","test"),required=True)
    p.add_argument("--chunk",type=int,choices=(0,1),default=0)
    p.add_argument("--calibration-file",type=Path)
    a=p.parse_args()
    if a.mode=="calibrate":
        result=calibrate(a.robot)
        Path(f"cross_robot_proprio_calibration_{a.robot}.json").write_text(
            json.dumps(result,sort_keys=True,indent=2)+"\n")
        print("CROSS_ROBOT_PROPRIO_CALIBRATION",
              json.dumps(result["model"],sort_keys=True),flush=True)
    else:
        if not a.calibration_file:
            p.error("--calibration-file required for original blind test")
        test(a.robot,a.chunk,json.loads(a.calibration_file.read_text()))


if __name__=="__main__":
    main()
