"""Common bounded command for TWO possible Panda controller target poses.

Conditional SETPOINT certificate, not robot trajectory/contact safety.
Explicit hypothesis completeness and trusted provenance are caller duties.
The two-state geodesic/Chebyshev midpoint is established geometry.

Root-translation and root-aligned-body rotation ONLY; refuses saturation
of requested native rotation instead of falsely certifying clipped output.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import warnings
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import TargetPose


class Reason(str, Enum):
    AUTHORIZE_BOUNDED_SETPOINT = "AUTHORIZE_BOUNDED_SETPOINT"
    REFUSE_INCOMPLETE_HYPOTHESES = "REFUSE_INCOMPLETE_HYPOTHESES"
    REFUSE_STALE_OR_UNTRUSTED = "REFUSE_STALE_OR_UNTRUSTED"
    REFUSE_UNVERIFIED_CONTROLLER = "REFUSE_UNVERIFIED_CONTROLLER"
    REFUSE_UNREPRESENTABLE_ROTATION = "REFUSE_UNREPRESENTABLE_ROTATION"
    REFUSE_POSITION_BUDGET = "REFUSE_POSITION_BUDGET"
    REFUSE_ROTATION_BUDGET = "REFUSE_ROTATION_BUDGET"


@dataclass(frozen=True)
class CommonCommand:
    reason: Reason
    normalized_6d: tuple[float,...] | None
    worst_position_inf_m: float
    worst_orientation_geodesic_rad: float
    hypotheses: int
    position_saturation_excess_m: tuple[float,...]
    explanation: str

    @property
    def authorized(self):
        return self.reason is Reason.AUTHORIZE_BOUNDED_SETPOINT


def _invalid_or_nan(*xs):
    return any(not np.all(np.isfinite(np.asarray(x,dtype=float))) for x in xs)


def common_two_history_command(
    histories: tuple[TargetPose,...],
    desired: TargetPose,
    *,
    pos_lower,
    pos_upper,
    rot_lower,
    position_budget_m: float,
    rotation_budget_rad: float,
    hypotheses_complete: bool,
    trusted_provenance: bool,
    age_steps: int,
    max_age_steps: int,
    root_translation_root_left_rotation_verified: bool,
    numeric_guard: float=1e-9,
):
    """Conditional minimax in (position infinity-norm, SO(3) geodesic).

    A common native command works for two candidate prior targets. Translation
    is a clipped box-Chebyshev-center increment. Orientation chooses the
    geodesic midpoint of the *two prior rotations*, then left-multiplies
    both by the SAME commanded rotation taking the midpoint to desired.
    Under the verified controller update, each orientation gets exactly
    one half of the separation as SO(3) geodesic residual.

    This is NOT an unconditional observation-only estimate: hypothesis set
    completeness, controller semantics and trustworthy reset/ACK evidence
    must be independently verified. A caller-supplied boolean cannot prove
    cryptographic authenticity.
    """
    if not isinstance(desired,TargetPose):
        raise TypeError("Desired setpoint must be TargetPose")
    if len(histories)!=2 or any(not isinstance(x,TargetPose) for x in histories):
        raise ValueError("This verifier supports exactly two explicit TargetPose hypotheses")
    for name,x in (("age",age_steps),("max_age",max_age_steps)):
        if type(x) is not int or x<0:
            raise ValueError(f"{name} must be nonnegative integer")
    low=np.broadcast_to(np.asarray(pos_lower,dtype=float),(3,)).copy()
    high=np.broadcast_to(np.asarray(pos_upper,dtype=float),(3,)).copy()
    scale=np.broadcast_to(np.asarray(rot_lower,dtype=float),(3,)).copy()
    if _invalid_or_nan(low,high,scale):
        raise ValueError("Invalid native controller scale")
    if np.any(low>=high) or np.any(np.abs(scale)<1e-12):
        raise ValueError("Invalid controller native action bounds")
    if _invalid_or_nan(position_budget_m,rotation_budget_rad,numeric_guard):
        raise ValueError("Invalid finite required error budgets")
    if min(position_budget_m,rotation_budget_rad)<0 or numeric_guard<=0:
        raise ValueError("Budgets nonnegative and numerical guard positive")

    prev=np.asarray([p.position for p in histories],dtype=float)
    target=np.asarray(desired.position,dtype=float)
    center=(prev[0]+prev[1])/2
    wanted=target-center
    physical=np.clip(wanted,low,high)
    excess=np.abs(wanted-physical)
    endpoints=np.max(np.abs(prev+physical-target),axis=1)
    error_position=float(np.max(endpoints))
    if not np.isfinite(error_position):
        raise ValueError("Numeric overflow in robust position")
    if len(histories)!=2:
        raise AssertionError("Incomplete candidate histories")

    rot_a=Rotation.from_quat(histories[0].quaternion_xyzw)
    rot_b=Rotation.from_quat(histories[1].quaternion_xyzw)
    rel=rot_a.inv()*rot_b
    separation=float(rel.magnitude())
    midpoint=rot_a*Rotation.from_rotvec(rel.as_rotvec()/2.0)
    rot_target=Rotation.from_quat(desired.quaternion_xyzw)
    commanded_rotation=rot_target*midpoint.inv()
    with warnings.catch_warnings():
        warnings.simplefilter("error",UserWarning)
        try:
            angles=commanded_rotation.as_euler("XYZ")
        except UserWarning:
            angles=np.array([np.nan]*3)
    native_rotation=angles/scale
    rotation_representable=(
        np.all(np.isfinite(native_rotation))
        and float(np.linalg.norm(native_rotation)) <= 1.0-numeric_guard
    )
    if rotation_representable:
        actual_commanded=Rotation.from_euler("XYZ",angles)
        # Round-trip exact root-left controller equation check.
        if (actual_commanded.inv()*commanded_rotation).magnitude()>1e-8:
            rotation_representable=False
    error_rotation=separation/2.0

    if not hypotheses_complete:
        reason=Reason.REFUSE_INCOMPLETE_HYPOTHESES
    elif not trusted_provenance or age_steps>max_age_steps:
        reason=Reason.REFUSE_STALE_OR_UNTRUSTED
    elif not root_translation_root_left_rotation_verified:
        reason=Reason.REFUSE_UNVERIFIED_CONTROLLER
    elif not rotation_representable:
        reason=Reason.REFUSE_UNREPRESENTABLE_ROTATION
    elif error_position+numeric_guard>position_budget_m:
        reason=Reason.REFUSE_POSITION_BUDGET
    elif error_rotation+numeric_guard>rotation_budget_rad:
        reason=Reason.REFUSE_ROTATION_BUDGET
    else:
        reason=Reason.AUTHORIZE_BOUNDED_SETPOINT
    normalized_position=2*(physical-low)/(high-low)-1
    native=np.r_[normalized_position,native_rotation]
    if reason is Reason.AUTHORIZE_BOUNDED_SETPOINT:
        if not (np.all(np.abs(native[:3])<=1.0000001)
                and np.linalg.norm(native[3:])<1):
            raise RuntimeError("Internal authorization disagrees with bounds")
    return CommonCommand(
        reason=reason,
        normalized_6d=tuple(float(x) for x in native) if reason is
        Reason.AUTHORIZE_BOUNDED_SETPOINT else None,
        worst_position_inf_m=error_position,
        worst_orientation_geodesic_rad=error_rotation,
        hypotheses=2,
        position_saturation_excess_m=tuple(float(x) for x in excess),
        explanation=(
            "Verified bounded commanded-target setpoint only; "
            "no collision/trajectory tracking, hardware safety or independent "
            "proof of memory-hypothesis provenance"
        ),
    )
