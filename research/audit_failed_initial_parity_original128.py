"""Original-source-only diagnostic for a FAILED strict identical-initial-reset factorial audit.

Never turns unequal per-seed initial physical SHA into a passed paired causal
study. Does not claim a numeric distance between states when the original data
only stored SHA-256 and not initial state vectors. All 128 native PhysX cells
remain included, and outcome totals are only exploratory.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,pathlib
TASKS={"pull_cube":range(1310001,1310017),"stack_cube":range(1320001,1320017)}
def audit(folder):
    files=sorted(folder.glob("factorial_*_original8.json"))
    if len(files)!=16:
        raise ValueError("Expected exact sixteen physically executed original shard files")
    cell={}; digests=[]
    for file in files:
        d=json.loads(file.read_bytes())
        task="pull_cube" if d["task"]=="PullCube-v1" else "stack_cube" if d["task"]=="StackCube-v1" else None
        if task not in TASKS or len(d.get("episodes",[]))!=8:
            raise ValueError("Unregistered PhysX source")
        t=d.get("within_reset_factorial_condition_index")
        if type(t) is not int or t not in range(4):
            raise ValueError("Missing true physical ACK condition")
        digests.append({"name":file.name,"sha256":hashlib.sha256(file.read_bytes()).hexdigest()})
        for ep in d["episodes"]:
            seed=ep["seed"]
            if seed not in TASKS[task]:
                raise ValueError("Unregistered seed")
            key=(task,seed,t)
            if key in cell or type(ep["initial_source_physical_obs_sha256"]) is not str:
                raise ValueError("Invalid duplicate or source initial hash")
            cell[key]={
              "initial_obs_sha256":ep["initial_source_physical_obs_sha256"],
              "truth_index":t,
              "actual_t2":ep["original_precommitted_physical_t2_execution_truth"],
              "actual_t3":ep["original_precommitted_physical_t3_execution_truth"],
              "public_success":ep["success_once"]["fault_public_t3_fourhistory_or_t4_query"],
              "fixed_success":ep["success_once"]["fault_always_single_privileged_query"],
              "public_reads":ep["privileged_target_readback_decision_count"]["fault_public_t3_fourhistory_or_t4_query"],
              "public_wrong":ep["public_t3_evidence"].get("wrong_confident",False),
              "within_single_truth_source_other_arms_max_diff":max(ep["initial_obs_diff"].values()),
            }
    required={(task,seed,t) for task,seeds in TASKS.items() for seed in seeds for t in range(4)}
    if set(cell)!=required:raise ValueError("Missing original PhysX factorial cells")
    grouped=[]; byTask={}
    for task,seeds in TASKS.items():
        match=0
        for seed in seeds:
            rows=[cell[(task,seed,t)] for t in range(4)]
            hashes=[r["initial_obs_sha256"] for r in rows]
            n=len(set(hashes))
            match+=n==1
            grouped.append({
              "task":task,"seed":seed,"matching_sha_across_four_truths":n==1,
              "unique_initial_sha_count":n,
              "hashes_by_truth":hashes,
              "within_shard_arm_max_diff":max(r["within_single_truth_source_other_arms_max_diff"] for r in rows),
              "outcomes_unmatched_exploratory_only":[r["public_success"] for r in rows],
              "reads_unmatched_exploratory_only":[r["public_reads"] for r in rows],
            })
        byTask[task]={"seed_clusters":len(seeds),"four_truth_identical_initial_SHA_clusters":match,
                      "four_truth_nonidentical_initial_SHA_clusters":len(seeds)-match}
    failures=[x for x in grouped if not x["matching_sha_across_four_truths"]]
    return {
      "schema":"FAILED_SAME_RESET_FACTORIAL_INITIAL_PARITY_PHYSX_DIAGNOSTIC_V1",
      "source_physics_run":"https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37930607707",
      "initial_SHA_matching_is_strict":True,
      "initial_observation_vectors_available":False,
      "numeric_tolerance_parity_CANNOT_BE_DETERMINED_from_SHA_alone":True,
      "FAIL_CLOSED_original_all_population_audit":len(failures)>0,
      "all_128_original_true_PhysX_cells":len(cell),
      "physically_stepped_worlds_not_repeated_here":1152,
      "not_valid_as_exact_same_initial_state_causal_experiment":len(failures)>0,
      "by_task":byTask,
      "failed_seed_clusters":failures,
      "all_seed_clusters":grouped,
      "sources_sha256":digests,
      "interpretation":"All 16 original physical shards independently stepped nine native worlds per reset/condition, but initial observation SHA differs for at least one within-seed four-condition comparison. Old raw files lack initial numerical observation vector, so a numeric closeness bound cannot be retrospectively proved. No cherry-picking or dropping mismatched clusters is allowed for a prospective causal factorial headline."
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    d=audit(a.source_dir)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("STRICT_SHA_INITIAL_PARITY_FULL128_DIAGNOSTIC",json.dumps({
      "all_cells":d["all_128_original_true_PhysX_cells"],
      "by_task":d["by_task"],
      "first_mismatch":d["failed_seed_clusters"][0] if d["failed_seed_clusters"] else None,
      "global_strict_factorial_invalid":d["FAIL_CLOSED_original_all_population_audit"]
    },sort_keys=True))
if __name__=="__main__": main()
