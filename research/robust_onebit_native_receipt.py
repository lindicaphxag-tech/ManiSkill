"""Native PhysX exact minimum single-bit-corruption-safe execution receipts.

Graph homomorphism to binary Hamming distance >=3 codewords is classical
source-channel coding (not novel mathematics); specific action-contract
experiment runs NEW frozen native Panda and xArm6 PhysX controller worlds.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
import math
from pathlib import Path
import subprocess
import numpy as np
import torch

from research.real_physx_ack_receipt_observability import (
    HISTORY_ORDER,load_native_protocol,original_native_state,supports_xyz,
)
from research.zero_error_execution_receipt import conflict_graph,dsatur_coloring

PLAN=Path("research/NATIVE_ONEBIT_ROBUST_RECEIPT_PREREG_20261013.json")
BLOB="53a4429f786e01a69670d61202da921fcc993f5a"


def frozen():
    got=subprocess.check_output(["git","hash-object",str(PLAN)],
                                text=True).strip()
    if got!=BLOB:
        raise RuntimeError("New original PhysX receipt prereg altered")
    p=json.loads(PLAN.read_text(encoding="utf-8"))
    if (p["robot_models"]!=["panda","xarm6_robotiq"]
        or p["new_reset_seeds"]["panda"]!=[5800411,5800412,5800413,5800414]
        or p["new_reset_seeds"]["xarm6_robotiq"]!=
            [5900411,5900412,5900413,5900414]
        or p["variants"]!=["A","B"]
        or p["ack_histories"]!=list(HISTORY_ORDER)
        or p["total_new_native_PhysX_worlds"]!=64
        or p["total_graph_cases"]!=96):
        raise RuntimeError("Registered original robot factorial changed")
    return p


def one_bit_correcting_codec(conflicts):
    """Exact length-minimum n=4 graph+Hamming-distance>=3 assignment."""
    if len(conflicts)!=4:
        raise ValueError("Original four execution histories required")
    if any((conflicts[i]>>i)&1 for i in range(4)):
        raise ValueError("No self-conflicts allowed")
    if any(bool((conflicts[i]>>j)&1)!=bool((conflicts[j]>>i)&1)
           for i in range(4) for j in range(4)):
        raise ValueError("Confusability must be symmetric")
    # A global XOR translation preserves every pairwise Hamming distance,
    # hence the first codeword can be fixed to all-zero without losing an
    # optimum. The remaining 3 words are searched by exact backtracking.
    for nbits in range(6):
        assigned=[0,-1,-1,-1]
        nwords=1<<nbits
        def choose(i):
            if i==4:
                return tuple(assigned)
            for v in range(nwords):
                if any((conflicts[i]>>j)&1 and
                       (v^assigned[j]).bit_count()<3
                       for j in range(i)):
                    continue
                assigned[i]=v
                witness=choose(i+1)
                if witness is not None:
                    return witness
                assigned[i]=-1
            return None
        result=choose(1)
        if result is not None:
            return nbits,result
    raise RuntimeError("Length 5 exact four-symbol protected code failed")


def decode_under_any_onebit_error(anchor,support,codes,nbits):
    entries={}
    attempted=0
    conflicts=0
    for h in sorted(anchor):
        for z in support[h]:
            for error in [0]+[1<<b for b in range(nbits)]:
                key=(z,codes[h]^error)
                attempted+=1
                if key in entries and entries[key]!=anchor[h]:
                    conflicts+=1
                entries[key]=anchor[h]
    return conflicts,attempted


def full_ack_one_error_correcting_baseline():
    """4 codewords length 5, minimum distance 3, and 4-bit impossible."""
    codes=(0,28,19,15)
    assert all((codes[i]^codes[j]).bit_count()>=3
               for i in range(4) for j in range(i+1,4))
    # A(4,3)=2 < 4 (standard Hamming coding bound/known exact table).
    return 5,codes


def one_native_sensor_contract(worlds,quantum,epsilon):
    if set(worlds)!=set(HISTORY_ORDER):
        raise RuntimeError("Native PhysX execution evidence incomplete")
    corrections=worlds["00"]["source_announced_corrective_native_actions"]
    commands=[np.asarray(corrections[h],dtype=float) for h in HISTORY_ORDER]
    for h in HISTORY_ORDER:
        for j,k in enumerate(HISTORY_ORDER):
            actual=np.asarray(worlds[h][
                "source_announced_corrective_native_actions"][k])
            if np.linalg.norm(actual-commands[j])>1e-5:
                raise RuntimeError("Candidate command depends on hidden truth")
    unique=[]
    anchor={}
    for i,cmd in enumerate(commands):
        if not np.isfinite(cmd).all() or cmd.shape!=(6,):
            raise RuntimeError("Native 6D corrective command missing")
        label=next((j for j,v in enumerate(unique)
                    if np.linalg.norm(cmd-v)<=1e-6),None)
        if label is None:
            unique.append(cmd)
            label=len(unique)-1
        anchor[i]=label
    support={i:supports_xyz(
        worlds[h]["public_relative_rotation_log_rad"],
        quantum,epsilon
    ) for i,h in enumerate(HISTORY_ORDER)}
    graph=conflict_graph(anchor,support)
    plain_colors,k=dsatur_coloring(graph)
    plain_length=math.ceil(math.log2(k)) if k>1 else 0
    protected_length,codes=one_bit_correcting_codec(graph)
    baseline_length,full_codes=full_ack_one_error_correcting_baseline()
    proto_bad,proto_attempts=decode_under_any_onebit_error(
        anchor,support,dict(enumerate(codes)),protected_length)
    full_bad,full_attempts=decode_under_any_onebit_error(
        anchor,support,dict(enumerate(full_codes)),baseline_length)
    if proto_bad or full_bad:
        raise RuntimeError("One-bit corruption created an unsafe wrong command")
    return {
        "sensor_cell_rad":quantum,
        "sensor_bound_rad":epsilon,
        "native_correction_action_modes":len(unique),
        "native_support_conflict_edges":sum(a.bit_count() for a in graph)//2,
        "unprotected_minimal_receipt_bits":plain_length,
        "onebit_safe_minimal_receipt_bits":protected_length,
        "optimal_full_four_history_onebit_safe_baseline_bits":baseline_length,
        "source_corrected_bitrate_savings_bits":baseline_length-protected_length,
        "onebit_error_decoding_attempts":proto_attempts,
        "universal_onebit_unsafe_decisions":proto_bad,
        "full_ack_onebit_unsafe_decisions":full_bad,
        "known_theory_not_original_binary_ECC":True,
    }


def run_robot(robot,output):
    p=frozen()
    _,old=load_native_protocol()
    if robot not in p["robot_models"]:
        raise ValueError("Unregistered native controller")
    torch.set_num_threads(1)
    original=[]
    cells=[]
    for seed in p["new_reset_seeds"][robot]:
        for variant in p["variants"]:
            scenarios={}
            for h in HISTORY_ORDER:
                w=original_native_state(old,robot,seed,variant,h)
                original.append(w)
                scenarios[h]=w
                print("ORIGINAL_NEW_ROBOT_ACK_WORLD",json.dumps(
                    {"robot":robot,"seed":seed,"variant":variant,"history":h}
                ),flush=True)
            for q,e in product(p["quantizers_rad"],p["bounded_component_noise_rad"]):
                r=one_native_sensor_contract(scenarios,q,e)
                r.update({"robot":robot,"reset_seed":seed,"variant":variant})
                cells.append(r)
                print("ORIGINAL_NEW_PROTECTED_RECEIPT_CELL",
                      json.dumps(r,sort_keys=True),flush=True)
    if len(original)!=32 or len(cells)!=48:
        raise RuntimeError("New original native robot denominator incomplete")
    good=sum(c["source_corrected_bitrate_savings_bits"]>=2 for c in cells)
    output.write_text(json.dumps({
        "schema":p["schema"],"prereg_git_blob":BLOB,
        "actual_new_native_robot":robot,
        "original_PhysX_worlds":32,"original_sensor_graphs":48,
        "graph_conditions_saving_two_or_more_bits":good,
        "full_5bit_optimal_baseline_used":True,
        "all_supported_onebit_errors_safe":True,
        "independent_reset_clusters":4,
        "all_worlds":original,"all_sensor_cases":cells,
        "no_real_hardware_and_no_PickCube_task_success":True,
    },indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_ONEBIT_NATIVE_SHARD_DONE",json.dumps(
        {"robot":robot,"worlds":32,"cells":48,"save_ge_two":good}
    ),flush=True)


if __name__=="__main__":
    args=argparse.ArgumentParser()
    args.add_argument("--robot",choices=["panda","xarm6_robotiq"],required=True)
    args.add_argument("--out",type=Path,required=True)
    v=args.parse_args()
    run_robot(v.robot,v.out)
