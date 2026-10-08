"""Set-membership ACK history identification from public achieved-EE response.

This is a pure geometric *conditional* identification certificate, NOT a
general robot-motion, collision, contact or task-success safety certificate.

Contract (explicit and externally validated, otherwise refuse):
  y = x_before + alpha * (M_h - x_before) + e
  alpha in independently attested [alpha_min,alpha_max], 0<=alpha<=1
  ||e||_2 <= independently attested sensor_and_model_error_m.

h in {"applied","held"} means the two candidate *commanded* target XYZ
from an action-history observer. y is achieved pose AFTER a common no-op
target-delta physical probe, not a hidden target getter.

Geometric test: the possible response under each history is a line segment
swept by alpha plus an error ball. A valid history is never eliminated if
the declared motion/noise envelope covers the actual motion. If exactly
one possible history remains, return that history; else abstain/fail closed.
No proof of the envelope's validity is implied by this module.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from math import isfinite, sqrt
from typing import Sequence


class Decision(str,Enum):
    APPLIED="APPLIED"
    HELD="HELD"
    ABSTAIN_OVERLAP="ABSTAIN_OVERLAP"
    REFUSE_UNATTESTED_DYNAMICS="REFUSE_UNATTESTED_DYNAMICS"
    REFUSE_MODEL_FALSIFIED="REFUSE_MODEL_FALSIFIED"


@dataclass(frozen=True)
class ProbeEvidence:
    before_xyz_m: tuple[float,float,float]
    after_xyz_m: tuple[float,float,float]
    applied_target_xyz_m: tuple[float,float,float]
    held_target_xyz_m: tuple[float,float,float]
    alpha_min: float
    alpha_max: float
    sensor_and_model_error_m: float
    external_calibration_attested: bool
    probe_native_zero_delta_confirmed: bool


@dataclass(frozen=True)
class HistoryDecision:
    decision: Decision
    applied_compatible: bool
    held_compatible: bool
    applied_residual_m: float
    held_residual_m: float
    applied_best_alpha: float | None
    held_best_alpha: float | None
    identification_margin_m: float
    reason: str

    @property
    def may_select_history(self) -> bool:
        return self.decision in (Decision.APPLIED,Decision.HELD)


def _v3(values: Sequence[float],name: str)->tuple[float,float,float]:
    if len(values)!=3:
        raise ValueError(name+" must have exactly three XYZ coordinates")
    out=tuple(float(v) for v in values)
    if not all(isfinite(v) for v in out):
        raise ValueError(name+" contains non-finite coordinates")
    return out


def _norm_sq(v): return sum(u*u for u in v)
def _dot(a,b): return sum(x*y for x,y in zip(a,b))
def _norm(v): return sqrt(_norm_sq(v))
def _sub(a,b): return tuple(x-y for x,y in zip(a,b))


def _segment_distance(x,y,target,lo,hi):
    """Minimum Euclidean residual to x + alpha(target-x), alpha in [lo,hi].

    Optimizes ONE scalar alpha exactly by projection on the line, clamps it
    to the externally declared interval. No stochastic state estimation.
    """
    direction=_sub(target,x)
    d_sq=_norm_sq(direction)
    if d_sq==0:
        return _norm(_sub(y,x)),lo
    alpha_hat=_dot(_sub(y,x),direction)/d_sq
    alpha=max(lo,min(hi,alpha_hat))
    predicted=tuple(xi+alpha*di for xi,di in zip(x,direction))
    return _norm(_sub(y,predicted)),alpha


def distinguish_history(evidence: ProbeEvidence, *, numerical_guard_m=1e-9)->HistoryDecision:
    if not isinstance(evidence,ProbeEvidence):
        raise TypeError("ProbeEvidence with independently attested physical model required")
    x=_v3(evidence.before_xyz_m,"before")
    y=_v3(evidence.after_xyz_m,"after")
    a=_v3(evidence.applied_target_xyz_m,"applied target")
    h=_v3(evidence.held_target_xyz_m,"held target")
    lo=float(evidence.alpha_min)
    hi=float(evidence.alpha_max)
    noise=float(evidence.sensor_and_model_error_m)
    guard=float(numerical_guard_m)
    if not all(isfinite(v) for v in (lo,hi,noise,guard)):
        raise ValueError("Non-finite dynamical interval, error bound or numerical margin")
    if not (0<=lo<=hi<=1 and 0<=noise<=0.25 and 0<=guard<=1e-5):
        raise ValueError("Unsupported response contraction/noise/guard contract")
    if not (evidence.external_calibration_attested and evidence.probe_native_zero_delta_confirmed):
        return HistoryDecision(Decision.REFUSE_UNATTESTED_DYNAMICS,
            False,False,float("inf"),float("inf"),None,None,0.0,
            "Independent response envelope or actual zero-delta probe not attested")
    d_a,alpha_a=_segment_distance(x,y,a,lo,hi)
    d_h,alpha_h=_segment_distance(x,y,h,lo,hi)
    feasible_a=d_a<=noise+guard
    feasible_h=d_h<=noise+guard
    margin=abs(d_a-d_h)
    if feasible_a and not feasible_h:
        return HistoryDecision(Decision.APPLIED,True,False,d_a,d_h,
            alpha_a,alpha_h,max(0.,d_h-noise-guard),
            "HELD hypothesis incompatible with declared public-response physics")
    if feasible_h and not feasible_a:
        return HistoryDecision(Decision.HELD,False,True,d_a,d_h,
            alpha_a,alpha_h,max(0.,d_a-noise-guard),
            "APPLIED hypothesis incompatible with declared public-response physics")
    if feasible_a and feasible_h:
        return HistoryDecision(Decision.ABSTAIN_OVERLAP,True,True,d_a,d_h,
            alpha_a,alpha_h,0.0,
            "Both hidden histories remain physically consistent; do not guess")
    return HistoryDecision(Decision.REFUSE_MODEL_FALSIFIED,False,False,d_a,d_h,
        alpha_a,alpha_h,0.0,
        "Neither history can explain achieved response under claimed model; refuse")
