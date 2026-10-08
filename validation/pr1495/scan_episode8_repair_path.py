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
import torch
from transforms3d.quaternions import quat2axangle

import mani_skill
from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory import replay_trajectory
from mani_skill.trajectory.utils.actions import conversion as action_conversion
from mani_skill.utils import gym_utils, io_utils
from mani_skill.utils.geometry import rotation_conversions


def baseline_main_action(controller, delta_pose, pos_only=False):
    low, high=controller.action_space_low, controller.action_space_high
    if pos_only:
        return gym_utils.inv_scale_action(
            delta_pose.p, low.cpu().numpy(), high.cpu().numpy()
        )
    axis, angle=quat2axangle(delta_pose.q)
    if angle > np.pi:
        angle=angle-2*np.pi
    compact=np.asarray(axis,dtype=np.float64)*float(angle)
    packed=np.r_[delta_pose.p,compact]
    return gym_utils.inv_scale_action(
        packed,low.cpu().numpy(),high.cpu().numpy()
    )


def make_single_episode(raw_h5: Path, episode_id: int, out_h5: Path):
    raw_json=raw_h5.with_suffix(".json")
    meta=io_utils.load_json(str(raw_json))
    chosen=[ep for ep in meta["episodes"] if int(ep["episode_id"])==episode_id]
    if len(chosen)!=1:
        raise RuntimeError(f"expected exactly one metadata episode {episode_id}")
    out_h5.parent.mkdir(parents=True,exist_ok=True)
    with h5py.File(raw_h5,"r") as src, h5py.File(out_h5,"w") as dst:
        for key,value in src.attrs.items():
            dst.attrs[key]=value
        src.copy(f"traj_{episode_id}",dst)
    out_meta=dict(meta)
    out_meta["episodes"]=chosen
    out_h5.with_suffix(".json").write_text(
        json.dumps(out_meta,indent=2)+"\n",encoding="utf-8"
    )


def parse_success(text: str) -> int:
    m=re.search(r"Replayed\s+1\s+episodes,\s+(\d+)/1=",text)
    if not m:
        raise RuntimeError("could not parse replay result")
    return int(m.group(1))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-traj",type=Path,required=True)
    p.add_argument("--candidate-source-root",type=Path,required=True)
    p.add_argument("--candidate-sha",required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--episode-id",type=int,default=8)
    p.add_argument("--step",type=float,default=0.05)
    a=p.parse_args()

    actual=Path(mani_skill.__file__).resolve()
    expected=a.candidate_source_root.resolve()
    if expected not in actual.parents:
        raise SystemExit(f"wrong source imported: {actual}; expected {expected}")

    original=action_conversion.delta_pose_to_pd_ee_delta
    alpha_box={"value":0.0}

    def hybrid(controller,delta_pose,pos_only=False):
        base=baseline_main_action(controller,delta_pose,pos_only=pos_only)
        repair=original(controller,delta_pose,pos_only=pos_only)
        alpha=alpha_box["value"]
        return (1.0-alpha)*np.asarray(base)+alpha*np.asarray(repair)

    action_conversion.delta_pose_to_pd_ee_delta=hybrid
    try:
        alphas=np.arange(0.0,1.0+a.step/2.0,a.step)
        alphas=np.clip(alphas,0.0,1.0)
        alphas=np.unique(np.round(alphas,10))
        results=[]
        root=a.output.parent/"episode8_repair_path_runs"
        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True)

        for alpha in alphas:
            alpha=float(alpha)
            run_dir=root/f"alpha_{alpha:.4f}"
            traj=run_dir/"trajectory.h5"
            make_single_episode(a.raw_traj,a.episode_id,traj)
            alpha_box["value"]=alpha
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
                        count=1,
                        num_envs=1,
                    )
                )
            success=parse_success(buf.getvalue())
            results.append({"alpha":alpha,"success":bool(success)})

        transitions=[]
        for left,right in zip(results,results[1:]):
            if left["success"] != right["success"]:
                transitions.append({
                    "left_alpha":left["alpha"],
                    "left_success":left["success"],
                    "right_alpha":right["alpha"],
                    "right_success":right["success"],
                    "width":right["alpha"]-left["alpha"],
                })

        report={
            "schema_version":1,
            "episode_id":a.episode_id,
            "candidate_sha":a.candidate_sha,
            "candidate_import":str(actual),
            "path_definition":"a_alpha=(1-alpha)*a_main+(alpha)*a_repair in normalized action space",
            "grid_step":a.step,
            "results":results,
            "transition_intervals":transitions,
            "success_alphas":[r["alpha"] for r in results if r["success"]],
            "failure_alphas":[r["alpha"] for r in results if not r["success"]],
            "endpoint_checks":{
                "alpha_0_main_success":next(r["success"] for r in results if r["alpha"]==0.0),
                "alpha_1_repair_success":next(r["success"] for r in results if r["alpha"]==1.0),
            },
            "claim_boundary":(
                "Deterministic same-episode continuation scan between the current-main "
                "converter output and the clean repair converter output. A transition "
                "interval measures path sensitivity under this interpolation; it is not "
                "a general robustness radius or physical safety certificate."
            ),
        }
        if not report["endpoint_checks"]["alpha_0_main_success"]:
            raise SystemExit("alpha=0 failed to reproduce main episode-8 success")
        if report["endpoint_checks"]["alpha_1_repair_success"]:
            raise SystemExit("alpha=1 unexpectedly reproduced repair success; endpoint drift")

        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        print(json.dumps(report,indent=2,sort_keys=True))
    finally:
        action_conversion.delta_pose_to_pd_ee_delta=original


if __name__=="__main__":
    main()
