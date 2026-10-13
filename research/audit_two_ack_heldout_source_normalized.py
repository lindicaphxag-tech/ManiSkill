"""Independent frozen-source holdout audit; NO physics package dependency.

Read original real PhysX JSON artifacts, not producer summaries. Recompute
every prospective policy prediction from public pre-correction XYZ and training
source-only goal, check complete factorial pairing, and report cluster-aware
paired comparisons WITHOUT pseudo-replicated significance claims.
"""
from __future__ import annotations

import argparse
import json
from math import isfinite, sqrt
from pathlib import Path
import subprocess


PROTO = Path("research/TWO_ACK_HELDOUT_SOURCE_NORMALIZED_PREREG_20261013.json")
PROTO_SHA = "b86bdf490d7bf3ee1335cfc774cdd11c41db7ae8"
TRAIN = Path("research/TWO_ACK_HELDOUT_TRAIN_PROTOTYPES_20261013.json")
TRAIN_SHA = "48000e2831537c178262835b17748b37672b10d4"
ORIGINAL_PHYSX_RUN_ID = 38332965278


def _norm(a, b):
    return sqrt(sum((float(x)-float(y))**2 for x,y in zip(a,b)))


def _nearest(f, prototypes, key):
    return min(
        ("00", "01", "10", "11"),
        key=lambda h: (sum(
            (float(a)-float(b))**2
            for a,b in zip(f,prototypes[h][key])
        ), h),
    )


