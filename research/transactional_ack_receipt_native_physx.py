"""Unseen real CPU PhysX transaction-bound execution ACK receipts.

Strong comparator contract: the receipt codebooks, public sensor supports and
Bayesian prior are frozen from an older PhysX training cohort, with NO use of
any of the 8 new test reset seeds in their fitting. Receiver never reads hidden
ACK truth except via trustworthy received tag/full receipt; sim provides truth
for sender and post-hoc audit only.

This is a known network sequence-number + zero-error graph coding + Bayes
integration, NOT new information theory nor task-level grasp performance.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess

import numpy as np
import torch
from scipy.spatial.transform import Rotation

from research.cross_robot_ack_physics import pose_from,stepping
from research.two_ack_so3_native_protocol import (
    HISTORY_ORDER, correction_from_history_so3, quaternion_angle,
    setup_public_two_ack_world, verify_registered_plan,
)
from research.zero_error_execution_receipt import (
    conflict_graph,dsatur_coloring,receipt_decoder,
)

FROZEN=Path("research/TRANSACTIONAL_NATIVE_RECEIPT_PREREG_20261013.json")
FROZEN_BLOB="3b79f160de1f30ec22419169956588853f6eb667"
HIST=tuple(HISTORY_ORDER)
POLICIES=(
    "EPOCH_FULL_ACK",
    "EPOCH_BLIND_COMPRESSED",
    "EPOCH_GUARDED_COMPRESSED",
    "SENSOR_ONLY_OPTIMAL_BAYES",
)


def registered():
    b=subprocess.check_output(["git","hash-object",str(FROZEN)],text=True).strip()
    if b!=FROZEN_BLOB:
        raise RuntimeError("Frozen pretest transmission/robot contract altered")
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    original=verify_registered_plan()
    if (
        p["status"]!="FROZEN_BEFORE_TEST_NATIVE_WORLDS"
        or p["robot_ids"]!=original["robots"]
        or p["variants"]!=list(original["action_variants"])
        or p["truth_histories"]!=list(HIST)
        or p["physx_policy_world_denominator"]!=256
        or p["quantizer_cell_rad"]!=.04
        or p["sensor_component_noise_support_rad"]!=.004
        or p["new_reset_seeds"]["panda"]!=list(range(6000501,6000505))
        or p["new_reset_seeds"]["xarm6_robotiq"]!=list(range(6100501,6100505))
        or p["training_observation_contract"]["original_training_physx_run"]!=38363869998
    ):
        raise RuntimeError("Prospective protocol not the original fixed design")
    return p,original


def quantized_support(point,cell,epsilon):
    # Include both closed endpoints, and clamp nothing based on test outcomes.
    ranges=[]
    q=Fraction(str(cell))
    e=Fraction(str(epsilon))
    for component in point:
        c=Fraction(str(round(float(component),12)))
        ranges.append(range(math.floor((c-e)/q),
                            math.floor((c+e)/q)+1))
    from itertools import product
    support=frozenset(product(*ranges))
    if not support or len(support)>64:
        raise RuntimeError("Expected finite quantization support outside range")
    return support


def precise_public_observation(measured_q,reset_q,cell):
    v=(Rotation.from_quat(measured_q) *
       Rotation.from_quat(reset_q).inv()).as_rotvec()
    if not np.isfinite(v).all():
        raise RuntimeError("Invalid native public quaternion")
    return tuple(int(math.floor(float(x)/cell)) for x in v)


def training_codec(train,robot,variant,cell,eps):
    if (
        train["original_native_robot"]!=robot
        or train["native_worlds"]!=32
        or train["independent_reset_clusters"]!=4
        or len(train["all_worlds"])!=32
    ):
        raise ValueError("Old native PhysX training source missing")
    worlds=[r for r in train["all_worlds"] if r["variant"]==variant]
    if (len(worlds)!=16 or
        len({r["seed"] for r in worlds})!=4 or
        set(r["true_ACK_history_audit_only"] for r in worlds)!=set(HIST)):
        raise ValueError("Old training model incomplete")
    grouped=defaultdict(list)
    for row in worlds:
        grouped[row["true_ACK_history_audit_only"]].append(
            row["public_relative_rotation_log_rad"]
        )
    # Robust sensor support is union over previous TRAINING reset seeds.
    # No test seed is used to learn it, unlike the former retrospective graph.
    supports={
        i:frozenset().union(*[
            quantized_support(p,cell,eps) for p in grouped[h]
        ]) for i,h in enumerate(HIST)
    }
    anchor={i:i for i in range(4)} # conservatively distinct command modes
    adj=conflict_graph(anchor,supports)
    colors,k=dsatur_coloring(adj)
    if receipt_decoder(anchor,supports,colors)[1]!=0:
        raise RuntimeError("Previous-source codec has hidden ambiguity")
    bits=math.ceil(math.log2(k)) if k>1 else 0
    return {
        "colors":tuple(colors),
        "bits":bits,
        "known_support":supports,
        "num_colors":k,
        "old_train_seeds":sorted(set(r["seed"] for r in worlds)),
        "edge_count":sum(x.bit_count() for x in adj)//2
    }


def decode_tag(codec,actual_bin,tag):
    matches=[
        i for i in range(4)
        if codec["colors"][i]==tag and actual_bin in codec["known_support"][i]
    ]
    # If the true new world falls outside TRAIN support: ABSTAIN.
    # If two histories alias under frozen code: ABSTAIN. No guessed truth.
    return HIST[matches[0]] if len(matches)==1 else None


def no_receipt_bayes(codec,actual_bin):
    # Training-only generative model: uniform histories and uniform bins
    # within source support. This is exact MAP under that DECLARED prior.
    probs=[
        (Fraction(1,4*len(codec["known_support"][i]))
         if actual_bin in codec["known_support"][i] else Fraction(0))
        for i in range(4)
    ]
    best=max(range(4),key=lambda i:(probs[i],-i))
    return HIST[best]


def choose_from_packet(codec,true_sender_history,bin_observed,policy):
    if policy not in POLICIES:
        raise ValueError("Unknown frozen policy")
    idx=HIST.index(true_sender_history)
    stale=idx in (1,2) # Frozen 50% stale per four-history quartet.
    # Packet sender truth is used ONLY to simulate what the actual
    # trusted controller sends; the below RECEIVER sees the packet
    # contents, an epoch field, and its own public quantized observation.
    original_sender_index=(idx+1)%4 if stale else idx
    packet_color=codec["colors"][original_sender_index]
    packet_epoch=0 if stale else 1
    current_epoch=1
    packet_cost=codec["bits"]+1
    if policy=="EPOCH_FULL_ACK":
        # Fully trusted, freshly obtained 2-bit full ACK + same epoch bit.
        return true_sender_history,3,False,False,stale
    if policy=="SENSOR_ONLY_OPTIMAL_BAYES":
        guess=no_receipt_bayes(codec,bin_observed)
        return guess,0,False,False,stale
    decoded=decode_tag(codec,bin_observed,packet_color)
    if policy=="EPOCH_BLIND_COMPRESSED":
        # Explicitly IGNORE mismatch: erroneous stale action or abstention.
        return decoded,packet_cost,False,decoded is None,stale
    # Transactional protocol: first enforce session epoch; if the message
    # is stale OR unknown under old-training sensor support, request fresh
    # trusted full ACK. Retransmission costs 2 more ACK bits, NO free oracle.
    if packet_epoch!=current_epoch or decoded is None:
        return true_sender_history,packet_cost+2,True,False,stale
    return decoded,packet_cost,False,False,stale


def one_actual_native_world(old,plan,codec,robot,seed,variant,truth,policy):
    cfg=deepcopy(old)
    # Old frozen helper requires seeds to be registered in its validation;
    # add only the prospectively specified new-test seed to a private copy.
    cfg["heldout_seeds"][robot].append(seed)
    env=None
    try:
        env,controller,arm,reset,measured,candidates=(
            setup_public_two_ack_world(cfg,robot,seed,variant,truth)
        )
        obs=precise_public_observation(
            measured.quaternion_xyzw,reset.quaternion_xyzw,
            plan["quantizer_cell_rad"]
        )
        guess,bits,requery,abstain,stale=choose_from_packet(
            codec,truth,obs,policy
        )
        if guess is not None:
            native=correction_from_history_so3(
                arm,candidates[guess],candidates["11"]
            )
        else:
            native=np.zeros(6,dtype=np.float64)
        stepping(env,controller,native)
        last=None
        for _ in range(old["recovery_hold_steps"]):
            last=stepping(env,controller,np.zeros(6,dtype=np.float64))
        achieved=pose_from(arm.ee_pose_at_base)
        goal=candidates["11"]
        correct_native=correction_from_history_so3(
            arm,candidates[truth],goal
        )
        action_error=float(np.linalg.norm(native-correct_native))
        return {
            "robot":robot,"new_unseen_seed":seed,
            "variant":variant,"truth_history_audit_only":truth,
            "policy":policy,"receiver_decoded_history_or_null":guess,
            "injected_stale_packet":stale,
            "requery_full_ack":requery,
            "abstained":abstain,
            "wire_bits_including_epoch_and_fresh_requery":bits,
            "visible_receiver_sensor_bin":list(obs),
            "bin_in_old_training_source_union":any(
                obs in s for s in codec["known_support"].values()
            ),
            "available_trained_color_bits":codec["bits"],
            "public_pre_quat_xyzw":list(measured.quaternion_xyzw),
            "public_reset_quat_xyzw":list(reset.quaternion_xyzw),
            "post_recovery_public_quat_xyzw":list(achieved.quaternion_xyzw),
            "source_goal_quat_xyzw":list(goal.quaternion_xyzw),
            "issued_native6_correction":list(map(float,native)),
            "oracle_native6_correction_audit_only":list(map(float,correct_native)),
            "actual_action_mismatch_norm":action_error,
            "orientation_error_to_goal_rad":quaternion_angle(
                achieved.quaternion_xyzw,goal.quaternion_xyzw
            ),
            "original_official_pickcube_success_descriptive":last["official_success"],
            "no_private_controller_target_read_in_policy":True,
            "strong_prior_art_sequence_numbers_and_graph_coding":True
        }
    finally:
        if env is not None:
            env.close()


def robot_study(robot,prior_artifacts_folder):
    plan,old=registered()
    if robot not in plan["robot_ids"]:
        raise ValueError("Unregistered original robot")
    artifact=prior_artifacts_folder/(
        f"actual-native-physx-receipt-{robot}")/(
            f"physx_native_receipt_{robot}.json")
    training=json.loads(artifact.read_text(encoding="utf-8"))
    codec_by_variant={
        v:training_codec(
            training,robot,v,plan["quantizer_cell_rad"],
            plan["sensor_component_noise_support_rad"]
        )
        for v in plan["variants"]
    }
    torch.set_num_threads(1)
    rows=[]
    for seed in plan["new_reset_seeds"][robot]:
        for v in plan["variants"]:
            code=codec_by_variant[v]
            for h in HIST:
                for method in POLICIES:
                    r=one_actual_native_world(
                        old,plan,code,robot,seed,v,h,method
                    )
                    rows.append(r)
                    print("TRANSACTIONAL_PHYSX_ORIGINAL_WORLD",
                          json.dumps({
                              "robot":robot,"seed":seed,"variant":v,
                              "truth":h,"policy":method,
                              "post_angle":r["orientation_error_to_goal_rad"],
                              "bits":r["wire_bits_including_epoch_and_fresh_requery"]
                          },sort_keys=True),flush=True)
    exp={(seed,v,h,m) for seed in plan["new_reset_seeds"][robot]
         for v in plan["variants"] for h in HIST for m in POLICIES}
    got={(r["new_unseen_seed"],r["variant"],r["truth_history_audit_only"],
          r["policy"]) for r in rows}
    if len(rows)!=128 or exp!=got:
        raise RuntimeError("A true original policy world was dropped")
    seed_results={}
    for seed in plan["new_reset_seeds"][robot]:
        data=[r for r in rows if r["new_unseen_seed"]==seed]
        means={}
        for m in POLICIES:
            subset=[r for r in data if r["policy"]==m]
            assert len(subset)==8
            means[m]={
                "orientation_error_rad":sum(r["orientation_error_to_goal_rad"]
                                            for r in subset)/8,
                "mean_paid_bits":sum(
                    r["wire_bits_including_epoch_and_fresh_requery"]
                    for r in subset
                )/8,
                "wrong_native_command_count":sum(
                    r["actual_action_mismatch_norm"]>1e-6
                    for r in subset
                ),
                "requery_count":sum(r["requery_full_ack"] for r in subset),
            }
        meets=(
            means["EPOCH_GUARDED_COMPRESSED"]["orientation_error_rad"]+.001<=
            means["EPOCH_BLIND_COMPRESSED"]["orientation_error_rad"]
            and means["EPOCH_GUARDED_COMPRESSED"]["orientation_error_rad"]<=
            means["EPOCH_FULL_ACK"]["orientation_error_rad"]+.001
        )
        seed_results[str(seed)]={
            "by_policy":means,
            "passes_precommitted_error_benefit":meets
        }
    passes=sum(x["passes_precommitted_error_benefit"]
               for x in seed_results.values())
    guarded=[r for r in rows if r["policy"]=="EPOCH_GUARDED_COMPRESSED"]
    avg_bits=sum(r["wire_bits_including_epoch_and_fresh_requery"]
                 for r in guarded)/len(guarded)
    output={
        "schema":plan["schema"],"robot":robot,
        "immutable_source_prereg_git_blob":FROZEN_BLOB,
        "training_source_old_physx_run":38363869998,
        "source_train_set_only_codebook":{
            v:{"colors":list(c["colors"]),"bits":c["bits"],
               "old_training_reset_seeds":c["old_train_seeds"],
               "conflicting_edges":c["edge_count"]}
            for v,c in codec_by_variant.items()
        },
        "actual_original_worlds":128,
        "new_independent_test_reset_clusters":4,
        "injected_packet_stale_fraction":.5,
        "registered_unguarded_naive_wrong_native_action_count":sum(
            r["actual_action_mismatch_norm"]>1e-6 for r in rows
            if r["policy"]=="EPOCH_BLIND_COMPRESSED"
        ),
        "guarded_wrong_native_command_count":sum(
            r["actual_action_mismatch_norm"]>1e-6 for r in guarded
        ),
        "guarded_mean_paid_bits":avg_bits,
        "passing_new_test_cluster_count":passes,
        "robot_primary_gate_passed":passes>=3 and avg_bits<=3,
        "cluster_evaluation":seed_results,
        "full_original_physx_policy_rows":rows,
        "assumed_trusted_receiver_receipt_sender_not_physically_constructed":True,
        "not_claiming_new_network_sequence_number_or_info_theory":True,
        "not_actual_pickcube_task_success_improvement":True
    }
    name=f"transactional_physx_{robot}.json"
    Path(name).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("TRANSACTIONAL_PHYSX_FULL_ROBOT_COMPLETE",json.dumps({
        k:v for k,v in output.items()
        if k not in ("cluster_evaluation","full_original_physx_policy_rows")
    },sort_keys=True),flush=True)


if __name__=="__main__":
    x=argparse.ArgumentParser()
    x.add_argument("--robot",choices=("panda","xarm6_robotiq"),required=True)
    x.add_argument("--train",type=Path,required=True)
    args=x.parse_args()
    robot_study(args.robot,args.train)
