"""Native-typed action chart authorization for an explicitly verified Panda EE controller.

A controller's rotation action is in a Euclidean UNIT BALL, not merely
the 3D per-coordinate [-1,1] cube. Both chart and observer compare in
float64 before stepping native PhysX. Optional exact radial projection is
reported NON_EXACT and is permitted ONLY when all intended commanded-target
pose errors, recomputed across the COMPLETE trusted history set, fit
predeclared budgets. Otherwise return no action.

An original source-frozen StackCube fault study found that float32
norm 1.0000009536743164 and float64 norm 1.0000010144344997 straddle
the history observer's 1+1e-6 gate. See strict budget original seed 370029.
This code is a prospective corrective PROTOTYPE; it was NOT applied to
that historical 64-state study and does NOT establish hardware safety.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import TargetPose


@dataclass(frozen=True)
class NativeActionAuthorization:
    accepted: bool
    reason: str
    normalized_command: Optional[Tuple[float, ...]]
    is_nonexact_projection: bool
    worst_commanded_position_error_m: float
    worst_commanded_orientation_error_rad: float
    confidence_scope: str = (
        "Conditioned on an independently complete/fresh target-history set, "
        "verified root-translation/left-root-rotation chart, and the intended "
        "commanded target. NOT actuator/contact/collision safety."
    )


def authorize_native_cartesian_ee(
    proposed_native_action,
    desired_commanded_target: TargetPose,
    possible_previous_target_poses,
    *,
    low_xyz,
    high_xyz,
    normalized_euler_rot_scale,
    max_position_inf_m: float,
    max_orientation_geodesic_rad: float,
    complete_trusted_histories: bool,
    verified_root_left_chart: bool,
    numerical_guard: float = 1e-8,
) -> NativeActionAuthorization:
    """Check native unit-ball legality, or conditionally project with audit.

    The actual official target update is:
      p_next = p_previous + low + (clip(u_xyz,-1,1)+1)*(high-low)/2
      R_next = Rotation.from_euler('XYZ', clipped_rot*rot_scale) * R_previous.
    Native rotations are normalized radially for ||u_rot||_2 > 1.
    This model requires explicit controller and shape attestation.
    """
    def refused(reason, p=float("inf"), r=float("inf"), nonexact=False):
        return NativeActionAuthorization(False,reason,None,nonexact,p,r)
    if not complete_trusted_histories:
        return refused("UNATTESTED_OR_INCOMPLETE_CONTROLLER_HISTORY")
    if not verified_root_left_chart:
        return refused("UNVERIFIED_ACTION_CHART")
    if not isinstance(desired_commanded_target, TargetPose):
        raise TypeError("Desired target must be TargetPose")
    if not isinstance(possible_previous_target_poses,(tuple,list)):
        raise TypeError("Previous target histories must be explicit")
    if len(possible_previous_target_poses) not in (1,2):
        return refused("UNSUPPORTED_HISTORY_CARDINALITY")
    if not all(isinstance(p,TargetPose) for p in possible_previous_target_poses):
        raise TypeError("Every hypothesized previous target must be TargetPose")
    a=np.asarray(proposed_native_action,dtype=np.float64)
    low=np.broadcast_to(np.asarray(low_xyz,dtype=np.float64),(3,))
    high=np.broadcast_to(np.asarray(high_xyz,dtype=np.float64),(3,))
    scale=np.broadcast_to(np.asarray(normalized_euler_rot_scale,dtype=np.float64),(3,))
    if a.shape!=(6,) or not np.isfinite(a).all():
        return refused("NONFINITE_OR_WRONG_DIMENSION_NATIVE_ACTION")
    if (not np.isfinite(low).all() or not np.isfinite(high).all()
        or not np.all(high>low) or not np.isfinite(scale).all()
        or np.any(scale==0)):
        return refused("UNDEFINED_OR_NONFINITE_CONTROLLER_SCALES")
    if (not np.isfinite([max_position_inf_m,max_orientation_geodesic_rad,numerical_guard]).all()
        or min(max_position_inf_m,max_orientation_geodesic_rad)<0
        or numerical_guard<=0):
        return refused("INVALID_DECLARED_ERROR_BUDGET")
    # Source adapter may have used a positive componentwise tolerance.
    # We never silently accept it as within the actual radial unit ball.
    u_pos=np.clip(a[:3],-1.0,1.0)
    radial=float(np.linalg.norm(a[3:]))
    u_rot=a[3:].copy() if radial<=1 else a[3:]/radial
    nonexact=(np.any(u_pos!=a[:3]) or radial>1)
    # Normalize for the actual float32 dispatch representation, THEN repeat
    # the float64 controller/observer guard; do not rely on float32 norms.
    u=np.r_[u_pos,u_rot].astype(np.float32)
    realized=u.astype(np.float64)
    if np.linalg.norm(realized[3:])>1+numerical_guard:
        # Roundoff at float32 transport boundary: project inward at the
        # actual representable precision, not a different source float64.
        # A mathematical float64 radius-one vector can round OUTSIDE
        # the legal SO3 unit ball again when transmitted as float32.
        # Move at least eight float32 ULPs into the interior, then
        # recompute every resulting native target pose from final bytes.
        inward=1.0-8.0*np.finfo(np.float32).eps
        corrected=(realized[3:]/np.linalg.norm(realized[3:]))*inward
        u[3:]=corrected.astype(np.float32)
        realized=u.astype(np.float64)
        nonexact=True
        if np.linalg.norm(realized[3:])>1+numerical_guard:
            return refused("ROTATION_STILL_OUTSIDE_NATIVE_UNIT_BALL",nonexact=True)
    physical_pos=low+(realized[:3]+1)*(high-low)/2
    physical_euler=realized[3:]*scale
    delta_R=Rotation.from_euler("XYZ",physical_euler)
    target_R=Rotation.from_quat(desired_commanded_target.quaternion_xyzw)
    target_p=np.asarray(desired_commanded_target.position,dtype=np.float64)
    max_p=0.
    max_r=0.
    for old in possible_previous_target_poses:
        p=np.asarray(old.position,dtype=np.float64)+physical_pos
        R=delta_R*Rotation.from_quat(old.quaternion_xyzw)
        max_p=max(max_p,float(np.max(np.abs(p-target_p))))
        max_r=max(max_r,float((target_R.inv()*R).magnitude()))
    if max_p+numerical_guard>max_position_inf_m:
        return refused("UNBOUNDED_COMMANDED_POSITION_ERROR",max_p,max_r,nonexact)
    if max_r+numerical_guard>max_orientation_geodesic_rad:
        return refused("UNBOUNDED_COMMANDED_ORIENTATION_ERROR",max_p,max_r,nonexact)
    if np.max(np.abs(realized[:3]))>1+numerical_guard:
        return refused("NATIVE_TRANSLATION_BOX_VIOLATED",max_p,max_r,nonexact)
    return NativeActionAuthorization(
        True,"CONDITIONALLY_AUTHORIZED_NATIVE_SETPOINT",
        tuple(float(t) for t in u),bool(nonexact),max_p,max_r
    )
