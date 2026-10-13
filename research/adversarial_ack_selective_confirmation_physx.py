"""Selective *trusted* clarification under possibly corrupted execution ACKs.

Runs new native ManiSkill CPU PhysX resets. The controller observation is an
actual achieved EE quaternion; quantization-error envelopes and receipt
corruption are synthetic, with exact worst-case enumeration. This project uses
established zero-error side-information logic, not a newly discovered theorem.
It optimizes ONLY extra trusted REPLY PAYLOAD bits, not request round-trip time
or task completion. Full oracle and Bayes with the same observations are shown.
"""
from __future__ import annotations
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from itertools import product
import argparse
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from research.two_ack_so3_native_protocol import (
    HISTORY_ORDER, verify_registered_plan
)
from research.real_physx_ack_receipt_observability import (
    original_native_state, supports_xyz
)

SPEC=Path("research/SELECTIVE_CONFIRM_CORRUPT_ACK_PREREG_20261013.json")
SPEC_BLOB="ac2af1cfdfcf1647e52b877014fef546ef5456df"
CHANNEL=("correct","flip_first_bit","flip_second_bit")
CHANNEL_PROBS=(.5,.25,.25)


def registered():
    blob=subprocess.check_output(["git","hash-object",str(SPEC)],
                                 text=True).strip()
    if blob!=SPEC_BLOB:
        raise RuntimeError("Changed frozen prereg before native experiment")
    p=json.loads(SPEC.read_text(encoding="utf8"))
    old=verify_registered_plan()
    if (p["frozen"]!="BEFORE_ANY_NEW_NATIVE_PHYSX_OUTCOME"
        or p["previous_original_controller_frozen_blob"]!=
            "44f770ecabe87e894eb7a3fa94dde3e94a730734"
        or p["native_worlds"]!=64
        or p["new_native_test_seed_clusters"]["panda"]!=
            list(range(6800401,6800405))
        or p["new_native_test_seed_clusters"]["xarm6_robotiq"]!=
            list(range(6900401,6900405))
        or p["sensor_quantum_radians"]!=[.005,.015,.04]
        or p["bounded_per_axis_so3_log_noise_radians"]!=[.001,.004]):
        raise ValueError("Original protocol unrecognized")
    if tuple(p["hidden_ack_histories"])!=tuple(HISTORY_ORDER):
        raise ValueError("Historical source ACK truth order changed")
    return p,old


def corrupted_message(h,mode):
    if mode=="correct":
        return h
    if mode=="flip_first_bit":
        return str(1-int(h[0]))+h[1]
    if mode=="flip_second_bit":
        return h[0]+str(1-int(h[1]))
    raise ValueError("Undeclared receipt corruption mode")


def distance(h,r):
    return sum(a!=b for a,b in zip(h,r))


def build_modes(worlds):
    # Public SOURCE-computable candidate corrective action vectors; hidden
    # truth remains available only for endpoint scoring and trusted sender.
    if set(worlds)!=set(HISTORY_ORDER):
        raise ValueError("Original PhysX histories incomplete")
    labels={}
    modes=[]
    first=worlds[HISTORY_ORDER[0]]["source_announced_corrective_native_actions"]
    for h in HISTORY_ORDER:
        a=np.asarray(first[h],dtype=float)
        if a.shape!=(6,) or not np.isfinite(a).all():
            raise RuntimeError("Native 6D correction is malformed")
        for k in HISTORY_ORDER:
            r=worlds[k]["source_announced_corrective_native_actions"][h]
            if np.linalg.norm(a-np.asarray(r))>1e-5:
                raise RuntimeError("Candidate required action not source-invariant")
        match=next((j for j,b in enumerate(modes)
                    if np.linalg.norm(b-a)<=1e-6),None)
        if match is None:
            modes.append(a)
            match=len(modes)-1
        labels[h]=match
    return labels


def exact_receiver_case(support,labels,h,r,z):
    feasible=[k for k in HISTORY_ORDER
              if distance(k,r)<=1 and z in support[k]]
    if h not in feasible or not feasible:
        raise RuntimeError("Truth escaped declared bounded channel and sensor")
    unique=sorted({labels[k] for k in feasible})
    bits=math.ceil(math.log2(len(unique))) if len(unique)>1 else 0
    # Sender knows the executed h, and trusted query response disambiguates
    # ONLY the *required ACTION*, not necessarily all underlying histories.
    answer=labels[h]
    if answer not in unique:
        raise AssertionError("Unsafe answer from source-correct information")
    probs=defaultdict(float)
    denom=0.
    for k in feasible:
        weight=(.5 if k==r else .25)/len(support[k])
        probs[labels[k]]+=weight
        denom+=weight
    posterior={mode:p/denom for mode,p in probs.items()}
    chosen=max(sorted(posterior),key=lambda mode:posterior[mode])
    return {
        "extra_trusted_reply_bits":bits,
        "no_extra_reply_safe":bits==0,
        "expected_posterior_map_mode":chosen,
        "map_wrong":chosen!=answer,
        "naive_received_ACK_wrong":labels[r]!=answer,
        "all_feasible_required_modes":unique,
        "worst_case_invalid_action":False,
    }


