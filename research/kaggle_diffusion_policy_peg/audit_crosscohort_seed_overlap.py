#!/usr/bin/env python3
"""Audit both *original* GitHub Actions 100-demo factorial artifacts together.

First cohort: original episode indices 0-99,  run 37719545972.
Second cohort: original episode indices 100-199, run 37752565886.

Important: distinct source EPISODES do not guarantee distinct source SEEDS.
This auditor explicitly measures that overlap, and reports the post-hoc
seed-disjoint sensitivity subset without cherry-picking based on success.
It cannot prove byte-level equality with the remote original HF data on its
own: physical HDF5 slicing is checked through the materialization/identity
attestation saved in the source experiment log and audited independently.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import json
from audit_factorial_replay import ARMS, verify, verify_execution_binding

FIRST_RUN=37719545972
HELDOUT_RUN=37752565886


def load_one(root: Path, *, cohort: str) -> tuple[dict, dict]:
    paths=list(root.rglob("factorial_replay.json"))
    if len(paths)!=1:
        raise ValueError(f"{cohort}: expected exactly one factorial ledger, found {len(paths)}")
    logs=list(root.rglob("experiment_log.json"))
    if len(logs)!=1:
        raise ValueError(f"{cohort}: expected exactly one raw experiment log, found {len(logs)}")
    return json.loads(paths[0].read_text()), json.loads(logs[0].read_text())


def audit(first_root: Path, heldout_root: Path) -> dict:
    first, first_execution=load_one(first_root, cohort="first")
    holdout, execution=load_one(heldout_root, cohort="heldout")

    first_result=verify(first,expected_size=100,source_offset=0,origin_run_id=FIRST_RUN)
    holdout_result=verify(holdout,expected_size=100,source_offset=100,origin_run_id=HELDOUT_RUN)
    physical=verify_execution_binding(holdout,execution,offset=100,count=100)
    if first_execution.get("status") != "passed":
        raise ValueError("first source execution did not pass")
    for k in ARMS:
        if first["per_arm_success_count"][k]!=first_result["per_arm_success_count"][k]:
            raise ValueError("first source evidence mismatch")
        if holdout["per_arm_success_count"][k]!=holdout_result["per_arm_success_count"][k]:
            raise ValueError("heldout evidence mismatch")

    first_seeds=[r["source_seed"] for r in first["source_seed_matrix"]]
    heldout_seeds=[r["source_seed"] for r in holdout["source_seed_matrix"]]
    first_set=set(first_seeds)
    second_set=set(heldout_seeds)
    if len(first_set)!=100 or len(second_set)!=100:
        raise ValueError("a single cohort contains nonunique episode seeds")
    overlapping=first_set & second_set
    nonoverlap_rows=[r for r in holdout["source_seed_matrix"] if r["source_seed"] not in first_set]
    overlapping_rows=[r for r in holdout["source_seed_matrix"] if r["source_seed"] in first_set]
    if len(nonoverlap_rows)+len(overlapping_rows)!=100:
        raise AssertionError("cohort-loss in exclusion analysis")
    if len(nonoverlap_rows)!=len(second_set-first_set):
        raise AssertionError("duplicate or discarded source seeds")

    def cell_counts(rows: list[dict]) -> dict[str,int]:
        return {arm:sum(row[arm] for row in rows) for arm in ARMS}

    def patterns(rows: list[dict]) -> dict[str,int]:
        return dict(sorted(Counter(
            "".join("1" if row[a] else "0" for a in ARMS)
            for row in rows
        ).items()))

    # Freeze the *observed* claims as change detection, not as a prospective
    # p-value or a claim that the source episodes were random IID draws.
    if len(overlapping)!=24 or len(nonoverlap_rows)!=76:
        raise ValueError("cross-cohort source-seed overlap differs from observed archive")
    if cell_counts(nonoverlap_rows)!={
        "upstream_baseline":71,
        "converter_only_pr1495":71,
        "controller_only_pr1472":0,
        "combined_pr1495_pr1472":71,
    }:
        raise ValueError("seed-disjoint sensitivity counts differ from original archive")
    if physical["physical_hdf5_cohort_verified"] is not True:
        raise ValueError("holdout original HDF5 materialization proof is missing")

    report={
        "schema_version":1,
        "status":"independent_cross_cohort_identity_audit_pass",
        "frozen_first_run":FIRST_RUN,
        "frozen_corrected_holdout_run":HELDOUT_RUN,
        "first_original_source_episode_indices":[0,99],
        "holdout_original_source_episode_indices":[100,199],
        "original_source_episodes_disjoint":True,
        "source_seed_sets_disjoint":not bool(overlapping),
        "duplicated_source_seeds_between_cohorts":len(overlapping),
        "unique_source_seeds_across_200_source_episodes":len(first_set|second_set),
        "first_100_conversion_success":cell_counts(first["source_seed_matrix"]),
        "heldout_100_conversion_success":cell_counts(holdout["source_seed_matrix"]),
        "seed_disjoint_holdout_sensitivity":{
            "selection_rule":"Keep a holdout row iff its original source_seed was absent from first 100, independent of replay outcome",
            "analysis_is_post_hoc":True,
            "source_episode_count":len(nonoverlap_rows),
            "conversion_success":cell_counts(nonoverlap_rows),
            "four_bit_patterns":patterns(nonoverlap_rows),
        },
        "physical_hdf5_source_provenance_audited":True,
        "physical_source_binding_by_arm":physical["physical_source_identity_sha256_by_arm"],
        "claim_boundary":(
            "Corrected independent-source-episode holdout and post-hoc seed-disjoint sensitivity; "
            "not 200 statistically independent seed draws, independent external researcher "
            "reproduction, learned-policy task-success evidence, or maintainer adoption."
        ),
    }
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--first",type=Path,required=True)
    parser.add_argument("--holdout",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=audit(args.first,args.holdout)
    content=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(content,encoding="utf-8")
    print(content)


if __name__=="__main__":
    main()
