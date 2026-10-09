"""Prospective NATIVE PhysX four physical ACK truths with equal common neutral probing.

Both missing ACKs (t2 and t3) are physically APPLIED/HELD on new reset seeds.
One known-delivered neutral motion step (t4) is shared by every FAULTED arm.
All native setpoint certificates concern targets, NOT robot/hardware safety.
Neither controller truth bit is accessible to the public action decision.
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
from research.multi_ack_se3_bounded import common_multi_history_command
from research.two_history_se3_robust import Reason
from research.empirical_probe_response_classifier import EPSILON_BY_TASK,_segment_min_distance

TASK=os.environ.get("ABI_TASK")
COHORT={
    "pull_cube":("PullCube-v1",range(1280001,1280009)),
    "stack_cube":("StackCube-v1",range(1290001,1290009))
}
if TASK not in COHORT:
    raise ValueError("ABI_TASK must name one of two frozen task/checkpoint cohorts")
TASK_NAME,SEEDS=COHORT[TASK]
FAULT_STEP=2
FAULT_STEPS=(2,3)
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
    "fault_always_single_privileged_query",
    "fault_assume_held_without_query",
    "fault_public_t3_fourhistory_or_t4_query"
)
PUBLIC_ARM=NAMES[-1]
BELIEF_ARMS=NAMES[3:6]+(PUBLIC_ARM,)
PROTO="research/TWO_UNKNOWN_ACK_TRUE_2X2_PPO64_PREOUTCOME_V1.json"


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
    return common_multi_history_command(
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
    # This modular schedule is source-audit ground truth, NEVER decision input.
    # 0 HH, 1 AH, 2 HA, 3 AA, with independent balanced 2x2 strata.
    truth_index=(int(seed)-1)%4
    t2_physically_applied=truth_index in (1,3)
    t3_physically_applied=truth_index in (2,3)
    result={
        "original_precommitted_physical_t2_execution_truth":("applied" if t2_physically_applied else "held"),
        "original_precommitted_physical_t3_execution_truth":("applied" if t3_physically_applied else "held"),
        "physical_truth_index_seed_mod4_AUDIT_ONLY":truth_index,
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
        "audit_only_native_hold_checks":{},
        "failure_causes":{},
        "success_step":{n:None for n in NAMES},
        "public_t3_evidence":{},
        "shared_neutral_probe_step4":{},
        "public_motion_observation_cost_samples":{n:0 for n in NAMES}
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
            "fault_always_single_privileged_query",
            "fault_assume_held_without_query"
        )}
        beliefs={n:belief(arms[n]) for n in BELIEF_ARMS}
        done={n:False for n in NAMES}
        result["max_belief_width"]={n:1 for n in BELIEF_ARMS}
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
                # Fixed readback is delayed until AFTER t4 neutral probe. This
                # comparator issues a genuinely physical t3 action using its
                # stale (unverified) command-target belief, then resynchronizes
                # with ONE counted private target read at t5.
                if n=="fault_always_single_privileged_query" and step==3:
                    old=as_pose(observers[n].pose)
                    rewritten,reason,amp=base.normalized_target_delta(
                        src,arm,native,approximate=True,old_override=old)
                    if rewritten is None:
                        result["refusals"][n]={"step":step,"reason":reason,
                            "native_amplitude":amp,"negative_pre_second_fault":True}
                        done[n]=True
                        continue
                    original=rewritten[0]
                    actual_apply=t3_physically_applied
                    delivered=(original if actual_apply else
                               torch.zeros_like(original))
                    goal_before=privileged_target(arm)  # AUDIT ONLY
                    gripper=controllers["source_no_fault"].to_action_dict(
                        native[0])["gripper"]
                    action=c.from_action_dict({
                        "arm":delivered,"gripper":gripper}).reshape(1,-1)
                    result["faults"].setdefault(n,[]).append({
                        "step":3,
                        "actual_native_arm_command":("native_intended_action_physically_applied"
                            if actual_apply else "all_zero_hold"),
                        "actual_native_6d_dispatched":[float(v) for v in delivered.detach().cpu().numpy()],
                        "actual_native_action_is_precommitted_applied":actual_apply,
                        "controller_execution_ack_seen_by_adapter":"unknown",
                        "fixed_baseline_target_belief_stale_until_step5":True,
                    })
                    observations[n],_,terminated,truncated,info=w.step(action)
                    goal_after=privileged_target(arm)  # AUDIT ONLY
                    pos,rot=audit_pose_error(goal_after,goal_before)
                    if not actual_apply and (pos>1e-4 or rot>1e-4):
                        raise RuntimeError("FIXED_COMPARATOR_SECOND_HELD_TARGET_CHANGED")
                    result["audit_only_native_hold_checks"].setdefault(n,[]).append({
                        "step":3,"audit_only_target_delta_inf_m":pos,
                        "audit_only_target_rot_change_rad":rot,
                        "expected_physical_execution_truth":("applied" if actual_apply else "held"),
                        "target_reads_not_exposed_to_controller_decisions":True,
                        "actual_native_action_physically_dispatched":True})
                    result["faults"][n][-1].update({
                        "actual_native_precommitted_execution_truth":("applied" if actual_apply else "held"),
                        "audit_only_after_real_step_target_delta_inf_m":pos,
                        "audit_only_after_real_step_target_rot_change_rad":rot})
                    if info.get("success") is None:
                        raise RuntimeError("Missing official native task result")
                    success=base._bool_value(info["success"])
                    result["success_once"][n]|=success
                    if success and result["success_step"][n] is None:
                        result["success_step"][n]=step+1
                    result["steps"][n]=step+1
                    done[n]=base._bool_value(terminated) or base._bool_value(truncated)
                    continue
                if n!="source_no_fault" and step==4:
                    before_target=privileged_target(arm)  # AUDIT ONLY
                    if n==PUBLIC_ARM:
                        result["public_t3_evidence"]["before_xyz"]=(
                            np.asarray(arm.ee_pose_at_base.p.detach().cpu(),dtype=float)
                            .reshape(-1,3)[0].tolist())
                        result["public_motion_observation_cost_samples"][n]+=1
                    gripper=controllers["source_no_fault"].to_action_dict(
                        native[0])["gripper"]
                    noop=torch.zeros_like(native[0,:6])
                    action=c.from_action_dict({"arm":noop,
                         "gripper":gripper}).reshape(1,-1)
                    observations[n],_,terminated,truncated,info=w.step(action)
                    after_target=privileged_target(arm)  # AUDIT ONLY
                    pos,rot=audit_pose_error(before_target,after_target)
                    if pos>1e-4 or rot>1e-4:
                        raise RuntimeError("KNOWN_DELIVERED_NEUTRAL_PROBE_MOVED_TARGET")
                    result["shared_neutral_probe_step4"][n]={
                        "step":4,"native_six_dim_arm":[0.0]*6,
                        "physically_dispatched":True,
                        "known_delivered_no_new_unknown_ack":True,
                        "audit_only_target_position_delta_m":pos,
                        "audit_only_target_orientation_delta_rad":rot}
                if n==PUBLIC_ARM and step==4:
                    ev=result["public_t3_evidence"]
                    after=np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                                     dtype=float).reshape(-1,3)[0]
                    before=np.asarray(ev["before_xyz"],dtype=float)
                    ev["after_xyz"]=after.tolist()
                    result["public_motion_observation_cost_samples"][n]+=1
                    hyps=tuple(beliefs[n].hypotheses)
                    eps=EPSILON_BY_TASK[TASK]
                    ev["physical_candidate_count"]=len(hyps)
                    ev["prior_training_epsilon_m"]=eps
                    ev["candidate_residuals_m"]=[
                        _segment_min_distance(before,after,np.asarray(h.position))[0]
                        for h in hyps]
                    ev["accepted_position_indices"]=[
                        i for i,d in enumerate(ev["candidate_residuals_m"])
                        if d<=eps+1e-12]
                    # Position alone cannot eliminate a distinct orientation-only
                    # latent history when the actuator and task also use orientation.
                    rots=[Rotation.from_quat(h.quaternion_xyzw) for h in hyps]
                    ev["max_hypothetical_rotation_spread_rad"]=max(
                        (rots[i].inv()*rots[j]).magnitude()
                        for i in range(len(rots)) for j in range(i+1,len(rots))
                    ) if len(rots)>1 else 0.0
                    winners=ev["accepted_position_indices"]
                    ev["authorized"]=bool(len(winners)==1 and
                        all(d>eps+.002 for i,d in enumerate(ev["candidate_residuals_m"])
                            if i!=winners[0]))
                    ev["selected_candidate_index"]=winners[0] if ev["authorized"] else None
                    ev["failure_reason"]=("unique_complete_history_by_public_position_witness"
                        if ev["authorized"] else "ambiguous_or_empirical_model_invalid")
                    # A private target getter is permitted AFTER physical actuation
                    # FOR AUDIT ONLY. It MUST NOT enter any decision-time branch.
                    truth=privileged_target(arm)
                    errors=[audit_pose_error(truth,h) for h in hyps]
                    ev["after_physics_audit_pose_errors"]=errors
                    ev["audit_only_true_candidate_indices"]=[
                        i for i,(pos,rot) in enumerate(errors)
                        if pos<=1e-4 and rot<=1e-3]
                    ev["wrong_confident"]=bool(
                        ev["authorized"] and winners[0] not in
                        ev["audit_only_true_candidate_indices"])
                    ev["audit_only_hidden_target_was_NOT_decision_input"]=True
                    ev["empirical_motion_envelope_NOT_physical_safety_certificate"]=True
                    if info.get("success") is None:
                        raise RuntimeError("Missing official native task success")
                    success=base._bool_value(info["success"])
                    result["success_once"][n]|=success
                    if success and result["success_step"][n] is None:
                        result["success_step"][n]=step+1
                    result["steps"][n]=step+1
                    done[n]=base._bool_value(terminated) or base._bool_value(truncated)
                    continue
                certificate=None
                desired=None
                if n=="source_no_fault":
                    action=native
                else:
                    name_belief=n in beliefs
                    if n==PUBLIC_ARM and step==5:
                        ev=result.get("public_t3_evidence",{})
                        if ev.get("authorized") is True:
                            idx=ev["selected_candidate_index"]
                            if idx<0 or idx>=len(beliefs[n].hypotheses):
                                raise RuntimeError("Stale public branch index, refuse")
                            # Empirical, not physically certified! Preserve source decision,
                            # separately record any post-physical audit-only wrong labels.
                            beliefs[n].reset(beliefs[n].hypotheses[idx])
                            ev["resync_source"]="empirical_public_achieved_motion"
                        else:
                            actual=privileged_target(arm)
                            beliefs[n].require_external_resync(actual)
                            result["privileged_target_readback_decision_count"][n]+=1
                            ev["resync_source"]="one_counted_authoritative_controller_target_read"
                    maybe_two=(name_belief and len(beliefs[n].hypotheses)>1)
                    if n=="fault_always_single_privileged_query" and step==5:
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
                    try:
                        if n in beliefs:
                            ticket=beliefs[n].prepare(intended)
                        elif n in observers:
                            ticket=observers[n].prepare(intended).ticket
                    except ValueError as err:
                        # A source-pretrained policy can propose an
                        # unrepresentable SO(3) command BEFORE the registered
                        # fault. This is a pre-fault failure, NOT an injected
                        # ACK trial. Preserve the entire seed denominator.
                        if str(err) not in (
                            "Unrepresentable target rotation",
                            "Unrepresentable target translation"):
                            raise
                        result["refusals"][n]={
                            "step":step,
                            "reason":"NATIVE_HISTORY_PREPARE_UNREPRESENTABLE",
                            "original_error":str(err),
                            "preserve_original_source_seed_as_failure":True}
                        result["failure_causes"][n]="NATIVE_HISTORY_PREPARE_UNREPRESENTABLE"
                        done[n]=True
                        continue
                    pre_fault_native_target=(privileged_target(arm)
                        if step in FAULT_STEPS else None)
                    # Audit-only private getter; NEVER a policy/decision input.
                    if step in FAULT_STEPS:
                        actual_apply=bool((step==2 and t2_physically_applied) or
                                          (step==3 and t3_physically_applied))
                        delivered=(rewritten[0] if actual_apply else
                                   torch.zeros_like(rewritten[0]))
                        result["faults"].setdefault(n,[]).append({
                            "step":step,
                            "actual_native_arm_command":(
                                "native_intended_action_physically_applied"
                                if actual_apply else "all_zero_hold"),
                            "actual_native_6d_dispatched":[float(v) for v in delivered.detach().cpu().numpy().tolist()],
                            "actual_native_action_is_precommitted_applied":actual_apply,
                            "original_desired_arm_action_l2":float(np.linalg.norm(intended)),
                            "controller_execution_ack_seen_by_adapter":"unknown"
                        })
                    else:
                        delivered=rewritten[0]
                    action=c.from_action_dict({
                        "arm":delivered,"gripper":gripper
                    }).reshape(1,-1)
                observations[n],_,terminated,truncated,info=w.step(action)
                if n in beliefs:
                    beliefs[n].acknowledge(
                        ticket,
                        applied=None if step in FAULT_STEPS else True)
                    result["max_belief_width"][n]=max(
                        result["max_belief_width"][n],len(beliefs[n].hypotheses))
                elif n in observers:
                    # ACK always unknown in experiment. Optimist deliberately
                    # assumes it arrived; query arm invalidates then reinitializes.
                    ack=None if (step in FAULT_STEPS and
                        n=="fault_always_single_privileged_query") else True
                    if n=="fault_assume_held_without_query" and step in FAULT_STEPS:
                        # Deliberately assumes both commands were HELD. This zero-read
                        # strong falsifier has NO physical ACK or test-seed parity access.
                        ack=False
                    observers[n].acknowledge(ticket,applied=ack)
                if n!="source_no_fault" and step in FAULT_STEPS:
                    actual_after=privileged_target(arm)
                    pos,rot=audit_pose_error(actual_after,pre_fault_native_target)
                    physically_applied=((step==2 and t2_physically_applied) or
                                        (step==3 and t3_physically_applied))
                    if not physically_applied and (pos>1e-4 or rot>1e-4):
                        raise RuntimeError(
                            f"NATIVE_ZERO_HOLD_DID_NOT_HOLD_TARGET task={TASK} "
                            f"seed={seed} step={step} arm={n} position={pos} rot={rot}")
                    result["audit_only_native_hold_checks"].setdefault(n,[]).append({
                        "step":step,"audit_only_target_delta_inf_m":pos,
                        "audit_only_target_rot_change_rad":rot,
                        "expected_physical_execution_truth":"applied" if physically_applied else "held",
                        "private_target_getter_audit_only_count":2,
                        "target_reads_not_exposed_to_controller_decisions":True,
                        "actual_native_action_physically_dispatched":True
                    })
                    result["faults"][n][-1].update({
                        "actual_native_precommitted_execution_truth":(
                            "applied" if physically_applied else "held"),
                        "audit_only_after_real_step_target_delta_inf_m":pos,
                        "audit_only_after_real_step_target_rot_change_rad":rot,
                        "actual_native_held_target_verified":not physically_applied,
                        "actual_applied_action_dispatched_not_claimed_safety":physically_applied
                    })
                if certificate is not None and certificate.authorized and step in FAULT_STEPS and not ((step==2 and t2_physically_applied) or (step==3 and t3_physically_applied)):
                    # Source-native fault forcibly replaces the authorized command
                    # with a ZERO/HOLD command. We must NEVER assert that an
                    # unapplied hypothetical command reached its certified goal.
                    # Preserve this attempted action as a masked certificate.
                    result.setdefault("certified_action_masked_by_injected_fault",{}).setdefault(n,[]).append({
                        "step":step,
                        "fault_truth":"arm command was physically replaced by zero",
                        "native_action_did_not_execute":True,
                        "postdispatch_certificate_check_not_applicable":True,
                        "claimed_physical_setpoint_certificate":False,
                    })
                if certificate is not None and certificate.authorized and (step not in FAULT_STEPS or (step==2 and t2_physically_applied) or (step==3 and t3_physically_applied)):
                    # Only a real dispatched bounded action is eligible for an
                    # AFTER-step physical target-memory audit. The accessor below
                    # is audit-only, never a decision-time observation.
                    actual=privileged_target(arm)
                    pa,ra=audit_pose_error(actual,desired)
                    accepted=(pa<=certificate.worst_position_inf_m+1e-4 and
                              ra<=certificate.worst_orientation_geodesic_rad+1e-4)
                    if not accepted:
                        raise RuntimeError(
                            f"UNMASKED CERTIFICATE VIOLATION task={TASK} seed={seed} arm={n} "
                            f"step={step} pos={pa:.9f} bound={certificate.worst_position_inf_m:.9f} "
                            f"rot={ra:.9f} bound={certificate.worst_orientation_geodesic_rad:.9f} "
                            f"all_hypotheses={certificate.hypotheses}"
                        )
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
            result["faults"].setdefault(n,[])
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
        "schema":"frozen_ppo_2x2_native_ack_truth_probe_at_step4_v1",
        "frozen_protocol":PROTO,
        "task":TASK_NAME,"original_seed_population":list(SEEDS),
        "original_external_frozen_checkpoint_sha256":digest,
        "frozen_model_retrained":False,
        "real_physx_simulator":True,
        "two_consecutive_unknown_ack_target_hold_steps":list(FAULT_STEPS),
        "both_physical_fault_target_reads_are_audit_only":True,
        "preoutcome_protocol":PROTO,
        "multi_belief_max_hypotheses":16,
        "fault_is_native_target_hold_not_network_loss":True,
        "privileged_readback_counts_are_decision_only_not_audit_reads":True,
        "all_nine_actual_control_arms":list(NAMES),
        "episodes":rows,
        "success_counts":{n:sum(int(r["success_once"][n]) for r in rows)
                          for n in NAMES},
        "fault_reached_counts":{n:sum(len(r["faults"].get(n,[]))==2
                                    for r in rows) for n in NAMES[1:]},
        "actual_native_ack_intervention_event_counts":{n:sum(len(r["faults"].get(n,[]))
                                    for r in rows) for n in NAMES[1:]},
        "selective_readback_counts":[
            r["privileged_target_readback_decision_count"][
                "fault_robust_then_single_privileged_query"] for r in rows],
        "robust_no_query_authorization_count":sum(
            r["robust_common_action_authorizations"].get(
                "fault_robust_two_history_without_query",0) for r in rows),
        "public_fourhistory_method":PUBLIC_ARM,
        "both_physical_ack_truths_balanced_over_seed_mod4":True,
        "second_ACK_mixed_physical_truth":True,
        "shared_known_delivered_neutral_probe_step4":True,
        "first_private_readback_fixed_at_step5":True,
        "explicit_zero_read_always_assume_held_comparator":"fault_assume_held_without_query",
        "full_history_index_vs_coordinatewise_rotation_agreement_v2":True,
        "empirical_public_model_not_attested":True,
        "public_exposure_attempt_counts":{n:sum(r["public_motion_observation_cost_samples"].get(n,0) for r in rows) for n in NAMES},
        "independent_external_reproduction":False,
        "physical_robot_safety_certified":False
    }
    p=f"mixed_ack_{TASK}_original8.json"
    Path(p).write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("COMPOUND_MULTI_ACK_REAL_PHYSX",json.dumps({
        "task":TASK,"success":record["success_counts"],
        "fault_reached":record["fault_reached_counts"],
        "public_evidence":[r["public_t3_evidence"] for r in rows],
        "readbacks":record["selective_readback_counts"],
        "robust_authorizations_no_query":record["robust_no_query_authorization_count"],
        "max_belief_width_by_arm":{n:max(r["max_belief_width"][n] for r in rows)
                for n in BELIEF_ARMS},
        "per_episode_max_belief_width":[r["max_belief_width"] for r in rows]
    },sort_keys=True))


if __name__=="__main__":
    main()
