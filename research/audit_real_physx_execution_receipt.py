"""Independent native PhysX original-controller receipt artifact census.

This does not import the policy's graph, Bayesian posterior, quantization, or
coloring code. It independently rebuilds exact finite receipt graphs from
reported ORIGINAL real PhysX quaternion observations and native source-valid
correction commands, using the preregistered bounded quantizer. Reuses the
same robot worlds, so not outside-lab replication. No grasp success claim.
"""
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

PLAN=Path("research/PHYSX_REAL_ACK_RECEIPT_PREREG_20261013.json")
BLOB="ece6ee56331c5855e6362c5505c8d145bdb968c3"
TRUTHS=("00","01","10","11")
ROBOTS=("panda","xarm6_robotiq")
RUN=38363869998


def possible_observations(log_rotation,cell,noise):
    q=Fraction(str(cell))
    e=Fraction(str(noise))
    bins=[]
    for component in log_rotation:
        x=Fraction(str(round(float(component),12)))
        bins.append(range(
            math.floor((x-e)/q),
            math.floor((x+e)/q)+1
        ))
    return set(product(*bins))


def independent_min_colors(adjacency):
    n=len(adjacency)
    if n!=4:
        raise ValueError("Original four-state controller register missing")
    for colors in range(1,n+1):
        if any(all(
            assignment[i]!=assignment[j]
            for i in range(n) for j in range(i+1,n)
            if j in adjacency[i]
        ) for assignment in product(range(colors),repeat=n)):
            return colors
    raise AssertionError("No safe full ACK coloring")


