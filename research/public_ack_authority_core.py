"""Minimal public-only ACK target authority core. Standard-library only.

Separates a KNOWN-EXECUTED native target/motion model witness (before ACK
uncertainty) from candidate-history UNIQUENESS under later unknown ACKs.

Not a dynamics certificate, no private robot controller access, no ROS.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Optional, Sequence, Tuple

Vec3=Tuple[float,float,float]
Quat=Tuple[float,float,float,float]

@dataclass(frozen=True)
class CompleteTargetHistory:
    """Full SE(3) identity is tracked even though public response is XYZ."""
    history_id: str
    target_xyz: Vec3
    quaternion_xyzw: Quat

@dataclass(frozen=True)
class KnownTargetAnchor:
    """Pre-fault motion with a KNOWN-DELIVERED native action."""
    before_xyz: Vec3
    after_xyz: Vec3
    acknowledged_native_target_xyz: Vec3
    source_step: int

@dataclass(frozen=True)
class AuthorityDecision:
    mode: str # AUTHORIZE_COMPLETE_HISTORY or QUERY_NATIVE_TARGET
    selected_history_id: Optional[str]
    reason: str
    anchor_residual_m: float
    candidate_public_residuals_m: Tuple[float,...]
    public_samples_charged: int

def _vec(value: Sequence[float], n: int, name: str):
    if len(value)!=n:
        raise ValueError(f"{name} must have {n} finite numbers")
    x=tuple(float(v) for v in value)
    if not all(isfinite(v) for v in x):
        raise ValueError(f"{name} contains a nonfinite value")
    return x

def _dist(a,b):
    return sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def public_segment_residual(before_xyz,after_xyz,known_target_xyz) -> float:
    """L2 min at alpha in [0,1] for after ~= before + alpha(target-before)."""
    start=_vec(before_xyz,3,"public_before")
    obs=_vec(after_xyz,3,"public_after")
    target=_vec(known_target_xyz,3,"hypothetical_native_target")
    direction=tuple(t-s for t,s in zip(target,start))
    denom=sum(d*d for d in direction)
    alpha=max(0.0,min(1.0,sum((o-s)*d for o,s,d in zip(obs,start,direction))/denom)) if denom>0 else 0.0
    projected=tuple(s+alpha*d for s,d in zip(start,direction))
    return _dist(obs,projected)

def public_only_authority(
    anchor: KnownTargetAnchor,
    probe_before_xyz: Vec3,
    probe_after_xyz: Vec3,
    complete_hypotheses: Sequence[CompleteTargetHistory],
    *,
    epsilon_m: float,
    competitor_margin_m: float=0.002,
    min_known_anchor_excitation_m: float=0.01
) -> AuthorityDecision:
    if not(isfinite(epsilon_m) and 0<epsilon_m<1
           and isfinite(competitor_margin_m) and competitor_margin_m>=0
           and isfinite(min_known_anchor_excitation_m) and min_known_anchor_excitation_m>0):
        raise ValueError("Invalid preregistered physical response model parameters")
    if anchor.source_step>=4:
        raise ValueError("Anchor must precede the unknown ACK and t4 public probe")
    known_before=_vec(anchor.before_xyz,3,"anchor_pre")
    known_after=_vec(anchor.after_xyz,3,"anchor_post")
    known_target=_vec(anchor.acknowledged_native_target_xyz,3,"anchor_known_target")
    probe_before=_vec(probe_before_xyz,3,"probe_before")
    probe_after=_vec(probe_after_xyz,3,"probe_after")
    if not 2<=len(complete_hypotheses)<=32:
        raise ValueError("Need a finite complete multiple execution-history set")
    seen=set()
    for h in complete_hypotheses:
        if not h.history_id or h.history_id in seen:
            raise ValueError("Target history identities must be unique and nonempty")
        seen.add(h.history_id)
        _vec(h.target_xyz,3,"target")
        q=_vec(h.quaternion_xyzw,4,"rotation")
        norm=sum(v*v for v in q)
        if not .999<=norm<=1.001:
            raise ValueError("Full native history quaternion must be normalized")
    anchor_error=public_segment_residual(known_before,known_after,known_target)
    residuals=tuple(public_segment_residual(probe_before,probe_after,h.target_xyz)
                    for h in complete_hypotheses)
    def query(reason):
        return AuthorityDecision("QUERY_NATIVE_TARGET",None,reason,
                                 anchor_error,residuals,4)
    if _dist(known_before,known_target)<min_known_anchor_excitation_m:
        return query("KNOWN_ACK_ANCHOR_INSUFFICIENT_EXCITATION")
    if anchor_error>epsilon_m:
        return query("KNOWN_ACK_MOTION_RESPONSE_MODEL_FAILED")
    viable=[i for i,r in enumerate(residuals) if r<=epsilon_m]
    if len(viable)!=1:
        return query("UNKNOWN_ACK_HISTORY_PUBLIC_RESPONSE_AMBIGUOUS_OR_OUTSIDE_MODEL")
    idx=viable[0]
    if any(r<=epsilon_m+competitor_margin_m for i,r in enumerate(residuals) if i!=idx):
        return query("PUBLIC_MODEL_MARGIN_NOT_SEPARATED")
    return AuthorityDecision("AUTHORIZE_COMPLETE_HISTORY",
                             complete_hypotheses[idx].history_id,
                             "CONDITIONAL_UNIQUE_PUBLIC_HISTORY_NOT_SAFETY_CERTIFICATE",
                             anchor_error,residuals,4)
