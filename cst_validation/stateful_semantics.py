from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class JointCommandMode(str, Enum):
    """Controller-level semantics for a joint-position command."""

    ABSOLUTE = "absolute"
    DELTA_CURRENT = "delta_current"
    DELTA_TARGET = "delta_target"


@dataclass(frozen=True)
class JointCommandContract:
    """Minimal semantic contract for joint-position controller actions.

    lower / upper describe the physical command range when normalized=True.
    For ABSOLUTE controllers they are absolute joint limits; for delta modes
    they are physical delta limits.
    """

    mode: JointCommandMode
    normalize_action: bool
    lower: np.ndarray | None = None
    upper: np.ndarray | None = None


@dataclass(frozen=True)
class JointControllerState:
    """Physical state needed to interpret a controller command."""

    current_qpos: np.ndarray
    target_qpos: np.ndarray


@dataclass(frozen=True)
class JointTransportCertificate:
    """Proof-carrying one-step transport between controller semantic charts."""

    exact: bool
    source_target_qpos: np.ndarray
    target_target_qpos: np.ndarray
    target_native_action: np.ndarray
    representable_mask: np.ndarray
    target_residual: np.ndarray
    max_abs_residual: float
    source_requires_target_state: bool
    target_requires_target_state: bool
    reason: str


