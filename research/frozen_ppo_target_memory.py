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

import mani_skill.envs  # noqa F401

from frozen_ppo_pickcube_gate import (
    _actor, _bool_value, REPO, FILENAME, EXPECTED,
)

SEEDS=tuple(range(22001,22033))
STEPS=50
TOL=1e-5


def env(mode):
    return gym.make("PickCube-v1",num_envs=1,obs_mode="state",
                    sim_backend="physx_cpu",reconfiguration_freq=1,
                    control_mode=mode,disable_env_checker=True)


def rot_from_wxyz(wxyz):
    q=np.asarray(wxyz,dtype=float).reshape(-1,4)[0]
    return Rotation.from_quat([q[1],q[2],q[3],q[0]])


def normalized_target_delta(source_arm,target_arm,policy_native, *, approximate=False, old_pose_override=None):
    """Inverts physical achieved-relative EE goal into target-relative ABI."""
    old=target_arm._target_pose if old_pose_override is None else old_pose_override
    if old is None:
        return None,"controller runtime previous target memory missing",None

    # Decode policy's original normalized achieved-relative command.
    delta=source_arm._preprocess_action(policy_native[:,:6])
    desired=source_arm.compute_target_pose(target_arm.ee_pose_at_base,delta)
    desired_pos=np.asarray(desired.p.detach().cpu(),dtype=float).reshape(-1,3)[0]
    old_pos=np.asarray(old.p.detach().cpu(),dtype=float).reshape(-1,3)[0]
    desired_R=rot_from_wxyz(desired.q)
    old_R=rot_from_wxyz(old.q)

    physical_pos=desired_pos-old_pos
    physical_euler=(desired_R*old_R.inv()).as_euler("XYZ")
    lower=float(source_arm.config.pos_lower)
    upper=float(source_arm.config.pos_upper)
    rot_scale=float(source_arm.config.rot_lower)
    if abs(rot_scale)<1e-8 or upper <= lower:
        return None,"ill-defined controller action limits",None

    # Inverse of ManiSkill's native bounded pos affine scaling:
    # physical delta = (u+1)/2*(upper-lower)+lower.
    pos_native=2*(physical_pos-lower)/(upper-lower)-1
    # PDEEPoseController._clip_and_scale_action multiplies native Euler
    # vector by config.rot_lower, clipping its Euclidean norm to <=1.
    rot_native=physical_euler/rot_scale
    amp=float(max(np.max(np.abs(pos_native)),np.linalg.norm(rot_native)))
    if not np.all(np.isfinite(pos_native)) or not np.all(np.isfinite(rot_native)):
        return None,"nonfinite target action",amp
    if amp>1+TOL:
        if not approximate:
            return None,"required delta outside target native bounds",amp
        # Experimental non-exact fallback: Euclidean closest normalized
        # position command (box) and rotation command (unit ball).
        pos_native=np.clip(pos_native,-1.0,1.0)
        rot_len=float(np.linalg.norm(rot_native))
        if rot_len>1.0:
            rot_native=rot_native/rot_len
        return torch.as_tensor(np.r_[pos_native,rot_native],
                               dtype=policy_native.dtype).reshape(1,6),"APPROXIMATE_BOUNDED_PROJECTION",amp
    return torch.as_tensor(np.r_[pos_native,rot_native],
                           dtype=policy_native.dtype).reshape(1,6),None,amp


def _project_policy_observation(flat_observation, environment):
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
        if memory.shape[-1]!=7 or obs.shape[-1]!=49:
            raise RuntimeError("Target observation ABI changed; cannot project")
        offset=nq+nv
        actual=obs[:,offset:offset+7]
        if not torch.allclose(actual,memory,atol=1e-5,rtol=0):
            raise RuntimeError("Observation controller-state slice mismatches live target memory")
        converted=torch.cat([obs[:,:offset],obs[:,offset+7:]],dim=1)
        if converted.shape[-1]!=42:
            raise RuntimeError("Projected observation ABI is not source policy's 42D input")
        return converted
    if obs.shape[-1]!=42:
        raise RuntimeError("Source observation ABI is not 42D")
    return obs


def act(policy,observation):
    with torch.no_grad():
        return policy(observation.detach().cpu().float()).clip(-1,1)


def trial(policy, seed):
    worlds={
        "source":env("pd_ee_delta_pose"),
        "memory":env("pd_ee_target_delta_pose"),
        "projected":env("pd_ee_target_delta_pose"),
        "memory_blind":env("pd_ee_target_delta_pose"),
        "naive":env("pd_ee_target_delta_pose"),
    }
    outcome={"seed":seed,"initial_obs_diff":{},"success_once":{},
             "steps":{},"refusals":{},"approximations":{},"max_required_native_amp":0.0}
    try:
        observations={k:w.reset(seed=seed)[0] for k,w in worlds.items()}
        canonical_start=_project_policy_observation(observations["source"],worlds["source"])
        for key in ("memory","projected","memory_blind","naive"):
            projected=_project_policy_observation(observations[key],worlds[key])
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
                native=act(policy,_project_policy_observation(observations[name],w))
                if name in ("memory","projected","memory_blind"):
                    arm=controller[name].controllers["arm"]
                    # Controlled ablation uses achieved pose as a false
                    # previous target; actual controller uses its own memory.
                    wrong_previous_target=(
                        arm.ee_pose_at_base if name=="memory_blind" else None
                    )
                    rewritten,reason,amplitude=normalized_target_delta(
                        source_arm,arm,native,
                        approximate=(name!="memory"),
                        old_pose_override=wrong_previous_target,
                    )
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
            for key in ("source","memory","projected","memory_blind","naive")}
    refusals=sum("memory" in x["refusals"] for x in records)
    data={"checkpoint_sha256":sha,"public_pretrained":True,
          "training_performed":False,"backend":"physx_cpu",
          "controller_contracts":{
             "source":"pd_ee_delta_pose achieved-relative",
             "memory":"pd_ee_target_delta_pose with live previous-target inversion",
             "projected":"pd_ee_target_delta_pose with bounded non-exact projection",
             "memory_blind":"pd_ee_target_delta_pose with achieved-as-previous-target ablation, bounded projection",
             "naive":"pd_ee_target_delta_pose direct-copy"},
          "success_count":counts,"refused_episodes":refusals,"episodes":records}
    Path("frozen_ppo_target_memory.json").write_text(json.dumps(data,indent=2))
    print("FROZEN_TARGET_MEMORY_SUMMARY",json.dumps({
        "success":counts,"refused":refusals,
        "approximate_steps":sum(len(x["approximations"].get("projected",[])) for x in records),
        "episodes":len(records)}))


if __name__=="__main__":
    main()
