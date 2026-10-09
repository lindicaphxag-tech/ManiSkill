"""Fail-closed audit for a *real* official LeRobot/LIBERO closed-loop pilot.

This only accepts original lerobot-eval eval_info.json from a single fixed task
and a single init-state episode. A successful CI job alone does NOT prove a
successful task: the official per-episode success flag is preserved verbatim.
No ACK faults or ManiSkill controller action translations are claimed here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


class EvidenceError(ValueError):
    pass


def audit(record: dict, *, suite: str = "libero_spatial", task_id: int = 0) -> dict:
    if not isinstance(record, dict):
        raise EvidenceError("Official evaluation object missing")
    tasks = record.get("per_task")
    groups = record.get("per_group")
    overall = record.get("overall")
    if not isinstance(tasks, list) or len(tasks) != 1 or not isinstance(groups, dict) or not isinstance(overall, dict):
        raise EvidenceError("Exactly one official task/group/overall result required")
    task = tasks[0]
    if task.get("task_group") != suite or type(task.get("task_id")) is not int or task["task_id"] != task_id:
        raise EvidenceError("Wrong official LIBERO task identity")
    raw = task.get("metrics")
    if not isinstance(raw, dict):
        raise EvidenceError("Missing original per-episode metrics")
    successes = raw.get("successes")
    if not isinstance(successes, list) or len(successes) != 1 or type(successes[0]) is not bool:
        raise EvidenceError("Missing/ambiguous true official per-episode success flag")
    rewards = raw.get("sum_rewards")
    if not isinstance(rewards, list) or len(rewards) != 1 or not all(
        type(v) in (int, float) and math.isfinite(v) for v in rewards
    ):
        raise EvidenceError("Missing/nonfinite original environment reward")
    if set(groups) != {suite}:
        raise EvidenceError("Unexpected task-group keys in official eval")
    success = int(successes[0])
    for key, summary in (("overall", overall), ("per_group", groups[suite]), ("per_task", task)):
        if type(summary.get("n_episodes")) is not int or summary["n_episodes"] != 1:
            raise EvidenceError(f"Wrong episode count in {key}")
        if type(summary.get("n_success")) is not int or summary["n_success"] != success:
            raise EvidenceError(f"Per-episode versus aggregate mismatch in {key}")
    if type(overall.get("pc_success")) not in (int, float) or abs(overall["pc_success"] - success*100.0) > 1e-6:
        raise EvidenceError("Inconsistent overall success percentage")
    return {
        "evidence_type": "AUTHENTIC_PRETRAINED_VLA_OFFICIAL_LIBERO_CLOSED_LOOP_PILOT",
        "suite": suite,
        "task_id": task_id,
        "n_episodes": 1,
        "n_success": success,
        "real_env_success": successes[0],
        "original_sum_reward": float(rewards[0]),
        "fault_injection_tested": False,
        "unknown_ack_recovery_tested": False,
        "maniskill_physics_tested": False,
        "controller_target_memory_verified": False,
        "not_a_full_benchmark": True,
    }


def _self_test():
    base = {
        "per_task": [{"task_group": "libero_spatial", "task_id": 0,
                       "metrics": {"successes": [True], "sum_rewards": [1.0]},
                       "n_episodes": 1, "n_success": 1}],
        "per_group": {"libero_spatial": {"n_episodes": 1, "n_success": 1}},
        "overall": {"n_episodes": 1, "n_success": 1, "pc_success": 100.0},
    }
    assert audit(base)["real_env_success"] is True
    base["per_task"][0]["metrics"]["successes"] = [False]
    for loc in [base["per_task"][0], base["per_group"]["libero_spatial"], base["overall"]]:
        loc["n_success"] = 0
    base["overall"]["pc_success"] = 0.0
    assert audit(base)["real_env_success"] is False
    base["overall"]["n_success"] = 1
    try:
        audit(base)
    except EvidenceError:
        pass
    else:
        raise AssertionError("Corrupt summary accepted")
    base["overall"]["n_success"] = 0
    base["per_task"][0]["metrics"]["successes"] = [0]
    try:
        audit(base)
    except EvidenceError:
        pass
    else:
        raise AssertionError("Integer truth label accepted")
    print("audit-self-test PASS (success, failure, contradicting count, invalid label)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if args.input is None or args.output is None:
        parser.error("--input and --output are required")
    payload = audit(json.loads(args.input.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
