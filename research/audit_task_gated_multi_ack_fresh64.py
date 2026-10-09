"""Reconstruct precommitted task-gated 64-state policy from actual native PhysX evidence.

Source strictness: all EIGHT true original simulation artifact directories,
each original SHA256SUMS manifest and native source JSON, plus task-gated
whole trajectory selected BEFORE reset. No per-step hybrid splicing.
This is author-run confirmation, not external independent experiment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from collections import Counter
from itertools import product
from pathlib import Path
from research.run_task_gated_multi_ack_fresh64 import (
    START,TASKS,ARMS,SELECTIVE,FIXED,ZERO,ROUTE,PROTOCOL,ORIGINAL_SHA,
    accepted,summarize
)

RUN_ID=37904539256
PRECOMMIT_PROTOCOL_BLOB="b4dbd98d73d2a22d9960c5b510e09f3927d63c0d"

def require(ok,msg):
    if not ok:raise ValueError(msg)

def sha(b):return hashlib.sha256(b).hexdigest()

def exact_two_sided(wins,losses):
    n=wins+losses
    return min(1.0,2*sum(math.comb(n,k) for k in range(min(wins,losses)+1))/2**n) if n else 1.0

def get_shard(root,task,chunk):
    dirname=f"taskgated-{task}-{chunk}-{RUN_ID}"
    directory=root/dirname
    require(directory.is_dir(),"Original PhysX shard absent: "+dirname)
    manifest=(directory/"SHA256SUMS").read_text("utf-8").splitlines()
    require(len(manifest)>=7,"Original runner metadata and native outcomes absent")
    names=set()
    for line in manifest:
        fields=line.split()
        require(len(fields)==2 and len(fields[0])==64,"Malformed original physical artifact digest")
        checksum,name=fields
        require(name not in names and "/" not in name and "\\" not in name
                and name not in (".",".."),"Duplicate or untrusted native artifact path")
        names.add(name)
        require(sha((directory/name).read_bytes())==checksum,
                "Original physical source artifact SHA-256 mismatch for "+name)
    for name,expected in {
        "original_controller_blob.txt":ORIGINAL_SHA["research/frozen_ppo_compound_ack_multi_belief.py"],
        "original_certifier_blob.txt":ORIGINAL_SHA["research/multi_ack_se3_bounded.py"],
        "protocol_blob.txt":PRECOMMIT_PROTOCOL_BLOB,
    }.items():
        require((directory/name).read_text("utf-8").strip()==expected,
                "Retrospective rule/source modification is prohibited: "+name)
    summary=json.loads((directory/"summary.json").read_text("utf-8"))
    original_name=f"task_gated_{task}_chunk{chunk}_original8.json"
    require(original_name in names,"Original eight native PhysX worlds not retained")
    original_bytes=(directory/original_name).read_bytes()
    require(summary["original_physx_raw_sha256"]==sha(original_bytes),
            "Native task source and routed output fingerprint disagree")
    original=json.loads(original_bytes)
    measured=summarize(original,task,chunk,accepted(task,chunk))
    for k in ("precommitted_task_route","source_full_original_native_success_counts",
              "source_full_original_true_decision_read_counts",
              "physical_after_dispatch_checks",
              "physically_masked_certificates_not_counted",
              "routed_policy_complete_native_successes",
              "routed_policy_true_privileged_reads",
              "all_original_eight_source_state_outcomes"):
        require(summary.get(k)==measured[k],"Reported route evidence not faithful to original PhysX: "+k)
    require(summary.get("source_git_blobs")==ORIGINAL_SHA
            and summary.get("frozen_preoutcome_task_rule")==ROUTE
            and summary.get("frozen_protocol")==PROTOCOL,
            "Original full-trajectory pre-outcome rule not source frozen")
    return {
        "task":task,"chunk":chunk,"artifact":dirname,
        "source_native_json_sha256":sha(original_bytes),
        "n_states":8,"routed_success":summary["routed_policy_complete_native_successes"],
        "routed_privileged_reads":summary["routed_policy_true_privileged_reads"],
        "physical_setpoint_audits":summary["physical_after_dispatch_checks"],
        "masked_not_physically_dispatched":summary["physically_masked_certificates_not_counted"],
        "rows":summary["all_original_eight_source_state_outcomes"],
    }

def audit(root):
    shards=[get_shard(root,task,chunk) for task,chunk in product(TASKS,range(4))]
    rows=[r for shard in shards for r in shard["rows"]]
    require(len(rows)==64 and len({(r["task"],r["seed"]) for r in rows})==64,
            "Distinct reset-state denominator is not 64")
    def group(task):
        subset=[x for x in rows if task is None or x["task"]==task]
        stats={
            "task_conditioned_route_success":sum(x["routed_success"] for x in subset),
            "task_conditioned_route_private_reads":sum(x["routed_privileged_reads"] for x in subset),
            "fixed_t4_success":sum(x["fixed_actual_native_success"] for x in subset),
            "fixed_t4_private_reads":sum(x["fixed_actual_privileged_reads"] for x in subset),
            "selective_success":sum(x["selective_actual_native_success"] for x in subset),
            "selective_private_reads":sum(x["selective_actual_privileged_reads"] for x in subset),
            "never_query_success":sum(x["zero_query_actual_native_success"] for x in subset),
            "n_distinct_source_states":len(subset)
        }
        c=Counter((r["routed_success"],r["fixed_actual_native_success"]) for r in subset)
        stats["paired_task_gated_vs_fixed"]={
            "both_success":c[(1,1)],"task_gated_only":c[(1,0)],
            "fixed_only":c[(0,1)],"both_failed":c[(0,0)],
            "exploratory_exact_two_sided_sign_p":exact_two_sided(c[(1,0)],c[(0,1)])
        }
        return stats
    return {
        "original_run_id":RUN_ID,
        "nature":"Contributor-run prospectively frozen, seven actual ManiSkill PhysX complete trajectories per reset seed",
        "n_distinct_source_states":64,
        "n_actual_native_matched_controller_episodes":448,
        "model_checkpoints":2,
        "router":"PullCube known task => selective certificate-triggered read; StackCube known task => fixed t4 read; no test outcome routing",
        "physical_after_dispatch_checks":sum(s["physical_setpoint_audits"] for s in shards),
        "fault_masked_tries_not_counted_as_dispatched":sum(s["masked_not_physically_dispatched"] for s in shards),
        "task_conditioned_route_is_whole_actually_executed_physx_trajectory":True,
        "all_8_original_shard_fingerprints":[{
            k:s[k] for k in ("task","chunk","artifact","source_native_json_sha256")
        } for s in shards],
        "overall":group(None),
        "tasks":{k:group(k) for k in TASKS},
        "full_64_original_reset_states":rows,
        "limitations":["Two tasks and two released pretrained PPOs on one Panda controller; task-label specialization, not a task-general intelligent router",
                       "Rule was motivated by PRIOR data, but these 64 seeds are the prospective unseen test",
                       "No exact active sensor information-budget fairness beyond measured resource/outcome frontier",
                       "A success tie across 64 does not establish formal noninferiority without an a priori powered margin",
                       "Two native simulated target holds rather than actual network packet-loss, not real hardware safety",
                       "This author-run source audit cannot itself establish outside-lab independent validation"],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifacts",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    out=audit(args.artifacts)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("TASK_ROUTER_ORIGINAL64_AUDIT",json.dumps({
       "states":out["n_distinct_source_states"],
       "route_success":out["overall"]["task_conditioned_route_success"],
       "route_reads":out["overall"]["task_conditioned_route_private_reads"],
       "fixed_success":out["overall"]["fixed_t4_success"],
       "fixed_reads":out["overall"]["fixed_t4_private_reads"],
       "selective_success":out["overall"]["selective_success"],
       "selective_reads":out["overall"]["selective_private_reads"],
       "after_dispatch_checks":out["physical_after_dispatch_checks"],
       "masked":out["fault_masked_tries_not_counted_as_dispatched"],
       "paired":out["overall"]["paired_task_gated_vs_fixed"],
    },sort_keys=True))

if __name__=="__main__":main()
