"""Preregistered NEW Panda/xArm6 native PhysX probe/hidden-target intervention.
Scripted controller worlds, not a learned policy task-success evaluation.
Audit-only native target getters never choose, alter or authorize t3 probes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
import gymnasium as gym
import mani_skill.envs
import numpy as np
from research.cross_robot_ack_physics import (
    ARM_MODE, TASK, actual_target_after_physics, get_arm,
    pose_residual, requested_native, stepping)

PRE="research/CAUSAL_PROBE_PREREG_20261010.json"
PRE_BLOB="34cb7673a0d5acd64be25d03b926ea6b0f20b54c"
SOURCE_BLOB="3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7"
SEEDS={"panda":990001,"xarm6_robotiq":991001}
PROBES={"zero":[0.,0.,0.,0.,0.,0.],
        "x":[.15,0.,0.,0.,0.,0.],
        "y":[0.,.15,0.,0.,0.,0.]}
TRUTHS=("held","applied")

def check_preoutcome():
    def gitblob(p):
        return subprocess.check_output(["git","hash-object",p],text=True).strip()
    if gitblob(PRE)!=PRE_BLOB or gitblob("research/cross_robot_ack_physics.py")!=SOURCE_BLOB:
        raise RuntimeError("Physical protocol/source differs from outcome-blind frozen blobs")
    obj=json.loads(Path(PRE).read_text())
    if (obj["new_seed_intervals_inclusive"]!={"panda":[990001,990008],
                                               "xarm6_robotiq":[991001,991008]}
        or obj["known_delivered_t3_probes"]!={k:[int(v) if v==0 else v for v in x] for k,x in PROBES.items()}
        or obj["expected_physical_worlds"]!=96
        or obj["allow_post_outcome_selection"] is not False):
        raise RuntimeError("Preregistered native experiment geometry changed")
    return obj

def _achieved_xyz(arm):
    return np.asarray(arm.ee_pose_at_base.p.detach().cpu(),dtype=float).reshape(-1,3)[0].tolist()

def one_world(robot,seed,truth,probe):
    if robot not in SEEDS or seed not in range(SEEDS[robot],SEEDS[robot]+8) or truth not in TRUTHS or probe not in PROBES:
        raise ValueError("Unregistered robot/seed/truth/probe")
    env=gym.make(TASK,robot_uids=robot,num_envs=1,obs_mode="state",
                 sim_backend="physx_cpu",reconfiguration_freq=1,
                 control_mode=ARM_MODE,disable_env_checker=True)
    try:
        env.reset(seed=seed)
        ctrl,arm=get_arm(env)
        public_before=None
        target_before=None
        target_after=None
        step_status=[]
        for t in range(4):
            action=(np.zeros(6,dtype=float) if t==2 and truth=="held"
                    else np.asarray(PROBES[probe],dtype=float) if t==3
                    else requested_native(t))
            step_status.append(stepping(env,ctrl,action))
            if t==1:
                public_before=_achieved_xyz(arm)
            if t==2:
                # Strictly post-action AUDIT, not consulted for next probe selection.
                target_before=actual_target_after_physics(arm)
            if t==3:
                target_after=actual_target_after_physics(arm)
                public_after=_achieved_xyz(arm)
        metric=pose_residual(target_before,target_after)
        xyz_delta=[float(v-w) for v,w in zip(public_after,public_before)]
        result=dict(robot=robot,seed=seed,truth_posthoc_only=truth,
            probe=probe,action_t3_native_six=PROBES[probe],
            public_xyz_after_t1=public_before,public_xyz_after_t3=public_after,
            public_xyz_delta=xyz_delta,
            target_before_t3_position_m=list(target_before.position),
            target_before_t3_quaternion_xyzw=list(target_before.quaternion_xyzw),
            target_after_t3_position_m=list(target_after.position),
            target_after_t3_quaternion_xyzw=list(target_after.quaternion_xyzw),
            target_change_translation_l2_m=metric["l2_m"],
            target_change_translation_linf_m=metric["linf_m"],
            target_change_orientation_so3_rad=metric["so3_rad"],
            native_source_action_reached=True,
            oracle_targets_used_by_decision=False,
            oracle_reads_audit_only_after_t2_and_t3=2,
            actual_native_physx_cpu=True,
            policy_source="scripted-native-no-VLA",
            task_success_measured=False,
            all_step_return_codes_available=len(step_status)==4)
        if any(not math.isfinite(x) for x in
               xyz_delta+[metric["l2_m"],metric["so3_rad"]]):
            raise RuntimeError("Nonfinite physical/native metrics")
        return result
    finally:
        env.close()

def run(robot,chunk,out):
    check_preoutcome()
    if robot not in SEEDS or type(chunk) is not int or chunk not in (0,1):
        raise ValueError("Only registered 2 robots x 2 chunks")
    seed0=SEEDS[robot]+4*chunk
    rows=[]
    for seed in range(seed0,seed0+4):
        for truth in TRUTHS:
            for probe in PROBES:
                row=one_world(robot,seed,truth,probe)
                rows.append(row)
                print("FROZEN_CAUSAL_PROBE_NATIVE_PHYSX",json.dumps(row,sort_keys=True),flush=True)
    result=dict(schema="causal_probe_post_action_target_shift_native_physx_v1",
        frozen_proto_blob=PRE_BLOB,frozen_native_source_blob=SOURCE_BLOB,
        robot=robot,chunk=chunk,seeds=list(range(seed0,seed0+4)),
        physical_worlds=len(rows),independent_reset_clusters=4,
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        rows=rows,
        no_trained_policy_task_success_claim=True,
        oracle_used_only_for_post_action_audit=True)
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True))
    if len(rows)!=24:raise RuntimeError("Incomplete prospective native source")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("preflight","run"),required=True)
    ap.add_argument("--robot",choices=tuple(SEEDS))
    ap.add_argument("--chunk",type=int,default=0)
    ap.add_argument("--out")
    args=ap.parse_args()
    if args.mode=="preflight":
        check_preoutcome()
        print("PREFLIGHT_PASS_ONLY_NO_PHYSICS",PRE_BLOB)
    else:
        if not args.robot or not args.out:ap.error("Real run needs robot and --out")
        run(args.robot,args.chunk,args.out)
