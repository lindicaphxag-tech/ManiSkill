from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class ReferenceKind(str, Enum):
    ABSOLUTE = "absolute"
    CURRENT_STATE = "current_state"
    CHUNK_ANCHOR = "chunk_anchor"
    PREVIOUS_COMMAND = "previous_command"
    CONTROLLER_TARGET = "controller_target"


@dataclass(frozen=True)
class ReferenceSemantics:
    kind: ReferenceKind
    relative_mask: np.ndarray

    def __post_init__(self):
        mask = np.asarray(self.relative_mask, dtype=bool)
        if mask.ndim != 1 or mask.size == 0:
            raise ValueError("relative_mask must be a non-empty vector")
        object.__setattr__(self, "relative_mask", mask)


@dataclass(frozen=True)
class DecodedTrace:
    goals: np.ndarray
    references: np.ndarray
    final_command: np.ndarray
    final_controller_target: np.ndarray


@dataclass(frozen=True)
class ReferenceTransport:
    target_actions: np.ndarray
    source_goals: np.ndarray
    target_goals: np.ndarray
    max_abs_goal_error: float
    exact: bool
    target_references: np.ndarray


def _matrix(x, name):
    out = np.asarray(x, dtype=float)
    if out.ndim != 2:
        raise ValueError(f"{name} must be [T, D]")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def decode_reference_trace(
    actions: np.ndarray,
    semantics: ReferenceSemantics,
    *,
    current_states: np.ndarray,
    chunk_anchor: np.ndarray | None = None,
    initial_previous_command: np.ndarray | None = None,
    controller_targets_before: np.ndarray | None = None,
) -> DecodedTrace:
    """Decode a native action sequence into absolute physical goals.

    The routine separates references that are often collapsed under the words
    "delta" or "relative":

    CURRENT_STATE:
        each step references the measured physical state at that step.

    CHUNK_ANCHOR:
        every action in a predicted chunk references one frozen state captured
        when the chunk was produced.

    PREVIOUS_COMMAND:
        the first action references an initial command/anchor; subsequent
        actions reference the previous decoded command.

    CONTROLLER_TARGET:
        each action references controller-owned target state supplied for that
        step.  This can differ from previous command after clipping,
        interpolation, reset, or other controller logic.
    """
    actions = _matrix(actions, "actions")
    states = _matrix(current_states, "current_states")
    if actions.shape != states.shape:
        raise ValueError("actions/current_states shape mismatch")
    T, D = actions.shape
    mask = semantics.relative_mask
    if mask.shape != (D,):
        raise ValueError("relative_mask dimension mismatch")

    anchor = None if chunk_anchor is None else np.asarray(chunk_anchor, dtype=float)
    previous = (
        None
        if initial_previous_command is None
        else np.asarray(initial_previous_command, dtype=float)
    )
    controller_targets = (
        None
        if controller_targets_before is None
        else _matrix(controller_targets_before, "controller_targets_before")
    )
    if anchor is not None and anchor.shape != (D,):
        raise ValueError("chunk_anchor dimension mismatch")
    if previous is not None and previous.shape != (D,):
        raise ValueError("initial_previous_command dimension mismatch")
    if controller_targets is not None and controller_targets.shape != (T, D):
        raise ValueError("controller_targets_before shape mismatch")

    goals = np.empty_like(actions)
    refs = np.empty_like(actions)

    for t in range(T):
        if semantics.kind is ReferenceKind.ABSOLUTE:
            ref = np.zeros(D)
            goal = actions[t].copy()
        elif semantics.kind is ReferenceKind.CURRENT_STATE:
            ref = states[t]
            goal = actions[t].copy()
            goal[mask] = ref[mask] + actions[t, mask]
        elif semantics.kind is ReferenceKind.CHUNK_ANCHOR:
            if anchor is None:
                raise ValueError("chunk_anchor is required")
            ref = anchor
            goal = actions[t].copy()
            goal[mask] = ref[mask] + actions[t, mask]
        elif semantics.kind is ReferenceKind.PREVIOUS_COMMAND:
            if previous is None:
                if anchor is None:
                    raise ValueError(
                        "PREVIOUS_COMMAND requires initial_previous_command or chunk_anchor"
                    )
                previous = anchor.copy()
            ref = previous
            goal = actions[t].copy()
            goal[mask] = ref[mask] + actions[t, mask]
            previous = goal.copy()
        elif semantics.kind is ReferenceKind.CONTROLLER_TARGET:
            if controller_targets is None:
                raise ValueError("controller_targets_before is required")
            ref = controller_targets[t]
            goal = actions[t].copy()
            goal[mask] = ref[mask] + actions[t, mask]
        else:
            raise AssertionError(semantics.kind)

        refs[t] = ref
        goals[t] = goal

    final_command = goals[-1].copy() if T else np.zeros(D)
    if controller_targets is None or T == 0:
        final_controller_target = final_command.copy()
    else:
        final_controller_target = controller_targets[-1].copy()

    return DecodedTrace(
        goals=goals,
        references=refs,
        final_command=final_command,
        final_controller_target=final_controller_target,
    )


