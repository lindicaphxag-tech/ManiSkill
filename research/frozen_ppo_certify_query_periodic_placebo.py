"""Original seven-arm PhysX unknown-ACK experiment PLUS a registered precommitted seed-modulo-4 query placebo.

Seven paired genuinely stepped target-control arms per original source seed.
Protocol fixed before this source in UNKNOWN_ACK_BOUNDED_QUERY_FROZEN_V1.json.
Physical injection is a native *arm target hold*, NOT network packet loss.
All geometry gates concern commanded targets, NOT hardware safety.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import torch
from scipy.spatial.transform import Rotation
from huggingface_hub import hf_hub_download
from mani_skill.utils.structs import Pose

import frozen_ppo_action_history_observer as base
from research.action_abi_history_observer import ActionHistoryObserver,TargetPose
from research.action_abi_uncertain_delivery_belief import UncertainDeliveryBelief
from research.two_history_se3_robust import common_two_history_command,Reason

TASK=os.environ.get("ABI_TASK")
CHUNK=int(os.environ.get("ABI_CHUNK","-1"))
FIRST={"pull_cube":260001,"stack_cube":270001}
if CHUNK not in (0,1,2,3):
    raise RuntimeError("Only 4 precommitted 8-state shards of each task allowed")
COHORT={
    "pull_cube":("PullCube-v1",range(260001+8*CHUNK,260009+8*CHUNK)),
    "stack_cube":("StackCube-v1",range(270001+8*CHUNK,270009+8*CHUNK))
}
if TASK not in COHORT:
    raise ValueError("ABI_TASK must name one of two frozen task/checkpoint cohorts")
TASK_NAME,SEEDS=COHORT[TASK]
FAULT_STEP=2
HORIZON=50
POS_BUDGET=.05
ROT_BUDGET=.05
NAMES=(
    "source_no_fault",
    "fault_oracle_private_target",
    "fault_optimistic_unverified_ack",
    "fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_precommitted_seed_schedule_query",
    "fault_always_single_privileged_query"
)
BELIEF_ARMS=(
    "fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_precommitted_seed_schedule_query"
)
PROTO="research/CERTIFY_QUERY_PERIODIC_PLACEBO_64_PREDECLARED_V1.json"
PERIODIC="fault_precommitted_seed_schedule_query"


def copy_target(pose):
    xyz=np.asarray(pose.p.detach().cpu(),dtype=float).reshape(-1,3)[0]
    q=np.asarray(pose.q.detach().cpu(),dtype=float).reshape(-1,4)[0]
    return TargetPose.from_arrays(xyz,q[[1,2,3,0]])


def privileged_target(arm):
    """Private target use is LIMITED to oracle, explicit query or audit only."""
    state=np.asarray(arm.get_state()["target_pose"].detach().cpu(),dtype=float).reshape(-1,7)[0]
    return TargetPose.from_arrays(state[:3],state[[4,5,6,3]])


def as_pose(target):
    q=np.asarray(target.quaternion_xyzw,dtype=np.float32)
    return Pose.create_from_pq(
        torch.as_tensor(np.asarray(target.position,dtype=np.float32)).reshape(1,3),
        torch.as_tensor(q[[3,0,1,2]]).reshape(1,4))


def observer(arm):
    cfg=arm.config
    o=ActionHistoryObserver(
        cfg.pos_lower,cfg.pos_upper,cfg.rot_lower,
        frame=cfg.frame,use_delta=cfg.use_delta,use_target=cfg.use_target,
        normalize_action=cfg.normalize_action)
    o.reset(copy_target(arm.ee_pose_at_base))
    return o


def belief(arm):
    cfg=arm.config
    b=UncertainDeliveryBelief(cfg.pos_lower,cfg.pos_upper,cfg.rot_lower)
    b.reset(copy_target(arm.ee_pose_at_base))
    return b


def geometry(arm, prior_candidates, desired):
    c=arm.config
    if c.frame!="root_translation:root_aligned_body_rotation":
        raise RuntimeError("Unverified native controller action chart")
    low=np.asarray(arm.action_space_low[:3].detach().cpu(),dtype=float)
    high=np.asarray(arm.action_space_high[:3].detach().cpu(),dtype=float)
    return common_two_history_command(
        tuple(prior_candidates),desired,
        pos_lower=low,pos_upper=high,rot_lower=float(c.rot_lower),
        position_budget_m=POS_BUDGET,rotation_budget_rad=ROT_BUDGET,
        hypotheses_complete=True,trusted_provenance=True,
        age_steps=0,max_age_steps=0,
        root_translation_root_left_rotation_verified=True,
    )


def desired_source_target(source_arm,target_arm,policy_native):
    decoded=source_arm._preprocess_action(policy_native[:,:6])
    return copy_target(source_arm.compute_target_pose(target_arm.ee_pose_at_base,decoded))


def audit_pose_error(real,desired):
    pos=float(np.max(np.abs(
        np.asarray(real.position)-np.asarray(desired.position))))
    rot=float((
        Rotation.from_quat(desired.quaternion_xyzw).inv()*
        Rotation.from_quat(real.quaternion_xyzw)
    ).magnitude())
    return pos,rot


def trial(policy,seed):
    worlds={
        n:base.env("pd_ee_delta_pose" if n=="source_no_fault"
                   else "pd_ee_target_delta_pose")
        for n in NAMES
    }
    result={
        "seed":seed,"task":TASK_NAME,"success_once":{n:False for n in NAMES},
        "steps":{},"initial_obs_diff":{},"faults":{},"refusals":{},
        "native_projection_NOT_EXACT":{},
        # -1 explicitly denotes unrestricted privileged target access in the
        # oracle, NOT zero decision readbacks. All other arms count real queries.
        "privileged_target_readback_decision_count":{
            n:(-1 if n=="fault_oracle_private_target" else 0) for n in NAMES},
        "robust_common_action_authorizations":{},
        "robust_common_action_refusals":{},
        "robust_native_target_bound_checks":{},
        "failure_causes":{},
        "success_step":{n:None for n in NAMES}
    }
    try:
        observations={n:w.reset(seed=seed)[0] for n,w in worlds.items()}
        source_observation=base._project_policy_observation(
            observations["source_no_fault"],worlds["source_no_fault"])
        result["initial_source_physical_obs_sha256"]=hashlib.sha256(
            source_observation.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
        for n in NAMES[1:]:
            view=base._project_policy_observation(
                observations[n],worlds[n],verify_memory=False)
            diff=float(torch.max(torch.abs(view-source_observation)))
            result["initial_obs_diff"][n]=diff
            if diff>5e-4:
                raise RuntimeError("Different physical source observation reset "+n)
        controllers={n:w.unwrapped.agent.controller for n,w in worlds.items()}
        arms={n:c.controllers["arm"] for n,c in controllers.items()}
        src=arms["source_no_fault"]
        observers={n:observer(arms[n]) for n in (
            "fault_optimistic_unverified_ack",
            "fault_always_single_privileged_query"
        )}
        beliefs={n:belief(arms[n]) for n in BELIEF_ARMS}
        done={n:False for n in NAMES}
        for step in range(HORIZON):
            for n in NAMES:
                if done[n]:
                    continue
                w=worlds[n]
                native=base.act(policy,base._project_policy_observation(
                    observations[n],w,verify_memory=(n in (
                        "source_no_fault","fault_oracle_private_target"))))
                c=controllers[n]
                arm=arms[n]
                certificate=None
                desired=None
                if n=="source_no_fault":
                    action=native
                else:
                    if n==PERIODIC and step==FAULT_STEP+1 and seed%4==0:
                        # PREDECLARED QUERY COST PLACEBO: no state, task or
                        # belief difficulty may enter this decision. Query
                        # seed 260004, 260008,.../270004, 270008,...
                        # once after the real unknown-ACK physical step.
                        actual=privileged_target(arm)
                        beliefs[n].require_external_resync(actual)
                        result["privileged_target_readback_decision_count"][n]+=1
                    name_belief=n in beliefs
                    maybe_two=(name_belief and len(beliefs[n].hypotheses)>1)
                    if n=="fault_always_single_privileged_query" and step==FAULT_STEP+1:
                        # Explicitly disclose this additional authoritative target read.
                        actual=privileged_target(arm)
                        observers[n].reset(actual)
                        result["privileged_target_readback_decision_count"][n]+=1
                    if maybe_two:
                        desired=desired_source_target(src,arm,native)
                        if n=="fault_strict_common_exact":
                            exact=beliefs[n].certify_common_exact_action(desired)
                            if not exact.authorized:
                                result["refusals"][n]={
                                    "step":step,"reason":exact.reason,
                                    "hypotheses":exact.possible_targets
                                }
                                done[n]=True
                                continue
                            rewritten=torch.as_tensor(
                                exact.native_action,dtype=native.dtype).reshape(1,6)
                            reason=None
                            amp=None
                        else:
                            certificate=geometry(arm,beliefs[n].hypotheses,desired)
                            if certificate.authorized:
                                rewritten=torch.as_tensor(
                                    certificate.normalized_6d,
                                    dtype=native.dtype).reshape(1,6)
                                reason=None
                                amp=None
                                result["robust_common_action_authorizations"][n]=(
                                    result["robust_common_action_authorizations"].get(n,0)+1)
                            elif n=="fault_robust_then_single_privileged_query" and (
                                result["privileged_target_readback_decision_count"][n]==0):
                                # Do NOT pretend the unknown ACK was answered by
                                # state-only observations. Spend one explicitly
                                # privileged read and collapse to the measured state.
                                result["robust_common_action_refusals"].setdefault(n,[]).append({
                                    "step":step,"reason":certificate.reason.value})
                                actual=privileged_target(arm)
                                beliefs[n].require_external_resync(actual)
                                result["privileged_target_readback_decision_count"][n]+=1
                                maybe_two=False
                            else:
                                result["refusals"][n]={
                                    "step":step,
                                    "reason":"ROBUST_BOUND_OR_REPRESENTABILITY_REJECTED",
                                    "certificate":certificate.reason.value,
                                    "possible_targets":certificate.hypotheses,
                                    "worst_position_m":certificate.worst_position_inf_m,
                                    "worst_rotation_rad":certificate.worst_orientation_geodesic_rad,
                                }
                                done[n]=True
                                continue

                    if not maybe_two:
                        if n=="fault_oracle_private_target":
                            previous=None  # original compiler reads actual native target.
                        elif n in observers:
                            previous=as_pose(observers[n].pose)
                        else:
                            previous=as_pose(beliefs[n].hypotheses[0])
                        rewritten,reason,amp=base.normalized_target_delta(
                            src,arm,native,approximate=True,old_override=previous)
                        if rewritten is None:
                            result["refusals"][n]={"step":step,
                                "reason":reason,"required_native_amp":amp}
                            done[n]=True
                            continue
                    if reason=="APPROXIMATE_BOUNDED_PROJECTION":
                        result["native_projection_NOT_EXACT"].setdefault(n,[]).append({
                            "step":step,"exactness":"NOT_EXACT",
                            "native_required_amplitude":amp
                        })
                    gripper=controllers["source_no_fault"].to_action_dict(
                        native[0])["gripper"]
                    intended=rewritten[0].detach().cpu().numpy()
                    if n in beliefs:
                        ticket=beliefs[n].prepare(intended)
                    elif n in observers:
                        ticket=observers[n].prepare(intended).ticket
                    if step==FAULT_STEP:
                        delivered=torch.zeros_like(rewritten[0])
                        result["faults"][n]={
                            "step":step,"actual_native_arm_command":"all_zero_hold",
                            "original_desired_arm_action_l2":float(np.linalg.norm(intended)),
                            "controller_execution_ack_seen_by_adapter":"unknown"
                        }
                    else:
                        delivered=rewritten[0]
                    action=c.from_action_dict({
                        "arm":delivered,"gripper":gripper
                    }).reshape(1,-1)
                observations[n],_,terminated,truncated,info=w.step(action)
                if n in beliefs:
                    beliefs[n].acknowledge(
                        ticket,
                        applied=None if step==FAULT_STEP else True)
                elif n in observers:
                    # ACK always unknown in experiment. Optimist deliberately
                    # assumes it arrived; query arm invalidates then reinitializes.
                    ack=None if (step==FAULT_STEP and
                        n=="fault_always_single_privileged_query") else True
                    observers[n].acknowledge(ticket,applied=ack)
                if certificate is not None and certificate.authorized:
                    # AUDIT-ONLY get_state AFTER env.step. Never inserted into
                    # next policy/observer command. Counts separated from queries.
                    actual=privileged_target(arm)
                    pa,ra=audit_pose_error(actual,desired)
                    accepted=(pa<=certificate.worst_position_inf_m+1e-4 and
                              ra<=certificate.worst_orientation_geodesic_rad+1e-4)
                    if not accepted:
                        raise RuntimeError("Robust certified setpoint violated in real controller")
                    result["robust_native_target_bound_checks"].setdefault(n,[]).append({
                        "step":step,"position_error_m":pa,
                        "rot_error_rad":ra,
                        "worst_case_position_limit_m":certificate.worst_position_inf_m,
                        "worst_case_rot_limit_rad":certificate.worst_orientation_geodesic_rad,
                        "only_audit_after_physical_dispatch":True
                    })
                if info.get("success") is None:
                    raise RuntimeError("Missing actual official ManiSkill task success")
                success=base._bool_value(info["success"])
                result["success_once"][n]|=success
                if success and result["success_step"][n] is None:
                    result["success_step"][n]=step+1
                result["steps"][n]=step+1
                done[n]=base._bool_value(terminated) or base._bool_value(truncated)
            if all(done.values()):
                break
        for n in NAMES[1:]:
            result["faults"].setdefault(n,None)
        print("ACK_BOUNDED_QUERY_ORIGINAL_EPISODE",json.dumps(result,sort_keys=True))
        return result
    finally:
        for w in worlds.values():w.close()


def main():
    task,path,sha,_=base.TASKS[TASK]
    if task!=TASK_NAME:raise RuntimeError("Published task registry changed")
    model=Path(hf_hub_download(
        repo_id=base.REPO,filename=path,
        revision=base.PUBLISHED_MODEL_REVISION))
    digest=hashlib.sha256(model.read_bytes()).hexdigest()
    if digest!=sha:raise RuntimeError("Changed third-party frozen model hash")
    env=base.env("pd_ee_delta_pose")
    try:
        obs,_=env.reset(seed=next(iter(SEEDS)))
        base.POLICY_OBS_DIM=int(obs.shape[-1])
        policy=base._actor(
            torch.load(model,map_location="cpu",weights_only=True),
            base.POLICY_OBS_DIM,7)
    finally:
        env.close()
    rows=[trial(policy,int(seed)) for seed in SEEDS]
    assert len(rows)==8 and [r["seed"] for r in rows]==list(SEEDS)
    record={
        "schema":"certify_query_nonadaptive_budget_placebo_new64_v1",
        "frozen_protocol":PROTO,
        "task":TASK_NAME,"original_seed_population":list(SEEDS),
        "original_external_frozen_checkpoint_sha256":digest,
        "frozen_model_retrained":False,
        "real_physx_simulator":True,
        "fault_is_native_target_hold_not_network_loss":True,
        "privileged_readback_counts_are_decision_only_not_audit_reads":True,
        "all_eight_actual_control_arms":list(NAMES),
        "original_source_method_git_blob":"1dc653cdc44e422c8340475ad00f828b3a41eb4f",
        "original_robust_certifier_git_blob":"bb5fd155b7291fb127f94138fca321201c8271c3",
        "precommitted_query_placebo":"one privileged target read at t3 if seed%4 == 0; else no reads; independent of prior task observations",
        "episodes":rows,
        "success_counts":{n:sum(int(r["success_once"][n]) for r in rows)
                          for n in NAMES},
        "fault_reached_counts":{n:sum(r["faults"].get(n) is not None
                                    for r in rows) for n in NAMES[1:]},
        "periodic_readback_counts":[
            r["privileged_target_readback_decision_count"][PERIODIC] for r in rows],
        "selective_readback_counts":[
            r["privileged_target_readback_decision_count"][
                "fault_robust_then_single_privileged_query"] for r in rows],
        "robust_no_query_authorization_count":sum(
            r["robust_common_action_authorizations"].get(
                "fault_robust_two_history_without_query",0) for r in rows),
        "independent_external_reproduction":False,
        "physical_robot_safety_certified":False
    }
    p=f"query_placebo_{TASK}_chunk{CHUNK}_original8.json"
    Path(p).write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("QUERY_PLACEBO_EIGHT_ARM_PHYSX_SUMMARY",json.dumps({
        "task":TASK,"success":record["success_counts"],
        "fault_reached":record["fault_reached_counts"],
        "readbacks":record["selective_readback_counts"],
        "robust_authorizations_no_query":record["robust_no_query_authorization_count"]
    },sort_keys=True))


if __name__=="__main__":
    main()
