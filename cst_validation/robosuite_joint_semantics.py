from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from trace_semantics import StatefulTraceIR
from piecewise_affine_clip import compile_clipped_affine_partition


@dataclass(frozen=True)
class RobosuiteAffineRegion:
    ir: StatefulTraceIR
    clip_inactive: bool
    unclipped_goal_low: np.ndarray
    unclipped_goal_high: np.ndarray
    qpos_low: np.ndarray | None
    qpos_high: np.ndarray | None
    reason: str


def _as_vector(value, d):
    value = np.asarray(value, dtype=float)
    if value.ndim == 0:
        value = np.full(d, float(value))
    if value.shape != (d,):
        raise ValueError("value must be scalar or shape [D]")
    return value


def robosuite_joint_position_ir(
    *,
    input_type,
    d,
    input_min=-1.0,
    input_max=1.0,
    output_min=-0.05,
    output_max=0.05,
    native_absolute_low=None,
    native_absolute_high=None,
):
    """Affine no-interpolator IR for robosuite fixed-impedance JOINT_POSITION.

    This models JointPositionController.set_goal() before qpos clipping.

    delta:
        clipped native action is affinely scaled from input range to output
        range, then added to current joint position.
    absolute:
        action is used directly as goal_qpos by set_goal().

    The controller stores goal_qpos, so z_next is the accepted goal. The stored
    goal is exposed as semantic memory even though the fixed delta branch uses
    current joint position, not previous goal, to interpret the next action.
    """
    if d <= 0:
        raise ValueError("d must be positive")
    input_min = _as_vector(input_min, d)
    input_max = _as_vector(input_max, d)
    output_min = _as_vector(output_min, d)
    output_max = _as_vector(output_max, d)
    if np.any(input_max <= input_min):
        raise ValueError("input_max must exceed input_min")

    trace_steps = 1
    zeros = np.zeros((d, d))
    eye = np.eye(d)

    if input_type == "delta":
        scale = np.abs(output_max - output_min) / np.abs(input_max - input_min)
        input_mid = 0.5 * (input_max + input_min)
        output_mid = 0.5 * (output_max + output_min)
        U = np.diag(scale)
        b = output_mid - scale * input_mid

        G_u = U
        G_x = eye
        G_z = zeros
        g = b
        native_low = input_min
        native_high = input_max
    elif input_type == "absolute":
        G_u = eye
        G_x = zeros
        G_z = zeros
        g = np.zeros(d)
        if native_absolute_low is None or native_absolute_high is None:
            raise ValueError(
                "absolute mode requires an explicit declared native physical domain"
            )
        native_low = _as_vector(native_absolute_low, d)
        native_high = _as_vector(native_absolute_high, d)
        if np.any(native_high <= native_low):
            raise ValueError("absolute native high must exceed low")
    else:
        raise ValueError("input_type must be delta or absolute")

    # Without an interpolator, run_controller consumes goal_qpos as the desired
    # joint target. We therefore expose one held drive-target step.
    return StatefulTraceIR(
        T_u=G_u.copy(),
        T_x=G_x.copy(),
        T_z=G_z.copy(),
        t=g.copy(),
        G_u=G_u,
        G_x=G_x,
        G_z=G_z,
        g=g,
        H_u=G_u.copy(),
        H_x=G_x.copy(),
        H_z=G_z.copy(),
        h=g.copy(),
        native_low=native_low,
        native_high=native_high,
        trace_steps=trace_steps,
        name=f"robosuite_joint_position:{input_type}",
    )


