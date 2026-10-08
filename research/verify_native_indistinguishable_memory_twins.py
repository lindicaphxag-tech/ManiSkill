"""Real ManiSkill replay witness for indistinguishable achieved-pose histories.

Native controller.state API creates *controlled counterfactual histories*;
this is not a natural-frequency experiment or task-success benchmark.
Protocol frozen before implementation in LATENT_MEMORY_NATIVE_TWINS_PRECOMMIT_V1.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
import mani_skill.envs  # noqa: F401
from latent_target_memory_cert import unavoidable_indistinguishable_history_error


TASKS = [
    ("PickCube-v1", 773),
    ("PushCube-v1", 884),
    ("PullCube-v1", 995),
    ("StackCube-v1", 1106),
]
SHIFT_M = np.array([0.02, 0., 0.], dtype=np.float64)
TARGET_OFFSET_M = np.array([0., 0., 0.004], dtype=np.float64)
TOL = 0.0001


def make_world(task):
    return gym.make(
        task, num_envs=1, obs_mode="state", control_mode="pd_ee_target_delta_pose",
        sim_backend="physx_cpu", reconfiguration_freq=1, disable_env_checker=True
    )


def vec(tensor):
    return tensor.detach().cpu().numpy().reshape(-1).astype(np.float64).copy()


def control_action(arm, cartesian_position_command):
    physical_lower = vec(arm.action_space_low[:3])
    physical_upper = vec(arm.action_space_high[:3])
    if not np.all(physical_lower < physical_upper):
        raise RuntimeError("Noninvertible native action bounds")
    if not (
        np.all(cartesian_position_command >= physical_lower - 1e-8)
        and np.all(cartesian_position_command <= physical_upper + 1e-8)
    ):
        raise RuntimeError("Native controller command outside physical bounds")
    native = 2*(cartesian_position_command - physical_lower)/(
        physical_upper - physical_lower
    )-1
    return torch.as_tensor(
        np.r_[native, 0.,0.,0.,0.], dtype=torch.float32
    ).reshape(1, -1)


def run_case(task, seed):
    worlds={name:make_world(task) for name in ("A","B","blindC")}
    try:
        for world in worlds.values():
            world.reset(seed=seed)
        arms={
            k:w.unwrapped.agent.controller.controllers["arm"]
            for k,w in worlds.items()
        }
        for arm in arms.values():
            assert arm.config.use_target and arm.config.use_delta
            assert "root_translation" in arm.config.frame
            assert arm._normalize_action

        initial_joint = {
            k: vec(w.unwrapped.agent.robot.get_qpos())
            for k,w in worlds.items()
        }
        achieved = {k: vec(arm.ee_pose_at_base.p) for k,arm in arms.items()}
        assert all(
            np.max(np.abs(initial_joint[name]-initial_joint["A"])) < 1e-8
            and np.max(np.abs(achieved[name]-achieved["A"])) < 1e-8
            for name in ("B","blindC")
        ), "The physical agent states MUST be observationally identical"

        initial=arms["A"].get_state()["target_pose"].clone()
        assert tuple(initial.shape)==(1,7)
        mutated=initial.clone()
        mutated[:, :3]+=torch.as_tensor(
            SHIFT_M,device=mutated.device,dtype=mutated.dtype).reshape(1,3)

        # This is the official reversible controller state-replay API. The
        # simulator robot's achieved pose/joint state is NOT modified.
        arms["B"].set_state({"target_pose":mutated.clone()})
        arms["blindC"].set_state({"target_pose":mutated.clone()})
        mA=vec(arms["A"]._target_pose.p)
        mB=vec(arms["B"]._target_pose.p)
        mC=vec(arms["blindC"]._target_pose.p)
        assert np.max(np.abs(mB-mC))<1e-7
        assert np.max(np.abs(mB-mA-SHIFT_M))<1e-6

        # After memory replay, the policy-visible source physical state
        # (joint positions + achieved end-effector pose) is unchanged.
        post_achieved={k:vec(arm.ee_pose_at_base.p) for k,arm in arms.items()}
        assert all(
            np.max(np.abs(post_achieved[name]-post_achieved["A"]))<1e-8
            for name in ("B","blindC")
        )

        desired=mA+TARGET_OFFSET_M
        cmdA=desired-mA
        cmdB=desired-mB
        lower_bound=unavoidable_indistinguishable_history_error(mA,mB)
        assert abs(lower_bound-0.01)<1e-6

        # Full-memory worlds invert their *actual* previous targets.
        # The state-blind world C uses A's apparently valid tensor action
        # even though its latent target memory is B's.
        worlds["A"].step(control_action(arms["A"],cmdA))
        worlds["B"].step(control_action(arms["B"],cmdB))
        worlds["blindC"].step(control_action(arms["blindC"],cmdA))

        next_A=vec(arms["A"]._target_pose.p)
        next_B=vec(arms["B"]._target_pose.p)
        next_C=vec(arms["blindC"]._target_pose.p)
        exact_A=float(np.max(np.abs(next_A-desired)))
        exact_B=float(np.max(np.abs(next_B-desired)))
        blind_error=float(np.max(np.abs(next_C-desired)))
        delta_C_B=next_C-next_B
        assert exact_A<TOL, exact_A
        assert exact_B<TOL, exact_B
        assert 0.0199 <= blind_error <= 0.0201, blind_error
        assert np.max(np.abs(delta_C_B-SHIFT_M))<TOL

        return {
            "task":task,"seed":seed,
            "native_simulator":"ManiSkill PhysX CPU",
            "state_replay_api":"PDEEPoseController.set_state",
            "physical_qpos_unchanged_before_action":True,
            "physical_achieved_ee_unchanged_before_action":True,
            "controller_target_hidden_state_A_xyz_m":mA.tolist(),
            "controller_target_hidden_state_B_xyz_m":mB.tolist(),
            "common_desired_target_xyz_m":desired.tolist(),
            "full_information_controller_commands_A_xyz_m":cmdA.tolist(),
            "full_information_controller_commands_B_xyz_m":cmdB.tolist(),
            "result_target_A_xyz_m":next_A.tolist(),
            "result_target_B_xyz_m":next_B.tolist(),
            "result_blind_C_xyz_m":next_C.tolist(),
            "full_info_world_A_error_m":exact_A,
            "full_info_world_B_error_m":exact_B,
            "blind_copy_error_m":blind_error,
            "information_lower_bound_m":lower_bound,
            "artificial_state_replay_not_natural_trajectory":True,
            "robot_safety_claim":False,
            "task_success_claim":False,
        }
    finally:
        for world in worlds.values():
            world.close()


def main():
    observations=[run_case(task, seed) for task, seed in TASKS]
    assert [(v["task"],v["seed"]) for v in observations]==TASKS
    report={
        "schema":"latent_target_memory_native_twins_v1",
        "protocol":"research/LATENT_MEMORY_NATIVE_TWINS_PRECOMMIT_V1.json",
        "n_genuine_physics_controller_cases":4,
        "only_controlled_state_replay":True,
        "author_operated_not_external_independent":True,
        "all_cases":observations,
    }
    Path("latent_memory_indistinguishable_twins.json").write_text(
        json.dumps(report, indent=2, sort_keys=True)+"\n"
    )
    print("NATIVE_INDISTINGUISHABLE_HISTORIES",json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
