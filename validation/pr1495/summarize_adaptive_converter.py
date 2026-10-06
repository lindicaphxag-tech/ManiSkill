#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import h5py

def stats(path: Path, expected: int) -> dict:
    if not path.exists():
        return {"exists": False, "episodes": 0, "steps": 0, "success_fraction": 0.0}
    with h5py.File(path, "r") as f:
        keys=[k for k in f.keys() if k.startswith("traj_")]
        steps=sum(len(f[k]["actions"]) for k in keys if "actions" in f[k])
    return {
        "exists": True,
        "episodes": len(keys),
        "steps": int(steps),
        "success_fraction": len(keys)/expected if expected else 0.0,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected", type=int, default=10)
    a=p.parse_args()

    variants={}
    for name in ["main","adaptive_current","adaptive_controller_fixed"]:
        path=a.root/f"demos-{name}"/"trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        variants[name]=stats(path,a.expected)

    baseline=variants["main"]
    current=variants["adaptive_current"]
    future=variants["adaptive_controller_fixed"]

    controller_mapping_invariant = bool(
        current["exists"] and future["exists"]
        and current["episodes"] == future["episodes"]
        and current["steps"] == future["steps"]
    )
    baseline_non_regression = bool(
        baseline["exists"] and current["exists"] and future["exists"]
        and current["episodes"] >= baseline["episodes"]
        and future["episodes"] >= baseline["episodes"]
    )
    exact_baseline_parity = bool(
        baseline["exists"] and current["exists"] and future["exists"]
        and current["episodes"] == baseline["episodes"] == future["episodes"]
        and current["steps"] == baseline["steps"] == future["steps"]
    )

    if controller_mapping_invariant and baseline_non_regression:
        decision="candidate_for_upstream_v2"
    elif controller_mapping_invariant:
        decision="controller_invariant_but_baseline_regresses"
    else:
        decision="reject_or_revise"

    report={
      "schema_version":2,
      "claim_boundary":"Official-demo serial replay evidence for controller-aware converter encoding; not policy-training success.",
      "expected_episodes":a.expected,
      "variants":variants,
      "controller_mapping_invariant":controller_mapping_invariant,
      "baseline_non_regression":baseline_non_regression,
      "exact_baseline_parity":exact_baseline_parity,
      "decision":decision,
    }
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
