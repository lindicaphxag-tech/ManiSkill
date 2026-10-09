"""Full original-source 2x2 ACK truth auditor; no simulator imports or result tuning.

Eight byte-exact original PhysX shard records + their independent per-shard
audits; preserve every enrolled pre-fault loss and negative control.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path
from research.run_matched_prefix_twoack_new64 import (
    PUBLIC, STRONG, FIXED, HELD, select, validate, assert_preoutcome, truth,
)

def audit(folder:Path):
    assert_preoutcome()
    expected={f"pairedprefix_{t}_chunk{i}_{kind}.json"
             for t in ("pull_cube","stack_cube")
             for i in range(4) for kind in ("original8","audit")}
    present={p.name for p in folder.glob("pairedprefix_*.json")}
    if present!=expected:
        raise ValueError(f"Expected exactly 16 unmodified JSON sources; missing={expected-present}; unknown={present-expected}")
    allrows=[]; sha256={}; signed_shards=[]
    for task in ("pull_cube","stack_cube"):
        for chunk in range(4):
            basename=f"pairedprefix_{task}_chunk{chunk}"
            p=folder/f"{basename}_original8.json"
            raw=p.read_bytes()
            if not raw:
                raise ValueError("Empty source")
            digest=hashlib.sha256(raw).hexdigest()
            source=json.loads(raw)
            recalculated=validate(source,task,chunk)
            recalculated.update(schema="matched_prefix_true_2x2_shard_source_audit_v1",
                physical_original_sha256=digest,
                prereg_git_blob=__import__("research.run_matched_prefix_twoack_new64",fromlist=["blob"]).blob(
                    "research/MATCHED_PREFIX_TWOACK_FROZEN_PPO64_PREOUTCOME_V1.json"),
                new_runner_git_blob=__import__("research.run_matched_prefix_twoack_new64",fromlist=["blob"]).blob(
                    "research/frozen_ppo_matched_prefix_twoack_2x2_physx.py"),
                unchanged_response_model_git_blob=__import__("research.run_matched_prefix_twoack_new64",fromlist=["blob"]).blob(
                    "research/empirical_probe_response_classifier.py"))
            original_audit=folder/f"{basename}_audit.json"
            if json.loads(original_audit.read_bytes())!=recalculated:
                raise ValueError("Independent full auditor and shard-native scorer disagree")
            sha256[p.name]=digest
            sha256[original_audit.name]=hashlib.sha256(original_audit.read_bytes()).hexdigest()
            signed_shards.append({"task":task,"chunk":chunk,"source_sha256":digest})
            allrows.extend(recalculated["rows"])
    required=[(task,s) for task,start in (("pull_cube",1380001),("stack_cube",1390001))
              for s in range(start,start+32)]
    if [(r["task"],r["seed"]) for r in allrows]!=required:
        raise ValueError("Original source denominator / frozen seed ordering corrupted")
    out={"schema":"causal_identical_prefix_true_2x2_64_native_physx_audit_v1",
         "unique_source_reset_states":64,
         "actually_stepped_simulator_worlds":576,
         "both_true_t2_and_t3_physically_mixed":True,
         "registered_source_64":signed_shards,
         "all_original_shard_sha256":sha256,
         "four_truth_strata":{},
         "all_episodes":allrows,
         "notes":"Not externally replicated, contact safe, network ACK loss or general VLA rollout."}
    comparisons={k:{"task_success":0,"private_reads":0}
                 for k in ("public","strong_task","fixed_t5","always_held")}
    pair={"both":0,"neither":0,"new_only":0,"strong_only":0}
    observed_confident=0; wrong_confident=0
    for row in allrows:
        for key,success,reads in (
            ("public",row["new_success"],row["new_reads"]),
            ("strong_task",row["strong_success"],row["strong_reads"]),
            ("fixed_t5",row["fixed_success"],row["fixed_reads"]),
            ("always_held",row["held_success"],0)):
            comparisons[key]["task_success"]+=int(success)
            comparisons[key]["private_reads"]+=reads
        x=row["new_success"];y=row["strong_success"]
        pair["both" if x and y else "new_only" if x else "strong_only" if y else "neither"]+=1
        observed_confident+=int(row["public_authorized"] is True)
        wrong_confident+=int(row["wrong_confident"] is True)
    for task in ("pull_cube","stack_cube"):
        for first,second in (("held","held"),("applied","held"),
                             ("held","applied"),("applied","applied")):
            stratum=first+"/"+second
            eligible=[r for r in allrows if r["task"]==task and r["truth"]==stratum]
            if len(eligible)!=8:
                raise ValueError("Physical truth mix not balanced inside task")
            out["four_truth_strata"][task+"/"+stratum]={
                "n":8,
                "public_success":sum(r["new_success"] for r in eligible),
                "strong_success":sum(r["strong_success"] for r in eligible),
                "fixed_success":sum(r["fixed_success"] for r in eligible),
                "always_held_success":sum(r["held_success"] for r in eligible),
                "public_private_reads":sum(r["new_reads"] for r in eligible),
                "strong_private_reads":sum(r["strong_reads"] for r in eligible),
                "public_confident":sum(r["public_authorized"] is True for r in eligible),
                "wrong_confident":sum(r["wrong_confident"] is True for r in eligible),
                "public_two_physical_faults_reached":sum(r["public_both_faults_exposed"] for r in eligible),
                "all_faulted_arms_shared_neutral_probe":sum(r["all_faulted_arms_received_neutral_probe"] for r in eligible),
                "actual_nonzero_applied_native_fault_actions_across_8_faulted_arms":sum(r["applied_nonzero_native_dispatch_events_all_faulted_arms"] for r in eligible),
            }
    out["outcomes"]=comparisons
    out["paired_new_vs_task_aware_strong"]=pair
    out["public_confident_history_admissions"]=observed_confident
    out["observed_confident_wrong_history"]=wrong_confident
    out["public_both_fault_events_exposed"]=sum(r["public_both_faults_exposed"] for r in allrows)
    out["all_faulted_worlds_received_shared_probe"]=sum(r["all_faulted_arms_received_neutral_probe"] for r in allrows)
    out["equal_probe_per_full_source_population"]=out["all_faulted_worlds_received_shared_probe"]==64
    out["interpretation_gates"]={
        "physical_2x2_protocol_balanced":True,
        "all_faulted_arms_physically_received_probe":out["equal_probe_per_full_source_population"],
        "no_observed_confident_mistakes":wrong_confident==0,
        "no_formal_safety_certification":True,
        "no_task_superiority_without_paired_statistical_test":True,
    }
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.source_dir)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("FULL_MATCHED_PREFIX_2X2_64_NATIVE_PHYSX",json.dumps({
        "reset_states":result["unique_source_reset_states"],
        "native_worlds":result["actually_stepped_simulator_worlds"],
        "outcomes":result["outcomes"],
        "paired":result["paired_new_vs_task_aware_strong"],
        "public_confident":result["public_confident_history_admissions"],
        "public_wrong":result["observed_confident_wrong_history"],
        "exposed_2x2_public_trials":result["public_both_fault_events_exposed"],
        "shared_probe_all_arms_trials":result["all_faulted_worlds_received_shared_probe"]},sort_keys=True))
    if result["observed_confident_wrong_history"]:
        print("NEGATIVE_RESULT_WRONG_CONFIDENT_HISTORY: retain every failure")
    if not result["equal_probe_per_full_source_population"]:
        print("INCOMPLETE_PROBE_EXPOSURE: interpret success ITT, do not claim full exposure")

if __name__=="__main__":
    main()
