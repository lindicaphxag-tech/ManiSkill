"""Real CPU PhysX public-observation ACK receipt audit.

64 native ManiSkill PickCube-v1 worlds (two truly different robot controller
interfaces, eight new registered reset seeds total, 2 announced native action
variants, four true ACK histories). Receipt side-information optimization is
EXACT but is established graph theory. Task-level grasp success is NOT tested.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from scipy.spatial.transform import Rotation
import torch

from research.two_ack_so3_native_protocol import (
    HISTORY_ORDER,
    correction_from_history_so3,
    setup_public_two_ack_world,
    verify_registered_plan,
)
from research.zero_error_execution_receipt import (
    bayes_accuracy,conflict_graph,dsatur_coloring,receipt_decoder,
)

PLAN=Path("research/PHYSX_REAL_ACK_RECEIPT_PREREG_20261013.json")
PLAN_BLOB="ece6ee56331c5855e6362c5505c8d145bdb968c3"


def load_native_protocol():
    sha=subprocess.check_output(["git","hash-object",str(PLAN)],
                                text=True).strip()
    if sha!=PLAN_BLOB:
        raise RuntimeError("New PhysX experiment design changed after freeze")
    plan=json.loads(PLAN.read_text(encoding="utf-8"))
    old=verify_registered_plan() # validates independent previously frozen source
    if (plan["status"]!="FROZEN_BEFORE_NATIVE_PHYSX_OUTCOMES"
        or plan["robots"]!=old["robots"]
        or plan["action_variants"]!=list(old["action_variants"])
        or plan["histories"]!=list(HISTORY_ORDER)
        or plan["original_native_PhysX_worlds"]!=64
        or plan["sensor_cell_radians"]!=[.005,.015,.04]
        or plan["independent_sensor_component_error_bounds_radians"]!=[.001,.004]):
        raise RuntimeError("Unregistered PhysX original controller or sensor study")
    return plan,old


def original_native_state(old,robot,seed,variant,h):
    # Prior source helper validates original controller chart and agent type.
    # The only change to source helper's accepted reset IDs is an **explicit
    # prospective validation ID**, not an alteration to prior heldout data.
    cfg=deepcopy(old)
    cfg["heldout_seeds"][robot].append(seed)
    env=None
    try:
        env,controller,arm,reset,measured,candidates=(
            setup_public_two_ack_world(cfg,robot,seed,variant,h)
        )
        # Public achieved EE geometry, minus public achieved reset pose.
        achieved=Rotation.from_quat(measured.quaternion_xyzw)
        initial=Rotation.from_quat(reset.quaternion_xyzw)
        feature=(achieved*initial.inv()).as_rotvec()
        if not np.isfinite(feature).all():
            raise RuntimeError("Original native PhysX generated nonfinite pose")
        # Encoder knows its actually executed ACK *only* to send trusted tag.
        # These are model-computable hypothetical future corrective controls.
        future={}
        for history in HISTORY_ORDER:
            native=correction_from_history_so3(
                arm,candidates[history],candidates["11"]
            )
            future[history]=[float(x) for x in native]
        return {
            "robot":robot,"seed":seed,"variant":variant,
            "true_ACK_history_audit_only":h,
            "public_reset_quaternion_xyzw":list(reset.quaternion_xyzw),
            "public_measured_quaternion_xyzw":list(measured.quaternion_xyzw),
            "public_relative_rotation_log_rad":feature.tolist(),
            "source_announced_corrective_native_actions":future,
            "trusted_sender_knows_actual_history":True,
            "model_did_not_consult_private_controller_target":True,
        }
    finally:
        if env is not None:
            env.close()


def supports_xyz(point,q,err):
    """Exhaustive bounded-error quantizer support in three exact rational axes."""
    out=[]
    for v in point:
        x=Fraction(str(round(float(v),12)))
        quantum=Fraction(str(q))
        epsilon=Fraction(str(err))
        indices=range(math.floor((x-epsilon)/quantum),
                      math.floor((x+epsilon)/quantum)+1)
        out.append(tuple(indices))
    support=frozenset(product(*out))
    if not support or len(support)>64:
        raise RuntimeError("Sensor quantization model outside registered support")
    return support


def analyse_real_robot_group(original_worlds,q,err):
    if set(original_worlds)!=set(HISTORY_ORDER):
        raise RuntimeError("True ACK histories dropped from native experiments")
    # Every native world is reset to the same seed + prefix, so the
    # source-announced candidate corrections must agree across truths.
    raw={
        h:original_worlds["00"]["source_announced_corrective_native_actions"][h]
        for h in HISTORY_ORDER
    }
    for truth in HISTORY_ORDER:
        for h in HISTORY_ORDER:
            actual=np.array(original_worlds[truth][
                "source_announced_corrective_native_actions"][h])
            want=np.array(raw[h])
            if np.linalg.norm(actual-want)>1e-5:
                raise RuntimeError("Source predictions vary across true ACK worlds")
    labels={}
    reference=[]
    for h in HISTORY_ORDER:
        v=np.asarray(raw[h],dtype=float)
        matching=[i for i,other in enumerate(reference)
                  if np.linalg.norm(v-other)<=1e-6]
        if not matching:
            reference.append(v)
            labels[h]=len(reference)-1
        else:
            labels[h]=matching[0]
    sensor={
        h:supports_xyz(
            original_worlds[h]["public_relative_rotation_log_rad"],q,err
        ) for h in HISTORY_ORDER
    }
    # Historical graph solver index order corresponds to 00, 01, 10, 11.
    anchor={i:labels[h] for i,h in enumerate(HISTORY_ORDER)}
    support={i:sensor[h] for i,h in enumerate(HISTORY_ORDER)}
    g=conflict_graph(anchor,support)
    code,k=dsatur_coloring(g)
    _,errors=receipt_decoder(anchor,support,code)
    if errors:
        raise RuntimeError("Unsafe receipt on actual native PhysX public EE data")
    bits=math.ceil(math.log2(k)) if k>1 else 0
    count_receipt={i:h.count("1") for i,h in enumerate(HISTORY_ORDER)}
    return {
        "sensor_quantization_rad":q,"sensor_bounded_error_rad":err,
        "original_4_PhysX_observation_worlds":4,
        "number_of_native_correction_modes":len(reference),
        "minimum_fixed_receipt_bits":bits,
        "full_ack_bits":2,
        "saved_bits":2-bits,
        "exact_conflicting_history_edges":sum(x.bit_count() for x in g)//2,
        "no_receipt_bayes_correct_under_synthetic_support_prior":
            bayes_accuracy(anchor,support),
        "popcount_bayes_correct_under_same_support_prior":
            bayes_accuracy(anchor,support,count_receipt),
        "minimal_receipt_bayes_correct_under_same_support_prior":
            bayes_accuracy(anchor,support,dict(enumerate(code))),
        "zero_confusion_for_any_supported_quantization":errors==0,
        "not_actual_robot_hardware_or_task_success":True
    }


def original_robot_shard(robot):
    plan,old=load_native_protocol()
    if robot not in plan["robots"]:
        raise ValueError("Unregistered robot")
    torch.set_num_threads(1)
    all_worlds=[]
    groups=[]
    for seed in plan["seeds"][robot]:
        for variant in plan["action_variants"]:
            group={}
            for h in HISTORY_ORDER:
                row=original_native_state(old,robot,seed,variant,h)
                group[h]=row
                all_worlds.append(row)
                print("RECEIPT_NATIVE_PHYSX_WORLD",
                      json.dumps({"robot":robot,"seed":seed,
                                  "variant":variant,"truth":h},
                                  sort_keys=True),flush=True)
            for q in plan["sensor_cell_radians"]:
                for err in plan["independent_sensor_component_error_bounds_radians"]:
                    e=analyse_real_robot_group(group,q,err)
                    e.update({"robot":robot,"seed":seed,"variant":variant})
                    groups.append(e)
                    print("RECEIPT_NATIVE_PHYSX_GRAPH",
                          json.dumps(e,sort_keys=True),flush=True)
    expected_world={(seed,variant,h)
        for seed in plan["seeds"][robot]
        for variant in plan["action_variants"] for h in HISTORY_ORDER}
    actual_world={(x["seed"],x["variant"],x["true_ACK_history_audit_only"])
                  for x in all_worlds}
    if expected_world!=actual_world or len(all_worlds)!=32 or len(groups)!=48:
        raise RuntimeError("Missing original PhysX world or receipt graph cell")
    saved=sum(x["saved_bits"]>=1 for x in groups)
    return {
        "schema":plan["schema"],
        "preoutcome_protocol_git_blob":PLAN_BLOB,
        "original_native_robot":robot,
        "independent_reset_clusters":4,
        "native_worlds":32,
        "original_nonindependent_sensor_parameter_graph_cases":48,
        "one_or_more_bits_saved_graph_count":saved,
        "zero_alias_decision_errors":all(
            x["zero_confusion_for_any_supported_quantization"] for x in groups
        ),
        "all_worlds":all_worlds,"all_sensor_receipt_graphs":groups,
        "native_physx_cpu_not_hardware":True,
        "no_pickcube_task_success_claim":True,
        "known_graph_coding_prior_art":True,
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--robot",required=True,choices=["panda","xarm6_robotiq"])
    args=ap.parse_args()
    summary=original_robot_shard(args.robot)
    out=Path(f"physx_native_receipt_{args.robot}.json")
    out.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("RECEIPT_NATIVE_PHYSX_SHARD_COMPLETE",json.dumps({
        k:v for k,v in summary.items()
        if k not in ("all_worlds","all_sensor_receipt_graphs")
    },sort_keys=True),flush=True)
