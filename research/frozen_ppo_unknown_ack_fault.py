"""Original frozen-PPO PhysX arm-hold fault: unknown delivery at one fixed step.

Six genuinely closed-loop control arms (not offline replay). Predeclared
cohorts and fixed fault step in CST_FAULT_ACK_PREDECLARED_V1.json.
No training. No independent robot/hardware or physical safety claim.

"Lost arm command" here is *implemented as a target-hold zero native arm
command* in ManiSkill during an otherwise normal physics step, with original
policy gripper command retained. It is not a network packet-loss simulator.
"""
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import torch
from scipy.spatial.transform import Rotation
from huggingface_hub import hf_hub_download

import frozen_ppo_action_history_observer as base
from action_abi_history_observer import ActionHistoryObserver, TargetPose
from action_abi_uncertain_delivery_belief import UncertainDeliveryBelief
from mani_skill.utils.structs import Pose

PREDECLARED={
    "pull_cube": ("PullCube-v1",range(102001,102009)),
    "stack_cube": ("StackCube-v1",range(112001,112009)),
}
MODELS=base.TASKS
NAMES=(
    "source_no_fault",
    "translated_no_fault",
    "fault_privileged_private_goal",
    "fault_optimistic_action_history",
    "fault_public_observation_one_shot_resync",
    "fault_finite_belief_exact_refusal",
)
FAULT_STEP=2
STEPS=50
TASK=os.environ.get("ABI_TASK")
if TASK not in PREDECLARED:
    raise ValueError("Invalid frozen task; preregistered pull_cube or stack_cube only")
TASK_NAME,SEEDS=PREDECLARED[TASK]
assert MODELS[TASK][0]==TASK_NAME


def target(pose):
    p=np.asarray(pose.p.detach().cpu(),dtype=float).reshape(-1,3)[0]
    q=np.asarray(pose.q.detach().cpu(),dtype=float).reshape(-1,4)[0]
    return TargetPose.from_arrays(p,q[[1,2,3,0]])


def as_maniskill_pose(pose):
    q=np.asarray(pose.quaternion_xyzw,dtype=np.float32)
    return Pose.create_from_pq(
        torch.as_tensor(np.asarray(pose.position,dtype=np.float32)).reshape(1,3),
        torch.as_tensor(q[[3,0,1,2]]).reshape(1,4))


def observed_target(observation,world):
    """Read ONLY the native public state observation; do not call get_state."""
    obs=torch.as_tensor(observation)
    agent=world.unwrapped.agent
    offset=(int(agent.robot.get_qpos().shape[-1])
           +int(agent.robot.get_qvel().shape[-1]))
    if obs.ndim!=2 or obs.shape[0]!=1 or obs.shape[-1]!=base.POLICY_OBS_DIM+7:
        raise RuntimeError("Public target-state observation unavailable")
    tensor=obs[0,offset:offset+7]
    if tensor.numel()!=7:
        raise RuntimeError("No public target state available: refuse resync")
    a=np.asarray(tensor.detach().cpu(),dtype=float)
    return TargetPose.from_arrays(a[:3],a[[4,5,6,3]])


def create_observer(arm):
    cfg=arm.config
    instance=ActionHistoryObserver(
        cfg.pos_lower,cfg.pos_upper,cfg.rot_lower,frame=cfg.frame,
        use_delta=cfg.use_delta,use_target=cfg.use_target,
        normalize_action=cfg.normalize_action)
    instance.reset(target(arm.ee_pose_at_base))
    return instance


