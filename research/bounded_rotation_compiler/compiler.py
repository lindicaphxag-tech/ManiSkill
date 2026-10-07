"""Compile an SO(3) target into the shortest feasible uniform controller stream.

This is a research artifact, not a replacement for ManiSkill's runtime
controller. It models the production XYZ-Euler action interpretation and its
radial normalized-action clipping.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(frozen=True)
class CompiledRotation:
    actions: np.ndarray  # shape (steps, 3), normalized controller actions
    step_euler_xyz: np.ndarray
    steps: int
    endpoint_error_rad: float


def _rotation_error(a: Rotation, b: Rotation) -> float:
    """Geodesic distance on SO(3), in radians."""
    return float((a.inv() * b).magnitude())


def compile_uniform_geodesic(
    target_quaternion_xyzw: np.ndarray,
    action_scale: np.ndarray,
    *,
    max_steps: int = 4096,
    atol: float = 1e-10,
) -> CompiledRotation:
    """Find the smallest N for which N equal geodesic increments are feasible.

    ManiSkill's ``PDEEPoseController`` maps a normalized rotation action ``u``
    to Euler angles ``action_scale * u`` (currently ``rot_lower``; a proposed
    controller fix uses ``rot_upper``). Each increment is bounded by the
    controller's radial ``||u||_2 <= 1`` clip. SciPy's uppercase ``XYZ`` Euler
    convention matches the production matrix product Rx @ Ry @ Rz.

    Repeating one increment R^(1/N) exactly reconstructs R because powers of a
    single SO(3) element commute. Search is ascending, so the result minimizes
    the number of steps among uniform subdivisions of the principal geodesic.
    It is not claimed globally time-optimal under robot dynamics.
    """
    q = np.asarray(target_quaternion_xyzw, dtype=np.float64)
    scale = np.asarray(action_scale, dtype=np.float64)
    if q.shape != (4,) or scale.shape != (3,):
        raise ValueError("expected quaternion shape (4,) and action scale shape (3,)")
    if not np.all(np.isfinite(q)) or not np.all(np.isfinite(scale)):
        raise ValueError("inputs must be finite")
    if np.linalg.norm(q) < 1e-12:
        raise ValueError("target quaternion must be nonzero")
    if np.any(np.abs(scale) < 1e-12):
        raise ValueError("all controller rotation scales must be nonzero")
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")

    target = Rotation.from_quat(q)
    rotvec = target.as_rotvec()  # principal angle in [0, pi]
    for n in range(1, max_steps + 1):
        step = Rotation.from_rotvec(rotvec / n)
        euler = step.as_euler("XYZ")
        normalized = euler / scale
        if np.linalg.norm(normalized) <= 1.0 + atol:
            endpoint = step ** n
            error = _rotation_error(target, endpoint)
            actions = np.repeat(normalized[None, :], n, axis=0)
            return CompiledRotation(actions, euler, n, error)
    raise ValueError(f"no feasible uniform subdivision found in {max_steps} steps")


def direct_single_step(
    target_quaternion_xyzw: np.ndarray, action_scale: np.ndarray
) -> tuple[np.ndarray, float, bool]:
    """Apply the controller's current normalized radial clip to one Euler action."""
    target = Rotation.from_quat(np.asarray(target_quaternion_xyzw, dtype=np.float64))
    scale = np.asarray(action_scale, dtype=np.float64)
    euler = target.as_euler("XYZ")
    raw = euler / scale
    feasible = bool(np.linalg.norm(raw) <= 1.0)
    normalized = raw / max(1.0, np.linalg.norm(raw))
    realized = Rotation.from_euler("XYZ", scale * normalized)
    return normalized, _rotation_error(target, realized), feasible
