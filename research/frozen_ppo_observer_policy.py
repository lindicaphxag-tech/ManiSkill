"""Frozen third-party PPO (ActionShift) source-policy competence gate.

This does not train or change the policy. Uses genuine ManiSkill PickCube
physics and exact public MIT checkpoint SHA; logs every episode.
"""
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
from huggingface_hub import hf_hub_download

import mani_skill.envs  # noqa: F401 - register environments

REPO="kattri15/actionshift-baselines"
FILENAME="ppo/pick_cube_final_ckpt.pt"
EXPECTED="3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8"
EPISODE_SEEDS=[42,270,429,2026]
STEPS=50


def _actor(state, observation_width, action_width):
    net=torch.nn.Sequential(
        torch.nn.Linear(observation_width,256),torch.nn.Tanh(),
        torch.nn.Linear(256,256),torch.nn.Tanh(),
        torch.nn.Linear(256,256),torch.nn.Tanh(),
        torch.nn.Linear(256,action_width),
    )
    actor={key[len("actor_mean."):]:val for key,val in state.items()
           if key.startswith("actor_mean.")}
    assert actor, "Checkpoint does not have frozen PPO actor weights"
    net.load_state_dict(actor,strict=True)
    return net.eval()


def _bool_value(value):
    if torch.is_tensor(value):
        return bool(value.detach().cpu().reshape(-1)[0].item())
    return bool(np.asarray(value).reshape(-1)[0])


def main():
    ckpt=Path(hf_hub_download(repo_id=REPO,filename=FILENAME))
    actual=hashlib.sha256(ckpt.read_bytes()).hexdigest()
    if actual != EXPECTED:
        raise RuntimeError("Frozen checkpoint SHA mismatch: "+actual)
    env=gym.make("PickCube-v1",num_envs=1,obs_mode="state",
                 control_mode="pd_ee_delta_pose",
                 sim_backend="physx_cpu",reconfiguration_freq=1,
                 disable_env_checker=True)
    records=[]
    try:
        initial,_=env.reset(seed=EPISODE_SEEDS[0])
        if not torch.is_tensor(initial):
            raise TypeError(f"Expected tensor observations, got {type(initial)}")
        low=torch.as_tensor(env.action_space.low,dtype=torch.float32).reshape(-1)
        high=torch.as_tensor(env.action_space.high,dtype=torch.float32).reshape(-1)
        state=torch.load(ckpt,map_location="cpu",weights_only=True)
        actor=_actor(state,initial.shape[-1],low.numel())
        print("POLICY_ABI",{"obs_dim":initial.shape[-1],"action_dim":low.numel(),"hash":actual})
        for seed in EPISODE_SEEDS:
            obs,_=env.reset(seed=seed)
            success_any=False
            steps=0
            for t in range(STEPS):
                with torch.no_grad():
                    x=obs.detach().cpu().to(torch.float32)
                    action=torch.minimum(torch.maximum(actor(x),low),high)
                obs,reward,terminated,truncated,info=env.step(action)
                success=info.get("success") if isinstance(info,dict) else None
                if success is None:
                    raise RuntimeError("Task did not supply success signal")
                success_any |= _bool_value(success)
                steps=t+1
                if _bool_value(terminated) or _bool_value(truncated):
                    break
            outcome={"seed":seed,"steps":steps,"success_once":success_any}
            records.append(outcome)
            print("FROZEN_PPO_EPISODE",json.dumps(outcome))
    finally:
        env.close()
    report={"checkpoint_repo":REPO,"checkpoint":FILENAME,
            "checkpoint_sha256":actual,"backend":"physx_cpu",
            "control_mode":"pd_ee_delta_pose",
            "source_policy":"official-ManiSkill-PPO-architecture ActionShift weights",
            "training_performed":False,
            "episodes":records,
            "success_count":sum(x["success_once"] for x in records),
            "denominator":len(records)}
    Path("frozen_ppo_gate.json").write_text(json.dumps(report,indent=2))
    print("FROZEN_PPO_GATE",json.dumps(report))
    if len(records)!=len(EPISODE_SEEDS):
        raise RuntimeError("Incomplete source-policy competence gate")


if __name__=="__main__":
    main()
