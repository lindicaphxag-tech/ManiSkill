#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

import mani_skill
from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory import replay_trajectory
from mani_skill.trajectory.utils.actions import conversion as action_conversion
from mani_skill.utils import io_utils
from mani_skill.utils.geometry import rotation_conversions


def _arr(x):
    if torch.is_tensor(x):
        x=x.detach().cpu().numpy()
    return np.asarray(x,dtype=np.float64).tolist()


def _quat_distance_deg(q1, q2):
    a=torch.as_tensor(q1,dtype=torch.float64)
    b=torch.as_tensor(q2,dtype=torch.float64)
    ma=rotation_conversions.quaternion_to_matrix(a)
    mb=rotation_conversions.quaternion_to_matrix(b)
    rel=ma.transpose(-1,-2) @ mb
    tr=torch.diagonal(rel,dim1=-2,dim2=-1).sum(-1)
    c=torch.clamp((tr-1)/2,-1.0,1.0)
    return float(torch.rad2deg(torch.acos(c)).item())


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--traj-path",required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--variant",required=True)
    p.add_argument("--expected-source-root",type=Path,required=True)
    p.add_argument("--count",type=int,default=9)
    p.add_argument("--episode-id",type=int,default=8)
    a=p.parse_args()

    actual=Path(mani_skill.__file__).resolve()
    expected=a.expected_source_root.resolve()
    if expected not in actual.parents:
        raise SystemExit(f"wrong source imported: {actual}; expected {expected}")

    metadata=io_utils.load_json(a.traj_path.replace(".h5",".json"))
    episode_ids=[int(ep["episode_id"]) for ep in metadata["episodes"][:a.count]]
    if a.episode_id not in episode_ids:
        raise SystemExit(f"episode {a.episode_id} not in first {a.count} episodes")

    original_delta=action_conversion.delta_pose_to_pd_ee_delta
    original_from=action_conversion.from_pd_joint_pos
    cursor={"episode":None,"call":0}
    rows=[]

    def wrapped_from(*args,**kwargs):
        idx=wrapped_from.index
        if idx>=len(episode_ids):
            raise RuntimeError("episode accounting overflow")
        cursor["episode"]=episode_ids[idx]
        cursor["call"]=0
        wrapped_from.index += 1
        result=original_from(*args,**kwargs)
        return result
    wrapped_from.index=0

    def wrapped_delta(controller,delta_pose,pos_only=False):
        before_ee=None
        before_target=None
        if isinstance(controller,PDEEPoseController):
            try:
                before_ee=controller.ee_link.pose
            except Exception:
                pass
            try:
                before_target=controller._target_pose
            except Exception:
                pass

        action=original_delta(controller,delta_pose,pos_only=pos_only)
        if (
            cursor["episode"]==a.episode_id
            and not pos_only
            and isinstance(controller,PDEEPoseController)
        ):
            tensor=torch.as_tensor(
                action,dtype=controller.action_space_low.dtype,
                device=controller.action_space_low.device,
            ).reshape(1,-1)
            physical=controller._clip_and_scale_action(tensor.clone())[0]
            qin=np.asarray(delta_pose.q,dtype=np.float64)
            desired_q=rotation_conversions.quaternion_invert(
                torch.as_tensor(qin,dtype=torch.float64)
            )
            desired_m=rotation_conversions.quaternion_to_matrix(desired_q)
            realized_m=rotation_conversions.euler_angles_to_matrix(
                physical[3:6].to(torch.float64),"XYZ"
            )
            rel=desired_m.transpose(-1,-2) @ realized_m
            tr=torch.diagonal(rel,dim1=-2,dim2=-1).sum(-1)
            cos=torch.clamp((tr-1)/2,-1.0,1.0)
            semantic_err=float(torch.rad2deg(torch.acos(cos)).item())
            row={
                "call_index":cursor["call"],
                "episode_id":a.episode_id,
                "delta_p":_arr(delta_pose.p),
                "delta_q_inverse":_arr(delta_pose.q),
                "normalized_action":_arr(action),
                "normalized_rotation_norm":float(np.linalg.norm(np.asarray(action[3:],dtype=np.float64))),
                "would_clip_rotation":bool(np.linalg.norm(np.asarray(action[3:],dtype=np.float64))>1.0),
                "physical_scaled_action":_arr(physical),
                "semantic_rotation_error_deg":semantic_err,
            }
            if before_ee is not None:
                row["ee_pose_p_before"]=_arr(before_ee.p)
                row["ee_pose_q_before"]=_arr(before_ee.q)
            if before_target is not None:
                row["target_pose_p_before"]=_arr(before_target.p)
                row["target_pose_q_before"]=_arr(before_target.q)
            rows.append(row)
            cursor["call"] += 1
        return action

    action_conversion.from_pd_joint_pos=wrapped_from
    action_conversion.delta_pose_to_pd_ee_delta=wrapped_delta
    try:
        replay_trajectory.main(
            replay_trajectory.Args(
                traj_path=a.traj_path,
                sim_backend="physx_cpu",
                obs_mode="state",
                target_control_mode="pd_ee_delta_pose",
                save_traj=False,
                save_video=False,
                use_first_env_state=True,
                count=a.count,
                num_envs=1,
            )
        )
    finally:
        action_conversion.from_pd_joint_pos=original_from
        action_conversion.delta_pose_to_pd_ee_delta=original_delta

    doc={
        "schema_version":1,
        "variant":a.variant,
        "episode_id":a.episode_id,
        "source_root":str(expected),
        "mani_skill_import":str(actual),
        "call_count":len(rows),
        "rows":rows,
        "claim_boundary":"Episode-level conversion/control trace for first-divergence diagnosis; not a performance metric.",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in doc.items() if k!="rows"},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
