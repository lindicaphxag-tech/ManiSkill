from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Literal

import numpy as np

from .core import JointControllerContext, JointGoalChart, MissingControllerStateError


ReachabilityStatus = Literal[
    "one_step_exact",
    "multi_step_semantic_possible",
    "unrepresentable",
]


@dataclass(frozen=True)
class HorizonReachabilityCertificate:
    """Semantic reachability certificate for one physical joint goal.

    The certificate is deliberately limited to controller-command semantics.
    It does not claim that the robot will realize the same state trajectory.

    For delta-current controllers, any multi-step realization requires fresh
    measured q_current feedback after every step. For delta-target controllers,
    the semantic reference is the controller's internal target and can be
    propagated deterministically at the command level.
    """

    status: ReachabilityStatus
    one_step_exact: bool
    min_semantic_steps: int | None
    requires_intermediate_state_feedback: bool
    displacement: np.ndarray
    per_step_lower: np.ndarray | None
    per_step_upper: np.ndarray | None
    reason: str


@dataclass(frozen=True)
class DeltaTargetSequence:
    """Constructive E1 command-level realization for delta-target control."""

    native_actions: np.ndarray
    physical_increments: np.ndarray
    semantic_goals: np.ndarray
    certificate: HorizonReachabilityCertificate


def _vec(value, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 1 or out.size == 0:
        raise ValueError(f"{name} must be a non-empty 1D array")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _reference(
    chart: JointGoalChart,
    context: JointControllerContext,
    dim: int,
) -> np.ndarray:
    if chart.mode == "absolute":
        # Absolute charts have no incremental reference. This sentinel is only
        # used to define displacement for reporting.
        return np.zeros(dim, dtype=float)
    name = "q_current" if chart.mode == "delta_current" else "q_target"
    value = getattr(context, name)
    if value is None:
        raise MissingControllerStateError(f"{chart.mode} chart requires {name}")
    value = _vec(value, name)
    if value.size != dim:
        raise ValueError(f"{name} dimension mismatch")
    return value


def _physical_bounds(
    chart: JointGoalChart,
    dim: int,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    # Reuse the chart's validated physical bounds. They are the reachable
    # command set before native normalization.
    return chart._bounds(dim)


def _box_min_steps(
    displacement: np.ndarray,
    low: np.ndarray,
    high: np.ndarray,
    *,
    tolerance: float,
) -> int | None:
    """Minimum H such that displacement belongs to H-fold Minkowski box sum."""
    if np.any(low > tolerance) or np.any(high < -tolerance):
        # A box that excludes zero has a minimum-magnitude complication; avoid
        # claiming a closed-form horizon in that uncommon controller regime.
        return None

    required = 1
    for delta, lo, hi in zip(displacement, low, high, strict=True):
        if abs(delta) <= tolerance:
            continue
        if delta > 0:
            if hi <= tolerance:
                return None
            required = max(required, int(ceil((delta - tolerance) / hi)))
        else:
            if lo >= -tolerance:
                return None
            required = max(required, int(ceil((-delta - tolerance) / (-lo))))
    return required


def certify_joint_goal_horizon(
    chart: JointGoalChart,
    q_goal: np.ndarray,
    context: JointControllerContext,
    *,
    tolerance: float = 1e-10,
) -> HorizonReachabilityCertificate:
    """Certify one-step exactness and a semantic minimum-horizon lower bound.

    For an incremental target controller with per-step physical command box B,
    a displacement d is one-step representable iff d is in B. A necessary
    command-level H-step condition is d in the H-fold Minkowski sum of B.

    The returned minimum is exact for a state-independent box at the semantic
    command level. It is *not* an E3 realized-trajectory guarantee.
    """
    goal = _vec(q_goal, "q_goal")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")

    if chart.mode == "absolute":
        encoded = chart.encode(goal, context)
        return HorizonReachabilityCertificate(
            status="one_step_exact" if encoded.representable else "unrepresentable",
            one_step_exact=encoded.representable,
            min_semantic_steps=1 if encoded.representable else None,
            requires_intermediate_state_feedback=False,
            displacement=goal.copy(),
            per_step_lower=(
                None
                if chart._bounds(goal.size)[0] is None
                else chart._bounds(goal.size)[0].copy()
            ),
            per_step_upper=(
                None
                if chart._bounds(goal.size)[1] is None
                else chart._bounds(goal.size)[1].copy()
            ),
            reason=(
                "absolute target is directly representable"
                if encoded.representable
                else "absolute target lies outside the target chart; repetition cannot fix representability"
            ),
        )

    reference = _reference(chart, context, goal.size)
    displacement = goal - reference
    low, high = _physical_bounds(chart, goal.size)

    if low is None:
        return HorizonReachabilityCertificate(
            status="one_step_exact",
            one_step_exact=True,
            min_semantic_steps=1,
            requires_intermediate_state_feedback=False,
            displacement=displacement,
            per_step_lower=None,
            per_step_upper=None,
            reason="incremental chart is physically unbounded at the semantic level",
        )

    one_step = bool(
        np.all(displacement >= low - tolerance)
        and np.all(displacement <= high + tolerance)
    )
    if one_step:
        return HorizonReachabilityCertificate(
            status="one_step_exact",
            one_step_exact=True,
            min_semantic_steps=1,
            requires_intermediate_state_feedback=False,
            displacement=displacement,
            per_step_lower=low,
            per_step_upper=high,
            reason="semantic displacement lies inside the one-step reachable box",
        )

    steps = _box_min_steps(displacement, low, high, tolerance=tolerance)
    if steps is None:
        return HorizonReachabilityCertificate(
            status="unrepresentable",
            one_step_exact=False,
            min_semantic_steps=None,
            requires_intermediate_state_feedback=(chart.mode == "delta_current"),
            displacement=displacement,
            per_step_lower=low,
            per_step_upper=high,
            reason=(
                "the requested displacement is unreachable in at least one direction "
                "under the configured incremental command bounds"
            ),
        )

    return HorizonReachabilityCertificate(
        status="multi_step_semantic_possible",
        one_step_exact=False,
        min_semantic_steps=steps,
        requires_intermediate_state_feedback=(chart.mode == "delta_current"),
        displacement=displacement,
        per_step_lower=low,
        per_step_upper=high,
        reason=(
            f"one-step exact transport is impossible; at least {steps} semantic "
            + (
                "steps are needed and each later step must be re-encoded from measured q_current"
                if chart.mode == "delta_current"
                else "target updates are needed under the controller's internal q_target semantics"
            )
        ),
    )


def construct_delta_target_sequence(
    chart: JointGoalChart,
    q_goal: np.ndarray,
    context: JointControllerContext,
    *,
    tolerance: float = 1e-10,
) -> DeltaTargetSequence:
    """Construct a minimum-length E1 sequence for a bounded delta-target chart.

    This is valid at command semantics because q_target is the reference that
    the controller itself accumulates. It does not assert E2/E3 equivalence.
    """
    if chart.mode != "delta_target":
        raise ValueError("construct_delta_target_sequence requires delta_target chart")
    goal = _vec(q_goal, "q_goal")
    cert = certify_joint_goal_horizon(
        chart,
        goal,
        context,
        tolerance=tolerance,
    )
    if cert.min_semantic_steps is None:
        raise ValueError(cert.reason)

    initial = _reference(chart, context, goal.size)
    steps = cert.min_semantic_steps
    total = goal - initial
    increment = total / float(steps)

    native_actions: list[np.ndarray] = []
    increments: list[np.ndarray] = []
    semantic_goals: list[np.ndarray] = []
    q_target = initial.copy()
    for _ in range(steps):
        next_goal = q_target + increment
        encoded = chart.encode(
            next_goal,
            JointControllerContext(q_target=q_target),
        )
        if not encoded.representable:
            raise RuntimeError(
                "minimum-horizon construction violated its own representability certificate"
            )
        native_actions.append(encoded.action)
        increments.append(increment.copy())
        semantic_goals.append(next_goal.copy())
        q_target = next_goal

    if np.linalg.norm(q_target - goal) > tolerance:
        raise RuntimeError("constructed semantic sequence does not terminate at q_goal")

    return DeltaTargetSequence(
        native_actions=np.stack(native_actions, axis=0),
        physical_increments=np.stack(increments, axis=0),
        semantic_goals=np.stack(semantic_goals, axis=0),
        certificate=cert,
    )
