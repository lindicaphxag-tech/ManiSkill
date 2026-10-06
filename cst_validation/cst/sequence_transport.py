from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .core import (
    EncodeResult,
    JointControllerContext,
    JointGoalChart,
    MissingControllerStateError,
)


SequenceTransportStatus = Literal["exact", "ambiguous", "nonrepresentable"]


@dataclass(frozen=True)
class SequenceTransportWitness:
    status: SequenceTransportStatus
    target_actions: np.ndarray | None
    semantic_goals: np.ndarray | None
    failure_step: int | None
    required_source_state: tuple[str, ...]
    required_target_state: tuple[str, ...]
    target_saturation: np.ndarray | None
    reason: str


def _actions(value: np.ndarray) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise ValueError("source_actions must have non-empty shape [T, D]")
    if not np.all(np.isfinite(out)):
        raise ValueError("source_actions must be finite")
    return out


def _trace(
    value: np.ndarray | None,
    *,
    length: int,
    dim: int,
    name: str,
) -> np.ndarray | None:
    if value is None:
        return None
    out = np.asarray(value, dtype=float)
    if out.shape != (length, dim) or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite with shape {(length, dim)}")
    return out


def _initial_vector(
    value: np.ndarray | None,
    *,
    dim: int,
    name: str,
) -> np.ndarray | None:
    if value is None:
        return None
    out = np.asarray(value, dtype=float)
    if out.shape != (dim,) or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite with shape {(dim,)}")
    return out.copy()


def _missing_sequence_state(
    chart: JointGoalChart,
    initial_context: JointControllerContext,
    q_current_trace: np.ndarray | None,
    *,
    side: str,
) -> tuple[str, ...]:
    if chart.mode == "absolute":
        return ()
    if chart.mode == "delta_current":
        return () if q_current_trace is not None else (f"{side}.q_current_trace",)
    if chart.mode == "delta_target":
        return () if initial_context.q_target is not None else (f"{side}.q_target",)
    if chart.mode == "relative_latched":
        return () if initial_context.q_latched is not None else (f"{side}.q_latched",)
    raise ValueError(f"unsupported chart mode: {chart.mode}")


def _context_at(
    chart: JointGoalChart,
    *,
    step: int,
    q_current_trace: np.ndarray | None,
    q_target: np.ndarray | None,
    q_latched: np.ndarray | None,
) -> JointControllerContext:
    if chart.mode == "absolute":
        return JointControllerContext()
    if chart.mode == "delta_current":
        if q_current_trace is None:
            raise MissingControllerStateError("delta_current requires q_current_trace")
        return JointControllerContext(q_current=q_current_trace[step])
    if chart.mode == "delta_target":
        if q_target is None:
            raise MissingControllerStateError("delta_target requires initial q_target")
        return JointControllerContext(q_target=q_target)
    if chart.mode == "relative_latched":
        if q_latched is None:
            raise MissingControllerStateError("relative_latched requires q_latched")
        return JointControllerContext(q_latched=q_latched)
    raise ValueError(f"unsupported chart mode: {chart.mode}")


def compile_joint_sequence_transport(
    *,
    source_chart: JointGoalChart,
    target_chart: JointGoalChart,
    source_actions: np.ndarray,
    source_initial_context: JointControllerContext,
    target_initial_context: JointControllerContext,
    source_q_current_trace: np.ndarray | None = None,
    target_q_current_trace: np.ndarray | None = None,
) -> SequenceTransportWitness:
    """Compile one action sequence through shared physical joint-goal semantics.

    The compiler treats reference semantics as state machines:

    - absolute: no reference state;
    - delta_current: exogenous q_current[t] is required every step;
    - delta_target: q_target is endogenous and advances to each decoded goal;
    - relative_latched: one q_latched is fixed for the whole chunk.

    It never uses target clipping as evidence of exact conversion. The first
    out-of-image target step returns a constructive nonrepresentability witness.
    """
    native = _actions(source_actions)
    length, dim = native.shape
    source_trace = _trace(
        source_q_current_trace,
        length=length,
        dim=dim,
        name="source_q_current_trace",
    )
    target_trace = _trace(
        target_q_current_trace,
        length=length,
        dim=dim,
        name="target_q_current_trace",
    )

    source_missing = _missing_sequence_state(
        source_chart,
        source_initial_context,
        source_trace,
        side="source",
    )
    target_missing = _missing_sequence_state(
        target_chart,
        target_initial_context,
        target_trace,
        side="target",
    )
    if source_missing or target_missing:
        return SequenceTransportWitness(
            status="ambiguous",
            target_actions=None,
            semantic_goals=None,
            failure_step=None,
            required_source_state=source_missing,
            required_target_state=target_missing,
            target_saturation=None,
            reason=(
                "exact sequence transport is not identifiable because required "
                "controller reference state is missing"
            ),
        )

    source_target = _initial_vector(
        source_initial_context.q_target,
        dim=dim,
        name="source q_target",
    )
    target_target = _initial_vector(
        target_initial_context.q_target,
        dim=dim,
        name="target q_target",
    )
    source_latch = _initial_vector(
        source_initial_context.q_latched,
        dim=dim,
        name="source q_latched",
    )
    target_latch = _initial_vector(
        target_initial_context.q_latched,
        dim=dim,
        name="target q_latched",
    )

    target_actions: list[np.ndarray] = []
    semantic_goals: list[np.ndarray] = []

    for step, source_action in enumerate(native):
        source_context = _context_at(
            source_chart,
            step=step,
            q_current_trace=source_trace,
            q_target=source_target,
            q_latched=source_latch,
        )
        goal = source_chart.decode(source_action, source_context)

        target_context = _context_at(
            target_chart,
            step=step,
            q_current_trace=target_trace,
            q_target=target_target,
            q_latched=target_latch,
        )
        encoded: EncodeResult = target_chart.encode(goal, target_context)
        if not encoded.representable:
            return SequenceTransportWitness(
                status="nonrepresentable",
                target_actions=(
                    np.stack(target_actions, axis=0)
                    if target_actions
                    else np.empty((0, dim), dtype=float)
                ),
                semantic_goals=(
                    np.stack(semantic_goals, axis=0)
                    if semantic_goals
                    else np.empty((0, dim), dtype=float)
                ),
                failure_step=step,
                required_source_state=(),
                required_target_state=(),
                target_saturation=encoded.saturation.copy(),
                reason=(
                    f"semantic goal at step {step} lies outside the target "
                    "controller action image"
                ),
            )

        reconstructed = target_chart.decode(encoded.action, target_context)
        if not np.allclose(reconstructed, goal, atol=1e-10, rtol=0.0):
            raise RuntimeError("target chart failed exact semantic round trip")

        target_actions.append(encoded.action.copy())
        semantic_goals.append(goal.copy())

        if source_chart.mode == "delta_target":
            source_target = goal.copy()
        if target_chart.mode == "delta_target":
            target_target = goal.copy()

    return SequenceTransportWitness(
        status="exact",
        target_actions=np.stack(target_actions, axis=0),
        semantic_goals=np.stack(semantic_goals, axis=0),
        failure_step=None,
        required_source_state=(),
        required_target_state=(),
        target_saturation=np.zeros(dim, dtype=bool),
        reason="all sequence steps preserve the shared physical joint-goal semantics",
    )
