"""Audit reproducibility of an ostensibly seeded frozen PPO PickCube episode.

Distinguish Python seed from *actual* initial state by SHA256 fingerprints
of full physics state and actor input observations. Run the same seed before
and after other trials. Do not suppress counterexamples.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
from huggingface_hub import hf_hub_download
from frozen_ppo_pickcube_gate import EXPECTED,FILENAME,REPO,_actor
from frozen_ppo_ee_swap import make_env,rollout_one

SEQUENCE=(10014,10014,10001,10014,10002,10014)
TARGET=10014


def tensor_signature(t):
    a=np.ascontiguousarray(torch.as_tensor(t).detach().cpu().numpy())
    return {"shape":list(a.shape),"dtype":str(a.dtype),
            "sha256":hashlib.sha256(a.tobytes()).hexdigest(),
            "head":[float(v) for v in a.reshape(-1)[:12]]}


def fingerprint(seed):
    engines={key:make_env(mode) for key,mode in
             (("source","pd_ee_delta_pose"),("compiled","pd_ee_pose"))}
    try:
        out={}
        for key,w in engines.items():
            obs,_=w.reset(seed=seed)
            sim=w.unwrapped.get_state()
            out[key]={"observation":tensor_signature(obs),
                      "sim_state":tensor_signature(sim),
                      "episode_seed":np.asarray(w.unwrapped._episode_seed).tolist()}
        return out
    finally:
        for w in engines.values():w.close()


def main():
    ckpt=Path(hf_hub_download(repo_id=REPO,filename=FILENAME))
    assert hashlib.sha256(ckpt.read_bytes()).hexdigest()==EXPECTED
    probe=make_env("pd_ee_delta_pose")
    try:
        obs,_=probe.reset(seed=TARGET)
        actor=_actor(torch.load(ckpt,map_location="cpu",weights_only=True),
                     int(obs.shape[-1]),7)
    finally:probe.close()
    records=[]
    for index,seed in enumerate(SEQUENCE):
        sig=fingerprint(seed)
        # Use exact same unmodified rollout on source and compiled
        # (diagnostic branch already logs all 50-step dynamics).
        res=rollout_one(actor,seed)
        row={"index":index,"requested_seed":seed,
             "initial_fingerprints":sig,
             "source_success":res["success_once"].get("source",False),
             "compiled_success":res["success_once"].get("compiled",False),
             "source_steps":res["episode_steps"].get("source"),
             "compiled_steps":res["episode_steps"].get("compiled")}
        records.append(row)
        print("CST_REPLAY_ORDER_AUDIT",json.dumps(row,sort_keys=True))
    target=[r for r in records if r["requested_seed"]==TARGET]
    distinct_obs=len(set(x["initial_fingerprints"]["source"]["observation"]["sha256"] for x in target))
    distinct_sim=len(set(x["initial_fingerprints"]["source"]["sim_state"]["sha256"] for x in target))
    payload={"sequence":SEQUENCE,"target":TARGET,"target_observation_unique_fingerprints":distinct_obs,
             "target_sim_state_unique_fingerprints":distinct_sim,
             "target_source_outcomes":[r["source_success"] for r in target],
             "target_compiled_outcomes":[r["compiled_success"] for r in target],
             "records":records}
    Path("seed_reproducibility_audit.json").write_text(json.dumps(payload,indent=2))
    print("CST_REPLAY_ORDER_SUMMARY",json.dumps({k:payload[k] for k in
          ("target_observation_unique_fingerprints","target_sim_state_unique_fingerprints",
           "target_source_outcomes","target_compiled_outcomes")}))
    # Crucial: a nonreproducible run reports the finding without ignoring it.


if __name__=="__main__":main()
