#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import h5py

VARIANTS={
  "main_count2":2,
  "main_count10":10,
  "candidate_count2":2,
  "candidate_with_main_conversion_count2":2,
}

def stats(path:Path,expected:int)->dict:
    if not path.exists():
        return {"exists":False,"episode_ids":[],"episodes":0,"expected":expected}
    with h5py.File(path,"r") as f:
        ids=sorted(int(k.split("_",1)[1]) for k in f.keys() if k.startswith("traj_"))
    return {"exists":True,"episode_ids":ids,"episodes":len(ids),"expected":expected}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    variants={}
    for name,expected in VARIANTS.items():
        path=a.root/f"demos-{name}"/"trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        variants[name]=stats(path,expected)

    checks={
      "main_count2_episode1_success":1 in variants["main_count2"]["episode_ids"],
      "main_count10_episode1_success":1 in variants["main_count10"]["episode_ids"],
      "candidate_count2_episode1_failure":1 not in variants["candidate_count2"]["episode_ids"],
      "main_file_replacement_episode1_success":1 in variants["candidate_with_main_conversion_count2"]["episode_ids"],
    }
    if checks["main_count2_episode1_success"] and checks["main_file_replacement_episode1_success"]:
        diagnosis="monkeypatch_intervention_not_endpoint_equivalent"
    elif not checks["main_count2_episode1_success"]:
        diagnosis="count2_regime_not_equivalent_to_certified_count10"
    elif not checks["main_file_replacement_episode1_success"]:
        diagnosis="candidate_checkout_has_unexpected_runtime_difference_or_file_replacement_insufficient"
    else:
        diagnosis="mixed_or_undetermined"

    report={
      "schema_version":1,
      "frozen_shas":{
        "current_main":"107c9528b23b55bd276cf723c260a45ae7ce00ec",
        "clean_adapter_v2":"bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
      },
      "variants":variants,
      "checks":checks,
      "diagnosis":diagnosis,
      "claim_boundary":"Endpoint-regime audit for causal-intervention validity; not a repair performance benchmark."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
