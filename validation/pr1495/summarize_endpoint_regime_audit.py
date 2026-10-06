#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import h5py

VARIANTS={
  "main_count2":2,
  "main_count10":10,
  "candidate_count2":2,
  "candidate_with_main_conversion_count2":2,
}
FAIL_RE=re.compile(r"Episode\s+(\d+)\s+is not replayed successfully")
SUMMARY_RE=re.compile(r"Replayed\s+(\d+)\s+episodes,\s+(\d+)/(\d+)=([0-9.]+)% demos saved")


def stats(path:Path, input_json:Path, log_path:Path, expected:int)->dict:
    metadata=json.loads(input_json.read_text(encoding="utf-8"))
    source_ids=[int(ep["episode_id"]) for ep in metadata["episodes"][:expected]]
    if len(source_ids)!=expected:
        raise RuntimeError(f"expected {expected} source episodes, got {len(source_ids)}")

    text=log_path.read_text(encoding="utf-8",errors="replace")
    failed=sorted({int(x) for x in FAIL_RE.findall(text)})
    unknown=sorted(set(failed)-set(source_ids))
    if unknown:
        raise RuntimeError(f"failure log contains ids outside frozen source set: {unknown}")
    success=[x for x in source_ids if x not in set(failed)]

    summaries=SUMMARY_RE.findall(text)
    if not summaries:
        raise RuntimeError(f"missing replay summary in {log_path}")
    replayed,saved,denom,pct=summaries[-1]
    if int(replayed)!=expected or int(denom)!=expected or int(saved)!=len(success):
        raise RuntimeError(
            f"replay/log identity mismatch for {log_path}: summary={summaries[-1]} success={success}"
        )

    artifact_count=0
    if path.exists():
        with h5py.File(path,"r") as f:
            artifact_count=sum(k.startswith("traj_") for k in f.keys())
    if artifact_count!=len(success):
        raise RuntimeError(
            f"renumbered artifact count disagrees with source outcomes: artifact={artifact_count} source={len(success)}"
        )

    return {
      "exists":path.exists(),
      "source_episode_ids":source_ids,
      "source_success_episode_ids":success,
      "source_failed_episode_ids":failed,
      "episodes":len(success),
      "expected":expected,
      "reported_percent":float(pct),
      "identity_source":"input trajectory.json + replay source-id failure log",
      "output_hdf5_keys_are_renumbered":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()

    variants={}
    for name,expected in VARIANTS.items():
        demo=a.root/f"demos-{name}"
        path=demo/"trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        variants[name]=stats(
            path,
            demo/"trajectory.json",
            a.root/f"{name}.replay.log",
            expected,
        )

    checks={
      "main_count2_episode1_success":1 in variants["main_count2"]["source_success_episode_ids"],
      "main_count10_episode1_success":1 in variants["main_count10"]["source_success_episode_ids"],
      "candidate_count2_episode1_failure":1 in variants["candidate_count2"]["source_failed_episode_ids"],
      "main_file_replacement_episode1_success":1 in variants["candidate_with_main_conversion_count2"]["source_success_episode_ids"],
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
      "schema_version":2,
      "frozen_shas":{
        "current_main":"107c9528b23b55bd276cf723c260a45ae7ce00ec",
        "clean_adapter_v2":"bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
      },
      "identity_provenance":{
        "source_episode_identity":"input JSON + replay log",
        "output_hdf5_keys":"renumbered saved-output ordinals; prohibited for source pairing",
      },
      "variants":variants,
      "checks":checks,
      "diagnosis":diagnosis,
      "claim_boundary":"Endpoint-regime audit for causal-intervention validity; source identity is provenance-bound and output HDF5 ordinals are never used as source episode IDs."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
