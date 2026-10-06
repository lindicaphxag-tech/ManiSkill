from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .core import JointControllerContext, JointGoalChart


SequenceIdentifiability = Literal["identifiable", "state_trace_required", "unidentifiable"]


@dataclass(frozen=True)
class SequenceStateRequirement:
    """Minimal controller-state provenance needed to decode an action sequence."""

    status: SequenceIdentifiability
    required_initial_state: tuple[str, ...]
    required_per_step_state: tuple[str, ...]
    recursively_reconstructible: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class ReconstructedGoalTrace:
    semantic_goals: np.ndarray
    reference_trace: np.ndarray | None
    requirement: SequenceStateRequirement


def sequence_state_requirement(chart: JointGoalChart) -> SequenceStateRequirement:
    """Return the minimal state provenance needed for lossless sequence decoding.

    The result is deliberately about E1 command semantics, not realized robot
    trajectories.

    - absolute actions directly identify the commanded joint goal;
    - delta_current actions require measured q_current at every step because
      dynamics determine the next reference;
    - delta_target actions need only the initial q_target. Thereafter the
      controller reference is recursively reconstructible from the command
      sequence itself, provided no hidden reset or target mutation occurs.
    """
    if chart.mode == "absolute":
        return SequenceStateRequirement(
            status="identifiable",
            required_initial_state=(),
            required_per_step_state=(),
            recursively_reconstructible=(),
            reason="absolute actions directly encode the physical joint goal",
        )
    if chart.mode == "delta_current":
        return SequenceStateRequirement(
            status="state_trace_required",
            required_initial_state=(),
            required_per_step_state=("q_current",),
            recursively_reconstructible=(),
            reason=(
                "each action is referenced to measured q_current; later references "
                "depend on realized dynamics and cannot be inferred from actions alone"
            ),
        )
    if chart.mode == "delta_target":
        return SequenceStateRequirement(
            status="identifiable",
            required_initial_state=("q_target",),
            required_per_step_state=(),
            recursively_reconstructible=("q_target",),
            reason=(
                "initial q_target plus the action sequence recursively determines "
                "all later target references at command semantics"
            ),
        )
    raise ValueError(f"unsupported chart mode: {chart.mode}")


def _actions(actions: np.ndarray) -> np.ndarray:
    out = np.asarray(actions, dtype=float)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise ValueError("actions must have non-empty shape [T, D]")
    if not np.all(np.isfinite(out)):
        raise ValueError("actions must be finite")
    return out


def reconstruct_joint_goal_trace(
    chart: JointGoalChart,
    actions: np.ndarray,
    *,
    initial_context: JointControllerContext | None = None,
    q_current_trace: np.ndarray | None = None,
) -> ReconstructedGoalTrace:
    """Losslessly decode a joint-action sequence when provenance is sufficient.

    Raises ValueError instead of inventing missing controller state.
    """
    native = _actions(actions)
    requirement = sequence_state_requirement(chart)
    context = initial_context or JointControllerContext()

    if chart.mode == "absolute":
        goals = np.stack(
            [chart.decode(action, JointControllerContext()) for action in native],
            axis=0,
        )
        return ReconstructedGoalTrace(
            semantic_goals=goals,
            reference_trace=None,
            requirement=requirement,
        )

    if chart.mode == "delta_current":
        if q_current_trace is None:
            raise ValueError(
                "lossless delta_current decoding requires q_current at every step"
            )
        current = np.asarray(q_current_trace, dtype=float)
        if current.shape != native.shape or not np.all(np.isfinite(current)):
            raise ValueError("q_current_trace must be finite with shape [T, D]")
        goals = np.stack(
            [
                chart.decode(
                    action,
                    JointControllerContext(q_current=q_current),
                )
                for action, q_current in zip(native, current, strict=True)
            ],
            axis=0,
        )
        return ReconstructedGoalTrace(
            semantic_goals=goals,
            reference_trace=current.copy(),
            requirement=requirement,
        )

    if chart.mode == "delta_target":
        if context.q_target is None:
            raise ValueError(
                "lossless delta_target decoding requires the initial q_target"
            )
        reference = np.asarray(context.q_target, dtype=float)
        if reference.shape != (native.shape[1],) or not np.all(np.isfinite(reference)):
            raise ValueError("initial q_target must be finite with shape [D]")

        refs = []
        goals = []
        for action in native:
            refs.append(reference.copy())
            goal = chart.decode(
                action,
                JointControllerContext(q_target=reference),
            )
            goals.append(goal)
            # Under delta-target semantics the decoded goal becomes the next
            # controller target reference.
            reference = goal
        return ReconstructedGoalTrace(
            semantic_goals=np.stack(goals, axis=0),
            reference_trace=np.stack(refs, axis=0),
            requirement=requirement,
        )

    raise ValueError(f"unsupported chart mode: {chart.mode}")
