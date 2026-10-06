from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from reference_semantics import ReferenceKind


class AdapterPhase(str, Enum):
    QUERY_TIME = "query_time"
    STEP_TIME = "step_time"


class CausalStatus(str, Enum):
    PRECOMPUTABLE = "precomputable"
    REQUIRES_STEP_HOOK = "requires_step_hook"
    EXECUTABLE_WITH_STEP_HOOK = "executable_with_step_hook"
    REFUSE_MISSING_RUNTIME_STATE = "refuse_missing_runtime_state"


@dataclass(frozen=True)
class CausalTransportCertificate:
    status: CausalStatus
    requested_phase: AdapterPhase
    horizon: int
    earliest_unavailable_step: int | None
    source_goal_available_at: tuple[int, ...]
    target_reference_available_at: tuple[int, ...]
    target_action_available_at: tuple[int, ...]
    requires_physical_state: bool
    requires_controller_target: bool
    minimum_phase: AdapterPhase
    reason: str


def _reference_availability(
    kind: ReferenceKind,
    *,
    horizon: int,
    query_step: int,
) -> tuple[int, ...]:
    """Earliest logical step at which each reference is known.

    query_step is the time at which a policy chunk is emitted. We use logical
    step indices rather than wall-clock time.

    ABSOLUTE has no reference and is available at query time.
    CHUNK_ANCHOR is captured at query time.
    PREVIOUS_COMMAND can be reconstructed recursively from an already available
    anchor and the action sequence, so its reference is query-time available
    for an offline/native chunk transform.
    CURRENT_STATE and CONTROLLER_TARGET for future actions are only known when
    that future step executes.
    """
    if kind in {
        ReferenceKind.ABSOLUTE,
        ReferenceKind.CHUNK_ANCHOR,
        ReferenceKind.PREVIOUS_COMMAND,
    }:
        return tuple(query_step for _ in range(horizon))
    if kind in {
        ReferenceKind.CURRENT_STATE,
        ReferenceKind.CONTROLLER_TARGET,
    }:
        return tuple(query_step + t for t in range(horizon))
    raise AssertionError(kind)


def analyze_chunk_transport_causality(
    source_kind: ReferenceKind,
    target_kind: ReferenceKind,
    *,
    horizon: int,
    requested_phase: AdapterPhase = AdapterPhase.QUERY_TIME,
    step_hook_has_physical_state: bool = True,
    step_hook_has_controller_target: bool = True,
    query_step: int = 0,
) -> CausalTransportCertificate:
    """Determine when an exact reference-semantic action transform can execute.

    The checker distinguishes offline trace convertibility from online causal
    deployability. A future current-state-relative action can be reconstructed
    after a rollout, but cannot in general be precomputed when a frozen policy
    first emits the whole action chunk.

    This function reasons only about information availability. Numeric
    representability such as bounds and saturation remains a separate CST
    obligation.
    """
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    source_ref = _reference_availability(
        source_kind, horizon=horizon, query_step=query_step
    )
    target_ref = _reference_availability(
        target_kind, horizon=horizon, query_step=query_step
    )

    source_goal = source_ref
    target_action = tuple(
        max(source_goal[t], target_ref[t]) for t in range(horizon)
    )

    requires_physical = (
        source_kind is ReferenceKind.CURRENT_STATE
        or target_kind is ReferenceKind.CURRENT_STATE
    )
    requires_target = (
        source_kind is ReferenceKind.CONTROLLER_TARGET
        or target_kind is ReferenceKind.CONTROLLER_TARGET
    )

    future_dependencies = [
        t for t, available in enumerate(target_action) if available > query_step
    ]
    minimum_phase = (
        AdapterPhase.STEP_TIME if future_dependencies else AdapterPhase.QUERY_TIME
    )

    if requested_phase is AdapterPhase.QUERY_TIME:
        if future_dependencies:
            first = future_dependencies[0]
            return CausalTransportCertificate(
                status=CausalStatus.REQUIRES_STEP_HOOK,
                requested_phase=requested_phase,
                horizon=horizon,
                earliest_unavailable_step=first,
                source_goal_available_at=source_goal,
                target_reference_available_at=target_ref,
                target_action_available_at=target_action,
                requires_physical_state=requires_physical,
                requires_controller_target=requires_target,
                minimum_phase=minimum_phase,
                reason=(
                    "at least one future target action depends on state owned by "
                    "a future execution step and cannot be precomputed when the "
                    "policy chunk is emitted"
                ),
            )
        return CausalTransportCertificate(
            status=CausalStatus.PRECOMPUTABLE,
            requested_phase=requested_phase,
            horizon=horizon,
            earliest_unavailable_step=None,
            source_goal_available_at=source_goal,
            target_reference_available_at=target_ref,
            target_action_available_at=target_action,
            requires_physical_state=requires_physical,
            requires_controller_target=requires_target,
            minimum_phase=minimum_phase,
            reason="all reference dependencies are available at chunk query time",
        )

    if requires_physical and not step_hook_has_physical_state:
        return CausalTransportCertificate(
            status=CausalStatus.REFUSE_MISSING_RUNTIME_STATE,
            requested_phase=requested_phase,
            horizon=horizon,
            earliest_unavailable_step=0,
            source_goal_available_at=source_goal,
            target_reference_available_at=target_ref,
            target_action_available_at=target_action,
            requires_physical_state=requires_physical,
            requires_controller_target=requires_target,
            minimum_phase=minimum_phase,
            reason="step-time adapter cannot observe required physical state",
        )
    if requires_target and not step_hook_has_controller_target:
        return CausalTransportCertificate(
            status=CausalStatus.REFUSE_MISSING_RUNTIME_STATE,
            requested_phase=requested_phase,
            horizon=horizon,
            earliest_unavailable_step=0,
            source_goal_available_at=source_goal,
            target_reference_available_at=target_ref,
            target_action_available_at=target_action,
            requires_physical_state=requires_physical,
            requires_controller_target=requires_target,
            minimum_phase=minimum_phase,
            reason="step-time adapter cannot observe required controller target state",
        )

    return CausalTransportCertificate(
        status=CausalStatus.EXECUTABLE_WITH_STEP_HOOK,
        requested_phase=requested_phase,
        horizon=horizon,
        earliest_unavailable_step=None,
        source_goal_available_at=source_goal,
        target_reference_available_at=target_ref,
        target_action_available_at=target_action,
        requires_physical_state=requires_physical,
        requires_controller_target=requires_target,
        minimum_phase=minimum_phase,
        reason="all future reference dependencies are available no later than execution",
    )
