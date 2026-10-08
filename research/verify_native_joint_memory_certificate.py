"""Second maintained low-level controller family: native joint target-memory audit.

Real official ManiSkill PhysX PDJointPosController, not pose controller.
Four source-seed cases and error budgets are frozen in
LATENT_MEMORY_NATIVE_JOINT_PRECOMMIT_V1.json before this runner.
"""
from __future__ import annotations

import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch

import mani_skill.envs  # noqa F401
from latent_target_memory_cert import (
    TransportRequest, Verdict, certify_box_memory_transport,
)

TASKS = [
    ("PickCube-v1", 1477), ("PushCube-v1", 2488),
    ("PullCube-v1", 3499), ("StackCube-v1", 4510),
]
DELTA = np.array([0.006, -0.004, 0.005, -0.002, 0.003, 0.004, -0.005])
RADIUS = 0.001
ERROR_BUDGET = 0.0015
TOLERANCE = 0.0001


def arr(t):
    return np.asarray(t.detach().cpu().numpy(), dtype=np.float64).reshape(-1).copy()


def evaluate(task, seed):
    env = gym.make(
        task, num_envs=1, obs_mode="state",
        control_mode="pd_joint_target_delta_pos", sim_backend="physx_cpu",
        reconfiguration_freq=1, disable_env_checker=True,
    )
    try:
        env.reset(seed=seed)
        agent = env.unwrapped.agent
        arm = agent.controller.controllers["arm"]
        cfg = arm.config
        assert cfg.use_delta and cfg.use_target and arm._normalize_action
        assert len(arm.joints) == 7
        initial = arr(arm._target_qpos)
        observed_qpos = arr(arm.qpos)
        assert len(initial) == len(observed_qpos) == 7
        native_min = arr(arm.action_space_low)
        native_max = arr(arm.action_space_high)
        assert len(native_min) == len(native_max) == 7
        assert np.all(native_min < native_max)
        assert np.allclose(native_min, float(cfg.lower))
        assert np.allclose(native_max, float(cfg.upper))

        desired = initial + DELTA

        def request(*, attest=True, age=0, verified=True, radius=RADIUS):
            return TransportRequest(
                desired_target=tuple(desired),
                memory_lower=tuple(initial-radius),
                memory_upper=tuple(initial+radius),
                command_lower=tuple(native_min),
                command_upper=tuple(native_max),
                error_budget=ERROR_BUDGET,
                trusted_memory_attestation=attest,
                memory_age_steps=age,
                max_memory_age_steps=0,
                additive_controller_contract_verified=verified,
            )

        refusal_cases = {
            "untrusted": (request(attest=False), Verdict.REFUSE_UNTRUSTED_MEMORY),
            "stale": (request(age=1), Verdict.REFUSE_STALE_MEMORY),
            "unverified": (request(verified=False), Verdict.REFUSE_UNVERIFIED_CONTROLLER),
            "too_wide": (request(radius=0.02), Verdict.REFUSE_GEOMETRICALLY_IMPOSSIBLE),
        }
        for label, (r, verdict) in refusal_cases.items():
            result = certify_box_memory_transport(r)
            assert result.verdict is verdict and result.command is None, label

        decision = certify_box_memory_transport(request())
        assert decision.may_dispatch
        assert np.isclose(decision.optimal_worst_case_setpoint_error,RADIUS,atol=1e-9)
        physical_command = np.asarray(decision.command)
        normalized = (
            2*(physical_command-native_min)/(native_max-native_min)-1
        )
        assert np.all(np.abs(normalized)<=1.000001)
        action = torch.as_tensor(
            np.r_[normalized, 0.0],dtype=torch.float32
        ).reshape(1,-1)
        assert action.shape[-1]==int(np.prod(env.action_space.shape))
        env.step(action)

        recorded_target = arr(arm._target_qpos)
        predicted_target = initial+physical_command
        native_diff = float(np.max(np.abs(recorded_target-predicted_target)))
        error = float(np.max(np.abs(recorded_target-desired)))
        assert native_diff < TOLERANCE, (task,seed,native_diff)
        assert error <= decision.optimal_worst_case_setpoint_error+TOLERANCE, (
            task,seed,error
        )

        return {
            "task":task, "seed":seed,
            "controller":"PDJointPosController",
            "mode":"pd_joint_target_delta_pos",
            "stateful_previous_target_qpos_rad":initial.tolist(),
            "observed_achieved_qpos_rad":observed_qpos.tolist(),
            "physical_joint_action_rad":physical_command.tolist(),
            "normalized_native_action":normalized.tolist(),
            "recorded_new_target_qpos_rad":recorded_target.tolist(),
            "native_commanded_joint_target_prediction_error_rad":native_diff,
            "actual_vs_desired_joint_target_error_rad":error,
            "minimax_interval_setpoint_error_rad":decision.optimal_worst_case_setpoint_error,
            "pre_dispatch_refusals":sorted(refusal_cases),
            "task_success_measured":False,
            "real_robot_safety_certified":False,
        }
    finally:
        env.close()


def main():
    records=[evaluate(task,seed) for task,seed in TASKS]
    assert [(r["task"],r["seed"]) for r in records]==TASKS
    result={
        "schema":"latent_memory_native_joint_target_v1",
        "protocol":"research/LATENT_MEMORY_NATIVE_JOINT_PRECOMMIT_V1.json",
        "simulation":"unmodified ManiSkill PhysX CPU",
        "actual_separate_controller_implementation":"PDJointPosController",
        "precommitted_count":4,
        "independent_third_party_replication":False,
        "hardware_robot_safety_claim":False,
        "records":records,
    }
    Path("latent_memory_joint_target_native_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print("JOINT_TARGET_MEMORY_NATIVE",json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
