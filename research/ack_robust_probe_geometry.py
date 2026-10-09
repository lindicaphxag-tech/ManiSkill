"""Geometric active information-probe certificate for UNKNOWN robot ACK histories.

This module is deliberately a SOURCE-ONLY geometric FALSIFIER, not a
physically implemented native controller action or new task benchmark.

For an achieved XYZ x, complete target candidates M_i, and a shared
physically realizable target displacement delta, consider the set-valued
public one-step observation model

 S_i(delta) = {x + alpha*(M_i + delta - x) : alpha in [amin,amax]}
              + B_2(epsilon).

We compute exact distance of the 3D finite line segments BEFORE epsilon balls
to derive conditional pairwise distinguishability. If alpha_min=0, ALL S_i
contain x, hence no delta has a POSITIVE worst-case identification margin.
This applies even if hypothetical histories have different commanded targets.

A positive certificate requires an independent established nonzero gain lower
bound and bounded error on the FUTURE physical regime. The data in the author's
existing PhysX studies do NOT establish those assumptions. XYZ also cannot
distinguish full histories differing only by orientation if target XYZ is same.

The result is an algorithmic geometry planning diagnostic, not a safety claim.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Sequence

def vec3(a):
    if len(a) != 3:
        raise ValueError("All physical achieved/commanded XYZ values have dimension 3")
    z = tuple(float(v) for v in a)
    if not all(isfinite(v) for v in z):
        raise ValueError("Nonfinite physical coordinate")
    return z

def add(a, b):
    return tuple(x+y for x,y in zip(a,b))

def sub(a, b):
    return tuple(x-y for x,y in zip(a,b))

def mul(a, r):
    return tuple(x*r for x in a)

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def norm(a):
    return sqrt(dot(a,a))

def dist(a,b):
    return norm(sub(a,b))

def clamp(t):
    return max(0.,min(1.,t))


def distance_between_segments(p0,p1,q0,q1):
    """True 3D minimum segment-to-segment Euclidean distance; stdlib only."""
    p0,p1,q0,q1 = tuple(map(vec3,(p0,p1,q0,q1)))
    v=sub(p1,p0)
    w=sub(q1,q0)
    r=sub(p0,q0)
    a=dot(v,v); b=dot(v,w); c=dot(w,w)
    d=dot(v,r); e=dot(w,r)
    candidates=[]
    def put(s,t):
        if -1e-12 <=s<=1+1e-12 and -1e-12<=t<=1+1e-12:
            s,t=clamp(s),clamp(t)
            candidates.append(dist(add(p0,mul(v,s)),add(q0,mul(w,t))))
    if a>1e-30 and c>1e-30:
        det=a*c-b*b
        if det>1e-12*a*c:
            put((b*e-c*d)/det,(a*e-b*d)/det)
    # Include optima along ALL four edges. Degenerate endpoints handled here.
    for s in (0.,1.):
        put(s,clamp((e+b*s)/c) if c>1e-30 else 0.)
    for t in (0.,1.):
        put(clamp((b*t-d)/a) if a>1e-30 else 0.,t)
    for s in (0.,1.):
        for t in (0.,1.):
            put(s,t)
    return min(candidates)


@dataclass(frozen=True)
class NativeHistory:
    history_id: str
    target_xyz: tuple[float,float,float]
    rotation_xyzw: tuple[float,float,float,float]


@dataclass(frozen=True)
class ProbeGeometryReport:
    proposed_common_target_delta_m: tuple[float,float,float]
    worst_nominal_pairwise_response_distance_m: float
    independently_required_noise_radius_m: float
    minimum_gain_assumed: float
    maximum_gain_assumed: float
    decision: str
    limitation: str


def information_probe_geometry(
    achieved_xyz: Sequence[float],
    histories: Sequence[NativeHistory],
    proposed_common_target_deltas: Sequence[Sequence[float]],
    *,
    independent_gain_lower_bound: float,
    independent_gain_upper_bound: float=1.,
    independent_noise_radius_m: float,
    required_clearance_m: float=0.002,
    max_proposed_delta_m: float=0.04,
) -> ProbeGeometryReport:
    x=vec3(achieved_xyz)
    amin,amax=independent_gain_lower_bound,independent_gain_upper_bound
    e=independent_noise_radius_m
    if not (all(isfinite(z) for z in (amin,amax,e,required_clearance_m,max_proposed_delta_m))
            and 0<=amin<=amax<=1 and e>=0 and required_clearance_m>=0 and
            max_proposed_delta_m>=0):
        raise ValueError("Invalid physical response/noise/action certificate")
    if not 2<=len(histories)<=16 or not proposed_common_target_deltas:
        raise ValueError("Need complete finite multiple target histories and prospective allowed probes")
    if len({h.history_id for h in histories})!=len(histories):
        raise ValueError("Duplicate target history")
    target=[]
    for h in histories:
        if not h.history_id or len(h.rotation_xyzw)!=4 or not all(
                isfinite(z) for z in h.rotation_xyzw):
            raise ValueError("Unknown or nonfinite complete target rotation")
        if not .999<=sum(z*z for z in h.rotation_xyzw)<=1.001:
            raise ValueError("Invalid full target quaternion")
        target.append(vec3(h.target_xyz))
    proposals=tuple(vec3(d) for d in proposed_common_target_deltas)
    if any(norm(d)>max_proposed_delta_m+1e-12 for d in proposals):
        raise ValueError("Native physical actuation budget exceeded")
    scored=[]
    for d in proposals:
        intervals=[]
        for t in target:
            displaced=add(t,d)
            diff=sub(displaced,x)
            intervals.append((add(x,mul(diff,amin)),add(x,mul(diff,amax))))
        sep=min(distance_between_segments(*intervals[i],*intervals[j])
                for i in range(len(target)) for j in range(i+1,len(target)))
        scored.append((sep,d))
    # Frozen deterministic tie-break by original declared proposal order.
    best_sep,best_d=max(enumerate(scored),key=lambda z:(z[1][0],-z[0]))[1]
    # Two separately bounded radius-e noise balls are guaranteed disjoint
    # only when nominal segment-segment distance exceeds 2e+margin.
    safe=best_sep>2*e+required_clearance_m
    return ProbeGeometryReport(
        proposed_common_target_delta_m=best_d,
        worst_nominal_pairwise_response_distance_m=best_sep,
        independently_required_noise_radius_m=e,
        minimum_gain_assumed=amin,
        maximum_gain_assumed=amax,
        decision=("CONDITIONAL_PAIRWISE_GEOMETRIC_SEPARATION" if safe
                  else "NO_UNIFORM_PUBLIC_HISTORY_CERTIFICATE_QUERY_OR_REFUSE"),
        limitation=("GEOMETRIC_DIAGNOSTIC_ONLY; requires independently verified "
                    "future gain/noise bounds and native action representability; "
                    "no physics deployment, collision, contact, latency or hardware guarantee"))


def inherent_zero_gain_nonidentifiability(
    achieved_xyz, histories, admissible_probes, *,
    epsilon_m: float
) -> bool:
    """Executable corollary: alpha in [0,1] destroys robust info by any probe."""
    r=information_probe_geometry(
        achieved_xyz,histories,admissible_probes,
        independent_gain_lower_bound=0.,
        independent_gain_upper_bound=1.,
        independent_noise_radius_m=epsilon_m)
    return abs(r.worst_nominal_pairwise_response_distance_m)<1e-10 and (
        r.decision=="NO_UNIFORM_PUBLIC_HISTORY_CERTIFICATE_QUERY_OR_REFUSE")
