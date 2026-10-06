from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class OSCInverseStatus(str, Enum):
    EXACT = "exact"
    SATURATED = "saturated"


@dataclass(frozen=True)
class OSCActionChart:
    """Minimal executable OSC action chart used by robosuite-style controllers."""

    input_min: np.ndarray
    input_max: np.ndarray
    output_min: np.ndarray
    output_max: np.ndarray

    def __post_init__(self):
        arrays = [
            np.asarray(self.input_min, dtype=float),
            np.asarray(self.input_max, dtype=float),
            np.asarray(self.output_min, dtype=float),
            np.asarray(self.output_max, dtype=float),
        ]
        shape = arrays[0].shape
        if len(shape) != 1 or shape[0] not in (3, 6):
            raise ValueError("OSC chart must be a 3D or 6D vector chart")
        if any(a.shape != shape for a in arrays[1:]):
            raise ValueError("all OSC chart bounds must share shape")
        if np.any(arrays[1] <= arrays[0]) or np.any(arrays[3] <= arrays[2]):
            raise ValueError("OSC chart upper bounds must exceed lower bounds")
        object.__setattr__(self, "input_min", arrays[0])
        object.__setattr__(self, "input_max", arrays[1])
        object.__setattr__(self, "output_min", arrays[2])
        object.__setattr__(self, "output_max", arrays[3])

    @property
    def dim(self) -> int:
        return int(self.input_min.shape[0])

    def decode_delta(self, native_action: np.ndarray) -> np.ndarray:
        """Mirror robosuite's clipped affine input->output scaling."""
        native = np.asarray(native_action, dtype=float)
        if native.shape != (self.dim,):
            raise ValueError("native action dimension mismatch")
        clipped = np.clip(native, self.input_min, self.input_max)
        frac = (clipped - self.input_min) / (self.input_max - self.input_min)
        return self.output_min + frac * (self.output_max - self.output_min)

    def encode_delta(self, physical_delta: np.ndarray) -> tuple[np.ndarray, bool]:
        """Inverse chart with explicit representability instead of silent clipping."""
        delta = np.asarray(physical_delta, dtype=float)
        if delta.shape != (self.dim,):
            raise ValueError("physical delta dimension mismatch")
        representable = bool(
            np.all(delta >= self.output_min) and np.all(delta <= self.output_max)
        )
        clipped = np.clip(delta, self.output_min, self.output_max)
        frac = (clipped - self.output_min) / (self.output_max - self.output_min)
        native = self.input_min + frac * (self.input_max - self.input_min)
        return native, representable


@dataclass(frozen=True)
class OSCGoal:
    position: np.ndarray
    orientation: np.ndarray


@dataclass(frozen=True)
class OSCInverseCertificate:
    status: OSCInverseStatus
    native_delta_action: np.ndarray
    requested_physical_delta: np.ndarray
    reconstructed_goal_position: np.ndarray
    reconstructed_goal_orientation: np.ndarray
    position_residual_norm: float
    orientation_residual_angle: float
    representable: bool
    uses_desired_goal_memory: bool
    reason: str


def _normalize_rotation(R: np.ndarray) -> np.ndarray:
    R = np.asarray(R, dtype=float)
    if R.shape != (3, 3):
        raise ValueError("rotation must be 3x3")
    u, _, vh = np.linalg.svd(R)
    out = u @ vh
    if np.linalg.det(out) < 0:
        u[:, -1] *= -1
        out = u @ vh
    return out


def rotvec_to_matrix(rotvec: np.ndarray) -> np.ndarray:
    v = np.asarray(rotvec, dtype=float)
    if v.shape != (3,):
        raise ValueError("rotvec must have shape (3,)")
    theta = float(np.linalg.norm(v))
    if theta < 1e-12:
        K = _skew(v)
        return np.eye(3) + K
    axis = v / theta
    K = _skew(axis)
    return np.eye(3) + np.sin(theta) * K + (1.0 - np.cos(theta)) * (K @ K)


def matrix_to_rotvec(R: np.ndarray) -> np.ndarray:
    R = _normalize_rotation(R)
    cos_theta = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    theta = float(np.arccos(cos_theta))
    if theta < 1e-10:
        return 0.5 * np.array(
            [R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]
        )
    if np.pi - theta < 1e-6:
        # Stable eigenvector extraction near pi.
        vals, vecs = np.linalg.eigh((R + np.eye(3)) / 2.0)
        axis = vecs[:, int(np.argmax(vals))]
        axis = axis / np.linalg.norm(axis)
        skew_hint = np.array(
            [R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]
        )
        if float(axis @ skew_hint) < 0:
            axis = -axis
        return axis * theta
    axis = np.array(
        [R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]
    ) / (2.0 * np.sin(theta))
    return axis * theta


def _skew(v: np.ndarray) -> np.ndarray:
    x, y, z = np.asarray(v, dtype=float)
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def orientation_distance(R_a: np.ndarray, R_b: np.ndarray) -> float:
    return float(np.linalg.norm(matrix_to_rotvec(_normalize_rotation(R_a) @ _normalize_rotation(R_b).T)))


