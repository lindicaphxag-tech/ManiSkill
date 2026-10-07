from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


JointMode = Literal["absolute", "delta_current", "delta_target"]


@dataclass(frozen=True)
class ControllerState:
    """Minimal hidden state needed to interpret one joint-position action."""

    current_qpos: np.ndarray
    target_qpos: np.ndarray | None = None


@dataclass(frozen=True)
class PhysicalJointTarget:
    """Controller-independent semantic normal form for this exact family."""

    qpos: np.ndarray


@dataclass(frozen=True)
class EncodedAction:
    action: np.ndarray
    representable: bool
    physical_payload: np.ndarray
    saturation_margin: float


@dataclass(frozen=True)
class TransportCertificate:
    """Evidence that two native actions denote the same physical joint target."""

    accepted: bool
    source_goal: np.ndarray
    target_action: np.ndarray
    reconstructed_goal: np.ndarray
    semantic_residual: float
    source_mode: JointMode
    target_mode: JointMode
    target_representable: bool
    reason: str


class JointPositionChart:
    """Native-action chart for one joint-position controller.

    lower and upper are physical controller-payload bounds: absolute qpos for
    absolute mode and delta-qpos for the two delta modes.

    Version 0 intentionally models only the exact joint-position semantic
    family. Velocity, torque, Cartesian pose, IK, interpolation dynamics and
    actuator traces require a richer semantic normal form.
    """

    def __init__(
        self,
        *,
        mode: JointMode,
        lower: np.ndarray,
        upper: np.ndarray,
        normalized: bool = True,
    ) -> None:
        if mode not in ("absolute", "delta_current", "delta_target"):
            raise ValueError(f"unsupported joint-position mode: {mode}")
        self.mode = mode
        self.lower = np.asarray(lower, dtype=float)
        self.upper = np.asarray(upper, dtype=float)
        if self.lower.ndim != 1 or self.upper.shape != self.lower.shape:
            raise ValueError("lower and upper must have one matching joint dimension")
        if not np.all(np.isfinite(self.lower)) or not np.all(np.isfinite(self.upper)):
            raise ValueError("controller bounds must be finite")
        if np.any(self.upper <= self.lower):
            raise ValueError("every upper bound must exceed its lower bound")
        self.normalized = bool(normalized)

    @property
    def dof(self) -> int:
        return int(self.lower.size)

    def _validate_state(
        self, state: ControllerState
    ) -> tuple[np.ndarray, np.ndarray | None]:
        current = np.asarray(state.current_qpos, dtype=float)
        if current.shape != (self.dof,):
            raise ValueError(f"current_qpos must have shape {(self.dof,)}")
        target = None
        if state.target_qpos is not None:
            target = np.asarray(state.target_qpos, dtype=float)
            if target.shape != (self.dof,):
                raise ValueError(f"target_qpos must have shape {(self.dof,)}")
        if not np.all(np.isfinite(current)) or (
            target is not None and not np.all(np.isfinite(target))
        ):
            raise ValueError("controller state must be finite")
        return current, target

    def _decode_payload(self, action: np.ndarray) -> np.ndarray:
        action = np.asarray(action, dtype=float)
        if action.shape != (self.dof,):
            raise ValueError(f"action must have shape {(self.dof,)}")
        if not np.all(np.isfinite(action)):
            raise ValueError("action must be finite")
        if not self.normalized:
            return action
        clipped = np.clip(action, -1.0, 1.0)
        return 0.5 * (self.upper + self.lower) + 0.5 * (
            self.upper - self.lower
        ) * clipped

    def decode(
        self,
        action: np.ndarray,
        *,
        state: ControllerState,
    ) -> PhysicalJointTarget:
        current, prior_target = self._validate_state(state)
        payload = self._decode_payload(action)
        if self.mode == "absolute":
            goal = payload
        elif self.mode == "delta_current":
            goal = current + payload
        else:
            if prior_target is None:
                raise ValueError(
                    "delta_target semantics require the controller's prior target_qpos"
                )
            goal = prior_target + payload
        return PhysicalJointTarget(qpos=np.asarray(goal, dtype=float))

    def encode(
        self,
        goal: PhysicalJointTarget,
        *,
        state: ControllerState,
        atol: float = 1e-9,
    ) -> EncodedAction:
        current, prior_target = self._validate_state(state)
        target_qpos = np.asarray(goal.qpos, dtype=float)
        if target_qpos.shape != (self.dof,):
            raise ValueError(f"goal qpos must have shape {(self.dof,)}")
        if not np.all(np.isfinite(target_qpos)):
            raise ValueError("goal qpos must be finite")

        if self.mode == "absolute":
            payload = target_qpos
        elif self.mode == "delta_current":
            payload = target_qpos - current
        else:
            if prior_target is None:
                raise ValueError(
                    "delta_target semantics require the controller's prior target_qpos"
                )
            payload = target_qpos - prior_target

        below = self.lower - payload
        above = payload - self.upper
        violation = float(max(np.max(below), np.max(above), 0.0))
        representable = violation <= atol

        if self.normalized:
            action = (payload - 0.5 * (self.upper + self.lower)) / (
                0.5 * (self.upper - self.lower)
            )
        else:
            action = payload.copy()

        if self.normalized:
            saturation_margin = float(1.0 - np.max(np.abs(action)))
        else:
            physical_margin = np.minimum(payload - self.lower, self.upper - payload)
            saturation_margin = float(np.min(physical_margin))

        return EncodedAction(
            action=np.asarray(action, dtype=float),
            representable=bool(representable),
            physical_payload=np.asarray(payload, dtype=float),
            saturation_margin=saturation_margin,
        )


