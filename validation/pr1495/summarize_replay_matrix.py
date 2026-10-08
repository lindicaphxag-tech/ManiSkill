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
        "success_fraction": len(keys) / expected if expected else 0.0,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected", type=int, default=10)
    a=p.parse_args()
    variants=["main","converter_only","controller_only","composed"]
    results={}
    for v in variants:
        path=a.root/f"demos-{v}"/"trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        results[v]=stats(path,a.expected)

    base=results["main"]["success_fraction"]
    converter=results["converter_only"]["success_fraction"]
    controller=results["controller_only"]["success_fraction"]
    composed=results["composed"]["success_fraction"]
    complete=all(results[v]["exists"] for v in variants)
    strict=bool(
        complete
        and converter < base
        and controller < base
        and composed >= base
    )

    report={
      "schema_version":2,
      "claim_boundary":"Replay-success matrix over the same first official PegInsertionSide demonstrations; diagnoses interaction between converter representation and controller sign semantics, not policy-training quality.",
      "expected_episodes":a.expected,
      "variants":results,
      "interaction":{
        "complete_factorial_evidence":complete,
        "strict_compensating_bundle":strict,
        "bundle":["controller-sign","converter-representation"] if strict else [],
        "authorization":{
          "converter_only":"reject" if strict else "undetermined",
          "controller_only":"reject" if strict else "undetermined",
          "composed":"allow" if strict else "undetermined",
        }
      }
    }
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
