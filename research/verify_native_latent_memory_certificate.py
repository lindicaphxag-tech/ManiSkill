"""Native four-task Panda target-position certificate contract check.

Real unmodified ManiSkill PhysX controller set_action/IK state, not synthetic
robot task success and not a learned frozen PPO experiment.

Pre-outcome freeze: research/LATENT_MEMORY_NATIVE_PRECOMMIT_V1.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch

import mani_skill.envs  # noqa: F401 -- register official simulator tasks
from latent_target_memory_cert import (
    TransportRequest, Verdict, certify_box_memory_transport,
)

TASK_SEEDS = [
    ("PickCube-v1", 2277), ("PushCube-v1", 3388),
    ("PullCube-v1", 4499), ("StackCube-v1", 5511),
]
DELTA = np.array([0.008, -0.006, 0.005], dtype=np.float64)
RADIUS_M = 0.0015
EPSILON_M = 0.002
NATIVE_TOLERANCE_M = 0.0001


def physical_position(pose) -> np.ndarray:
    result = pose.p.detach().cpu().numpy().reshape(-1, 3)[0]
    if not np.all(np.isfinite(result)):
        raise RuntimeError("Nonfinite physical controller target")
    return np.array(result, dtype=np.float64, copy=True)


def case(task: str, seed: int) -> dict:
    env = gym.make(
        task, num_envs=1, obs_mode="state", control_mode="pd_ee_target_delta_pose",
        sim_backend="physx_cpu", reconfiguration_freq=1, disable_env_checker=True,
    )
    try:
        _, _ = env.reset(seed=seed)
        agent = env.unwrapped.agent
        composite = agent.controller
        arm = composite.controllers["arm"]
        cfg = arm.config
        # These are substantive certified-model assumptions. Refuse instead
        # of silently using an incorrect frame or unnormalized action ABI.
        assert cfg.use_target and cfg.use_delta
        assert "root_translation" in cfg.frame
        assert arm._normalize_action
        assert arm._target_pose is not None

        prior = physical_position(arm._target_pose)
        desired = prior + DELTA

        # The position limits come from the REAL native controller.
        native_low = arm.action_space_low[:3].detach().cpu().numpy().astype(np.float64)
        native_high = arm.action_space_high[:3].detach().cpu().numpy().astype(np.float64)
        assert native_low.shape == native_high.shape == (3,)
        assert np.all(native_high > native_low)
        assert np.allclose(native_low, float(cfg.pos_lower))
        assert np.allclose(native_high, float(cfg.pos_upper))

        uncertainty_lo = prior - RADIUS_M
        uncertainty_hi = prior + RADIUS_M

        def inquiry(*, attested=True, age=0, verified=True, radius=RADIUS_M):
            return TransportRequest(
                desired_target=tuple(desired),
                memory_lower=tuple(prior - radius),
                memory_upper=tuple(prior + radius),
                command_lower=tuple(native_low),
                command_upper=tuple(native_high),
                error_budget=EPSILON_M,
                trusted_memory_attestation=attested,
                memory_age_steps=age,
                max_memory_age_steps=0,
                additive_controller_contract_verified=verified,
            )

        # Fail closed BEFORE real actuator dispatch.
        rejects = {
            "not_attested": (inquiry(attested=False), Verdict.REFUSE_UNTRUSTED_MEMORY),
            "stale": (inquiry(age=1), Verdict.REFUSE_STALE_MEMORY),
            "wrong_controller": (inquiry(verified=False), Verdict.REFUSE_UNVERIFIED_CONTROLLER),
            "unobservable_radius": (inquiry(radius=0.02), Verdict.REFUSE_GEOMETRICALLY_IMPOSSIBLE),
        }
        for name, (request, expected) in rejects.items():
            declined = certify_box_memory_transport(request)
            assert declined.verdict is expected and declined.command is None, name

        answer = certify_box_memory_transport(inquiry())
        assert answer.verdict is Verdict.AUTHORIZE_COMMANDED_TARGET, answer
        assert np.isclose(answer.optimal_worst_case_setpoint_error, RADIUS_M, atol=1e-9)
        physical_command = np.array(answer.command, dtype=np.float64)
        # Feed the official native normalized source only, never set _target_pose
        # directly (that would validate the mathematics but bypass controller).
        pos_action_native = (
            2.0 * (physical_command - native_low) / (native_high - native_low) - 1.0
        )
        assert np.all(np.abs(pos_action_native) <= 1 + 1e-6)
        # Orientation unchanged and gripper command neutral.
        concat = torch.as_tensor(
            np.r_[pos_action_native, [0.0, 0.0, 0.0, 0.0]], dtype=torch.float32
        ).reshape(1, -1)
        assert concat.shape[-1] == int(np.prod(env.action_space.shape))
        env.step(concat)

        after = physical_position(arm._target_pose)
        predicted = prior + physical_command
        actual_discrepancy = float(np.max(np.abs(after - predicted)))
        actual_setpoint_error = float(np.max(np.abs(after - desired)))
        assert actual_discrepancy <= NATIVE_TOLERANCE_M, (
            task, seed, actual_discrepancy
        )
        assert actual_setpoint_error <= (
            answer.optimal_worst_case_setpoint_error + NATIVE_TOLERANCE_M
        ), (task, seed, actual_setpoint_error)

        return {
            "task": task, "seed": seed, "official_controller": "pd_ee_target_delta_pose",
            "source": "actual Panda PDEEPoseController",
            "physical_cartesian_command_m": physical_command.tolist(),
            "prior_controller_target_xyz_m": prior.tolist(),
            "new_controller_target_xyz_m": after.tolist(),
            "native_controller_position_action": pos_action_native.tolist(),
            "actual_vs_additive_prediction_max_abs_m": actual_discrepancy,
            "actual_vs_desired_target_max_abs_m": actual_setpoint_error,
            "minimax_worst_case_error_m": answer.optimal_worst_case_setpoint_error,
            "refusals_without_dispatch": list(rejects),
            "physical_execution_tested": True,
            "physical_robot_tested": False,
            "task_success_measured": False,
        }
    finally:
        env.close()


def main():
    records = [case(task, seed) for task, seed in TASK_SEEDS]
    assert len(records) == 4
    assert [(d["task"], d["seed"]) for d in records] == TASK_SEEDS
    output = {
        "schema": "latent_target_memory_native_contract_v1",
        "protocol": "research/LATENT_MEMORY_NATIVE_PRECOMMIT_V1.json",
        "simulator": "unmodified ManiSkill PhysX CPU, official Panda controller",
        "total_predeclared_cases": 4,
        "real_robot_physical_safety_certified": False,
        "controller_target_position_abi_audited": True,
        "author_executed": True,
        "records": records,
    }
    Path("latent_target_memory_native_contract_v1.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("LATENT_TARGET_MEMORY_NATIVE_CONTRACT", json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
