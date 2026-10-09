"""Conservative bounded-action certificate for 1–16 uncertain controller targets.

One native command, conditional on *all* explicitly tracked target-memory
hypotheses. Position uses an exact axis-aligned Chebyshev center; SO(3) uses
a finite family of pairwise geodesic midpoints and returns a certified
upper bound after checking the actual representable left-root Euler command.

SO(3) candidate search is CONSERVATIVE, not a proof of globally optimal
multi-rotation minimax action. A refusal need not imply impossibility.
The safety scope is commanded setpoints under a verified controller chart,
NOT physical trajectories, IK, collisions, forces or hardware.
"""
from __future__ import annotations
import warnings
from itertools import combinations
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import TargetPose
from research.two_history_se3_robust import (
    CommonCommand, Reason, common_two_history_command,
)

MAX_HYPOTHESES=16


def common_multi_history_command(
    histories: tuple[TargetPose, ...], desired: TargetPose, *,
    pos_lower, pos_upper, rot_lower, position_budget_m: float,
    rotation_budget_rad: float, hypotheses_complete: bool,
    trusted_provenance: bool, age_steps: int, max_age_steps: int,
    root_translation_root_left_rotation_verified: bool,
    numeric_guard: float=1e-9,
) -> CommonCommand:
    kwargs=dict(pos_lower=pos_lower,pos_upper=pos_upper,rot_lower=rot_lower,
                position_budget_m=position_budget_m,
                rotation_budget_rad=rotation_budget_rad,
                hypotheses_complete=hypotheses_complete,
                trusted_provenance=trusted_provenance,
                age_steps=age_steps,max_age_steps=max_age_steps,
                root_translation_root_left_rotation_verified=
                    root_translation_root_left_rotation_verified,
                numeric_guard=numeric_guard)
    if not isinstance(histories,tuple) or not (
            1<=len(histories)<=MAX_HYPOTHESES
    ) or any(not isinstance(p,TargetPose) for p in histories):
        raise ValueError("Explicit 1–16 controller target hypotheses required")
    if not isinstance(desired,TargetPose):
        raise TypeError("Target setpoint must be TargetPose")
    if len(histories)==2:
        return common_two_history_command(histories,desired,**kwargs)
    if type(age_steps) is not int or type(max_age_steps) is not int or min(age_steps,max_age_steps)<0:
        raise ValueError("Invalid age")
    if (not np.isfinite(position_budget_m) or
        not np.isfinite(rotation_budget_rad) or
        min(position_budget_m,rotation_budget_rad)<0 or
        not np.isfinite(numeric_guard) or numeric_guard<=0):
        raise ValueError("Invalid finite budgets or numerical guard")
    low=np.broadcast_to(np.asarray(pos_lower,dtype=float),(3,)).copy()
    high=np.broadcast_to(np.asarray(pos_upper,dtype=float),(3,)).copy()
    scale=np.broadcast_to(np.asarray(rot_lower,dtype=float),(3,)).copy()
    if (not np.isfinite(low).all() or not np.isfinite(high).all()
        or not np.isfinite(scale).all() or np.any(low>=high)
        or np.any(np.abs(scale)<1e-12)):
        raise ValueError("Untrusted native action chart")
    positions=np.asarray([p.position for p in histories],dtype=float)
    goal=np.asarray(desired.position,dtype=float)
    if not np.isfinite(positions).all() or not np.isfinite(goal).all():
        raise ValueError("Nonfinite target positions")
    center=(np.min(positions,axis=0)+np.max(positions,axis=0))/2
    wanted=goal-center
    translation=np.clip(wanted,low,high)
    excess=np.abs(wanted-translation)
    pos_error=float(np.max(np.abs(positions+translation-goal)))
    if not np.isfinite(pos_error):
        raise ValueError("Position overflow")
    old_rot=[Rotation.from_quat(h.quaternion_xyzw) for h in histories]
    goal_rot=Rotation.from_quat(desired.quaternion_xyzw)
    candidates=list(old_rot)
    for a,b in combinations(old_rot,2):
        rel=a.inv()*b
        candidates.append(a*Rotation.from_rotvec(0.5*rel.as_rotvec()))
    quat=np.asarray([r.as_quat() for r in old_rot])
    quat=np.where((quat@quat[0])[:,None]<0,-quat,quat)
    qmean=quat.sum(axis=0)
    if np.linalg.norm(qmean)>1e-12:
        candidates.append(Rotation.from_quat(qmean/np.linalg.norm(qmean)))
    best=None
    for midpoint in candidates:
        requested=goal_rot*midpoint.inv()
        with warnings.catch_warnings():
            warnings.simplefilter("error",UserWarning)
            try:
                euler=requested.as_euler("XYZ")
            except UserWarning:
                continue
        native=euler/scale
        if not np.isfinite(native).all() or np.linalg.norm(native)>=1-numeric_guard:
            continue
        actual=Rotation.from_euler("XYZ",euler)
        if (actual.inv()*requested).magnitude()>1e-8:
            continue
        # Verify every actual controller equation AFTER representability check.
        worst=max(float(((actual*r).inv()*goal_rot).magnitude())
                  for r in old_rot)
        if not np.isfinite(worst):
            continue
        if best is None or worst<best[0]:
            best=(worst,native)
    if not hypotheses_complete:
        reason=Reason.REFUSE_INCOMPLETE_HYPOTHESES
    elif not trusted_provenance or age_steps>max_age_steps:
        reason=Reason.REFUSE_STALE_OR_UNTRUSTED
    elif not root_translation_root_left_rotation_verified:
        reason=Reason.REFUSE_UNVERIFIED_CONTROLLER
    elif best is None:
        reason=Reason.REFUSE_UNREPRESENTABLE_ROTATION
    elif pos_error+numeric_guard>position_budget_m:
        reason=Reason.REFUSE_POSITION_BUDGET
    elif best[0]+numeric_guard>rotation_budget_rad:
        reason=Reason.REFUSE_ROTATION_BUDGET
    else:
        reason=Reason.AUTHORIZE_BOUNDED_SETPOINT
    norm_pos=2*(translation-low)/(high-low)-1
    norm_rot=best[1] if best else np.zeros(3)
    output=np.r_[norm_pos,norm_rot]
    if reason is Reason.AUTHORIZE_BOUNDED_SETPOINT:
        if not np.isfinite(output).all() or np.max(np.abs(output[:3]))>1+1e-7 or np.linalg.norm(output[3:])>=1:
            raise RuntimeError("Approved invalid native controller command")
    return CommonCommand(
        reason=reason,
        normalized_6d=tuple(float(x) for x in output)
            if reason is Reason.AUTHORIZE_BOUNDED_SETPOINT else None,
        worst_position_inf_m=pos_error,
        worst_orientation_geodesic_rad=(best[0] if best else float("inf")),
        hypotheses=len(histories),
        position_saturation_excess_m=tuple(float(x) for x in excess),
        explanation="Conservative actual-setpoint bound over all enumerated histories; "
                    "candidate SO(3) search is not globally optimal; "
                    "no collision, tracking or external memory authenticity guarantee",
    )
