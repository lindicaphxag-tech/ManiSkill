#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import sapien
import torch

import mani_skill
from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory.utils.actions import conversion as action_conversion
from mani_skill.utils.geometry import rotation_conversions


def _summary(values):
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


def _rotation_error_deg(desired, realized):
    rel=desired.transpose(-1,-2) @ realized
    trace=torch.diagonal(rel,dim1=-2,dim2=-1).sum(-1)
    cosine=torch.clamp((trace-1.0)/2.0,-1.0,1.0)
    return float(torch.rad2deg(torch.acos(cosine)).item())


def _restore(value):
    if isinstance(value,list):
        return np.asarray(value,dtype=np.float64)
    return float(value)


def _controller(record):
    controller=object.__new__(PDEEPoseController)
    cfg=record["config"]
    controller.config=SimpleNamespace(
        use_delta=bool(cfg["use_delta"]),
        normalize_action=bool(cfg["normalize_action"]),
        rot_lower=_restore(cfg["rot_lower"]),
        rot_upper=_restore(cfg["rot_upper"]),
        frame=str(cfg["frame"]),
    )
    controller.action_space_low=torch.tensor(
        record["action_space_low"],dtype=torch.float64
    )
    controller.action_space_high=torch.tensor(
        record["action_space_high"],dtype=torch.float64
    )
    return controller


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--corpus",type=Path,required=True)
    p.add_argument("--variant",required=True)
    p.add_argument("--expected-source-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()

    actual=Path(mani_skill.__file__).resolve()
    expected=args.expected_source_root.resolve()
    if expected not in actual.parents:
        raise SystemExit(f"wrong ManiSkill source imported: {actual}; expected {expected}")

    corpus=json.loads(args.corpus.read_text(encoding="utf-8"))
    rows=[]
    for index,record in enumerate(corpus["records"]):
        controller=_controller(record)
        delta_pose=sapien.Pose(
            np.asarray(record["p"],dtype=np.float64),
            np.asarray(record["q_inverse_input"],dtype=np.float64),
        )
        action=action_conversion.delta_pose_to_pd_ee_delta(
            controller,delta_pose,pos_only=False
        )
        tensor=torch.as_tensor(action,dtype=torch.float64).reshape(1,-1)
        physical=controller._clip_and_scale_action(tensor.clone())[0]

        inverse_q=torch.as_tensor(
            record["q_inverse_input"],dtype=torch.float64
        )
        desired_q=rotation_conversions.quaternion_invert(inverse_q)
        desired_matrix=rotation_conversions.quaternion_to_matrix(desired_q)
        realized_matrix=rotation_conversions.euler_angles_to_matrix(
            physical[3:6],"XYZ"
        )
        rotation_error=_rotation_error_deg(desired_matrix,realized_matrix)
        position_error=float(
            torch.linalg.norm(
                physical[:3]-torch.as_tensor(record["p"],dtype=torch.float64)
            ).item()
        )
        rot_norm=float(np.linalg.norm(np.asarray(action[3:],dtype=np.float64)))
        rows.append(
            {
                "index":index,
                "rotation_error_deg":rotation_error,
                "position_error":position_error,
                "normalized_rotation_norm":rot_norm,
                "rotation_clipped":bool(rot_norm>1.0+1e-6),
            }
        )

    if len(rows)!=int(corpus["request_count"]):
        raise SystemExit("paired request accounting mismatch")
    rot=[x["rotation_error_deg"] for x in rows]
    pos=[x["position_error"] for x in rows]
    unclipped=[x["rotation_error_deg"] for x in rows if not x["rotation_clipped"]]
    clipped=[x["rotation_error_deg"] for x in rows if x["rotation_clipped"]]
    report={
        "schema_version":1,
        "variant":args.variant,
        "corpus":corpus["corpus"],
        "corpus_sha256":corpus["corpus_sha256"],
        "source_root":str(expected),
        "mani_skill_import":str(actual),
        "request_count":len(rows),
        "rotation_error_deg":_summary(rot),
        "rotation_error_deg_unclipped":_summary(unclipped),
        "rotation_error_deg_clipped":_summary(clipped),
        "position_error":_summary(pos),
        "clipped_calls":sum(x["rotation_clipped"] for x in rows),
        "paired_rows":rows,
        "claim_boundary":(
            "Paired converter-to-controller semantic fidelity on one immutable "
            "request corpus. Every compared implementation receives the exact same "
            "delta poses and controller bounds."
        ),
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="paired_rows"},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
