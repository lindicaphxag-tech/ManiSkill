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
        return {"exists": False, "episodes": 0, "steps": 0, "success_fraction": 0.0, "episode_ids": []}
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
    sa, sb = set(a["episode_ids"]), set(b["episode_ids"])
    a_only, b_only = sorted(sa - sb), sorted(sb - sa)
    return {
        "both_success": len(sa & sb),
        "both_fail": expected - len(sa | sb),
        "a_only_success": len(a_only),
        "b_only_success": len(b_only),
        "a_only_success_ids": a_only,
        "b_only_success_ids": b_only,
        "success_rate_delta": b["success_fraction"] - a["success_fraction"],
        "mcnemar_exact_two_sided_p": exact_mcnemar_two_sided(len(a_only), len(b_only)),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected", type=int, default=100)
    a=p.parse_args()

    variants={}
    for name in VARIANTS:
        path=a.root/f"demos-{name}"/"trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        variants[name]=stats(path,a.expected)

    base=variants["current_main"]
    adapter=variants["contract_adapter_v2"]
    future=variants["contract_adapter_v2_controller_fixed"]
    report={
        "schema_version":1,
        "task":"PickCube-v1",
        "selection_provenance":"PickCube is the task named in the original public reporter reproduction on ManiSkill issue #1138; it was fixed before this cross-task gate was run.",
        "expected_episodes":a.expected,
        "frozen_shas":{
            "upstream_main":"62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3",
            "contract_adapter_v2":"c2a0c20bc5755ab2c87637206ab2a234485990c4",
            "controller_fix":"eed9be164797d41540421bda8adb3840377d7087",
        },
        "variants":variants,
        "paired":{
            "main_vs_adapter":paired(base,adapter,a.expected),
            "main_vs_adapter_controller_fixed":paired(base,future,a.expected),
            "adapter_vs_controller_fixed":paired(adapter,future,a.expected),
        },
        "gates":{
            "controller_mapping_invariance": bool(
                adapter["episode_ids"]==future["episode_ids"] and adapter["steps"]==future["steps"]
            ),
            "adapter_non_regressive_count": adapter["episodes"] >= base["episodes"],
            "future_non_regressive_count": future["episodes"] >= base["episodes"],
            "exact_episode_set_parity_with_main": bool(
                adapter["episode_ids"]==base["episode_ids"] and future["episode_ids"]==base["episode_ids"]
            ),
        },
        "claim_boundary":"Official-demo serial replay on an externally specified second task. This is trajectory-conversion execution evidence, not learned-policy performance or upstream adoption.",
    }
    if report["gates"]["controller_mapping_invariance"] and report["gates"]["adapter_non_regressive_count"] and report["gates"]["future_non_regressive_count"]:
        report["decision"]="cross_task_execution_gate_pass"
    elif report["gates"]["controller_mapping_invariance"]:
        report["decision"]="controller_invariant_but_cross_task_regression"
    else:
        report["decision"]="controller_contract_not_invariant"

    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