def _vector(value, *, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 1 or out.size == 0:
        raise ValueError(f"{name} must be a non-empty vector")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _bounds(contract: JointCommandContract, dim: int) -> tuple[np.ndarray, np.ndarray]:
    if contract.lower is None or contract.upper is None:
        raise ValueError("normalized controller requires physical lower/upper bounds")
    low = np.broadcast_to(np.asarray(contract.lower, dtype=float), (dim,)).copy()
    high = np.broadcast_to(np.asarray(contract.upper, dtype=float), (dim,)).copy()
    if np.any(~np.isfinite(low)) or np.any(~np.isfinite(high)) or np.any(high <= low):
        raise ValueError("controller bounds must be finite with upper > lower")
    return low, high


def decode_native_action(
    contract: JointCommandContract,
    native_action: np.ndarray,
) -> np.ndarray:
    """Decode a controller-native action into its physical command vector."""
    action = _vector(native_action, name="native_action")
    if not contract.normalize_action:
        return action.copy()
    low, high = _bounds(contract, action.size)
    return 0.5 * (high + low) + 0.5 * (high - low) * np.clip(action, -1.0, 1.0)


def encode_physical_command(
    contract: JointCommandContract,
    physical_command: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Encode a physical command and report coordinate-wise representability."""
    command = _vector(physical_command, name="physical_command")
    if not contract.normalize_action:
        return command.copy(), np.ones(command.shape, dtype=bool)
    low, high = _bounds(contract, command.size)
    native = (command - 0.5 * (high + low)) / (0.5 * (high - low))
    representable = np.logical_and(native >= -1.0, native <= 1.0)
    return np.clip(native, -1.0, 1.0), representable


def command_to_target_qpos(
    contract: JointCommandContract,
    state: JointControllerState,
    native_action: np.ndarray,
) -> np.ndarray:
    """Interpret one native action as the physical target qpos it commands."""
    current = _vector(state.current_qpos, name="current_qpos")
    target = _vector(state.target_qpos, name="target_qpos")
    if current.shape != target.shape:
        raise ValueError("current_qpos and target_qpos must have identical shape")
    physical = decode_native_action(contract, native_action)
    if physical.shape != current.shape:
        raise ValueError("action dimension does not match controller state")

    if contract.mode is JointCommandMode.ABSOLUTE:
        return physical
    if contract.mode is JointCommandMode.DELTA_CURRENT:
        return current + physical
    if contract.mode is JointCommandMode.DELTA_TARGET:
        return target + physical
    raise AssertionError(contract.mode)


def target_qpos_to_native_action(
    contract: JointCommandContract,
    state: JointControllerState,
    desired_target_qpos: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Encode one desired physical target in the target controller semantics."""
    desired = _vector(desired_target_qpos, name="desired_target_qpos")
    current = _vector(state.current_qpos, name="current_qpos")
    previous_target = _vector(state.target_qpos, name="target_qpos")
    if desired.shape != current.shape or desired.shape != previous_target.shape:
        raise ValueError("desired target and controller state dimensions differ")

    if contract.mode is JointCommandMode.ABSOLUTE:
        physical = desired
    elif contract.mode is JointCommandMode.DELTA_CURRENT:
        physical = desired - current
    elif contract.mode is JointCommandMode.DELTA_TARGET:
        physical = desired - previous_target
    else:
        raise AssertionError(contract.mode)
    return encode_physical_command(contract, physical)


def compile_joint_transport(
    source_contract: JointCommandContract,
    target_contract: JointCommandContract,
    *,
    source_state: JointControllerState,
    target_state: JointControllerState,
    source_native_action: np.ndarray,
    atol: float = 1e-10,
) -> JointTransportCertificate:
    """Compile a one-step semantic transport and certify physical-target equality.

    The common semantic observable is the physical target joint configuration.
    Conversion is exact only if the desired source target is representable by
    the target controller under its *current hidden controller state*.
    """
    desired = command_to_target_qpos(
        source_contract,
        source_state,
        source_native_action,
    )
    target_native, representable = target_qpos_to_native_action(
        target_contract,
        target_state,
        desired,
    )
    reconstructed = command_to_target_qpos(
        target_contract,
        target_state,
        target_native,
    )
    residual = reconstructed - desired
    max_abs = float(np.max(np.abs(residual)))
    exact = bool(np.all(representable) and max_abs <= atol)
    if exact:
        reason = "target controller exactly represents the source physical target"
    elif not np.all(representable):
        reason = "source target lies outside the target controller representable set"
    else:
        reason = "target controller reconstruction exceeds the semantic residual limit"
    return JointTransportCertificate(
        exact=exact,
        source_target_qpos=desired,
        target_target_qpos=reconstructed,
        target_native_action=target_native,
        representable_mask=representable,
        target_residual=residual,
        max_abs_residual=max_abs,
        source_requires_target_state=source_contract.mode is JointCommandMode.DELTA_TARGET,
        target_requires_target_state=target_contract.mode is JointCommandMode.DELTA_TARGET,
        reason=reason,
    )


def advance_target_state(
    state: JointControllerState,
    commanded_target_qpos: np.ndarray,
    *,
    next_current_qpos: np.ndarray | None = None,
) -> JointControllerState:
    """Advance the semantic controller state after issuing one target."""
    target = _vector(commanded_target_qpos, name="commanded_target_qpos")
    current = (
        _vector(next_current_qpos, name="next_current_qpos")
        if next_current_qpos is not None
        else _vector(state.current_qpos, name="current_qpos")
    )
    if target.shape != current.shape:
        raise ValueError("next current qpos and target qpos dimensions differ")
    return JointControllerState(current_qpos=current, target_qpos=target)


@dataclass(frozen=True)
class JointTraceTransportCertificate:
    """Proof summary for a whole controller-action trajectory."""

    exact: bool
    exact_prefix_steps: int
    first_failure_step: int | None
    target_native_actions: np.ndarray
    source_target_trace: np.ndarray
    target_target_trace: np.ndarray
    max_abs_residual: float
    max_state_relation_error: float
    reason: str


def compile_joint_trace(
    source_contract: JointCommandContract,
    target_contract: JointCommandContract,
    *,
    initial_source_target_qpos: np.ndarray,
    initial_target_target_qpos: np.ndarray,
    current_qpos_trace: np.ndarray,
    source_native_actions: np.ndarray,
    atol: float = 1e-10,
) -> JointTraceTransportCertificate:
    """Compile a trajectory while preserving the controller target-state relation.

    current_qpos_trace[t] is the physical joint configuration at which the
    t-th source action is interpreted. For an exact transport, the target
    controller is required to share this physical state at the same step; this
    is the inductive premise later checked by native simulator replay.

    The compiler fails closed at the first unrepresentable target. It returns
    only the target actions in the exact prefix and never silently clips a
    non-equivalent remainder.
    """
    actions = np.asarray(source_native_actions, dtype=float)
    current = np.asarray(current_qpos_trace, dtype=float)
    if actions.ndim != 2 or current.ndim != 2:
        raise ValueError("actions and current_qpos_trace must have shape [T, D]")
    if actions.shape != current.shape:
        raise ValueError("actions and current_qpos_trace must have identical shape")
    if actions.shape[0] == 0:
        raise ValueError("trace must contain at least one action")

    source_target = _vector(
        initial_source_target_qpos, name="initial_source_target_qpos"
    )
    target_target = _vector(
        initial_target_target_qpos, name="initial_target_target_qpos"
    )
    if source_target.shape != (actions.shape[1],):
        raise ValueError("initial source target dimension mismatch")
    if target_target.shape != (actions.shape[1],):
        raise ValueError("initial target target dimension mismatch")

    compiled: list[np.ndarray] = []
    source_targets: list[np.ndarray] = []
    target_targets: list[np.ndarray] = []
    max_residual = 0.0
    max_state_error = float(np.max(np.abs(source_target - target_target)))
    failure_step: int | None = None
    failure_reason = ""

    for step in range(actions.shape[0]):
        source_state = JointControllerState(
            current_qpos=current[step],
            target_qpos=source_target,
        )
        target_state = JointControllerState(
            current_qpos=current[step],
            target_qpos=target_target,
        )
        cert = compile_joint_transport(
            source_contract,
            target_contract,
            source_state=source_state,
            target_state=target_state,
            source_native_action=actions[step],
            atol=atol,
        )
        max_residual = max(max_residual, cert.max_abs_residual)
        if not cert.exact:
            failure_step = step
            failure_reason = cert.reason
            break

        compiled.append(cert.target_native_action)
        source_targets.append(cert.source_target_qpos)
        target_targets.append(cert.target_target_qpos)
        source_target = cert.source_target_qpos
        target_target = cert.target_target_qpos
        max_state_error = max(
            max_state_error,
            float(np.max(np.abs(source_target - target_target))),
        )

    exact = failure_step is None
    prefix = len(compiled)
    dim = actions.shape[1]
    target_actions_array = (
        np.stack(compiled, axis=0)
        if compiled
        else np.empty((0, dim), dtype=float)
    )
    source_trace_array = (
        np.stack(source_targets, axis=0)
        if source_targets
        else np.empty((0, dim), dtype=float)
    )
    target_trace_array = (
        np.stack(target_targets, axis=0)
        if target_targets
        else np.empty((0, dim), dtype=float)
    )
    return JointTraceTransportCertificate(
        exact=exact,
        exact_prefix_steps=prefix,
        first_failure_step=failure_step,
        target_native_actions=target_actions_array,
        source_target_trace=source_trace_array,
        target_target_trace=target_trace_array,
        max_abs_residual=max_residual,
        max_state_relation_error=max_state_error,
        reason=(
            "entire trajectory preserves the physical target-state relation"
            if exact
            else f"semantic transport fails at step {failure_step}: {failure_reason}"
        ),
    )
