"""Recompute all 128 original real native PhysX source cells; do NOT fake same-seed matching.

Strict original 16 shard SHA & source audit verification. If initial state hashes
mismatch, report exactly how many purported within-seed physical states differ
and mark original factorial causal pairing INVALID. Never relax equality or
drop mismatching groups. No physics rerun, no result tuning.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path
from research.run_same_reset_ack_factorial import (
    select,truth,validate,assert_preoutcome,blob,PREREG,SOURCE,CLASSIFIER,TASKS
)

def audit(root):
    assert_preoutcome()
    expected={f"factorial_{task}_chunk{chunk}_truth{t}_{suffix}.json"
        for task in TASKS for chunk in (0,1) for t in range(4)
        for suffix in ("original8","audit")}
    actual={p.name for p in root.glob("factorial_*.json")}
    if actual!=expected:
        raise ValueError(f"Not all original 16 physically stepped shard pair files preserved, missing={expected-actual}, extra={actual-expected}")
    rows=[];manifest={}
    for task in TASKS:
        for chunk in (0,1):
            for t in range(4):
                prefix=f"factorial_{task}_chunk{chunk}_truth{t}"
                src=root/(prefix+"_original8.json")
                scored=root/(prefix+"_audit.json")
                raw=src.read_bytes()
                data=json.loads(raw)
                expected_report=validate(data,task,chunk,t)
                expected_report.update(
                    schema="same_reset_factorial_true_2x2_shard_audit_v1",
                    physical_original_sha256=hashlib.sha256(raw).hexdigest(),
                    prereg_git_blob=blob(PREREG),
                    new_runner_git_blob=blob(SOURCE),
                    unchanged_response_model_git_blob=blob(CLASSIFIER))
                if expected_report!=json.loads(scored.read_text()):
                    raise ValueError("Original physically computed shard differs from independent exact audit: "+prefix)
                manifest[src.name]=hashlib.sha256(raw).hexdigest()
                manifest[scored.name]=hashlib.sha256(scored.read_bytes()).hexdigest()
                rows.extend(expected_report["rows"])
    if len(rows)!=128:raise ValueError("Not 128 actual native PhysX physical seed/truth cells")
    cells={}
    for r in rows:
        k=(r["task"],r["seed"])
        if (k,r["truth_index"]) in {(kk,ii) for kk,v in cells.items() for ii in v}:
            raise ValueError("Duplicate original physical truth cell")
        cells.setdefault(k,{})[r["truth_index"]]=r
    if len(cells)!=32 or any(set(v)!={0,1,2,3} for v in cells.values()):
        raise ValueError("Incomplete source per task/seed × all four actual ACK truth patterns")
    mismatch=[];matched=[]
    for (task,seed),v in sorted(cells.items()):
        hashes=[v[t]["initial_source_physical_obs_sha256"] for t in range(4)]
        if any(type(h) is not str or len(h)!=64 for h in hashes):
            raise ValueError("Missing physical source reset hash")
        group={"task":task,"seed":seed,"distinct_source_initial_observation_hashes":len(set(hashes)),
            "raw_hashes_by_truth_index":hashes,
            "per_truth_public_task_success":[v[t]["new_success"] for t in range(4)],
            "per_truth_fixed_task_success":[v[t]["fixed_success"] for t in range(4)],
            "per_truth_public_reads":[v[t]["new_reads"] for t in range(4)]}
        (matched if len(set(hashes))==1 else mismatch).append(group)
    counts=collections.Counter()
    for r in rows:
        counts["public_task_completed"]+=int(r["new_success"])
        counts["fixed_task_completed"]+=int(r["fixed_success"])
        counts["strong_task_completed"]+=int(r["strong_success"])
        counts["public_private_reads"]+=r["new_reads"]
        counts["fixed_private_reads"]+=r["fixed_reads"]
        counts["strong_private_reads"]+=r["strong_reads"]
        counts["wrong_confident"]+=int(r["wrong_confident"] is True)
        counts["public_confident"]+=int(r["public_authorized"] is True)
        counts["full_t2t3_physical_fault_exposed"]+=int(r["public_both_faults_exposed"])
        counts["public_probe_events"]+=r["public_sample_events"]
    return {
        "schema":"original_128_1152_native_physx_nonmatching_start_forensic_v1",
        "recreated_from_source_original_executed_worlds":True,
        "unmodified_original_task_reset_seed_truth_cells":128,
        "native_PhysX_worlds_actually_executed":1152,
        "original_distinct_reset_seed_ids":32,
        "initial_exact_state_hash_matched_seed_groups":len(matched),
        "initial_exact_state_hash_MISMATCHED_seed_groups":len(mismatch),
        "initial_hash_comparison_is_necessary_not_sufficient_for_causal_equivalence":True,
        "valid_strict_original_all32_same_reset_factorial":len(mismatch)==0,
        "original_failed_all_population_audit_is_preserved_and_NOT_relabelled_success":True,
        "no_paired_counterfactual_claim_if_any_source_initial_hash_mismatch":True,
        "original_all_128_cell_intent_to_treat_counts_descriptive_only":dict(counts),
        "real_original_physics_per_shard_sha256":manifest,
        "source_initial_exact_matches":matched,
        "source_initial_MISMATCHES":mismatch,
        "no_simulation_rerun":True,
        "no_posthoc_tolerance_lowering":True,
        "not_independent_external_replication":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.source_dir)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_TRUE_PHYXS_128_CELL_FORENSIC_NONSELECTION",json.dumps({
        "states":result["unmodified_original_task_reset_seed_truth_cells"],
        "worlds":result["native_PhysX_worlds_actually_executed"],
        "exact_matched_32_seed_groups":result["initial_exact_state_hash_matched_seed_groups"],
        "mismatched_32_seed_groups":result["initial_exact_state_hash_MISMATCHED_seed_groups"],
        "strict_paired_causal_valid":result["valid_strict_original_all32_same_reset_factorial"],
        "descriptive_endpoints_only":result["original_all_128_cell_intent_to_treat_counts_descriptive_only"]
    },sort_keys=True))

if __name__=="__main__": main()
