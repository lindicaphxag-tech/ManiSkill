#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import shutil
from pathlib import Path

import h5py
import numpy as np
from transforms3d.quaternions import quat2axangle

import mani_skill
from mani_skill.trajectory import replay_trajectory
from mani_skill.trajectory.utils.actions import conversion as action_conversion
from mani_skill.utils import gym_utils, io_utils


PREFIXES=(0,1,2,4,8,16,32,64,128,256)
CONTEXTS=("candidate_prior","main_prior")


def baseline_main_action(controller, delta_pose, pos_only=False):
    low,high=controller.action_space_low,controller.action_space_high
    if pos_only:
        return gym_utils.inv_scale_action(
            delta_pose.p,low.cpu().numpy(),high.cpu().numpy()
        )
    axis,angle=quat2axangle(delta_pose.q)
    if angle>np.pi:
        angle=angle-2*np.pi
    compact=np.asarray(axis,dtype=np.float64)*float(angle)
    packed=np.r_[delta_pose.p,compact]
    return gym_utils.inv_scale_action(
        packed,low.cpu().numpy(),high.cpu().numpy()
    )


def parse_success_ids(text:str)->list[int]:
    failures={int(x) for x in re.findall(
        r"Episode\s+(\d+)\s+is not replayed successfully",text
    )}
    return [i for i in (0,1) if i not in failures]


def run_one(raw_h5:Path,root:Path,prior_mode:str,prefix:int,target_episode:int)->dict:
    run_dir=root/f"{prior_mode}__k_{prefix:03d}"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    traj=run_dir/"trajectory.h5"
    shutil.copy2(raw_h5,traj)
    shutil.copy2(raw_h5.with_suffix(".json"),traj.with_suffix(".json"))

    metadata=io_utils.load_json(str(traj.with_suffix(".json")))
    episode_ids=[int(ep["episode_id"]) for ep in metadata["episodes"][:2]]
    if episode_ids!=[0,1]:
        raise RuntimeError(f"expected first two episode IDs [0,1], got {episode_ids}")

    original_delta=action_conversion.delta_pose_to_pd_ee_delta
    original_from=action_conversion.from_pd_joint_pos
    cursor={"episode":None,"call":0}

    def wrapped_from(*args,**kwargs):
        idx=wrapped_from.index
        if idx>=len(episode_ids):
            raise RuntimeError("episode accounting overflow")
        cursor["episode"]=episode_ids[idx]
        cursor["call"]=0
        wrapped_from.index+=1
        return original_from(*args,**kwargs)
    wrapped_from.index=0

    def wrapped_delta(controller,delta_pose,pos_only=False):
        candidate=original_delta(controller,delta_pose,pos_only=pos_only)
        use_main=False
        if cursor["episode"]<target_episode:
            use_main=prior_mode=="main_prior"
        elif cursor["episode"]==target_episode and cursor["call"]<prefix:
            use_main=True
        result=baseline_main_action(controller,delta_pose,pos_only=pos_only) if use_main else candidate
        if cursor["episode"]==target_episode and not pos_only:
            cursor["call"]+=1
        return result

    action_conversion.from_pd_joint_pos=wrapped_from
    action_conversion.delta_pose_to_pd_ee_delta=wrapped_delta
    try:
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf):
            replay_trajectory.main(
                replay_trajectory.Args(
                    traj_path=str(traj),
                    sim_backend="physx_cpu",
                    obs_mode="state",
                    target_control_mode="pd_ee_delta_pose",
                    save_traj=False,
                    save_video=False,
                    use_first_env_state=True,
                    count=2,
                    num_envs=1,
                )
            )
        text=buf.getvalue()
    finally:
        action_conversion.from_pd_joint_pos=original_from
        action_conversion.delta_pose_to_pd_ee_delta=original_delta

    success_ids=parse_success_ids(text)
    return {
        "prior_mode":prior_mode,
        "prefix_main_calls":prefix,
        "episode0_success":0 in success_ids,
        "episode1_success":1 in success_ids,
        "target_converter_calls_observed":cursor["call"],
        "stdout_tail":text[-1200:],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-traj",type=Path,required=True)
    p.add_argument("--candidate-source-root",type=Path,required=True)
    p.add_argument("--candidate-sha",required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--episode-id",type=int,default=1)
    a=p.parse_args()

    actual=Path(mani_skill.__file__).resolve()
    expected=a.candidate_source_root.resolve()
    if expected not in actual.parents:
        raise SystemExit(f"wrong source imported: {actual}; expected {expected}")
    if a.episode_id!=1:
        raise SystemExit("this frozen protocol is preregistered for episode 1")

    results=[]
    root=a.output.parent/"prefix_runs"
    root.mkdir(parents=True,exist_ok=True)
    for prior in CONTEXTS:
        for prefix in PREFIXES:
            row=run_one(a.raw_traj,root,prior,prefix,a.episode_id)
            results.append(row)
            print(json.dumps({k:v for k,v in row.items() if k!="stdout_tail"},sort_keys=True))

    by={(r["prior_mode"],r["prefix_main_calls"]):r for r in results}
    endpoint_checks={
        "candidate_prior_k0_episode1_failure":not by[("candidate_prior",0)]["episode1_success"],
        "main_prior_k256_episode1_success":by[("main_prior",256)]["episode1_success"],
    }

    summaries={}
    for prior in CONTEXTS:
        rows=[r for r in results if r["prior_mode"]==prior]
        success_prefixes=[r["prefix_main_calls"] for r in rows if r["episode1_success"]]
        transitions=[]
        for left,right in zip(rows,rows[1:]):
            if left["episode1_success"]!=right["episode1_success"]:
                transitions.append({
                    "left_prefix":left["prefix_main_calls"],
                    "left_success":left["episode1_success"],
                    "right_prefix":right["prefix_main_calls"],
                    "right_success":right["episode1_success"],
                })
        summaries[prior]={
            "success_prefixes":success_prefixes,
            "minimum_success_prefix":min(success_prefixes) if success_prefixes else None,
            "transitions":transitions,
            "monotone_non_decreasing":all(
                (not rows[i]["episode1_success"]) or rows[i+1]["episode1_success"]
                for i in range(len(rows)-1)
            ),
        }

    report={
        "schema_version":1,
        "candidate_sha":a.candidate_sha,
        "candidate_import":str(actual),
        "episode_id":a.episode_id,
        "prefix_grid":list(PREFIXES),
        "contexts":list(CONTEXTS),
        "endpoint_checks":endpoint_checks,
        "valid_for_causal_interpretation":all(endpoint_checks.values()),
        "summaries":summaries,
        "results":results,
        "claim_boundary":(
            "Serial-context counterfactual prefix replacement along one repeatability-qualified "
            "discordant episode. It localizes whether early historical-main converter outputs "
            "are sufficient to recover the outcome; it is not a general robustness radius."
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="results"},indent=2,sort_keys=True))

    if not all(endpoint_checks.values()):
        raise SystemExit("prefix-intervention endpoint checks failed; do not interpret path")


if __name__=="__main__":
    main()
