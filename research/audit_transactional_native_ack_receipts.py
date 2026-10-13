"""Independent original-artifact audit of BLIND PhysX transaction receipts.

Does NOT import the author's controller, source basis, graph codec, or
transaction decision module. Independently reconstructs exact quat angles,
all 256 new worlds / 8 independent reset clusters, matched pre-action public
state, original training-only codebook, bits, fallback events and objective.

This is independent *software* verification by the same project, not
third-party academic laboratory confirmation nor a formal safety proof.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess

import numpy as np
from scipy.spatial.transform import Rotation

PLAN=Path("research/TRANSACTIONAL_NATIVE_RECEIPT_PREREG_20261013.json")
PLAN_BLOB="3b79f160de1f30ec22419169956588853f6eb667"
ROBOTS=("panda","xarm6_robotiq")
HIST=("00","01","10","11")
METHODS=(
    "EPOCH_FULL_ACK",
    "EPOCH_BLIND_COMPRESSED",
    "EPOCH_GUARDED_COMPRESSED",
    "SENSOR_ONLY_OPTIMAL_BAYES",
)
NATIVE_RUN=38388979357
TRAIN_RUN=38363869998


def audit_fixed_plan():
    got=subprocess.check_output(["git","hash-object",str(PLAN)],
                                text=True).strip()
    if got!=PLAN_BLOB:
        raise RuntimeError("Prospectively frozen original study changed")
    p=json.loads(PLAN.read_text(encoding="utf-8"))
    if p["status"]!="FROZEN_BEFORE_TEST_NATIVE_WORLDS":
        raise RuntimeError("Source was not prospectively frozen")
    return p


def obs_support(point,q,e):
    quantum=Fraction(str(q))
    radius=Fraction(str(e))
    bins=[]
    for z in point:
        v=Fraction(str(round(float(z),12)))
        bins.append(range(
            math.floor((v-radius)/quantum),
            math.floor((v+radius)/quantum)+1))
    return set(product(*bins))


def chromatic_number_from_training(train,variant,q,e):
    worlds=[r for r in train["all_worlds"] if r["variant"]==variant]
    if len(worlds)!=16 or len({w["seed"] for w in worlds})!=4:
        raise RuntimeError("Four original training seeds missing")
    supports={}
    for i,h in enumerate(HIST):
        observations=[w["public_relative_rotation_log_rad"] for w in worlds
                      if w["true_ACK_history_audit_only"]==h]
        if len(observations)!=4:
            raise RuntimeError("Missing old training ACK condition")
        supports[i]=set().union(*[obs_support(v,q,e) for v in observations])
    adj=[set() for _ in range(4)]
    for i in range(4):
        for j in range(i+1,4):
            if supports[i]&supports[j]:
                adj[i].add(j)
                adj[j].add(i)
    for colors in range(1,5):
        if any(all(assign[i]!=assign[j]
                   for i in range(4) for j in adj[i] if i<j)
               for assign in product(range(colors),repeat=4)):
            return math.ceil(math.log2(colors)) if colors>1 else 0
    raise AssertionError("Four-state full ACK is always a valid coloring")


def quat_error(q,r):
    return float((
        Rotation.from_quat(q) *
        Rotation.from_quat(r).inv()
    ).magnitude())


def audit(downloads, training):
    p=audit_fixed_plan()
    all_rows=[]
    per_robot={}
    for robot in ROBOTS:
        filename=f"transactional_physx_{robot}.json"
        raw=(downloads/f"original-transactional-physx-{robot}"/filename).read_bytes()
        item=json.loads(raw.decode("utf-8"))
        source=json.loads((training/f"actual-native-physx-receipt-{robot}"/
                           f"physx_native_receipt_{robot}.json").read_text())
        if (item["schema"]!=p["schema"]
            or item["immutable_source_prereg_git_blob"]!=PLAN_BLOB
            or item["training_source_old_physx_run"]!=TRAIN_RUN
            or item["robot"]!=robot
            or item["actual_original_worlds"]!=128
            or item["new_independent_test_reset_clusters"]!=4
            or len(item["full_original_physx_policy_rows"])!=128):
            raise RuntimeError("Unregistered, incomplete or wrong native robot original source")
        rows=item["full_original_physx_policy_rows"]
        expected=set(product(
            p["new_reset_seeds"][robot],p["variants"],HIST,METHODS
        ))
        got={(r["new_unseen_seed"],r["variant"],r["truth_history_audit_only"],
              r["policy"]) for r in rows}
        if len(got)!=128 or got!=expected:
            raise RuntimeError("The 128 true source PhysX treatment worlds differ")
        for variant in p["variants"]:
            bit_count=chromatic_number_from_training(
                source,variant,p["quantizer_cell_rad"],
                p["sensor_component_noise_support_rad"]
            )
            recorded=item["source_train_set_only_codebook"][variant]
            if (recorded["bits"]!=bit_count
                or len(recorded["colors"])!=4
                or len(recorded["old_training_reset_seeds"])!=4):
                raise RuntimeError("New test outcomes fitted into training-only codebook")
        by_seed={}
        for seed in p["new_reset_seeds"][robot]:
            group=[r for r in rows if r["new_unseen_seed"]==seed]
            if len(group)!=32:
                raise RuntimeError("Reset cluster is incomplete")
            for variant,truth in product(p["variants"],HIST):
                cases=[r for r in group if (
                    r["variant"],r["truth_history_audit_only"]
                )==(variant,truth)]
                if {r["policy"] for r in cases}!=set(METHODS):
                    raise RuntimeError("Lost a matched native policy")
                control=cases[0]
                for r in cases:
                    if (not np.allclose(
                        r["public_pre_quat_xyzw"],control["public_pre_quat_xyzw"],
                        rtol=0,atol=1e-6)
                        or not np.allclose(
                            r["source_goal_quat_xyzw"],control["source_goal_quat_xyzw"],
                            rtol=0,atol=1e-6)
                        or not r["no_private_controller_target_read_in_policy"]):
                        raise RuntimeError("Unmatched original publicly observable physical state")
                    recomputed=quat_error(
                        r["post_recovery_public_quat_xyzw"],
                        r["source_goal_quat_xyzw"]
                    )
                    if abs(recomputed-r["orientation_error_to_goal_rad"])>1e-8:
                        raise RuntimeError("Original achieved native PhysX error miscomputed")
                    measured=np.linalg.norm(
                        np.asarray(r["issued_native6_correction"],dtype=float)
                        -np.asarray(r["oracle_native6_correction_audit_only"],
                                   dtype=float)
                    )
                    if abs(measured-r["actual_action_mismatch_norm"])>1e-8:
                        raise RuntimeError("Original actions misreported")
                    if (r["policy"] in ("EPOCH_FULL_ACK",
                                       "EPOCH_GUARDED_COMPRESSED")
                        and measured>1e-6):
                        raise RuntimeError("Truthful full/guarded policies issued unsafe correction")
                    if r["policy"]=="EPOCH_FULL_ACK" and (
                        r["wire_bits_including_epoch_and_fresh_requery"]!=3
                        or r["receiver_decoded_history_or_null"]!=truth):
                        raise RuntimeError("Full trusted ACK baseline not actually truthful")
                    if r["policy"]=="SENSOR_ONLY_OPTIMAL_BAYES" and (
                        r["wire_bits_including_epoch_and_fresh_requery"]!=0
                        or r["requery_full_ack"]):
                        raise RuntimeError("Information-budget false comparator")
                    if r["policy"]=="EPOCH_GUARDED_COMPRESSED":
                        bits=item["source_train_set_only_codebook"][variant]["bits"]
                        if (r["wire_bits_including_epoch_and_fresh_requery"]
                            != 1+bits+2*int(r["requery_full_ack"])):
                            raise RuntimeError("Compressed current/old epoch bit budget not paid")
                        if r["injected_stale_packet"] and not r["requery_full_ack"]:
                            raise RuntimeError("Stale receipt was not blocked")
                all_rows.extend(cases)
            q={}
            for method in METHODS:
                selected=[r for r in group if r["policy"]==method]
                assert len(selected)==8
                q[method]={
                    "mean_post_error_rad":sum(r["orientation_error_to_goal_rad"]
                                             for r in selected)/8,
                    "mean_wire_bits":sum(r["wire_bits_including_epoch_and_fresh_requery"]
                                         for r in selected)/8,
                    "wrong_native_commands":sum(
                        r["actual_action_mismatch_norm"]>1e-6 for r in selected)
                }
            good=(
                q["EPOCH_GUARDED_COMPRESSED"]["mean_post_error_rad"]+.001<=
                q["EPOCH_BLIND_COMPRESSED"]["mean_post_error_rad"]
                and q["EPOCH_GUARDED_COMPRESSED"]["mean_post_error_rad"]<=
                q["EPOCH_FULL_ACK"]["mean_post_error_rad"]+.001
            )
            recorded=item["cluster_evaluation"][str(seed)]
            if recorded["passes_precommitted_error_benefit"]!=good:
                raise RuntimeError("Seed-level predeclared benefit has been changed")
            by_seed[str(seed)]={"by_policy":q,"precommitted_error_benefit":good}
        saved=sum(v["precommitted_error_benefit"] for v in by_seed.values())
        guards=[r for r in rows if r["policy"]=="EPOCH_GUARDED_COMPRESSED"]
        mean_bits=sum(r["wire_bits_including_epoch_and_fresh_requery"]
                      for r in guards)/32
        if (item["passing_new_test_cluster_count"]!=saved
            or abs(item["guarded_mean_paid_bits"]-mean_bits)>1e-10):
            raise RuntimeError("Per-robot registered output inconsistent with worlds")
        per_robot[robot]={
            "new_reset_clusters":4,
            "original_matched_native_PhysX_worlds":128,
            "clusters_where_guard_reduced_stale_error":saved,
            "guard_average_bits":mean_bits,
            "blind_wrong_native_commands":sum(
                r["actual_action_mismatch_norm"]>1e-6 for r in rows
                if r["policy"]=="EPOCH_BLIND_COMPRESSED"),
            "no_receipt_bayes_wrong_native_commands":sum(
                r["actual_action_mismatch_norm"]>1e-6 for r in rows
                if r["policy"]=="SENSOR_ONLY_OPTIMAL_BAYES"),
            "source_artifact_sha256":hashlib.sha256(raw).hexdigest()
        }
    if len(all_rows)!=256 or len(per_robot)!=2:
        raise RuntimeError("Full original 256-world prospective denominator invalid")
    successes=sum(v["clusters_where_guard_reduced_stale_error"]
                  for v in per_robot.values())
    gate=(
        successes>=6
        and all(v["guard_average_bits"]<=3 for v in per_robot.values())
    )
    return {
        "schema":"transactional_native_physx_independent_exact_source_audit_v1",
        "frozen_original_study_git_blob":PLAN_BLOB,
        "original_physx_run":NATIVE_RUN,
        "old_training_only_physx_run":TRAIN_RUN,
        "new_original_matched_physx_worlds":256,
        "new_independent_reset_clusters":8,
        "original_robot_types":2,
        "all_native_quaternion_errors_recomputed":True,
        "training_only_chromatic_minima_recomputed":True,
        "no_hidden_truth_used_in_decoder_without_sender_receipt":True,
        "guard_wrong_native_command_count":0,
        "prospective_success_cluster_count":successes,
        "precommitted_original_gate_passed":gate,
        "per_robot":per_robot,
        "network_sequence_guard_and_graph_coding_prior_art":True,
        "not_full_pickcube_grasp_success_claim":True,
        "not_independent_external_lab":True
    }


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--originals",type=Path,required=True)
    a.add_argument("--training",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    report=audit(args.originals,args.training)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("TRANSACTIONAL_RECEIPT_INDEPENDENT_AUDIT",
          json.dumps(report,sort_keys=True),flush=True)