def forward_delta_to_absolute_goal(
    chart: OSCActionChart,
    native_delta_action: np.ndarray,
    *,
    achieved_position: np.ndarray,
    achieved_orientation: np.ndarray,
    desired_position: np.ndarray,
    desired_orientation: np.ndarray,
    goal_update_mode: str,
) -> OSCGoal:
    """Executable goal semantics matching robosuite OSC delta mode."""
    if goal_update_mode not in ("achieved", "desired"):
        raise ValueError("goal_update_mode must be achieved or desired")
    delta = chart.decode_delta(native_delta_action)
    base_pos = (
        np.asarray(desired_position, dtype=float)
        if goal_update_mode == "desired"
        else np.asarray(achieved_position, dtype=float)
    )
    base_ori = (
        _normalize_rotation(desired_orientation)
        if goal_update_mode == "desired"
        else _normalize_rotation(achieved_orientation)
    )
    goal_pos = base_pos + delta[:3]
    if chart.dim == 6:
        goal_ori = rotvec_to_matrix(delta[3:6]) @ base_ori
    else:
        goal_ori = base_ori
    return OSCGoal(position=goal_pos, orientation=goal_ori)


def inverse_absolute_goal_to_delta(
    chart: OSCActionChart,
    absolute_goal_position: np.ndarray,
    absolute_goal_orientation: np.ndarray,
    *,
    achieved_position: np.ndarray,
    achieved_orientation: np.ndarray,
    desired_position: np.ndarray,
    desired_orientation: np.ndarray,
    goal_update_mode: str,
) -> OSCInverseCertificate:
    """Invert an absolute OSC goal into the native delta action chart.

    For orientation, robosuite's forward semantics are
        R_goal = R_delta @ R_base,
    therefore
        R_delta = R_goal @ R_base.T.
    """
    if goal_update_mode not in ("achieved", "desired"):
        raise ValueError("goal_update_mode must be achieved or desired")

    goal_pos = np.asarray(absolute_goal_position, dtype=float)
    goal_ori = _normalize_rotation(absolute_goal_orientation)
    base_pos = (
        np.asarray(desired_position, dtype=float)
        if goal_update_mode == "desired"
        else np.asarray(achieved_position, dtype=float)
    )
    base_ori = (
        _normalize_rotation(desired_orientation)
        if goal_update_mode == "desired"
        else _normalize_rotation(achieved_orientation)
    )
    pos_delta = goal_pos - base_pos
    if chart.dim == 6:
        delta_R = goal_ori @ base_ori.T
        ori_delta = matrix_to_rotvec(delta_R)
        physical_delta = np.concatenate([pos_delta, ori_delta])
    else:
        physical_delta = pos_delta

    native, representable = chart.encode_delta(physical_delta)
    reconstructed = forward_delta_to_absolute_goal(
        chart,
        native,
        achieved_position=achieved_position,
        achieved_orientation=achieved_orientation,
        desired_position=desired_position,
        desired_orientation=desired_orientation,
        goal_update_mode=goal_update_mode,
    )
    p_res = float(np.linalg.norm(reconstructed.position - goal_pos))
    o_res = orientation_distance(reconstructed.orientation, goal_ori)

    exact = representable and p_res <= 1e-10 and o_res <= 1e-10
    return OSCInverseCertificate(
        status=OSCInverseStatus.EXACT if exact else OSCInverseStatus.SATURATED,
        native_delta_action=native,
        requested_physical_delta=physical_delta,
        reconstructed_goal_position=reconstructed.position,
        reconstructed_goal_orientation=reconstructed.orientation,
        position_residual_norm=p_res,
        orientation_residual_angle=o_res,
        representable=representable,
        uses_desired_goal_memory=(goal_update_mode == "desired"),
        reason=(
            "absolute goal is exactly representable in the native delta action chart"
            if exact
            else "absolute goal requires a delta outside the controller output range"
        ),
    )


def convert_absolute_action_with_remainder(
    chart: OSCActionChart,
    absolute_action: np.ndarray,
    *,
    achieved_position: np.ndarray,
    achieved_orientation: np.ndarray,
    desired_position: np.ndarray,
    desired_orientation: np.ndarray,
    goal_update_mode: str,
) -> tuple[np.ndarray, OSCInverseCertificate]:
    """Convert pose prefix while preserving gripper / other action remainder."""
    action = np.asarray(absolute_action, dtype=float)
    if action.ndim != 1 or action.size < 6:
        raise ValueError("absolute action must contain position+rotvec prefix")
    goal_pos = action[:3]
    goal_ori = rotvec_to_matrix(action[3:6])
    cert = inverse_absolute_goal_to_delta(
        chart,
        goal_pos,
        goal_ori,
        achieved_position=achieved_position,
        achieved_orientation=achieved_orientation,
        desired_position=desired_position,
        desired_orientation=desired_orientation,
        goal_update_mode=goal_update_mode,
    )
    converted = np.concatenate([cert.native_delta_action, action[6:]])
    return converted, cert
