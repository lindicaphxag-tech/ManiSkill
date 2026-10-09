"""Authentic source-locked aggregate of ALL 64 unseen native PhysX Multi-ACK states.

Rebuild exclusively from original GitHub Action run #37900209486 and its EIGHT
raw shard artifacts (no simulations run here). This script refuses partial
denominators, invalid source/checkpoint/protocol, modified original bytes,
false setpoint authorizations and any excluded official task failures.

No real hardware or outside-laboratory replication claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from itertools import product
from math import comb
from pathlib import Path

RUN_ID=37900209486
TASKS=("pull_cube","stack_cube")
START={"pull_cube":420001,"stack_cube":430001}
ARM=("source_no_fault","fault_oracle_private_target",
    "fault_optimistic_unverified_ack","fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query")
SEL=ARM[5];FIXED=ARM[6];ZERO=ARM[4]
EXPECTED_SOURCE={
"research/frozen_ppo_compound_ack_multi_belief.py":"99836af14205fe3e95e52a2e0d68237c7c8a9045",
"research/multi_ack_se3_bounded.py":"36707a177549104ba5b4bd9bcebc76518f0d2840",
"research/frozen_ppo_ack_bounded_query.py":"1dc653cdc44e422c8340475ad00f828b3a41eb4f",
"research/two_history_se3_robust.py":"bb5fd155b7291fb127f94138fca321201c8271c3",
}
CHECKPOINT_SHA={
"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
"stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}
PROTOCOL="research/COMPOUND_ACK_NEW64_PROSPECTIVE_V1.md"

def require(cond,why):
    if not cond:raise ValueError(why)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def exact_sign_test(b,c):
    n=b+c
    if not n:return 1.0
    return min(1.0,2.0*sum(comb(n,k) for k in range(min(b,c)+1))/2**n)

def verify_manifest(dir):
    m=dir/"SHA256SUMS"
    raw=m.read_text("utf-8").splitlines()
    require(len(raw)>=6,"Missing original immutable raw file hash manifest")
    seen=set()
    for ln in raw:
        fields=ln.split()
        require(len(fields)==2 and len(fields[0])==64,"Malformed original SHA256 manifest")
        digest,name=fields
        require(name not in seen and not name.startswith("/") and ".." not in Path(name).parts,
                "Duplicate/path traversal evidence manifest entry")
        seen.add(name)
        require(sha((dir/name).read_bytes())==digest,
                "Checksum mismatch for original named source artifact "+name)
    require("summary.json" in seen,"Missing original per-shard summary from manifest")
    return seen

def read_chunk(root,task,chunk):
    name=f"multiack-prospective-{task}-chunk{chunk}-{RUN_ID}"
    directory=root/name
    require(directory.is_dir(),"Missing true native PhysX original artifact "+name)
    manifest_names=verify_manifest(directory)
    info=json.loads((directory/"summary.json").read_text("utf-8"))
    original_name=f"compound_new64_{task}_chunk{chunk}_original8.json"
    require(original_name in manifest_names,
            "Original eight native episodes missing from SHA manifest")
    original=(directory/original_name).read_bytes()
    require(sha(original)==info.get("original_json_sha256"),
            "Mismatch between immutable original source and summary")
    record=json.loads(original)
    seeds=list(range(START[task]+8*chunk,START[task]+8*chunk+8))
    require(info.get("task")==task and info.get("chunk")==chunk
            and info.get("seeds")==seeds and record.get("original_seed_population")==seeds,
            "Changed prospective seed/task shard")
    require(info.get("source_blobs")==EXPECTED_SOURCE,
            "Unfrozen method or certifier source")
    require(info.get("original_released_checkpoint_sha256")==CHECKPOINT_SHA[task],
            "Published frozen PPO checkpoint changed")
    require(info.get("protocol")==PROTOCOL
            and info.get("no_source_training") is True
            and record.get("preoutcome_protocol")==PROTOCOL,
            "No valid prospective source freeze")
    require(record.get("schema")=="compound_two_unknown_ack_multihistory_physx_v1"
            and record.get("task")==("PullCube-v1" if task=="pull_cube" else "StackCube-v1")
            and record.get("frozen_model_retrained") is False
            and record.get("real_physx_simulator") is True
            and record.get("fault_is_native_target_hold_not_network_loss") is True
            and record.get("two_consecutive_unknown_ack_target_hold_steps")==[2,3]
            and record.get("all_seven_actual_control_arms")==list(ARM),
            "Invalid genuine native double-ACK original controller experiment")
    episodes=record.get("episodes")
    require(isinstance(episodes,list) and len(episodes)==8
            and [r.get("seed") for r in episodes]==seeds,
            "Not all original eight reset states retained")
    score=Counter();reads=Counter();physical=masked=0;maxbelief=0;case_rows=[]
    for row in episodes:
        flags=row.get("success_once")
        require(type(flags) is dict and set(flags)==set(ARM)
                and all(type(flags[n]) is bool for n in ARM),
                "Invalid original ManiSkill task success flags")
        q=row.get("privileged_target_readback_decision_count",{})
        require(q.get(ARM[1])==-1,"Unrestricted private target oracle falsely labelled cost-free")
        require(all(type(q.get(n)) is int and q[n] in (0,1) for n in ARM if n!=ARM[1]),
                "Invalid decision privilege readcount")
        require(all(q[n]==0 for n in (ARM[0],ARM[2],ARM[3],ARM[4])),
                "Private information leaked into zero-query arm")
        for n in ARM:
            score[n]+=int(flags[n])
            if n!=ARM[1]:
                reads[n]+=q[n]
        beliefs=row.get("max_belief_width",{})
        require(all(type(beliefs.get(n)) is int and beliefs[n]>=1 and beliefs[n]<=16
                    for n in (ARM[3],ZERO,SEL,FIXED)),
                "Missing full multi-history belief evidence")
        maxbelief=max(maxbelief,max(beliefs.values()))
        require(all(beliefs[n]>=4 for n in (ZERO,SEL,FIXED)),
                "At least one original world did not reach four possible states")
        faults=row.get("faults",{})
        for n in ARM[1:]:
            fs=faults.get(n,[])
            steps=[w["step"] for w in fs]
            require(steps in ([2],[2,3]),"Invalid original fault injection times")
            if n!=ARM[3]:
                require(steps==[2,3],"Missing second actual arm target hold")
        masks=row.get("certified_action_masked_by_injected_fault",{})
        audits=row.get("robust_native_target_bound_checks",{})
        for n,arr in masks.items():
            require(n in (ZERO,SEL,FIXED,ARM[3]),"Invalid masked authorization controller world")
            for entry in arr:
                masked+=1
                require(entry["step"] in (2,3)
                        and entry["native_action_did_not_execute"] is True
                        and entry["postdispatch_certificate_check_not_applicable"] is True
                        and entry["claimed_physical_setpoint_certificate"] is False,
                        "Attempted but held command disguised as physically verified")
                require(all(v["step"]!=entry["step"] for v in audits.get(n,[])),
                        "Fault-masked command incorrectly certified after dispatch")
        for n,arr in audits.items():
            require(n in (ZERO,SEL,FIXED,ARM[3]),"Invalid afterdispatch audit arm")
            for z in arr:
                physical+=1
                require(z["step"] not in (2,3)
                        and z["only_audit_after_physical_dispatch"] is True
                        and z["position_error_m"]<=z["worst_case_position_limit_m"]+1e-4+1e-10
                        and z["rot_error_rad"]<=z["worst_case_rot_limit_rad"]+1e-4+1e-10,
                        "False real PhysX commanded target certificate after dispatch")
        case_rows.append({
           "task":task,"seed":row["seed"],
           "success":{k:int(flags[k]) for k in ARM},
           "privileged_reads":{k:q[k] for k in ARM if k!=ARM[1]},
           "max_belief_width":beliefs,
        })
    require(dict(score)==record.get("success_counts"),
            "Original summary task-success totals changed")
    require(all(info.get("original_official_success_counts",{}).get(a)==score[a] for a in ARM),
            "Per-shard original source outcomes and printed summary disagree")
    require(all(info.get("privileged_decision_read_counts",{}).get(a)==reads[a] for a in reads),
            "Source private information costs do not reconcile")
    require(info.get("genuine_afterdispatch_certified_setpoint_checks")==physical
            and info.get("masked_commands_not_counted_as_dispatched")==masked,
            "Original physical validation/masked ledgers mismatch")
    return {"task":task,"chunk":chunk,"name":name,
            "original_json_sha256":sha(original),
            "official_task_successes":dict(score),
            "privileged_reads":dict(reads),
            "physical_checks":physical,"masked":masked,
            "max_belief":maxbelief,"episodes":case_rows}

def aggregate(root):
    chunks=[read_chunk(root,t,ch) for t,ch in product(TASKS,range(4))]
    rows=[r for c in chunks for r in c["episodes"]]
    require(len(rows)==64 and len({(r["task"],r["seed"]) for r in rows})==64,
            "64 state source denominator incomplete")
    def condition(group):
        sub=[r for r in rows if group is None or r["task"]==group]
        counts={a:sum(r["success"][a] for r in sub) for a in ARM}
        queries={a:sum(r["privileged_reads"][a] for r in sub) for a in ARM if a!=ARM[1]}
        flags=Counter((r["success"][SEL],r["success"][FIXED]) for r in sub)
        agree={"both_success":flags[(1,1)],
               "selective_only":flags[(1,0)],
               "fixed_only":flags[(0,1)],
               "both_fail":flags[(0,0)]}
        return {"n_states":len(sub),"official_successes":counts,
                "decision_privileged_queries":queries,
                "paired_adaptive_vs_fixed":agree,
                "paired_exact_two_sided_p_exploratory":exact_sign_test(agree["selective_only"],agree["fixed_only"])}
    return {
       "original_run_id":RUN_ID,
       "source_blobs":EXPECTED_SOURCE,
       "n_source_states":64,
       "n_genuine_matched_worlds":448,
       "n_independent_original_frozen_PPOs":2,
       "four_distinct_target_memory_states_exercised":all(
           min(r["max_belief_width"][n] for n in (ZERO,SEL,FIXED))>=4 for r in rows),
       "no_source_retraining":True,
       "original_physical_afterdispatch_checks":sum(x["physical_checks"] for x in chunks),
       "original_fault_masked_attempts_excluded":sum(x["masked"] for x in chunks),
       "evidence_artifact_shards":[{
           k:x[k] for k in ("task","chunk","name","original_json_sha256")}
           for x in chunks],
       "overall":condition(None),
       "by_task":{t:condition(t) for t in TASKS},
       "raw_all_64_original_states":rows,
       "claim_scope":"64 new contributor-operated real ManiSkill PhysX states, one Panda controller family, known exact source and faults",
       "not_claimed":["actual network packet loss","physical robot safety or collision protection",
                      "out-of-distribution multi-robot evidence","outside-lab replication","published original research",
                      "algorithmic superiority without equal-information controls"],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifacts",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    d=aggregate(args.artifacts)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("MULTI_ACK_NEW64_ORIGINAL_SOURCE_AUDIT",json.dumps({
      "states":d["n_source_states"],
      "physical_setpoint_checks":d["original_physical_afterdispatch_checks"],
      "masked_fault_attempts":d["original_fault_masked_attempts_excluded"],
      "four_state_belief_exercised":d["four_distinct_target_memory_states_exercised"],
      "selective_success":d["overall"]["official_successes"][SEL],
      "fixed_success":d["overall"]["official_successes"][FIXED],
      "selective_reads":d["overall"]["decision_privileged_queries"][SEL],
      "fixed_reads":d["overall"]["decision_privileged_queries"][FIXED],
      "paired":d["overall"]["paired_adaptive_vs_fixed"],
    },sort_keys=True))

if __name__=="__main__":main()
