#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import h5py


VARIANTS = (
    "current_main",
    "contract_adapter_v2",
    "contract_adapter_v2_controller_fixed",
)


def stats(path: Path, expected: int) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "episodes": 0,
            "steps": 0,
            "success_fraction": 0.0,
            "episode_ids": [],
        }
    with h5py.File(path, "r") as f:
        keys = sorted(
            (k for k in f.keys() if k.startswith("traj_")),
            key=lambda k: int(k.split("_", 1)[1]),
        )
        steps = sum(len(f[k]["actions"]) for k in keys if "actions" in f[k])
    ids = [int(k.split("_", 1)[1]) for k in keys]
    return {
        "exists": True,
        "episodes": len(ids),
        "steps": int(steps),
        "success_fraction": len(ids) / expected if expected else 0.0,
        "episode_ids": ids,
    }


def exact_mcnemar_two_sided(a_only: int, b_only: int) -> float:
    n = a_only + b_only
    if n == 0:
        return 1.0
    k = min(a_only, b_only)
    lower = sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * lower)


def paired(a: dict, b: dict, expected: int) -> dict:
    sa = set(a["episode_ids"])
    sb = set(b["episode_ids"])
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
        variants[name] = stats(path, a.expected)

    base = variants["current_main"]
    current = variants["contract_adapter_v2"]
    future = variants["contract_adapter_v2_controller_fixed"]

    base_vs_current = paired(base, current, a.expected)
    base_vs_future = paired(base, future, a.expected)
    current_vs_future = paired(current, future, a.expected)

    exact_controller_invariance = bool(
        current["episode_ids"] == future["episode_ids"]
        and current["steps"] == future["steps"]
    )
    non_regressive_both = bool(
        current["episodes"] >= base["episodes"]
        and future["episodes"] >= base["episodes"]
    )
    episode_set_parity_with_base = bool(
        current["episode_ids"] == base["episode_ids"]
        and future["episode_ids"] == base["episode_ids"]
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
        "schema_version": 1,
        "claim_boundary": (
            "Same-base official-demo replay gate for a controller-contract "
            "adapter. All three variants share current_main@107c9528 as the "
            "software baseline except for the named intervention. This is "
            "execution-domain replay evidence, not learned-policy performance."
        ),
        "expected_episodes": a.expected,
        "frozen_shas": {
            "current_main": "107c9528b23b55bd276cf723c260a45ae7ce00ec",
            "contract_adapter_v2": "bd0e4feae2491a0d433107210ce8c16b8e8fb69a",
            "controller_fix": "eed9be164797d41540421bda8adb3840377d7087",
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
            "Advance only if the adapter remains execution-non-regressive under "
            "both historical and sign-preserving controller mappings. Exact "
            "episode-set parity is reported separately and is not silently "
            "substituted by count parity."
        ),
    }

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
