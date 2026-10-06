#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from mani_skill.utils.geometry import rotation_conversions


def _a(x):
    return np.asarray(x,dtype=np.float64)


def _quat_deg(q1,q2):
    a=torch.as_tensor(q1,dtype=torch.float64)
    b=torch.as_tensor(q2,dtype=torch.float64)
    ma=rotation_conversions.quaternion_to_matrix(a)
    mb=rotation_conversions.quaternion_to_matrix(b)
    rel=ma.transpose(-1,-2) @ mb
    tr=torch.diagonal(rel,dim1=-2,dim2=-1).sum(-1)
    c=torch.clamp((tr-1.0)/2.0,-1.0,1.0)
    return float(torch.rad2deg(torch.acos(c)).item())


def _pair(main,cand):
    n=min(len(main),len(cand))
    rows=[]
    first_action=None
    first_state=None
    first_request=None
    for i in range(n):
        m=main[i]; c=cand[i]
        request_pos=float(np.linalg.norm(_a(m["delta_p"])-_a(c["delta_p"])))
        request_rot=_quat_deg(m["delta_q_inverse"],c["delta_q_inverse"])
        action_l2=float(np.linalg.norm(_a(m["normalized_action"])-_a(c["normalized_action"])))
        physical_l2=float(np.linalg.norm(_a(m["physical_scaled_action"])-_a(c["physical_scaled_action"])))
        ee_pos=float("nan"); ee_rot=float("nan")
        if "ee_pose_p_before" in m and "ee_pose_p_before" in c:
            ee_pos=float(np.linalg.norm(_a(m["ee_pose_p_before"])-_a(c["ee_pose_p_before"])))
        if "ee_pose_q_before" in m and "ee_pose_q_before" in c:
            ee_rot=_quat_deg(m["ee_pose_q_before"],c["ee_pose_q_before"])
        target_pos=float("nan"); target_rot=float("nan")
        if "target_pose_p_before" in m and "target_pose_p_before" in c:
            target_pos=float(np.linalg.norm(_a(m["target_pose_p_before"])-_a(c["target_pose_p_before"])))
        if "target_pose_q_before" in m and "target_pose_q_before" in c:
            target_rot=_quat_deg(m["target_pose_q_before"],c["target_pose_q_before"])
        row={
            "call_index":i,
            "request_position_delta_m":request_pos,
            "request_rotation_delta_deg":request_rot,
            "normalized_action_l2":action_l2,
            "physical_scaled_action_l2":physical_l2,
            "ee_position_delta_m_before":ee_pos,
            "ee_rotation_delta_deg_before":ee_rot,
            "target_position_delta_m_before":target_pos,
            "target_rotation_delta_deg_before":target_rot,
            "main_rotation_norm":m["normalized_rotation_norm"],
            "candidate_rotation_norm":c["normalized_rotation_norm"],
            "main_would_clip":m["would_clip_rotation"],
            "candidate_would_clip":c["would_clip_rotation"],
            "main_semantic_error_deg":m["semantic_rotation_error_deg"],
            "candidate_semantic_error_deg":c["semantic_rotation_error_deg"],
        }
        rows.append(row)
        if first_action is None and physical_l2>1e-7:
            first_action=i
        if first_request is None and (request_pos>1e-7 or request_rot>1e-5):
            first_request=i
        if first_state is None and (
            (np.isfinite(ee_pos) and ee_pos>1e-7)
            or (np.isfinite(ee_rot) and ee_rot>1e-5)
            or (np.isfinite(target_pos) and target_pos>1e-7)
            or (np.isfinite(target_rot) and target_rot>1e-5)
        ):
            first_state=i
    return {
        "aligned_call_count":n,
        "main_call_count":len(main),
        "candidate_call_count":len(cand),
        "first_physical_action_divergence_call":first_action,
        "first_request_divergence_call":first_request,
        "first_controller_state_divergence_call":first_state,
        "clip_schedule_identical_on_aligned_calls":all(
            bool(main[i]["would_clip_rotation"])==bool(cand[i]["would_clip_rotation"])
            for i in range(n)
        ),
        "main_clip_calls":[i for i in range(len(main)) if main[i]["would_clip_rotation"]],
        "candidate_clip_calls":[i for i in range(len(cand)) if cand[i]["would_clip_rotation"]],
        "max_request_position_delta_m":max((r["request_position_delta_m"] for r in rows),default=0.0),
        "max_request_rotation_delta_deg":max((r["request_rotation_delta_deg"] for r in rows),default=0.0),
        "max_physical_scaled_action_l2":max((r["physical_scaled_action_l2"] for r in rows),default=0.0),
        "mean_main_semantic_error_deg":float(np.mean([r["main_semantic_error_deg"] for r in rows])) if rows else None,
        "mean_candidate_semantic_error_deg":float(np.mean([r["candidate_semantic_error_deg"] for r in rows])) if rows else None,
        "rows":rows,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)\n    p.add_argument("--episode-id",type=int,required=True)
    a=p.parse_args()
    docs={}
    for name in ("current_main","contract_adapter_v2","contract_adapter_v2_controller_fixed"):
        docs[name]=json.loads((a.root/f"{name}.json").read_text())
    report={
        "schema_version":1,
        "episode_id":a.episode_id,
        "pairs":{
            "main_vs_adapter":_pair(docs["current_main"]["rows"],docs["contract_adapter_v2"]["rows"]),
            "main_vs_adapter_controller_fixed":_pair(docs["current_main"]["rows"],docs["contract_adapter_v2_controller_fixed"]["rows"]),
            "adapter_vs_adapter_controller_fixed":_pair(docs["contract_adapter_v2"]["rows"],docs["contract_adapter_v2_controller_fixed"]["rows"]),
        },
        "claim_boundary":(
            f"First-divergence diagnostic for serial-context episode {a.episode_id}. Thresholds identify where "
            "observable request/controller traces diverge; they do not by themselves "
            "prove which divergence causes final task failure."
        ),
        "thresholds":{
            "position_m":1e-7,
            "rotation_deg":1e-5,
            "physical_action_l2":1e-7,
        },
    }
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    compact={k:{kk:vv for kk,vv in v.items() if kk!="rows"} for k,v in report["pairs"].items()}
    print(json.dumps({"episode_id":a.episode_id,"pairs":compact,"claim_boundary":report["claim_boundary"]},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
