"""Original-source audit of genuinely indistinguishable native controller memories.

From 16 ACTUAL FIRST-run physically stepped same-seed four-truth PhysX shards.
No new physics, learning, likelihood calibration, or new independent trial.
Same initial public state + exactly identical before/after achieved XYZ can
coexist with DIFFERENT true full commanded-target memories despite two true
physical ACK interventions and a delivered zero neutral t4 probe.

The impossibility is deliberately LIMITED: deterministic inference using
only {task, frozen initial state, before-XYZ, after-XYZ, same known probe}
cannot identify both original actual target histories. Richer sensors,
new discriminative actions, or a privileged read could separate them.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import isfinite, sqrt
from pathlib import Path

DEFAULT_SOURCE = (
    Path(__file__).resolve().parent
    / "frozen_policy_transfer/evidence/numeric_initial_parity_factorial_original128_2110001_2120016"
)
PUBLIC = "fault_public_t3_fourhistory_or_t4_query"
SOURCE_COUNTS = {"pull_cube": 2110001, "stack_cube": 2120001}

def checked_sources(root: Path):
    manifest_path = root / "SHA256SUMS"
    records = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        sha, file = line.split(maxsplit=1)
        if file in records or len(sha) != 64 or any(ch in file for ch in "/\\"):
            raise ValueError("Duplicate/unsafe/invalid FIRST original source manifest")
        records[file] = sha
        actual = sha256((root / file).read_bytes()).hexdigest()
        if actual != sha:
            raise ValueError(f"IMMUTABLE_FIRST_PHYSX_SOURCE_CHANGED {file}")
    if len(records) != 34:
        raise ValueError("Incomplete first-run 16 originals + 16 audits + two aggregates")
    expected = {
        f"factorial_{task}_chunk{chunk}_truth{truth}_{tail}.json"
        for task in SOURCE_COUNTS
        for chunk in range(2)
        for truth in range(4)
        for tail in ("original8", "audit")
    } | {"original_run_full128_audit.json", "separate_independent_source_only_full128_audit.json"}
    if set(records) != expected:
        raise ValueError("Incomplete or substituted first-run physical source set")
    original = {}
    for task, start in SOURCE_COUNTS.items():
        for chunk in range(2):
            seeds = list(range(start + chunk * 8, start + chunk * 8 + 8))
            for truth in range(4):
                basename = f"factorial_{task}_chunk{chunk}_truth{truth}_original8.json"
                # Original research source uses Python's non-strict Infinity in a
                # *refusal diagnostic*; the original bytes are never rewritten.
                d = json.loads((root / basename).read_text(encoding="utf-8"))
                if (d.get("real_physx_simulator") is not True
                    or d.get("frozen_model_retrained") is not False
                    or d.get("original_seed_population") != seeds
                    or len(d.get("episodes", [])) != 8
                    or [x["seed"] for x in d["episodes"]] != seeds
                    or d.get("within_reset_factorial_condition_index") != truth):
                    raise ValueError("Original registered native PhysX trial identity mismatch")
                for row in d["episodes"]:
                    if row["physical_truth_index_factorial_condition_AUDIT_ONLY"] != truth:
                        raise ValueError("Counterfactual ACK truth was retrospectively altered")
                    key = (task, row["seed"])
                    original.setdefault(key, {})[truth] = row
    if len(original) != 32 or any(len(arms) != 4 for arms in original.values()):
        raise ValueError("Not all 32 original reset clusters have all four physical truths")
    return original,records

def measurement(row):
    ev = row["public_t3_evidence"]
    before, after = ev.get("before_xyz"), ev.get("after_xyz")
    if not (isinstance(before,list) and isinstance(after,list) and len(before)==len(after)==3
            and all(type(x) in (float,int) and isfinite(x) for x in before+after)):
        return None
    faults = row["faults"].get(PUBLIC, [])
    if [f["step"] for f in faults] != [2,3]:
        return None
    probe = row.get("shared_neutral_probe_step4", {}).get(PUBLIC, {})
    if not (probe.get("physically_dispatched") is True
            and probe.get("known_delivered_no_new_unknown_ack") is True
            and probe.get("native_six_dim_arm") == [0,0,0,0,0,0]):
        return None
    idx = ev.get("audit_only_true_candidate_indices", [])
    if not (isinstance(idx,list) and len(idx)==1 and type(idx[0]) is int):
        raise ValueError("True target-history audit label absent")
    posrot = ev.get("after_physics_audit_pose_errors")
    if not (isinstance(posrot,list) and len(posrot)==4
            and all(len(pair)==2 and all(isfinite(x) for x in pair) for pair in posrot)
            and posrot[idx[0]][0] < 1e-5 and posrot[idx[0]][1] < 1e-5):
        raise ValueError("Original auditor true full target candidate not identifiable")
    return tuple(before+after)

def audit(root: Path = DEFAULT_SOURCE, exact: bool = True):
    rows, ledger = checked_sources(root)
    total_cells = 0
    physical_measured = 0
    compared = 0
    collided = []
    observations_missing = []
    pairwise_dists = []
    for (task,seed),states in sorted(rows.items()):
        records=[]
        for truth in range(4):
            row = states[truth]
            total_cells+=1
            obs=measurement(row)
            if obs is None:
                observations_missing.append({"task":task,"seed":seed,"truth":truth})
                continue
            physical_measured+=1
            records.append((truth,row,obs))
        for i,(truth_a,a,x) in enumerate(records):
            for truth_b,b,y in records[i+1:]:
                compared+=1
                d = sqrt(sum((p-q)**2 for p,q in zip(x,y)))
                pairwise_dists.append(d)
                if d!=0: continue
                if a["initial_source_physical_obs_sha256"] != b["initial_source_physical_obs_sha256"]:
                    # A numeric near-match in source reset is NOT exact same
                    # immutable initial public observation. Treat as inconclusive.
                    continue
                idx_a=a["public_t3_evidence"]["audit_only_true_candidate_indices"][0]
                idx_b=b["public_t3_evidence"]["audit_only_true_candidate_indices"][0]
                if idx_a==idx_b:
                    # Same true target despite a nominal ACK-truth intervention;
                    # cannot be a target-memory indistinguishability witness.
                    continue
                sep_a=a["public_t3_evidence"]["after_physics_audit_pose_errors"][idx_b]
                sep_b=b["public_t3_evidence"]["after_physics_audit_pose_errors"][idx_a]
                if min(sep_a[0],sep_b[0]) <= .01 or min(sep_a[1],sep_b[1]) <= .01:
                    continue
                fa = a["faults"][PUBLIC]
                fb = b["faults"][PUBLIC]
                expected = lambda fs: tuple(f["actual_native_precommitted_execution_truth"] for f in fs)
                if expected(fa)==expected(fb):
                    raise ValueError("Indistinguishable rows have same physical ground truth")
                collided.append({
                    "task":task, "reset_seed":seed, "truth_conditions":[truth_a,truth_b],
                    "physical_truth_A":expected(fa), "physical_truth_B":expected(fb),
                    "original_initial_public_obs_sha256":a["initial_source_physical_obs_sha256"],
                    "six_public_XYZ_numbers_bitwise_equal_after_JSON_load":True,
                    "same_public_before_xyz":list(x[:3]), "same_public_after_xyz":list(x[3:]),
                    "actual_hidden_target_index_A":idx_a,"actual_hidden_target_index_B":idx_b,
                    "commanded_target_position_separation_m_min_two_audits":min(sep_a[0],sep_b[0]),
                    "commanded_target_orientation_separation_rad_min_two_audits":min(sep_a[1],sep_b[1]),
                    "source_both_faults_physically_exposed":True,
                    "actual_delivered_neutral_t4_probe_both_worlds":True,
                    "interpretation":"Impossible to correctly force two distinct target-history labels from same stated public sensor+control+initial data in BOTH factual worlds",
                })
    witness_seeds={ (q["task"],q["reset_seed"]) for q in collided}
    if exact and (total_cells,compared,len(collided),len(witness_seeds)) != (128,187,3,3):
        raise ValueError(f"Original full source 2x2 observability evidence changed: {(total_cells,compared,len(collided),len(witness_seeds))}")
    if exact and {r["reset_seed"] for r in collided}!={2110003,2110004,2110012}:
        raise ValueError("Original source exact-same-observation distinct-target case hidden")
    return {
        "schema":"source_pinned_physical_hidden_target_observational_equivalence_v1",
        "source_original_manifest_SHA256_verified_file_count":len(ledger),
        "source_32_reset_clusters":len(rows),
        "actual_physx_worlds_original":1152,
        "registered_real_ACK_truth_cells":total_cells,
        "cells_with_two_faults_and_delivered_observation_probe":physical_measured,
        "observation_pairs_actually_available":compared,
        "cells_without_complete_valid_public_measurement":observations_missing,
        "exact_six_value_public_XYZ_collisions_with_distinct_hidden_full_pose":len(collided),
        "independent_original_reset_clusters_with_observability_counterexample":len(witness_seeds),
        "source_frozen_conflict_witnesses":collided,
        "conditional_information_floor":"At least one of two different true targets must be misidentified by any forced deterministic function of the EXACT stated common public inputs, or the method must abstain",
        "equal_prior_two_world_forced_classifier_accuracy_upper":0.5,
        "not_an_unconditional_robot_safety_theorem":True,
        "not_a_proof_all_nonzero_probes_are_useless":True,
        "not_an_independently_run_outside_physics_experiment":True,
        "measurement_scope":"task+identical_initial_obs+achievedXYZ_before_and_after+known_zero_t4_probe; no full video, IMU, encoder, or privileged target at run time",
        "caution":"This is a finite-record counterexample, not a population error lower bound or an original mathematical impossibility theorem. Probe can be redesigned or an authoritative memory read used.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.source)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("FACTUAL_PHYSX_OBSERVABILITY_COLLISION",json.dumps({
       "source_orig_sha_files":result["source_original_manifest_SHA256_verified_file_count"],
       "cells":result["registered_real_ACK_truth_cells"],
       "valid_public_pairs":result["observation_pairs_actually_available"],
       "distinct_target_same_public_XYZ_witnesses":result["source_frozen_conflict_witnesses"]},sort_keys=True))

if __name__=="__main__":main()
