#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import h5py


VARIANTS = (
    "current_main",
    "contract_adapter_v2",
    "contract_adapter_v2_controller_fixed",
)
FAIL_RE = re.compile(r"Episode\s+(\d+)\s+is not replayed successfully")
SUMMARY_RE = re.compile(
    r"Replayed\s+(\d+)\s+episodes,\s+(\d+)/(\d+)=([0-9.]+)% demos saved"
)


def stats(path: Path, log_path: Path, expected: int) -> dict:
    saved_count = 0
    steps = 0
    if path.exists():
        with h5py.File(path, "r") as f:
            keys = [k for k in f.keys() if k.startswith("traj_")]
            saved_count = len(keys)
            steps = sum(len(f[k]["actions"]) for k in keys if "actions" in f[k])

    if not log_path.exists():
        raise RuntimeError(f"missing replay provenance log: {log_path}")
    text = log_path.read_text(encoding="utf-8", errors="replace")
    failed_ids = sorted({int(x) for x in FAIL_RE.findall(text)})
    success_ids = [i for i in range(expected) if i not in set(failed_ids)]
    summaries = SUMMARY_RE.findall(text)
    if not summaries:
        raise RuntimeError(f"missing replay summary in {log_path}")
    replayed, reported_saved, denominator, percent = summaries[-1]
    if int(replayed) != expected or int(denominator) != expected:
        raise RuntimeError(
            f"unexpected replay denominator in {log_path}: {summaries[-1]}"
        )
    if int(reported_saved) != len(success_ids):
        raise RuntimeError(
            f"source-id reconstruction disagrees with replay summary in {log_path}"
        )
    if path.exists() and saved_count != len(success_ids):
        raise RuntimeError(
            f"saved artifact count disagrees with source-id log in {log_path}: "
            f"artifact={saved_count} source_success={len(success_ids)}"
        )

    return {
        "exists": path.exists(),
        "episodes": len(success_ids),
        "steps": int(steps),
        "success_fraction": len(success_ids) / expected if expected else 0.0,
        "source_success_episode_ids": success_ids,
        "source_failed_episode_ids": failed_ids,
        "reported_percent": float(percent),
        "artifact_episode_keys_are_renumbered": True,
        "identity_source": "replay log source episode ids; never output HDF5 traj_k",
    }


def exact_mcnemar_two_sided(a_only: int, b_only: int) -> float:
    n = a_only + b_only
    if n == 0:
        return 1.0
    k = min(a_only, b_only)
    lower = sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * lower)


def paired(a: dict, b: dict, expected: int) -> dict:
    sa = set(a["source_success_episode_ids"])
    sb = set(b["source_success_episode_ids"])
    a_only = sorted(sa - sb)
    b_only = sorted(sb - sa)
    both = sorted(sa & sb)
    return {
        "both_success_ids": both,
        "both_success": len(both),
        "both_fail": expected - len(sa | sb),
        "a_only_success_ids": a_only,
        "b_only_success_ids": b_only,
        "a_only_success": len(a_only),
        "b_only_success": len(b_only),
        "success_rate_delta": b["success_fraction"] - a["success_fraction"],
        "mcnemar_exact_two_sided_p": exact_mcnemar_two_sided(
            len(a_only), len(b_only)
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected", type=int, default=10)
    a = p.parse_args()

    variants = {}
    for name in VARIANTS:
        path = (
            a.root
            / f"demos-{name}"
            / "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        )
        variants[name] = stats(path, a.root / f"{name}.replay.log", a.expected)

    base = variants["current_main"]
    current = variants["contract_adapter_v2"]
    future = variants["contract_adapter_v2_controller_fixed"]

    base_vs_current = paired(base, current, a.expected)
    base_vs_future = paired(base, future, a.expected)
    current_vs_future = paired(current, future, a.expected)

    exact_controller_invariance = bool(
        current["source_success_episode_ids"]
        == future["source_success_episode_ids"]
        and current["steps"] == future["steps"]
    )
    non_regressive_both = bool(
        current["episodes"] >= base["episodes"]
        and future["episodes"] >= base["episodes"]
    )
    episode_set_parity_with_base = bool(
        current["source_success_episode_ids"]
        == base["source_success_episode_ids"]
        and future["source_success_episode_ids"]
        == base["source_success_episode_ids"]
    )

    if exact_controller_invariance and non_regressive_both:
        decision = "advance_candidate_v2"
    elif non_regressive_both:
        decision = "non_regressive_but_controller_sensitive"
    elif exact_controller_invariance:
        decision = "controller_invariant_but_execution_regresses"
    else:
        decision = "reject_or_revise"

    report = {
        "schema_version": 2,
        "claim_boundary": (
            "Same-base official-demo serial replay observation. Source episode "
            "identity is reconstructed only from replay logs because RecordEpisode "
            "renumbers saved output trajectories. Repeatability must be established "
            "before this result can serve as a canonical execution-effect certificate."
        ),
        "expected_episodes": a.expected,
        "frozen_shas": {
            "current_main": "107c9528b23b55bd276cf723c260a45ae7ce00ec",
            "contract_adapter_v2": "bd0e4feae2491a0d433107210ce8c16b8e8fb69a",
            "controller_fix": "eed9be164797d41540421bda8adb3840377d7087",
        },
        "identity_provenance": {
            "source_episode_identity": "replay log",
            "output_hdf5_keys": "renumbered saved-trajectory identity; not source identity",
        },
        "variants": variants,
        "paired": {
            "current_main_vs_contract_adapter_v2": base_vs_current,
            "current_main_vs_contract_adapter_v2_controller_fixed": base_vs_future,
            "contract_adapter_v2_vs_controller_fixed": current_vs_future,
        },
        "gates": {
            "exact_controller_invariance": exact_controller_invariance,
            "non_regressive_both": non_regressive_both,
            "episode_set_parity_with_base": episode_set_parity_with_base,
        },
        "decision": decision,
        "decision_policy": (
            "This serial-run decision is provisional. Do not promote it to repair "
            "authority unless a separate repeatability certificate passes."
        ),
    }

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
