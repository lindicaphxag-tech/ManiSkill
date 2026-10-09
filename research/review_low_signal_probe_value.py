"""Reviewer-only paired analysis of ORIGINAL low-signal PhysX source.

No physics is run here. Accept only a complete, original, immutable six-shard
archive and recompute every label from calibration physical rows. Unit of
statistical resampling/sign flips: independent robot/reset ID, NOT its six
correlated ACK-truth/probe interventions.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

from research.low_signal_probe_selection_physx import (
    PROBES, ROBOTS, TEST, audit_root
)

SOURCE=Path("research/frozen_policy_transfer/evidence/low_signal_first192_20261010")
NAMES={f"low_signal_calibration_{r}.json" for r in ROBOTS}
NAMES|={f"low_signal_holdout_{r}_chunk{i}.json" for r in ROBOTS for i in (0,1)}

def _clopper_zero(n):
    if n<0:raise ValueError("Negative admitting reset count")
    return 1.0 if n==0 else 1.0-.05**(1/n)

def _signflip_two_sided(values):
    """Exact grouped random sign-flip test; exploratory, not preregistration."""
    counts=Counter({0:1})
    for v in values:
        nxt=Counter()
        for total,m in counts.items():
            nxt[total+v]+=m
            nxt[total-v]+=m
        counts=nxt
    observed=sum(values)
    return sum(m for value,m in counts.items() if abs(value)>=abs(observed))/(2**len(values))

def _stratified_bootstrap(grouped,seed=20261010,draws=20000):
    rng=random.Random(seed)
    out=[]
    for _ in range(draws):
        sample=0
        for robot in ROBOTS:
            values=grouped[robot]
            for _ in range(len(values)):
                sample+=values[rng.randrange(len(values))]
        out.append(sample)
    out.sort()
    return [out[int(draws*.025)],out[int(draws*.975)]]

def review(folder:Path):
    orig=audit_root(folder)
    if orig["original_physics_worlds_calibration"]!=96 or orig["original_physics_worlds_heldout"]!=96:
        raise ValueError("Required all 192 physical outcomes")
    sha={}
    for name in sorted(NAMES):
        p=folder/name
        if not p.is_file():raise ValueError("Missing original source file "+name)
        sha[name]=hashlib.sha256(p.read_bytes()).hexdigest()
    rows={}
    by_robot={}
    deltas=defaultdict(list)
    for robot in ROBOTS:
        cal=json.loads((folder/f"low_signal_calibration_{robot}.json").read_bytes())
        selected=cal["selected_nonzero_probe"]
        if selected not in ("x","y"):raise ValueError("Not a physically executed nonzero probe")
        cases={}
        for chunk in (0,1):
            p=folder/f"low_signal_holdout_{robot}_chunk{chunk}.json"
            source=json.loads(p.read_bytes())
            for row in source["original_rows"]:
                key=(row["seed"],row["hidden_physical_truth_posthoc_only"],row["known_delivered_native_probe_id"])
                if key in cases:raise ValueError("Repeated physical outcome")
                cases[key]=row
        for seed in range(TEST[robot],TEST[robot]+8):
            group=[r for (s,_,_),r in cases.items() if s==seed]
            if len(group)!=6:raise ValueError("Loss of an original six-world independent reset")
            before=group[0]["public_xyz_after_t1"]
            if any(math.dist(x["public_xyz_after_t1"],before)>5e-5 for x in group):
                raise ValueError("Prior heldout same-seed initial physical prefix invalid")
            for p in PROBES:
                ar=cases[(seed,"applied",p)]
                hr=cases[(seed,"held",p)]
                deltas[(robot,p)].append(math.dist(ar["delta_public_xyz"],hr["delta_public_xyz"]))
        scores={}
        for probe in PROBES:
            cc=[r for (s,t,p),r in cases.items() if p==probe]
            allowed={i["seed"] for i in cc if i["decision"]["label"] is not None}
            wrong={i["seed"] for i in cc if i["wrong_confident_history"] is True}
            scores[probe]={
                "physical_worlds":len(cc),
                "independent_reset_clusters":8,
                "correct":sum(i["decision"]["label"]==i["hidden_physical_truth_posthoc_only"] for i in cc),
                "confident_wrong":sum(i["wrong_confident_history"] is True for i in cc),
                "abstain":sum(i["decision"]["label"] is None for i in cc),
                "native_target_corrections_within_1e4m":sum(i["target_restored_below_1e4_m"] for i in cc),
                "admitting_reset_clusters":len(allowed),
                "wrong_reset_clusters":len(wrong),
                "one_sided_95pct_error_upper_if_selected_resets_iid":
                    _clopper_zero(len(allowed)) if not wrong else None,
                "mean_applied_versus_held_public_motion_distance_m":
                    sum(deltas[(robot,probe)])/len(deltas[(robot,probe)]),
                "nominal_native6_probe_norm":math.sqrt(sum(x*x for x in PROBES[probe]))
            }
        per_robot={}
        for cmp in ("zero","x","y"):
            values=[]
            wrongs=[]
            for seed in range(TEST[robot],TEST[robot]+8):
                def gain(p):
                    rr=[cases[(seed,t,p)] for t in ("applied","held")]
                    return sum(v["decision"]["label"]==t for t,v in zip(("applied","held"),rr))
                def wrong(p):
                    return sum(cases[(seed,t,p)]["wrong_confident_history"] is True for t in ("applied","held"))
                values.append(gain(selected)-gain(cmp))
                wrongs.append(wrong(selected)-wrong(cmp))
            per_robot[f"selected_vs_{cmp}"]={
                "correct_history_delta_by_independent_seed":values,
                "wrong_confident_delta_by_independent_seed":wrongs,
                "observed_correct_history_delta":sum(values),
                "observed_wrong_confident_delta":sum(wrongs)
            }
            if cmp=="zero":
                deltas[("correct",robot)].extend(values)
        by_robot[robot]={
            "calibration_selected_nonzero_probe":selected,
            "calibration_margin_m":cal["old_only_selection_scores"][selected]["worst_response_ball_margin_m"],
            "diagnostic_empirical_ball_separation_only":True,
            "heldout_by_actual_probe":scores,
            "paired":per_robot,
        }
    paired=[v for robot in ROBOTS for v in deltas[("correct",robot)]]
    return {
        "audit_status":"PASS_AUTHOR_OPERATED_192_ORIGINAL_NATIVE_PHYSX_WORLDS",
        "original_source_sha256":sha,
        "heldout_distinct_independent_reset_seeds":16,
        "all_heldout_physical_truth_probe_worlds":96,
        "calibration_worlds":96,
        "calibration_probe_selection_reuses_the_same_empirical_fit":True,
        "no_valid_distribution_free_95pct_two_history_safety_certificate_at_eight_calibration_resets":True,
        "by_robot":by_robot,
        "pooled_selected_vs_zero": {
            "correct_history_delta_actual":sum(paired),
            "independent_reset_deltas":paired,
            "whole_reset_exact_signflip_p_exploratory":_signflip_two_sided(paired),
            "robot_stratified_bootstrap_correct_history_delta_95pct_exploratory":
                _stratified_bootstrap({r:deltas[("correct",r)] for r in ROBOTS}),
            "zero_probe_cost_equal_to_nonzero":False,
            "task_success_tested":False,
            "robot_safety_certified":False,
            "third_party_replicated":False
        },
        "source_total_crosscheck":orig
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=SOURCE)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=review(a.source)
    a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("REVIEWER_LOW_SIGNAL_FIRST192",json.dumps({
        "by_robot":d["by_robot"],
        "pooled":d["pooled_selected_vs_zero"]
    },sort_keys=True))

if __name__=="__main__":
    main()
