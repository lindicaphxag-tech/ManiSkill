"""Controller-memory funnel feasibility, under the VERIFIED ManiSkill native chart.

A sequence of common root-frame target deltas cannot erase hidden commanded-
target disagreement: translations share the same delta and root-left rotation
is an SO(3) isometry. Observations may separate beliefs and a privileged
noninjective setter may collapse them; neither is a free physical command.
Only NEGATIVE feasibility certificates; any pass is UNKNOWN, not safe/optimal.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import acos, isfinite, sqrt
from itertools import combinations

CHART="root_translation:root_aligned_body_rotation"
@dataclass(frozen=True)
class Pose:
    xyz:tuple[float,float,float]
    xyzw:tuple[float,float,float,float]

@dataclass(frozen=True)
class Verdict:
    status:str
    exact_translation_lower_bound_m:float
    universal_rotation_lower_bound_rad:float
    translation_pair_diameter_inf_m:float
    rotation_pair_diameter_rad:float
    active_privileged_write_cost:int
    reason:str

def _valid_pose(p):
    if not isinstance(p,Pose) or len(p.xyz)!=3 or len(p.xyzw)!=4:
        raise ValueError("Complete SE3 hypotheses required")
    if not all(isfinite(x) for x in (*p.xyz,*p.xyzw)):
        raise ValueError("Nonfinite native target hypotheses")
    q=sqrt(sum(x*x for x in p.xyzw))
    if abs(q-1.)>1e-5:
        raise ValueError("Unnormalized controller quaternion")

def _rot_distance(p,q):
    dot=abs(sum(a*b for a,b in zip(p.xyzw,q.xyzw)))
    return 2*acos(min(1.,max(0.,dot)))

def assess(*,histories,desired:Pose,delta_lower,delta_upper,
           position_budget_inf_m,rotation_budget_rad,
           controller_frame,verified_contract,has_authorized_absolute_target_write=False):
    if not isinstance(histories,tuple) or not histories or len(histories)>16:
        raise ValueError("One to sixteen explicit target histories required")
    for x in (*histories,desired):_valid_pose(x)
    if (len(delta_lower)!=3 or len(delta_upper)!=3 or
        not all(isfinite(v) for v in (*delta_lower,*delta_upper)) or
        any(lo>hi for lo,hi in zip(delta_lower,delta_upper)) or
        not all(isfinite(x) and x>=0 for x in (position_budget_inf_m,rotation_budget_rad))):
        raise ValueError("Invalid native translation bounds / task budgets")
    if controller_frame!=CHART or verified_contract is not True:
        return Verdict("REFUSE_UNVERIFIED_CONTROLLER_CHART",float("inf"),
                       float("inf"),float("inf"),float("inf"),0,
                       "Cannot prove memory-funnel invariance on an unverified action chart")
    positions=[p.xyz for p in histories]
    lo=[min(p[j] for p in positions) for j in range(3)]
    hi=[max(p[j] for p in positions) for j in range(3)]
    diam_inf=max(hi[j]-lo[j] for j in range(3))
    diam_rot=max((_rot_distance(a,b) for a,b in combinations(histories,2)),default=0.)
    # Exact minimax translation under native action box: axis-aligned centers,
    # then clamp each dimension to feasible delta. No stochastic assumption.
    worst_per_axis=[]
    for j in range(3):
        midpoint=(lo[j]+hi[j])/2.
        wanted=desired.xyz[j]-midpoint
        delta=max(delta_lower[j],min(delta_upper[j],wanted))
        worst_per_axis.append(max(abs(lo[j]+delta-desired.xyz[j]),
                                  abs(hi[j]+delta-desired.xyz[j])))
    translation_exact=max(worst_per_axis)
    # SO3 triangle inequality: any common left-root rotation is isometric,
    # so max_i d(R_delta R_i,R_goal)>= max_i,j d(R_i,R_j)/2.
    rot_lb=diam_rot/2.
    if (translation_exact>position_budget_inf_m+1e-10 or
        rot_lb>rotation_budget_rad+1e-10):
        return Verdict("IMPOSSIBLE_UNDER_COMMON_RELATIVE_DELTA",translation_exact,rot_lb,
                       diam_inf,diam_rot,0,
                       "Geometric lower bound excludes every common relative action; sensing or a genuinely different control interface is required")
    if diam_inf>1e-9 or diam_rot>1e-8:
        if has_authorized_absolute_target_write:
            return Verdict("POTENTIAL_PRIVILEGED_REANCHOR_MUST_BE_EXECUTED_AND_AUDITED",
                           translation_exact,rot_lb,diam_inf,diam_rot,1,
                           "Noninjective internal target write can collapse memory hypotheses but costs one privileged state mutation; physical task outcome remains unknown")
        return Verdict("UNKNOWN_FEASIBLE_GOAL_BUT_MEMORY_CANNOT_COLLAPSE",
                       translation_exact,rot_lb,diam_inf,diam_rot,0,
                       "Necessary geometric budgets pass; action feasibility, contacts, IK and eventual task success remain unproven")
    return Verdict("UNKNOWN_SINGLE_MEMORY_REQUIRES_NATIVE_VERIFICATION",
                   translation_exact,rot_lb,diam_inf,diam_rot,0,
                   "State is already singular; this is not permission to execute a possibly unsafe action")