def transport_joint_position_action(
    *,
    source_chart: JointPositionChart,
    source_state: ControllerState,
    source_action: np.ndarray,
    target_chart: JointPositionChart,
    target_state: ControllerState,
    semantic_tolerance: float = 1e-9,
) -> TransportCertificate:
    """Transport through a controller-independent physical joint target.

    This is exact only for the semantic family represented by
    PhysicalJointTarget. The function fails closed when the goal cannot be
    represented by the target controller without saturation.
    """
    if source_chart.dof != target_chart.dof:
        raise ValueError("source and target controllers must have the same DoF")
    if semantic_tolerance < 0 or not np.isfinite(semantic_tolerance):
        raise ValueError("semantic_tolerance must be finite and non-negative")

    source_goal = source_chart.decode(source_action, state=source_state)
    encoded = target_chart.encode(source_goal, state=target_state)
    reconstructed = target_chart.decode(encoded.action, state=target_state)
    residual = float(np.linalg.norm(reconstructed.qpos - source_goal.qpos))
    accepted = encoded.representable and residual <= semantic_tolerance

    if not encoded.representable:
        reason = (
            "physical goal lies outside the target controller's representable action image"
        )
    elif residual > semantic_tolerance:
        reason = (
            "target native action does not reconstruct the same physical joint target"
        )
    else:
        reason = (
            "source and target native actions decode to the same physical joint target"
        )

    return TransportCertificate(
        accepted=accepted,
        source_goal=source_goal.qpos.copy(),
        target_action=encoded.action.copy(),
        reconstructed_goal=reconstructed.qpos.copy(),
        semantic_residual=residual,
        source_mode=source_chart.mode,
        target_mode=target_chart.mode,
        target_representable=encoded.representable,
        reason=reason,
    )


def native_copy_semantic_residual(
    *,
    source_action: np.ndarray,
    source_chart: JointPositionChart,
    source_state: ControllerState,
    target_chart: JointPositionChart,
    target_state: ControllerState,
) -> float:
    """Measure semantic error caused by naively copying an action tensor."""
    source_goal = source_chart.decode(source_action, state=source_state)
    target_goal = target_chart.decode(source_action, state=target_state)
    return float(np.linalg.norm(target_goal.qpos - source_goal.qpos))
