"""Prospective real PhysX ZERO-native-probe collection, not an ACK detector.

The pre-outcome protocol freezes two robot embodiments and disjoint 4+4
calibration/heldout seeds. It does NOT test proposed nonzero probe selection,
frozen PPO task recovery, actual network ACK loss or hardware safety.

Private controller getter is used ONLY AFTER each physical step for audit.
Candidate target histories used by a possible runtime are command-observer
projections; public achieved pose is collected independently for each truth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import mani_skill.envs
import numpy as np

from research.cross_robot_ack_physics import (
    ARM_MODE, TASK, get_arm, observer_for, pose_from, pose_residual,
    requested_native, stepping, actual_target_after_physics,
)


PROTO = Path("research/PUBLIC_ZERO_PROBE_CROSS_ROBOT_PREOUTCOME_V1.json")
BASE_SEED = {"panda": 640001, "xarm6_robotiq": 650001}
FAULT_STEP = 2
PROBE_STEP = 3


def public_achieved(arm):
    """Public achieved EE state: this is NOT controller.target_pose."""
    return np.asarray(
        arm.ee_pose_at_base.p.detach().cpu(), dtype=float
    ).reshape(-1, 3)[0].tolist()


def one_seed(robot: str, seed: int) -> dict:
    sims = {}
    record = dict(robot=robot, seed=seed, task=TASK, truth_branches={},
                  fault_step=FAULT_STEP, probe_step=PROBE_STEP,
                  target_getter_only_after_step_for_audit=True)
    try:
        for truth in ("applied", "held"):
            e = gym.make(TASK, robot_uids=robot, num_envs=1, obs_mode="state",
                         sim_backend="physx_cpu", reconfiguration_freq=1,
                         control_mode=ARM_MODE, disable_env_checker=True)
            e.reset(seed=seed)
            sims[truth] = e
        controllers = {truth: get_arm(e) for truth, e in sims.items()}
        observers = {truth: observer_for(arm) for truth, (_, arm) in controllers.items()}
        reset_xyz = {truth: public_achieved(arm) for truth, (_, arm) in controllers.items()}
        if np.linalg.norm(np.asarray(reset_xyz["applied"]) -
                          np.asarray(reset_xyz["held"])) > 1e-5:
            raise RuntimeError("Matched physical reset diverged")
        states = {truth: dict(public_before=None, public_after=None,
                              post_fault_target_history_xyz=None,
                              target_observer_residual_max_m=0.0,
                              physical_fault_native_zero_applied=False)
                  for truth in sims}
        for t in range(PROBE_STEP + 1):
            for truth in ("applied", "held"):
                ctrl, arm = controllers[truth]
                native = requested_native(t)
                if t == FAULT_STEP and truth == "held":
                    native = np.zeros(6, dtype=float)
                    states[truth]["physical_fault_native_zero_applied"] = True
                if t == PROBE_STEP:
                    states[truth]["public_before"] = public_achieved(arm)
                    if np.any(native != 0):
                        raise RuntimeError("Known-delivered probe MUST be ZERO native arm action")
                ticket = observers[truth].prepare(native)
                stepping(sims[truth], ctrl, native)
                observers[truth].acknowledge(ticket.ticket, applied=True)
                # Actual hidden state read ONLY after physical step, for audit.
                actual = actual_target_after_physics(arm)
                residual = pose_residual(observers[truth].pose, actual)
                states[truth]["target_observer_residual_max_m"] = max(
                    states[truth]["target_observer_residual_max_m"], residual["l2_m"])
                if residual["linf_m"] > 1e-4 or residual["so3_rad"] > 1e-3:
                    raise RuntimeError("Actual native hidden target disagrees with action history")
                if t == FAULT_STEP:
                    states[truth]["post_fault_target_history_xyz"] = [
                        float(v) for v in observers[truth].pose.position]
                if t == PROBE_STEP:
                    states[truth]["public_after"] = public_achieved(arm)
                    states[truth]["observed_post_probe_target_error_m"] = residual["l2_m"]
        hypotheses = [states[truth]["post_fault_target_history_xyz"]
                      for truth in ("applied", "held")]
        if np.linalg.norm(np.asarray(hypotheses[0]) - np.asarray(hypotheses[1])) < 1e-5:
            raise RuntimeError("Native physical ACK fault did not separate target hypotheses")
        for truth in ("applied", "held"):
            states[truth]["observed_probe_displacement_m"] = float(
                np.linalg.norm(np.asarray(states[truth]["public_after"]) -
                               np.asarray(states[truth]["public_before"])))
        record["history_targets_xyz_m_from_command_observer"] = hypotheses
        record["truth_branches"] = states
        record["known_delivered_probe_native_6d"] = [0.0] * 6
        record["source_policy_used"] = False
        record["native_physx_cpu_executed"] = True
        return record
    finally:
        for e in sims.values():
            e.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", choices=tuple(BASE_SEED), required=True)
    parser.add_argument("--chunk", type=int, choices=(0, 1), required=True)
    args = parser.parse_args()
    proto_bytes = PROTO.read_bytes()
    proto_hash = hashlib.sha1(
        b"blob " + str(len(proto_bytes)).encode() + b"\0" + proto_bytes).hexdigest()
    start = BASE_SEED[args.robot] + 4 * args.chunk
    expected = list(range(start, start + 4))
    rows = [one_seed(args.robot, seed) for seed in expected]
    if [r["seed"] for r in rows] != expected:
        raise RuntimeError("Missing preregistered native PhysX seeds")
    out = dict(schema="public_zero_probe_cross_robot_native_physx_v1",
               preregistration_git_blob=proto_hash,
               robot=args.robot, chunk=args.chunk, seeds=expected,
               split="CALIBRATION" if args.chunk == 0 else "UNSEEN_HELDOUT",
               rows=rows, actual_native_physics=True,
               author_operated_not_independent_replication=True,
               no_ppo_task_success_or_hardware_safety=True)
    path = Path(f"public_zero_probe_{args.robot}_chunk{args.chunk}_original4.json")
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("REAL_PHYSX_PUBLIC_ZERO_PROBE", json.dumps(dict(
        robot=args.robot, split=out["split"], seeds=expected,
        probe_displacements=[round(r["truth_branches"][t]["observed_probe_displacement_m"], 6)
                             for r in rows for t in ("applied", "held")]), sort_keys=True))


if __name__ == "__main__":
    main()
