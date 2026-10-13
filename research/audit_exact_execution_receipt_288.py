"""Independent original-artifact audit of 288 finite execution receipts.

This program does NOT import the policy's graph building, coloring or Bayesian
functions. It reproduces the exact registered controller anchor/quantized
observation relation from output steps, checks all report cells, verifies
minimum colors by a separate decision SAT-style backtracker, and compares
cross-OS outputs. Independent executable verification != outside lab review.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess


FROZEN="b0acaad21cae056f609b7614ed6f0a37a432c22c"
PLAN=Path("research/EXECUTION_RECEIPT_FINITE_PREREG_20261013.json")
PARENT_RUN=38362714720


def k_colorable(adj,k):
    """Independent satisfiability backtracking, not DSATUR minimizing search."""
    n=len(adj)
    order=sorted(range(n),key=lambda v:(-len(adj[v]),v))
    assign=[-1]*n
    def recurse(i,used):
        if i==n:
            return True
        v=order[i]
        for c in range(min(k,used+1)):
            if any(assign[u]==c for u in adj[v]):
                continue
            assign[v]=c
            if recurse(i+1,max(used,c+1)):
                return True
            assign[v]=-1
        return False
    return recurse(0,0)


def expected_case(row):
    count=row["history_bits"]
    steps=row["controller_steps_scaled_x20"]
    n=2**count
    q=[16,28,42][row["quantization_index"]]
    e=Fraction(q*[0,2][row["noise_index"]],25)
    anchors=[]
    support=[]
    for h in range(n):
        a=sum(steps[j]*((h>>j)&1) for j in range(count))
        anchors.append(a)
        support.append(set(range(
            math.floor((Fraction(a)-e)/q),
            math.floor((Fraction(a)+e)/q)+1
        )))
    adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if anchors[i]!=anchors[j] and support[i] & support[j]:
                adj[i].add(j)
                adj[j].add(i)
    k=row["minimum_distinct_tags"]
    if k<1 or k>n or not k_colorable(adj,k) or (
        k>1 and k_colorable(adj,k-1)
    ):
        raise AssertionError("Claimed chromatic minimum is incorrect")
    bits=int(math.ceil(math.log2(k))) if k>1 else 0
    if (row["exact_minimum_receipt_bits"]!=bits
            or row["saved_bits"]!=count-bits
            or row["full_ack_bits"]!=count
            or row["number_of_conflicts"]!=sum(map(len,adj))//2):
        raise AssertionError("Source graph bits or conflict count inconsistent")
    masses=defaultdict(lambda:defaultdict(Fraction))
    for h, a in enumerate(anchors):
        for z in support[h]:
            masses[z][a]+=Fraction(1,n*len(support[h]))
    bayes=float(sum((max(hist.values()) for hist in masses.values()),
                    Fraction(0)))
    if abs(bayes-row["sensor_only_bayes_anchor_accuracy"])>1e-12:
        raise AssertionError("Bayes optimal no receipt evidence incorrect")
    if abs(row["minimum_receipt_bayes_anchor_accuracy"]-1)>1e-12:
        raise AssertionError("Zero-error decision source violated")
    return True


def audit(folder):
    digest=subprocess.check_output(["git","hash-object",str(PLAN)],
                                   text=True).strip()
    if digest!=FROZEN:
        raise AssertionError("Original preregistered task parameters changed")
    spec=json.loads(PLAN.read_text(encoding="utf-8"))
    outputs={}
    for os in ["ubuntu-latest","windows-latest","macos-latest"]:
        p=(folder/f"full-288-execution-receipt-controller-results-{os}"/
           "exact_receipt_288_controller_cases.json")
        raw=p.read_bytes()
        item=json.loads(raw.decode("utf-8"))
        if (item["registered_original_protocol_blob"]!=FROZEN
            or item["original_finite_controller_cases"]!=288
            or len(item["all_cases"])!=288):
            raise AssertionError(f"OS result not complete: {os}")
        outputs[os]=(hashlib.sha256(raw).hexdigest(),item)
    if len({a[0] for a in outputs.values()})!=1:
        raise AssertionError("Unstable 288-case cross-OS original artifacts")
    output=outputs["ubuntu-latest"][1]
    rows=output["all_cases"]
    keys={(r["morphology"],r["history_bits"],r["seed"],
           r["quantization_index"],r["noise_index"]) for r in rows}
    required=set(product(range(2),spec["fixed_environments"]["ack_history_lengths"],
                         spec["fixed_environments"]["seed_ids"],range(3),range(2)))
    if len(keys)!=288 or keys!=required:
        raise AssertionError("Missing/duplicated predeclared environments")
    for row in rows:
        expected_case(row)
    good=sum(row["saved_bits"] / row["full_ack_bits"]>=.25 for row in rows)
    if (good!=output["cases_with_at_least_25pct_receipt_bit_saving"]
        or output["original_preregistered_gate_passed"] != (good>=144)
        or not output["zero_error_protocol_all_cases"]):
        raise AssertionError("Primary registered gate vs observed data disagrees")
    return {
        "schema":"independent_exact_finite_controller_receipt_audit_v1",
        "original_source_workflow_run":PARENT_RUN,
        "original_controller_conditions":288,
        "recomputed_original_cases":len(rows),
        "original_OS_workers_all_identical":True,
        "sha256_of_original_288_case_result":outputs["ubuntu-latest"][0],
        "exhaustively_certified_color_minimum_288_of_288":True,
        "zero_ambiguity_decision_all_original_cases":True,
        "at_least_25pct_saving_cases":good,
        "precommitted_144_case_gate_passed":good>=144,
        "morphology_a_savings_cases":sum(
            row["morphology"]==0 and row["saved_bits"]/row["full_ack_bits"]>=.25
            for row in rows
        ),
        "morphology_b_savings_cases":sum(
            row["morphology"]==1 and row["saved_bits"]/row["full_ack_bits"]>=.25
            for row in rows
        ),
        "graph_coding_is_existing_information_theory":True,
        "simulation_is_idealized_not_native_PhysX":True,
        "external_peer_recognition_not_established":True,
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--originals",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    a=audit(args.originals)
    args.out.write_text(json.dumps(a,indent=2,sort_keys=True)+"\n")
    print("INDEPENDENT_RECEIPT_288_AUDIT",json.dumps(a,sort_keys=True),flush=True)
