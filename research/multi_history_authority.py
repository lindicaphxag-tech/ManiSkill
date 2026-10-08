"""Finite-set action authority under MULTIPLE uncertain controller command histories.

This extends a known two-history SE(3) controller-target certificate, but
must NOT be confused with an optimal multi-rotation Chebyshev solver. The
position optimizer IS exact (per-axis box-constrained L-infinity radius).
For SO(3), we use a disclosed finite candidate covering-center set and
evaluate *every* credible history. Pairwise SO(3) diameter/2 gives a
provable lower bound, and the selected feasible finite candidate supplies
an actual upper bound. An untrusted or incomplete belief MUST NOT authorize.

This guarantees a commanded SETPOINT discrepancy under an exact documented
root-frame position + left-acting spatial rotation controller chart. No
claim is made about physical trajectory/force/collision safety, validity
of supplied histories, confidence intervals, or pretrained model reward.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
import warnings

import numpy as np
from scipy.spatial.transform import Rotation

from research.action_abi_history_observer import TargetPose


class Authority(str, Enum):
    CERTIFIED_FOR_ALL_HISTORIES = "CERTIFIED_FOR_ALL_HISTORIES"
    REFUSE_INCOMPLETE_HISTORIES = "REFUSE_INCOMPLETE_HISTORIES"
    REFUSE_UNTRUSTED_OR_STALE = "REFUSE_UNTRUSTED_OR_STALE"
    REFUSE_UNVERIFIED_CHART = "REFUSE_UNVERIFIED_CHART"
    REFUSE_NATIVE_ROTATION = "REFUSE_NATIVE_ROTATION"
    REFUSE_POSITION_BOUND = "REFUSE_POSITION_BOUND"
    REFUSE_ROTATION_BOUND = "REFUSE_ROTATION_BOUND"


@dataclass(frozen=True)
class MultiHistoryCertificate:
    authority: Authority
    command_normalized_6d: tuple[float, ...] | None
    credible_history_count: int
    exact_position_radius_m: float
    verified_rotation_upper_bound_rad: float
    universal_rotation_lower_bound_rad: float
    rotation_approximation_gap_upper_bound_rad: float
    evaluated_orientation_centers: int
    representable_orientation_centers: int
    declared_history_complete: bool
    note: str

    @property
    def authorized(self):
        return self.authority is Authority.CERTIFIED_FOR_ALL_HISTORIES


def _rotation_candidates(rotations: list[Rotation]) -> list[Rotation]:
    """Finite, deterministic covering-center witnesses, never global SO3 claim."""
    from itertools import combinations
    candidates = list(rotations)
    for i, j in combinations(range(len(rotations)), 2):
        a, b = rotations[i], rotations[j]
        candidates.append(a * Rotation.from_rotvec((a.inv() * b).as_rotvec() / 2.))
    # Mean is just another candidate, not a globally optimal rotation center.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        try:
            candidates.append(Rotation.concatenate(rotations).mean())
        except (ValueError, RuntimeError):
            pass
    return candidates


def certify_multi_history_action(
    histories: tuple[TargetPose, ...],
    desired: TargetPose,
    *,
    pos_lower,
    pos_upper,
    rot_lower,
    position_budget_m: float,
    rotation_budget_rad: float,
    histories_complete: bool,
    trusted_history: bool,
    age_steps: int,
    max_age_steps: int,
    root_left_rotation_verified: bool,
    numeric_guard: float = 1e-8,
) -> MultiHistoryCertificate:
    if not isinstance(histories, tuple) or not 2 <= len(histories) <= 256:
        raise ValueError("Provide every one of 2..256 explicit possible previous targets")
    if not all(isinstance(h, TargetPose) for h in histories) or not isinstance(desired, TargetPose):
        raise TypeError("Only explicit TargetPose physical states are accepted")
    if type(age_steps) is not int or type(max_age_steps) is not int or min(age_steps,max_age_steps)<0:
        raise ValueError("A genuine nonnegative history age contract is required")
    low=np.broadcast_to(np.asarray(pos_lower,dtype=np.float64),(3,)).copy()
    high=np.broadcast_to(np.asarray(pos_upper,dtype=np.float64),(3,)).copy()
    scale=np.broadcast_to(np.asarray(rot_lower,dtype=np.float64),(3,)).copy()
    vals=(position_budget_m,rotation_budget_rad,numeric_guard)
    if (not np.isfinite(low).all() or not np.isfinite(high).all()
            or not np.isfinite(scale).all()
            or not all(isfinite(float(x)) for x in vals)
            or np.any(low>=high) or np.any(np.abs(scale)<=1e-12)
            or position_budget_m<0 or rotation_budget_rad<0 or numeric_guard<=0):
        raise ValueError("Nonfinite, inverted or unsupported native bounds/budget")
    xyz=np.asarray([h.position for h in histories],dtype=float)
    dest=np.asarray(desired.position,dtype=float)
    if xyz.shape!=(len(histories),3) or not np.isfinite(xyz).all() or not np.isfinite(dest).all():
        raise ValueError("Nonfinite or inconsistent 3-D target")
    # Exact coordinate-wise Chebyshev center for any FINITE history set.
    # Each coordinate's maximum |prior + delta - desired| is minimized by
    # clamping the midpoint of its extremal prior positions to legal DELTA.
    midpoint=(np.min(xyz,axis=0)+np.max(xyz,axis=0))/2
    translated=np.clip(dest-midpoint,low,high)
    pos_err=float(np.max(np.abs(xyz+translated-dest)))
    if not np.isfinite(pos_err):
        raise ValueError("Overflow in all-history worst-case position")

    rotations=[Rotation.from_quat(h.quaternion_xyzw) for h in histories]
    target=Rotation.from_quat(desired.quaternion_xyzw)
    # Fundamental SO(3) geodesic triangle-inequality lower bound.
    diameter=0.
    for i in range(len(rotations)):
        for j in range(i+1,len(rotations)):
            diameter=max(diameter,float((rotations[i].inv()*rotations[j]).magnitude()))
    lower=diameter/2
    all_centers=_rotation_candidates(rotations)
    available=[]
    for k,center in enumerate(all_centers):
        commanded=target*center.inv()
        with warnings.catch_warnings():
            warnings.simplefilter("error",UserWarning)
            try:
                angles=commanded.as_euler("XYZ")
            except UserWarning:
                continue
        native=angles/scale
        if not np.isfinite(native).all() or float(np.linalg.norm(native))>=1.-numeric_guard:
            continue
        actual=Rotation.from_euler("XYZ", angles)
        if (actual.inv()*commanded).magnitude()>1e-8:
            continue
        worst=max(float((target.inv()*actual*r).magnitude()) for r in rotations)
        available.append((worst,k,tuple(float(x) for x in native)))
    if available:
        worst,_,native_rot=min(available, key=lambda t:(t[0],t[1]))
        if worst+2e-8<lower:
            raise RuntimeError("SO(3) lower-bound violated; chart or rotation convention bug")
    else:
        worst=float("inf")
        native_rot=None
    if not histories_complete:
        why=Authority.REFUSE_INCOMPLETE_HISTORIES
    elif not trusted_history or age_steps>max_age_steps:
        why=Authority.REFUSE_UNTRUSTED_OR_STALE
    elif not root_left_rotation_verified:
        why=Authority.REFUSE_UNVERIFIED_CHART
    elif native_rot is None:
        why=Authority.REFUSE_NATIVE_ROTATION
    elif pos_err+numeric_guard>position_budget_m:
        why=Authority.REFUSE_POSITION_BOUND
    elif worst+numeric_guard>rotation_budget_rad:
        why=Authority.REFUSE_ROTATION_BOUND
    else:
        why=Authority.CERTIFIED_FOR_ALL_HISTORIES
    normalized_position=2*(translated-low)/(high-low)-1
    output=tuple(float(x) for x in normalized_position)+native_rot if why is Authority.CERTIFIED_FOR_ALL_HISTORIES else None
    if output is not None:
        assert len(output)==6 and max(abs(x) for x in output[:3])<=1+1e-12
        assert np.linalg.norm(output[3:])<1
    return MultiHistoryCertificate(
        authority=why,command_normalized_6d=output,
        credible_history_count=len(histories),
        exact_position_radius_m=pos_err,
        verified_rotation_upper_bound_rad=worst,
        universal_rotation_lower_bound_rad=lower,
        rotation_approximation_gap_upper_bound_rad=max(0.,worst-lower),
        evaluated_orientation_centers=len(all_centers),
        representable_orientation_centers=len(available),
        declared_history_complete=histories_complete,
        note=("Setpoint-only verified finite-set upper bound; unknown hidden "
              "histories or undocumented controller updates require refusal. "
              "SO3 finite candidates need not attain optimal K>=3 covering center."),
    )
