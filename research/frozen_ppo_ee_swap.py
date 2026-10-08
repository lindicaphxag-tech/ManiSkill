"""Frozen published PPO, three-way real ManiSkill controller swap.

Source frozen policy: pd_ee_delta_pose. Target: pd_ee_pose. All three
simulators receive the same policy checkpoint but choose actions from
their OWN current observations (closed-loop). No training or updates.

This is an exploratory CI, not a pre-declared clinical safety guarantee.
"""
import json
import hashlib
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from huggingface_hub import hf_hub_download

import mani_skill.envs  # noqa: F401

from frozen_ppo_pickcube_gate import (
    EXPECTED, FILENAME, REPO, _actor, _bool_value
)
import hashlib

SEEDS=(10014,10014,10014,10014)
MAX_STEPS=50


def make_env(control_mode):
    return gym.make(
        "PickCube-v1",num_envs=1,obs_mode="state",
        sim_backend="physx_cpu",reconfiguration_freq=1,
        control_mode=control_mode,disable_env_checker=True
    )


def current_arm(controller):
    return controller.controllers["arm"]


def get_policy_action(actor, obs):
    # Both policy calls consume own observations and identical *frozen*
    # network weights. The PPO native action chart is 7D normalized deltas.
    with torch.no_grad():
        native=actor(obs.detach().cpu().to(torch.float32)).clip(-1,1)
    if native.ndim!=2 or native.shape[0]!=1 or native.shape[1]!=7:
        raise RuntimeError("Unexpected frozen PPO action ABI "+str(native.shape))
    return native


def compile_pd_ee_delta_to_absolute_pose(source_arm, destination_arm, native):
    # PhysX CPU source delta controller uses root_translation and
    # root-aligned body orientation. Use official controller math to
    # decode the *source* native action chart; output root-frame
    # absolute translation + XYZ Euler radians for pd_ee_pose.
    canonical_arm=native[:,:6]
    delta=source_arm._preprocess_action(canonical_arm)
    achieved=destination_arm.ee_pose_at_base
    # This computes a TARGET pose without mutating source controller state.
    target_pose=source_arm.compute_target_pose(achieved,delta)
    pos=target_pose.p.detach().cpu().numpy().reshape(-1,3)[0]
    q=target_pose.q.detach().cpu().numpy().reshape(-1,4)[0]
    euler=Rotation.from_quat([q[1],q[2],q[3],q[0]]).as_euler("XYZ")
    arm=torch.as_tensor(np.r_[pos,euler],dtype=native.dtype).reshape(1,6)
    return arm