def fault_trial(actor,seed):
    worlds={
        name:base.env("pd_ee_delta_pose" if name=="source_no_fault"
                      else "pd_ee_target_delta_pose")
        for name in NAMES
    }
    record={
        "seed":seed,"initial_physical_obs_sha256":None,
        "initial_observation_max_abs_diff":{},
        "success_once":{name:False for name in NAMES},
        "success_step":{name:None for name in NAMES},
        "steps":{},"faults":{},"approximations":{},
        "refusals":{},"resync":{},
        "target_memory_terminal_error":{},
        "belief_branches_after_unknown":None,
    }
    try:
        observations={k:w.reset(seed=seed)[0] for k,w in worlds.items()}
        source_obs=base._project_policy_observation(
            observations["source_no_fault"],worlds["source_no_fault"])
        record["initial_physical_obs_sha256"]=hashlib.sha256(
            source_obs.detach().cpu().contiguous().numpy().tobytes()
        ).hexdigest()
        for name in NAMES[1:]:
            converted=base._project_policy_observation(
                observations[name],worlds[name],verify_memory=False)
            difference=float(torch.max(torch.abs(converted-source_obs)))
            record["initial_observation_max_abs_diff"][name]=difference
            if difference>5e-4:
                raise RuntimeError("Nonpaired initial state "+name)
        controllers={k:w.unwrapped.agent.controller for k,w in worlds.items()}
        arms={k:c.controllers["arm"] for k,c in controllers.items()}
        source_arm=arms["source_no_fault"]
        observers={
            k:create_observer(arms[k])
            for k in ("fault_optimistic_action_history",
                      "fault_public_observation_one_shot_resync")
        }
        bname="fault_finite_belief_exact_refusal"
        bc=arms[bname].config
        belief=UncertainDeliveryBelief(bc.pos_lower,bc.pos_upper,bc.rot_lower)
        belief.reset(target(arms[bname].ee_pose_at_base))
        done={k:False for k in NAMES}
        for step in range(STEPS):
            for name in NAMES:
                if done[name]:
                    continue
                w=worlds[name]
                obs=base._project_policy_observation(
                    observations[name],w,
                    verify_memory=(name in ("source_no_fault","translated_no_fault",
                                            "fault_privileged_private_goal")))
                policy_native=base.act(actor,obs)
                if name=="source_no_fault":
                    action=policy_native
                else:
                    arm=arms[name]
                    if name in observers:
                        prior=as_maniskill_pose(observers[name].pose)
                    elif name==bname:
                        if len(belief.hypotheses)>1:
                            decoded=source_arm._preprocess_action(policy_native[:,:6])
                            desired=source_arm.compute_target_pose(
                                arm.ee_pose_at_base,decoded)
                            cert=belief.certify_common_exact_action(target(desired))
                            record.setdefault("belief_certificates",[]).append({
                                "step":step,"authorized":cert.authorized,
                                "reason":cert.reason,"possible_targets":cert.possible_targets,
                                "maximum_native_spread":cert.maximum_native_spread
                            })
                            if not cert.authorized:
                                record["refusals"][name]={
                                    "step":step,"reason":cert.reason,
                                    "possible_targets":cert.possible_targets,
                                    "maximum_native_spread":cert.maximum_native_spread
                                }
                                done[name]=True
                                continue
                            rewritten=torch.tensor(
                                cert.native_action,dtype=policy_native.dtype).reshape(1,6)
                            reason=None
                            amplitude=None
                        else:
                            prior=as_maniskill_pose(belief.hypotheses[0])
                    else:
                        prior=None
                    if not (name==bname and len(belief.hypotheses)>1):
                        rewritten,reason,amplitude=base.normalized_target_delta(
                            source_arm,arm,policy_native,
                            approximate=True,old_override=prior)
                    if rewritten is None:
                        record["refusals"][name]={
                            "step":step,"reason":reason,"required_amp":amplitude
                        }
                        done[name]=True
                        continue
                    if reason=="APPROXIMATE_BOUNDED_PROJECTION":
                        record["approximations"].setdefault(name,[]).append({
                            "step":step,"exactness":"NOT_EXACT",
                            "required_native_amp":amplitude
                        })
                    gripper=controllers["source_no_fault"].to_action_dict(
                        policy_native[0])["gripper"]
                    planned=rewritten[0].detach().cpu().numpy()
                    if name in observers:
                        ticket=observers[name].prepare(planned).ticket
                    elif name==bname:
                        ticket=belief.prepare(planned)
                    if name in NAMES[2:] and step==FAULT_STEP:
                        # Intervention is an *arm target hold*: zero native
                        # target-delta, original policy gripper still executes.
                        delivered=torch.zeros_like(rewritten[0])
                        record["faults"][name]={
                            "step":step,"intervention":"hold_native_arm_zero",
                            "requested_arm_native_norm":float(np.linalg.norm(planned)),
                            "acknowledgement_visible_to_adapter":"unknown"
                        }
                    else:
                        delivered=rewritten[0]
                    action=controllers[name].from_action_dict({
                        "arm":delivered,"gripper":gripper
                    }).reshape(1,-1)
                observations[name],_,terminal,truncated,info=w.step(action)
                if name in observers:
                    # Optimistic and observation-resync arms both treat the
                    # *issued* command as accepted until the resync channel.
                    observers[name].acknowledge(ticket,applied=True)
                    if (name=="fault_public_observation_one_shot_resync"
                            and step==FAULT_STEP):
                        correction=observed_target(observations[name],w)
                        observers[name].reset(correction)
                        record["resync"][name]={
                            "step":step,"source":"public_state_observation_7d_target_pose",
                            "private_controller_getter_used":False
                        }
                elif name==bname:
                    belief.acknowledge(
                        ticket,applied=None if step==FAULT_STEP else True)
                    if step==FAULT_STEP:
                        record["belief_branches_after_unknown"]=len(belief.hypotheses)
                if info.get("success") is None:
                    raise RuntimeError("Missing official task success flag")
                succeeded=base._bool_value(info["success"])
                record["success_once"][name]|=succeeded
                if succeeded and record["success_step"][name] is None:
                    record["success_step"][name]=step+1
                record["steps"][name]=step+1
                done[name]=base._bool_value(terminal) or base._bool_value(truncated)
            if all(done.values()):
                break
        # TRUE controller memory is read only after all policy actions are
        # decided; this is outcome auditing, never an observer input.
        for name in observers:
            arm=arms[name]
            actual=arm.get_state()["target_pose"].detach().cpu().numpy().reshape(-1,7)[0]
            estimate=observers[name].pose
            qreal=base.rot_from_wxyz(actual[3:])
            qest=Rotation.from_quat(estimate.quaternion_xyzw)
            record["target_memory_terminal_error"][name]={
                "max_position_abs_m":float(np.max(np.abs(
                    actual[:3]-np.asarray(estimate.position)))),
                "rotation_rad":float((qreal*qest.inv()).magnitude())
            }
        print("CST_FAULT_ACK_EPISODE",json.dumps(record,sort_keys=True))
        return record
    finally:
        for w in worlds.values():
            w.close()


