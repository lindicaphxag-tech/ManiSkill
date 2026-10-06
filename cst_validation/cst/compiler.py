from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .core import (
    JointControllerContext,
    JointGoalChart,
    MissingControllerStateError,
)


CompileStatus = Literal["exact", "ambiguous", "nonrepresentable"]


@dataclass(frozen=True)
class ExactTransportResult:
    status: Literal["exact"]
    source_goal: np.ndarray
    target_action: np.ndarray
    decoded_target_goal: np.ndarray
    semantic_residual: float
    required_source_state: tuple[str, ...]
    required_target_state: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class AmbiguousTransportWitness:
    status: Literal["ambiguous"]
    missing_source_state: tuple[str, ...]
    source_action: np.ndarray
    witness_context_a: JointControllerContext | None
    witness_context_b: JointControllerContext | None
    witness_goal_a: np.ndarray | None
    witness_goal_b: np.ndarray | None
    reason: str


@dataclass(frozen=True)
class NonRepresentableTransportWitness:
    status: Literal["nonrepresentable"]
    source_goal: np.ndarray
    target_reference: np.ndarray | None
    required_native_action: np.ndarray
    violating_coordinates: tuple[int, ...]
    lower_native_bound: float
    upper_native_bound: float
    reason: str


CompiledTransport = (
    ExactTransportResult
    | AmbiguousTransportWitness
    | NonRepresentableTransportWitness
)


def _state_requirements(chart: JointGoalChart) -> tuple[str, ...]:
    if chart.mode == "absolute":
        return ()
    if chart.mode == "delta_current":
        return ("q_current",)
    if chart.mode == "delta_target":
        return ("q_target",)
    if chart.mode == "relative_latched":
        return ("q_latched",)
    raise ValueError(f"unsupported chart mode: {chart.mode}")


def _missing(
    context: JointControllerContext,
    requirements: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(name for name in requirements if getattr(context, name) is None)


def _ambiguous_joint_witness(
    chart: JointGoalChart,
    action: np.ndarray,
    missing: tuple[str, ...],
) -> AmbiguousTransportWitness:
    """Construct an explicit hidden-state ambiguity witness for joint deltas."""
    action = np.asarray(action, dtype=float)
    if len(missing) != 1:
        return AmbiguousTransportWitness(
            status="ambiguous",
            missing_source_state=missing,
            source_action=action,
            witness_context_a=None,
            witness_context_b=None,
            witness_goal_a=None,
            witness_goal_b=None,
            reason="source semantic decoding requires unobserved controller state",
        )

    name = missing[0]
    zeros = np.zeros_like(action)
    shifted = np.full_like(action, 0.37)
    if name == "q_current":
        ca = JointControllerContext(q_current=zeros)
        cb = JointControllerContext(q_current=shifted)
    elif name == "q_target":
        ca = JointControllerContext(q_target=zeros)
        cb = JointControllerContext(q_target=shifted)
    elif name == "q_latched":
        ca = JointControllerContext(q_latched=zeros)
        cb = JointControllerContext(q_latched=shifted)
    else:
        return AmbiguousTransportWitness(
            status="ambiguous",
            missing_source_state=missing,
            source_action=action,
            witness_context_a=None,
            witness_context_b=None,
            witness_goal_a=None,
            witness_goal_b=None,
            reason=f"no constructive witness implemented for hidden state {name}",
        )

    ga = chart.decode(action, ca)
    gb = chart.decode(action, cb)
    if np.allclose(ga, gb, atol=1e-12, rtol=0.0):
        raise RuntimeError("constructed ambiguity witness did not change source semantics")
    return AmbiguousTransportWitness(
        status="ambiguous",
        missing_source_state=missing,
        source_action=action,
        witness_context_a=ca,
        witness_context_b=cb,
        witness_goal_a=ga,
        witness_goal_b=gb,
        reason=(
            f"same recorded source action is compatible with distinct {name} "
            "values and therefore distinct physical joint goals"
        ),
    )


def compile_exact_joint_transport(
    *,
    source_chart: JointGoalChart,
    target_chart: JointGoalChart,
    source_action: np.ndarray,
    source_context: JointControllerContext,
    target_context: JointControllerContext,
    tolerance: float = 1e-10,
) -> CompiledTransport:
    """Compile an E1-exact joint transport or return a constructive witness.

    This implements the finite-dimensional joint-chart form of the CST
    exactness theorem:

      exact E1 transport exists for the recorded boundary
      iff
      (i) source semantics are identifiable from the available source context,
      and
      (ii) the unique source semantic goal lies in the target chart image for
           the available target context.

    No E2/E3/E4 claim is implied.
    """
    action = np.asarray(source_action, dtype=float)
    if action.ndim != 1 or action.size == 0 or not np.all(np.isfinite(action)):
        raise ValueError("source_action must be a finite non-empty 1D array")
    if tolerance < 0 or not np.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative")

    source_req = _state_requirements(source_chart)
    target_req = _state_requirements(target_chart)
    missing_source = _missing(source_context, source_req)
    if missing_source:
        return _ambiguous_joint_witness(source_chart, action, missing_source)

    missing_target = _missing(target_context, target_req)
    if missing_target:
        return AmbiguousTransportWitness(
            status="ambiguous",
            missing_source_state=tuple(f"target.{x}" for x in missing_target),
            source_action=action,
            witness_context_a=None,
            witness_context_b=None,
            witness_goal_a=None,
            witness_goal_b=None,
            reason=(
                "target encoding is not uniquely determined because required "
                "target controller reference state is unavailable"
            ),
        )

    source_goal = source_chart.decode(action, source_context)

    # encode() is the target image-membership oracle for these charts.  It
    # returns the unclipped native action and an explicit representability flag.
    encoded = target_chart.encode(source_goal, target_context)
    if not encoded.representable:
        violating = tuple(
            int(i) for i in np.flatnonzero(np.abs(encoded.action) > 1.0 + tolerance)
        )
        target_reference = None
        if target_chart.mode == "delta_current":
            target_reference = np.asarray(target_context.q_current, dtype=float)
        elif target_chart.mode == "delta_target":
            target_reference = np.asarray(target_context.q_target, dtype=float)
        elif target_chart.mode == "relative_latched":
            target_reference = np.asarray(target_context.q_latched, dtype=float)

        return NonRepresentableTransportWitness(
            status="nonrepresentable",
            source_goal=source_goal,
            target_reference=target_reference,
            required_native_action=encoded.action,
            violating_coordinates=violating,
            lower_native_bound=-1.0,
            upper_native_bound=1.0,
            reason=(
                "unique source semantic goal lies outside the target chart's "
                "one-step native action image"
            ),
        )

    decoded = target_chart.decode(encoded.action, target_context)
    residual = float(np.max(np.abs(decoded - source_goal)))
    if residual > tolerance:
        raise RuntimeError(
            "target chart claimed representability but round-trip semantic "
            f"residual {residual:.6g} exceeds tolerance {tolerance:.6g}"
        )

    return ExactTransportResult(
        status="exact",
        source_goal=source_goal,
        target_action=encoded.action,
        decoded_target_goal=decoded,
        semantic_residual=residual,
        required_source_state=source_req,
        required_target_state=target_req,
        reason="source semantics are identifiable and lie in the target chart image",
    )
