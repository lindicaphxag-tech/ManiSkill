"""Check 3 publicly released ActionShift PPO backbones before any transfer."""
import os,json,hashlib
from pathlib import Path
import gymnasium as gym
import torch
from huggingface_hub import hf_hub_download
import mani_skill.envs # noqa F401
from frozen_ppo_pickcube_gate import _actor,_bool_value,REPO

MODELS={
 "push_cube":("PushCube-v1","ppo/push_cube_final_ckpt.pt",
              "a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf"),
 "pull_cube":("PullCube-v1","ppo/pull_cube_final_ckpt.pt",
              "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
 "stack_cube":("StackCube-v1","ppo/stack_cube_final_ckpt.pt",
               "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"),
}
SEEDS=(42,270,429,2026)
task=os.environ["CST_TASK"]
assert task in MODELS
env_id,filename,expected_sha=MODELS[task]
ckpt=Path(hf_hub_download(repo_id=REPO,filename=filename))
sha=hashlib.sha256(ckpt.read_bytes()).hexdigest()
assert sha==expected_sha, f"Frozen source weights changed: {sha}"
env=gym.make(env_id,num_envs=1,obs_mode="state",control_mode="pd_ee_delta_pose",
             sim_backend="physx_cpu",reconfiguration_freq=1,disable_env_checker=True)
records=[]
try:
 obs,_=env.reset(seed=SEEDS[0])
 low=torch.as_tensor(env.action_space.low,dtype=torch.float32).reshape(-1)
 high=torch.as_tensor(env.action_space.high,dtype=torch.float32).reshape(-1)
 actor=_actor(torch.load(ckpt,map_location="cpu",weights_only=True),
              int(obs.shape[-1]),len(low))
 print("CST_MULTITASK_POLICY_ABI",json.dumps({"task":task,"obs_dim":int(obs.shape[-1]),
       "action_dim":len(low),"sha256":sha}))
 for seed in SEEDS:
  obs,_=env.reset(seed=seed)
  success=False
  steps=0
  for step in range(50):
   with torch.no_grad():
    action=torch.maximum(torch.minimum(actor(obs.detach().cpu().float()),high),low)
   obs,_,terminated,truncated,info=env.step(action)
   success |= _bool_value(info["success"])
   steps=step+1
   if _bool_value(terminated) or _bool_value(truncated):break
  result={"task":task,"seed":seed,"success":success,"steps":steps}
  print("CST_MULTITASK_SOURCE_EPISODE",json.dumps(result),flush=True)
  records.append(result)
finally:env.close()
summary={"task":task,"checkpoint":filename,"checkpoint_sha256":sha,
 "n":len(records),"successes":sum(int(x["success"]) for x in records),
 "training_performed":False,"records":records}
Path(f"frozen_ppo_competence_{task}.json").write_text(json.dumps(summary,indent=2))
print("CST_MULTITASK_SOURCE_GATE",json.dumps(summary))
assert len(records)==len(SEEDS)