def rollout_one(actor,seed):
    envs={
        "source":make_env("pd_ee_delta_pose"),
        "compiled":make_env("pd_ee_pose"),
        "naive":make_env("pd_ee_pose"),
    }
    report={"seed":seed,"max_steps":MAX_STEPS,"success_once":{},
            "initial_obs_maxdiff":{},"episode_steps":{}}
    try:
        observations={}
        for key,env in envs.items():
            observations[key],_=env.reset(seed=seed)
        shape={k:tuple(v.shape) for k,v in observations.items()}
        if len(set(shape.values()))!=1:
            raise RuntimeError("Mismatch observation ABI: "+str(shape))
        for target in ("compiled","naive"):
            diff=float(torch.max(torch.abs(observations["source"]-observations[target])).item())
            report["initial_obs_maxdiff"][target]=diff
            if diff>5e-4:
                raise RuntimeError("Different initial physics/goal observation; result invalid "+str(diff))

        import hashlib as _hashlib
        initial_numpy=observations["source"].detach().cpu().numpy().astype(np.float32)
        report["initial_obs_sha256"]=_hashlib.sha256(initial_numpy.tobytes()).hexdigest()
        report["initial_obs_head10"]=initial_numpy.reshape(-1)[:10].astype(float).tolist()
        controllers={name:env.unwrapped.agent.controller for name,env in envs.items()}
        source_arm=current_arm(controllers["source"])
        detailed_trace=[]
        completed={k:False for k in envs}
        for t in range(MAX_STEPS):
            before_obs={name:observations[name].detach().cpu().numpy().reshape(-1).copy()
                        for name in ("source","compiled")}
            inputs={}
            issued={}
            for name in envs:
                if completed[name]:
                    continue
                native=get_policy_action(actor,observations[name])
                inputs[name]=native.detach().cpu().numpy().reshape(-1).tolist()
                if name=="compiled":
                    new_arm=compile_pd_ee_delta_to_absolute_pose(
                        source_arm,current_arm(controllers[name]),native)
                    canonical_dict=controllers["source"].to_action_dict(native.squeeze(0))
                    canon_gripper=canonical_dict["gripper"]
                    target_action=controllers[name].from_action_dict(
                        {"arm":new_arm.reshape(-1).to(canon_gripper.device),
                         "gripper":canon_gripper.reshape(-1)}
                    ).reshape(1,-1)
                elif name=="naive":
                    # Wrong action ABI: raw normalized delta interpreted as
                    # absolute EE pose by destination controller.
                    target_action=native
                else:
                    target_action=native

                issued[name]=target_action.detach().cpu().numpy().reshape(-1).tolist()
                observations[name],_,terminated,truncated,info=envs[name].step(target_action)
                success=info.get("success") if isinstance(info,dict) else None
                if success is None:
                    raise RuntimeError("Missing official ManiSkill success flag")
                report["success_once"][name]=report["success_once"].get(name,False) or _bool_value(success)
                report["episode_steps"][name]=t+1
                completed[name] = _bool_value(terminated) or _bool_value(truncated)
            qref=envs["source"].unwrapped.agent.robot.get_qpos().detach().cpu().numpy().reshape(-1)
            qdst=envs["compiled"].unwrapped.agent.robot.get_qpos().detach().cpu().numpy().reshape(-1)
            ee_src=envs["source"].unwrapped.agent.tcp.pose.p.detach().cpu().numpy().reshape(-1)
            ee_dst=envs["compiled"].unwrapped.agent.tcp.pose.p.detach().cpu().numpy().reshape(-1)
            obs_diff=float(np.max(np.abs(before_obs["source"]-before_obs["compiled"])))
            trace_entry={"step":t+1,
                        "source_completed":completed["source"],
                        "compiled_completed":completed["compiled"],
                        "source_success_once":report["success_once"].get("source",False),
                        "compiled_success_once":report["success_once"].get("compiled",False),
                        "prestep_obs_max_abs_diff":obs_diff,
                        "policy_input_action_source":inputs.get("source"),
                        "policy_input_action_compiled":inputs.get("compiled"),
                        "issued_action_source":issued.get("source"),
                        "issued_action_compiled":issued.get("compiled"),
                        "robot_joint_qpos_max_abs_diff":float(np.max(np.abs(qref-qdst))),
                        "tcp_position_l2_diff":float(np.linalg.norm(ee_src-ee_dst))}
            detailed_trace.append(trace_entry)
            print("FROZEN_10014_DIAGNOSTIC_STEP",json.dumps(trace_entry,sort_keys=True))
            if all(completed.values()):
                break
        report["detailed_trace"]=detailed_trace
        print("FROZEN_PPO_SWAP_EPISODE",json.dumps({k:v for k,v in report.items() if k!="detailed_trace"},sort_keys=True))
        return report
    finally:
        for env in envs.values():
            env.close()


def main():
    file=Path(hf_hub_download(repo_id=REPO,filename=FILENAME))
    digest=hashlib.sha256(file.read_bytes()).hexdigest()
    if digest != EXPECTED:
        raise RuntimeError("Frozen checkpoint hash mismatch "+digest)

    # Match the checkpoint architecture and policy input/output chart
    # to the actual original training mode before starting comparisons.
    env=make_env("pd_ee_delta_pose")
    try:
        obs,_=env.reset(seed=SEEDS[0])
        sd=torch.load(file,map_location="cpu",weights_only=True)
        net=_actor(sd,int(obs.shape[-1]),7)
    finally:
        env.close()

    runs=[rollout_one(net,s) for s in SEEDS]
    outcomes={name:sum(r["success_once"].get(name,False) for r in runs)
              for name in ("source","compiled","naive")}
    result={"checkpoint_repo":REPO,"checkpoint":FILENAME,
            "checkpoint_sha256":digest,"policy_frozen":True,
            "controller_modes":{"source":"pd_ee_delta_pose",
                                 "compiled":"pd_ee_pose",
                                 "naive":"pd_ee_pose"},
            "backend":"physx_cpu","episodes":runs,"success_count":outcomes,
            "denominator":len(SEEDS),
            "interpretation":"exploratory; must require competent source before claiming a migration benefit"}
    Path("frozen_ppo_controller_swap.json").write_text(json.dumps(result,indent=2))
    Path("seed10014_diagnostic.json").write_text(json.dumps(runs,indent=2))
    print("FROZEN_PPO_SWAP_SUMMARY",json.dumps({
        "source":outcomes["source"],"compiled":outcomes["compiled"],
        "naive":outcomes["naive"],"episodes":len(SEEDS)
    }))
    # Any initial-observation mismatch throws rather than silently
    # promoting incomparable scenes; zero source competence is a
    # measured negative result, not an integration green success claim.


if __name__=="__main__":
    main()
