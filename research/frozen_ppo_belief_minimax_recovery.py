"""Frozen, prespecified lost-ACK PPO six-arm real PhysX trial.

Important: neutral arm delta is issued via *env.step*, not network-level timeout.
This is an acknowledged command-history fault MODEL on the native controller,
not hardware safety or unknown-action inference from camera feedback.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import torch
from scipy.spatial.transform import Rotation
from research.action_abi_uncertain_delivery_belief import UncertainDeliveryBelief, positional_diameter
from huggingface_hub import hf_hub_download
from mani_skill.utils.structs import Pose

import frozen_ppo_action_history_observer as original
from action_abi_history_observer import ActionHistoryObserver, TargetPose
from frozen_ppo_observer_policy import _actor, REPO

TASK = os.environ["ABI_TASK"]
CONDITION = os.environ["ABI_FAULT"]
FIRST = {"pull_cube": 96001, "stack_cube": 97001}
CHUNK = int(os.environ["ABI_CHUNK"])
if CHUNK not in (0,1):
    raise ValueError("64-case frozen cohort has exactly two chunks per condition/task")
if TASK not in FIRST or CONDITION not in ("applied_no_ack", "neutral_arm_delta_no_ack"):
    raise ValueError("Only frozen preregistered task/fault conditions are permitted")
SEEDS = tuple(range(FIRST[TASK]+8*CHUNK,FIRST[TASK]+8*(CHUNK+1)))
FAULT_STEP = 2
SOURCE_SHA = "495e76e5d95ca0c309449f544b9c61c727b4bd22"
PROTOCOL = "research/CST_BELIEF_MINIMAX_PROSPECTIVE_64_V1.json"
ARMS = ("source","oracle_live_memory","recovered_one_readback",
        "optimistic_assume_applied","pessimistic_assume_neutral","fail_closed_stop","belief_minimax_zero_readback")
FAILING = CONDITION == "neutral_arm_delta_no_ack"


def pose_record(arm) -> TargetPose:
    # The initial achieved pose is public state; read only *once at reset*.
    p = np.asarray(arm.ee_pose_at_base.p.detach().cpu()).reshape(-1,3)[0]
    q = np.asarray(arm.ee_pose_at_base.q.detach().cpu()).reshape(-1,4)[0]
    return TargetPose.from_arrays(p,q[[1,2,3,0]])


def target_record(arm) -> TargetPose:
    # Privileged controller readback; only oracle and the SINGLE authorized
    # post-loss resync use this DURING decisions. All other reads are audit.
    v = np.asarray(arm.get_state()["target_pose"].detach().cpu()).reshape(-1,7)[0]
    return TargetPose.from_arrays(v[:3],v[[4,5,6,3]])


def as_pose(record: TargetPose) -> Pose:
    q=np.asarray(record.quaternion_xyzw,dtype=np.float32)[[3,0,1,2]]
    p=np.asarray(record.position,dtype=np.float32)
    return Pose.create_from_pq(torch.as_tensor(p).reshape(1,3),
                               torch.as_tensor(q).reshape(1,4))


def discrepancy(a: TargetPose,b: TargetPose) -> dict:
    return {
        "position_m":float(np.max(np.abs(np.asarray(a.position)-np.asarray(b.position)))),
        "rotation_rad":float((Rotation.from_quat(a.quaternion_xyzw)
                             *Rotation.from_quat(b.quaternion_xyzw).inv()).magnitude())
    }


def make_observer(arm):
    c=arm.config
    x=ActionHistoryObserver(c.pos_lower,c.pos_upper,c.rot_lower,
                            frame=c.frame,use_delta=c.use_delta,
                            use_target=c.use_target,
                            normalize_action=c.normalize_action)
    x.reset(pose_record(arm))
    return x


def midpoint_target_hypotheses(hypotheses):
    """Two-target translation L-infinity midpoint and SO3 geodesic midpoint.

    This is a *candidate bounded-risk controller action*, NOT an exact
    source-policy action or a general safety certificate. No controller
    target memory is accessed to calculate this midpoint.
    """
    if len(hypotheses)==1:
        return hypotheses[0]
    if len(hypotheses)!=2:
        raise RuntimeError("Midpoint protocol supports exactly two histories; refuse")
    a,b=hypotheses
    pa=np.asarray(a.position,dtype=np.float64)
    pb=np.asarray(b.position,dtype=np.float64)
    ra=Rotation.from_quat(a.quaternion_xyzw)
    rb=Rotation.from_quat(b.quaternion_xyzw)
    geod=ra*((ra.inv()*rb)**0.5)
    return TargetPose.from_arrays((pa+pb)/2,geod.as_quat())


def trial(policy, seed):
    worlds={name:original.env("pd_ee_delta_pose" if name=="source"
                              else "pd_ee_target_delta_pose") for name in ARMS}
    rec={"seed":seed,"task":original.TASK_NAME,"fault":CONDITION,
         "fault_step":FAULT_STEP,"fault_reached":{},
         "success_once":{},"steps":{},"initial_obs_diff":{},
         "approximations":{},"refusals":{},"readback_queries":{},
         "resync_position_error_m":None,
         "ambiguity_diameter_m":None,
         "post_fault_optimistic_position_error_m":None,
         "post_fault_pessimistic_position_error_m":None,
         "audit_endpoint_residual":{},
         "midpoint_belief_size_at_fault":None,
         "midpoint_postfault_max_memory_diameter_m":0.0,
         "midpoint_projected_action_count":0,
         "midpoint_final_target_hypothesis_error_m":None}
    try:
        observations={n:w.reset(seed=seed)[0] for n,w in worlds.items()}
        canonical=original._project_policy_observation(
            observations["source"],worlds["source"])
        for name in ARMS[1:]:
            target=original._project_policy_observation(observations[name],
                worlds[name],verify_memory=(name=="oracle_live_memory"))
            diff=float(torch.max(torch.abs(canonical-target)).item())
            rec["initial_obs_diff"][name]=diff
            if diff>5e-4:
                raise RuntimeError("Different initial task/robot physical state")
        ctrl={name:w.unwrapped.agent.controller for name,w in worlds.items()}
        src_arm=ctrl["source"].controllers["arm"]
        observers={name:make_observer(ctrl[name].controllers["arm"])
                   for name in ARMS if name not in ("source","oracle_live_memory",
                                              "belief_minimax_zero_readback")}
        rc=ctrl["belief_minimax_zero_readback"].controllers["arm"].config
        midpoint_belief=UncertainDeliveryBelief(rc.pos_lower,rc.pos_upper,rc.rot_lower)
        midpoint_belief.reset(pose_record(ctrl["belief_minimax_zero_readback"].controllers["arm"]))
        done={name:False for name in ARMS}
        for t in range(original.STEPS):
            for name,w in worlds.items():
                if done[name]:
                    continue
                # Fail-closed controller never issues an action after ambiguous ACK.
                if name=="fail_closed_stop" and t>FAULT_STEP:
                    done[name]=True
                    rec["refusals"][name]={"step":t,"reason":"UNKNOWN_ACK_NO_ATTESTED_MEMORY"}
                    continue
                native=original.act(policy,original._project_policy_observation(
                    observations[name],w,verify_memory=(name=="oracle_live_memory")))
                if name=="source":
                    action=native
                else:
                    arm=ctrl[name].controllers["arm"]
                    prior=(None if name=="oracle_live_memory" else
                           as_pose(midpoint_target_hypotheses(midpoint_belief.hypotheses))
                           if name=="belief_minimax_zero_readback" else
                           as_pose(observers[name].pose))
                    rewritten,reason,amplitude=original.normalized_target_delta(
                        src_arm,arm,native,approximate=True,
                        old_override=prior)
                    if rewritten is None:
                        done[name]=True
                        rec["refusals"][name]={"step":t,"reason":reason,
                                              "required_amp":amplitude}
                        continue
                    if reason=="APPROXIMATE_BOUNDED_PROJECTION" and name=="belief_minimax_zero_readback":
                        rec["midpoint_projected_action_count"]+=1
                    if reason=="APPROXIMATE_BOUNDED_PROJECTION":
                        rec["approximations"].setdefault(name,[]).append(
                            {"step":t,"exactness":"NOT_EXACT",
                             "required_native_amp":amplitude})
                    source_action=ctrl["source"].to_action_dict(native[0])
                    dispatched_arm=rewritten[0].clone()
                    if t==FAULT_STEP and FAILING:
                        dispatched_arm=torch.zeros_like(dispatched_arm)
                    action=ctrl[name].from_action_dict({
                        "arm":dispatched_arm,
                        "gripper":source_action["gripper"]}).reshape(1,-1)
                    if name=="belief_minimax_zero_readback":
                        midpoint_ticket=midpoint_belief.prepare(
                            rewritten[0].detach().cpu().numpy())
                    if name in observers:
                        observer=observers[name]
                        before=observer.pose
                        ticket=observer.prepare(rewritten[0].detach().cpu().numpy())
                        # Do not advance / commit belief until env.step returns.
                observations[name],_,term,trunc,info=w.step(action)
                if name=="oracle_live_memory" and t==FAULT_STEP:
                    rec["fault_reached"][name]=True
                if name=="belief_minimax_zero_readback":
                    midpoint_belief.acknowledge(
                        midpoint_ticket,applied=None if t==FAULT_STEP else True)
                    if t==FAULT_STEP:
                        rec["fault_reached"][name]=True
                        rec["midpoint_belief_size_at_fault"]=len(midpoint_belief.hypotheses)
                    rec["midpoint_postfault_max_memory_diameter_m"]=max(
                        rec["midpoint_postfault_max_memory_diameter_m"],
                        positional_diameter(midpoint_belief.hypotheses))
                if name in observers:
                    if t==FAULT_STEP:
                        rec["fault_reached"][name]=True
                        if name=="recovered_one_readback":
                            # ACK is UNKNOWN, so continue only following the
                            # single explicitly trusted controller target read.
                            observer.acknowledge(ticket.ticket,applied=None)
                            if observer._valid:
                                raise RuntimeError("Ambiguous ACK unexpectedly preserved observer authority")
                            truth=target_record(ctrl[name].controllers["arm"])
                            rec["readback_queries"][name]=1
                            observer.reset(truth)
                            rec["resync_position_error_m"]=discrepancy(
                                observer.pose,truth)["position_m"]
                        elif name=="optimistic_assume_applied":
                            observer.acknowledge(ticket.ticket,applied=True)
                        elif name=="pessimistic_assume_neutral":
                            observer.acknowledge(ticket.ticket,applied=False)
                        else:
                            # Safe stop has no action after this unknown ACK.
                            observer.acknowledge(ticket.ticket,applied=None)
                        if name=="optimistic_assume_applied":
                            truth=target_record(ctrl[name].controllers["arm"])
                            rec["post_fault_optimistic_position_error_m"]=discrepancy(
                                observer.pose,truth)["position_m"]
                        if name=="pessimistic_assume_neutral":
                            truth=target_record(ctrl[name].controllers["arm"])
                            rec["post_fault_pessimistic_position_error_m"]=discrepancy(
                                observer.pose,truth)["position_m"]
                        if name=="recovered_one_readback":
                            # Captures the two possible prior target states
                            # using only acknowledged PRE-fault history and
                            # the issued (not applied) command transition.
                            # Intentionally no alternative branch is pruned.
                            ghost=make_observer(ctrl[name].controllers["arm"])
                            ghost.reset(before)
                            predicted=ghost.prepare(rewritten[0].detach().cpu().numpy())
                            ghost.acknowledge(predicted.ticket,applied=True)
                            rec["ambiguity_diameter_m"]=float(np.linalg.norm(
                                np.asarray(ghost.pose.position)-
                                np.asarray(before.position)))
                    else:
                        observer.acknowledge(ticket.ticket,applied=True)
                value=info.get("success")
                if value is None:
                    raise RuntimeError("No native ManiSkill task success info")
                rec["success_once"][name]=rec["success_once"].get(name,False) or original._bool_value(value)
                rec["steps"][name]=t+1
                done[name]=original._bool_value(term) or original._bool_value(trunc)
            if all(done.values()):
                break
        if rec["fault_reached"].get("belief_minimax_zero_readback",False):
            truth=target_record(ctrl["belief_minimax_zero_readback"].controllers["arm"])
            deviations=[discrepancy(h,truth)["position_m"] for h in midpoint_belief.hypotheses]
            rec["midpoint_final_target_hypothesis_error_m"]=min(deviations)
            if min(deviations)>0.0002:
                raise RuntimeError("Actual target not in predicted belief set: falsified controller recurrence")
        for name in observers:
            if name=="fail_closed_stop" and not observers[name]._valid:
                continue
            if name not in rec["fault_reached"]:
                # No fault reached, but all pre-fault states retained.
                continue
            actual=target_record(ctrl[name].controllers["arm"])
            rec["audit_endpoint_residual"][name]=discrepancy(observers[name].pose,actual)
        for name in ARMS[1:]:
            rec["fault_reached"].setdefault(name,False)
            rec["readback_queries"].setdefault(name,0)
        # Oracle has privileged private target access throughout the loop.
        # Sentinel -1 means ongoing privileged access, NOT zero reads.
        rec["readback_queries"]["oracle_live_memory"]=-1
        rec["readback_queries"]["belief_minimax_zero_readback"]=0
        print("UNKNOWN_ACK_EPISODE",json.dumps(rec,sort_keys=True))
        return rec
    finally:
        for env in worlds.values():
            env.close()


def main():
    info=original.TASKS[TASK]
    path=Path(hf_hub_download(repo_id=REPO,filename=info[1],
                               revision=original.PUBLISHED_MODEL_REVISION))
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=info[2]:
        raise RuntimeError("Frozen independent PPO checkpoint digest changed")
    e=original.env("pd_ee_delta_pose")
    try:
        obs,_=e.reset(seed=SEEDS[0])
        original.POLICY_OBS_DIM=int(obs.shape[-1])
        policy=_actor(torch.load(path,map_location="cpu",weights_only=True),
                      original.POLICY_OBS_DIM,7)
    finally:
        e.close()
    rows=[trial(policy,s) for s in SEEDS]
    counts={k:sum(bool(r["success_once"].get(k,False)) for r in rows)
            for k in ARMS}
    data={"schema":"cst_belief_minimax_64_prospective_v1",
          "preregistration":PROTOCOL,"chunk":CHUNK,
          "midpoint_is_nonexact_under_clipping":True,
          "frozen_prereg_commit":SOURCE_SHA,
          "task":original.TASK_NAME,"fault":CONDITION,
          "seeds":list(SEEDS),"real_physx":True,
          "backend":"physx_cpu","checkpoint_sha256":digest,
          "checkpoint_revision":original.PUBLISHED_MODEL_REVISION,
          "training_performed":False,"success_count":counts,"rows":rows}
    out=Path(f"belief_minimax_{TASK}_{CONDITION}_chunk{CHUNK}_fresh8.json")
    out.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("BELIEF_MINIMAX_REAL_PHYSX_SUMMARY",json.dumps({
        "task":original.TASK_NAME,"fault":CONDITION,"success":counts,
        "n":len(rows),"fault_reached":{
            name:sum(bool(r["fault_reached"].get(name,False)) for r in rows)
            for name in ARMS[1:]},
        "readback_count":sum(r["readback_queries"].get("recovered_one_readback",0)
                             for r in rows)},sort_keys=True))


if __name__=="__main__":
    main()
