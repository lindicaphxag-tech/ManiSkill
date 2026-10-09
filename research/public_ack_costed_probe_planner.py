"""Deterministic BOUNDED active probe heuristic for latent controller target memory.

Original prospective physical trial: research/ACTIVE_ACK_PROBE_NATIVE_NEW64_PREOUTCOME_V1.json.
All inputs are PUBLIC achieved XYZ, prior action-history native target hypotheses
and VERIFIED documented native normalized action BOX. No true physical ACK
receipt, no private controller-state access and NO claimed collision safety.

IMPORTANT: after actual known-delivered actuation, the runtime MUST update
EVERY complete pose-history hypothesis with that probe action before scoring.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import sqrt,isfinite
from typing import Sequence,Tuple

def vec(value,n):
    if len(value)!=n or any(not isfinite(float(q)) for q in value):
        raise ValueError("Nonfinite/malformed prior public XYZ or native limits")
    return tuple(float(z) for z in value)

def segment_min_residual(start,target,observed):
    p=vec(start,3);t=vec(target,3);y=vec(observed,3)
    v=tuple(t[i]-p[i] for i in range(3))
    d=sum(z*z for z in v)
    alpha=max(0.,min(1.,sum((y[i]-p[i])*v[i] for i in range(3))/d)) if d>0 else 0.
    proj=tuple(p[i]+alpha*v[i] for i in range(3))
    return sqrt(sum((y[i]-proj[i])**2 for i in range(3)))

@dataclass(frozen=True)
class PlannedNativeProbe:
    normalized_native_6d:Tuple[float,float,float,float,float,float]
    actual_target_translation_m:Tuple[float,float,float]
    minimum_cross_hypothesis_segment_distance_m:float
    sum_cross_hypothesis_segment_distances_m:float
    candidate_count:int
    selector_public_only:bool=True
    no_deterministic_safety_guarantee:bool=True

def choose_bounded_probe(achieved_xyz, complete_targets_xyz, native_lower_xyz, native_upper_xyz,
                         amplitude=0.12):
    x=vec(achieved_xyz,3)
    pts=[vec(v,3) for v in complete_targets_xyz]
    low=vec(native_lower_xyz,3);high=vec(native_upper_xyz,3)
    if not 2<=len(pts)<=16 or any(high[i]<=low[i] for i in range(3)):
        raise ValueError("No complete finite multi-ACK target history or illegal BOX")
    if not 0<amplitude<=1:
        raise ValueError("Probe amplitude outside declared normalized native BOX")
    # Predeclared six search candidates, without seed parity/true ACK knowledge.
    natives=[]
    for axis in range(3):
        for sign in (1.,-1.):
            values=[0.,0.,0.];values[axis]=sign*amplitude
            natives.append(tuple(values))
    selected=None
    for u in natives:
        delta=tuple(low[i]+(u[i]+1)*.5*(high[i]-low[i]) for i in range(3))
        targets=[tuple(y[i]+delta[i] for i in range(3)) for y in pts]
        midpoints=[tuple(x[i]+.5*(y[i]-x[i]) for i in range(3)) for y in targets]
        directed=[segment_min_residual(x,targets[j],midpoints[i])
                  for i in range(len(targets)) for j in range(len(targets))
                  if i!=j]
        if not directed: raise ValueError("Missing distinct complete hypotheses")
        out=PlannedNativeProbe(tuple(u)+(0.,0.,0.),delta,
                               min(directed),sum(directed),len(pts))
        if (selected is None or
            (out.minimum_cross_hypothesis_segment_distance_m,
             out.sum_cross_hypothesis_segment_distances_m)>
            (selected.minimum_cross_hypothesis_segment_distance_m,
             selected.sum_cross_hypothesis_segment_distances_m)):
            selected=out
    return selected
