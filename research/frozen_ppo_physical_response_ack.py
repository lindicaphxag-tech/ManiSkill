"""Prospective real PhysX: physical-response read-free ACK ambiguity probe.

One common zero-target-native arm action after unknown ACK. Uses achieved
end-effector position only to decide which *commanded* target history matches.
Never uses target memory getter to choose blind commands. Getter is permitted
once after probe in the privileged comparator, and after trial for AUDIT only.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import torch
from huggingface_hub import hf_hub_download

import frozen_ppo_action_history_observer as original
from frozen_ppo_observer_policy import REPO, _actor
from action_abi_history_observer import ActionHistoryObserver
from frozen_ppo_unknown_ack_recovery import pose_record, target_record, as_pose, discrepancy
from physical_response_classifier import pure_classification

TASK=os.environ["ABI_TASK"]
FAULT=os.environ["ABI_FAULT"]
FIRST={"pull_cube":140001,"stack_cube":150001}
if TASK not in FIRST or FAULT not in ("applied_no_ack","neutral_arm_delta_no_ack"):
    raise RuntimeError("Only preregistered task/fault permitted")
START=int(os.environ.get("ABI_START","0"))
if START not in (0,4):
    raise ValueError("Four per-shard registered states; start=0 or 4 only")
SEEDS=tuple(range(FIRST[TASK]+START,FIRST[TASK]+START+4))
DROPPED=FAULT=="neutral_arm_delta_no_ack"
STEP_FAULT=2
STEP_PROBE=3
MARGIN_M=0.002
PROTOCOL="research/PHYSICAL_RESPONSE_ACK_PROSPECTIVE_V1.json"
FREEZE_COMMIT="f237fadb70895bc94889f3ff44cb6c41d296b323"
ARMS=("source_pause_no_fault","blind_probe_optimistic",
      "blind_probe_pessimistic","achieved_probe_classifier",
      "privileged_once_after_probe")


def make_observer(arm):
    c=arm.config
    x=ActionHistoryObserver(c.pos_lower,c.pos_upper,c.rot_lower,
                            frame=c.frame,use_delta=c.use_delta,
                            use_target=c.use_target,
                            normalize_action=c.normalize_action)
    x.reset(pose_record(arm))
    return x


def actual_xyz(arm):
    # Public achieved kinematics; neither controller.target_pose nor _target_pose.
    return np.asarray(arm.ee_pose_at_base.p.detach().cpu(),
                      dtype=np.float64).reshape(-1,3)[0].copy()


def trial(policy,seed):
    worlds={a:original.env("pd_ee_delta_pose" if a=="source_pause_no_fault"
                            else "pd_ee_target_delta_pose") for a in ARMS}
    rec=dict(seed=seed,task=original.TASK_NAME,unknown_ack_truth=FAULT,
             fault_step=STEP_FAULT,probe_step=STEP_PROBE,
             steps={},success_once={},fault_reached={},probe_reached={},
             initial_obs_diff={},projections={},refusals={},
             private_memory_reads_during_action_decision={a:0 for a in ARMS},
             classifier=None,wrong_authorization=None,
             probe_positions={},candidate_goal_positions={},
             privileged_read_residual_m=None,
             end_audit_target_residual={})
    try:
        obs={a:w.reset(seed=seed)[0] for a,w in worlds.items()}
        canonical=original._project_policy_observation(
            obs["source_pause_no_fault"],worlds["source_pause_no_fault"])
        for name in ARMS[1:]:
            flat=original._project_policy_observation(obs[name],
                             worlds[name],verify_memory=False)
            error=float(torch.max(torch.abs(flat-canonical)).item())
            rec["initial_obs_diff"][name]=error
            if error>5e-4:
                raise RuntimeError("Different task or robot state at paired reset")
        controllers={a:w.unwrapped.agent.controller for a,w in worlds.items()}
        src_arm=controllers["source_pause_no_fault"].controllers["arm"]
        observers={a:make_observer(controllers[a].controllers["arm"])
                   for a in ARMS[1:]}
        hypotheses={}
        last_gripper={}
        done={a:False for a in ARMS}
        for t in range(original.STEPS):
            for name,w in worlds.items():
                if done[name]:
                    continue
                if t>STEP_PROBE and name=="achieved_probe_classifier" and (
                        rec["classifier"] is not None and
                        rec["classifier"]["label"] is None):
                    rec["refusals"][name]={"step":t,
                       "reason":"AMBIGUOUS_ACHIEVED_RESPONSE_NO_TARGET_GETTER"}
                    done[name]=True
                    continue
                ctrl=controllers[name]
                arm=ctrl.controllers["arm"]
                if t==STEP_PROBE:
                    if name not in last_gripper:
                        raise RuntimeError("Missing preceding source gripper command")
                    # Active physical measurement: zero target-native 6D arm,
                    # unchanged gripper from last native PPO action.
                    action=ctrl.from_action_dict({
                        "arm":torch.zeros_like(last_gripper[name][0]),
                        "gripper":last_gripper[name][1]}).reshape(1,-1)
                    before_xyz=actual_xyz(arm)
                    obs[name],_,term,trunc,info=w.step(action)
                    after_xyz=actual_xyz(arm)
                    rec["probe_reached"][name]=True
                    rec["probe_positions"][name]={
                        "achieved_pre_probe_xyz":before_xyz.tolist(),
                        "achieved_post_probe_xyz":after_xyz.tolist(),
                        "motion_m":float(np.linalg.norm(after_xyz-before_xyz))}
                    if name in ("blind_probe_optimistic","blind_probe_pessimistic"):
                        # These maintained a single valid guessed target; one
                        # zero target-native delta leaves its target unchanged.
                        tracker=observers[name]
                        ticket=tracker.prepare(np.zeros(6,dtype=np.float32))
                        tracker.acknowledge(ticket.ticket,applied=True)
                    # Ambiguous belief and privileged comparator were
                    # intentionally invalidated by UNKNOWN ACK: they are
                    # resynchronized only after this physical response.
                    if name=="achieved_probe_classifier":
                        if name not in hypotheses:
                            raise RuntimeError("No untrusted candidate histories")
                        h,a=hypotheses[name]
                        classification=pure_classification(
                            after_xyz,h.position,a.position)
                        rec["classifier"]=classification
                        label=classification["label"]
                        rec["wrong_authorization"]=(
                            (label != ("held" if DROPPED else "applied"))
                            if label is not None else None)
                        rec["candidate_goal_positions"]={
                            "held":list(h.position),"applied":list(a.position)}
                        if label is not None:
                            observers[name].reset(a if label=="applied" else h)
                    elif name=="privileged_once_after_probe":
                        # Stronger-information ceiling: EXACTLY one private
                        # memory getter here, never used by blind arms.
                        truth=target_record(arm)
                        rec["private_memory_reads_during_action_decision"][name]=1
                        observers[name].reset(truth)
                        rec["privileged_read_residual_m"]=discrepancy(
                            observers[name].pose,truth)["position_m"]
                else:
                    native=original.act(policy,
                       original._project_policy_observation(
                            obs[name],w,verify_memory=False))
                    if name=="source_pause_no_fault":
                        action=native
                        parts=ctrl.to_action_dict(native[0])
                        if t==STEP_FAULT:
                            last_gripper[name]=(parts["arm"].clone(),
                                                parts["gripper"].clone())
                    else:
                        tracker=observers[name]
                        prior=as_pose(tracker.pose)
                        rewritten,reason,amplitude=original.normalized_target_delta(
                           src_arm,arm,native,approximate=True,
                           old_override=prior)
                        if rewritten is None:
                            rec["refusals"][name]={"step":t,
                               "reason":reason,"required_amplitude":amplitude}
                            done[name]=True
                            continue
                        if reason=="APPROXIMATE_BOUNDED_PROJECTION":
                            rec["projections"].setdefault(name,[]).append(
                                {"step":t,"amplitude":amplitude,
                                 "exactness":"NOT_EXACT"})
                        parts=controllers["source_pause_no_fault"].to_action_dict(
                            native[0])
                        dispatched=rewritten[0].clone()
                        if t==STEP_FAULT and DROPPED:
                            dispatched=torch.zeros_like(dispatched)
                        action=ctrl.from_action_dict({
                            "arm":dispatched,"gripper":parts["gripper"]
                        }).reshape(1,-1)
                        pending=tracker.prepare(rewritten[0].detach().cpu().numpy())
                        if t==STEP_FAULT:
                            last_gripper[name]=(dispatched.clone(),parts["gripper"].clone())
                            # Candidate = pre-fault held pose, or fully
                            # acknowledged dispatched commanded-target pose.
                            old=tracker.pose
                            clone=make_observer(arm)
                            clone.reset(old)
                            ticket=clone.prepare(rewritten[0].detach().cpu().numpy())
                            clone.acknowledge(ticket.ticket,applied=True)
                            hypotheses[name]=(old,clone.pose)
                    obs[name],_,term,trunc,info=w.step(action)
                    if name in observers:
                        tracker=observers[name]
                        if t==STEP_FAULT:
                            rec["fault_reached"][name]=True
                            if name=="blind_probe_optimistic":
                                tracker.acknowledge(pending.ticket,applied=True)
                            elif name=="blind_probe_pessimistic":
                                tracker.acknowledge(pending.ticket,applied=False)
                            else:
                                tracker.acknowledge(pending.ticket,applied=None)
                        else:
                            tracker.acknowledge(pending.ticket,applied=True)
                val=info.get("success")
                if val is None:
                    raise RuntimeError("No official native task success flag")
                rec["success_once"][name]=(rec["success_once"].get(name,False)
                                              or original._bool_value(val))
                rec["steps"][name]=t+1
                done[name]=original._bool_value(term) or original._bool_value(trunc)
            if all(done.values()):
                break
        # Audit strictly after all control decisions and closed-loop steps.
        for name in ARMS[1:]:
            if not rec["probe_reached"].get(name,False):
                continue
            tracker=observers[name]
            if not tracker._valid:
                continue
            truth=target_record(controllers[name].controllers["arm"])
            rec["end_audit_target_residual"][name]=discrepancy(
                  tracker.pose,truth)
        for name in ARMS:
            rec["fault_reached"].setdefault(name,False)
            rec["probe_reached"].setdefault(name,False)
            rec["success_once"].setdefault(name,False)
        print("PHYSICAL_RESPONSE_EPISODE",json.dumps(rec,sort_keys=True))
        return rec
    finally:
        for w in worlds.values():
            w.close()


def main():
    info=original.TASKS[TASK]
    path=Path(hf_hub_download(repo_id=REPO,filename=info[1],
                               revision=original.PUBLISHED_MODEL_REVISION))
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=info[2]:
        raise RuntimeError("Published frozen PPO SHA256 changed")
    env0=original.env("pd_ee_delta_pose")
    try:
        obs,_=env0.reset(seed=SEEDS[0])
        original.POLICY_OBS_DIM=int(obs.shape[-1])
        policy=_actor(torch.load(path,map_location="cpu",weights_only=True),
                      original.POLICY_OBS_DIM,7)
    finally:
        env0.close()
    rows=[trial(policy,seed) for seed in SEEDS]
    counts={a:sum(bool(x["success_once"][a]) for x in rows) for a in ARMS}
    chosen=sum(x["classifier"] is not None and
               x["classifier"]["label"] is not None for x in rows)
    wrong=sum(x["wrong_authorization"] is True for x in rows)
    data=dict(schema="physical_response_ack_ambiguity_frozen_ppo_prospective_v1",
              protocol=PROTOCOL,preoutcome_frozen_commit=FREEZE_COMMIT,
              task=original.TASK_NAME,truth=FAULT,seeds=list(SEEDS),
              third_party_checkpoint_sha256=digest,
              published_revision=original.PUBLISHED_MODEL_REVISION,
              training_performed=False,real_physx=True,
              success_count=counts,classification_covered=chosen,
              false_history_authorizations=wrong,rows=rows)
    out=Path(f"physical_response_{TASK}_{FAULT}_{START}_fresh4.json")
    out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("PHYSICAL_RESPONSE_PHYSX_SUMMARY",json.dumps({
        "task":original.TASK_NAME,"fault":FAULT,"n":len(rows),
        "success":counts,"classified":chosen,"wrong_authorizations":wrong,
        "probe_reached":{a:sum(r["probe_reached"][a] for r in rows)
                         for a in ARMS}},sort_keys=True))


if __name__=="__main__":
    main()
