"""Prospectively frozen two-world public-motion separation in genuine ManiSkill PhysX.

A and B receive identical commands until the third action. Thereafter the A
arm executes the converted PPO command, while B receives a native zero arm
delta with the same gripper command. No target-memory field enters reported
observability metrics; private targets are endpoint audit only.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
import torch
from huggingface_hub import hf_hub_download

sys.path.insert(0,str(Path(__file__).resolve().parent))
import frozen_ppo_action_history_observer as original
from frozen_ppo_observer_policy import _actor, REPO

TASK=os.environ.get("ABI_TASK")
SPECS={
    "pull_cube": ("PullCube-v1","ppo/pull_cube_final_ckpt.pt",
        "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",98001),
    "stack_cube": ("StackCube-v1","ppo/stack_cube_final_ckpt.pt",
        "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",99001)
}
if TASK not in SPECS:
    raise ValueError("Only two preregistered tasks")
TASK_NAME,WEIGHTS,HASH,FIRST=SPECS[TASK]
SEEDS=list(range(FIRST,FIRST+8))
PROTOCOL="research/PUBLIC_MOTION_FAULT_IDENTIFIABILITY_PRECOMMIT_V1.json"


def unpack_metrics(env):
    agent=env.unwrapped.agent
    qpos=np.asarray(agent.robot.get_qpos().detach().cpu(),dtype=float).reshape(-1)
    qvel=np.asarray(agent.robot.get_qvel().detach().cpu(),dtype=float).reshape(-1)
    if not (np.isfinite(qpos).all() and np.isfinite(qvel).all()):
        raise RuntimeError("Nonfinite physical public observation")
    return qpos,qvel


def observe_pair(a,b,step):
    qa,va=unpack_metrics(a)
    qb,vb=unpack_metrics(b)
    if qa.shape!=qb.shape or va.shape!=vb.shape:
        raise RuntimeError("Public qpos/qvel shapes differ")
    return {
        "diagnostic_step_since_fault":step,
        "max_abs_qpos_gap_rad":float(np.max(np.abs(qa-qb))),
        "max_abs_qvel_gap_rad_s":float(np.max(np.abs(va-vb))),
        "qpos_gap_l2_rad":float(np.linalg.norm(qa-qb)),
        "qvel_gap_l2_rad_s":float(np.linalg.norm(va-vb)),
    }


def target_audit(a,b):
    def target(env):
        arm=env.unwrapped.agent.controller.controllers["arm"]
        return np.asarray(arm.get_state()["target_pose"].detach().cpu(),dtype=float).reshape(-1,7)[0]
    x,y=target(a),target(b)
    # Only audit: values MUST NOT be used in public-motion classifier.
    return {"max_target_position_gap_m":float(np.max(np.abs(x[:3]-y[:3]))),
            "q_wxyz_a":list(map(float,x[3:])),
            "q_wxyz_b":list(map(float,y[3:]))}


def episode(actor,seed):
    envs={
        "source":original.env("pd_ee_delta_pose"),
        "applied":original.env("pd_ee_target_delta_pose"),
        "held":original.env("pd_ee_target_delta_pose"),
    }
    try:
        obs={k:e.reset(seed=seed)[0] for k,e in envs.items()}
        srcobs=original._project_policy_observation(obs["source"],envs["source"])
        for arm in ("applied","held"):
            same=original._project_policy_observation(obs[arm],envs[arm],verify_memory=False)
            if float(torch.max(torch.abs(srcobs-same)))>5e-4:
                raise RuntimeError("Initial physical task state is not paired")
        source_ctrl=envs["source"].unwrapped.agent.controller
        source_arm=source_ctrl.controllers["arm"]
        native_fault=None
        last_gripper=None
        initial=observe_pair(envs["applied"],envs["held"],-1)
        if max(initial["max_abs_qpos_gap_rad"],initial["max_abs_qvel_gap_rad_s"])>1e-6:
            raise RuntimeError("Initial robot states differ")
        for t in range(3):
            native=original.act(actor,original._project_policy_observation(
                obs["applied"],envs["applied"],verify_memory=False))
            parts=source_ctrl.to_action_dict(native[0])
            rewritten={}
            for arm in ("applied","held"):
                ctrl=envs[arm].unwrapped.agent.controller
                x,reason,amp=original.normalized_target_delta(
                    source_arm,ctrl.controllers["arm"],native,
                    approximate=True)
                if x is None:
                    raise RuntimeError("Unrepresentable source converted command")
                rewritten[arm]=x[0]
            if torch.max(torch.abs(rewritten["applied"]-rewritten["held"]))>1e-5:
                raise RuntimeError("Pre-fault target command already differed")
            last_gripper=parts["gripper"]
            if t==2:
                native_fault=rewritten["applied"].detach().cpu().numpy()
            for arm in ("applied","held"):
                ctrl=envs[arm].unwrapped.agent.controller
                command=(torch.zeros_like(rewritten[arm]) if t==2 and arm=="held"
                         else rewritten[arm])
                full=ctrl.from_action_dict({
                    "arm":command,"gripper":last_gripper}).reshape(1,-1)
                obs[arm],_,_,_,_=envs[arm].step(full)
        metrics=[observe_pair(envs["applied"],envs["held"],0)]
        for k in range(1,5):
            for arm in ("applied","held"):
                ctrl=envs[arm].unwrapped.agent.controller
                full=ctrl.from_action_dict({
                    "arm":torch.zeros_like(rewritten[arm]),"gripper":last_gripper
                }).reshape(1,-1)
                obs[arm],_,_,_,_=envs[arm].step(full)
            metrics.append(observe_pair(envs["applied"],envs["held"],k))
        # Intentionally after ALL measurements have been collected.
        audit=target_audit(envs["applied"],envs["held"])
        action_mag=float(np.linalg.norm(native_fault))
        return {"seed":seed,"public_initial_state":initial,
                "fault_step":2,"native_converted_arm_magnitude":action_mag,
                "different_actual_native_arm_action":bool(action_mag>1e-8),
                "public_observation_7d_target_slice_excluded":True,
                "comparisons":metrics,"post_trial_private_target_audit_only":audit}
    finally:
        for e in envs.values():e.close()


def main():
    global TASK
    weights=Path(hf_hub_download(repo_id=REPO,filename=WEIGHTS,
                                 revision=original.PUBLISHED_MODEL_REVISION))
    sha=hashlib.sha256(weights.read_bytes()).hexdigest()
    if sha!=HASH:
        raise RuntimeError("Released frozen checkpoint SHA mismatch")
    source=original.env("pd_ee_delta_pose")
    try:
        obs,_=source.reset(seed=SEEDS[0])
        original.POLICY_OBS_DIM=int(obs.shape[-1])
        actor=_actor(torch.load(weights,map_location="cpu",weights_only=True),
                     original.POLICY_OBS_DIM,7)
    finally:source.close()
    rows=[episode(actor,seed) for seed in SEEDS]
    thresholds=(1e-6,1e-4,1e-3)
    hist={}
    for t in range(5):
        hist[str(t)]={
            "max_qpos_gap_rad":max(x["comparisons"][t]["max_abs_qpos_gap_rad"] for x in rows),
            "min_qpos_gap_rad":min(x["comparisons"][t]["max_abs_qpos_gap_rad"] for x in rows),
            "median_qpos_gap_rad":float(np.median([x["comparisons"][t]["max_abs_qpos_gap_rad"] for x in rows])),
            "threshold_exceedance":{str(v):sum(
                x["comparisons"][t]["max_abs_qpos_gap_rad"]>v for x in rows)
                for v in thresholds},
        }
    data={"experiment":"public-motion-fault-identifiability-v1","protocol":PROTOCOL,
          "task":TASK_NAME,"seeds":SEEDS,"model_sha256":sha,
          "model_revision":original.PUBLISHED_MODEL_REVISION,
          "frozen_policy":True,"training_performed":False,
          "real_physx_cpu":True,"n":len(rows),"rows":rows,
          "summary_by_diagnostic_step":hist,
          "claims_excluded":["no noisy-sensor identifiability claim",
                             "no automatic latent-state recovery demonstrated",
                             "no hardware, no independent outside execution"]}
    target=Path(f"public_motion_fault_{TASK}_8.json")
    target.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("PUBLIC_MOTION_FAULT_OBSERVABILITY",json.dumps({
        "task":TASK_NAME,"n":len(rows),
        "all_command_divergences_nonzero":all(x["different_actual_native_arm_action"] for x in rows),
        "gap_qpos_at_fault":hist["0"],
        "gap_qpos_after_four_diagnostic_steps":hist["4"]},sort_keys=True))


if __name__=="__main__":
    main()
