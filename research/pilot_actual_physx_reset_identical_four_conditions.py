"""One-seed authentic PhysX reset-identity PILOT; NO task-level outcomes.

The original four-truth experiment incorrectly treated a shared reset integer
as a proof of identical full initial physical state. This measures actual
original actor/PPO observation equality and max component disagreement before
ANY ACK fault. It is method development, NOT prospective task evaluation.
"""
from __future__ import annotations
import argparse, hashlib, json, random
import numpy as np
import torch
import frozen_ppo_action_history_observer as base
import mani_skill.envs   # real native CPU PhysX

NAMES=("source_no_fault","fault_oracle_private_target",
"fault_optimistic_unverified_ack","fault_strict_common_exact",
"fault_robust_two_history_without_query",
"fault_robust_then_single_privileged_query",
"fault_always_single_privileged_query",
"fault_assume_held_without_query",
"fault_public_t3_fourhistory_or_t4_query")

def one(seed,global_seed:bool):
    if global_seed:
        # This is a pilot for a DIFFERENT prospective protocol; previous
        # method/physics results must never be retconned.
        random.seed(seed)
        np.random.seed(seed%(2**32))
        torch.manual_seed(seed)
    worlds={n:base.env("pd_ee_delta_pose" if n=="source_no_fault" else
                       "pd_ee_target_delta_pose") for n in NAMES}
    try:
        ob={n:w.reset(seed=seed)[0] for n,w in worlds.items()}
        initial=torch.as_tensor(ob["source_no_fault"]).detach().cpu().contiguous().numpy()
        if initial.shape[0]!=1 or initial.ndim!=2:
            raise ValueError("Physical native reset did not produce one source policy state")
        parts={
            "source_initial_obs_sha256":hashlib.sha256(initial.tobytes()).hexdigest(),
            "source_original_obs_dim":initial.shape[1],
            "initial_source_obs":initial.reshape(-1).astype(float).tolist(),
            "target_world_native_qpos_mismatch_max":max(
                float(torch.max(torch.abs(
                    w.unwrapped.agent.robot.get_qpos()-worlds["source_no_fault"].unwrapped.agent.robot.get_qpos()
                ))) for n,w in worlds.items() if n!="source_no_fault"
            )
        }
        return parts
    finally:
        for w in worlds.values(): w.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--seeds",default="1320001,1310001")
    args=p.parse_args()
    result=[]
    for seed in [int(x) for x in args.seeds.split(",")]:
        task="stack_cube" if seed//10000==132 else "pull_cube"
        if task not in base.TASKS: raise ValueError("Unexpected real task")
        # A single work process runs four simulated truth resets in sequence.
        # Each has the original nine controller environments.
        for reseed in (False,True):
            runs=[one(seed,reseed) for _ in range(4)]
            arrays=[np.asarray(x.pop("initial_source_obs"),dtype=float) for x in runs]
            h=[x["source_initial_obs_sha256"] for x in runs]
            result.append({
                "task":task,"seed":seed,
                "global_rng_reseed_before_world_creation":reseed,
                "four_original_paired_source_obs_hashes":h,
                "four_reset_observations_bitwise_identical":len(set(h))==1,
                "max_pairwise_source_PPO_input_difference":max(float(np.max(np.abs(a-b))) for a in arrays for b in arrays),
                "per_condition_source_dim":[x["source_original_obs_dim"] for x in runs],
                "within_condition_initial_robot_qpos_mismatch_max":[x["target_world_native_qpos_mismatch_max"] for x in runs],
                "requires_other_unobserved_native_state_validation":True,
                "zero_ACK_faults_injected":True,
                "zero_policy_task_outcomes_measured":True
            })
    from pathlib import Path
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({"evidence":"ORIGINAL_PHYSX_RESET_PILOT_NOT_TASK_ANSWER","data":result},indent=2,sort_keys=True)+"\n")
    print("AUTHENTIC_PHYSX_RESET_BYTE_EQUALITY_PILOT",json.dumps([{k:v for k,v in x.items() if k not in ("four_original_paired_source_obs_hashes",)} for x in result],sort_keys=True))

if __name__=="__main__":main()
