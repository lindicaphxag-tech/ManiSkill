"""Finite-step executable witness for desired-goal OSC action feasibility.

This module has no learned weights and makes NO hardware-safety claim.
It is a deliberately restricted physical action contract:
  root-frame translation, root-aligned body rotation, fixed-impedance
  controller, no interpolation, native position box and Euler norm ball.

The returned residual is the *geometric target* residual after applying
the attainable native command, not a bound on the next physical state.
"""
from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.spatial.transform import Rotation


class ExecutionStatus(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    REFUSED = "refused"


@dataclass(frozen=True)
class PoseTransportWitness:
    status: ExecutionStatus
    native_action: tuple[float, ...] | None
    required_native_amplitude: float
    position_goal_residual_m: float
    orientation_goal_residual_rad: float
    reason: str


def _vec(value, size, name):
    x=np.asarray(value,dtype=float)
    if x.shape!=(size,) or not np.all(np.isfinite(x)):
        raise ValueError(f"{name} must have {size} finite coordinates")
    return x


def _rot(value, name):
    x=np.asarray(value,dtype=float)
    if x.shape!=(3,3) or not np.all(np.isfinite(x)):
        raise ValueError(f"{name} must be a finite 3x3 matrix")
    if np.linalg.det(x)<0.0 or np.linalg.norm(x.T @ x-np.eye(3))>1e-5:
        raise ValueError(f"{name} must lie in SO(3)")
    return Rotation.from_matrix(x)


def compile_target_goal(
    desired_position,
    desired_orientation_matrix,
    previous_target_position,
    previous_target_orientation_matrix,
    *,
    pos_lower: float,
    pos_upper: float,
    rot_lower: float,
    allow_approximation: bool=False,
    tolerance: float=1e-7,
) -> PoseTransportWitness:
    """Compile physical desired target into a previous-target-relative command.

    Position convention: normalized u in [-1,1] maps linearly into
    [pos_lower,pos_upper]. Orientation convention: normalized XYZ Euler
    vector has Euclidean norm <=1, multiplied by rot_lower (usually
    negative), then left-composed with previous target orientation.

    EXACT only means pose-goal reconstruction within the stated tolerance.
    APPPROXIMATE is a *measured* nonzero one-step target residual.
    """
    goal_p=_vec(desired_position,3,"desired_position")
    old_p=_vec(previous_target_position,3,"previous_target_position")
    goal_r=_rot(desired_orientation_matrix,"desired_orientation_matrix")
    old_r=_rot(previous_target_orientation_matrix,"previous_target_orientation_matrix")
    bounds=np.asarray([pos_lower,pos_upper,rot_lower,tolerance],dtype=float)
    if not np.all(np.isfinite(bounds)) or pos_upper<=pos_lower or abs(rot_lower)<1e-12 or tolerance<=0:
        raise ValueError("unsupported native action bounds")
    delta_pos=goal_p-old_p
    # ManiSkill root-aligned-body rotation: R_next = R_delta @ R_previous.
    delta_rot=goal_r * old_r.inv()
    with np.errstate(invalid="raise",divide="raise"):
        required_euler=delta_rot.as_euler("XYZ",degrees=False)
    normalized_position=2*(delta_pos-pos_lower)/(pos_upper-pos_lower)-1
    normalized_rotation=required_euler/rot_lower
    required_amp=max(float(np.max(np.abs(normalized_position))),
                     float(np.linalg.norm(normalized_rotation)))
    projected_position=np.clip(normalized_position,-1.0,1.0)
    rotation_size=float(np.linalg.norm(normalized_rotation))
    projected_rotation=normalized_rotation / max(1.0,rotation_size)

    actual_delta=pos_lower+(projected_position+1)*(pos_upper-pos_lower)/2
    actual_position=old_p+actual_delta
    actual_orientation=Rotation.from_euler("XYZ",projected_rotation*rot_lower)*old_r
    distance_p=float(np.linalg.norm(actual_position-goal_p))
    distance_r=float((actual_orientation.inv()*goal_r).magnitude())
    exact=(distance_p<=tolerance and distance_r<=tolerance and required_amp<=1+1e-8)
    if exact:
        native=np.r_[normalized_position,normalized_rotation]
        status=ExecutionStatus.EXACT
        reason="native controller action exactly represents desired pose target"
    elif allow_approximation:
        native=np.r_[projected_position,projected_rotation]
        status=ExecutionStatus.APPROXIMATE
        reason="bounded target projection; residual measured, NOT exact"
    else:
        native=None
        status=ExecutionStatus.REFUSED
        reason="desired target not exactly representable in native action constraints"
    return PoseTransportWitness(
        status=status,
        native_action=None if native is None else tuple(float(x) for x in native),
        required_native_amplitude=required_amp,
        position_goal_residual_m=distance_p,
        orientation_goal_residual_rad=distance_r,
        reason=reason
    )
