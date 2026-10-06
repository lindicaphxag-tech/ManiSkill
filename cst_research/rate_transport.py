from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from reference_semantics import (
    ReferenceKind,
    ReferenceSemantics,
    decode_reference_trace,
    encode_goals_with_reference,
)


class RateDeployability(str, Enum):
    PRECOMPUTABLE = "precomputable"
    REQUIRES_STEP_HOOK = "requires_step_hook"
    REFUSE_MISSING_REFERENCE = "refuse_missing_reference"


@dataclass(frozen=True)
class RateTransportCertificate:
    source_rate_hz: float
    target_rate_hz: float
    integer_ratio: int
    deployability: RateDeployability
    refined_goals: np.ndarray
    target_actions: np.ndarray | None
    target_references: np.ndarray | None
    source_boundary_goals: np.ndarray
    target_boundary_goals: np.ndarray | None
    max_boundary_goal_error: float | None
    naive_repeat_boundary_error: float | None
    reason: str


def _integer_rate_ratio(source_rate_hz: float, target_rate_hz: float) -> int:
    if source_rate_hz <= 0 or target_rate_hz <= 0:
        raise ValueError("rates must be positive")
    ratio = target_rate_hz / source_rate_hz
    rounded = int(round(ratio))
    if rounded < 1 or abs(ratio - rounded) > 1e-12:
        raise ValueError(
            "v0.1 supports integer target/source rate ratios >= 1 only"
        )
    return rounded


def zoh_refine_goals(goals: np.ndarray, ratio: int) -> np.ndarray:
    """Refine a source goal trace using zero-order hold."""
    goals = np.asarray(goals, dtype=float)
    if goals.ndim != 2:
        raise ValueError("goals must be [T, D]")
    if ratio < 1:
        raise ValueError("ratio must be >= 1")
    return np.repeat(goals, ratio, axis=0)


def boundary_indices(source_steps: int, ratio: int) -> np.ndarray:
    """Indices of the final target substep corresponding to each source step."""
    return np.arange(ratio - 1, source_steps * ratio, ratio, dtype=int)


def target_rate_deployability(kind: ReferenceKind) -> RateDeployability:
    if kind in (
        ReferenceKind.ABSOLUTE,
        ReferenceKind.CHUNK_ANCHOR,
        ReferenceKind.PREVIOUS_COMMAND,
    ):
        return RateDeployability.PRECOMPUTABLE
    if kind in (ReferenceKind.CURRENT_STATE, ReferenceKind.CONTROLLER_TARGET):
        return RateDeployability.REQUIRES_STEP_HOOK
    raise AssertionError(kind)


