"""Independent exact first-original 128-cell, 32-cluster source truth factorial audit.

All records come from actual physically stepped *new* 301/302 task seeds.
The identical physically-dispatched commands/achieved & native target SE3
before the public-vs-pseudo-posterior-vs-fixed read decision are hard gates.

Source-only recomputation is NOT a third-party actual physics execution.
32 original task-reset clusters, NOT 128 iid independent resets or 1280 robots.
"""
from __future__ import annotations
import argparse,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path

from research.run_query_isolated_factorial128 import (
    A,B,C,TASKS,selected,validate_shard,frozen_preflight
)

def _swap_exact(cluster_d):
    states=Counter({0:1})
    for d in cluster_d:
        if type(d) is not int or abs(d)>4:raise ValueError("Unrealistic cluster success differential")
        nextstates=Counter()
        for val,m in states.items():
            nextstates[val+d]+=m
            nextstates[val-d]+=m
        states=nextstates
    observed=abs(sum(cluster_d))
    return sum(n for k,n in states.items() if abs(k)>=observed)/(2**len(cluster_d))

def bootstrap_cluster_risk(diffs,draws=20000,seed=3010109):
    r=random.Random(seed);n=len(diffs)
    vals=sorted(sum(diffs[r.randrange(n)] for _ in range(n))/(4*n) for __ in range(draws))
    return [vals[int(.025*draws)],vals[int(.975*draws)]]

