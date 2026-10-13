"""Independent source-only 320-world SO3 audit of immutable PhysX artifacts.

Checks the 8 original heldout reset clusters, 4 truth labels x 2 command
variants x 5 preregistered policies, re-executes every public nearest-neighbor
decision with immutable training centroids, and recomputes full task metrics.
No private target state, trained VLA or independent outside-lab replication.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

PROTO=Path("research/TWO_ACK_SO3_VS_RESET_STRONG_PREREG_20261013.json")
PROTO_SHA="44f770ecabe87e894eb7a3fa94dde3e94a730734"
CENT=Path("research/TWO_ACK_SO3_FROZEN_TRAIN_CENTROIDS_20261013.json")
CENT_SHA="e078ba7e735874751e4c20b3768bd8bc56924d66"
HISTORY=("00","01","10","11")
POLICIES=("SOURCE_SO3_HYPOTHESES","RESET_SO3_BY_VARIANT",
          "RESET_SO3_POOLED","NO_ACTION","PRIVILEGED_ORACLE")
PHYSX_RUN_ID=38335458988


def _angle(qa,qb):
    return float((Rotation.from_quat(qa)*
                  Rotation.from_quat(qb).inv()).magnitude())


def _nearest(quat,reference):
    return min(HISTORY,key=lambda h:(_angle(quat,reference[h]),h))


def _mean(qs):
    anchor=np.asarray(qs[0],dtype=float)
    A=np.array(qs,dtype=float)
    flip=np.where(A@anchor<0,-1,1)
    q=np.sum(A*flip[:,None],axis=0)
    return (q/np.linalg.norm(q)).tolist()


def inspect_original_artifacts(directory):
    for path,want in [(PROTO,PROTO_SHA),(CENT,CENT_SHA)]:
        if subprocess.check_output(
            ["git","hash-object",str(path)],text=True
        ).strip()!=want:
            raise RuntimeError("Research prereg/prototypes altered after test")
    spec=json.loads(PROTO.read_text(encoding="utf-8"))
    training=json.loads(CENT.read_text(encoding="utf-8"))
    assert training["original_real_physx_training_run_id"]==38335064480
    assert training["training_physx_worlds"]==64
    answer={}
    for robot in spec["robots"]:
        raw=training["raw_training_worlds"][robot]
        if len(raw)!=32:
            raise ValueError("Lost original training source worlds")
        original={(r["seed"],r["variant"],r["true_history_training_only"])
                  for r in raw}
        expect={(seed,v,h) for seed in spec["training_seeds"][robot]
                for v in spec["action_variants"] for h in HISTORY}
        if original!=expect:
            raise ValueError("Training source cohort or denominator altered")
        frozen=training["centroids"][robot]
        for variant in spec["action_variants"]:
            for h in HISTORY:
                q=_mean([
                    x["relative_public_so3_quat_xyzw"] for x in sorted(
                        raw,key=lambda x:x["seed"]
                    ) if x["variant"]==variant
                    and x["true_history_training_only"]==h
                ])
                if _angle(q,frozen["by_variant"][variant][h])>1e-9:
                    raise ValueError("Frozen strong baseline was not built from train")
        for h in HISTORY:
            subset=sorted(
                (x for x in raw if x["true_history_training_only"]==h),
                key=lambda x:(x["seed"],x["variant"])
            )
            if _angle(_mean([x["relative_public_so3_quat_xyzw"]
                            for x in subset]),frozen["pooled"][h])>1e-9:
                raise ValueError("Pooled reset reference does not reproduce")
        name=directory/f"two_ack_so3_new_holdout_{robot}.json"
        payload=json.loads(name.read_text(encoding="utf-8"))
        rows=payload["rows"]
        if (payload["robot"]!=robot or len(rows)!=160
                or payload["registered_original_physical_worlds"]!=160
                or payload["unique_holdout_reset_clusters"]!=4
                or payload["training_centroids_frozen_git_blob"]!=CENT_SHA
                or payload["preoutcome_preregister_blob"]!=PROTO_SHA):
            raise ValueError("Original robot sample or prereg provenance failed")
        expected={(s,v,h,p) for s in spec["heldout_seeds"][robot]
                  for v in spec["action_variants"] for h in HISTORY
                  for p in POLICIES}
        seen={(r["seed"],r["variant"],r["true_history_audit_only"],r["policy"])
              for r in rows}
        if len(seen)!=160 or expected!=seen:
            raise ValueError("Dropped/duplicated original PhysX factorial cell")
        for s in spec["heldout_seeds"][robot]:
            for v in spec["action_variants"]:
                for h in HISTORY:
                    cells=[r for r in rows if r["seed"]==s
                           and r["variant"]==v
                           and r["true_history_audit_only"]==h]
                    if len(cells)!=5:
                        raise ValueError("Paired comparator rows not present")
                    # Absolute state before choice must be precisely identical:
                    if (len({tuple(r["public_pre_decision_quat_xyzw"])
                             for r in cells})!=1 or
                        len({tuple(r["public_reset_quat_xyzw"])
                             for r in cells})!=1 or
                        len({tuple(r["source_goal_quat_xyzw"])
                             for r in cells})!=1):
                        raise ValueError("Data leakage or nonidentical before-choice worlds")
        for x in rows:
            if (x.get("real_native_physx_cpu") is not True
                    or x.get("source_controller_private_target_read_count_before_decision")!=0
                    or x.get("public_policy_hidden_truth_access") is not False
                    or x.get("oracle_only_has_hidden_truth") !=
                       (x["policy"]=="PRIVILEGED_ORACLE")
                    or x.get("task_success_improvement_claimed") is not False):
                raise ValueError("Private ACK access or substituted source")
            n=x["native_rotation_recovery_action"]
            if (len(n)!=6 or not np.isfinite(n).all()
                    or np.linalg.norm(n[3:])>1+1e-6
                    or not np.allclose(n[:3],0)):
                raise ValueError("Unsupported, nonnative or overlimit correction")
            observed=x["public_pre_decision_quat_xyzw"]
            reset=x["public_reset_quat_xyzw"]
            rel=(Rotation.from_quat(observed)*
                 Rotation.from_quat(reset).inv()).as_quat()
            if x["policy"]=="SOURCE_SO3_HYPOTHESES":
                predicted=_nearest(observed,x["source_candidate_quaternions"])
            elif x["policy"]=="RESET_SO3_BY_VARIANT":
                predicted=_nearest(rel,frozen["by_variant"][x["variant"]])
            elif x["policy"]=="RESET_SO3_POOLED":
                predicted=_nearest(rel,frozen["pooled"])
            elif x["policy"]=="NO_ACTION":
                predicted=None
                if np.any(n):
                    raise ValueError("NO_ACTION silently moved robot")
            else:
                predicted=x["true_history_audit_only"]
            if predicted!=x["predicted_history_or_null"]:
                raise ValueError("Real policy used oracle truth or changed frozen decision")
            value=_angle(x["post_recovery_public_quat_xyzw"],
                         x["source_goal_quat_xyzw"])
            if abs(value-x["achieved_recovery_orientation_error_rad"])>1e-9:
                raise ValueError("Producer altered original achieved angular error")
        means={}
        for p in POLICIES:
            subset=[x for x in rows if x["policy"]==p]
            means[p]=sum(x["achieved_recovery_orientation_error_rad"]
                         for x in subset)/40
            count=None if p=="NO_ACTION" else sum(
                x["predicted_history_or_null"]==x["true_history_audit_only"]
                for x in subset
            )
            if (abs(means[p]-
                    payload["results"][p]["mean_end_angle_error_rad"])>1e-12
                    or payload["results"][p]["correct_hidden_history_or_null"]!=count):
                raise ValueError("Published risk/count differs from original 40 worlds")
        seed_details={}
        wins=0
        for seed in spec["heldout_seeds"][robot]:
            pair={}
            for p in POLICIES:
                subset=[x for x in rows if x["policy"]==p
                        and x["seed"]==seed]
                if len(subset)!=8:
                    raise ValueError("Original independent-cluster denominator wrong")
                pair[p]=sum(
                    x["achieved_recovery_orientation_error_rad"]
                    for x in subset
                )/len(subset)
            outcome=(pair["SOURCE_SO3_HYPOTHESES"]+.01 <
                     pair["RESET_SO3_BY_VARIANT"] and
                     pair["SOURCE_SO3_HYPOTHESES"]<pair["NO_ACTION"])
            if payload["paired_seed_results"][str(seed)][
                "source_beats_strong_reset_by_point_01rad"]!=outcome:
                raise ValueError("Precommitted positive gate misreported")
            wins+=int(outcome)
            seed_details[str(seed)]={"mean_error_rad":pair,
                                    "precommitted_gate_passed":outcome}
        if (wins!=payload["passing_independent_test_seed_clusters"]
                or (wins>=3)!=payload["precommitted_positive_gate_met"]):
            raise ValueError("Original researcher failed to enforce frozen gate")
        answer[robot]={
            "heldout_reset_clusters":4,
            "actual_physical_conditions":160,
            "source_replay_blind_and_comparator_pairing_audited":True,
            "mean_error_rad":means,
            "accuracies":{p:(None if p=="NO_ACTION" else sum(
                x["predicted_history_or_null"]==x["true_history_audit_only"]
                for x in rows if x["policy"]==p
            )) for p in POLICIES},
            "passing_new_reset_clusters":wins,
            "preregistered_positive_gate_met":wins>=3,
            "per_reset":seed_details,
        }
    return {
        "schema":"independent_real_so3_ack_study_audit_v1",
        "original_real_physics_run_id":PHYSX_RUN_ID,
        "total_true_new_physx_conditions":320,
        "independent_heldout_reset_clusters":8,
        "external_peer_review_or_hardware_safety_claim":False,
        "both_robot_positive_gates_met":all(
            r["preregistered_positive_gate_met"] for r in answer.values()
        ),
        "robots":answer,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=inspect_original_artifacts(args.input_dir)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("INDEPENDENT_SO3_STRONG_BASELINE_AUDIT",json.dumps({
        "both_robot_positive_gate":result["both_robot_positive_gates_met"],
        "robots":{
            robot:{
                "worlds":obj["actual_physical_conditions"],
                "paired_seed_wins":obj["passing_new_reset_clusters"],
                "mean_rad":{k:round(v,6)
                            for k,v in obj["mean_error_rad"].items()},
                "classification_correct":obj["accuracies"]
            } for robot,obj in result["robots"].items()
        }
    },sort_keys=True))


if __name__=="__main__":
    main()
