"""Prospectively frozen true-heldout source-normalized ACK recovery on PhysX.

Hypothesis class/centroids fixed on prior 2026-10-13 160-world training pilot.
This execution uses brand-new reset seeds: no posthoc tuning or privileged ACK
in public decision routes. True ACK is used only to CREATE the fault and to
score the resulting experiment. Official PickCube success is descriptive.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

import gymnasium as gym
import mani_skill.envs  # noqa: F401
import numpy as np

from research.cross_robot_ack_physics import (
    ARM_MODE, TASK, actual_target_after_physics, get_arm, observer_for,
    requested_native, stepping,
)
from research.two_ack_real_recovery_physx import (
    counterfactual_target, choose_hypothesis_recovery,
)

PLAN = Path("research/TWO_ACK_HELDOUT_SOURCE_NORMALIZED_PREREG_20261013.json")
PLAN_SHA = "b86bdf490d7bf3ee1335cfc774cdd11c41db7ae8"
TRAIN = Path("research/TWO_ACK_HELDOUT_TRAIN_PROTOTYPES_20261013.json")
TRAIN_SHA = "48000e2831537c178262835b17748b37672b10d4"
HELPER = Path("research/two_ack_real_recovery_physx.py")
HELPER_SHA = "f6bf527362d04e0e7fc4b240cbb6913edd01eeee"


def validate_freeze():
    for path, want in ((PLAN, PLAN_SHA), (TRAIN, TRAIN_SHA),
                       (HELPER, HELPER_SHA)):
        digest = subprocess.check_output(
            ["git", "hash-object", str(path)], text=True
        ).strip()
        if digest != want:
            raise RuntimeError(f"Altered pre-outcome preregistered bytes: {path}")
    spec = json.loads(PLAN.read_text(encoding="utf-8"))
    data = json.loads(TRAIN.read_text(encoding="utf-8"))
    if (spec["status"] != "FROZEN_BEFORE_TEST_PHYSX_OUTCOMES"
            or data["training_origin_workflow_run_id"] != 38331837905
            or spec["frozen_training_prototypes_git_blob"] != TRAIN_SHA
            or spec["task"] != TASK or spec["controller"] != ARM_MODE
            or spec["denominator"]["real_physx_worlds_total"] != 128):
        raise RuntimeError("Training/heldout protocol mismatch")
    for robot in spec["robots"]:
        if (set(spec["new_holdout_test_seeds"][robot]) &
                set(spec["prior_train_seeds"][robot])):
            raise RuntimeError("Training/test reset overlap")
        if (len(spec["new_holdout_test_seeds"][robot]) != 4
                or len(data["training_rows"][robot]) != 16
                or set(data["training_prototypes"][robot]) != set(spec["histories"])):
            raise RuntimeError("Incomplete original source prototypes or test split")
    return spec, data


def frozen_nearest_centroid(feature_xyz, prototype_by_history, feature_name):
    """Only public features and frozen training centroids; never true history."""
    feat = np.asarray(feature_xyz, dtype=float)
    if feat.shape != (3,) or not np.all(np.isfinite(feat)):
        raise RuntimeError("Public xyz response must be finite shape (3,)")
    answer = None
    for h in ("00", "01", "10", "11"):
        center = np.asarray(prototype_by_history[h][feature_name], dtype=float)
        if center.shape != (3,) or not np.all(np.isfinite(center)):
            raise RuntimeError("Frozen source prototype corrupt")
        # Exact registered tie-breaker in historical order.
        candidate = (float(np.sum((feat - center)**2)), h)
        if answer is None or candidate < answer:
            answer = candidate
    return answer[1]


def physical_test_world(robot, seed, truth, policy, spec, train):
    if (robot not in spec["robots"]
            or seed not in spec["new_holdout_test_seeds"][robot]
            or truth not in spec["histories"]
            or policy not in spec["policies"]):
        raise RuntimeError("Unknown holdout test scenario")
    env = gym.make(
        TASK, robot_uids=robot, num_envs=1, obs_mode="state",
        sim_backend="physx_cpu", reconfiguration_freq=1,
        control_mode=ARM_MODE, disable_env_checker=True,
    )
    try:
        env.reset(seed=int(seed))
        ctrl, arm = get_arm(env)
        prefix = observer_for(arm)
        for t in spec["prefix_steps"]:
            native = requested_native(t)
            ticket = prefix.prepare(native)
            stepping(env, ctrl, native)
            prefix.acknowledge(ticket.ticket, applied=True)
        states = {
            h: counterfactual_target(arm, prefix.pose, h, {
                "histories": spec["histories"],
                "ambiguous_actions": spec["uncertain_source_actions"]
            }) for h in spec["histories"]
        }
        common_goal = states["11"]
        # Disturb the native persistent target state using the frozen *true*
        # action-delivery conditions. This variable is unavailable to the
        # public classifier and used ONLY in the simulator fault injector.
        for bit, t in zip(truth, ("t2", "t3")):
            nominal = np.asarray(spec["uncertain_source_actions"][t], dtype=float)
            physical = nominal if bit == "1" else np.zeros(6, dtype=float)
            stepping(env, ctrl, physical)
        observed = np.asarray(
            arm.ee_pose_at_base.p.detach().cpu(), dtype=float
        ).reshape(-1, 3)[0]
        goal_xyz = np.asarray(common_goal.position, dtype=float)
        if policy == "ABSOLUTE_XYZ":
            feature = observed.copy()
            decision = frozen_nearest_centroid(
                feature, train["training_prototypes"][robot], "raw_xyz"
            )
        elif policy == "SOURCE_RELATIVE_XYZ":
            # From the reset/issued actions' *public* source replay only.
            # NEVER a privileged controller target or hidden ACK getter.
            feature = observed - goal_xyz
            decision = frozen_nearest_centroid(
                feature, train["training_prototypes"][robot],
                "source_normalized_xyz",
            )
        elif policy == "NO_ACTION":
            feature, decision = None, None
        else:  # PRIVILEGED_ORACLE: explicitly labeled impossible ceiling
            feature, decision = None, truth
        native_recovery = (
            np.zeros(6, dtype=float) if decision is None else
            choose_hypothesis_recovery(arm, states[decision], common_goal)
        )
        stepping(env, ctrl, native_recovery)
        last = None
        for _ in range(spec["hold_steps_after_recovery"]):
            last = stepping(env, ctrl, np.zeros(6, dtype=float))
        achieved = np.asarray(
            arm.ee_pose_at_base.p.detach().cpu(), dtype=float
        ).reshape(-1, 3)[0]
        # Protected: source target getter only after decision and stepping.
        private = actual_target_after_physics(arm)
        return {
            "robot": robot, "seed": int(seed),
            "true_history_audit_only": truth, "policy": policy,
            "predicted_history_or_null": decision,
            "observed_pre_recovery_public_xyz": observed.tolist(),
            "source_only_common_goal_xyz": goal_xyz.tolist(),
            "public_classifier_feature_xyz_or_null": (
                None if feature is None else feature.tolist()
            ),
            "native_recovery_action": native_recovery.tolist(),
            "achieved_end_xyz": achieved.tolist(),
            "achieved_goal_error_m": float(np.linalg.norm(achieved-goal_xyz)),
            "post_action_private_target_audit_error_m": float(np.linalg.norm(
                np.asarray(private.position) - goal_xyz
            )),
            "official_pickcube_success_descriptive": last["official_success"],
            "public_policy_hidden_ack_reads": 0,
            "public_policy_private_target_reads": 0,
            "post_action_private_audit_reads": 1,
            "oracle_privileged_truth_only": policy == "PRIVILEGED_ORACLE",
            "true_new_physx_world": True,
        }
    finally:
        env.close()


def run_robot(robot):
    spec, training = validate_freeze()
    if robot not in spec["robots"]:
        raise RuntimeError("Robot not precommitted")
    rows = []
    for seed in spec["new_holdout_test_seeds"][robot]:
        for truth in spec["histories"]:
            for policy in spec["policies"]:
                result = physical_test_world(
                    robot, seed, truth, policy, spec, training
                )
                print("SOURCE_HELDOUT_PHYSX_WORLD",
                      json.dumps(result, sort_keys=True), flush=True)
                rows.append(result)
    expected = {
        (seed, h, method) for seed in spec["new_holdout_test_seeds"][robot]
        for h in spec["histories"] for method in spec["policies"]
    }
    if (len(rows) != 64 or len(expected) != 64
            or {(
                r["seed"], r["true_history_audit_only"], r["policy"]
            ) for r in rows} != expected):
        raise RuntimeError("Original physical holdout denominator incomplete")
    summary = {}
    for policy in spec["policies"]:
        subset = [r for r in rows if r["policy"] == policy]
        summary[policy] = {
            "mean_goal_error_m": float(np.mean([
                r["achieved_goal_error_m"] for r in subset
            ])),
            "correct_ack_count_or_null": (
                None if policy == "NO_ACTION" else
                sum(r["predicted_history_or_null"] ==
                    r["true_history_audit_only"] for r in subset)
            ),
            "original_worlds": len(subset),
        }
    positive_per_seed = {}
    for seed in spec["new_holdout_test_seeds"][robot]:
        means = {}
        for policy in spec["policies"]:
            xs = [r["achieved_goal_error_m"] for r in rows
                  if r["seed"] == seed and r["policy"] == policy]
            assert len(xs) == 4
            means[policy] = float(np.mean(xs))
        positive_per_seed[str(seed)] = {
            "policy_goal_error_means_m": means,
            "source_normalized_better_than_both_baselines": (
                means["SOURCE_RELATIVE_XYZ"] < means["ABSOLUTE_XYZ"]
                and means["SOURCE_RELATIVE_XYZ"] < means["NO_ACTION"]
            ),
        }
    out = {
        "schema": spec["schema"], "robot": robot,
        "preregistered_protocol_git_blob": PLAN_SHA,
        "frozen_train_prototypes_git_blob": TRAIN_SHA,
        "public_decision_source_frozen": True,
        "independent_new_reset_clusters": 4,
        "real_physical_holdout_worlds": 64,
        "mean_accuracy_and_error_by_policy": summary,
        "paired_original_seed_results": positive_per_seed,
        "prospective_positive_gate_met_on_this_robot": (
            sum(x["source_normalized_better_than_both_baselines"]
                for x in positive_per_seed.values()) >= 3
        ),
        "task_completion_gain_not_claimed": True,
        "no_external_replication_or_physical_safety_claim": True,
        "rows": rows,
    }
    name = f"source_normalized_two_ack_new_holdout_{robot}.json"
    Path(name).write_text(json.dumps(out, indent=2, sort_keys=True)+"\n")
    print("SOURCE_HELDOUT_PHYSX_COMPLETE", json.dumps({
        "robot": robot, "worlds": len(rows),
        "model_summaries": summary,
        "paired_seed_results": positive_per_seed,
        "positive_gate_met": out["prospective_positive_gate_met_on_this_robot"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", choices=("panda", "xarm6_robotiq"),
                        required=True)
    args = parser.parse_args()
    run_robot(args.robot)
