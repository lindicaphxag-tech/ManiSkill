"""Independent evidence-based cost/risk sensitivity for a FROZEN PhysX audit.

Input: SOURCE_FIRST_128_CLUSTER_RISK.json in original workflow artifact
1280-native-physx-32cluster-statistical-audit-ubuntu-latest-3.11, run
37947358998 (derived from original PhysX run 37944800521).

This script does NOT run PhysX; its output is a post-hoc cost sensitivity
analysis of archived counts, NOT new method evaluation or low-risk proof.

Usage:
 python research/audit_original_cluster_cost_frontier.py --self-test
 python research/audit_original_cluster_cost_frontier.py \
   --source SOURCE_FIRST_128_CLUSTER_RISK.json --output report.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = "b1619a4ca6c99cdc4901d04f47f9d3518e077fb0d39e1da471668448ac9c1690"
ARM = "fault_public_t3_fourhistory_or_t4_query"
CONTROL = "fault_always_single_privileged_query"
OTHER = "fault_same_public_posterior_or_query"


def audit_original(raw: bytes) -> dict:
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source does not match original pinned CI JSON")
    d = json.loads(raw)
    if d["real_task_reset_independent_sample_units"] != 32 or d["correlated_physical_ACK_truth_cells"] != 128:
        raise ValueError("Incorrect reset / true-ACK clustering")
    if d["actual_native_PhysX_controller_worlds"] != 1280:
        raise ValueError("Unmatched physical experiment source")
    s = d["pooled"]["strategy"]
    b, a, o = s[CONTROL], s[ARM], s[OTHER]
    if not a["wrong_clusters"] == 0 or a["accepted_clusters"] != 20:
        raise ValueError("Unexpected source authority labels")
    if any(x["official_successes"] != b["official_successes"] for x in (a,o)):
        raise ValueError("Official outcome mismatch; cannot claim paired success preservation")
    if b["official_successes"] != 104:
        raise ValueError("Unexpected archived outcome count")
    saved = b["true_target_reads"]-a["true_target_reads"]
    extra = a["public_xyz_observation_events"]-b["public_xyz_observation_events"]
    if saved != 25 or extra != 256:
        raise ValueError("Unexpected frozen cost counts")
    task = {}
    for name, data in sorted(d["per_task"].items()):
        x, y = data["strategy"][ARM], data["strategy"][CONTROL]
        if x["original_reset_clusters"] != 16 or x["correlated_truth_cells"] != 64:
            raise ValueError("Each task must have 16 original reset clusters")
        # Zero events CP bound is 1 - alpha**(1/n) for n independent accepted
        # CLUSTERS, not n correlated 4-truth or read/query events.
        cp = 1 - 0.05 ** (1/x["accepted_clusters"])
        if abs(cp-x["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"])>1e-10:
            raise ValueError("Original cluster exact-bound disagreement")
        task[name] = {
            "independent_reset_clusters":16,
            "authorized_reset_clusters":x["accepted_clusters"],
            "wrong_clusters":x["wrong_clusters"],
            "one_sided_95pct_cluster_risk_upper_descriptive":cp,
            "official_successes_of_64":x["official_successes"],
            "fixed_reads":y["true_target_reads"],
            "selective_reads":x["true_target_reads"]
        }
    cp_all = 1-0.05 ** (1/a["accepted_clusters"])
    if abs(cp_all-a["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"])>1e-10:
        raise ValueError("Pooled cluster bound mismatch")
    return {
        "study_scope":"Source-verified posthoc descriptive 32-reset PhysX cluster audit",
        "original_json_sha256":SOURCE_SHA256,
        "physical_worlds":1280,
        "unique_initial_resets":32,
        "correlated_ack_truth_cells":128,
        "same_successes":104,
        "fixed_privileged_reads":b["true_target_reads"],
        "selective_privileged_reads":a["true_target_reads"],
        "read_savings":saved,
        "additional_public_xyz_observation_events":extra,
        "authorized_clusters":a["accepted_clusters"],
        "wrong_authorized_clusters":a["wrong_clusters"],
        "one_sided_95pct_cluster_error_upper_exploratory":cp_all,
        "target_risk_10pct_confirmed":False,
        "per_task":task,
        "normalized_incremental_total_cost_sensitivity":[
            {"public_XYZ_to_privileged_getter_cost_ratio":w,
             "getter_equivalent_cost_saved_before_probe_physics":saved-w*extra}
            for w in (0.,0.025,0.05,0.1,0.2)
        ],
        "break_even_public_XYZ_cost_ratio_ignoring_probe_physics":saved/extra,
        "scientific_limitations":[
            "Public observation events, neutral physical probe steps and latency cannot be assumed free",
            "Four ACK conditions on the same initial state are dependent",
            "Zero wrong authorizations in 20 clusters does not certify <10% selective risk",
            "The cluster estimand is any wrong among four truths given one or more authorized in a reset, not per-event error",
            "All outcomes come from author-operated original PhysX experiments, not third-party replication",
            "No new policy improvement, prospective calibration, statistical noninferiority, or hardware safety is established",
        ]
    }


def self_test():
    # Algebra-only checks, no manufactured PhysX source measurements.
    assert abs((1 - 0.05 ** (1/10)) - 0.2588655508930523) < 1e-10
    assert abs((1 - 0.05 ** (1/20)) - 0.13910834066826525) < 1e-10
    assert 25 - .1 * 256 < 0
    try:
        audit_original(b'{}')
        raise AssertionError("Altered source accepted")
    except ValueError:
        pass
    print("PASS: CP cluster counts, cost break-even, SHA fail-closed")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path)
    p.add_argument("--output",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        self_test()
        return
    if args.source is None or args.output is None:
        p.error("--source and --output required")
    report=audit_original(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
