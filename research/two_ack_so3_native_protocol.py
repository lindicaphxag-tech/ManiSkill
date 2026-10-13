"""Frozen native-SO(3) two-ACK state observation and recovery utilities.

Two controller-command histories are simulated by applying/holding the same
six-D action in real ManiSkill CPU PhysX. Public EE pose, reset pose and issued
actions are the ONLY policy-side state. The private commanded-target getter is
NOT called for inference. Not a new control theorem or safety guarantee.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import gymnasium as gym
import mani_skill.envs  # noqa: F401
import numpy as np
from scipy.spatial.transform import Rotation

from research.action_abi_history_observer import ActionHistoryObserver
from research.cross_robot_ack_physics import (
    ARM_MODE, TASK, get_arm, observer_for, pose_from, requested_native,
    stepping,
)
from research.two_ack_real_recovery_physx import counterfactual_target

PREREG_PATH = Path("research/TWO_ACK_SO3_VS_RESET_STRONG_PREREG_20261013.json")
PREREG_BLOB = "44f770ecabe87e894eb7a3fa94dde3e94a730734"
HISTORY_ORDER = ("00", "01", "10", "11")


def verify_registered_plan():
    sha = subprocess.check_output(
        ["git", "hash-object", str(PREREG_PATH)], text=True
    ).strip()
    if sha != PREREG_BLOB:
        raise RuntimeError("Frozen preregistered study source has changed")
    spec = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    if (spec["state"] != "FROZEN_PRE_OUTCOME"
            or spec["task"] != TASK or spec["mode"] != ARM_MODE
            or spec["history_register"] != list(HISTORY_ORDER)
            or spec["frozen_training_conditions_total"] != 64
            or spec["new_test_conditions_total"] != 320):
        raise RuntimeError("Unexpected or posthoc changed study denominator")
    return spec


def _r(quaternion_xyzw):
    q = np.asarray(quaternion_xyzw, dtype=np.float64)
    if q.shape != (4,) or not np.all(np.isfinite(q)):
        raise ValueError("finite public orientation quaternion required")
    return Rotation.from_quat(q)


def quaternion_angle(a, b):
    return float((_r(a) * _r(b).inv()).magnitude())


def reset_so3_feature(public_q, public_reset_q):
    # Root-frame relative achieved orientation; registered conventional
    # representation with no private target information.
    return (_r(public_q) * _r(public_reset_q).inv()).as_quat().tolist()


def setup_public_two_ack_world(spec, robot, seed, variant, truth):
    if (robot not in spec["robots"] or variant not in spec["action_variants"]
            or truth not in HISTORY_ORDER
            or seed not in (spec["training_seeds"][robot]
                            + spec["heldout_seeds"][robot])):
        raise ValueError("Unregistered robot, native action, seed or ACK truth")
    env = gym.make(
        TASK, robot_uids=robot, num_envs=1, obs_mode="state",
        sim_backend="physx_cpu", reconfiguration_freq=1,
        control_mode=ARM_MODE, disable_env_checker=True,
    )
    try:
        env.reset(seed=int(seed))
        controller, arm = get_arm(env)
        if (arm.config.frame != spec["chart"]
                or not arm.config.use_delta or not arm.config.use_target
                or not arm.config.normalize_action):
            raise RuntimeError("Source chart not matching frozen controller semantics")
        reset = pose_from(arm.ee_pose_at_base)
        source = observer_for(arm)
        for t in spec["prefix_steps"]:
            issued = requested_native(t)
            ticket = source.prepare(issued)
            stepping(env, controller, issued)
            source.acknowledge(ticket.ticket, applied=True)
        variant_actions = spec["action_variants"][variant]
        candidates = {
            h: counterfactual_target(
                arm, source.pose, h,
                {"histories":list(HISTORY_ORDER),
                 "ambiguous_actions":variant_actions}
            ) for h in HISTORY_ORDER
        }
        for bit, step in zip(truth, ("t2", "t3")):
            issued = np.asarray(variant_actions[step], dtype=np.float64)
            stepping(env, controller, issued if bit == "1" else np.zeros(6))
        for _ in range(spec["observation_hold_steps"]):
            stepping(env, controller, np.zeros(6))
        measured = pose_from(arm.ee_pose_at_base)
        return env, controller, arm, reset, measured, candidates
    except BaseException:
        env.close()
        raise


def correction_from_history_so3(arm, guessed, goal):
    # In root-aligned body-rotation chart: Rgoal = RxYZ(delta) * Rguessed.
    delta = _r(goal.quaternion_xyzw) * _r(guessed.quaternion_xyzw).inv()
    euler = delta.as_euler("XYZ", degrees=False)
    scale = np.broadcast_to(
        np.asarray(arm.config.rot_lower, dtype=np.float64), (3,)
    )
    if (not np.all(np.isfinite(scale)) or
            np.any(np.abs(scale) <= 1e-8)):
        raise RuntimeError("Unsupported native rotation scaling")
    rotation = euler / scale
    if (not np.all(np.isfinite(rotation))
            or np.linalg.norm(rotation) > 1.0 + 1e-7):
        raise RuntimeError("Recovery rotation outside native unit-ball action")
    native = np.r_[np.zeros(3), rotation]
    # Source-model self-check: no private controller target read.
    observer = ActionHistoryObserver(
        arm.config.pos_lower, arm.config.pos_upper, arm.config.rot_lower,
        frame=arm.config.frame, use_delta=arm.config.use_delta,
        use_target=arm.config.use_target,
        normalize_action=arm.config.normalize_action,
    )
    observer.reset(guessed)
    ticket = observer.prepare(native)
    observer.acknowledge(ticket.ticket, applied=True)
    if quaternion_angle(observer.pose.quaternion_xyzw,
                        goal.quaternion_xyzw) > 1e-6:
        raise RuntimeError("Recovered target does not match source-predicted goal")
    return native


def nearest_source_hypothesis(measured_q, candidates):
    return min(HISTORY_ORDER, key=lambda h: (
        quaternion_angle(measured_q, candidates[h].quaternion_xyzw), h
    ))


def nearest_reset_so3(public_q, reset_q, centroids):
    feat = reset_so3_feature(public_q, reset_q)
    if set(centroids) != set(HISTORY_ORDER):
        raise ValueError("Original training centroid family incomplete")
    return min(HISTORY_ORDER, key=lambda h: (
        quaternion_angle(feat, centroids[h]), h
    ))
