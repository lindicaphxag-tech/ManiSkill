"""Prospective out-of-distribution ACTION AMPLITUDE stress for two real PhysX robots.

FROZEN original public achieved-motion classifier versus predeclared command
conditioned alternative. Four actual native PhysX robot-control worlds per
truth per held-out seed; ZERO private target reads before corrective actuation.
Only after actual native arm correction may true target be audited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import mani_skill.envs
import numpy as np

from research.action_abi_history_observer import ActionHistoryObserver
from research.cross_robot_ack_physics import (
    ARM_MODE,TASK,actual_target_after_physics,get_arm,observer_for,requested_native,stepping)
from research.cross_robot_online_proprio_classifier import LABELS,train
from research.cross_robot_online_proprio_physx import (
    _public_xyz,_arm_inverse_for_desired_held)
from research.cross_robot_ack_amplitude_inference import predict

PREREG="research/CROSS_ROBOT_ACK_AMPLITUDE_SHIFT_PREOUTCOME_V1.json"
PREREG_GIT_BLOB="24ac966eecb765a609b3f5601c755216b24501c3"
CALDIR=Path("research/frozen_policy_transfer/evidence/cross_robot_online_public_proprio_new32_480001_490008")
TASK_SEEDS={"panda":540001,"xarm6_robotiq":550001}
AMPLITUDES={"shift040":0.4,"nominal100":1.0}
CONTROLS=("frozen_scale1","command_affine","optimistic_applied","pessimistic_held")

def assert_frozen():
    raw=Path(PREREG).read_bytes()
    git_blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if git_blob!=PREREG_GIT_BLOB:
        raise RuntimeError("Preoutcome physical amplitude shift protocol altered")
    params=json.loads(raw)
    if params["amplitude_multipliers"]!=[0.4,1.0] or params["new_test_seeds"]!={"panda":[540001,540004],"xarm6_robotiq":[550001,550004]}:
        raise RuntimeError("Original tests/seeds changed")

def load_calibration(robot):
    path=CALDIR/f"cross_robot_proprio_calibration_{robot}.json"
    raw=json.loads(path.read_text())
    if (raw.get("schema")!="cross_robot_online_ack_calibration_original16_v1"
        or raw.get("robot")!=robot
        or raw.get("original_preoutcome_protocol_git_blob")!="0cb66afc8a9c362ee764a83b7e558069ef6bd09c"):
        raise RuntimeError("Source archive calibration provenance mismatch")
    training=[dict(robot=r["robot"],seed=r["seed"],truth=r["hidden_truth"],
                   delta_public_xyz=r["delta_public_xyz"])
              for r in raw["calibration_source_rows"]]
    model=train(training,robot)
    if model!=raw["model"]:
        raise RuntimeError("Calibration source rows do not regenerate original model")
    if set(model["training_seeds"]) != set(range(420001 if robot=="panda" else 430001,
                                               420009 if robot=="panda" else 430009)):
        raise RuntimeError("Calibration seeds overlap the held-out stress cases")
    return model

def candidate_held_and_applied(arm,amplitude):
    observer=observer_for(arm)
    for t in (0,1):
        ticket=observer.prepare(requested_native(t))
        observer.acknowledge(ticket.ticket,applied=True)
    held=observer.pose
    altered=observer_for(arm)
    altered.reset(held)
    ticket=altered.prepare(requested_native(2)*amplitude)
    altered.acknowledge(ticket.ticket,applied=True)
    return {"held":held,"applied":altered.pose}

def physically_execute(robot,seed,truth,amplitude,control,model):
    if (robot not in TASK_SEEDS or truth not in LABELS
        or amplitude not in tuple(AMPLITUDES.values()) or control not in CONTROLS):
        raise ValueError("Unknown frozen paired physical trial condition")
    env=gym.make(TASK,robot_uids=robot,num_envs=1,
                 obs_mode="state",sim_backend="physx_cpu",
                 reconfiguration_freq=1,control_mode=ARM_MODE,
                 disable_env_checker=True)
    try:
        env.reset(seed=seed)
        ctrl,arm=get_arm(env)
        cands=candidate_held_and_applied(arm,amplitude)
        before=after=None
        for step in range(4):
            native=requested_native(step)
            if step==2:
                native=native*amplitude if truth=="applied" else np.zeros(6)
            if step==3:
                native=np.zeros(6)
            stepping(env,ctrl,native)
            if step==1:
                before=_public_xyz(arm)
            if step==3:
                after=_public_xyz(arm)
        observed=(after-before).tolist()
        if control in ("frozen_scale1","command_affine"):
            decision=predict(observed,model,amplitude,control)
        elif control=="optimistic_applied":
            decision={"label":"applied","status":"FIXED_UNINFORMED_APPLIED",
                      "private_target_getter_calls_at_decision":0}
        else:
            decision={"label":"held","status":"FIXED_UNINFORMED_HELD",
                      "private_target_getter_calls_at_decision":0}
        selected=decision["label"]
        row=dict(robot=robot,seed=seed,truth=truth,amplitude=amplitude,
                 control=control,action_native_t2_requested=(requested_native(2)*amplitude).tolist(),
                 action_native_t2_physical=(requested_native(2)*amplitude if truth=="applied" else np.zeros(6)).tolist(),
                 probe_native_t3=[0.]*6,
                 public_achieved_xyz_t1=before.tolist(),
                 public_achieved_xyz_t3=after.tolist(),
                 public_motion_delta_xyz=observed,
                 controller_keys=list(ctrl.controllers),
                 inference=decision,
                 incorrect_confident_history_authorization=(
                     None if selected is None else selected!=truth),
                 refused_due_ambiguous_history=selected is None,
                 private_target_reads_before_and_during_decision=0,
                 correction_physically_executed=False,
                 corrected_target_position_linf_m=None,
                 commanded_target_restored_within_1e4_m=False,
                 original_model_not_refit=True)
        if selected is not None:
            native=_arm_inverse_for_desired_held(arm,cands[selected],cands["held"])
            stepping(env,ctrl,native)
            # Privileged comparison is strictly after the native corrective
            # controller action has already been PHYSICALLY STEPPED.
            actual=actual_target_after_physics(arm)
            error=float(np.max(np.abs(
                np.asarray(actual.position)-np.asarray(cands["held"].position))))
            row.update(correction_physically_executed=True,
                       corrective_native_action=native.tolist(),
                       corrected_target_position_linf_m=error,
                       commanded_target_restored_within_1e4_m=error<=1e-4)
        return row
    finally:
        env.close()

def execute(robot,amplitude_tag):
    assert_frozen()
    if robot not in TASK_SEEDS or amplitude_tag not in AMPLITUDES:
        raise ValueError("Only original robot × amplitude study groups permitted")
    model=load_calibration(robot)
    amp=AMPLITUDES[amplitude_tag]
    seeds=list(range(TASK_SEEDS[robot],TASK_SEEDS[robot]+4))
    rows=[]
    for seed in seeds:
        for truth in LABELS:
            trials=[physically_execute(robot,seed,truth,amp,c,model) for c in CONTROLS]
            # The 4 actual control worlds must match public pre-correction
            # evidence to detect accidental different reset or wrong ABI.
            base=np.asarray(trials[0]["public_motion_delta_xyz"])
            if any(np.max(np.abs(base-np.asarray(r["public_motion_delta_xyz"])))>1e-4 for r in trials[1:]):
                raise RuntimeError("Paired physical worlds differ before correction")
            record=dict(seed=seed,robot=robot,physical_truth=truth,amplitude=amp,
                        four_actual_physx_control_worlds=trials)
            rows.append(record)
            print("CROSS_ROBOT_AMP_OOD_ORIGINAL_EPISODE",json.dumps(record,sort_keys=True),flush=True)
    totals={c:{
        "authorized":sum(r["four_actual_physx_control_worlds"][i]["correction_physically_executed"] for r in rows),
        "wrong_history":sum(r["four_actual_physx_control_worlds"][i]["incorrect_confident_history_authorization"] is True for r in rows),
        "target_position_restored":sum(r["four_actual_physx_control_worlds"][i]["commanded_target_restored_within_1e4_m"] for r in rows)}
        for i,c in enumerate(CONTROLS)}
    out=dict(schema="cross_robot_ack_amplitude_shift_falsifier_original_physx_v1",
             preregistration=PREREG,prereg_git_blob=PREREG_GIT_BLOB,
             robot=robot,amplitude_tag=amplitude_tag,amplitude=amp,seeds=seeds,
             prior_model_sha256=hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest(),
             prior_model_fixed=True,physx_cpu=True,no_predecision_private_target=True,
             total_truth_cases=8,all_four_controls_real_native_physx=True,
             no_frozen_PPO_or_task_success_claim=True,no_external_replication=True,
             no_real_packet_loss=True,totals=totals,rows=rows)
    path=Path(f"cross_robot_amp_{robot}_{amplitude_tag}_original8.json")
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("CROSS_ROBOT_AMP_SHIFT_PHYSX_SUMMARY",json.dumps({
        "robot":robot,"amplitude_tag":amplitude_tag,"n_truth_cases":len(rows),
        "totals":totals},sort_keys=True),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--robot",choices=list(TASK_SEEDS),required=True)
    p.add_argument("--amplitude-tag",choices=list(AMPLITUDES),required=True)
    a=p.parse_args()
    execute(a.robot,a.amplitude_tag)

if __name__=="__main__":
    main()
