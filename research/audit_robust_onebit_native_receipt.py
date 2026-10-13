"""Independent auditor of *new* Panda/xArm6 native 1-bit robust receipts.

Does not import producer algorithm, its quantizer, or binary code search.
Uses raw original native quaternions and original 6D controller candidate
commands from artifacts; reconstructs confusability with rational bounds.
Mathematically derives minimum 0/3/5 bits for n=4 under 1-bit worst-case
corruption, using classical finite Hamming code distance facts.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from scipy.spatial.transform import Rotation


PLAN=Path("research/NATIVE_ONEBIT_ROBUST_RECEIPT_PREREG_20261013.json")
BLOB="53a4429f786e01a69670d61202da921fcc993f5a"
ROBOT_NAMES=("panda","xarm6_robotiq")
TRUTHS=("00","01","10","11")


def independent_sensor_support(quat,reset,cell,err):
    current=Rotation.from_quat(quat)
    start=Rotation.from_quat(reset)
    relative=(current*start.inv()).as_rotvec()
    axes=[]
    for coordinate in relative:
        v=Fraction(str(round(float(coordinate),12)))
        q=Fraction(str(cell))
        e=Fraction(str(err))
        axes.append(tuple(range(
            math.floor((v-e)/q),math.floor((v+e)/q)+1
        )))
    return frozenset(product(*axes))


def minimal_1bit_robust_receipt_bits_4states(adj):
    """New derivation route (not the producer's search) for all four-node graphs.

    No edges => one zero-length codeword.
    Edges but triangle-free => bipartite (all <=4-vertex graphs), code
    {000,111} can encode its two colors, and one edge requires >=3 bits.
    Triangle => at least 3 codewords mutually Hamming distance >=3.
    Binary length <=4 has at most 2 such codewords; binary length=5 has
    four d3 codewords, so five bits are necessary/sufficient.
    """
    n=len(adj)
    if n!=4:
        raise ValueError("Only registered 4 ACK alternatives supported")
    if all(len(neighbors)==0 for neighbors in adj):
        return 0
    triangle=any(j in adj[i] and k in adj[i] and k in adj[j]
                 for i in range(4) for j in range(i+1,4)
                 for k in range(j+1,4))
    return 5 if triangle else 3


def audit(originals):
    blob=subprocess.check_output(
        ["git","hash-object",str(PLAN)],text=True
    ).strip()
    if blob!=BLOB:
        raise AssertionError("Registered prospective native receipt changed")
    spec=json.loads(PLAN.read_text(encoding="utf-8"))
    per_robot={}
    total_cases=0
    for robot in ROBOT_NAMES:
        file=originals/f"fresh-original-native-onebit-{robot}"/(
            f"original_onebit_robust_{robot}.json")
        result=json.loads(file.read_text(encoding="utf-8"))
        if (result["schema"]!=spec["schema"]
            or result["prereg_git_blob"]!=BLOB
            or result["actual_new_native_robot"]!=robot
            or result["original_PhysX_worlds"]!=32
            or result["original_sensor_graphs"]!=48
            or result["independent_reset_clusters"]!=4):
            raise AssertionError("Reported original PhysX robot denominator altered")
        worlds=result["all_worlds"]
        conditions=result["all_sensor_cases"]
        true_ids={(w["seed"],w["variant"],
                   w["true_ACK_history_audit_only"]) for w in worlds}
        want_ids=set(product(spec["new_reset_seeds"][robot],
                             spec["variants"],TRUTHS))
        if len(worlds)!=32 or true_ids!=want_ids:
            raise AssertionError("New heldout robot seed/variant/history missing")
        cell_index={
            (r["reset_seed"],r["variant"],
             r["sensor_cell_rad"],r["sensor_bound_rad"]):r
            for r in conditions
        }
        expected_cells=set(product(
            spec["new_reset_seeds"][robot],spec["variants"],
            spec["quantizers_rad"],
            spec["bounded_component_noise_rad"]
        ))
        if len(cell_index)!=48 or set(cell_index)!=expected_cells:
            raise AssertionError("Original native corruption/sensor factorial incomplete")
        for seed,variant in product(
            spec["new_reset_seeds"][robot],spec["variants"]
        ):
            by_truth={r["true_ACK_history_audit_only"]:r
                      for r in worlds if r["seed"]==seed
                      and r["variant"]==variant}
            if set(by_truth)!=set(TRUTHS):
                raise AssertionError("One actual executable history absent")
            for w in by_truth.values():
                if (not w["model_did_not_consult_private_controller_target"]
                    or not w["trusted_sender_knows_actual_history"]):
                    raise AssertionError("Original information-boundary violated")
            actions=[np.asarray(by_truth["00"][
                "source_announced_corrective_native_actions"][h],dtype=float)
                for h in TRUTHS]
            for actual in by_truth.values():
                for i,h in enumerate(TRUTHS):
                    if np.linalg.norm(
                        np.asarray(actual["source_announced_corrective_native_actions"][h])
                        -actions[i]
                    )>1e-5:
                        raise AssertionError("Source hypothesis changed with hidden history")
            equivalent=[]
            for c in actions:
                if not np.isfinite(c).all() or c.shape!=(6,):
                    raise AssertionError("Controller did not declare a finite 6D action")
                label=next((i for i,x in enumerate(equivalent)
                            if np.linalg.norm(c-x)<=1e-6),None)
                if label is None:
                    equivalent.append(c)
            label_by_history={}
            for h,c in zip(TRUTHS,actions):
                label_by_history[h]=next(i for i,x in enumerate(equivalent)
                    if np.linalg.norm(c-x)<=1e-6)
            for cell,err in product(spec["quantizers_rad"],
                                    spec["bounded_component_noise_rad"]):
                obs={h:independent_sensor_support(
                    by_truth[h]["public_measured_quaternion_xyzw"],
                    by_truth[h]["public_reset_quaternion_xyzw"],
                    cell,err
                ) for h in TRUTHS}
                adj=[set() for _ in range(4)]
                for i in range(4):
                    for j in range(i+1,4):
                        if (label_by_history[TRUTHS[i]] !=
                            label_by_history[TRUTHS[j]] and
                            bool(obs[TRUTHS[i]] & obs[TRUTHS[j]])):
                            adj[i].add(j);adj[j].add(i)
                minimum=minimal_1bit_robust_receipt_bits_4states(adj)
                rec=cell_index[seed,variant,cell,err]
                if (
                    rec["onebit_safe_minimal_receipt_bits"]!=minimum
                    or rec["optimal_full_four_history_onebit_safe_baseline_bits"]!=5
                    or rec["source_corrected_bitrate_savings_bits"]!=5-minimum
                    or rec["native_correction_action_modes"]!=len(equivalent)
                    or rec["native_support_conflict_edges"]!=
                        sum(len(s) for s in adj)//2
                    or rec["universal_onebit_unsafe_decisions"]!=0
                    or rec["full_ack_onebit_unsafe_decisions"]!=0
                ):
                    raise AssertionError("Independently derived source/control/coding result mismatch")
                total_cases+=1
        saved=sum(r["source_corrected_bitrate_savings_bits"]>=2
                  for r in conditions)
        if saved!=result["graph_conditions_saving_two_or_more_bits"]:
            raise AssertionError("Original robot summary not supported by evidence")
        per_robot[robot]={"original_new_native_worlds":32,
                          "original_graph_cases":48,
                          "strict_two_or_more_bit_saving_cases":saved}
    successes=sum(r["strict_two_or_more_bit_saving_cases"]
                  for r in per_robot.values())
    if total_cases!=96:
        raise AssertionError("Original complete native sample size missing")
    return {
        "schema":"independent_onebit_robust_receipt_original_physx_audit_v1",
        "preoutcome_original_plan_blob":BLOB,
        "original_physx_worlds":64,
        "original_independent_reset_clusters":8,
        "original_quantisers_and_error_cases":96,
        "independent_recomputed_robust_minimum_cases":96,
        "no_unsafe_decisions_under_single_corrupt_bit":True,
        "using_strong_optimal_protected_full_ACK_5bit_baseline":True,
        "saved_at_least_2bits_total_cases":successes,
        "prospective_full_gate_passed":(
            successes>=48 and all(
                r["strict_two_or_more_bit_saving_cases"]>=16
                for r in per_robot.values()
            )
        ),
        "robots":per_robot,
        "not_external_lab_replication":True,
        "zero_error_source_channel_coding_is_prior_art":True,
        "no_PickCube_task_or_hardware_success_claim":True,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--originals",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    opts=parser.parse_args()
    result=audit(opts.originals)
    opts.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                        encoding="utf-8")
    print("INDEPENDENT_ROBUST_NATIVE_RECEIPT_AUDIT",
          json.dumps(result,sort_keys=True),flush=True)
