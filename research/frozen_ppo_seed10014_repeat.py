"""Twelve complete same-seed controller-swap rollouts without selective retry.

Audits a discrepancy between one failed 32-seed holdout case and one
successful separately instrumented reproduction. Not a new holdout.
"""
import hashlib
import json
from pathlib import Path
import torch
from huggingface_hub import hf_hub_download

from frozen_ppo_pickcube_gate import REPO,FILENAME,EXPECTED,_actor
from frozen_ppo_ee_swap import make_env,rollout_one

REPETITIONS=12
SEED=10014


def main():
    ckpt=Path(hf_hub_download(repo_id=REPO,filename=FILENAME))
    digest=hashlib.sha256(ckpt.read_bytes()).hexdigest()
    assert digest==EXPECTED
    env=make_env("pd_ee_delta_pose")
    try:
        obs,_=env.reset(seed=SEED)
        actor=_actor(torch.load(ckpt,map_location="cpu",weights_only=True),obs.shape[-1],7)
    finally:
        env.close()

    records=[]
    for repetition in range(REPETITIONS):
        trial=rollout_one(actor,SEED)
        assert trial["seed"]==SEED
        trial["replicate"]=repetition
        records.append(trial)
        print("REPEAT10014",json.dumps({
            "replicate":repetition,"success":trial["success_once"],
            "steps":trial["episode_steps"],
            "initial_obs_maxdiff":trial["initial_obs_maxdiff"],
        },sort_keys=True))
    summary={key:sum(bool(x["success_once"].get(key,False)) for x in records)
             for key in ("source","compiled","naive")}
    payload={
        "purpose":"same-seed run repeatability; not independent holdout",
        "checkpoint_sha256":digest,
        "seed":SEED,"replications":REPETITIONS,
        "success_count":summary,
        "records":records,
    }
    Path("seed10014_repeatability.json").write_text(json.dumps(payload,indent=2))
    print("REPEAT10014_SUMMARY",json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    main()
