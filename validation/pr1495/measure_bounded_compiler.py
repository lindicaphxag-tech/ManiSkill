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
from mani_skill.utils.geometry import rotation_conversions


def summary(values):
    a=np.asarray(values,dtype=np.float64)
    if a.size==0:
        return {"count":0}
    return {
        "count":int(a.size),
        "mean":float(a.mean()),
        "median":float(np.median(a)),
        "p90":float(np.percentile(a,90)),
        "p95":float(np.percentile(a,95)),
        "p99":float(np.percentile(a,99)),
        "max":float(a.max()),
    }


def rotation_error_deg(desired_matrix, realized_matrix):
    rel=desired_matrix.transpose(-1,-2) @ realized_matrix
    trace=torch.diagonal(rel,dim1=-2,dim2=-1).sum(-1)
    cosine=torch.clamp((trace-1.0)/2.0,-1.0,1.0)
    return float(torch.rad2deg(torch.acos(cosine)).item())


def realized_matrix(controller, rotation_action):
    dtype=controller.action_space_low.dtype
    device=controller.action_space_low.device
    full=torch.zeros(6,dtype=dtype,device=device)
    full[3:]=torch.as_tensor(rotation_action,dtype=dtype,device=device)
    physical=controller._clip_and_scale_action(full[None,:])[0,3:]
    return rotation_conversions.euler_angles_to_matrix(physical,"XYZ")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--traj-path",required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--count",type=int,default=10)
    p.add_argument("--expected-source-root",type=Path,required=True)
    args=p.parse_args()

    actual=Path(mani_skill.__file__).resolve()
    expected=args.expected_source_root.resolve()
    if expected not in actual.parents:
        raise SystemExit(f"wrong ManiSkill source imported: {actual}; expected {expected}")

    original=action_conversion.delta_pose_to_pd_ee_delta
    records=[]

    def instrumented(controller,delta_pose,pos_only=False):
        result=original(controller,delta_pose,pos_only=pos_only)
        if pos_only or not isinstance(controller,PDEEPoseController):
            return result

        dtype=controller.action_space_low.dtype
        device=controller.action_space_low.device
        inverse_input=torch.as_tensor(
            np.asarray(delta_pose.q),dtype=dtype,device=device
        )
        desired_q=rotation_conversions.quaternion_invert(inverse_input)
        desired_matrix=rotation_conversions.quaternion_to_matrix(desired_q)
        desired_euler=rotation_conversions.matrix_to_euler_angles(
            desired_matrix,"XYZ"
        )

        raw=np.asarray(
            action_conversion._normalized_pd_ee_rotation_action(
                controller,desired_euler.cpu().numpy()
            ),
            dtype=np.float64,
        )
        raw_norm=float(np.linalg.norm(raw))
        if raw_norm <= 1.0 + 1e-6:
            return result

        radial=raw/raw_norm
        bounded=np.asarray(
            action_conversion._bounded_pd_ee_rotation_action(
                controller,desired_q.cpu().numpy()
            ),
            dtype=np.float64,
        )

        radial_error=rotation_error_deg(
            desired_matrix,realized_matrix(controller,radial)
        )
        bounded_error=rotation_error_deg(
            desired_matrix,realized_matrix(controller,bounded)
        )
        records.append({
            "raw_norm":raw_norm,
            "radial_error_deg":radial_error,
            "bounded_error_deg":bounded_error,
            "improvement_deg":radial_error-bounded_error,
            "bounded_norm":float(np.linalg.norm(bounded)),
        })
        return result

    action_conversion.delta_pose_to_pd_ee_delta=instrumented
    try:
        replay_trajectory.main(
            replay_trajectory.Args(
                traj_path=args.traj_path,
                sim_backend="physx_cpu",
                obs_mode="state",
                target_control_mode="pd_ee_delta_pose",
                save_traj=False,
                save_video=False,
                use_first_env_state=True,
                count=args.count,
                num_envs=1,
            )
        )
    finally:
        action_conversion.delta_pose_to_pd_ee_delta=original

    radial=[x["radial_error_deg"] for x in records]
    bounded=[x["bounded_error_deg"] for x in records]
    improvements=[x["improvement_deg"] for x in records]
    bounded_norm=[x["bounded_norm"] for x in records]
    report={
        "schema_version":1,
        "source_root":str(expected),
        "mani_skill_import":str(actual),
        "claim_boundary":"Clipped-call local SO(3) compilation error on calls generated while replaying official PegInsertionSide demonstrations; not task success.",
        "bound_required_calls":len(records),
        "radial_clip_error_deg":summary(radial),
        "bounded_compiler_error_deg":summary(bounded),
        "improvement_deg":summary(improvements),
        "fraction_strictly_improved":float(np.mean(np.asarray(improvements)>1e-7)) if improvements else 0.0,
        "max_bounded_action_norm":max(bounded_norm) if bounded_norm else 0.0,
        "dominates_mean":bool(records and np.mean(bounded) <= np.mean(radial)+1e-8),
        "dominates_p95":bool(records and np.percentile(bounded,95) <= np.percentile(radial,95)+1e-8),
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

    if not records:
        raise SystemExit("no bound-required official-demo calls were observed")
    if not report["dominates_mean"] or not report["dominates_p95"]:
        raise SystemExit("bounded compiler did not dominate radial clipping")
    if report["max_bounded_action_norm"] > 1.0 + 1e-5:
        raise SystemExit("bounded compiler violated normalized action ball")


if __name__=="__main__":
    main()