def certify_robosuite_delta_affine_region(
    *,
    d,
    state_low,
    state_high,
    input_min=-1.0,
    input_max=1.0,
    output_min=-0.05,
    output_max=0.05,
    qpos_limits=None,
):
    """Certify that robosuite's qpos clipping is inactive on a whole region."""
    state_low = _as_vector(state_low, d)
    state_high = _as_vector(state_high, d)
    if np.any(state_high < state_low):
        raise ValueError("state_high must be >= state_low")

    ir = robosuite_joint_position_ir(
        input_type="delta",
        d=d,
        input_min=input_min,
        input_max=input_max,
        output_min=output_min,
        output_max=output_max,
    )

    # The native action box maps monotonically coordinate-wise through
    # robosuite scale_action; derive exact physical delta extrema.
    input_min_v = _as_vector(input_min, d)
    input_max_v = _as_vector(input_max, d)
    output_min_v = _as_vector(output_min, d)
    output_max_v = _as_vector(output_max, d)
    scale = np.abs(output_max_v - output_min_v) / np.abs(
        input_max_v - input_min_v
    )
    input_mid = 0.5 * (input_max_v + input_min_v)
    output_mid = 0.5 * (output_max_v + output_min_v)
    delta_at_low = (input_min_v - input_mid) * scale + output_mid
    delta_at_high = (input_max_v - input_mid) * scale + output_mid
    delta_low = np.minimum(delta_at_low, delta_at_high)
    delta_high = np.maximum(delta_at_low, delta_at_high)

    goal_low = state_low + delta_low
    goal_high = state_high + delta_high

    if qpos_limits is None:
        return RobosuiteAffineRegion(
            ir=ir,
            clip_inactive=True,
            unclipped_goal_low=goal_low,
            unclipped_goal_high=goal_high,
            qpos_low=None,
            qpos_high=None,
            reason="no qpos clipping is configured",
        )

    limits = np.asarray(qpos_limits, dtype=float)
    if limits.shape != (2, d):
        raise ValueError("qpos_limits must have shape [2, D]")
    qlow, qhigh = limits[0], limits[1]
    inactive = bool(
        np.all(goal_low >= qlow) and np.all(goal_high <= qhigh)
    )
    reason = (
        "declared action/state region stays inside qpos limits"
        if inactive
        else "declared region crosses a qpos clipping boundary; split or refuse"
    )
    return RobosuiteAffineRegion(
        ir=ir,
        clip_inactive=inactive,
        unclipped_goal_low=goal_low,
        unclipped_goal_high=goal_high,
        qpos_low=qlow,
        qpos_high=qhigh,
        reason=reason,
    )


def compile_robosuite_delta_goal_partition(
    *,
    d,
    state_low,
    state_high,
    input_min=-1.0,
    input_max=1.0,
    output_min=-0.05,
    output_max=0.05,
    qpos_limits=None,
):
    """Compile robosuite delta joint goals including qpos clipping exactly.

    Input variable is v = [native_delta_action, current_qpos].
    For fixed-impedance JOINT_POSITION before clipping,

        goal = S u + x + b.

    Coordinate-wise qpos clipping makes this piecewise affine.  The returned
    polyhedral partition is exact on the full declared action/state box.
    """
    if qpos_limits is None:
        raise ValueError("qpos_limits are required for clipped partition")
    state_low = _as_vector(state_low, d)
    state_high = _as_vector(state_high, d)
    input_min_v = _as_vector(input_min, d)
    input_max_v = _as_vector(input_max, d)
    output_min_v = _as_vector(output_min, d)
    output_max_v = _as_vector(output_max, d)
    limits = np.asarray(qpos_limits, dtype=float)
    if limits.shape != (2, d):
        raise ValueError("qpos_limits must have shape [2, D]")

    scale = np.abs(output_max_v - output_min_v) / np.abs(
        input_max_v - input_min_v
    )
    input_mid = 0.5 * (input_max_v + input_min_v)
    output_mid = 0.5 * (output_max_v + output_min_v)
    b = output_mid - scale * input_mid
    A = np.concatenate([np.diag(scale), np.eye(d)], axis=1)

    return compile_clipped_affine_partition(
        A=A,
        b=b,
        clip_low=limits[0],
        clip_high=limits[1],
        input_low=np.concatenate([input_min_v, state_low]),
        input_high=np.concatenate([input_max_v, state_high]),
    )
