"""Frozen task/action expert selector over original geometry and trained ICERE.

Offline training labels and native privileged ground truth are NOT accepted by
this API. The source-only empirical zero-error calibration IS NOT a guarantee
of selective error probability on fresh reset populations.
"""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
import torch
from research.conditional_residual_energy import ConditionalResidualEnergy,authorize_from_public

PROTO="research/ICERE_UNSEEN_PPO_TASK_PREOUTCOME_20261010.json"
_cached=None

def frozen_model():
    global _cached
    if _cached is not None:return _cached
    m=json.loads(Path(PROTO).read_text())
    if m["schema"]!="icere_unseen_physx_selective_authority_v1":
        raise RuntimeError("Missing frozen heldout test protocol")
    path=os.environ.get("ICERE_FROZEN_MODEL_PT","")
    if not path or not Path(path).is_file():
        raise RuntimeError("Missing frozen source-only checkpoint, refuse any online learned authority")
    digest=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest!=m["model_full_weights_sha256"]:
        raise RuntimeError("Source-only pretrained ICERE checkpoint identity mismatch")
    net=ConditionalResidualEnergy(hidden=24)
    net.load_state_dict(torch.load(path,map_location="cpu",weights_only=True),strict=True)
    net.eval()
    _cached=net
    return net

def decide_public_authority(*,task:str,probe:str,evidence:dict)->tuple[bool,int|None,str,float]:
    """Only data available from the public observer BEFORE audit truth reads."""
    p=json.loads(Path(PROTO).read_text())
    key=task+":"+probe
    if p["expert_route"][key]=="A_original_geometry":
        residuals=evidence["candidate_residuals_m"]
        eps=evidence["prior_training_epsilon_m"]
        winners=[i for i,d in enumerate(residuals) if d<=eps+1e-12]
        good=bool(len(winners)==1 and all(d>eps+.002 for i,d in enumerate(residuals) if i!=winners[0]))
        return good,(winners[0] if good else None),"ORIGINAL_GEOMETRY_REGISTERED_EXPERT",float("nan")
    if p["expert_route"][key]!="ICERE_full":
        return False,None,"UNKNOWN_EXPERT_FAIL_CLOSED",float("nan")
    try:
        result=authorize_from_public(frozen_model(),
            threshold=float(p["full_model_offline_thresholds"][key]),task=task,probe=probe,
            epsilon_m=float(evidence["prior_training_epsilon_m"]),
            residuals_m=tuple(evidence["candidate_residuals_m"]),
            public_before_xyz_m=tuple(evidence["before_xyz"]),
            public_after_xyz_m=tuple(evidence["after_xyz"]),
            rotation_spread_rad=float(evidence["max_hypothetical_rotation_spread_rad"]))
        return result.kind=="AUTHORIZE",result.candidate_index,result.reason,result.score
    except (KeyError,ValueError,TypeError,RuntimeError) as exc:
        # Unlike model/weight integrity failures caught by frozen_model(), a
        # missing public value must not silently authorize.
        if "checkpoint" in str(exc).lower() or "missing frozen" in str(exc).lower():
            raise
        return False,None,"PUBLIC_EVIDENCE_MISSING_OR_INVALID",float("nan")
