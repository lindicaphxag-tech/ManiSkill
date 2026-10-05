#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import h5py

def stats(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "episodes": 0, "steps": 0}
    with h5py.File(path, "r") as f:
        keys=[k for k in f.keys() if k.startswith("traj_")]
        steps=sum(len(f[k]["actions"]) for k in keys if "actions" in f[k])
    return {"exists": True, "episodes": len(keys), "steps": int(steps)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a=p.parse_args()
    variants=["main","converter_only","controller_only","composed"]
    report={"schema_version":1,
      "claim_boundary":"Replay-success matrix over the same first official PegInsertionSide demonstrations; diagnoses interaction between converter representation and controller sign semantics, not policy-training quality.",
      "variants":{}}
    for v in variants:
        path=a.root/f"demos-{v}"/"trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        report["variants"][v]=stats(path)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
