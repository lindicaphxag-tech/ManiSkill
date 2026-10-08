"""Native two-history common-action experiment.

All four task resets, hidden memory deltas and acceptance tolerances frozen
before implementation: TWO_HISTORY_SE3_ROBUST_NATIVE_FROZEN_V1.json.

Controlled target-controller state replay, not an actual lost-message protocol.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import torch
from scipy.spatial.transform import Rotation
import gymnasium as gym
import mani_skill.envs  # noqa F401

from research.action_abi_history_observer import TargetPose
from two_history_se3_robust import common_two_history_command, Reason


CASES=[
    ("PickCube-v1",13077),("PushCube-v1",14088),
    ("PullCube-v1",15099),("StackCube-v1",16110)
]
SHIFT=np.array([.02,0.,0.])
SHIFT_ROT=Rotation.from_rotvec([0.,0.,.03])
DESIRED_OFFSET=np.array([0.,0.,.005])
BUDGET_POS=.0105
BUDGET_ROT=.0155


def arr(t):
    return t.detach().cpu().numpy().reshape(-1).astype(np.float64).copy()


def control_target(arm):
    t=arm.get_state()["target_pose"]
    a=arr(t)
    return TargetPose.from_arrays(a[:3],a[[4,5,6,3]])


def evaluate(task,seed):
    worlds=[
        gym.make(task,num_envs=1,obs_mode="state",
                 control_mode="pd_ee_target_delta_pose",
                 sim_backend="physx_cpu",reconfiguration_freq=1,
                 disable_env_checker=True)
        for _ in range(2)
    ]
    try:
        for w in worlds: w.reset(seed=seed)
        arms=[w.unwrapped.agent.controller.controllers["arm"] for w in worlds]
        for arm in arms:
            assert arm.config.use_delta and arm.config.use_target
            assert arm.config.frame=="root_translation:root_aligned_body_rotation"
            assert arm._normalize_action
        achieved=[arr(x.ee_pose_at_base.p) for x in arms]
        qpos=[arr(w.unwrapped.agent.robot.get_qpos()) for w in worlds]
        assert np.max(np.abs(achieved[0]-achieved[1]))<1e-8
        assert np.max(np.abs(qpos[0]-qpos[1]))<1e-8

        A=control_target(arms[0])
        state_B=arms[1].get_state()["target_pose"].clone()
        before_B=arr(state_B)
        Bpos=before_B[:3]+SHIFT
        Bq=(
            SHIFT_ROT*Rotation.from_quat(before_B[[4,5,6,3]])
        ).as_quat()
        state_B[:,:3]=torch.as_tensor(Bpos,dtype=state_B.dtype,device=state_B.device)
        state_B[:,3:]=torch.as_tensor(
            Bq[[3,0,1,2]],dtype=state_B.dtype,device=state_B.device
        )
        arms[1].set_state({"target_pose":state_B})
        B=control_target(arms[1])
        assert np.max(np.abs(arr(arms[1].ee_pose_at_base.p)-achieved[1]))<1e-8
        assert np.max(np.abs(arr(worlds[1].unwrapped.agent.robot.get_qpos())-qpos[1]))<1e-8

        desired=TargetPose.from_arrays(
            np.asarray(A.position)+DESIRED_OFFSET,np.asarray(A.quaternion_xyzw)
        )
        old_position_low=arr(arms[0].action_space_low[:3])
        old_position_high=arr(arms[0].action_space_high[:3])
        assert np.allclose(old_position_low,arr(arms[1].action_space_low[:3]))
        assert np.allclose(old_position_high,arr(arms[1].action_space_high[:3]))
        rot_scale=float(arms[0].config.rot_lower)
        assert abs(rot_scale-float(arms[1].config.rot_lower))<1e-8

        opts=dict(
            histories=(A,B),desired=desired,
            pos_lower=old_position_low,pos_upper=old_position_high,
            rot_lower=rot_scale,position_budget_m=BUDGET_POS,
            rotation_budget_rad=BUDGET_ROT,
            hypotheses_complete=True,trusted_provenance=True,
            age_steps=0,max_age_steps=0,
            root_translation_root_left_rotation_verified=True
        )
        # Rejection cases prove the API refuses before physical actuation.
        negative={
            "untrusted":({"trusted_provenance":False},Reason.REFUSE_STALE_OR_UNTRUSTED),
            "stale":({"age_steps":1},Reason.REFUSE_STALE_OR_UNTRUSTED),
            "incomplete":({"hypotheses_complete":False},Reason.REFUSE_INCOMPLETE_HYPOTHESES),
            "unsupported_chart":({"root_translation_root_left_rotation_verified":False},Reason.REFUSE_UNVERIFIED_CONTROLLER),
            "exact_position":({"position_budget_m":.001},Reason.REFUSE_POSITION_BUDGET),
            "exact_orientation":({"rotation_budget_rad":.001},Reason.REFUSE_ROTATION_BUDGET)
        }
        for label,(changes,reason) in negative.items():
            cert=common_two_history_command(**(opts|changes))
            assert cert.reason is reason and cert.normalized_6d is None,(label,cert.reason)
        result=common_two_history_command(**opts)
        assert result.authorized,result.reason
        assert abs(result.worst_position_inf_m-.01)<1e-6
        assert abs(result.worst_orientation_geodesic_rad-.015)<1e-6
        arm=np.array(result.normalized_6d,dtype=np.float64)
        assert np.all(np.abs(arm[:3])<=1.000001)
        assert np.linalg.norm(arm[3:])<1.0

        recorded=[]
        for w in worlds:
            # EXACT SAME action tensor applied to both distinct target-memory
            # worlds via official simulator; gripper action stays neutral.
            physical=torch.as_tensor(
                np.r_[arm,0.],dtype=torch.float32
            ).reshape(1,-1)
            assert physical.shape[-1]==int(np.prod(w.action_space.shape))
            w.step(physical)
            recorded.append(control_target(w.unwrapped.agent.controller.controllers["arm"]))
        errors=[]
        for after in recorded:
            pos_e=float(np.max(np.abs(
                np.asarray(after.position)-np.asarray(desired.position)
            )))
            rot_e=float((
                Rotation.from_quat(desired.quaternion_xyzw).inv()*
                Rotation.from_quat(after.quaternion_xyzw)
            ).magnitude())
            assert pos_e<=.0101,(task,seed,pos_e)
            assert rot_e<=.0151,(task,seed,rot_e)
            errors.append((pos_e,rot_e))
        return {
            "task":task,"seed":seed,"pre_action_robot_states_identical":True,
            "different_hidden_targets_created_by_official_controller_set_state":True,
            "plausible_old_target_A":{
                "position_m":list(A.position),"quaternion_xyzw":list(A.quaternion_xyzw)},
            "plausible_old_target_B":{
                "position_m":list(B.position),"quaternion_xyzw":list(B.quaternion_xyzw)},
            "desired_commanded_target":{
                "position_m":list(desired.position),
                "quaternion_xyzw":list(desired.quaternion_xyzw)},
            "identical_native_action_6d":list(result.normalized_6d),
            "minimax_bound_position_inf_m":result.worst_position_inf_m,
            "minimax_bound_rotation_geodesic_rad":result.worst_orientation_geodesic_rad,
            "world_A_observed_errors_position_inf_m_and_rotation_rad":list(errors[0]),
            "world_B_observed_errors_position_inf_m_and_rotation_rad":list(errors[1]),
            "six_fail_closed_negative_controls":list(negative),
            "actual_policy_task_success_measured":False,
            "unknown_ACK_in_actual_robot_emulated":False,
            "physics_simulated":True,"hardware_safe":False
        }
    finally:
        for w in worlds:w.close()


def main():
    rows=[evaluate(task,seed) for task,seed in CASES]
    assert [(r["task"],r["seed"]) for r in rows]==CASES
    result={
        "schema":"two_history_commanded_pose_minimax_v1",
        "frozen_protocol":"research/TWO_HISTORY_SE3_ROBUST_NATIVE_FROZEN_V1.json",
        "real_native_physx_controlled_cases":4,
        "two_worlds_per_case":2,
        "independently_reproduced":False,
        "robot_hardware_safety_certified":False,
        "results":rows
    }
    Path("two_history_se3_native_real_physx.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print("TWO_HISTORY_SE3_NATIVE_RESULT",json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
