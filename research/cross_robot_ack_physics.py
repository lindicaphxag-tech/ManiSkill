"""PhysX test of ACTION CONTRACT observability across Panda and xArm6 morphologies.

Not task success, policy transfer, robot safety, certified physical pose tracking,
or independent outside-lab adoption. The observer receives the issued native
actions and two explicit hypothetical delivery histories, never target getters.
Private commanded target data is inspected ONLY after an actual simulator step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import mani_skill.envs
import numpy as np
import torch
from scipy.spatial.transform import Rotation

from research.action_abi_history_observer import ActionHistoryObserver,TargetPose

TASK="PickCube-v1"
ARM_MODE="pd_ee_target_delta_pose"
FAULT_STEP=2
PROBE_STEP=3
SEED_FIRST={"panda":420001,"xarm6_robotiq":430001}
PROTO="research/CROSS_EMBODIMENT_ACK_PREOUTCOME_V1.json"


def pose_from(raw):
    p=np.asarray(raw.p.detach().cpu(),dtype=float).reshape(-1,3)[0]
    q=np.asarray(raw.q.detach().cpu(),dtype=float).reshape(-1,4)[0]
    return TargetPose.from_arrays(p,q[[1,2,3,0]])


def actual_target_after_physics(arm):
    raw=arm.get_state().get("target_pose")
    if raw is None:
        raise RuntimeError("No target controller state after actual physics step")
    v=np.asarray(raw.detach().cpu(),dtype=float).reshape(-1,7)[0]
    return TargetPose.from_arrays(v[:3],v[[4,5,6,3]])


def pose_residual(candidate,actual):
    d=np.asarray(candidate.position)-np.asarray(actual.position)
    rotation=Rotation.from_quat(actual.quaternion_xyzw).inv()*Rotation.from_quat(candidate.quaternion_xyzw)
    return dict(linf_m=float(np.max(np.abs(d))),l2_m=float(np.linalg.norm(d)),
                so3_rad=float(rotation.magnitude()))


def requested_native(t):
    # Same announced actions on both distinct robot morphologies;
    # meaningful t2 target separation, small bounded controls, zero from t3.
    vals={0:[.15,-.1,.1,.02,-.02,.01],
          1:[-.1,.16,.05,.02,.015,-.01],
          2:[.45,-.3,.35,.25,-.12,.1]}
    return np.asarray(vals.get(t,[0.]*6),dtype=np.float64)


def observer_for(arm):
    c=arm.config
    o=ActionHistoryObserver(c.pos_lower,c.pos_upper,c.rot_lower,
                            frame=c.frame,use_delta=c.use_delta,
                            use_target=c.use_target,
                            normalize_action=c.normalize_action)
    o.reset(pose_from(arm.ee_pose_at_base))
    return o


def get_arm(env):
    controller=env.unwrapped.agent.controller
    if env.unwrapped.agent.uid not in ("panda","xarm6_robotiq"):
        raise RuntimeError("Wrong robot actual articulation; refuse substituted robot")
    arm=controller.controllers["arm"]
    if type(arm).__name__ != "PDEEPoseController":
        raise RuntimeError("Not actual native EE pose controller, unexpected ABI")
    if arm.config.frame!=ActionHistoryObserver.FRAME:
        raise RuntimeError("Different unverified rotation chart, refuse instead of forcing")
    return controller,arm


def stepping(env,ctrl,native6):
    grip=ctrl.controllers["gripper"]
    gshape=grip.single_action_space.shape
    act=ctrl.from_action_dict({
        "arm":torch.as_tensor(native6,dtype=torch.float32),
        "gripper":torch.zeros(gshape,dtype=torch.float32)
    }).reshape(1,-1)
    obs,reward,term,trunc,info=env.step(act)
    if info.get("success") is None:
        raise RuntimeError("Official ManiSkill state/task flag missing")
    return dict(done=bool((term|trunc).reshape(-1)[0]),official_success=bool(info["success"].reshape(-1)[0]))


def one_seed(robot,seed):
    sims={}
    rows=dict(robot_uid=robot,seed=seed,task=TASK,control_mode=ARM_MODE,
              real_physx_cpu=True,source_policy_trained=False,
              native_command_ack_visible="unknown",
              xarm6_is_not_a_Panda_relabel=robot=="xarm6_robotiq",
              commanded_target_residual_by_step={}, probe={},
              official_task_success_by_truth={},
              both_private_target_reads_for_audit_only=True,
              native_requested_commands=[requested_native(t).tolist() for t in range(6)])
    try:
        for truth in ("applied","held"):
            env=gym.make(TASK,robot_uids=robot,num_envs=1,obs_mode="state",
                         sim_backend="physx_cpu",reconfiguration_freq=1,
                         control_mode=ARM_MODE,disable_env_checker=True)
            env.reset(seed=seed)
            sims[truth]=env
        states={truth:get_arm(env) for truth,env in sims.items()}
        initials={truth:pose_from(arm.ee_pose_at_base) for truth,(_,arm) in states.items()}
        reset_l2=pose_residual(initials["applied"],initials["held"])["l2_m"]
        if reset_l2>1e-5:
            raise RuntimeError(f"Paired robot reset achieved pose mismatch {reset_l2}")
        rows["pair_reset_l2_m"]=reset_l2
        # Each hypothesis maintained without controller private state. The
        # two histories differ only in the physical delivery truth at t=2.
        observers={truth:observer_for(arm) for truth,(_,arm) in states.items()}
        achieved={}
        actuals={}
        for t in range(6):
            for truth,(ctrl,arm) in states.items():
                intended=requested_native(t)
                actual_native=np.zeros(6) if (t==FAULT_STEP and truth=="held") else intended
                ticket=observers[truth].prepare(actual_native)
                outcome=stepping(sims[truth],ctrl,actual_native)
                observers[truth].acknowledge(ticket.ticket,applied=True)
                # Only AFTER physical stepping! Never feed this into observer.
                observed=actual_target_after_physics(arm)
                residual=pose_residual(observers[truth].pose,observed)
                rows["commanded_target_residual_by_step"].setdefault(truth,[]).append(residual)
                if residual["linf_m"]>1e-4 or residual["so3_rad"]>1e-3:
                    raise RuntimeError("History-target simulation disagrees with native robot controller")
                actuals[truth]=observed
                achieved[truth]=np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                                            dtype=float).reshape(-1,3)[0]
                rows["official_task_success_by_truth"][truth]=(
                    rows["official_task_success_by_truth"].get(truth,False)
                    or outcome["official_success"])
            if t==FAULT_STEP:
                delta=pose_residual(actuals["applied"],actuals["held"])
                rows["fault_divergence"]=delta
                rows["fault_target_distinct"]=delta["l2_m"]>1e-5 or delta["so3_rad"]>1e-5
            if t==PROBE_STEP:
                rows["probe"]={
                    "achieved_ee_xyz_applied":achieved["applied"].tolist(),
                    "achieved_ee_xyz_held":achieved["held"].tolist(),
                    "achieved_ee_branch_distance_m":float(
                        np.linalg.norm(achieved["applied"]-achieved["held"])),
                    "probe_native_arm_command":[0.]*6,
                    "private_target_reads_used_in_inference":0}
        for truth in ("applied","held"):
            rows["commanded_target_residual_max_linf_m_"+truth]=max(
                d["linf_m"] for d in rows["commanded_target_residual_by_step"][truth])
            rows["commanded_target_residual_max_so3_rad_"+truth]=max(
                d["so3_rad"] for d in rows["commanded_target_residual_by_step"][truth])
        print("CROSS_ROBOT_ACK_PHYSX_SEED",json.dumps(rows,sort_keys=True))
        return rows
    finally:
        for env in sims.values():env.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--robot",choices=tuple(SEED_FIRST),required=True)
    parser.add_argument("--chunk",choices=(0,1),type=int,required=True)
    args=parser.parse_args()
    original=Path(PROTO).read_bytes()
    if hashlib.sha1(b"blob "+str(len(original)).encode()+b"\0"+original).hexdigest()!="REPLACE_PROTOCOL_BLOB":
        raise RuntimeError("Before-outcome robot/seed/fault protocol unexpectedly changed")
    seeds=list(range(SEED_FIRST[args.robot]+4*args.chunk,SEED_FIRST[args.robot]+4*args.chunk+4))
    rows=[one_seed(args.robot,seed) for seed in seeds]
    if [r["seed"] for r in rows]!=seeds:
        raise RuntimeError("Original four-seed source denominator not preserved")
    out=dict(schema="cross_embodiment_stateful_action_observability_physics_v1",
             protocol=PROTO,robot=args.robot,task=TASK,control=ARM_MODE,
             real_physx_cpu=True,all_seeds=seeds,done=len(rows)==4,
             author_executed_only=True,external_independent_replication=False,
             not_policy_transfer_or_task_success_claim=True,
             nonzero_target_divergence=sum(r["fault_target_distinct"] for r in rows),
             probe_achieved_ee_separation_m=[r["probe"]["achieved_ee_branch_distance_m"] for r in rows],
             rows=rows)
    name=f"cross_robot_ack_{args.robot}_chunk{args.chunk}_original4.json"
    Path(name).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("CROSS_ROBOT_ACK_PHYSX_SUMMARY",json.dumps({
        "robot":args.robot,"seeds":seeds,
        "nonzero_target_divergence":out["nonzero_target_divergence"],
        "probe_achieved_ee_separation_m":out["probe_achieved_ee_separation_m"],
        "max_commanded_target_error_m":max(
            r["commanded_target_residual_max_linf_m_"+truth]
            for r in rows for truth in ("applied","held"))
    },sort_keys=True))
if __name__=="__main__":
    main()
