"""Original heldout native-SO3 two-missed-ACK policy comparison.

No new-reset data calibrates train centroids. Same real native PhysX world
setup for all 5 preregistered policies. Target private state getter absent
from training, classification, and correction stages.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

from research.cross_robot_ack_physics import pose_from, stepping
from research.two_ack_so3_native_protocol import (
    HISTORY_ORDER, correction_from_history_so3,
    nearest_reset_so3, nearest_source_hypothesis, quaternion_angle,
    setup_public_two_ack_world, verify_registered_plan,
)

TRAIN_PATH=Path("research/TWO_ACK_SO3_FROZEN_TRAIN_CENTROIDS_20261013.json")
TRAIN_BLOB="e078ba7e735874751e4c20b3768bd8bc56924d66"
PUBLIC=("SOURCE_SO3_HYPOTHESES","RESET_SO3_BY_VARIANT","RESET_SO3_POOLED")
POLICIES=(*PUBLIC,"NO_ACTION","PRIVILEGED_ORACLE")


def frozen_centroids(spec):
    current=subprocess.check_output(
        ["git","hash-object",str(TRAIN_PATH)],text=True
    ).strip()
    if current!=TRAIN_BLOB:
        raise RuntimeError("Training centroids altered after the prospective freeze")
    data=json.loads(TRAIN_PATH.read_text(encoding="utf-8"))
    if (data["original_real_physx_training_run_id"]!=38335064480
            or data["precommitted_design_blob"]!="44f770ecabe87e894eb7a3fa94dde3e94a730734"
            or data["training_physx_worlds"]!=64
            or set(data["centroids"])!=set(spec["robots"])):
        raise RuntimeError("Strong baseline training provenance mismatch")
    for robot in spec["robots"]:
        original=data["raw_training_worlds"][robot]
        if (len(original)!=32 or set(r["seed"] for r in original)!=set(
                spec["training_seeds"][robot])):
            raise RuntimeError("Baseline trained on unexpected reset cohort")
        expected={(int(seed),v,h) for seed in spec["training_seeds"][robot]
                  for v in spec["action_variants"] for h in HISTORY_ORDER}
        if {(r["seed"],r["variant"],r["true_history_training_only"])
            for r in original}!=expected:
            raise RuntimeError("Training true-history denominator wrong")
    return data


def real_physics_world(spec,train,robot,seed,variant,truth,policy):
    if (policy not in POLICIES
            or seed not in spec["heldout_seeds"].get(robot,())
            or variant not in spec["action_variants"]
            or truth not in HISTORY_ORDER):
        raise ValueError("Unregistered frozen test cell")
    env=None
    try:
        env,controller,arm,reset,measured,candidates=(
            setup_public_two_ack_world(spec,robot,seed,variant,truth)
        )
        public_quat=measured.quaternion_xyzw
        if policy=="SOURCE_SO3_HYPOTHESES":
            guess=nearest_source_hypothesis(public_quat,candidates)
        elif policy=="RESET_SO3_BY_VARIANT":
            guess=nearest_reset_so3(
                public_quat,reset.quaternion_xyzw,
                train["centroids"][robot]["by_variant"][variant]
            )
        elif policy=="RESET_SO3_POOLED":
            guess=nearest_reset_so3(
                public_quat,reset.quaternion_xyzw,
                train["centroids"][robot]["pooled"]
            )
        elif policy=="NO_ACTION":
            guess=None
        else:
            guess=truth # privileged oracle ONLY
        if guess is None:
            native=np.zeros(6,dtype=float)
        else:
            native=correction_from_history_so3(
                arm,candidates[guess],candidates["11"]
            )
        stepping(env,controller,native)
        last=None
        for _ in range(spec["recovery_hold_steps"]):
            last=stepping(env,controller,np.zeros(6))
        final=pose_from(arm.ee_pose_at_base)
        goal=candidates["11"]
        return {
            "robot":robot,"seed":seed,"variant":variant,
            "true_history_audit_only":truth,
            "policy":policy,"predicted_history_or_null":guess,
            "public_reset_quat_xyzw":list(reset.quaternion_xyzw),
            "public_pre_decision_quat_xyzw":list(public_quat),
            "source_candidate_quaternions":{h:list(candidates[h].quaternion_xyzw)
                                             for h in HISTORY_ORDER},
            "source_goal_quat_xyzw":list(goal.quaternion_xyzw),
            "native_rotation_recovery_action":native.tolist(),
            "post_recovery_public_quat_xyzw":list(final.quaternion_xyzw),
            "pre_recovery_goal_error_rad":quaternion_angle(
                public_quat,goal.quaternion_xyzw
            ),
            "achieved_recovery_orientation_error_rad":quaternion_angle(
                final.quaternion_xyzw,goal.quaternion_xyzw
            ),
            "official_pickcube_success_descriptive":last["official_success"],
            "source_controller_private_target_read_count_before_decision":0,
            "public_policy_hidden_truth_access":False,
            "oracle_only_has_hidden_truth":policy=="PRIVILEGED_ORACLE",
            "real_native_physx_cpu":True,
            "task_success_improvement_claimed":False,
        }
    finally:
        if env is not None:
            env.close()


def heldout_robot(robot):
    spec=verify_registered_plan()
    train=frozen_centroids(spec)
    if robot not in spec["robots"]:
        raise ValueError("Wrong robot")
    rows=[]
    for seed in spec["heldout_seeds"][robot]:
        for variant in spec["action_variants"]:
            for truth in HISTORY_ORDER:
                for policy in POLICIES:
                    row=real_physics_world(spec,train,robot,seed,
                                           variant,truth,policy)
                    print("NATIVE_SO3_HELDOUT_WORLD",
                          json.dumps(row,sort_keys=True),flush=True)
                    rows.append(row)
    expected={(seed,v,h,p) for seed in spec["heldout_seeds"][robot]
              for v in spec["action_variants"] for h in HISTORY_ORDER
              for p in POLICIES}
    actual={(x["seed"],x["variant"],x["true_history_audit_only"],x["policy"])
            for x in rows}
    if actual!=expected or len(rows)!=160:
        raise RuntimeError("Incomplete original SO3 physical test denominator")
    summary={}
    for policy in POLICIES:
        items=[x for x in rows if x["policy"]==policy]
        summary[policy]={
            "worlds":len(items),
            "mean_end_angle_error_rad":sum(
                x["achieved_recovery_orientation_error_rad"]
                for x in items
            )/len(items),
            "correct_hidden_history_or_null":(
                None if policy=="NO_ACTION" else sum(
                    x["true_history_audit_only"]==x["predicted_history_or_null"]
                    for x in items
                )
            ),
        }
    seed_level={}
    for seed in spec["heldout_seeds"][robot]:
        vals={}
        for policy in POLICIES:
            items=[x["achieved_recovery_orientation_error_rad"]
                   for x in rows if x["seed"]==seed and x["policy"]==policy]
            assert len(items)==8
            vals[policy]=sum(items)/len(items)
        seed_level[str(seed)]={
            "mean_orientation_error_rad_by_policy":vals,
            "source_beats_strong_reset_by_point_01rad":(
                vals["SOURCE_SO3_HYPOTHESES"]+.01 <
                vals["RESET_SO3_BY_VARIANT"]
                and vals["SOURCE_SO3_HYPOTHESES"] <
                vals["NO_ACTION"]
            ),
        }
    passes=sum(x["source_beats_strong_reset_by_point_01rad"]
               for x in seed_level.values())
    result={
        "schema":spec["schema"],"robot":robot,
        "training_centroids_frozen_git_blob":TRAIN_BLOB,
        "preoutcome_preregister_blob":"44f770ecabe87e894eb7a3fa94dde3e94a730734",
        "real_native_physx_cpu":True,
        "unique_holdout_reset_clusters":4,
        "registered_original_physical_worlds":160,
        "results":summary,
        "paired_seed_results":seed_level,
        "precommitted_positive_gate_met":passes>=3,
        "passing_independent_test_seed_clusters":passes,
        "constrained_recovery_not_automatic_cube_grasp":True,
        "rows":rows,
    }
    file=f"two_ack_so3_new_holdout_{robot}.json"
    Path(file).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                          encoding="utf-8")
    print("NATIVE_SO3_HELDOUT_COMPLETE",json.dumps({
        "robot":robot,"worlds":len(rows),
        "corrected_policy_results":summary,
        "prospective_win_clusters":passes,
        "positive_gate":passes>=3
    },sort_keys=True),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--robot",choices=("panda","xarm6_robotiq"),
                        required=True)
    heldout_robot(parser.parse_args().robot)
