"""Original, source-pinned cost-sensitivity audit for actual frozen-PPO PhysX.

This is NOT new robotics physics, SmolVLA, independent adoption, non-inferiority,
or robot safety. It accepts only the already independent-source-audited,
historical FIRST 32-reset x four-ACK-truth × 10-controller dataset.

Every outcome/cost comes from the source-recomputed original physical JSON,
not an invented simulation or programmatically regenerated toy task.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / (
    "frozen_policy_transfer/evidence/"
    "strong060_prospective_original128_first_3110001_3120016/"
    "INDEPENDENT_SOURCE_RECOMPUTATION.json"
)
A = "fault_public_t3_fourhistory_or_t4_query"
B = "fault_same_public_posterior_or_query"
C = "fault_always_single_privileged_query"
ARMS = (A, B, C)


def percentile(values, q):
    x = sorted(values)
    return x[int((len(x) - 1)*q)]


def cluster_bootstrap(groups, control, *, draws=20000, seed=20261010):
    """Paired cluster bootstrap, truths correlated within 32 original resets."""
    if len(groups) != 32:
        raise ValueError("Expected 32 unique task/reset clusters")
    diffs = [
        sum(int(r["success"][A])-int(r["success"][control]) for r in rows)
        for rows in groups.values()
    ]
    r = random.Random(seed)
    estimates = []
    for _ in range(draws):
        estimates.append(sum(diffs[r.randrange(len(diffs))] for _ in diffs) /
                         (4*len(diffs)))
    return [percentile(estimates, .025), percentile(estimates, .975)]


def audit(path=SOURCE):
    data = Path(path).read_bytes()
    d = json.loads(data)
    if d["actual_genuine_native_controller_worlds"] != 1280:
        raise AssertionError("Not the original 1280-world frozen PPO source")
    rows = d["all_orig_source_seed_cell_vectors"]
    if len(rows) != 128:
        raise AssertionError("Lost or added a physical task/truth outcome")
    groups = defaultdict(list)
    unique = set()
    by_arm = {a: dict(success=0, reads=0, public_xyz=0, wrong=0) for a in ARMS}
    for x in rows:
        task, seed, truth = x["task"], x["seed"], x["truth"]
        if task not in ("pull_cube","stack_cube") or truth not in (0,1,2,3):
            raise AssertionError("Unknown task or physical ACK truth")
        key = (task,seed,truth)
        if key in unique:
            raise AssertionError("Duplicate original task reset / truth")
        unique.add(key)
        groups[(task,seed)].append(x)
        for a in ARMS:
            z=by_arm[a]
            z["success"] += int(x["success"][a])
            z["reads"] += int(x["reads"][a])
            z["public_xyz"] += int(x["public_xyz"][a])
            z["wrong"] += int(x["wrong"].get(a,False))
    if len(groups)!=32 or any(
        len(v)!=4 or {x["truth"] for x in v}!={0,1,2,3}
        for v in groups.values()
    ):
        raise AssertionError("Must preserve 32 paired reset clusters times four truths")
    for a in ARMS:
        old=d["all_cells"][a]
        now=by_arm[a]
        if (old["success"],old["private_reads"],old["decision_public_xyz_events"],
            old["wrong_confident_authorizations"]) != (
            now["success"],now["reads"],now["public_xyz"],now["wrong"]):
            raise AssertionError("Original source recomputation and new audit disagree")
    expected={A:(109,94,256,0), B:(109,98,256,0), C:(110,128,0,0)}
    for a,(s,q,o,w) in expected.items():
        if (by_arm[a]["success"],by_arm[a]["reads"],by_arm[a]["public_xyz"],
            by_arm[a]["wrong"])!=(s,q,o,w):
            raise AssertionError("Source frozen result changed")
    # Real-world price schedule is NOT known; report a sensitivity boundary.
    # Utility = task successes - lambda_private * private getter reads
    #         - lambda_public * public XYZ acquisitions.
    # U(A)-U(C) = -1 + 34*lambda_private - 256*lambda_public.
    threshold_private_no_public = 1/34
    price_frontier=[]
    for public_price in (0.0,0.001,0.002,0.005,0.01):
        minimum_private_price=(1+256*public_price)/34
        price_frontier.append({
            "public_XYZ_price_success_unit":public_price,
            "minimum_private_read_price_for_A_over_C_success_unit":minimum_private_price,
        })
    # Equal aggregate success A and B, fewer reads A. Since per-case
    # outcomes can differ, this only establishes aggregate counts, not an
    # all-task per-case dominance claim.
    paired={}
    for b in (B,C):
        paired[b]={
            "A_success_minus_control_per_truth_cell":
                (by_arm[A]["success"]-by_arm[b]["success"])/128,
            "paired_32_reset_cluster_bootstrap_95":
                cluster_bootstrap(groups,b),
            "A_only":sum(x["success"][A] and not x["success"][b] for x in rows),
            "control_only":sum(x["success"][b] and not x["success"][A] for x in rows),
        }
    return {
        "analysis_identity":"PPO original 32-reset 128 truth cell resource sensitivity audit",
        "source_sha256":hashlib.sha256(data).hexdigest(),
        "source_genuine_PhysX_worlds":1280,
        "independent_reset_clusters":32,
        "correlated_ACK_truth_cells":128,
        "original_source_counts":by_arm,
        "paired_success":paired,
        "break_even_strict_A_vs_fixed_C":"34*lambda_private > 1 + 256*lambda_public",
        "read_price_threshold_by_public_observation_price":price_frontier,
        "claim_restrictions":[
            "No VLA-controlled robot task; frozen PPO policy only",
            "Author-operated genuine CPU PhysX, not ROS/TCP dropped packets nor physical hardware",
            "0 observed wrong confident approvals does not demonstrate zero population risk",
            "No measured real cost conversion from read, public observation and task success",
            "Observed A=109 and C=110 does not establish task noninferiority",
            "32 reset clusters are independent design units, not 128 task trials or 1280 robots",
            "Price frontier is algebraic sensitivity, NOT measured sensor cost or demonstrated advantage"
        ],
    }


def selftest():
    z=audit()
    assert z["independent_reset_clusters"]==32
    assert abs(z["read_price_threshold_by_public_observation_price"][0][
        "minimum_private_read_price_for_A_over_C_success_unit"]-1/34)<1e-14
    assert z["paired_success"][C]["A_success_minus_control_per_truth_cell"]==-1/128
    return z


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=SOURCE)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.source)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
