"""Prospectively frozen two-ACK four-history native PhysX recovery matrix.

Real controller steps in Panda and xArm6, NOT a trained VLA or adaptive
classifier. Recovery action is derived from a publicly reconstructed
hypothesized controller history, not hidden true ACK or private target getter.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import gymnasium as gym
import mani_skill.envs  # noqa: F401
import numpy as np

from research.action_abi_history_observer import ActionHistoryObserver
from research.cross_robot_ack_physics import (
    ARM_MODE, TASK, actual_target_after_physics, get_arm, observer_for,
    requested_native, stepping,
)

PROTO = Path("research/TWO_ACK_REAL_RECOVERY_MATRIX_PREREG_20261013.json")
PROTO_SHA = "6789866ddfdc48350a56be6b50da66fd07014457"
SOURCE_PATH = Path("research/cross_robot_ack_physics.py")
SOURCE_SHA = "3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7"


def verify_protocol():
    for path, digest in [(PROTO, PROTO_SHA), (SOURCE_PATH, SOURCE_SHA)]:
        actual = subprocess.check_output(
            ["git", "hash-object", str(path)], text=True
        ).strip()
        if actual != digest:
            raise RuntimeError(f"Source/preregister bytes drifted: {path}")
    obj = json.loads(PROTO.read_text(encoding="utf-8"))
    if (obj["state"] != "FROZEN_BEFORE_NEW_PHYSX_OUTCOMES"
            or obj["task"] != TASK or obj["control_mode"] != ARM_MODE
            or obj["denominator"]["physical_worlds_total"] != 160
            or obj["denominator"]["independent_reset_clusters"] != 8):
        raise RuntimeError("Unexpected study design or denominator")
    assert obj["histories"] == ["00", "01", "10", "11"]
    assert obj["candidate_decisions"] == ["00", "01", "10", "11", "NO_ACTION"]
    return obj


def counterfactual_target(arm, base_pose, history, spec):
    if history not in spec["histories"]:
        raise ValueError("Unregistered two-ACK history")
    cfg = arm.config
    model = ActionHistoryObserver(
        cfg.pos_lower, cfg.pos_upper, cfg.rot_lower,
        frame=cfg.frame, use_delta=cfg.use_delta,
        use_target=cfg.use_target, normalize_action=cfg.normalize_action,
    )
    model.reset(base_pose)
    for bit, key in zip(history, ("t2", "t3")):
        requested = np.asarray(spec["ambiguous_actions"][key], dtype=np.float64)
        actual = requested if bit == "1" else np.zeros(6, dtype=np.float64)
        ticket = model.prepare(actual)
        model.acknowledge(ticket.ticket, applied=True)
    return model.pose


def choose_hypothesis_recovery(arm, guessed, goal):
    """Invert the source's *root-frame* target-relative translation mapping.

    Only uses two source-reconstructed counterfactual commanded targets.
    No actual target getter, true-history label or privileged sim state.
    """
    cfg = arm.config
    lo = np.broadcast_to(np.asarray(cfg.pos_lower, dtype=float), (3,))
    hi = np.broadcast_to(np.asarray(cfg.pos_upper, dtype=float), (3,))
    if not np.all(np.isfinite(lo)) or not np.all(np.isfinite(hi)):
        raise RuntimeError("Nonfinite native position mapping")
    if not np.allclose(hi, -lo, atol=1e-7, rtol=0):
        raise RuntimeError("Zero native is not certified target hold")
    if np.any(hi <= lo):
        raise RuntimeError("Invalid native position bounds")
    needed = np.asarray(goal.position) - np.asarray(guessed.position)
    normalized = 2 * (needed - lo) / (hi - lo) - 1
    if not np.all(np.isfinite(normalized)) or np.any(np.abs(normalized) > 1+1e-6):
        raise RuntimeError("Unrepresentable guessed-history recovery action")
    return np.r_[normalized, np.zeros(3, dtype=np.float64)]


def one_physics_world(robot, seed, true_history, decision, spec):
    if (robot not in spec["robots"]
            or seed not in spec["reset_seeds"][robot]
            or true_history not in spec["histories"]
            or decision not in spec["candidate_decisions"]):
        raise ValueError("Unregistered robot/reset/history/recovery arm")
    env = gym.make(
        TASK, robot_uids=robot, num_envs=1, obs_mode="state",
        sim_backend="physx_cpu", reconfiguration_freq=1,
        control_mode=ARM_MODE, disable_env_checker=True,
    )
    try:
        env.reset(seed=int(seed))
        ctrl, arm = get_arm(env)
        prefix = observer_for(arm)
        for step in spec["prefix_steps"]:
            native = requested_native(step)
            t = prefix.prepare(native)
            stepping(env, ctrl, native)
            prefix.acknowledge(t.ticket, applied=True)
        base = prefix.pose
        # Every recovery candidate and the canonical goal are computed
        # BEFORE consulting which hidden commands actually occurred.
        predictions = {
            h: counterfactual_target(arm, base, h, spec)
            for h in spec["histories"]
        }
        goal = predictions["11"]
        correction = (
            np.zeros(6, dtype=float) if decision == "NO_ACTION"
            else choose_hypothesis_recovery(arm, predictions[decision], goal)
        )
        if decision != "NO_ACTION":
            recovered = ActionHistoryObserver(
                arm.config.pos_lower, arm.config.pos_upper, arm.config.rot_lower,
                frame=arm.config.frame, use_delta=arm.config.use_delta,
                use_target=arm.config.use_target,
                normalize_action=arm.config.normalize_action,
            )
            recovered.reset(predictions[decision])
            tick = recovered.prepare(correction)
            recovered.acknowledge(tick.ticket, applied=True)
            err = float(np.linalg.norm(
                np.asarray(recovered.pose.position) - np.asarray(goal.position)
            ))
            if err > 1e-6:
                raise RuntimeError("Source inverse action cannot reconstruct the goal")
        for bit, key in zip(true_history, ("t2", "t3")):
            proposed = np.asarray(spec["ambiguous_actions"][key], dtype=float)
            physical_action = proposed if bit == "1" else np.zeros(6)
            stepping(env, ctrl, physical_action)
        pre_xyz = np.asarray(
            arm.ee_pose_at_base.p.detach().cpu(), dtype=float
        ).reshape(-1, 3)[0]
        stepping(env, ctrl, correction)
        outcome = None
        for _ in range(spec["followup_zero_native_steps"]):
            outcome = stepping(env, ctrl, np.zeros(6))
        achieved = np.asarray(
            arm.ee_pose_at_base.p.detach().cpu(), dtype=float
        ).reshape(-1, 3)[0]
        # Private native controller target is read only AFTER all action
        # choices and physics steps, strictly for source-integrity audit.
        actual_target = actual_target_after_physics(arm)
        audit_target_error = float(np.linalg.norm(
            np.asarray(actual_target.position) - np.asarray(goal.position)
        ))
        return {
            "robot": robot, "reset_seed": int(seed),
            "true_history_audit_only": true_history,
            "fixed_recovery_decision": decision,
            "native_correction": correction.tolist(),
            "canonical_goal_source_xyz": list(goal.position),
            "pre_recovery_public_ee_xyz": pre_xyz.tolist(),
            "post_recovery_public_ee_xyz": achieved.tolist(),
            "achieved_xyz_error_m": float(np.linalg.norm(
                achieved - np.asarray(goal.position)
            )),
            "private_target_audit_residual_m": audit_target_error,
            "official_pickcube_success_descriptive": outcome["official_success"],
            "decision_time_hidden_ack_reads": 0,
            "decision_time_private_controller_target_reads": 0,
            "post_action_target_audit_reads": 1,
            "real_physx_cpu": True,
            "physical_safety_certificate": False,
        }
    finally:
        env.close()


def run_robot(robot):
    spec = verify_protocol()
    if robot not in spec["robots"]:
        raise ValueError("Robot outside frozen protocol")
    rows = []
    for seed in spec["reset_seeds"][robot]:
        for history in spec["histories"]:
            for decision in spec["candidate_decisions"]:
                row = one_physics_world(robot, seed, history, decision, spec)
                print("NATIVE_RECOVERY_WORLD", json.dumps(row, sort_keys=True),
                      flush=True)
                rows.append(row)
    if len(rows) != 80:
        raise RuntimeError("Incomplete prospective actual PhysX denominator")
    # Truth/candidate full cartesian coverage is audited before summarizing.
    required = {
        (int(seed), h, d)
        for seed in spec["reset_seeds"][robot]
        for h in spec["histories"]
        for d in spec["candidate_decisions"]
    }
    observed = {
        (x["reset_seed"], x["true_history_audit_only"],
         x["fixed_recovery_decision"]) for x in rows
    }
    if required != observed:
        raise RuntimeError("Missing/duplicated paired true-history decision cell")
    summary = {}
    for truth in spec["histories"]:
        summary[truth] = {
            decision: float(np.mean([
                x["achieved_xyz_error_m"] for x in rows
                if x["true_history_audit_only"] == truth
                and x["fixed_recovery_decision"] == decision
            ]))
            for decision in spec["candidate_decisions"]
        }
    result = {
        "schema": spec["schema"], "robot": robot,
        "preoutcome_protocol_git_blob": PROTO_SHA,
        "native_mapping_source_git_blob": SOURCE_SHA,
        "unique_reset_clusters": 4,
        "actual_physical_worlds": 80,
        "metric": spec["primary_loss"],
        "no_probe_classifier_or_adaptive_policy": True,
        "not_independent_replication": True,
        "source_truth_decision_mean_loss_matrix_m": summary,
        "rows": rows,
    }
    filename = f"two_ack_recovery_matrix_{robot}.json"
    Path(filename).write_text(
        json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8"
    )
    print("REAL_RECOVERY_MATRIX_COMPLETE", json.dumps(
        {"robot": robot, "worlds": len(rows), "matrix": summary},
        sort_keys=True), flush=True)
    return filename


if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("--robot", choices=("panda", "xarm6_robotiq"), required=True)
    run_robot(argp.parse_args().robot)
