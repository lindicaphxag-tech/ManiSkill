#!/usr/bin/env python3
"""Independent audit of the 100-199 precommitted original-demo holdout.

All scores use the ORIGINAL source-denominator, never post-treatment training
survivors. Takes the actual GitHub Actions artifact and separately pinned
original demo ZIP; no simulator, CUDA, author inference or live PR needed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from audit_factorial_replay import audit

ARCHIVE_SHA = "7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c"
RUN_SHA = "e6ff03f291cbc262d6218fa3299f567c5f308574"
ARTIFACT_RUN = 37745942944
OFFSET, N = 100, 100
EXPECTED = {
    "upstream_baseline": 90,
    "converter_only_pr1495": 91,
    "controller_only_pr1472": 1,
    "combined_pr1495_pr1472": 91,
}

def one(root: Path, name: str) -> Path:
    files=list(root.rglob(name))
    if len(files)!=1:
        raise ValueError(f"expected one actual {name}, got {len(files)}")
    return files[0]

def archived_metadata(path: Path) -> dict:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        while chunk:=stream.read(1024*1024):
            h.update(chunk)
    if h.hexdigest()!=ARCHIVE_SHA:
        raise ValueError("original official demo ZIP SHA-256 drift")
    with zipfile.ZipFile(path) as z:
        names=[n for n in z.namelist()
               if n.endswith("/PegInsertionSide-v1/motionplanning/trajectory.json")
               or n=="PegInsertionSide-v1/motionplanning/trajectory.json"]
        if len(names)!=1:
            raise ValueError(f"original ZIP metadata cardinality: {names}")
        return json.loads(z.read(names[0]))

def validate(matrix: dict, log: dict, source_metadata: dict) -> dict:
    # First verify the original evidence unit, before computing contrasts.
    if log.get("status")!="passed":
        raise ValueError("original execution was not a pass")
    if log.get("source_episode_offset")!=OFFSET:
        raise ValueError("holdout origin offset is not the locked 100")
    if log.get("source_episode_indices")!=list(range(OFFSET,OFFSET+N)):
        raise ValueError("holdout indices do not equal locked 100..199")
    if matrix.get("original_source_episode_offset")!=OFFSET:
        raise ValueError("matrix doesn't bind the 100-199 holdout")
    if matrix.get("sample_size")!=N:
        raise ValueError("original source-denominator is not 100")

    raw=source_metadata.get("episodes", [])
    if len(raw)<OFFSET+N:
        raise ValueError("pinned archive has insufficient source episodes")
    cohort=raw[OFFSET:OFFSET+N]
    ids=[row["episode_id"] for row in cohort]
    seeds=[int(row["episode_seed"]) for row in cohort]
    if any(row.get("success") is not True for row in cohort):
        raise ValueError("pinned holdout includes unsuccessful source episode")
    if len(set(seeds))!=N or len(set(ids))!=N:
        raise ValueError("non-unique source seed or episode")
    selected=log["raw_dataset"]["replay_selection"]
    if selected["count"]!=N or selected["episode_ids"]!=ids or selected["all_successful"] is not True:
        raise ValueError("selected source IDs differ from pinned original ZIP")
    observed=[row["source_seed"] for row in matrix["source_seed_matrix"]]
    if observed!=seeds:
        raise ValueError("holdout source seed order differs from original ZIP")
    frozen=log.get("factorial_replay",{})
    for key in ("source_seed_matrix","per_arm_success_count",
                "four_way_intersection_count",
                "four_way_intersection_source_seed_sha256"):
        if frozen.get(key)!=matrix.get(key):
            raise ValueError(f"original run log and evidence matrix disagree on {key}")

    recomputed=audit(matrix)
    if recomputed["success_counts"]!=EXPECTED:
        raise ValueError(f"unexpected actual original holdout counts: {recomputed['success_counts']}")
    if recomputed["four_way_intersection"]!=0:
        raise ValueError("holdout four-way selected intersection was not zero")
    if recomputed["source_matched_factorial_interaction_exact"]!="89/100":
        raise ValueError("holdout original-denominator interaction mismatch")

    B=EXPECTED["upstream_baseline"]/N
    K=EXPECTED["controller_only_pr1472"]/N
    CK=EXPECTED["combined_pr1495_pr1472"]/N
    assert B-K>=0.20 and CK-K>=0.20
    return {
      "audit":"passed",
      "cohort":"precommitted original indices 100..199",
      "origin":"official public ManiSkill demos, unchanged source SHA-256",
      "source_dataset_sha256":ARCHIVE_SHA,
      "head_run":ARTIFACT_RUN,
      "exact_run_head_sha":RUN_SHA,
      "source_index_first":OFFSET,
      "source_index_last":OFFSET+N-1,
      "original_denominator":N,
      "success_counts":recomputed["success_counts"],
      "source_matched_factorial_interaction_exact":recomputed["source_matched_factorial_interaction_exact"],
      "controller_only_penalty_absolute":B-K,
      "composition_vs_controller_only_absolute":CK-K,
      "frozen_thresholds_pass":True,
      "four_way_intersection":0,
      "trainable_four_arm_factorial":False,
      "recomputed_seed_matrix":True,
      "independence_boundary":"Author-run holdout, distinct source indices but NOT a third-party replication",
      "outcome_boundary":"Official demo replay, not trained Diffusion Policy or robot-task success",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--official-archive",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    root=a.evidence_dir
    result=validate(json.loads(one(root,"factorial_replay.json").read_text()),
                    json.loads(one(root,"experiment_log.json").read_text()),
                    archived_metadata(a.official_archive))
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(a.output.read_text())

if __name__=="__main__":
    main()
