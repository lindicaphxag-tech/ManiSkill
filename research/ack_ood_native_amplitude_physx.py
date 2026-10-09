"""Prospectively frozen out-of-amplitude native PhysX ACK classifier falsifier.

Two ACTUAL robots, both applied/held physical ACK worlds for each NEW seed.
Four matched genuinely stepped recovery controllers per physical truth.
Policy/task success is NOT measured. Nothing in the action path reads
controller private target state until AFTER executing real correction.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

import gymnasium as gym
import mani_skill.envs
import numpy as np

from research.cross_robot_ack_physics import (
    ARM_MODE,TASK,get_arm,observer_for,requested_native,stepping,
    actual_target_after_physics)
from research.cross_robot_online_proprio_physx import _arm_inverse_for_desired_held
from research.cross_robot_online_proprio_classifier import train,decide
from research.ood_ack_motion_response import predict_ood_public_history

PROTO="research/OOD_ACK_PUBLIC_MOTION_PROSPECTIVE_V1.json"
PROTO_SHA="d1f017d8ca994ec6be62daf3dc6940f038b8dff4"
ORIGINAL_DATA=Path("research/frozen_policy_transfer/evidence/"
  "cross_robot_online_public_proprio_new32_480001_490008")
MODELS_SHA={"panda":"f41bd0cc010cdcaf836a6d8ba2722313baf692d3",
             "xarm6_robotiq":"e8ec9c607059c3e538d2e1bfe35f0fdf1bd89830"}
BASE={("panda","low"):680001,("panda","high"):681001,
      ("xarm6_robotiq","low"):690001,("xarm6_robotiq","high"):691001}
FACTOR={"low":0.55,"high":1.45}
LABELS=("applied","held")
METHODS=("frozen_old_empirical","gain_segment_empirical","blind_optimistic","blind_pessimistic")


def _git_sha(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\\0"+b).hexdigest()


def frozen_provenance():
    b=Path(PROTO).read_bytes()
    if _git_sha(b)!=PROTO_SHA:
        raise RuntimeError("Original preregistration source changed")
    return _git_sha(b)


def locked_model(robot):
    p=ORIGINAL_DATA/f"cross_robot_proprio_calibration_{robot}.json"
    if _git_sha(p.read_bytes())!=MODELS_SHA[robot]:
        raise RuntimeError("Original prior calibrated model/source changed")
    d=json.loads(p.read_text())
    if d.get("robot")!=robot or d.get("schema")!="cross_robot_online_ack_calibration_original16_v1":
        raise RuntimeError("Prior calibration robot/source not original")
    raw=d.get("calibration_source_rows",[])
    rec=[dict(robot=r["robot"],seed=r["seed"],truth=r["hidden_truth"],
              delta_public_xyz=r["delta_public_xyz"]) for r in raw]
    if len(rec)!=16 or train(rec,robot)!=d.get("model"):
        raise RuntimeError("Original calibration cannot be reproduced from source rows")
    return d["model"]


def target_hypotheses(arm,scaled_t2):
    observer=observer_for(arm)
    for t in (0,1):
        ticket=observer.prepare(requested_native(t))
        observer.acknowledge(ticket.ticket,applied=True)
    held=observer.pose
    candidate=observer_for(arm)
    candidate.reset(held)
    ticket=candidate.prepare(scaled_t2)
    candidate.acknowledge(ticket.ticket,applied=True)
    return dict(held=held,applied=candidate.pose)


def public_xyz(arm):
    return np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                      dtype=np.float64).reshape(-1,3)[0].copy()


def actual_physical_world(robot,seed,truth,method,scale,prior_model):
    env=gym.make(TASK,robot_uids=robot,num_envs=1,obs_mode="state",
                 sim_backend="physx_cpu",reconfiguration_freq=1,
                 control_mode=ARM_MODE,disable_env_checker=True)
    try:
        env.reset(seed=seed)
        ctrl,arm=get_arm(env)
        commanded=requested_native(2)*scale
        if np.max(np.abs(commanded))>1 or np.linalg.norm(commanded[3:])>=1:
            raise RuntimeError("New stress native command outside actual controller action ball")
        targets=target_hypotheses(arm,commanded)
        before_t1=None
        before_t3=None
        after_t3=None
        for t in range(4):
            native=(commanded if t==2 else requested_native(t))
            if t==2 and truth=="held":
                native=np.zeros(6,dtype=float)
            if t==1:
                stepping(env,ctrl,native)
                before_t1=public_xyz(arm)
            elif t==3:
                before_t3=public_xyz(arm)
                if np.max(np.abs(native))!=0:
                    raise RuntimeError("Probe must be known native zero command")
                stepping(env,ctrl,native)
                after_t3=public_xyz(arm)
            else:
                stepping(env,ctrl,native)
        old_delta=(after_t3-before_t1).tolist()
        if method=="frozen_old_empirical":
            decision=decide(old_delta,prior_model)
            label=decision["label"]
        elif method=="gain_segment_empirical":
            decision=predict_ood_public_history(
                robot=robot,public_before_xyz=before_t3,
                public_after_xyz=after_t3,
                applied_history_target_xyz=targets["applied"].position,
                held_history_target_xyz=targets["held"].position)
            label=decision["label"]
        elif method in ("blind_optimistic","blind_pessimistic"):
            label="applied" if method=="blind_optimistic" else "held"
            decision=dict(label=label,status="FIXED_NO_PUBLIC_DECISION",
                          no_privileged_state_reads_for_inference=True)
        else:
            raise RuntimeError("Wrong method")
        row=dict(robot=robot,seed=seed,truth=truth,method=method,
                 native_scale=scale,fault_native_zero_physically_dispatched=truth=="held",
                 native_t2_requested_6d=commanded.tolist(),
                 native_t3_known_delivered_probe_6d=[0.]*6,
                 model_sha256=hashlib.sha256(json.dumps(prior_model,sort_keys=True).encode()).hexdigest(),
                 public_t1_xyz=before_t1.tolist(),
                 public_t3_before_xyz=before_t3.tolist(),
                 public_t3_after_xyz=after_t3.tolist(),
                 old_method_delta_public_t1_t3=old_delta,
                 public_response_current_probe_delta=(after_t3-before_t3).tolist(),
                 public_hypothesis_target_xyz={key:list(pose.position) for key,pose in targets.items()},
                 decision=decision,private_target_calls_at_decision=0,
                 wrong_confident_history_label=(None if label is None else label!=truth),
                 refusal=label is None,corrective_action_executed=False,
                 correct_commanded_target_POSITION_only=False,
                 after_physics_private_target_position_error_m=None)
        if label is not None:
            native=_arm_inverse_for_desired_held(arm,targets[label],targets["held"])
            row["corrective_native_6d"]=native.tolist()
            stepping(env,ctrl,native)
            row["corrective_action_executed"]=True
            # Only audit a hidden target AFTER all physical control actions.
            actual=actual_target_after_physics(arm)
            error=float(np.max(np.abs(np.asarray(actual.position)
                                      -np.asarray(targets["held"].position))))
            row["after_physics_private_target_position_error_m"]=error
            row["correct_commanded_target_POSITION_only"]=error<=1e-4
        return row
    finally:
        env.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--robot",choices=("panda","xarm6_robotiq"),required=True)
    parser.add_argument("--scale",choices=("low","high"),required=True)
    parser.add_argument("--chunk",type=int,choices=(0,1),required=True)
    args=parser.parse_args()
    ph=frozen_provenance()
    model=locked_model(args.robot)
    first=BASE[(args.robot,args.scale)]+4*args.chunk
    seeds=list(range(first,first+4))
    scale=FACTOR[args.scale]
    rows=[]
    for seed in seeds:
        for truth in LABELS:
            arms=[]
            for method in METHODS:
                row=actual_physical_world(args.robot,seed,truth,method,scale,model)
                arms.append(row)
            if any(np.max(np.abs(
                np.asarray(arms[0]["public_t3_after_xyz"])-
                np.asarray(a["public_t3_after_xyz"])))>1e-4 for a in arms[1:]):
                raise RuntimeError("Pair-matched public native motion differs across real physical comparator worlds")
            rows.append(dict(seed=seed,truth=truth,actual_native_physical_controllers=arms))
            print("OOD_ACK_NATIVE_PHYSX_TRUTH",json.dumps(dict(robot=args.robot,scale=args.scale,
                  seed=seed,truth=truth,methods={
                   a["method"]:{"label":a["decision"]["label"],
                   "restored":a["correct_commanded_target_POSITION_only"]}
                   for a in arms}),sort_keys=True),flush=True)
    result=dict(schema="ack_ood_native_amplitude_physx_v1",protocol_git_blob=ph,
                robot=args.robot,scale=args.scale,scale_factor=scale,chunk=args.chunk,
                seeds=seeds,physical_truth_conditions=8,physical_comparator_worlds=32,
                source_model_Git_blob=MODELS_SHA[args.robot],real_physx_cpu=True,
                no_ppo_checkpoint_or_task_success_measured=True,rows=rows)
    out=f"ood_ack_{args.robot}_{args.scale}_chunk{args.chunk}_original8.json"
    Path(out).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("OOD_ACK_NATIVE_PHYSX_ORIGINAL",json.dumps(
          dict(robot=args.robot,scale=args.scale,seeds=seeds,truths=8,
               summary={m:dict(correct=sum(r["actual_native_physical_controllers"][i]
                    ["correct_commanded_target_POSITION_only"] for r in rows),
                               wrong=sum(r["actual_native_physical_controllers"][i]
                    ["wrong_confident_history_label"] is True for r in rows),
                               abstain=sum(r["actual_native_physical_controllers"][i]
                    ["refusal"] for r in rows)) for i,m in enumerate(METHODS)}),
            sort_keys=True),flush=True)


if __name__=="__main__":
    main()