def encode_goals_with_reference(
    goals: np.ndarray,
    semantics: ReferenceSemantics,
    *,
    current_states: np.ndarray,
    chunk_anchor: np.ndarray | None = None,
    initial_previous_command: np.ndarray | None = None,
    controller_targets_before: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Encode absolute goals into a target reference convention."""
    goals = _matrix(goals, "goals")
    states = _matrix(current_states, "current_states")
    if goals.shape != states.shape:
        raise ValueError("goals/current_states shape mismatch")
    T, D = goals.shape
    mask = semantics.relative_mask
    if mask.shape != (D,):
        raise ValueError("relative_mask dimension mismatch")

    anchor = None if chunk_anchor is None else np.asarray(chunk_anchor, dtype=float)
    previous = (
        None
        if initial_previous_command is None
        else np.asarray(initial_previous_command, dtype=float)
    )
    targets = (
        None
        if controller_targets_before is None
        else _matrix(controller_targets_before, "controller_targets_before")
    )

    actions = goals.copy()
    refs = np.zeros_like(goals)
    for t in range(T):
        if semantics.kind is ReferenceKind.ABSOLUTE:
            ref = np.zeros(D)
        elif semantics.kind is ReferenceKind.CURRENT_STATE:
            ref = states[t]
            actions[t, mask] = goals[t, mask] - ref[mask]
        elif semantics.kind is ReferenceKind.CHUNK_ANCHOR:
            if anchor is None:
                raise ValueError("chunk_anchor is required")
            ref = anchor
            actions[t, mask] = goals[t, mask] - ref[mask]
        elif semantics.kind is ReferenceKind.PREVIOUS_COMMAND:
            if previous is None:
                if anchor is None:
                    raise ValueError(
                        "PREVIOUS_COMMAND requires initial_previous_command or chunk_anchor"
                    )
                previous = anchor.copy()
            ref = previous
            actions[t, mask] = goals[t, mask] - ref[mask]
            previous = goals[t].copy()
        elif semantics.kind is ReferenceKind.CONTROLLER_TARGET:
            if targets is None:
                raise ValueError("controller_targets_before is required")
            ref = targets[t]
            actions[t, mask] = goals[t, mask] - ref[mask]
        else:
            raise AssertionError(semantics.kind)
        refs[t] = ref

    return actions, refs


def transport_reference_semantics(
    source_actions: np.ndarray,
    source_semantics: ReferenceSemantics,
    target_semantics: ReferenceSemantics,
    *,
    current_states: np.ndarray,
    source_chunk_anchor: np.ndarray | None = None,
    target_chunk_anchor: np.ndarray | None = None,
    source_initial_previous_command: np.ndarray | None = None,
    target_initial_previous_command: np.ndarray | None = None,
    source_controller_targets_before: np.ndarray | None = None,
    target_controller_targets_before: np.ndarray | None = None,
    atol: float = 1e-12,
) -> ReferenceTransport:
    """Decode source goals, then encode them under target reference semantics."""
    decoded = decode_reference_trace(
        source_actions,
        source_semantics,
        current_states=current_states,
        chunk_anchor=source_chunk_anchor,
        initial_previous_command=source_initial_previous_command,
        controller_targets_before=source_controller_targets_before,
    )
    target_actions, target_refs = encode_goals_with_reference(
        decoded.goals,
        target_semantics,
        current_states=current_states,
        chunk_anchor=target_chunk_anchor,
        initial_previous_command=target_initial_previous_command,
        controller_targets_before=target_controller_targets_before,
    )
    target_decoded = decode_reference_trace(
        target_actions,
        target_semantics,
        current_states=current_states,
        chunk_anchor=target_chunk_anchor,
        initial_previous_command=target_initial_previous_command,
        controller_targets_before=target_controller_targets_before,
    )
    err = float(np.max(np.abs(target_decoded.goals - decoded.goals)))
    return ReferenceTransport(
        target_actions=target_actions,
        source_goals=decoded.goals,
        target_goals=target_decoded.goals,
        max_abs_goal_error=err,
        exact=bool(err <= atol),
        target_references=target_refs,
    )
