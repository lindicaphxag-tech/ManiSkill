"""Real ManiSkill PhysX controller-reference probe, no policy training.

Only the OUTER evaluator knows true source/target controller names.
The estimator receives read-only translation telemetry and never
receives use_target or a control-mode string. A normalized-zero
command may still cause motion! This is a CPU simulation proof only.

  python research/blind_controller_probe/physx_probe.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch

import mani_skill.envs  # noqa: F401  (registers tasks)
from research.blind_controller_probe.infer import (
    ACHIEVED, TARGET, ABSTAIN, REFUSE, infer_zero_delta_reference,
)

TASKS = ("PickCube-v1", "PushCube-v1")
HIDDEN_MODES = {
    "pd_ee_delta_pose": ACHIEVED,
    "pd_ee_target_delta_pose": TARGET,
}
SEEDS = tuple(range(24001, 24009))
WARMUP_NATIVE_X = 0.25
MAX_WARMUP_TRANSLATION_M = 0.03
MAX_PREPROBE_ROTATION_RAD = 0.10
MAX_PREPROBE_GAP_M = 0.04
OUTPUT = Path("blind_controller_probe_physx_24001_24008.json")


def xyz(pose) -> tuple[float, float, float]:
    if pose is None:
        raise ValueError("controller target pose telemetry missing")
    xyz_array = pose.p.detach().cpu().numpy().reshape(-1, 3)[0]
    x = tuple(float(a) for a in xyz_array)
    if len(x) != 3 or not all(np.isfinite(x)):
        raise ValueError("invalid/unauthenticated target position telemetry")
    return x


def rotation_gap_rad(a, b) -> float:
    qa = a.q.detach().cpu().numpy().reshape(-1, 4)[0]
    qb = b.q.detach().cpu().numpy().reshape(-1, 4)[0]
    aa = qa / np.linalg.norm(qa)
    bb = qb / np.linalg.norm(qb)
    return float(2 * np.arccos(np.clip(abs(np.dot(aa, bb)), 0.0, 1.0)))


def create_world(task: str, mode: str):
    return gym.make(
        task, num_envs=1, obs_mode="state", sim_backend="physx_cpu",
        reconfiguration_freq=1, control_mode=mode,
        disable_env_checker=True,
    )


def experiment(task: str, ground_truth_mode: str, seed: int) -> dict:
    world = create_world(task, ground_truth_mode)
    row = {
        "task": task, "seed": seed,
        "ground_truth_outer_evaluator_only": HIDDEN_MODES[ground_truth_mode],
        "warmup_native_x": WARMUP_NATIVE_X,
        "zero_delta_executed": False,
        "inferred_mode": ABSTAIN,
    }
    try:
        world.reset(seed=seed)
        controller = world.unwrapped.agent.controller
        arm = controller.controllers["arm"]
        cfg = arm.config
        low, high = np.broadcast_to(cfg.pos_lower, 3), np.broadcast_to(cfg.pos_upper, 3)
        warmup_native = np.array([WARMUP_NATIVE_X, 0.0, 0.0])
        neutral_native = np.zeros(3, dtype=np.float64)
        physical_delta = (warmup_native - neutral_native) * (high - low) / 2
        if (
            not np.all(np.isfinite(physical_delta))
            or float(np.linalg.norm(physical_delta)) > MAX_WARMUP_TRANSLATION_M
        ):
            row.update(inferred_mode=REFUSE, reason="warmup outside translation cap")
            return row

        # Standard full 7D Panda native controller action: 6D EE + gripper.
        warmup = torch.zeros((1, 7), dtype=torch.float32, device=arm.device)
        warmup[0, 0] = WARMUP_NATIVE_X
        world.step(warmup)
        pre_achieved_pose = arm.ee_pose_at_base
        pre_target_pose = arm._target_pose
        if pre_target_pose is None:
            row.update(inferred_mode=REFUSE, reason="no prior target telemetry")
            return row
        before_achieved, before_target = xyz(pre_achieved_pose), xyz(pre_target_pose)
        physical_gap_m = float(np.linalg.norm(
            np.asarray(before_achieved) - np.asarray(before_target)
        ))
        rot_gap = rotation_gap_rad(pre_achieved_pose, pre_target_pose)
        row.update(
            preprobe_gap_m=physical_gap_m,
            preprobe_rotation_gap_rad=rot_gap,
            observed_achieved_m=list(before_achieved),
            observed_previous_target_m=list(before_target),
            measured_native_warmup_translation_m=float(np.linalg.norm(physical_delta)),
        )
        if physical_gap_m > MAX_PREPROBE_GAP_M or rot_gap > MAX_PREPROBE_ROTATION_RAD:
            row.update(inferred_mode=REFUSE, reason="unsafe local preprobe discrepancy")
            return row
        if physical_gap_m < 0.001:
            row.update(inferred_mode=ABSTAIN, reason="unidentifiable tracking gap")
            return row

        # This zero-native action may cause physical motion if there is a
        # previous target tracking error. It is NOT a no-motion guarantee.
        zero_action = torch.zeros((1, 7), dtype=torch.float32, device=arm.device)
        world.step(zero_action)
        row["zero_delta_executed"] = True
        measured_after = xyz(arm._target_pose)
        result = infer_zero_delta_reference(
            before_achieved, before_target, measured_after,
        )
        row.update(
            inferred_mode=result.decision,
            reason=result.reason,
            observed_target_after_probe_m=list(measured_after),
            achieved_error_m=result.achieved_error_m,
            previous_target_error_m=result.target_error_m,
        )
        return row
    except (ValueError, RuntimeError) as exc:
        row.update(inferred_mode=REFUSE, reason=str(exc)[:300])
        return row
    finally:
        world.close()


def main():
    evidence = [experiment(t, mode, seed)
                for t in TASKS for mode in HIDDEN_MODES for seed in SEEDS]
    if len(evidence) != 32 or any(
        len([r for r in evidence if r["task"] == t
             and r["ground_truth_outer_evaluator_only"] == label]) != 8
        for t in TASKS for label in HIDDEN_MODES.values()
    ):
        raise RuntimeError("missing or duplicate frozen simulator treatment rows")
    summary = {}
    for task in TASKS:
        for label in HIDDEN_MODES.values():
            rows = [x for x in evidence if x["task"] == task
                    and x["ground_truth_outer_evaluator_only"] == label]
            counts = {kind: sum(r["inferred_mode"] == kind for r in rows)
                      for kind in (ACHIEVED, TARGET, ABSTAIN, REFUSE)}
            correct = counts[label]
            wrong = counts[TARGET if label == ACHIEVED else ACHIEVED]
            summary[f"{task}:{label}"] = {
                "n": 8, "correct": correct, "incorrect": wrong,
                "abstain": counts[ABSTAIN], "refuse": counts[REFUSE],
                "precommitted_accept": correct >= 6 and wrong == 0,
            }
    result = {
        "schema": "mani-skill-telemetry-bound-controller-probe-v1",
        "protocol": "research/blind_controller_probe/PREREGISTRATION.md",
        "backend": "physx_cpu",
        "real_simulator_episodes": len(evidence),
        "trained_policy_updates": 0,
        "summary": summary,
        "all_groups_precommitted_accept": all(
            v["precommitted_accept"] for v in summary.values()
        ),
        "rows": evidence,
        "limitations": [
            "Requires trusted internal target and achieved EE pose telemetry, not pure black-box",
            "Only two supplied controller-mode hypotheses in one robot stack",
            "A normalized zero action is NOT physically motion-free",
            "No freeze-policy task performance measured in this identification-only experiment",
            "Preflight translation gap is not a full real-robot safety certificate",
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("CONTROLLER_ABI_PROBE_RESULT", json.dumps({
        "summary": summary, "all_groups_accept": result["all_groups_precommitted_accept"],
        "episodes": len(evidence),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