def compile_zoh_rate_transport(
    source_actions: np.ndarray,
    source_semantics: ReferenceSemantics,
    target_semantics: ReferenceSemantics,
    *,
    source_rate_hz: float,
    target_rate_hz: float,
    source_current_states: np.ndarray,
    source_chunk_anchor: np.ndarray | None = None,
    source_initial_previous_command: np.ndarray | None = None,
    source_controller_targets_before: np.ndarray | None = None,
    target_current_states: np.ndarray | None = None,
    target_chunk_anchor: np.ndarray | None = None,
    target_initial_previous_command: np.ndarray | None = None,
    target_controller_targets_before: np.ndarray | None = None,
) -> RateTransportCertificate:
    """Compile a semantic rate adapter under a declared ZOH physical-goal contract.

    The physical contract is: each source absolute goal is held for r target
    controller ticks.  This is a goal-trace certificate, not a dynamics or
    smoothness guarantee.
    """
    ratio = _integer_rate_ratio(source_rate_hz, target_rate_hz)
    src_actions = np.asarray(source_actions, dtype=float)
    src_states = np.asarray(source_current_states, dtype=float)
    decoded = decode_reference_trace(
        src_actions,
        source_semantics,
        current_states=src_states,
        chunk_anchor=source_chunk_anchor,
        initial_previous_command=source_initial_previous_command,
        controller_targets_before=source_controller_targets_before,
    )
    refined_goals = zoh_refine_goals(decoded.goals, ratio)
    deployability = target_rate_deployability(target_semantics.kind)

    if deployability is RateDeployability.REQUIRES_STEP_HOOK:
        if target_current_states is None and target_semantics.kind is ReferenceKind.CURRENT_STATE:
            return RateTransportCertificate(
                source_rate_hz=source_rate_hz,
                target_rate_hz=target_rate_hz,
                integer_ratio=ratio,
                deployability=deployability,
                refined_goals=refined_goals,
                target_actions=None,
                target_references=None,
                source_boundary_goals=decoded.goals,
                target_boundary_goals=None,
                max_boundary_goal_error=None,
                naive_repeat_boundary_error=_naive_repeat_error(
                    src_actions,
                    target_semantics,
                    ratio,
                    source_current_states=src_states,
                    target_current_states=None,
                    target_chunk_anchor=target_chunk_anchor,
                    target_initial_previous_command=target_initial_previous_command,
                    target_controller_targets_before=target_controller_targets_before,
                ),
                reason="future target current states are required at target-rate execution steps",
            )
        if (
            target_controller_targets_before is None
            and target_semantics.kind is ReferenceKind.CONTROLLER_TARGET
        ):
            return RateTransportCertificate(
                source_rate_hz=source_rate_hz,
                target_rate_hz=target_rate_hz,
                integer_ratio=ratio,
                deployability=deployability,
                refined_goals=refined_goals,
                target_actions=None,
                target_references=None,
                source_boundary_goals=decoded.goals,
                target_boundary_goals=None,
                max_boundary_goal_error=None,
                naive_repeat_boundary_error=None,
                reason="future target controller-owned reference is required",
            )

    if target_current_states is None:
        # Precomputable semantics do not use measured state numerically, but the
        # shared encoder API requires a shape-matched state array.
        target_states = np.zeros_like(refined_goals)
    else:
        target_states = np.asarray(target_current_states, dtype=float)
        if target_states.shape != refined_goals.shape:
            raise ValueError("target_current_states must match refined goal shape")

    target_actions, target_refs = encode_goals_with_reference(
        refined_goals,
        target_semantics,
        current_states=target_states,
        chunk_anchor=target_chunk_anchor,
        initial_previous_command=target_initial_previous_command,
        controller_targets_before=target_controller_targets_before,
    )
    target_decoded = decode_reference_trace(
        target_actions,
        target_semantics,
        current_states=target_states,
        chunk_anchor=target_chunk_anchor,
        initial_previous_command=target_initial_previous_command,
        controller_targets_before=target_controller_targets_before,
    )
    idx = boundary_indices(len(decoded.goals), ratio)
    boundary = target_decoded.goals[idx]
    error = float(np.max(np.abs(boundary - decoded.goals))) if len(idx) else 0.0

    return RateTransportCertificate(
        source_rate_hz=source_rate_hz,
        target_rate_hz=target_rate_hz,
        integer_ratio=ratio,
        deployability=deployability,
        refined_goals=refined_goals,
        target_actions=target_actions,
        target_references=target_refs,
        source_boundary_goals=decoded.goals,
        target_boundary_goals=boundary,
        max_boundary_goal_error=error,
        naive_repeat_boundary_error=_naive_repeat_error(
            src_actions,
            target_semantics,
            ratio,
            source_current_states=src_states,
            target_current_states=target_states,
            target_chunk_anchor=target_chunk_anchor,
            target_initial_previous_command=target_initial_previous_command,
            target_controller_targets_before=target_controller_targets_before,
        ),
        reason="semantic re-encoding preserves the declared source goal at each source-rate boundary",
    )


def _naive_repeat_error(
    source_actions: np.ndarray,
    target_semantics: ReferenceSemantics,
    ratio: int,
    *,
    source_current_states: np.ndarray,
    target_current_states: np.ndarray | None,
    target_chunk_anchor: np.ndarray | None,
    target_initial_previous_command: np.ndarray | None,
    target_controller_targets_before: np.ndarray | None,
) -> float | None:
    """Diagnostic only: decode repeated numeric source actions as target actions."""
    repeated = np.repeat(np.asarray(source_actions, dtype=float), ratio, axis=0)
    D = repeated.shape[1]
    if target_current_states is None:
        if target_semantics.kind in (
            ReferenceKind.CURRENT_STATE,
            ReferenceKind.CONTROLLER_TARGET,
        ):
            return None
        states = np.zeros((len(repeated), D))
    else:
        states = np.asarray(target_current_states, dtype=float)
        if states.shape != repeated.shape:
            return None

    try:
        decoded = decode_reference_trace(
            repeated,
            target_semantics,
            current_states=states,
            chunk_anchor=target_chunk_anchor,
            initial_previous_command=target_initial_previous_command,
            controller_targets_before=target_controller_targets_before,
        )
    except ValueError:
        return None

    # Compare the repeated-action goal at each source boundary with the source
    # action interpreted only as a numeric diagnostic.  This is deliberately
    # not presented as source semantic equivalence.
    idx = boundary_indices(len(source_actions), ratio)
    if target_semantics.kind is ReferenceKind.PREVIOUS_COMMAND:
        # The accumulation pathology is directly meaningful here.
        first = decoded.goals[idx]
        # Expected one application per source action under the same previous-command chain.
        base_states = np.zeros_like(source_actions)
        try:
            expected = decode_reference_trace(
                np.asarray(source_actions, dtype=float),
                target_semantics,
                current_states=base_states,
                chunk_anchor=target_chunk_anchor,
                initial_previous_command=target_initial_previous_command,
            ).goals
            return float(np.max(np.abs(first - expected)))
        except ValueError:
            return None
    return None