def main():
    task,filename,expected,_=MODELS[TASK]
    assert task==TASK_NAME
    file=Path(hf_hub_download(
        repo_id=base.REPO,filename=filename,
        revision=base.PUBLISHED_MODEL_REVISION))
    actual=hashlib.sha256(file.read_bytes()).hexdigest()
    if actual!=expected:
        raise RuntimeError("External frozen PPO checkpoint hash mismatch")
    first=base.env("pd_ee_delta_pose")
    try:
        initial,_=first.reset(seed=list(SEEDS)[0])
        base.POLICY_OBS_DIM=initial.shape[-1]
        actor=base._actor(
            torch.load(file,map_location="cpu",weights_only=True),
            int(initial.shape[-1]),7)
    finally:
        first.close()
    episodes=[fault_trial(actor,int(s)) for s in SEEDS]
    if len(episodes)!=8 or [q["seed"] for q in episodes]!=list(SEEDS):
        raise RuntimeError("Missing preregistered denominator")
    report={
        "protocol":"research/CST_FAULT_ACK_PREDECLARED_V1.json",
        "task":task,"seeds":list(SEEDS),"checkpoint_sha256":actual,
        "training_performed":False,"simulator":"ManiSkill PhysX CPU",
        "fault":"fixed step-2 target-native arm hold, original gripper still executes",
        "not_network_loss_simulator":True,
        "episodes":episodes,
        "success_counts":{n:sum(int(ep["success_once"][n]) for ep in episodes)
                          for n in NAMES},
        "fault_reached_counts":{n:sum(n in ep["faults"] for ep in episodes)
                                for n in NAMES[2:]},
        "belief_refusal_count":sum(
            "fault_finite_belief_exact_refusal" in ep["refusals"]
            for ep in episodes)
    }
    name="cst_fault_ack_"+TASK+"_8.json"
    Path(name).write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("CST_FAULT_ACK_SUMMARY",json.dumps({
        "task":task,"counts":report["success_counts"],
        "fault_reached":report["fault_reached_counts"],
        "belief_refusal":report["belief_refusal_count"]
    },sort_keys=True))


if __name__=="__main__":
    main()
