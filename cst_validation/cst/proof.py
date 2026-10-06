from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

import numpy as np

from .compiler import ExactTransportResult, compile_exact_joint_transport
from .core import JointControllerContext, JointGoalChart


@dataclass(frozen=True)
class JointTransportProof:
    """Proof-carrying record for one exact E1 controller transport.

    The record binds the compiled target action to the exact source/target chart
    definitions and controller-reference states used during compilation.
    """

    schema_version: str
    source_chart_digest: str
    target_chart_digest: str
    source_context_digest: str
    target_context_digest: str
    source_action: np.ndarray
    target_action: np.ndarray
    semantic_goal: np.ndarray
    compiler_residual: float
    proof_id: str


@dataclass(frozen=True)
class JointTransportVerification:
    valid: bool
    source_goal_residual: float
    target_goal_residual: float
    cross_goal_residual: float
    identity_match: bool
    target_native_representable: bool
    reason: str


def _array_or_none(value):
    if value is None:
        return None
    return np.asarray(value, dtype=float).tolist()


def _chart_payload(chart: JointGoalChart) -> dict:
    return {
        "mode": chart.mode,
        "normalized": bool(chart.normalized),
        "lower": _array_or_none(chart.lower),
        "upper": _array_or_none(chart.upper),
    }


def _context_payload(context: JointControllerContext) -> dict:
    return {
        "q_current": _array_or_none(context.q_current),
        "q_target": _array_or_none(context.q_target),
    }


def _digest(payload: dict) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def joint_chart_digest(chart: JointGoalChart) -> str:
    return _digest(_chart_payload(chart))


def joint_context_digest(context: JointControllerContext) -> str:
    return _digest(_context_payload(context))


def _proof_id(
    *,
    source_chart_digest: str,
    target_chart_digest: str,
    source_context_digest: str,
    target_context_digest: str,
    source_action: np.ndarray,
    target_action: np.ndarray,
    semantic_goal: np.ndarray,
) -> str:
    payload = {
        "schema_version": "cst-joint-proof-v0",
        "source_chart_digest": source_chart_digest,
        "target_chart_digest": target_chart_digest,
        "source_context_digest": source_context_digest,
        "target_context_digest": target_context_digest,
        "source_action": np.asarray(source_action, dtype=float).tolist(),
        "target_action": np.asarray(target_action, dtype=float).tolist(),
        "semantic_goal": np.asarray(semantic_goal, dtype=float).tolist(),
    }
    return _digest(payload)


def emit_exact_joint_transport_proof(
    *,
    source_chart: JointGoalChart,
    target_chart: JointGoalChart,
    source_action: np.ndarray,
    source_context: JointControllerContext,
    target_context: JointControllerContext,
    tolerance: float = 1e-10,
) -> JointTransportProof:
    """Compile one exact transport and bind it to chart/context identities."""
    result = compile_exact_joint_transport(
        source_chart=source_chart,
        target_chart=target_chart,
        source_action=source_action,
        source_context=source_context,
        target_context=target_context,
        tolerance=tolerance,
    )
    if not isinstance(result, ExactTransportResult):
        raise ValueError(
            f"cannot emit an exact proof for compiler status {result.status}: "
            f"{result.reason}"
        )

    sc = joint_chart_digest(source_chart)
    tc = joint_chart_digest(target_chart)
    sx = joint_context_digest(source_context)
    tx = joint_context_digest(target_context)
    source = np.asarray(source_action, dtype=float).copy()
    target = np.asarray(result.target_action, dtype=float).copy()
    goal = np.asarray(result.source_goal, dtype=float).copy()
    return JointTransportProof(
        schema_version="cst-joint-proof-v0",
        source_chart_digest=sc,
        target_chart_digest=tc,
        source_context_digest=sx,
        target_context_digest=tx,
        source_action=source,
        target_action=target,
        semantic_goal=goal,
        compiler_residual=float(result.semantic_residual),
        proof_id=_proof_id(
            source_chart_digest=sc,
            target_chart_digest=tc,
            source_context_digest=sx,
            target_context_digest=tx,
            source_action=source,
            target_action=target,
            semantic_goal=goal,
        ),
    )


