"""Prospective PhysX TWO UNKNOWN ACKs: conservative multi-hypothesis bounded-or-query.

Nine separately physically stepped comparator controllers per original source reset seed.
Full two-ACK joint truth protocol registered before this implementation.
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
from research.multi_ack_se3_bounded import common_multi_history_command
from research.two_history_se3_robust import Reason
from research.empirical_probe_response_classifier import EPSILON_BY_TASK,_segment_min_distance

TASK=os.environ.get("ABI_TASK")
COHORT={
    "pull_cube":("PullCube-v1",range(1020101,1020109)),
    "stack_cube":("StackCube-v1",range(1030101,1030109))
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
    "fault_public_t4_original_eps_or_t5_query",
    "fault_robust_first_public_second_or_query",
    "fault_contact_precision_aef_1cm_or_query"
)
PUBLIC_ARM=NAMES[-2]
STRICT_ARM=NAMES[-1]
NARROW_ARM=NAMES[-3]
HYBRID_ARMS=(PUBLIC_ARM,STRICT_ARM)
PUBLIC_ARMS=(NARROW_ARM,PUBLIC_ARM,STRICT_ARM)
BELIEF_ARMS=NAMES[3:6]+PUBLIC_ARMS
CONTACT_STACK_POSITION_BUDGET_M=.01
CONTACT_STACK_ROTATION_BUDGET_RAD=.02
DRIVE_MODES={
    "slow":{"stiffness":500.0,"damping":70.0,"force_limit":100.0},
    "fast":{"stiffness":1500.0,"damping":130.0,"force_limit":100.0},
}
PROTO="research/AEF_STACK_CONTACT_PRECISION_NEW64_PREOUTCOME_V1.json"


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


def geometry(arm, prior_candidates, desired, *, position_budget_m=None, rotation_budget_rad=None):
    c=arm.config
    if c.frame!="root_translation:root_aligned_body_rotation":
        raise RuntimeError("Unverified native controller action chart")
    low=np.asarray(arm.action_space_low[:3].detach().cpu(),dtype=float)
    high=np.asarray(arm.action_space_high[:3].detach().cpu(),dtype=float)
    return common_multi_history_command(
        tuple(prior_candidates),desired,
        pos_lower=low,pos_upper=high,rot_lower=float(c.rot_lower),
        position_budget_m=(POS_BUDGET if position_budget_m is None else float(position_budget_m)),
        rotation_budget_rad=(ROT_BUDGET if rotation_budget_rad is None else float(rotation_budget_rad)),
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


def set_physical_arm_joint_drive(w,mode):
    """Actually change/verify PhysX Panda arm PD drives. Audit-only mode ID.

    No policy observation, public-model decision or native target-history
    hypothesis receives this mode. This is a domain-randomization injector.
    """
    settings=DRIVE_MODES[mode]
    robot=w.unwrapped.agent.robot
    matches=[]
    original=[]
    for joint in robot.joints:
        name=str(joint.name)
        if name not in {f"panda_joint{i}" for i in range(1,8)}:
            continue
        def scalar(z):
            if hasattr(z,"detach"):
                z=z.detach().cpu().numpy()
            a=np.asarray(z,dtype=float).ravel()
            if len(a)!=1:
                raise RuntimeError("Not a single actual real CPU native PhysX joint")
            return float(a[0])
        original.append({"joint":name,
                         "stiffness":scalar(joint.stiffness),
                         "damping":scalar(joint.damping)})
        joint.set_drive_properties(
            stiffness=settings["stiffness"],
            damping=settings["damping"],
            force_limit=settings["force_limit"])
        measured=(scalar(joint.stiffness),scalar(joint.damping))
        if abs(measured[0]-settings["stiffness"])>1e-4 or abs(measured[1]-settings["damping"])>1e-4:
            raise RuntimeError("PhysX stiffness/damping injection NOT physically applied")
        matches.append(name)
    if len(matches)!=7 or len(set(matches))!=7:
        raise RuntimeError(f"Physical Panda seven-joint domain shift failed: {matches}")
    return {"domain_mode_injector_AUDIT_ONLY":mode,
            "all_seven_physical_Panda_joint_drives_modified_and_read_back":True,
            "original_joint_drive_parameters":original,
            "actual_joint_parameters_after_setter":settings,
            "verified_arm_joints":sorted(matches)}


def trial(policy,seed):
    worlds={
        n:base.env("pd_ee_delta_pose" if n=="source_no_fault"
                   else "pd_ee_target_delta_pose")
        for n in NAMES
    }
    t2_physically_applied=(int(seed)%2==0)
    t3_physically_applied=((int(seed)//2)%2==0)
    result={
        "original_precommitted_physical_t2_execution_truth":("applied" if t2_physically_applied else "held"),
        "original_precommitted_physical_t3_execution_truth":("applied" if t3_physically_applied else "held"),
        "physical_truth_condition_uses_seed_parity_AUDIT_ONLY":True,
        "four_joint_execution_outcomes_physically_realized_across_cohort":True,
        "known_delivered_zero_probe":{},
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
        "public_t4_evidence":{n:{} for n in PUBLIC_ARMS},
        "hybrid_authority_trace":{n:{} for n in HYBRID_ARMS},
        "domain_shift_actual_physx_readback_AUDIT_ONLY":{},
        "public_motion_observation_cost_samples":{n:0 for n in NAMES}
    }
    try:
        observations={n:w.reset(seed=seed)[0] for n,w in worlds.items()}
        drive_mode="slow" if (int(seed)//4)%2==0 else "fast"
        result["actual_domain_mode_source_seed_assignment_AUDIT_ONLY"]=drive_mode
        for n,w in worlds.items():
            result["domain_shift_actual_physx_readback_AUDIT_ONLY"][n]=(
                set_physical_arm_joint_drive(w,drive_mode))
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
                # Exactly ONE additional KNOWN-DELIVERED neutral native command
                # after BOTH unknown executions, across ALL nine controllers.
                # No hidden getter is used by the public inference at t4.
                if step==4:
                    public_ev=result["public_t4_evidence"].get(n)
                    if n in PUBLIC_ARMS:
                        public_ev["before_xyz"]=(
                            np.asarray(arm.ee_pose_at_base.p.detach().cpu(),dtype=float)
                            .reshape(-1,3)[0].tolist())
                        result["public_motion_observation_cost_samples"][n]+=1
                    prior=(privileged_target(arm) if n!="source_no_fault" else None)
                    gripper=controllers["source_no_fault"].to_action_dict(
                        native[0])["gripper"]
                    zero=torch.zeros_like(native[0,:6])
                    neutral_action=c.from_action_dict({
                        "arm":zero,"gripper":gripper}).reshape(1,-1)
                    observations[n],_,terminated,truncated,info=w.step(neutral_action)
                    if prior is not None:
                        final=privileged_target(arm)  # AFTER physical step AUDIT ONLY
                        dpos,drot=audit_pose_error(final,prior)
                        if dpos>1e-4 or drot>1e-4:
                            raise RuntimeError("KNOWN_DELIVERED_ZERO_CHANGED_TARGET "
                                f"task={TASK} seed={seed} arm={n} position={dpos} rotation={drot}")
                    result["known_delivered_zero_probe"][n]={
                        "step":4,"actual_native_6d_dispatched":[0.]*6,
                        "acknowledgement":"known_applied",
                        "is_extra_common_physical_action":True,
                        "audit_only_native_target_unchanged":prior is not None,
                        "public_before_after_xyz_used_by_policy":n in PUBLIC_ARMS}
                    if n in PUBLIC_ARMS and step==4:
                        ev=result["public_t4_evidence"][n]
                        after=np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                                         dtype=float).reshape(-1,3)[0]
                        before=np.asarray(ev["before_xyz"],dtype=float)
                        ev["after_xyz"]=after.tolist()
                        result["public_motion_observation_cost_samples"][n]+=1
                        hyps=tuple(beliefs[n].hypotheses)
                        eps=float(EPSILON_BY_TASK[TASK])
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
                        pure_authorize=bool(len(winners)==1 and
                            all(d>eps+.002 for i,d in enumerate(ev["candidate_residuals_m"])
                                if i!=winners[0]))
                        ev["ungated_public_compatibility_authorization"]=pure_authorize
                        ev["authorized"]=pure_authorize
                        ev["not_a_physical_safety_certificate"]=True
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
                        raise RuntimeError("Missing official task success on real neutral step")
                    success=base._bool_value(info["success"])
                    result["success_once"][n]|=success
                    if success and result["success_step"][n] is None:
                        result["success_step"][n]=step+1
                    result["steps"][n]=step+1
                    done[n]=base._bool_value(terminated) or base._bool_value(truncated)
                    continue
                # A SECOND intentionally forced native ZERO/HOLD after an
                # unseen first ACK requires NO unauthorized history inversion.
                # The one-read comparator is correctly UNSYNCHRONIZED until
                # its registered authoritative read at step 4. Do not call
                # its observer.prepare at step 3; the physical arm command is
                # zero regardless of what that observer would have planned.
                if (n=="fault_always_single_privileged_query"
                    and step==FAULT_STEPS[1]):
                    goal_before=privileged_target(arm)  # audit ONLY
                    gripper=controllers["source_no_fault"].to_action_dict(
                        native[0])["gripper"]
                    # The second unknown ACK can ACTUALLY execute or hold.
                    # This fixed-query comparator is unsynchronized: dispatch
                    # a concrete normalized SOURCE-native action, NOT a private
                    # target-guided inverse; a single query at t5 resynchronizes.
                    directly_dispatched=(native[0,:6].clone()
                       if t3_physically_applied else torch.zeros_like(native[0,:6]))
                    action=c.from_action_dict({
                        "arm":directly_dispatched,
                        "gripper":gripper}).reshape(1,-1)
                    result["faults"].setdefault(n,[]).append({
                        "step":step,
                        "actual_native_arm_command":("native_intended_source_arm_physically_applied" if t3_physically_applied else "all_zero_hold"),
                        "actual_native_action_is_precommitted_applied":bool(t3_physically_applied),
                        "actual_native_6d_dispatched":[float(q) for q in directly_dispatched.detach().cpu().tolist()],
                        "original_desired_arm_action_l2":float(torch.linalg.norm(
                            native[0,:6]).item()),
                        "controller_execution_ack_seen_by_adapter":"unknown",
                        "no_intended_native_conversion_authorized_while_unsynchronized":True
                    })
                    observations[n],_,terminated,truncated,info=w.step(action)
                    goal_after=privileged_target(arm)  # audit ONLY
                    pos,rot=audit_pose_error(goal_after,goal_before)
                    if not t3_physically_applied and (pos>1e-4 or rot>1e-4):
                        raise RuntimeError(
                            "MANDATORY_SECOND_PHYSICAL_HOLD_TARGET_CHANGED "
                            f"task={TASK} seed={seed} position={pos} rot={rot}")
                    result["audit_only_native_hold_checks"].setdefault(n,[]).append({
                        "step":step,
                        "held_position_error_inf_m":pos,
                        "held_rotation_error_rad":rot,
                        "private_target_getter_audit_only_count":2,
                        "target_reads_not_exposed_to_controller_decisions":True
                    })
                    result["faults"][n][-1].update({
                        "actual_native_target_hold_verified":not t3_physically_applied,
                        "actual_native_execution_truth":"applied" if t3_physically_applied else "held",
                        "actual_native_held_position_error_m":pos,
                        "actual_native_held_rotation_error_rad":rot
                    })
                    # No ACK is asserted and the observer remains invalid.
                    # A SINGLE explicit trusted read at t=5 will reset it.
                    if info.get("success") is None:
                        raise RuntimeError("Missing actual official ManiSkill task success")
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
                    if n in PUBLIC_ARMS and step==5:
                        ev=result["public_t4_evidence"][n]
                        # The novel hybrid FIRST asks whether the desired next
                        # action can be dispatched with a documented bounded
                        # error across ALL currently possible native target
                        # histories. It does NOT identify the real ACK.
                        robust_cert=None
                        if n in HYBRID_ARMS and len(beliefs[n].hypotheses)>1:
                            requested=desired_source_target(src,arm,native)
                            robust_cert=geometry(
                                arm,beliefs[n].hypotheses,requested,
                                position_budget_m=(CONTACT_STACK_POSITION_BUDGET_M
                                    if n==STRICT_ARM and TASK=="stack_cube" else POS_BUDGET),
                                rotation_budget_rad=(CONTACT_STACK_ROTATION_BUDGET_RAD
                                    if n==STRICT_ARM and TASK=="stack_cube" else ROT_BUDGET))
                            ev["robust_first_step5_certificate_authorized"]=robust_cert.authorized
                            ev["robust_first_step5_certificate_reason"]=robust_cert.reason.value
                            ev["robust_first_step5_hypotheses"] = len(beliefs[n].hypotheses)
                        if robust_cert is not None and robust_cert.authorized:
                            # Preserve every candidate native history and
                            # let the actual following step dispatch the
                            # independently recomputed bounded common command.
                            ev["resync_source"]="common_bounded_action_without_latent_history_selection"
                            ev["public_unique_history_used_for_policy"]=False
                        elif ev.get("authorized") is True:
                            idx=ev["selected_candidate_index"]
                            if idx<0 or idx>=len(beliefs[n].hypotheses):
                                raise RuntimeError("Stale public branch index, refuse")
                            beliefs[n].reset(beliefs[n].hypotheses[idx])
                            ev["resync_source"]="empirical_public_achieved_motion"
                            ev["public_unique_history_used_for_policy"]=True
                        else:
                            actual=privileged_target(arm)
                            beliefs[n].require_external_resync(actual)
                            result["privileged_target_readback_decision_count"][n]+=1
                            ev["resync_source"]="one_counted_authoritative_controller_target_read"
                            ev["public_unique_history_used_for_policy"]=False
                    maybe_two=(name_belief and len(beliefs[n].hypotheses)>1)
                    if n=="fault_always_single_privileged_query" and step==max(FAULT_STEPS)+2:
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
                            certificate=geometry(
                                arm,beliefs[n].hypotheses,desired,
                                position_budget_m=(CONTACT_STACK_POSITION_BUDGET_M
                                    if n==STRICT_ARM and TASK=="stack_cube" else POS_BUDGET),
                                rotation_budget_rad=(CONTACT_STACK_ROTATION_BUDGET_RAD
                                    if n==STRICT_ARM and TASK=="stack_cube" else ROT_BUDGET))
                            if certificate.authorized:
                                rewritten=torch.as_tensor(
                                    certificate.normalized_6d,
                                    dtype=native.dtype).reshape(1,6)
                                reason=None
                                amp=None
                                result["robust_common_action_authorizations"][n]=(
                                    result["robust_common_action_authorizations"].get(n,0)+1)
                            elif n in ("fault_robust_then_single_privileged_query",PUBLIC_ARM,STRICT_ARM) and (
                                result["privileged_target_readback_decision_count"][n]==0):
                                # Do NOT pretend the unknown ACK was answered by
                                # state-only observations. Spend one explicitly
                                # privileged read and collapse to the measured state.
                                result["robust_common_action_refusals"].setdefault(n,[]).append({
                                    "step":step,"reason":certificate.reason.value})
                                if n in HYBRID_ARMS:
                                    result["public_t4_evidence"][n]["eventual_robust_fallback_query_step"]=step
                                    result["public_t4_evidence"][n]["resync_source"]="one_counted_authoritative_controller_target_read"
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
                        actual_apply=bool((step==2 and t2_physically_applied) or (step==3 and t3_physically_applied))
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
                    physically_applied=((step==2 and t2_physically_applied) or (step==3 and t3_physically_applied))
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
        "schema":"frozen_ppo_AEF_task_precision_5cm_vs_1cm_real_physx_v8",
        "frozen_protocol":PROTO,
        "task":TASK_NAME,"original_seed_population":list(SEEDS),
        "original_external_frozen_checkpoint_sha256":digest,
        "frozen_model_retrained":False,
        "real_physx_simulator":True,
        "two_consecutive_unknown_ack_target_hold_steps":list(FAULT_STEPS),
        "native_hold_step2_step3_target_reads_audit_only":True,
        "preoutcome_protocol":PROTO,
        "multi_belief_max_hypotheses":16,
        "fault_is_native_target_hold_not_network_loss":True,
        "privileged_readback_counts_are_decision_only_not_audit_reads":True,
        "all_eleven_actual_control_arms":list(NAMES),
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
        "original_narrow_public_model_arm":NARROW_ARM,
        "prior_true_history_calibrated_model_arm":PUBLIC_ARM,
        "prior_max_residual_calibration_fixed_before_all_test_outcomes":None,
        "ood_physical_PD_drive_modes":DRIVE_MODES,
        "hybrid_robust_common_native_action_attempt_precedes_public_history_at_step5":True,
        "stack_strict_precision_position_budget_m":CONTACT_STACK_POSITION_BUDGET_M,
        "stack_strict_precision_rotation_budget_rad":CONTACT_STACK_ROTATION_BUDGET_RAD,
        "strict_precision_AEF_method":STRICT_ARM,
        "five_cm_comparator_AEF_method":PUBLIC_ARM,
        "public_samples_each_public_method":2,
        "domain_mode_NOT_accessible_to_controller_decision":True,
        "first_physical_ack_truth_balanced_by_original_seed_parity":True,
        "second_ack_actual_execution_truth_mixed":True,
        "known_delivered_public_zero_probe_step":4,
        "authoritative_query_after_neutral_probe_step":5,
        "explicit_zero_read_always_assume_held_comparator":"fault_assume_held_without_query",
        "full_history_index_vs_coordinatewise_rotation_agreement_v2":True,
        "empirical_public_model_not_attested":True,
        "public_exposure_attempt_counts":{n:sum(r["public_motion_observation_cost_samples"].get(n,0) for r in rows) for n in NAMES},
        "independent_external_reproduction":False,
        "physical_robot_safety_certified":False
    }
    p=f"aef_precision_{TASK}_original8.json"
    Path(p).write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("COMPOUND_MULTI_ACK_REAL_PHYSX",json.dumps({
        "task":TASK,"success":record["success_counts"],
        "fault_reached":record["fault_reached_counts"],
        "public_evidence":[r["public_t4_evidence"] for r in rows],
        "readbacks":record["selective_readback_counts"],
        "robust_authorizations_no_query":record["robust_no_query_authorization_count"],
        "max_belief_width_by_arm":{n:max(r["max_belief_width"][n] for r in rows)
                for n in BELIEF_ARMS},
        "per_episode_max_belief_width":[r["max_belief_width"] for r in rows]
    },sort_keys=True))


if __name__=="__main__":
    main()
