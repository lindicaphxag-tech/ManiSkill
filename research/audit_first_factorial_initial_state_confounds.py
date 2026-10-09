"""Independent original FIRST FAILED same-seed 2x2 PhysX source integrity census.

The 16 native physics shard jobs DID succeed and the 128 original seed-truth
cells exist, but the whole-population causal match gate DID NOT pass.
This tool documents exactly why without weakening, deleting or rewriting data.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

TASKS=("pull_cube","stack_cube")
TRUTHS=(0,1,2,3)
ARM_NAMES=("source_no_fault","fault_oracle_private_target",
"fault_optimistic_unverified_ack","fault_strict_common_exact",
"fault_robust_two_history_without_query",
"fault_robust_then_single_privileged_query",
"fault_always_single_privileged_query",
"fault_assume_held_without_query",
"fault_public_t3_fourhistory_or_t4_query")

def audit(folder:Path):
    source=list(folder.glob("factorial_*_original8.json"))
    shards=list(folder.glob("factorial_*_audit.json"))
    if len(source)!=16 or len(shards)!=16:
        raise ValueError("First failed native PhysX run must include ALL 16 untouched source and 16 accompanying audit files")
    rows=[]
    hashes={}
    all_episodes=0
    for task in TASKS:
        for chunk in range(2):
            for truth_index in TRUTHS:
                prefix=f"factorial_{task}_chunk{chunk}_truth{truth_index}"
                p=folder/f"{prefix}_original8.json"
                raw=p.read_bytes()
                record=json.loads(raw)
                if (record.get("within_reset_factorial_condition_index")!=truth_index or
                    record.get("task")!=("PullCube-v1" if task=="pull_cube" else "StackCube-v1") or
                    len(record.get("episodes",[]))!=8):
                    raise ValueError(f"Original native physical source metadata inconsistent: {prefix}")
                hashes[p.name]=hashlib.sha256(raw).hexdigest()
                hashes[prefix+"_audit.json"]=hashlib.sha256((folder/(prefix+"_audit.json")).read_bytes()).hexdigest()
                for i,r in enumerate(record["episodes"]):
                    seed=(1310001 if task=="pull_cube" else 1320001)+chunk*8+i
                    if r["seed"]!=seed:
                        raise ValueError("Unexpected or omitted original initial reset identity")
                    if r["physical_truth_index_factorial_condition_AUDIT_ONLY"]!=truth_index:
                        raise ValueError("Truth assignment mutated in original source")
                    h=r.get("initial_source_physical_obs_sha256")
                    if not isinstance(h,str) or len(h)!=64:
                        raise ValueError("Missing first-run original physical initial reset hash")
                    armdiffs=r.get("initial_obs_diff",{})
                    if set(armdiffs)!=(set(ARM_NAMES)-{"source_no_fault"}):
                        raise ValueError("All other actual treatment arms' initial observations missing")
                    if max(float(x) for x in armdiffs.values())>5e-4:
                        raise ValueError("Different controller treatment arms within one physical condition; separate confound")
                    rows.append({"task":task,"seed":seed,"truth_idx":truth_index,
                                 "initial_hash":h,"source_shard":p.name,
                                 "within_condition_other_arms_max_initial_obs_diff":max(armdiffs.values()),
                                 "public_success":r["success_once"]["fault_public_t3_fourhistory_or_t4_query"],
                                 "public_target_reads":r["privileged_target_readback_decision_count"]["fault_public_t3_fourhistory_or_t4_query"]})
                    all_episodes+=1
    if all_episodes!=128:raise ValueError("Incomplete source")
    grouped=defaultdict(dict)
    for row in rows:
        grouped[(row["task"],row["seed"])][row["truth_idx"]]=row
    if len(grouped)!=32 or any(set(x)!=set(TRUTHS) for x in grouped.values()):
        raise ValueError("128 source cells not exactly grouped to 32 complete task/seed clusters")
    bad=[]
    good=[]
    for (task,seed),blocks in grouped.items():
        sources={t:blocks[t]["initial_hash"] for t in TRUTHS}
        entry={"task":task,"seed":seed,"initial_hashes_by_real_execution_truth":sources,
               "identical_across_HH_AH_HA_AA":len(set(sources.values()))==1,
               "within_each_condition_original_controller_arms_match":True}
        (good if entry["identical_across_HH_AH_HA_AA"] else bad).append(entry)
    if not bad:raise AssertionError("Original whole-factorial failed init-hash audit but this tool found no discrepancy")
    counts={t:{"matched":sum(x["task"]==t for x in good),
               "mismatched":sum(x["task"]==t for x in bad)}
            for t in TASKS}
    return {"schema":"first_original_true_native_PhysX_2x2_initial_source_hash_invalidity_v1",
            "original_source_run":"https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37930607707",
            "source_commit":"06e4ceec3b6f0a5c5b174e272d965d1166c93ed7",
            "first_run_all_physically_step_shards_completed":16,
            "first_run_independent_full_factorial_audit_passed":False,
            "source_cells":128,"source_reset_clusters":32,
            "same_seed_initial_hash_valid_clusters":len(good),
            "same_seed_initial_hash_INVALID_clusters":len(bad),
            "counts_by_task":counts,
            "invalid_original_source_clusters":bad,
            "matching_source_clusters":good,
            "original_source_SHA256_ledger":hashes,
            "NO_task_success_causal_claim_from_unmatched_clusters":True,
            "do_not_relabel_this_first_run_as_all_green":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.original_source_dir)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_FACTORED_PHYSICS_FAILED_INITIAL_HASH_CAUSAL_MATCH",
          json.dumps({"n_original_cells":result["source_cells"],
                     "n_actual_clusters":result["source_reset_clusters"],
                     "n_mismatched_clusters":result["same_seed_initial_hash_INVALID_clusters"],
                     "by_task":result["counts_by_task"]},sort_keys=True))
if __name__=="__main__":
    main()
