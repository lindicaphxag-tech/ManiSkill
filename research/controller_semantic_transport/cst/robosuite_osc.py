from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(frozen=True)
class OSCState:
    """Hidden state needed to interpret a robosuite-style OSC delta action."""

    achieved_pos: np.ndarray
    achieved_ori: np.ndarray
    desired_pos: np.ndarray
    desired_ori: np.ndarray


@dataclass(frozen=True)
class OSCInverseCertificate:
    accepted: bool
    native_delta_action: np.ndarray
    physical_delta: np.ndarray
    reconstructed_absolute_action: np.ndarray
    position_residual: float
    orientation_residual: float
    saturation_margin: float
    reason: str


def _as_vec(x, n: int, name: str) -> np.ndarray:
    out = np.asarray(x, dtype=float)
    if out.shape != (n,) or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be a finite vector of shape {(n,)}")
    return out


def _as_rot(x, name: str) -> np.ndarray:
    out = np.asarray(x, dtype=float)
    if out.shape != (3, 3) or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be a finite 3x3 rotation matrix")
    return out


def _rotation_geodesic(a: np.ndarray, b: np.ndarray) -> float:
    relative = a.T @ b
    value = np.clip((np.trace(relative) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.arccos(value))


def inverse_affine_action_scale(
    physical: np.ndarray,
    *,
    input_min: np.ndarray,
    input_max: np.ndarray,
    output_min: np.ndarray,
    output_max: np.ndarray,
) -> tuple[np.ndarray, bool, float]:
    """Invert robosuite Controller.scale_action without silently clipping."""
    physical = np.asarray(physical, dtype=float)
    input_min = np.broadcast_to(np.asarray(input_min, dtype=float), physical.shape)
    input_max = np.broadcast_to(np.asarray(input_max, dtype=float), physical.shape)
    output_min = np.broadcast_to(np.asarray(output_min, dtype=float), physical.shape)
    output_max = np.broadcast_to(np.asarray(output_max, dtype=float), physical.shape)

    if np.any(input_max <= input_min) or np.any(output_max <= output_min):
        raise ValueError("input/output action bounds must have positive width")

    output_mid = 0.5 * (output_max + output_min)
    input_mid = 0.5 * (input_max + input_min)
    scale = (output_max - output_min) / (input_max - input_min)
    native = (physical - output_mid) / scale + input_mid

    representable = bool(
        np.all(native >= input_min - 1e-12)
        and np.all(native <= input_max + 1e-12)
    )
    left = (native - input_min) / (input_max - input_min)
    right = (input_max - native) / (input_max - input_min)
    margin = float(np.min(np.minimum(left, right)))
    return native, representable, margin


def absolute_pose_to_delta_action(
    *,
    absolute_action: np.ndarray,
    state: OSCState,
    goal_update_mode: str,
    input_min: np.ndarray,
    input_max: np.ndarray,
    output_min: np.ndarray,
    output_max: np.ndarray,
) -> OSCInverseCertificate:
    """Compile an absolute OSC pose into a robosuite-style native delta action.

    Version 0 intentionally handles the world-reference-frame semantics used by
    robosuite's OperationalSpaceController.  The absolute action is
    [x, y, z, rx, ry, rz], with orientation represented as a rotation vector.

    Forward robosuite semantics are:
      p_goal = p_base + delta_p
      R_goal = Exp(delta_r) @ R_base

    where base is either the achieved or previous desired pose.  Therefore:
      delta_p = p_abs - p_base
      Exp(delta_r) = R_abs @ R_base.T
    """
    absolute = _as_vec(absolute_action, 6, "absolute_action")
    achieved_pos = _as_vec(state.achieved_pos, 3, "achieved_pos")
    desired_pos = _as_vec(state.desired_pos, 3, "desired_pos")
    achieved_ori = _as_rot(state.achieved_ori, "achieved_ori")
    desired_ori = _as_rot(state.desired_ori, "desired_ori")

    if goal_update_mode == "achieved":
        base_pos = achieved_pos
        base_ori = achieved_ori
    elif goal_update_mode == "desired":
        base_pos = desired_pos
        base_ori = desired_ori
    else:
        raise ValueError("goal_update_mode must be 'achieved' or 'desired'")

    target_pos = absolute[:3]
    target_ori = Rotation.from_rotvec(absolute[3:]).as_matrix()
    delta_pos = target_pos - base_pos
    delta_ori = target_ori @ base_ori.T
    delta_rotvec = Rotation.from_matrix(delta_ori).as_rotvec()
    physical_delta = np.concatenate([delta_pos, delta_rotvec])

    native, representable, margin = inverse_affine_action_scale(
        physical_delta,
        input_min=input_min,
        input_max=input_max,
        output_min=output_min,
        output_max=output_max,
    )

    # Pure semantic reconstruction mirrors the documented/implemented forward
    # decoder and is checked again against the upstream implementation in the
    # frozen robosuite integration gate.
    scaled_pos = base_pos + physical_delta[:3]
    scaled_ori = Rotation.from_rotvec(physical_delta[3:]).as_matrix() @ base_ori
    reconstructed = np.concatenate(
        [scaled_pos, Rotation.from_matrix(scaled_ori).as_rotvec()]
    )
    pos_residual = float(np.linalg.norm(scaled_pos - target_pos))
    ori_residual = _rotation_geodesic(scaled_ori, target_ori)

    accepted = representable and pos_residual <= 1e-9 and ori_residual <= 1e-9
    if not representable:
        reason = "absolute pose requires a delta outside the target OSC native action image"
    elif not accepted:
        reason = "inverse OSC action does not reconstruct the requested absolute pose"
    else:
        reason = "native delta action reconstructs the requested absolute OSC pose"

    return OSCInverseCertificate(
        accepted=accepted,
        native_delta_action=native,
        physical_delta=physical_delta,
        reconstructed_absolute_action=reconstructed,
        position_residual=pos_residual,
        orientation_residual=ori_residual,
        saturation_margin=margin,
        reason=reason,
    )
