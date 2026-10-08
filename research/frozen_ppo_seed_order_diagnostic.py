"""Order-effect diagnostic without changing the frozen PPO or controller adapter."""
import hashlib
import json
from pathlib import Path
import torch
from huggingface_hub import hf_hub_download

from frozen_ppo_pickcube_gate import EXPECTED,REPO,FILENAME,_actor
from frozen_ppo_ee_swap import make_env,rollout_one


def main():
    ckpt=Path(hf_hub_download(repo_id=REPO,filename=FILENAME))
    assert hashlib.sha256(ckpt.read_bytes()).hexdigest()==EXPECTED
    env=make_env("pd_ee_delta_pose")
    try:
        obs,_=env.reset(seed=10014)
        policy=_actor(torch.load(ckpt,map_location="cpu",weights_only=True),
                      int(obs.shape[-1]),7)
    finally:
        env.close()
    schedules={"isolated":[10014],"prefix":list(range(10001,10015))}
    results={}
    for name,seeds in schedules.items():
        row=None
        for seed in seeds:
            current=rollout_one(policy,seed)
            if seed==10014:
                row=current
        assert row is not None
        results[name]=row
        print("STATE_IDENTITY_SCHEDULE",json.dumps({
            "schedule":name,"source_observation_hash":row["initial_observation_sha256"],
            "source_physics_hash":row["initial_physics_state_sha256"],
            "success":row["success_once"],"steps":row["episode_steps"],
            "first_observation8":row["initial_obs_first8"]},sort_keys=True))
    comparison={
        "observation_same":results["isolated"]["initial_observation_sha256"]==
                            results["prefix"]["initial_observation_sha256"],
        "physics_same":results["isolated"]["initial_physics_state_sha256"]==
                            results["prefix"]["initial_physics_state_sha256"],
        "source_compiled_success_A":{
            k:results[k]["success_once"] for k in results
        },
    }
    output={"schedules":results,"comparison":comparison}
    Path("state_order_effects.json").write_text(json.dumps(output,indent=2))
    print("STATE_ORDER_EFFECT_SUMMARY",json.dumps(comparison,sort_keys=True))


if __name__=="__main__":
    main()
