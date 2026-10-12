"""FIRST-OUTCOME frozen PhysX pilot for source-valid zero/X/Y ACK probes.

Precommitted JSON blob MUST precede code/outcomes. This uses genuine ManiSkill
CPU PhysX, not a VLA policy or independent laboratory replication. No trained
classifier or deterministic physical response envelope is claimed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import gymnasium as gym
import mani_skill.envs  # noqa: F401 register original environments
import numpy as np

from research.action_abi_history_observer import ActionHistoryObserver
from research.ack_native_probe_source_adapter import propose_from_common_native_action
from research.cross_robot_ack_physics import (
    ARM_MODE, TASK, actual_target_after_physics, get_arm,
    observer_for, requested_native, stepping,
)

PROTOCOL = Path("research/ACK_ACTIVE_NATIVE_PROBE_PILOT_PREREG_20261013.json")
PROTOCOL_BLOB = "6f97dccaa4740039019db0726e21ea0a970a1fa3"
CONTROLLER_SOURCE = Path("research/cross_robot_ack_physics.py")
CONTROLLER_BLOB = "3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7"


def require(value, message):
    if not value:
        raise RuntimeError(message)


def source_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)],
                                   text=True).strip()


def verify_freeze():
    require(source_blob(PROTOCOL) == PROTOCOL_BLOB,
            "Pre-outcome frozen protocol bytes changed")
    require(source_blob(CONTROLLER_SOURCE) == CONTROLLER_BLOB,
            "Robot physics source/control chart changed")
    obj = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    require(obj["status"] == "FROZEN_BEFORE_NEW_PHYSX_OUTCOMES",
            "Protocol is not precommitted")
    spec = obj["world_conditions"]
    require(spec["total_physical_truth_probe_worlds"] == 48
            and spec["total_reset_clusters"] == 8, "Study denominator wrong")
    require(tuple(obj["robots"]) == ("panda", "xarm6_robotiq")
            and obj["task"] == TASK and obj["control_mode"] == ARM_MODE,
            "Robot/task chart differs from the frozen plan")
    require(set(spec["probes"]) == {"zero", "native_x", "native_y"}
            and set(spec["truths"]) == {"applied", "held"},
            "Probe/truth arms do not match freeze")
    for robot in obj["robots"]:
        require(len(obj["seed_register"][robot]) == 4,
                "Each robot must have exactly four new paired reset clusters")
    return obj


def one_physical_world(robot, seed, truth, probe_name, protocol):
    spec = protocol["world_conditions"]
    require(truth in spec["truths"] and probe_name in spec["probes"],
            "Unknown truth or probe")
    native = np.asarray(spec["probes"][probe_name], dtype=np.float64)
    requested_fault = np.asarray(spec["fault_native_arm_six"], dtype=np.float64)
    env = gym.make(TASK, robot_uids=robot, num_envs=1, obs_mode="state",
                   sim_backend="physx_cpu", reconfiguration_freq=1,
                   control_mode=ARM_MODE, disable_env_checker=True)
    try:
        env.reset(seed=int(seed))
        ctrl, arm = get_arm(env)
        observer = observer_for(arm)
        for t in (0, 1):
            command = requested_native(t)
            ticket = observer.prepare(command)
            stepping(env, ctrl, command)
            observer.acknowledge(ticket.ticket, applied=True)
        before_fault_target = observer.pose
        applied_observer = ActionHistoryObserver(
            arm.config.pos_lower, arm.config.pos_upper, arm.config.rot_lower,
            frame=arm.config.frame, use_delta=arm.config.use_delta,
            use_target=arm.config.use_target,
            normalize_action=arm.config.normalize_action,
        )
        applied_observer.reset(before_fault_target)
        t = applied_observer.prepare(requested_fault)
        applied_observer.acknowledge(t.ticket, applied=True)
        hidden = {
            "held": before_fault_target,
            "applied": applied_observer.pose,
        }
        real_fault_command = (
            requested_fault if truth == "applied" else np.zeros(6, dtype=np.float64)
        )
        stepping(env, ctrl, real_fault_command)
        before = np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                            dtype=np.float64).reshape(-1, 3)[0].copy()
        # Inferred targets are source-replayed with ONE common native probe;
        # no controller target read and no true ACK label reach the proposal.
        proposal = propose_from_common_native_action(
            hidden, native, name=probe_name,
            pos_lower=arm.config.pos_lower, pos_upper=arm.config.pos_upper,
            rot_lower=arm.config.rot_lower, declared_action_cost=1.0 +
            float(np.linalg.norm(native)),  # DECLARED proxy, not motor energy
        )
        outcome = stepping(env, ctrl, native)
        after = np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                           dtype=np.float64).reshape(-1, 3)[0].copy()
        # PRIVILEGED TRUE TARGET READ: explicit post-action integrity audit only.
        actual = actual_target_after_physics(arm)
        expected_xyz = np.asarray(proposal.candidate.targets[truth])
        target_err = float(np.max(np.abs(
            np.asarray(actual.position) - expected_xyz
        )))
        require(target_err <= 1e-4,
                f"Actual native controller violates pinned target recurrence: {target_err}")
        return dict(
            robot=robot, seed=int(seed), truth_score_only=truth,
            probe_id=probe_name, probe_native_six=native.tolist(),
            fault_native_six=real_fault_command.tolist(),
            observation_preprobe_xyz=before.tolist(),
            observation_postprobe_xyz=after.tolist(),
            model_predicted_hidden_targets_xyz=proposal.candidate.targets,
            native_target_recurrence_error_linf_m=target_err,
            official_task_success_descriptive=outcome["official_success"],
            public_motion_after_true_actuation=True,
            native_controller_mapping=sorted(ctrl.controllers),
            decision_time_privileged_target_reads=0,
            post_action_audit_target_reads=1,
            nominal_probe_cost_only=proposal.candidate.cost,
            no_certified_physical_safety=True,
        )
    finally:
        env.close()


def run_robot(robot: str):
    proto = verify_freeze()
    require(robot in proto["robots"], "Unregistered robot")
    spec = proto["world_conditions"]
    rows = []
    for seed in proto["seed_register"][robot]:
        for truth in spec["truths"]:
            for probe_id in spec["probes"]:
                row = one_physical_world(robot, seed, truth, probe_id, proto)
                rows.append(row)
                print("FROZEN_NATIVE_PROBE_WORLD", json.dumps(row, sort_keys=True),
                      flush=True)
    require(len(rows) == 24, "Incomplete original per-robot physical denominator")
    gaps = []
    for seed in proto["seed_register"][robot]:
        distances = {}
        for probe_id in spec["probes"]:
            match = [r for r in rows if r["seed"] == seed and
                     r["probe_id"] == probe_id]
            require(len(match) == 2 and
                    {r["truth_score_only"] for r in match} == {"applied", "held"},
                    "Incomplete paired actual-ACK comparison")
            a, b = (np.asarray(r["observation_postprobe_xyz"]) for r in match)
            distances[probe_id] = float(np.linalg.norm(a - b))
        gaps.append(dict(
            seed=seed, observed_public_xyz_separation_m=distances,
            delta_native_x_minus_zero_m=distances["native_x"]-distances["zero"],
            delta_native_y_minus_zero_m=distances["native_y"]-distances["zero"],
        ))
    result = dict(
        schema=proto["schema"], protocol_git_blob=PROTOCOL_BLOB,
        controller_source_git_blob=CONTROLLER_BLOB, robot=robot,
        original_unique_reset_clusters=4, original_native_physx_worlds=24,
        paired_descriptive_gaps=gaps, rows=rows,
        model_does_not_include_physical_calibration=True,
        no_claim_of_policy_success_or_new_active_certificate=True,
        author_operated_only=True,
    )
    name = f"ack_native_probe_physx_pilot_{robot}.json"
    Path(name).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",
                          encoding="utf-8")
    print("NATIVE_ACK_PROBE_PILOT_COMPLETE",
          json.dumps(dict(robot=robot, source_worlds=24, paired_gaps=gaps),
                     sort_keys=True), flush=True)
    return name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", required=True,
                        choices=("panda", "xarm6_robotiq"))
    args = parser.parse_args()
    run_robot(args.robot)