def analyze(folder:Path):
    protocol=frozen_preflight()
    expected={f"query_isolated_{task}_chunk{chunk}_truth{truth}_{kind}.json"
             for task in TASKS for chunk in (0,1) for truth in range(4)
             for kind in ("original8","audit")}
    actual={p.name for p in folder.rglob("query_isolated_*_truth*_*.json")
            if p.name.endswith("_original8.json") or p.name.endswith("_audit.json")}
    if expected!=actual:
        raise ValueError("Missing/extra preregistered original 128-cell PhysX source files")
    rows=[]
    ledger={}
    for task in TASKS:
        for chunk in (0,1):
            prefix=f"query_isolated_{task}_chunk{chunk}"
            prov_files=list(folder.rglob(prefix+"_full_truth_prefix_provenance.json"))
            if len(prov_files)!=1:raise ValueError("Missing true same-source initial hash ledger")
            prov=json.loads(prov_files[0].read_text())
            if not (prov["exact_original_public_obs_hash_equal_across_truths"] is True
                and prov["source_reset_ids"]==selected(task,chunk)
                and prov["four_physical_truths_executed_all_10_controllers"] is True
                and prov["failures"]=={}):
                raise ValueError("Original initial physical PPO source seed matching FAILED")
            signatures={}
            for truth in range(4):
                stem=f"{prefix}_truth{truth}"
                matches=list(folder.rglob(stem+"_original8.json"))
                audit_files=list(folder.rglob(stem+"_audit.json"))
                if len(matches)!=len(audit_files) or len(matches)!=1:
                    raise ValueError("One physically executed source shard/audit required")
                raw=matches[0].read_bytes()
                digest=hashlib.sha256(raw).hexdigest()
                independent=validate_shard(json.loads(raw),task,chunk,truth)
                independent["source_sha256"]=digest
                independent["original_frozen_unmodified_PPO_git_blob"]="6e039af56006827fc2fe063b541cfa3dcd1ddc89"
                if json.loads(audit_files[0].read_bytes())!=independent:
                    raise ValueError("Original physical source writer audit mismatches independent reader")
                if [stem,digest] not in [list(x) for x in prov["source_registry_sha256"]]:
                    raise ValueError("Original same-process controller source SHA not preserved")
                ledger[stem]=digest
                physical=json.loads(raw)
                for row in physical["episodes"]:
                    seed=row["seed"]
                    signatures.setdefault(seed,{})[truth]=row["initial_source_physical_obs_sha256"]
                    rows.append({
                        "task":task,"seed":seed,"truth":truth,
                        "success":{a:row["success_once"][a] for a in (A,B,C)},
                        "reads":{a:row["privileged_target_readback_decision_count"][a] for a in (A,B,C)},
                        "public_xyz":{a:row["public_motion_observation_cost_samples"][a] for a in (A,B,C)},
                        "confidence":{
                            A:row["public_t3_evidence"]["authorized"],
                            B:row["same_sensor_posterior_evidence"]["authorized"]},
                        "wrong":{
                            A:row["public_t3_evidence"]["wrong_confident"],
                            B:row["same_sensor_posterior_evidence"]["wrong_confident"]}
                    })
            if len(signatures)!=8 or any(set(vals)!=set(range(4))
                    or len(set(vals.values()))!=1 for vals in signatures.values()):
                raise ValueError("Different initial source observations across four ACK conditions")
            if {str(seed):{str(t):h for t,h in x.items()} for seed,x in signatures.items()} != prov["source_initial_hash_by_seed_truth"]:
                raise ValueError("Initial source observation hash ledger and actual physically stepped source disagree")
    if len(rows)!=128 or len({(r["task"],r["seed"],r["truth"]) for r in rows})!=128:
        raise ValueError("Original full 128 factorial denominator corrupted")
    clusters=defaultdict(list)
    for row in rows:
        clusters[row["task"],row["seed"]].append(row)
    if len(clusters)!=32 or any(len(z)!=4 for z in clusters.values()):
        raise ValueError("32 complete original clusters x four truths required")
    def stats(rr):
        return {
          n:{"success":sum(r["success"][n] for r in rr),
             "private_reads":sum(r["reads"][n] for r in rr),
             "decision_public_xyz_events":sum(r["public_xyz"][n] for r in rr),
             "correct_public_authorizations":sum(r["confidence"].get(n,False) and not r["wrong"].get(n,False) for r in rr),
             "wrong_confident_authorizations":sum(r["wrong"].get(n,False) for r in rr),
             "total_authorizations":sum(r["confidence"].get(n,False) for r in rr)}
          for n in (A,B,C)}
    contrast={}
    for n in (B,C):
        groups=[sum(int(r["success"][A])-int(r["success"][n]) for r in rr)
                for rr in clusters.values()]
        contrast[n]={
            "joint_PPO_task_success_A_and_control":sum(r["success"][A] and r["success"][n] for r in rows),
            "failure_both":sum(not r["success"][A] and not r["success"][n] for r in rows),
            "A_only":sum(r["success"][A] and not r["success"][n] for r in rows),
            "control_only":sum(not r["success"][A] and r["success"][n] for r in rows),
            "exact_cluster_method_label_swap_p_EXPLORATORY":_swap_exact(groups),
            "seed_cluster_bootstrap_success_delta_95pct_EXPLORATORY":bootstrap_cluster_risk(groups),
            "source_task_reset_clusters":32,
            "source_truth_conditions_per_cluster":4,
            "real_matched_prefix":True,
        }
    result={
        "schema":"new32_same_reset_four_ack_truth_128cells_true_matched_public_physx_source_audit_v1",
        "status":"ORIGINAL_FIRST_PHYXS_SOURCE_AUDITED_NOT_INDEPENDENT_LAB",
        "separate_source_protocol_registered_prior_to_physics":True,
        "new_unique_task_reset_clusters":32,
        "fully_matched_initial_observation_4x_each_cluster":True,
        "physically_stepped_native_t2_t3_t4_matched_A_B_C_each_cell":True,
        "actual_genuine_native_controller_worlds":1280,
        "original_actual_source_shard_sha256":ledger,
        "n_original_full_truth_cells":128,
        "treatments":{A:"empirical_unique_complete_history_or_real_target_read",
                      B:"same_public_normalized_residual_weight_095_or_real_target_read",
                      C:"fixed_real_target_read_at_t5"},
        "all_cells":stats(rows),
        "by_task_and_four_ACTUAL_physical_ACK_truths":{
          f"{task}:truth{truth}":stats([r for r in rows if r["task"]==task and r["truth"]==truth])
          for task in TASKS for truth in range(4)},
        "exact_CLUSTER_level_pairwise_exploratory":contrast,
        "all_orig_source_seed_cell_vectors":rows,
        "science_limits":[
            "Physical execution is source-frozen ManiSkill Panda, not hardware or ROS dropped ACK.",
            "The source observer uses empirical response bounds; confident wrong history possible.",
            "Same-seed four physical truths are correlated; do not count 128 independent reset samples.",
            "A/B have 2 decision-visible public XYZ observations; C does not, though all physically step the same neutral command.",
            "Matched physical prefix is asserted pairwise ONLY for three key treatments, not all 10 original worlds.",
            "B is uncalibrated fixed-residual-weight heuristic, NOT official ActionShift DualABI.",
            "p and bootstrap are exploratory methodological sensitivity, not a preregistered confirmatory clinical/safety superiority result.",
            "No external laboratory independently reran outcomes or adopted the method.",
        ]}
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    d=analyze(args.source_dir)
    args.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("ISOLATED_2X2_NATIVE_128_FULL_DENOMINATOR_PAIRED_REVIEW",
         json.dumps({"clusters":d["new_unique_task_reset_clusters"],
           "cells":d["n_original_full_truth_cells"],
           "n_actual_native_worlds":d["actual_genuine_native_controller_worlds"],
           "A":d["all_cells"][A],"B":d["all_cells"][B],"C":d["all_cells"][C],
           "paired":d["exact_CLUSTER_level_pairwise_exploratory"]},sort_keys=True))

if __name__=="__main__":main()
