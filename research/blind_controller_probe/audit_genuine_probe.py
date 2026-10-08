"""Independent original-episode audit of published PhysX active-probe artifact.

This is a pure CPU checker of *contributor-generated* simulator evidence.
It does not run ManiSkill nor create independent physical measurements.
"""
from __future__ import annotations
from collections import Counter
import json
import math
from pathlib import Path
import sys

from infer import (
    ABSTAIN, ACHIEVED, REFUSE, TARGET, infer_zero_delta_reference,
)

SOURCE_RUN_ID = 37817533332
SOURCE_HEAD_SHA = "4ac39699c694600ae33f21386eddd12e63cbe427"
TASKS = ("PickCube-v1", "PushCube-v1")
MODES = (ACHIEVED, TARGET)
SEEDS = tuple(range(24001, 24009))


def audit(data: dict) -> dict:
    if data.get("schema") != "mani-skill-telemetry-bound-controller-probe-v1":
        raise ValueError("wrong frozen evidence schema")
    if data.get("real_simulator_episodes") != 32:
        raise ValueError("incorrect original simulation episode denominator")
    if data.get("trained_policy_updates") != 0:
        raise ValueError("unexpected training provenance claim")
    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != 32:
        raise ValueError("missing source simulator episodes")
    expected = [(task, mode, seed)
                for task in TASKS for mode in MODES for seed in SEEDS]
    recorded = [(r.get("task"), r.get("ground_truth_outer_evaluator_only"),
                 r.get("seed")) for r in rows]
    if recorded != expected:
        raise ValueError("missing/duplicated/reordered preregistered source episodes")
    summary = {}
    audit_rows = []
    for t in TASKS:
        for mode in MODES:
            rs = [r for r in rows if r["task"] == t and
                  r["ground_truth_outer_evaluator_only"] == mode]
            counters = Counter()
            for r in rs:
                if not r.get("zero_delta_executed", False):
                    if r.get("inferred_mode") not in (ABSTAIN, REFUSE):
                        raise ValueError("claim of diagnosis without issued probe")
                else:
                    for k in ("preprobe_gap_m", "preprobe_rotation_gap_rad",
                              "measured_native_warmup_translation_m"):
                        v = r.get(k)
                        if not isinstance(v, (float, int)) or not math.isfinite(v):
                            raise ValueError("invalid/missing bounded intervention evidence")
                    if r["preprobe_gap_m"] > 0.04 + 1e-8:
                        raise ValueError("unbounded target tracking discrepancy")
                    if r["preprobe_rotation_gap_rad"] > 0.10 + 1e-8:
                        raise ValueError("unbounded orientation mismatch")
                    if r["measured_native_warmup_translation_m"] > 0.03 + 1e-8:
                        raise ValueError("unbounded warm-up command")
                    decision = infer_zero_delta_reference(
                        r["observed_achieved_m"],
                        r["observed_previous_target_m"],
                        r["observed_target_after_probe_m"],
                    )
                    if r["inferred_mode"] != decision.decision:
                        raise ValueError("fabricated decision contradicts original telemetry")
                    if r["preprobe_gap_m"] < 0.001:
                        raise ValueError("unsafe/unidentifiable probe executed")
                counters[r["inferred_mode"]] += 1
                audit_rows.append({
                    "task": t, "true_mode": mode, "seed": r["seed"],
                    "predicted": r["inferred_mode"],
                    "zero_probe_executed": bool(r["zero_delta_executed"]),
                    "tracking_gap_m": r.get("preprobe_gap_m"),
                })
            correct = counters[mode]
            incorrect = counters[TARGET if mode == ACHIEVED else ACHIEVED]
            summary[f"{t}:{mode}"] = {
                "n": 8, "correct": correct, "incorrect": incorrect,
                "abstain": counters[ABSTAIN], "refuse": counters[REFUSE],
                "precommitted_accept": correct >= 6 and incorrect == 0,
            }
    if summary != data.get("summary"):
        raise ValueError("reported summary disagrees with all original source episodes")
    if bool(data.get("all_groups_precommitted_accept")) != all(
        x["precommitted_accept"] for x in summary.values()
    ):
        raise ValueError("forgeable claimed overall experiment acceptance")
    return {
        "audit": "ALL_32_ORIGINAL_SOURCE_ROWS_RECONSTRUCTED",
        "source_action_run": SOURCE_RUN_ID, "source_head": SOURCE_HEAD_SHA,
        "summary": summary, "rows": audit_rows,
        "not_a_claim": "No unseen hardware/controller types, policy training or real-world safety",
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python audit_genuine_probe.py RAW_ACTIONS_JSON")
    path = Path(sys.argv[1])
    actual = audit(json.loads(path.read_text(encoding="utf-8")))
    print("AUDITED_REAL_PHYSX_PROBE", json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
