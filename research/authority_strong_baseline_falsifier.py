"""Retrospective SHA-pinned scientific falsifier for 128 PhysX cells.

Explicit independence: 32 reset clusters x 4 correlated ACK truths. This uses
previously recorded official task outcomes, NOT new native physics or a new
randomized experiment; the sign test is exploratory.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path

SOURCE_SHA256="57485114f58101a24c20d2f1155ac96482a7754693878e940a2197215cf142e8"
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
Q="fault_always_single_privileged_query"

def _exact_signflip(xs):
    vals=[x for x in xs if x]
    if len(vals)>22:raise ValueError("Exact enumeration limited to <=22 nonzero clusters")
    if not vals:return 1.
    hit=sum(abs(sum(x*s for x,s in zip(vals,z)))>=abs(sum(vals))
            for z in product((-1,1),repeat=len(vals)))
    return hit/2**len(vals)

def audit(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError("SOURCE DRIFT: frozen original 128-cell SHA256 mismatch")
    j=json.loads(raw);rows=j["all_orig_source_seed_cell_vectors"]
    if len(rows)!=128 or j["actual_genuine_native_controller_worlds"]!=1280:
        raise ValueError("Invalid original denominator")
    expected={(task,seed,truth)
              for task,start in (("pull_cube",3110001),("stack_cube",3120001))
              for seed in range(start,start+16) for truth in range(4)}
    groups=defaultdict(list);strata=defaultdict(list);seen=set()
    for x in rows:
        key=(x["task"],x["seed"],x["truth"])
        if key not in expected or key in seen:raise ValueError("Wrong/duplicate original cell")
        seen.add(key)
        if (set(x["success"])!={A,B,Q} or set(x["reads"])!={A,B,Q}
            or set(x["public_xyz"])!={A,B,Q}):
            raise ValueError("Missing strong same-source comparator")
        if any(type(x["success"][a]) is not bool or type(x["reads"][a]) is not int
               or x["reads"][a] not in (0,1) for a in (A,B,Q)):
            raise ValueError("Malformed genuine per-cell native task/reads")
        if x["public_xyz"][A]!=2 or x["public_xyz"][B]!=2 or x["public_xyz"][Q]!=0:
            raise ValueError("Public observation budget mismatch")
        groups[key[:2]].append(x);strata[(x["task"],x["truth"])].append(x)
    if seen!=expected or len(groups)!=32 or any(len(g)!=4 for g in groups.values()):
        raise ValueError("Full original independent reset/fault matrix missing")
    def summary(records):
        return {a:{"success":sum(x["success"][a] for x in records),
                   "privileged_reads":sum(x["reads"][a] for x in records),
                   "public_xyz":sum(x["public_xyz"][a] for x in records),
                   "wrong_confident":sum(bool(x["wrong"][a]) for x in records)}
                for a in (A,B)}
    full=summary(rows)
    if (full[A]["success"],full[B]["success"],full[A]["privileged_reads"],
        full[B]["privileged_reads"])!=(109,109,94,98):
        raise ValueError("Preexisting original audit totals no longer reproduce")
    if any(x["success"][A]!=x["success"][B] for x in rows):
        raise ValueError("Matched strong task outcomes differ from published originals")
    diffs={f"{t}:{s}":sum(x["reads"][B]-x["reads"][A] for x in rr)
           for (t,s),rr in sorted(groups.items())}
    return {"status":"PASS_OLD_SOURCE_FALSIFIER_NOT_A_NEW_EXPERIMENT",
            "original_physx_worlds":1280,"independent_reset_clusters":32,
            "correlated_ack_cells":128,"strong_benchmark":B,"candidate":A,
            "pooled":full,
            "by_task":{t:summary([x for x in rows if x["task"]==t])
                       for t in ("pull_cube","stack_cube")},
            "by_task_and_actual_truth":{f"{task}:truth{truth}":summary(v)
                                         for (task,truth),v in sorted(strata.items())},
            "per_independent_reset_query_savings":diffs,
            "observed_total_read_savings":sum(diffs.values()),
            "exploratory_two_sided_cluster_signflip_p":_exact_signflip(list(diffs.values())),
            "paired_success_discordances":0,
            "task_success_gain":0,
            "marginal_public_sample_cost_difference":0,
            "top_maintrack_positive_task_gain_established":False,
            "caveat":"Retrospective same-cohort paired analysis, not a preregistered hypothesis test or statistical equivalence."}
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("original_json");args=p.parse_args()
    print(json.dumps(audit(args.original_json),indent=2))