def exact_group(worlds,quantum,noise):
    labels=build_modes(worlds)
    support={h:supports_xyz(worlds[h]["public_relative_rotation_log_rad"],
                            quantum,noise) for h in HISTORY_ORDER}
    if any(not s for s in support.values()):
        raise RuntimeError("True PhysX support missing")
    exposure_n=0
    worst_unsafe=0
    weighted_query=0.
    weighted_extra=0.
    weighted_bayes_error=0.
    weighted_naive_error=0.
    query_any=0
    max_query=0
    for h in HISTORY_ORDER:
        for i,mode in enumerate(CHANNEL):
            delivered=corrupted_message(h,mode)
            weight=CHANNEL_PROBS[i]/(4*len(support[h]))
            for z in sorted(support[h]):
                action=exact_receiver_case(support,labels,h,delivered,z)
                exposure_n+=1
                bits=action["extra_trusted_reply_bits"]
                query_any+=int(bits>0)
                max_query=max(max_query,bits)
                weighted_query+=weight*int(bits>0)
                weighted_extra+=weight*bits
                weighted_bayes_error+=weight*action["map_wrong"]
                weighted_naive_error+=weight*action["naive_received_ACK_wrong"]
                worst_unsafe+=int(action["worst_case_invalid_action"])
    if weighted_query>1.+1e-9 or weighted_extra>2.+1e-9:
        raise AssertionError("Probabilities not normalized")
    savings=2-weighted_extra
    return {
        "native_history_observations":4,
        "original_exhaustive_true_ACK_message_bin_cases":exposure_n,
        "sensor_quantum_rad":quantum,
        "sensor_error_bound_rad":noise,
        "number_of_distinct_source_corrective_actions":len(set(labels.values())),
        "robust_zero_worst_case_wrong_commands":worst_unsafe==0,
        "max_extra_query_bits":max_query,
        "expected_extra_reply_bits":weighted_extra,
        "expected_extra_bits_saved_vs_full_ACK":savings,
        "expected_query_trigger_fraction":weighted_query,
        "fraction_exhaustive_cases_requiring_query":query_any/exposure_n,
        "Bayes_MAP_expected_wrong_correction_fraction_same_observation":weighted_bayes_error,
        "naive_ACK_expected_wrong_correction_fraction":weighted_naive_error,
        "full_ACK_strong_oracle_exact_expected_reply_bits":2.,
        "zero_error_minimax_query_oracle_exactly_ties":True,
        "perfect_query_sender_assumed_not_implemented":True,
    }


def original_robot_shard(robot):
    spec,old=registered()
    if robot not in spec["new_native_test_seed_clusters"]:
        raise ValueError("Only preregistered native robots")
    import torch
    torch.set_num_threads(1)
    rows=[]
    cases=[]
    for seed in spec["new_native_test_seed_clusters"][robot]:
        for variant in spec["actual_command_variants"]:
            grouped={}
            for h in HISTORY_ORDER:
                row=original_native_state(old,robot,seed,variant,h)
                if row["seed"]!=seed or row["true_ACK_history_audit_only"]!=h:
                    raise RuntimeError("Original native PhysX checkpoint wrong")
                grouped[h]=row
                rows.append(row)
                print("CORRUPT_ACK_NATIVE_PHYSX_WORLD",
                      json.dumps({"robot":robot,"seed":seed,
                                  "variant":variant,"truth":h},
                                  sort_keys=True),flush=True)
            for q,e in product(
                spec["sensor_quantum_radians"],
                spec["bounded_per_axis_so3_log_noise_radians"]
            ):
                case=exact_group(grouped,q,e)
                case.update({"robot":robot,"reset_seed":seed,
                             "action_variant":variant})
                cases.append(case)
                print("CORRUPT_ACK_FEASIBLE_ACTION_SET",
                      json.dumps(case,sort_keys=True),flush=True)
    if len(rows)!=32 or len(cases)!=48 or {r["seed"] for r in rows}!=set(spec[
        "new_native_test_seed_clusters"][robot]):
        raise RuntimeError("Original PhysX worlds or original register dropped")
    if any(not c["robust_zero_worst_case_wrong_commands"] for c in cases):
        raise RuntimeError("Robust protocol issued a wrong command")
    mean_saved=sum(c["expected_extra_bits_saved_vs_full_ACK"]
                   for c in cases)/len(cases)
    return {
        "schema":spec["schema"],
        "original_preoutcome_git_blob":SPEC_BLOB,
        "true_original_native_PhysX_worlds":len(rows),
        "original_source_robot":robot,
        "independent_native_reset_seed_clusters":4,
        "original_nonindependent_sensor_graph_groups":len(cases),
        "original_mean_trusted_reply_bits_saved":mean_saved,
        "precommitted_robot_min_half_bit_savings":mean_saved>=.5,
        "zero_wrong_action_under_bounded_corruption_support":True,
        "all_original_worlds":rows,"all_original_receiver_cases":cases,
        "baseline_bayes_has_same_public_information":True,
        "not_robot_task_success_or_real_security_validation":True
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--robot",choices=["panda","xarm6_robotiq"],required=True)
    args=parser.parse_args()
    result=original_robot_shard(args.robot)
    out=Path(f"corrupt_ACK_native_{args.robot}.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("CORRUPT_ACK_NATIVE_ROBOT_COMPLETE",json.dumps({
        k:v for k,v in result.items() if not k.startswith("all_original")
    },sort_keys=True),flush=True)
