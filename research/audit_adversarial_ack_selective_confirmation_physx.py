"""Independent source-artifact audit: corrupted ACK, native PhysX, query cost.

Reconstructs exact robot sensor supports, candidate corrective actions, posterior
and reply payload from ORIGINAL PhysX fields, without importing or invoking
the principal policy/query functions. This is independent CODE verification,
not an independent research institution, a safety certification or grasp task.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from scipy.spatial.transform import Rotation

PLAN=Path("research/SELECTIVE_CONFIRM_CORRUPT_ACK_PREREG_20261013.json")
PLAN_HASH="ac2af1cfdfcf1647e52b877014fef546ef5456df"
ORIGINAL_RUN=38376280332
TRUTHS=("00","01","10","11")
ROBOTS=("panda","xarm6_robotiq")


def observed_bins(vec,grid,bound):
    step=Fraction(str(grid))
    epsilon=Fraction(str(bound))
    axes=[]
    for v in vec:
        vv=Fraction(str(round(float(v),12)))
        axes.append(range(
            math.floor((vv-epsilon)/step),
            math.floor((vv+epsilon)/step)+1
        ))
    return set(product(*axes))


def materialized_modes(group):
    possible=group["00"]["source_announced_corrective_native_actions"]
    labels={}
    controls=[]
    for h in TRUTHS:
        x=np.asarray(possible[h],dtype=float)
        if x.shape!=(6,) or not np.isfinite(x).all():
            raise RuntimeError("Source-reported native6D correction invalid")
        equal=next((i for i,v in enumerate(controls)
                    if np.linalg.norm(x-v)<=1e-6),None)
        if equal is None:
            controls.append(x)
            equal=len(controls)-1
        labels[h]=equal
        for truth in TRUTHS:
            other=np.asarray(group[truth][
                "source_announced_corrective_native_actions"][h],dtype=float)
            if np.linalg.norm(other-x)>1e-5:
                raise RuntimeError("Truth-dependent source-correct control impossible")
    return labels


def independent_cell(group,grid,bound):
    modes=materialized_modes(group)
    visible={h:observed_bins(group[h]["public_relative_rotation_log_rad"],
                             grid,bound)
             for h in TRUTHS}
    total_bits=0.
    total_bayes_loss=0.
    total_naive_loss=0.
    total_query=0.
    n_exposures=0
    for h in TRUTHS:
        for message_i in (0,1,2):
            receipt=(h if message_i==0 else
                     str(1-int(h[0]))+h[1] if message_i==1 else
                     h[0]+str(1-int(h[1])))
            prior=(.5,.25,.25)[message_i]
            for obs in visible[h]:
                compatible=[
                    k for k in TRUTHS
                    if sum(int(a!=b) for a,b in zip(k,receipt))<=1
                    and obs in visible[k]
                ]
                if h not in compatible:
                    raise AssertionError("True executed ACK omitted by noisy channel")
                needed={modes[k] for k in compatible}
                reply_len=math.ceil(math.log2(len(needed))) if len(needed)>1 else 0
                mass=defaultdict(float)
                for k in compatible:
                    message_prob=(.5 if k==receipt else .25)
                    mass[modes[k]]+=message_prob/len(visible[k])
                chosen=max(sorted(mass),key=lambda mode:mass[mode])
                weight=prior/(4*len(visible[h]))
                total_bits+=weight*reply_len
                total_query+=weight*int(reply_len>0)
                total_bayes_loss+=weight*int(chosen!=modes[h])
                total_naive_loss+=weight*int(modes[receipt]!=modes[h])
                n_exposures+=1
    if total_bayes_loss > total_naive_loss+1e-12:
        raise RuntimeError("Bayes-MAP with same observations worse than naive")
    return dict(
        original_exhaustive_true_ACK_message_bin_cases=n_exposures,
        number_of_distinct_source_corrective_actions=len(set(modes.values())),
        expected_extra_reply_bits=total_bits,
        expected_extra_bits_saved_vs_full_ACK=2.-total_bits,
        expected_query_trigger_fraction=total_query,
        Bayes_MAP_expected_wrong_correction_fraction_same_observation=total_bayes_loss,
        naive_ACK_expected_wrong_correction_fraction=total_naive_loss,
        robust_zero_worst_case_wrong_commands=True
    )


def audit(path):
    actual=subprocess.check_output(["git","hash-object",str(PLAN)],
                                   text=True).strip()
    if actual!=PLAN_HASH:
        raise RuntimeError("Primary model or test set original preregistration changed")
    p=json.loads(PLAN.read_text(encoding="utf8"))
    results={}
    means={}
    for robot in ROBOTS:
        src=path/f"unseen-native-corrupt-ACK-{robot}"/f"corrupt_ACK_native_{robot}.json"
        data=json.loads(src.read_text(encoding="utf8"))
        if (
            data["schema"]!=p["schema"]
            or data["original_preoutcome_git_blob"]!=PLAN_HASH
            or data["original_source_robot"]!=robot
            or data["true_original_native_PhysX_worlds"]!=32
            or data["original_nonindependent_sensor_graph_groups"]!=48
        ):
            raise RuntimeError("Original sharded PhysX denominator/provenance wrong")
        worlds=data["all_original_worlds"]
        cases=data["all_original_receiver_cases"]
        expected={(seed,variant,h)
                  for seed in p["new_native_test_seed_clusters"][robot]
                  for variant in p["actual_command_variants"] for h in TRUTHS}
        if (
            len(worlds)!=32
            or {(w["seed"],w["variant"],w["true_ACK_history_audit_only"])
                for w in worlds}!=expected
            or len(cases)!=48
        ):
            raise RuntimeError("Original native robot environment dropped or duplicated")
        groups=defaultdict(dict)
        for w in worlds:
            reset=Rotation.from_quat(w["public_reset_quaternion_xyzw"])
            measured=Rotation.from_quat(w["public_measured_quaternion_xyzw"])
            computed=(measured*reset.inv()).as_rotvec()
            if not np.allclose(computed,w["public_relative_rotation_log_rad"],
                               rtol=0,atol=1e-8):
                raise RuntimeError("Original public PhysX achieved pose inconsistent")
            if not w["model_did_not_consult_private_controller_target"]:
                raise RuntimeError("Policy accessed a forbidden controller getter")
            groups[w["seed"],w["variant"]][w["true_ACK_history_audit_only"]]=w
        required=set(product(
            p["new_native_test_seed_clusters"][robot],
            p["actual_command_variants"],p["sensor_quantum_radians"],
            p["bounded_per_axis_so3_log_noise_radians"]
        ))
        got={(x["reset_seed"],x["action_variant"],
              x["sensor_quantum_rad"],x["sensor_error_bound_rad"])
             for x in cases}
        if len(got)!=48 or got!=required:
            raise RuntimeError("Original PhysX sensor corruption grid incomplete")
        for case in cases:
            key=(case["reset_seed"],case["action_variant"])
            graph=groups[key]
            if set(graph)!=set(TRUTHS):
                raise RuntimeError("Original true ACK histories absent")
            check=independent_cell(graph,case["sensor_quantum_rad"],
                                   case["sensor_error_bound_rad"])
            for k,value in check.items():
                claimed=case[k]
                if isinstance(value,bool):
                    if claimed is not value:
                        raise RuntimeError("Unsafe false-source decision")
                elif isinstance(value,int):
                    if claimed!=value:
                        raise RuntimeError(f"Source count mismatch {k}")
                elif abs(claimed-value)>1e-10:
                    raise RuntimeError(f"Changed original query/baseline value: {k}")
        mean=float(np.mean([x["expected_extra_bits_saved_vs_full_ACK"]
                            for x in cases]))
        if abs(mean-data["original_mean_trusted_reply_bits_saved"])>1e-10:
            raise RuntimeError("Primary mean not original artifact-derived")
        results[robot]={
            "independent_original_reset_seed_clusters":4,
            "original_native_physx_worlds":32,
            "original_corruptACK_sensor_groups":48,
            "mean_extra_reply_payload_bits_saved":mean,
            "original_declared_positive_gate":mean>=.5,
            "recalculated_Bayes_mean_wrong_fraction":float(np.mean([
                x["Bayes_MAP_expected_wrong_correction_fraction_same_observation"]
                for x in cases
            ])),
            "recalculated_bounded_safety_violations":0,
        }
        means[robot]=mean
    return {
        "schema":"independent_actual_native_physx_corrupt_ACK_audit_v1",
        "original_physx_run":ORIGINAL_RUN,
        "source_prereg_blob":PLAN_HASH,
        "fully_verified_actual_native_worlds":64,
        "two_robot_independent_reset_clusters":8,
        "fully_verified_original_grid_scenarios":96,
        "original_full_bounded_receipt_exposures_verified":True,
        "actually_signed_authenticated_sender":False,
        "feedback_query_cost_included":False,
        "native_task_success_measured":False,
        "both_robot_means_at_least_half_bit":all(v>=.5 for v in means.values()),
        "robot_results":results,
        "mathematical_approach_prior_art":True,
        "external_third_party_academic_review":False,
    }


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    x=audit(args.source)
    args.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("INDEPENDENT_NEW_PHYSX_CORRUPT_ACK_AUDIT",
          json.dumps(x,sort_keys=True),flush=True)