def audit(input_dir):
    for path,digest in ((PROTO,PROTO_SHA),(TRAIN,TRAIN_SHA)):
        blob = subprocess.check_output(
            ["git","hash-object",str(path)],text=True
        ).strip()
        if blob != digest:
            raise RuntimeError("After-outcome prereg/prototype alteration forbidden")
    spec = json.loads(PROTO.read_text(encoding="utf-8"))
    training = json.loads(TRAIN.read_text(encoding="utf-8"))
    if (spec["status"] != "FROZEN_BEFORE_TEST_PHYSX_OUTCOMES"
            or spec["frozen_training_prototypes_git_blob"] != TRAIN_SHA
            or spec["denominator"]["real_physx_worlds_total"] != 128):
        raise ValueError("Wrong prospective protocol")
    result = {}
    for robot in spec["robots"]:
        original = json.loads(
            (input_dir/f"source_normalized_two_ack_new_holdout_{robot}.json")
            .read_text(encoding="utf-8")
        )
        rows = original["rows"]
        expected = {
            (seed,h,p) for seed in spec["new_holdout_test_seeds"][robot]
            for h in spec["histories"] for p in spec["policies"]
        }
        if (original["robot"] != robot
                or original["preregistered_protocol_git_blob"] != PROTO_SHA
                or original["frozen_train_prototypes_git_blob"] != TRAIN_SHA
                or original["independent_new_reset_clusters"] != 4
                or original["real_physical_holdout_worlds"] != 64
                or len(rows) != 64):
            raise ValueError("Wrong robot/heldout denominator")
        keys = [(r["seed"],r["true_history_audit_only"],r["policy"])
                for r in rows]
        if set(keys) != expected or len(set(keys)) != 64:
            raise ValueError("Missing, duplicated or substituted heldout policy arm")
        if set(spec["new_holdout_test_seeds"][robot]) & set(
            spec["prior_train_seeds"][robot]
        ):
            raise ValueError("Training/holdout reset overlap")
        prototypes = training["training_prototypes"][robot]
        for row in rows:
            if (row["robot"] != robot
                    or row["true_new_physx_world"] is not True
                    or row["public_policy_hidden_ack_reads"] != 0
                    or row["public_policy_private_target_reads"] != 0
                    or row["post_action_private_audit_reads"] != 1
                    or row["oracle_privileged_truth_only"] != (
                        row["policy"] == "PRIVILEGED_ORACLE"
                    )):
                raise ValueError("Privileged information or wrong source world")
            old = row["observed_pre_recovery_public_xyz"]
            goal = row["source_only_common_goal_xyz"]
            feature = row["public_classifier_feature_xyz_or_null"]
            if any(len(x)!=3 for x in (old,goal,row["achieved_end_xyz"])):
                raise ValueError("Malformed robot XYZ")
            numerics = [
                row["achieved_goal_error_m"],
                row["post_action_private_target_audit_error_m"],
                *old,*goal,*row["achieved_end_xyz"],*row["native_recovery_action"]
            ]
            if len(row["native_recovery_action"]) != 6 or any(
                not isinstance(x,(int,float)) or not isfinite(x) for x in numerics
            ):
                raise ValueError("Malformed physical evidence")
            if abs(_norm(row["achieved_end_xyz"],goal) -
                   row["achieved_goal_error_m"]) > 1e-9:
                raise ValueError("Producer's public task-space error is incorrect")
            if row["policy"] == "ABSOLUTE_XYZ":
                expected_input = old
                guessed = _nearest(old,prototypes,"raw_xyz")
            elif row["policy"] == "SOURCE_RELATIVE_XYZ":
                expected_input = [a-b for a,b in zip(old,goal)]
                guessed = _nearest(
                    expected_input,prototypes,"source_normalized_xyz"
                )
            elif row["policy"] == "NO_ACTION":
                expected_input,guessed = None,None
                if any(row["native_recovery_action"]):
                    raise ValueError("NO_ACTION secretly applied nonzero action")
            else:
                expected_input,guessed = None,row["true_history_audit_only"]
            if feature is None and expected_input is not None:
                raise ValueError("Public feature missing")
            if feature is not None and (
                expected_input is None or _norm(feature,expected_input) > 1e-10
            ):
                raise ValueError("Public feature substituted or hidden state read")
            if row["predicted_history_or_null"] != guessed:
                raise ValueError("Public model didn't follow frozen train centroids")
        # Critical paired-fairness audit: prior to decision, all four policies
        # must observe IDENTICAL public state for each new reset and true ACK.
        for seed in spec["new_holdout_test_seeds"][robot]:
            for h in spec["histories"]:
                records=[r for r in rows if r["seed"]==seed
                         and r["true_history_audit_only"]==h]
                if len(records)!=4 or len({
                    tuple(r["observed_pre_recovery_public_xyz"]) for r in records
                })!=1 or len({
                    tuple(r["source_only_common_goal_xyz"]) for r in records
                })!=1:
                    raise ValueError("Non-paired reset or policy changed state pre-choice")
        metrics={}
        for policy in spec["policies"]:
            records=[r for r in rows if r["policy"]==policy]
            mean=sum(r["achieved_goal_error_m"] for r in records)/len(records)
            chosen_count=(None if policy=="NO_ACTION" else sum(
                r["predicted_history_or_null"]==r["true_history_audit_only"]
                for r in records
            ))
            producer=original["mean_accuracy_and_error_by_policy"][policy]
            if (abs(mean-producer["mean_goal_error_m"])>1e-10
                    or chosen_count!=producer["correct_ack_count_or_null"]
                    or len(records)!=16):
                raise ValueError("Producer's outcome summary isn't raw-record correct")
            metrics[policy]={
                "holdout_original_worlds":len(records),
                "history_correct_or_null":chosen_count,
                "mean_achieved_xyz_error_m":mean,
            }
        by_seed={}
        for seed in spec["new_holdout_test_seeds"][robot]:
            mean={}
            for policy in spec["policies"]:
                values=[r["achieved_goal_error_m"] for r in rows
                        if r["seed"]==seed and r["policy"]==policy]
                if len(values)!=4:
                    raise ValueError("Missing paired true history within seed")
                mean[policy]=sum(values)/4
            gate=(mean["SOURCE_RELATIVE_XYZ"]<mean["ABSOLUTE_XYZ"]
                  and mean["SOURCE_RELATIVE_XYZ"]<mean["NO_ACTION"])
            prior=original["paired_original_seed_results"][str(seed)]
            if prior["source_normalized_better_than_both_baselines"]!=gate:
                raise ValueError("Producer changed prospective success gate")
            by_seed[str(seed)]={
                "paired_goal_error_means_m":mean,
                "source_better_than_both_baselines":gate,
            }
        gate_count=sum(v["source_better_than_both_baselines"]
                       for v in by_seed.values())
        if ((gate_count>=3) !=
                original["prospective_positive_gate_met_on_this_robot"]):
            raise ValueError("Producer altered preregistered per-robot gate")
        result[robot]={
            "unique_new_reset_clusters":4,
            "real_native_physx_worlds":64,
            "public_decision_reexecution_check":True,
            "paired_before_choice_states_identical":True,
            "policy_metrics":metrics,
            "prospective_win_seeds_out_of_four":gate_count,
            "prospective_positive_gate_met":gate_count>=3,
            "paired_new_seed_results":by_seed,
        }
    return {
        "schema":"independent_holdout_public_ack_policy_audit_v1",
        "original_physx_run_id":ORIGINAL_PHYSX_RUN_ID,
        "new_independent_reset_clusters":8,
        "physically_executed_condition_count":128,
        "no_first_experiment_as_external_replication":True,
        "no_task_completion_or_robot_safety_claim":True,
        "positive_gate_requires_both_robots":all(
            x["prospective_positive_gate_met"] for x in result.values()
        ),
        "by_robot":result,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.input_dir)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("TWO_ACK_PROSPECTIVE_INDEPENDENT_AUDIT",json.dumps({
        "positive_gate":result["positive_gate_requires_both_robots"],
        "robot_summaries":{
            r:{
                "independent_seeds":x["unique_new_reset_clusters"],
                "complete_worlds":x["real_native_physx_worlds"],
                "paired_win_seeds":x["prospective_win_seeds_out_of_four"],
                "mean_error_mm":{
                    p:round(1000*v["mean_achieved_xyz_error_m"],4)
                    for p,v in x["policy_metrics"].items()
                },
                "history_predictions_correct":{
                    p:v["history_correct_or_null"]
                    for p,v in x["policy_metrics"].items()
                }
            } for r,x in result["by_robot"].items()
        }
    },sort_keys=True))


if __name__=="__main__":
    main()
