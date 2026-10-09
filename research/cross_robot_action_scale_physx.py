"""Physical Panda/xArm6 action-amplitude stress of paired-one-seed ACK inference.

Genuine official ManiSkill CPU PhysX native PickCube control, six actually
stepped source comparator worlds per robot/seed/true command delivery/scale.
This is scripted native command-target restoration, NOT PPO policy task success.
The source model calibration and new physical reset seed list are frozen in
CROSS_ROBOT_ACTION_SCALE_32_PRECOMMIT_V1.json before this runner existed.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import mani_skill.envs
import numpy as np

from research.cross_robot_ack_physics import (
    ARM_MODE,TASK,actual_target_after_physics,get_arm,observer_for,
    requested_native,stepping)
from research.cross_robot_online_proprio_classifier import decide,LABELS
from research.cross_robot_ack_calibration_portability import (
    DATA,one_calibrated_model,source_audit,immutable_source)

PROTO="research/CROSS_ROBOT_ACTION_SCALE_32_PRECOMMIT_V1.json"
ROBOT_SEEDS={"panda":610001,"xarm6_robotiq":620001}
SCALES=(0.6,1.35)
CONTROLS=("foreign_zero_shot","paired_fixed","paired_action_scaled",
          "blind_optimistic","blind_pessimistic","privileged_once_after_probe")


def require(x,msg):
    if not x:raise RuntimeError(msg)


def verify_calibrations():
    immutable_source(DATA)
    a=source_audit(DATA)
    canonical=json.loads((DATA/"full_cross_robot_online_ack32_audit.json").read_text())
    require(a==canonical,"Earlier source native PhysX full audit differs")
    return {robot:json.loads((DATA/f"cross_robot_proprio_calibration_{robot}.json").read_text())
            for robot in ROBOT_SEEDS}


def preoutcome():
    p=json.loads(Path(PROTO).read_text())
    require(p["schema"]=="cross_robot_unknown_ack_action_scale_stress_new32_preoutcome_v1",
            "Modified protocol")
    require(p["true_physx_evaluation"]["native_fault_amplitude_scales"]==list(SCALES),
            "Actual physical command amplitudes changed")
    for robot,start in ROBOT_SEEDS.items():
        key="reset_seed_panda" if robot=="panda" else "reset_seed_xarm6_robotiq"
        require(p["true_physx_evaluation"][key]==list(range(start,start+4)),
                "Preregistered unseen robot seeds changed")
    return p


def models_for_robot(robot,calibrations,scale):
    other="xarm6_robotiq" if robot=="panda" else "panda"
    source=calibrations[other]["model"]
    paired=one_calibrated_model(source,calibrations[robot],robot,1)
    scaled=copy.deepcopy(paired)
    c=scaled["class_models"]
    # Locked pre-run action-conditioned AFFINE pilot, no test-data learning.
    held=np.asarray(c["held"]["mean_public_motion_m"],dtype=np.float64)
    applied=np.asarray(c["applied"]["mean_public_motion_m"],dtype=np.float64)
    c["applied"]["mean_public_motion_m"]=(held+scale*(applied-held)).tolist()
    return {
        "foreign_zero_shot":source,"paired_fixed":paired,
        "paired_action_scaled":scaled
    }


def hypothesis_targets(arm,scale):
    observer=observer_for(arm)
    for t in (0,1):
        ticket=observer.prepare(requested_native(t))
        observer.acknowledge(ticket.ticket,applied=True)
    held=observer.pose
    advanced=observer_for(arm)
    advanced.reset(held)
    ticket=advanced.prepare(requested_native(2)*scale)
    advanced.acknowledge(ticket.ticket,applied=True)
    return {"held":held,"applied":advanced.pose}


def public_xyz(arm):
    return np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                      dtype=np.float64).reshape(-1,3)[0].copy()


def legal_inverse(arm,candidate,desired):
    c=arm.config
    require(c.frame=="root_translation:root_aligned_body_rotation" and
            c.use_delta and c.use_target and c.normalize_action,
            "Actual native controller chart unknown, refuse")
    p=np.asarray(candidate.position,dtype=np.float64)
    q=np.asarray(desired.position,dtype=np.float64)
    lo=np.asarray(c.pos_lower,dtype=np.float64).reshape(-1)
    hi=np.asarray(c.pos_upper,dtype=np.float64).reshape(-1)
    if len(lo)==1:lo=np.repeat(lo,3)
    if len(hi)==1:hi=np.repeat(hi,3)
    require(len(lo)==3 and len(hi)==3 and
            np.all(lo<0) and np.all(hi>0),
            "Unverified actual normalized native position chart")
    displacement=q-p
    native=displacement/np.where(displacement>=0,hi,-lo)
    require(np.max(np.abs(native))<=1.0+1e-6,
            "Requested native correction cannot be represented; keep failed original source row")
    return np.r_[np.clip(native,-1,1),np.zeros(3)]


def one_actual_world(robot,seed,scale,truth,control,models):
    env=gym.make(TASK,robot_uids=robot,num_envs=1,obs_mode="state",
                 sim_backend="physx_cpu",reconfiguration_freq=1,
                 control_mode=ARM_MODE,disable_env_checker=True)
    try:
        env.reset(seed=seed)
        controller,arm=get_arm(env)
        hypotheses=hypothesis_targets(arm,scale)
        before=after=None
        for t in range(4):
            actual=(requested_native(t)*scale if t==2 and truth=="applied"
                    else np.zeros(6) if t==2
                    else requested_native(t))
            stepping(env,controller,actual)
            if t==1:before=public_xyz(arm)
            if t==3:after=public_xyz(arm)
        difference=(after-before).tolist()
        read_count=0
        if control in ("foreign_zero_shot","paired_fixed","paired_action_scaled"):
            decision=decide(difference,models[control])
            label=decision["label"]
        elif control=="blind_optimistic":
            label="applied"
            decision={"label":label,"status":"NO_PUBLIC_RESPONSE_USED",
                      "private_target_getter_calls_at_decision":0}
        elif control=="blind_pessimistic":
            label="held"
            decision={"label":label,"status":"NO_PUBLIC_RESPONSE_USED",
                      "private_target_getter_calls_at_decision":0}
        elif control=="privileged_once_after_probe":
            read_count=1
            actual=actual_target_after_physics(arm)
            err={k:float(np.max(np.abs(
                np.asarray(actual.position)-np.asarray(v.position))))
                for k,v in hypotheses.items()}
            compatible=[k for k,e in err.items() if e<=1e-4]
            require(len(compatible)==1,
                    "Privileged controller target read cannot distinguish two actual targets")
            label=compatible[0]
            decision={"label":label,"status":"PRIVILEGED_ONE_TARGET_READ",
                      "private_target_getter_calls_at_decision":1,
                      "goal_candidate_discrepancy_audit_m":err}
        else:raise ValueError("Unregistered source physical comparator")
        record={
            "robot":robot,"seed":seed,"scale":scale,"truth":truth,
            "control":control,"real_physx_cpu":True,
            "source_policy_trained":False,
            "scripted_native_commands_no_frozen_ppo":True,
            "native_controller_keys":list(controller.controllers),
            "step2_actual_delivery":("scaled_native_applied" if truth=="applied"
                                     else "native_zero_held"),
            "step3_common_native_zero_probed":True,
            "original_public_before_xyz":before.tolist(),
            "original_public_after_xyz":after.tolist(),
            "public_delta_xyz":difference,
            "private_target_getter_calls_at_decision":read_count,
            "decision":decision,"wrong_confident_ack_history":(
                None if label is None else label!=truth),
            "refused_ambiguous_public_response":label is None,
            "correction_actually_physx_executed":False,
            "corrected_target_position_linf_m":None,
            "corrected_position_within_1e4_m":False,
        }
        if label is not None:
            try:
                corrected=legal_inverse(arm,hypotheses[label],hypotheses["held"])
            except RuntimeError as e:
                record["native_correction_failure"]=str(e)
            else:
                stepping(env,controller,corrected)
                record["corrective_native6"]=corrected.tolist()
                record["correction_actually_physx_executed"]=True
                # True private state read strictly AFTER the physical corrective
                # command, apart from the explicitly counted privileged comparator.
                attained=actual_target_after_physics(arm)
                err=float(np.max(np.abs(
                    np.asarray(attained.position,dtype=np.float64)-
                    np.asarray(hypotheses["held"].position,dtype=np.float64))))
                record["corrected_target_position_linf_m"]=err
                record["corrected_position_within_1e4_m"]=err<=1e-4
        return record
    finally:
        env.close()


def shard(robot,scale):
    p=preoutcome()
    calibrations=verify_calibrations()
    models=models_for_robot(robot,calibrations,scale)
    first=ROBOT_SEEDS[robot]
    cases=[]
    for seed in range(first,first+4):
        for truth in LABELS:
            six=[one_actual_world(robot,seed,scale,truth,control,models)
                 for control in CONTROLS]
            if (max(np.max(np.abs(
                    np.asarray(x["public_delta_xyz"])-
                    np.asarray(six[0]["public_delta_xyz"]))) for x in six)>1e-4):
                raise RuntimeError("Same reset actual PhysX public response disagrees between control worlds")
            cases.append({
                "seed":seed,"actual_delivery_truth":truth,
                "six_independently_physx_stepped_native_arms":six})
            print("SCALED_NATIVE_ACK_REAL_PHYSX_SOURCE_EPISODE",
                  json.dumps(cases[-1],sort_keys=True),flush=True)
    scores={}
    for control in CONTROLS:
        allarms=[next(x for x in c["six_independently_physx_stepped_native_arms"]
                      if x["control"]==control) for c in cases]
        scores[control]={
            "confident":sum(x["decision"]["label"] is not None for x in allarms),
            "wrong_confident":sum(x["wrong_confident_ack_history"] is True for x in allarms),
            "refusal":sum(x["decision"]["label"] is None for x in allarms),
            "actual_native_target_position_restored":sum(
                x["corrected_position_within_1e4_m"] is True for x in allarms),
            "privileged_decision_reads":sum(
                x["private_target_getter_calls_at_decision"] for x in allarms)
        }
    result={
        "schema":"prospective_cross_robot_action_scale_ack_32_physics_shard_v1",
        "protocol":"research/CROSS_ROBOT_ACTION_SCALE_32_PRECOMMIT_V1.json",
        "robot":robot,"scale":scale,"original_seed_range":list(range(first,first+4)),
        "actual_delivery_truths":list(LABELS),"control_names":list(CONTROLS),
        "original_source_manifest_git_blob":p["previous_source_manifest_git_blob"],
        "task":TASK,"control_mode":ARM_MODE,"real_cpu_physx":True,
        "not_ppo_task_success":True,"not_real_robot_or_network_packet_loss":True,
        "not_independent_external_lab":True,
        "calibration_models":models,
        "cases":cases,"scores":scores
    }
    tag=str(scale).replace(".","p")
    path=Path(f"cross_robot_ack_scale_{robot}_{tag}_original8.json")
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("CROSS_ROBOT_ACTION_SCALE_REAL_PHYSX_RESULT",
          json.dumps({"robot":robot,"scale":scale,"scores":scores},sort_keys=True),
          flush=True)
    return path


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--robot",choices=list(ROBOT_SEEDS),required=True)
    p.add_argument("--scale",type=float,choices=SCALES,required=True)
    a=p.parse_args()
    shard(a.robot,a.scale)
