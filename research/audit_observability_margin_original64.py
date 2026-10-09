"""Independent source-only re-audit of 64 ORIGINAL physically stepped PhysX states.

This verifier reads eight original shard JSONs from a completed GitHub Actions
run, recomputes paired official outcomes, private reads and authority errors,
verifies SHA/source commitments, then checks the completed full audit. This
is NOT an independently executed physics replication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_extra_margin_or_query"
C="fault_always_single_privileged_query"
FROZEN_SOURCE_COMMIT="a7fd01fcb0e633408bce5da573bf09758c317aaa"
FIRSTS={"pull_cube":[2020001,2020009,2020017,2020025],
        "stack_cube":[2030001,2030009,2030017,2030025]}
EXPECTED_CHECKPOINTS={
 "pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
 "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}

def truth(seed):
    index=(seed-1)%4
    return ("applied" if index in (1,3) else "held",
            "applied" if index in (2,3) else "held")

def read_source(orig_dir):
    files=sorted(orig_dir.rglob("mixed_ack_*_original8.json"))
    if len(files)!=8:
        raise ValueError(f"Expected exactly 8 original physical sources; found {len(files)}")
    enrolled=[]
    source_hashes=[]
    seen_shards=set()
    for file in files:
        raw=file.read_bytes()
        d=json.loads(raw)
        task="pull_cube" if d["task"]=="PullCube-v1" else "stack_cube" if d["task"]=="StackCube-v1" else None
        if task is None or len(d.get("episodes",[]))!=8:
            raise ValueError("Unknown original PhysX task")
        first=d["original_seed_population"][0]
        if first not in FIRSTS[task] or d["original_seed_population"]!=list(range(first,first+8)):
            raise ValueError("Missing/shifted prospectively frozen original shard")
        if (task,first) in seen_shards:
            raise ValueError("Duplicate source shard")
        seen_shards.add((task,first))
        if d["real_physx_simulator"] is not True or d["frozen_model_retrained"] is not False:
            raise ValueError("Source is not frozen actual native CPU PhysX")
        if d["original_external_frozen_checkpoint_sha256"]!=EXPECTED_CHECKPOINTS[task]:
            raise ValueError("Third-party published checkpoint identity changed")
        pin=file.parent/"GIT_SOURCE_SHA.txt"
        if pin.read_text().strip()!=FROZEN_SOURCE_COMMIT:
            raise ValueError("Mixed pre/post outcome physical source revisions")
        src_sha=hashlib.sha256(raw).hexdigest()
        source_hashes.append({"task":task,"first":first,"sha256":src_sha,"original_name":file.name})
        for e in d["episodes"]:
            seed=e["seed"]
            if seed not in range(first,first+8) or (e["original_precommitted_physical_t2_execution_truth"],
                e["original_precommitted_physical_t3_execution_truth"])!=truth(seed):
                raise ValueError("Physical ground truth drift")
            reads=e["privileged_target_readback_decision_count"]
            successful=e["success_once"]
            if any(type(successful[n]) is not bool or type(reads[n]) is not int or reads[n] not in (0,1) for n in (A,B,C)):
                raise ValueError("Unknown method success/private read budget")
            if reads[C]!=1:
                raise ValueError("Fixed-reader control missing its charged private read")
            observed=e["public_motion_observation_cost_samples"]
            if observed[A]!=2 or observed[B]!=2:
                raise ValueError("Unequal physically observed two-public-sample budget")
            for n in (A,B,C):
                ff=e["faults"][n]
                if [x["step"] for x in ff]!=[2,3]:
                    raise ValueError("Fault pair not genuinely exposed")
            for k in ("matched_prefix_physical_audit","matched_margin_prefix_audit"):
                pref=e[k]
                if pref["valid_exact_prefix"] is not True or max(pref["native_fault_dispatch_linf_each"])>5e-5:
                    raise ValueError("Actual dispatched physical history prefix mismatch")
                for f in ("pre_t5_achieved_position_max_abs_m","pre_t5_achieved_orientation_geodesic_rad",
                          "pre_t5_target_position_max_abs_m","pre_t5_target_orientation_geodesic_rad"):
                    if pref[f]>5e-5:
                        raise ValueError("Predecision physical state diverged")
            a=e["public_t3_evidence"]
            b=e["same_sensor_margin_evidence"]
            vals=[float(z) for z in b["candidate_residuals_m"]]
            if len(vals) not in (2,3,4) or not all(math.isfinite(z) for z in vals):
                raise ValueError("Malformed public observation hypothesis residuals")
            order=sorted(range(len(vals)),key=lambda i:vals[i])
            gap=vals[order[1]]-vals[order[0]]
            eps=float(b["prior_training_epsilon_m"])
            possible=[i for i,distance in enumerate(vals) if distance<=eps+1e-12]
            orig=(len(possible)==1 and possible[0]==order[0] and
                all(distance>eps+.002 for i,distance in enumerate(vals) if i!=order[0]))
            gated=orig and gap>=0.0045
            if (b["raw_public_history_base_admissible"] is not orig
                or b["authorized"] is not gated
                or abs(b["candidate_second_best_separation_m"]-gap)>1e-10
                or b["gap_threshold_exploratory_training_chosen_m"]!=0.0045):
                raise ValueError("Registered additional separation decision was altered")
            if reads[A]!=int(not a["authorized"]) or reads[B]!=int(not gated):
                raise ValueError("Actual policy read counts inconsistent with physical decision")
            if b["wrong_confident"] is not (gated and order[0] not in b["audit_only_true_candidate_indices"]):
                raise ValueError("Independent wrong confident truth audit drift")
            enrolled.append({
                "task":task,"seed":seed,"truth":"/".join(truth(seed)),
                "A_success":successful[A],"B_success":successful[B],"C_success":successful[C],
                "A_read":reads[A],"B_read":reads[B],"C_read":reads[C],
                "A_authorized":bool(a["authorized"]),"B_authorized":gated,
                "A_wrong":bool(a["wrong_confident"]),"B_wrong":bool(b["wrong_confident"]),
                "B_public_gap_m":gap})
    expected={(t,f) for t,fs in FIRSTS.items() for f in fs}
    if seen_shards!=expected or len(enrolled)!=64:
        raise ValueError("Incomplete 64 actual original native source cohort")
    enrolled.sort(key=lambda x:(x["task"],x["seed"]))
    return enrolled,sorted(source_hashes,key=lambda x:(x["task"],x["first"]))

def aggregate(rr):
    return {
        "n":len(rr),
        "A_success":sum(x["A_success"] for x in rr),
        "B_success":sum(x["B_success"] for x in rr),
        "C_success":sum(x["C_success"] for x in rr),
        "A_reads":sum(x["A_read"] for x in rr),
        "B_reads":sum(x["B_read"] for x in rr),
        "C_reads":sum(x["C_read"] for x in rr),
        "A_authorized":sum(x["A_authorized"] for x in rr),
        "B_authorized":sum(x["B_authorized"] for x in rr),
        "A_wrong":sum(x["A_wrong"] for x in rr),
        "B_wrong":sum(x["B_wrong"] for x in rr),
        "both_A_B_success":sum(x["A_success"] and x["B_success"] for x in rr),
        "both_A_B_fail":sum(not x["A_success"] and not x["B_success"] for x in rr),
        "A_only":sum(x["A_success"] and not x["B_success"] for x in rr),
        "B_only":sum(x["B_success"] and not x["A_success"] for x in rr),
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--originals",type=Path,required=True)
    parser.add_argument("--completed-full",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    rr,sources=read_source(args.originals)
    official=json.loads(args.completed_full.read_bytes())
    stats=aggregate(rr)
    reference={
      "A_success":official["pub_success"],"B_success":official["margin_success"],"C_success":official["fixed_success"],
      "A_reads":official["pub_reads"],"B_reads":official["margin_reads"],"C_reads":official["fixed_reads"],
      "A_authorized":official["pub_unique"],"B_authorized":official["margin_unique"],
      "A_wrong":official["pub_wrong"],"B_wrong":official["margin_wrong"],
    }
    for key,expected in reference.items():
        if stats[key]!=expected:
            raise ValueError(f"Original full source auditor vs independent rescore disagrees: {key}")
    if (stats["both_A_B_success"]!=official["paired_A_vs_B_task_outcomes"]["both"]
        or stats["both_A_B_fail"]!=official["paired_A_vs_B_task_outcomes"]["neither"]
        or stats["A_only"]!=official["paired_A_vs_B_task_outcomes"]["A_only"]
        or stats["B_only"]!=official["paired_A_vs_B_task_outcomes"]["B_only"]):
        raise ValueError("Original paired task-outcome audit changed")
    o=sorted(official["original_physical_sha256"],key=lambda x:(x["task"],x["first"]))
    if any(a["sha256"]!=b["sha256"] for a,b in zip(sources,o)) or len(o)!=8:
        raise ValueError("Exact raw native PhysX SHA256 mismatch")
    out={
      "schema":"INDEPENDENT_SOURCE_ONLY_REAUDIT_NEW64_OBSERVABILITY_MARGIN_REAL_PHYSX_V1",
      "original_640_physx_worlds_executed":True,
      "separate_third_party_execution":False,
      "prospective_native_source_head":FROZEN_SOURCE_COMMIT,
      "two_public_xyz_samples_each":128,
      "experimental_64_task_resets":64,
      "SHA256_original_shards":sources,
      "overall":stats,
      "by_task":{t:aggregate([x for x in rr if x["task"]==t]) for t in FIRSTS},
      "per_actual_original_state":rr,
      "interpretation":"Prospective threshold-test NEGATIVE: both public treatments succeeded on exactly same original states, no observed errors in either, extra margin gate spent 2 more privileged reads. Fixed reader achieved one additional StackCube task success. Not physical safety, conformal reliability, external replication or proof of noninferiority.",
    }
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("ORIGINAL_SHA256_FULL_NEW64_SOURCE_REAUDIT",json.dumps({
       "n":len(rr),"overall":stats,"by_task":out["by_task"],"original_shards":len(sources)
    },sort_keys=True))

if __name__=="__main__":
    main()