def _vec(value, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 1 or out.size == 0 or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be a finite non-empty 1D array")
    return out


def _bounds(chart: JointGoalChart, dim: int):
    if chart.lower is None and chart.upper is None:
        return None, None
    if chart.lower is None or chart.upper is None:
        raise ValueError("chart lower/upper bounds must be provided together")
    low = np.broadcast_to(np.asarray(chart.lower, dtype=float), (dim,))
    high = np.broadcast_to(np.asarray(chart.upper, dtype=float), (dim,))
    return low, high


def _independent_decode(
    chart: JointGoalChart,
    action: np.ndarray,
    context: JointControllerContext,
) -> tuple[np.ndarray, np.ndarray]:
    """Verifier-side decode that does not call JointGoalChart.decode."""
    native = _vec(action, "native action")
    low, high = _bounds(chart, native.size)
    if chart.normalized:
        if low is None:
            raise ValueError("normalized chart requires physical bounds")
        physical = (
            0.5 * (high + low)
            + 0.5 * (high - low) * np.clip(native, -1.0, 1.0)
        )
    else:
        physical = native.copy()

    if chart.mode == "absolute":
        return physical, physical
    if chart.mode == "delta_current":
        if context.q_current is None:
            raise ValueError("delta_current verifier requires q_current")
        reference = _vec(context.q_current, "q_current")
    elif chart.mode == "delta_target":
        if context.q_target is None:
            raise ValueError("delta_target verifier requires q_target")
        reference = _vec(context.q_target, "q_target")
    else:
        raise ValueError(f"unsupported chart mode: {chart.mode}")
    if reference.shape != physical.shape:
        raise ValueError("controller reference dimension mismatch")
    return reference + physical, physical


def verify_exact_joint_transport_proof(
    proof: JointTransportProof,
    *,
    source_chart: JointGoalChart,
    target_chart: JointGoalChart,
    source_context: JointControllerContext,
    target_context: JointControllerContext,
    tolerance: float = 1e-10,
) -> JointTransportVerification:
    """Independently verify a CST exact-transport proof.

    The verifier never invokes the CST compiler. It re-evaluates the controller
    semantics from chart parameters and rejects chart/context identity drift.
    """
    if proof.schema_version != "cst-joint-proof-v0":
        return JointTransportVerification(
            False, float("inf"), float("inf"), float("inf"), False, False,
            "unsupported proof schema",
        )
    identity_match = (
        proof.source_chart_digest == joint_chart_digest(source_chart)
        and proof.target_chart_digest == joint_chart_digest(target_chart)
        and proof.source_context_digest == joint_context_digest(source_context)
        and proof.target_context_digest == joint_context_digest(target_context)
    )
    expected_proof_id = _proof_id(
        source_chart_digest=proof.source_chart_digest,
        target_chart_digest=proof.target_chart_digest,
        source_context_digest=proof.source_context_digest,
        target_context_digest=proof.target_context_digest,
        source_action=proof.source_action,
        target_action=proof.target_action,
        semantic_goal=proof.semantic_goal,
    )
    identity_match = identity_match and proof.proof_id == expected_proof_id

    try:
        source_goal, _ = _independent_decode(
            source_chart, proof.source_action, source_context
        )
        target_goal, target_physical = _independent_decode(
            target_chart, proof.target_action, target_context
        )
    except ValueError as exc:
        return JointTransportVerification(
            False, float("inf"), float("inf"), float("inf"), identity_match, False,
            f"verifier could not decode controller semantics: {exc}",
        )

    goal = _vec(proof.semantic_goal, "semantic_goal")
    if source_goal.shape != goal.shape or target_goal.shape != goal.shape:
        return JointTransportVerification(
            False, float("inf"), float("inf"), float("inf"), identity_match, False,
            "semantic dimensions do not match proof",
        )

    source_residual = float(np.max(np.abs(source_goal - goal)))
    target_residual = float(np.max(np.abs(target_goal - goal)))
    cross_residual = float(np.max(np.abs(source_goal - target_goal)))

    low, high = _bounds(target_chart, target_physical.size)
    target_representable = True
    if target_chart.normalized:
        target_representable = bool(
            np.all(np.asarray(proof.target_action) >= -1.0 - tolerance)
            and np.all(np.asarray(proof.target_action) <= 1.0 + tolerance)
        )
    elif low is not None:
        target_representable = bool(
            np.all(target_physical >= low - tolerance)
            and np.all(target_physical <= high + tolerance)
        )

    valid = (
        identity_match
        and target_representable
        and source_residual <= tolerance
        and target_residual <= tolerance
        and cross_residual <= tolerance
    )
    if not identity_match:
        reason = "proof identity does not match current chart/context or proof payload"
    elif not target_representable:
        reason = "target native action is outside the declared target chart image"
    elif not valid:
        reason = "independent semantic reconstruction exceeds tolerance"
    else:
        reason = "independent verifier confirms exact semantic transport"

    return JointTransportVerification(
        valid=valid,
        source_goal_residual=source_residual,
        target_goal_residual=target_residual,
        cross_goal_residual=cross_residual,
        identity_match=identity_match,
        target_native_representable=target_representable,
        reason=reason,
    )
