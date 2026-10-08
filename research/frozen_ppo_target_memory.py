"""Frozen PPO under achieved-delta vs target-delta controller semantics.

No training. Controller interface can refuse nonrepresentable target memory
translations rather than silently clipping and claiming exact transfer.
"""
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from huggingface_hub import hf_hub_download
from target_memory_feasibility import compile_target_memory_action, TransportDecision

import mani_skill.envs  # noqa F401

from frozen_ppo_pickcube_gate import (
    _actor, _bool_value, REPO, FILENAME, EXPECTED,
)

REPO="kattri15/actionshift-baselines"
FILENAME="ppo/push_cube_final_ckpt.pt"
EXPECTED="a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf"
TASK="PushCube-v1"
SEEDS=tuple(range(31001,31033))
STEPS=50
TOL=1e-5


def env(mode):
    return gym.make(TASK,num_envs=1,obs_mode="state",
                    sim_backend="physx_cpu",reconfiguration_freq=1,
                    control_mode=mode,disable_env_checker=True)


def rot_from_wxyz(wxyz):
    q=np.asarray(wxyz,dtype=float).reshape(-1,4)[0]
    return Rotation.from_quat([q[1],q[2],q[3],q[0]])


def normalized_target_delta(source_arm,target_arm,policy_native, *, approximate=False):
    """Compile exact/approximate target-native pose command with checkable witness."""
    previous=target_arm._target_pose
    if previous is None:
        return None,"missing live controller target pose",None,None,None
    delta=source_arm._preprocess_action(policy_native[:,:6])
    desired=source_arm.compute_target_pose(target_arm.ee_pose_at_base,delta)
    actual=compile_target_memory_action(
        np.asarray(previous.p.detach().cpu(),dtype=float).reshape(-1,3)[0],
        rot_from_wxyz(previous.q).as_matrix(),
        np.asarray(desired.p.detach().cpu(),dtype=float).reshape(-1,3)[0],
        rot_from_wxyz(desired.q).as_matrix(),
        pos_lower=float(source_arm.config.pos_lower),
        pos_upper=float(source_arm.config.pos_upper),
        rotation_native_scale=float(source_arm.config.rot_lower),
        mode="project" if approximate else "strict",
        feasibility_tolerance=1e-5,
    )
    if not actual.executable:
        return None,actual.reason,actual.required_native_amplitude,actual,desired
    rewritten=torch.as_tensor(actual.native_action,dtype=policy_native.dtype).reshape(1,6)
    reason="APPROXIMATE_BOUNDED_PROJECTION" if actual.decision is TransportDecision.APPROXIMATE else None
    return rewritten,reason,actual.required_native_amplitude,actual,desired


def _project_policy_observation(flat_observation, environment, expected_width):
    """Project target controller observations back into the source ABI.

    ManiSkill's state observation order is: agent.qpos, agent.qvel,
    agent.controller.target_pose (7D when use_target=True), task.extra.
    The frozen PPO was trained without the controller target-pose field.
    Do not merely truncate: preserve all task.extra coordinates.
    """
    obs=torch.as_tensor(flat_observation)
    if obs.ndim != 2 or obs.shape[0] != 1:
        raise RuntimeError("Unexpected state observation batch shape")
    agent=environment.unwrapped.agent
    arm=agent.controller.controllers["arm"]
    nq=int(agent.robot.get_qpos().shape[-1])
    nv=int(agent.robot.get_qvel().shape[-1])
    if agent.controller.controllers["arm"].config.use_target:
        memory=arm.get_state().get("target_pose")
        if memory is None:
            raise RuntimeError("Controller target memory missing: refuse projection")
        memory=torch.as_tensor(memory,device=obs.device,dtype=obs.dtype)
        if memory.shape[-1]!=7 or obs.shape[-1]!=expected_width+7:
            raise RuntimeError("Target observation ABI changed; cannot project")
        offset=nq+nv
        actual=obs[:,offset:offset+7]
        if not torch.allclose(actual,memory,atol=1e-5,rtol=0):
            raise RuntimeError("Observation controller-state slice mismatches live target memory")
        converted=torch.cat([obs[:,:offset],obs[:,offset+7:]],dim=1)
        if converted.shape[-1]!=expected_width:
            raise RuntimeError("Projected observation ABI does not equal original checkpoint input width")
        return converted
    if obs.shape[-1]!=expected_width:
        raise RuntimeError("Source observation ABI does not equal checkpoint input width")
    return obs


def act(policy,observation):
    with torch.no_grad():
        return policy(observation.detach().cpu().float()).clip(-1,1)


