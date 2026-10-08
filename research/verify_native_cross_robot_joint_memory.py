"""Actual two-robot native joint-action/hidden-memory contract evidence.

This deliberately does NOT use a Panda model, and does NOT assume the
composite action has any fixed width or a fixed gripper slot.

Frozen source: research/LATENT_MEMORY_CROSS_ROBOT_PRECOMMIT_V1.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch

import mani_skill.envs  # noqa F401 -- official task and robot registry
from latent_target_memory_cert import (
    TransportRequest, Verdict, certify_box_memory_transport,
)

CASES = [
    ("fetch",1271), ("fetch",1282),
    ("xarm6_robotiq",2373), ("xarm6_robotiq",2384),
]
DELTA_RAD = np.array(
    [0.006,-0.004,0.005,-0.002,0.003,0.004,-0.005],dtype=np.float64
)
RADIUS_RAD = 0.001
BUDGET_RAD = 0.0015
TOLERANCE_RAD = 0.0001


def tovec(tensor):
    return np.asarray(tensor.detach().cpu().numpy(),dtype=np.float64).reshape(-1).copy()


def run(robot,seed):
    env = gym.make(
        "PickCube-v1",
        robot_uids=robot,
        num_envs=1,
        obs_mode="state",
        control_mode="pd_joint_target_delta_pos",
        sim_backend="physx_cpu",
        reconfiguration_freq=1,
        disable_env_checker=True,
    )
    try:
        env.reset(seed=seed)
        agent=env.unwrapped.agent
        controller=agent.controller
        arm=controller.controllers["arm"]
        assert arm.config.use_delta and arm.config.use_target
        assert arm._normalize_action

        target_before=tovec(arm._target_qpos)
        observed_qpos=tovec(arm.qpos)
        n=len(target_before)
        assert n in (6,7), f"Unregistered arm dimension {n}"
        assert len(observed_qpos)==n
        deltas=DELTA_RAD[:n]
        desired=target_before+deltas

        low=tovec(arm.action_space_low)
        high=tovec(arm.action_space_high)
        assert len(low)==len(high)==n
        assert np.all(high>low)
        assert np.allclose(low, float(arm.config.lower))
        assert np.allclose(high, float(arm.config.upper))

        def get_request(*, trust=True, age=0, verified=True, width=RADIUS_RAD):
            return TransportRequest(
                desired_target=tuple(desired),
                memory_lower=tuple(target_before-width),
                memory_upper=tuple(target_before+width),
                command_lower=tuple(low),
                command_upper=tuple(high),
                error_budget=BUDGET_RAD,
                trusted_memory_attestation=trust,
                memory_age_steps=age,max_memory_age_steps=0,
                additive_controller_contract_verified=verified,
            )
        failures={
            "untrusted":(get_request(trust=False),Verdict.REFUSE_UNTRUSTED_MEMORY),
            "stale":(get_request(age=1),Verdict.REFUSE_STALE_MEMORY),
            "unverified":(get_request(verified=False),Verdict.REFUSE_UNVERIFIED_CONTROLLER),
            "unobservable_box":(
                get_request(width=0.02),Verdict.REFUSE_GEOMETRICALLY_IMPOSSIBLE
            ),
        }
        for label,(request, expected) in failures.items():
            result=certify_box_memory_transport(request)
            assert result.verdict is expected and result.command is None,label

        certificate=certify_box_memory_transport(get_request())
        assert certificate.verdict is Verdict.AUTHORIZE_COMMANDED_TARGET
        assert abs(certificate.optimal_worst_case_setpoint_error-RADIUS_RAD)<1e-8
        physical_action=np.asarray(certificate.command,dtype=np.float64)
        normalized=2*(physical_action-low)/(high-low)-1
        assert np.all(np.abs(normalized)<=1.000001)

        # Distinct robots have different action counts and non-arm subcontrollers:
        # Fetch has body and base; XArm6 Robotiq has active/passive fingers.
        # Ask the production controller itself to assemble the native vector.
        native_width=int(np.prod(env.action_space.shape))
        neutral=torch.zeros((native_width,),dtype=torch.float32)
        parts=controller.to_action_dict(neutral)
        assert "arm" in parts
        assert len(parts["arm"])==n
        parts["arm"]=torch.as_tensor(normalized,dtype=torch.float32)
        whole=controller.from_action_dict(parts).reshape(1,-1)
        assert whole.shape[-1]==native_width
        env.step(whole)

        after=tovec(arm._target_qpos)
        predicted=target_before+physical_action
        native_err=float(np.max(np.abs(after-predicted)))
        target_err=float(np.max(np.abs(after-desired)))
        assert native_err<TOLERANCE_RAD,(robot,seed,native_err)
        assert target_err<=certificate.optimal_worst_case_setpoint_error+TOLERANCE_RAD

        return {
            "robot":robot,"task":"PickCube-v1","seed":seed,
            "actual_robot_arm_joint_dof":n,
            "full_native_action_width":native_width,
            "controller":"PDJointPosController",
            "mode":"pd_joint_target_delta_pos",
            "initial_target_qpos_rad":target_before.tolist(),
            "observed_joint_qpos_rad":observed_qpos.tolist(),
            "native_normalized_arm_action":normalized.tolist(),
            "physical_arm_command_rad":physical_action.tolist(),
            "actual_next_target_qpos_rad":after.tolist(),
            "native_next_target_qpos_prediction_error_rad":native_err,
            "actual_vs_desired_target_qpos_error_rad":target_err,
            "certificate_max_interval_error_rad":certificate.optimal_worst_case_setpoint_error,
            "rejected_before_dispatch":sorted(failures),
            "policy_performance_measured":False,
            "real_robot_execution":False,
        }
    finally:
        env.close()


def main():
    records=[run(robot,seed) for robot,seed in CASES]
    assert [(v["robot"],v["seed"]) for v in records]==CASES
    report={
        "schema":"latent_memory_cross_robot_native_v1",
        "protocol":"research/LATENT_MEMORY_CROSS_ROBOT_PRECOMMIT_V1.json",
        "n_cases":4,
        "n_distinct_robot_embodiments":2,
        "distinct_maintained_controller_class":"PDJointPosController",
        "hardware_robot_tested":False,
        "third_party_independent_reproduction":False,
        "records":records,
    }
    Path("latent_memory_cross_robot_native_v1.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n"
    )
    print("LATENT_MEMORY_CROSS_ROBOT_NATIVE",json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
