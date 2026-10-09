"""Actual 2-robot PhysX full-SE3 anchored-repair transition falsifier.

Four truth/probe combinations x two independently stepped repair arms on each
physical robot/reset. Two arms have oracle-known ACK truth; comparison isolates
action-conditioned *repair semantics*, not ACK recognition or policy success.
All private getter calls are post-action AUDIT only and never fed to planning.
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
from scipy.spatial.transform import Rotation

from research.action_abi_history_observer import ActionHistoryObserver
from research.cross_robot_ack_physics import (
    ARM_MODE, TASK, actual_target_after_physics, get_arm,
    observer_for, pose_residual, requested_native, stepping,
)

PROTO=Path("research/PHYSX_ANCHOR_REPAIR_FIRST128_PREOUTCOME_V1.json")
PROTO_HASH="2e78bf28f746d9ffa95ca7cf7a8b99646614d8cd"
SOURCE_BLOBS={
 "research/cross_robot_ack_physics.py":"3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7",
 "research/action_abi_history_observer.py":"2aa52e477c202386fb6a7e43586d246026b6041d",
}
START={"panda":720001,"xarm6_robotiq":730001}
PROBES={"zero":np.zeros(6,dtype=np.float64),
        "rotation_z":np.array([0,0,0,0,0,0.35],dtype=np.float64)}
TRUTHS=("held","applied")
ARMS=("no_probe_transition_ablation","actual_transition_compensation")
POS_TOL=1e-4
ROT_TOL=1e-3

def frozen_preflight():
    def sha(p):return subprocess.check_output(["git","hash-object",str(p)],text=True).strip()
    if sha(PROTO)!=PROTO_HASH:
        raise ValueError("Pre-outcome protocol mutated")
    for path,digest in SOURCE_BLOBS.items():
        if sha(path)!=digest:
            raise ValueError("Previously validated physical command semantics mutated "+path)
    d=json.loads(PROTO.read_text(encoding="utf-8"))
    if (d["robot_seeds"]!={k:[v,v+7] for k,v in START.items()} or
        d["known_delivered_t3_probes"]!={k:list(map(float,v)) for k,v in PROBES.items()} or
        d["truths"]!=list(TRUTHS) or d["repair_comparators"]!=list(ARMS) or
        d["registered_worlds"]!=128 or d["independent_robot_reset_seeds"]!=16 or
        d["predeclared_t4_success"]!={"position_max_abs_error_m":POS_TOL,
                                      "rotation_geodesic_error_rad":ROT_TOL}):
        raise ValueError("Frozen native probe/truth/goal/denominator changed")
    return d

def reverse_native_full_se3(arm,current,desired):
    c=arm.config
    if not (c.frame==ActionHistoryObserver.FRAME and c.use_delta and
            c.use_target and c.normalize_action):
        raise RuntimeError("Unverified target controller frame/ABI")
    lo=np.broadcast_to(np.asarray(c.pos_lower,dtype=float),(3,))
    hi=np.broadcast_to(np.asarray(c.pos_upper,dtype=float),(3,))
    if not (np.all(lo<0) and np.all(hi>0)):
        raise RuntimeError("Unsupported asymmetric native position chart")
    delta=np.asarray(desired.position)-np.asarray(current.position)
    native_position=delta/np.where(delta>=0,hi,-lo)
    rotation=(Rotation.from_quat(desired.quaternion_xyzw)*
              Rotation.from_quat(current.quaternion_xyzw).inv())
    angles=rotation.as_euler("XYZ")
    scale=np.broadcast_to(np.asarray(c.rot_lower,dtype=float),(3,))
    if not np.all(np.abs(scale)>1e-12):
        raise RuntimeError("Unverified native rotation chart")
    native_rotation=angles/scale
    native=np.r_[native_position,native_rotation]
    if (not np.isfinite(native).all() or
        np.any(np.abs(native_position)>1+1e-5) or
        np.linalg.norm(native_rotation)>1+1e-5):
        raise RuntimeError("Full-SE3 anchor restoration exceeds representable native action")
    return np.clip(native,-1,1)

def physical_world(robot,seed,truth,probe_name,repair_name):
    if robot not in START or truth not in TRUTHS or probe_name not in PROBES or repair_name not in ARMS:
        raise ValueError("Unregistered fully factored physical world")
    env=gym.make(TASK,robot_uids=robot,num_envs=1,obs_mode="state",
                 sim_backend="physx_cpu",reconfiguration_freq=1,
                 control_mode=ARM_MODE,disable_env_checker=True)
    try:
        env.reset(seed=int(seed))
        ctrl,arm=get_arm(env)
        observer=observer_for(arm)
        outcomes=[]
        t1_anchor=t2_state=t3_state=None
        real_t1=real_t3=None
        public_t1=public_t3=None
        for t in range(4):
            if t==2 and truth=="held":
                action=np.zeros(6)
            elif t==3:
                action=PROBES[probe_name]
            else:
                action=requested_native(t)
            ticket=observer.prepare(action)
            outcome=stepping(env,ctrl,action)
            observer.acknowledge(ticket.ticket,applied=True)
            outcomes.append(outcome["official_success"])
            if t==1:
                t1_anchor=observer.pose
                real_t1=actual_target_after_physics(arm)
                public_t1=np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                                     dtype=float).reshape(-1,3)[0].tolist()
            if t==2:t2_state=observer.pose
            if t==3:
                t3_state=observer.pose
                real_t3=actual_target_after_physics(arm)
                public_t3=np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                                     dtype=float).reshape(-1,3)[0].tolist()
        if max(pose_residual(t1_anchor,real_t1)["linf_m"],
               pose_residual(t3_state,real_t3)["linf_m"])>POS_TOL:
            raise RuntimeError("Original source controller target prediction fails")
        if max(pose_residual(t1_anchor,real_t1)["so3_rad"],
               pose_residual(t3_state,real_t3)["so3_rad"])>ROT_TOL:
            raise RuntimeError("Original source quaternion target prediction fails")
        current=(t2_state if repair_name=="no_probe_transition_ablation"
                 else t3_state)
        correction=reverse_native_full_se3(arm,current,t1_anchor)
        last=stepping(env,ctrl,correction)
        observed_final=actual_target_after_physics(arm)
        err=pose_residual(t1_anchor,observed_final)
        real_drift=pose_residual(real_t1,real_t3)
        return {
            "schema":"original_native_se3_probe_repair_world_v1",
            "robot":robot,"seed":seed,"truth_oracle_known_to_both_repair_arms":truth,
            "known_delivered_probe":probe_name,"repair_strategy":repair_name,
            "native_probe":PROBES[probe_name].tolist(),
            "native_correction":correction.tolist(),
            "predicted_anchor_pose":{"position":list(t1_anchor.position),
                                     "quaternion_xyzw":list(t1_anchor.quaternion_xyzw)},
            "public_achieved_t1_xyz":public_t1,
            "public_achieved_t3_xyz":public_t3,
            "actual_target_after_probe_drift":real_drift,
            "predicted_physical_target_residual_t3":pose_residual(t3_state,real_t3),
            "real_t4_controller_target_restoration_error":err,
            "native_target_restoration_pass":(err["linf_m"]<=POS_TOL and
                                               err["so3_rad"]<=ROT_TOL),
            "actual_physx_world":True,
            "controller_keys":list(ctrl.controllers),
            "getter_called_after_t1_t3_for_audit_only":True,
            "getter_not_input_to_repair":True,
            "actual_t4_official_task_flag_context_only":last["official_success"],
            "actual_prefix_task_flag_context_only":outcomes,
            "scripted_native_only_no_learned_policy":True,
            "real_hardware_safety_claim":False,
        }
    finally:
        env.close()


def audit(folder:Path)->dict:
    pre=frozen_preflight()
    worlds=[]
    for robot in START:
        for chunk in (0,1):
            name=folder/f"anchor_repair_{robot}_chunk{chunk}.json"
            d=json.loads(name.read_bytes())
            if (d["schema"]!="original_anchor_repair_source_32_worlds_v1" or
                d["robot"]!=robot or d["chunk"]!=chunk or
                d["protocol_hash"]!=PROTO_HASH or len(d["worlds"])!=32):
                raise ValueError("Missing/malformed actual PhysX source shard")
            worlds+=d["worlds"]
    index={}
    for w in worlds:
        k=(w["robot"],w["seed"],w["truth_oracle_known_to_both_repair_arms"],
           w["known_delivered_probe"],w["repair_strategy"])
        if (k in index or w["robot"] not in START or
            w["seed"] not in range(START[w["robot"]],START[w["robot"]]+8) or
            w["truth_oracle_known_to_both_repair_arms"] not in TRUTHS or
            w["known_delivered_probe"] not in PROBES or
            w["repair_strategy"] not in ARMS or w["actual_physx_world"] is not True or
            w["getter_not_input_to_repair"] is not True):
            raise ValueError("Duplicated or invalid original PhysX observation")
        index[k]=w
    expected={(robot,seed,t,p,a) for robot,start in START.items()
              for seed in range(start,start+8) for t in TRUTHS for p in PROBES for a in ARMS}
    if set(index)!=expected or len(worlds)!=128:
        raise ValueError("Incomplete original matched 128 world denominator")
    result={}
    for robot in START:
        by_pair={}
        for probe in PROBES:
            for name in ARMS:
                subset=[w for key,w in index.items() if key[0]==robot and
                        key[3]==probe and key[4]==name]
                if len(subset)!=16:raise ValueError("Incorrect 8x2 population")
                successes=sum(w["native_target_restoration_pass"] for w in subset)
                rawmax=max(w["real_t4_controller_target_restoration_error"]["so3_rad"]
                           for w in subset)
                by_pair[f"{probe}/{name}"]={
                    "physical_worlds":len(subset),"full_se3_commanded_target_restorations":successes,
                    "max_target_so3_error_rad":rawmax}
        result[robot]=by_pair
    prefixes=0
    probe_changes=0
    for robot,start in START.items():
        for seed in range(start,start+8):
            for truth in TRUTHS:
                for probe in PROBES:
                    w1=index[robot,seed,truth,probe,ARMS[0]]
                    w2=index[robot,seed,truth,probe,ARMS[1]]
                    if (w1["public_achieved_t1_xyz"]!=w2["public_achieved_t1_xyz"] or
                        w1["public_achieved_t3_xyz"]!=w2["public_achieved_t3_xyz"] or
                        w1["predicted_anchor_pose"]!=w2["predicted_anchor_pose"] or
                        w1["native_probe"]!=w2["native_probe"]):
                        raise ValueError("Different original physical pre-repair prefixes")
                    prefixes+=1
                    if probe=="rotation_z" and w1["actual_target_after_probe_drift"]["so3_rad"]>0.001:
                        probe_changes+=1
    return {
        "schema":"first_original_full_se3_anchor_repair_all_source_audit_v1",
        "original_physx_worlds":len(worlds),
        "independent_seed_clusters":16,
        "same_repair_prefix_matched_seed_truth_probe_groups":prefixes,
        "nonzero_rotation_known_delivered_target_drift_gt_0_001rad_groups":probe_changes,
        "original_heldout_each_robot":result,
        "real_task_success_not_established":True,
        "no_online_ACK_classifier_used":True,
        "full_hidden_controller_action_model_complete":False,
        "external_independent_lab_replication":False,
        "source_evidence_only_not_safety":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=("preflight","trial","audit"))
    p.add_argument("--robot",choices=tuple(START))
    p.add_argument("--chunk",type=int,choices=(0,1))
    p.add_argument("--folder",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    frozen_preflight()
    if args.mode=="preflight":
        print("PASS FIRST128 PREOUTCOME PROTOCOL AND EXACT NATIVE SOURCE IDENTITY")
    elif args.mode=="trial":
        if args.robot is None or args.chunk is None:
            p.error("--robot and --chunk required")
        seedstart=START[args.robot]+4*args.chunk
        rows=[physical_world(args.robot,seed,t,probe,a)
              for seed in range(seedstart,seedstart+4)
              for t in TRUTHS for probe in PROBES for a in ARMS]
        result={"schema":"original_anchor_repair_source_32_worlds_v1",
                "robot":args.robot,"chunk":args.chunk,"protocol_hash":PROTO_HASH,
                "seeds":list(range(seedstart,seedstart+4)),
                "author_operated_cpu_physx_only":True,"worlds":rows}
        out=args.output or Path(f"anchor_repair_{args.robot}_chunk{args.chunk}.json")
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("FIRST128 ORIGINAL_NATIVE_PHYSX_SHARD",args.robot,args.chunk,
              len(rows),sum(w["native_target_restoration_pass"] for w in rows))
    else:
        if args.folder is None:
            p.error("--folder required")
        out=audit(args.folder)
        target=args.output or Path("first128_original_se3_anchor_repair_audit.json")
        target.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print("FIRST128 ORIGINAL_FULL_SE3_AUDITED",json.dumps(out,sort_keys=True))


if __name__=="__main__":
    main()