def trial(policy, seed):
    worlds={
        "source":env("pd_ee_delta_pose"),
        "memory":env("pd_ee_target_delta_pose"),
        "projected":env("pd_ee_target_delta_pose"),
        "naive":env("pd_ee_target_delta_pose"),
    }
    policy_input_width=int(policy[0].in_features)
    outcome={"seed":seed,"task":TASK,"checkpoint_observation_width":policy_input_width,"initial_obs_diff":{},"success_once":{},
             "steps":{},"refusals":{},"approximations":{},"physical_witness_checks":0,
             "max_witness_position_residual_error_m":0.0,
             "max_witness_orientation_residual_error_rad":0.0,
             "max_required_native_amp":0.0}
    try:
        observations={k:w.reset(seed=seed)[0] for k,w in worlds.items()}
        canonical_start=_project_policy_observation(observations["source"],worlds["source"],policy_input_width)
        for key in ("memory","projected","naive"):
            projected=_project_policy_observation(observations[key],worlds[key],policy_input_width)
            diff=float(torch.max(torch.abs(canonical_start-projected)).item())
            outcome["initial_obs_diff"][key]=diff
            if diff>5e-4:
                raise RuntimeError(f"Nonidentical physical/task initial state {key}: {diff}")
        controller={k:w.unwrapped.agent.controller for k,w in worlds.items()}
        source_arm=controller["source"].controllers["arm"]
        done={k:False for k in worlds}
        for t in range(STEPS):
            for name,w in worlds.items():
                if done[name]:
                    continue
                native=act(policy,_project_policy_observation(observations[name],w,policy_input_width))
                if name in ("memory","projected"):
                    arm=controller[name].controllers["arm"]
                    rewritten,reason,amplitude,witness,requested_pose=normalized_target_delta(
                        source_arm,arm,native,approximate=(name=="projected"))
                    if reason == "APPROXIMATE_BOUNDED_PROJECTION":
                        outcome["approximations"].setdefault(name,[]).append({
                            "step":t,"required_native_amp":amplitude,
                            "exactness":"NOT_EXACT",
                        })
                    if amplitude is not None:
                        outcome["max_required_native_amp"]=max(
                            outcome["max_required_native_amp"],amplitude)
                    if rewritten is None:
                        outcome["refusals"][name]={
                            "step":t,"reason":reason,"required_amp":amplitude
                        }
                        done[name]=True
                        continue
                    source_parts=controller["source"].to_action_dict(native[0])
                    action=controller[name].from_action_dict({
                        "arm":rewritten[0],"gripper":source_parts["gripper"]
                    }).reshape(1,-1)
                else:
                    action=native
                observations[name],_,term,trunc,info=w.step(action)
                if name in ("memory","projected"):
                    # Verify that the ACTUAL physics controller's updated
                    # target pose agrees with the witness predicted residual.
                    final_pose=controller[name].controllers["arm"]._target_pose
                    if final_pose is None or witness is None:
                        raise RuntimeError("Controller lost target memory after applying witness")
                    pos_now=np.asarray(final_pose.p.detach().cpu()).reshape(-1,3)[0]
                    pos_want=np.asarray(requested_pose.p.detach().cpu()).reshape(-1,3)[0]
                    pos_actual=float(np.linalg.norm(pos_now-pos_want))
                    ori_actual=float((rot_from_wxyz(requested_pose.q)*rot_from_wxyz(final_pose.q).inv()).magnitude())
                    dp=abs(pos_actual-witness.position_goal_residual_m)
                    dr=abs(ori_actual-witness.orientation_goal_residual_rad)
                    outcome["physical_witness_checks"]+=1
                    outcome["max_witness_position_residual_error_m"]=max(
                        outcome["max_witness_position_residual_error_m"],dp)
                    outcome["max_witness_orientation_residual_error_rad"]=max(
                        outcome["max_witness_orientation_residual_error_rad"],dr)
                    if dp>5e-5 or dr>5e-5:
                        raise RuntimeError(
                            f"Actual controller target disagreed with executable "
                            f"feasibility witness: dp={dp}, dr={dr}, mode={name}"
                        )
                val=info.get("success")
                if val is None:
                    raise RuntimeError("Missing actual PickCube success flag")
                outcome["success_once"][name]=(
                    outcome["success_once"].get(name,False) or _bool_value(val)
                )
                outcome["steps"][name]=t+1
                done[name]=_bool_value(term) or _bool_value(trunc)
            if all(done.values()):
                break
        print("FROZEN_TARGET_MEMORY_EPISODE",json.dumps(outcome,sort_keys=True))
        return outcome
    finally:
        for x in worlds.values():
            x.close()


def main():
    file=Path(hf_hub_download(repo_id=REPO,filename=FILENAME))
    sha=hashlib.sha256(file.read_bytes()).hexdigest()
    if sha!=EXPECTED:
        raise RuntimeError("Published frozen model hash changed")
    env0=env("pd_ee_delta_pose")
    try:
        observation,_=env0.reset(seed=SEEDS[0])
        actor=_actor(torch.load(file,map_location="cpu",weights_only=True),
                     int(observation.shape[-1]),7)
    finally:
        env0.close()
    records=[trial(actor,seed) for seed in SEEDS]
    counts={key:sum(x["success_once"].get(key,False) for x in records)
            for key in ("source","memory","projected","naive")}
    refusals=sum("memory" in x["refusals"] for x in records)
    data={"task":TASK,"checkpoint_file":FILENAME,"checkpoint_sha256":sha,"public_pretrained":True,
          "training_performed":False,"backend":"physx_cpu",
          "controller_contracts":{
             "source":"pd_ee_delta_pose achieved-relative",
             "memory":"pd_ee_target_delta_pose with live previous-target inversion",
             "projected":"pd_ee_target_delta_pose with bounded non-exact projection",
             "naive":"pd_ee_target_delta_pose direct-copy"},
          "success_count":counts,"refused_episodes":refusals,"episodes":records}
    Path("frozen_ppo_target_memory.json").write_text(json.dumps(data,indent=2))
    print("FROZEN_TARGET_MEMORY_SUMMARY",json.dumps({
        "task":TASK,"success":counts,"refused":refusals,
        "approximate_steps":sum(len(x["approximations"].get("projected",[])) for x in records),
        "episodes":len(records)}))


if __name__=="__main__":
    main()
