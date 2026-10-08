"""Executable one-step target-memory feasibility witness for OSC-like pose actions.

This is a numerically checked adapter with a constrained Euclidean
projection, NOT a formally verified safety certificate. No policy training.
Source provenance: learnable-policy experiments in this repository.
"""
from dataclasses import dataclass
from enum import Enum
import warnings

import numpy as np
from scipy.spatial.transform import Rotation


class TransportDecision(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    REFUSED = "refused"


@dataclass(frozen=True)
class FeasibilityWitness:
    decision: TransportDecision
    reason: str
    native_action: tuple[float, ...] | None
    required_native_amplitude: float | None
    position_goal_residual_m: float | None
    orientation_goal_residual_rad: float | None

    @property
    def executable(self) -> bool:
        return self.native_action is not None


def _refuse(reason: str, amp=None) -> FeasibilityWitness:
    return FeasibilityWitness(
        decision=TransportDecision.REFUSED,
        reason=reason,
        native_action=None,
        required_native_amplitude=amp,
        position_goal_residual_m=None,
        orientation_goal_residual_rad=None,
    )


def _pose(p, r, name):
    pos=np.asarray(p,dtype=float)
    rot=np.asarray(r,dtype=float)
    if pos.shape!=(3,) or rot.shape!=(3,3):
        raise ValueError(f"{name} pose has incompatible dimensions")
    if not np.all(np.isfinite(pos)) or not np.all(np.isfinite(rot)):
        raise ValueError(f"{name} pose has nonfinite entries")
    if np.max(np.abs(rot.T @ rot-np.eye(3)))>1e-6 or abs(np.linalg.det(rot)-1.0)>1e-6:
        raise ValueError(f"{name} orientation is not a rotation matrix")
    return pos,rot


def compile_target_memory_action(
    previous_target_position,
    previous_target_rotation,
    desired_position,
    desired_rotation,
    *,
    pos_lower=-0.1,
    pos_upper=0.1,
    rotation_native_scale=-0.1,
    mode="strict",
    feasibility_tolerance=1e-7,
):
    """Translate absolute desired pose into bounded target-relative 6D native input.

    Rotation convention is left-multiplied XYZ Euler delta:
    R_desired = R_delta @ R_previous. This matches the tested
    ManiSkill root_translation:root_aligned_body_rotation controller.

    mode='strict': refuse any unrepresentable one-step desired pose.
    mode='project': box-clip translation and ball-project the normalized
    rotation vector. For project mode, residuals quantify the *target
    displacement implied by the projected native command*, not the
    actual next simulated achieved robot pose.
    """
    if mode not in ("strict","project"):
        return _refuse("mode must be strict or project")
    try:
        previous_p,previous_R=_pose(
            previous_target_position,previous_target_rotation,"previous")
        desired_p,desired_R=_pose(
            desired_position,desired_rotation,"desired")
        lower=np.broadcast_to(np.asarray(pos_lower,dtype=float),(3,))
        upper=np.broadcast_to(np.asarray(pos_upper,dtype=float),(3,))
        scale=float(rotation_native_scale)
        if (
            not np.all(np.isfinite(lower))
            or not np.all(np.isfinite(upper))
            or not np.all(upper>lower)
            or not np.isfinite(scale)
            or abs(scale)<1e-10
        ):
            return _refuse("invalid action limits or rotation native scale")
        req_xyz=2*(desired_p-previous_p-lower)/(upper-lower)-1
        with warnings.catch_warnings():
            warnings.filterwarnings("error", category=UserWarning)
            req_euler=Rotation.from_matrix(desired_R @ previous_R.T).as_euler("XYZ")
        req_rot=req_euler/scale
        if not np.all(np.isfinite(req_xyz)) or not np.all(np.isfinite(req_rot)):
            return _refuse("nonfinite inverse native command")
        amplitude=float(max(np.max(np.abs(req_xyz)),np.linalg.norm(req_rot)))
        is_feasible=amplitude<=1.0+feasibility_tolerance
        if not is_feasible and mode=="strict":
            return _refuse("requested target exceeds one-step native controller set",amplitude)

        if is_feasible:
            # Near-floating-point edge (1+eps) may still be clipped by
            # the downstream controller; project to legal set here and
            # only label EXACT when physical residual is negligible.
            native_xyz=np.clip(req_xyz,-1.0,1.0)
            native_rot=req_rot.copy()
            n=float(np.linalg.norm(native_rot))
            if n>1: native_rot=native_rot/n
        else:
            native_xyz=np.clip(req_xyz,-1.0,1.0)
            native_rot=req_rot.copy()
            n=float(np.linalg.norm(native_rot))
            if n>1: native_rot=native_rot/n

        physical_pos=(native_xyz+1)*(upper-lower)/2+lower
        physical_rot=native_rot*scale
        implied_p=previous_p+physical_pos
        implied_R=Rotation.from_euler("XYZ",physical_rot).as_matrix()@previous_R
        pos_res=float(np.linalg.norm(desired_p-implied_p))
        ori_res=float(Rotation.from_matrix(desired_R@implied_R.T).magnitude())
        exact=(pos_res<=1e-6 and ori_res<=1e-6)
        decision=TransportDecision.EXACT if exact else TransportDecision.APPROXIMATE
        # A strict promise never silently degrades into approximation.
        if mode=="strict" and not exact:
            return _refuse("numerical/native-limit inconsistency in strict mode",amplitude)
        return FeasibilityWitness(
            decision=decision,
            reason="goal represented within native action set" if exact else "bounded nonexact projection",
            native_action=tuple(map(float,np.r_[native_xyz,native_rot])),
            required_native_amplitude=amplitude,
            position_goal_residual_m=pos_res,
            orientation_goal_residual_rad=ori_res,
        )
    except (ValueError,TypeError,FloatingPointError,UserWarning) as exc:
        return _refuse(f"invalid pose/action contract: {exc}")