def audit_original_json(folder):
    digest=subprocess.check_output(
        ["git","hash-object",str(PLAN)],text=True
    ).strip()
    if digest!=BLOB:
        raise RuntimeError("Prospective original native PhysX source changed")
    plan=json.loads(PLAN.read_text(encoding="utf-8"))
    per_robot={}
    all_groups=[]
    original_poses=[]
    for robot in ROBOTS:
        path=folder/f"actual-native-physx-receipt-{robot}"/(
            f"physx_native_receipt_{robot}.json")
        raw=path.read_bytes()
        data=json.loads(raw.decode("utf-8"))
        if (data["preoutcome_protocol_git_blob"]!=BLOB
            or data["original_native_robot"]!=robot
            or data["native_worlds"]!=32
            or data["original_nonindependent_sensor_parameter_graph_cases"]!=48):
            raise RuntimeError("Incomplete source PhysX robot artifact")
        worlds=data["all_worlds"]
        graphs=data["all_sensor_receipt_graphs"]
        if len(worlds)!=32 or len(graphs)!=48:
            raise RuntimeError("One native physics world or sensor condition dropped")
        expected={(seed,variant,h)
                  for seed in plan["seeds"][robot]
                  for variant in plan["action_variants"] for h in TRUTHS}
        seen={(w["seed"],w["variant"],w["true_ACK_history_audit_only"])
              for w in worlds}
        if seen!=expected:
            raise RuntimeError("Robot reset seed/variant/ACK truth denominator wrong")
        for w in worlds:
            reset=Rotation.from_quat(w["public_reset_quaternion_xyzw"])
            after=Rotation.from_quat(w["public_measured_quaternion_xyzw"])
            computed=(after*reset.inv()).as_rotvec()
            if not np.allclose(computed,w["public_relative_rotation_log_rad"],
                               rtol=0,atol=1e-8):
                raise AssertionError("Public native pose rotation does not reconstruct")
            if (not w["model_did_not_consult_private_controller_target"]
                or not w["trusted_sender_knows_actual_history"]):
                raise RuntimeError("Forbidden privileged getter/unknown receipt sender")
            original_poses.append(w)
        graph_index={(r["seed"],r["variant"],
                      r["sensor_quantization_rad"],r["sensor_bounded_error_rad"]):r
                     for r in graphs}
        required=set(product(
            plan["seeds"][robot],plan["action_variants"],
            plan["sensor_cell_radians"],
            plan["independent_sensor_component_error_bounds_radians"],
        ))
        if len(graph_index)!=48 or set(graph_index)!=required:
            raise RuntimeError("Original native sensor factorial incomplete")
        for seed,variant in product(plan["seeds"][robot],plan["action_variants"]):
            matching={w["true_ACK_history_audit_only"]:w for w in worlds
                      if w["seed"]==seed and w["variant"]==variant}
            if set(matching)!=set(TRUTHS):
                raise RuntimeError("Absent original controller state")
            actions={h:np.asarray(
                matching["00"]["source_announced_corrective_native_actions"][h],
                dtype=float
            ) for h in TRUTHS}
            labels={}
            unique=[]
            for h in TRUTHS:
                a=actions[h]
                if not np.isfinite(a).all() or a.shape!=(6,):
                    raise RuntimeError("Not actual 6D native corrective action")
                idx=next((j for j,u in enumerate(unique)
                          if np.linalg.norm(a-u)<=1e-6),None)
                if idx is None:
                    unique.append(a)
                    idx=len(unique)-1
                labels[h]=idx
                for other in TRUTHS:
                    b=matching[other][
                        "source_announced_corrective_native_actions"][h]
                    if np.linalg.norm(a-np.asarray(b))>1e-5:
                        raise RuntimeError("Native corrective source depends on hidden truth")
            for cell,noise in product(
                plan["sensor_cell_radians"],
                plan["independent_sensor_component_error_bounds_radians"]
            ):
                g=graph_index[seed,variant,cell,noise]
                possible={
                    h:possible_observations(
                        matching[h]["public_relative_rotation_log_rad"],cell,noise
                    ) for h in TRUTHS
                }
                adjacency=[set() for _ in TRUTHS]
                for i in range(4):
                    for j in range(i+1,4):
                        h,k=TRUTHS[i],TRUTHS[j]
                        if labels[h]!=labels[k] and possible[h]&possible[k]:
                            adjacency[i].add(j)
                            adjacency[j].add(i)
                chi=independent_min_colors(adjacency)
                saved=2-(math.ceil(math.log2(chi)) if chi>1 else 0)
                if (g["minimum_fixed_receipt_bits"]!=2-saved
                    or g["saved_bits"]!=saved
                    or g["number_of_native_correction_modes"]!=len(unique)
                    or g["exact_conflicting_history_edges"]!=
                       sum(map(len,adjacency))//2
                    or not g["zero_confusion_for_any_supported_quantization"]
                    or abs(g["minimal_receipt_bayes_correct_under_same_support_prior"]-1)>1e-12):
                    raise AssertionError("Claimed native sensor/receipt certificate is wrong")
                all_groups.append(g)
        successful=sum(g["saved_bits"]>=1 for g in graphs)
        if successful!=data["one_or_more_bits_saved_graph_count"]:
            raise AssertionError("Reported native per-robot bit saving incorrect")
        per_robot[robot]={
            "original_native_PhysX_worlds":len(worlds),
            "original_quantizer_graphs":len(graphs),
            "cases_which_save_at_least_one_bit":successful,
            "sha256_original_worker_artifact":hashlib.sha256(raw).hexdigest(),
        }
    success=sum(r["cases_which_save_at_least_one_bit"]
                for r in per_robot.values())
    source_safe=all(g["zero_confusion_for_any_supported_quantization"]
                    for g in all_groups)
    if len(all_groups)!=96 or len(original_poses)!=64 or not source_safe:
        raise AssertionError("Incomplete native physical-source denominator")
    return {
        "schema":"original_native_physx_execution_receipt_independent_audit_v1",
        "source_native_physx_workflow":RUN,
        "actual_original_native_PhysX_worlds":64,
        "original_reset_clusters":8,
        "original_sensor_graphs":96,
        "minimum_fixed_receipt_code_independently_brute_verified":96,
        "no_ambiguous_correction_under_registered_bounded_noise":True,
        "cases_save_at_least_one_bit":success,
        "precommitted_both_robot_gate_passed":(
            success>=48 and all(x["cases_which_save_at_least_one_bit"]>=16
                                for x in per_robot.values())
        ),
        "robots":per_robot,
        "originally_precommitted_protocol_git_blob":BLOB,
        "native_simulation_not_real_hardware":True,
        "no_official_pickcube_success_gain":True,
        "graph_coloring_information_theory_is_prior_art":True,
        "not_outside_lab_validation":True,
    }


if __name__=="__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("--originals",type=Path,required=True)
    arg.add_argument("--output",type=Path,required=True)
    args=arg.parse_args()
    result=audit_original_json(args.originals)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("NATIVE_RECEIPT_INDEPENDENT_PHYSX_AUDIT",
          json.dumps(result,sort_keys=True),flush=True)
