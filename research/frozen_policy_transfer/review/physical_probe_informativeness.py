"""Predeclared physical information-gap diagnostic for zero/nonzero ACK probes.

PhysX RUN REQUIRED: Reads each of the four original new-test JSON shards.
The observed Euclidean public-pose response gap between known REAL applied
and held experiment worlds is calculated for both matched probes and seeds.
It does not compare unknown-counterfactual responses within ONE actual
robot execution, and requires both simulator truths to be experimentally
stepped. A known truth is used ONLY by this OUTCOME/ANALYSIS program.

The algebraic common-input null is conditional: if
y_h=x+alpha*(M_h+u-x)+e with identical alpha independent of
history/probe and identical residual sets, then the noise-free
between-history mean gap is alpha*(M_applied-M_held), not a function of u.
This is elementary cancellation, NOT a new theorem or collision proof.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean

ROBOTS={"panda":660001,"xarm6_robotiq":670001}
PROBES=("zero","nonzero_x")
TRUTHS=("applied","held")


def original_source_gap_report(source:Path)->dict:
    rows={}
    for robot,start in ROBOTS.items():
        for chunk in (0,1):
            path=source/f"native_two_probes_{robot}_chunk{chunk}_original16.json"
            raw=json.loads(path.read_text(encoding="utf-8"))
            ids=list(range(start+4*chunk,start+4*chunk+4))
            if (raw.get("schema")!="zero_nonzero_common_probe_cross_robot_fresh16_truth_probes_v1"
                or raw.get("robot")!=robot or raw.get("original_seed_register")!=ids):
                raise ValueError("Original physical task seed split has changed")
            for r in raw["rows"]:
                for trial in r["original_two_physically_stepped_probe_worlds"]:
                    key=(robot,r["seed"],r["actual_execution_truth_score_only"],
                         trial["known_delivered_native_probe_id"])
                    if key in rows:
                        raise ValueError("Duplicated actual physical truth/probe world")
                    if not (trial.get("real_physx_cpu") is True
                        and trial.get("robot")==robot and trial.get("seed")==r["seed"]
                        and trial.get("hidden_physical_truth_posthoc_only")==key[2]
                        and trial.get("private_target_reads_before_classification")==0):
                        raise ValueError("Physics physical-probe/truth identity corrupted")
                    delta=trial["delta_public_xyz"]
                    if (len(delta)!=3 or not all(math.isfinite(x) for x in delta)):
                        raise ValueError("Nonfinite native achieved XYZ response")
                    rows[key]=delta
    if len(rows)!=64:
        raise ValueError("64 actual source physical trial worlds required")
    scores={}
    contrasts=[]
    for robot,start in ROBOTS.items():
        diffs={p:[] for p in PROBES}
        for seed in range(start,start+8):
            one={}
            for probe in PROBES:
                a=rows[(robot,seed,"applied",probe)]
                h=rows[(robot,seed,"held",probe)]
                one[probe]=math.dist(a,h)
                diffs[probe].append(one[probe])
            contrasts.append({
                "robot":robot,"seed":seed,
                "zero_public_histories_separation_m":one["zero"],
                "nonzero_public_histories_separation_m":one["nonzero_x"],
                "nonzero_minus_zero_m":one["nonzero_x"]-one["zero"],
            })
        scores[robot]={
            name:{"mean_between_truth_separation_m":mean(v),
                  "min_between_truth_separation_m":min(v),
                  "max_between_truth_separation_m":max(v)}
            for name,v in diffs.items()
        }
    changes=[r["nonzero_minus_zero_m"] for r in contrasts]
    return {
        "schema":"physical_probe_gap_posthoc_of_source_frozen_new64_real_physx_v1",
        "physical_worlds":64,"independent_reset_seeds":16,
        "two_distinct_robot_bodies":list(ROBOTS),
        "per_robot_public_xyz_truth_gap":scores,
        "paired_nonzero_gap_increase_count":sum(d>1e-6 for d in changes),
        "paired_nonzero_gap_decrease_count":sum(d<-1e-6 for d in changes),
        "paired_negligible_within_1um_count":sum(abs(d)<=1e-6 for d in changes),
        "observed_mean_gap_delta_m":mean(changes),
        "all_original_seed_probes":contrasts,
        "scientific_limits":[
            "Original task/seed/probe outcome is checked by the separate original full-denominator audit.",
            "This is a post-run source-derived diagnostic of a predeclared response-gap measure, not an additional experiment.",
            "A fixed nonzero probe has different physical actuation energy and may alter contacts; equal step counts only.",
            "Paired source outcomes per one robot seed are correlated across truths/probes; not 64 independent policies.",
            "No optimizer-selected active probe or independently attested deterministic response law was executed.",
            "Different mean gaps do not themselves prove more accepted correct history labels or safer task performance.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    v=p.parse_args()
    d=original_source_gap_report(v.input_dir)
    v.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("TWO_ROBOT_REAL_PHYSX_PUBLIC_PROBE_GAP",json.dumps({
        "per_robot":d["per_robot_public_xyz_truth_gap"],
        "gain":d["paired_nonzero_gap_increase_count"],
        "loss":d["paired_nonzero_gap_decrease_count"],
        "near_equal":d["paired_negligible_within_1um_count"],
        "worlds":d["physical_worlds"],
    },sort_keys=True))


if __name__=="__main__":
    main()
