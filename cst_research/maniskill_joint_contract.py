from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class JointTransportStatus(str, Enum):
    EXACT = "exact"
    SATURATED = "saturated"


@dataclass(frozen=True)
class JointPositionContract:
    """Executable semantics of a joint-position controller action chart.

    low/high are the physical bounds *before* normalization.  For absolute
    control they are joint-position bounds; for delta control they are delta-q
    bounds.
    """

    use_delta: bool
    use_target: bool
    normalize_action: bool
    low: np.ndarray
    high: np.ndarray

    def __post_init__(self):
        low = np.asarray(self.low, dtype=float)
        high = np.asarray(self.high, dtype=float)
        if low.ndim == 0:
            low = low.reshape(1)
        if high.ndim == 0:
            high = high.reshape(1)
        if low.shape != high.shape or low.ndim != 1:
            raise ValueError("low/high must be equal-shape vectors")
        if np.any(high <= low):
            raise ValueError("each high bound must exceed low")
        if self.use_target and not self.use_delta:
            raise ValueError("use_target only has semantics for delta control")
        object.__setattr__(self, "low", low)
        object.__setattr__(self, "high", high)

    @property
    def dim(self) -> int:
        return int(self.low.shape[0])

    def decode(self, native_action: np.ndarray) -> np.ndarray:
        action = np.asarray(native_action, dtype=float)
        if action.shape != (self.dim,):
            raise ValueError("action dimension mismatch")
        if self.normalize_action:
            clipped = np.clip(action, -1.0, 1.0)
            return 0.5 * (self.high + self.low) + 0.5 * (
                self.high - self.low
            ) * clipped
        return np.clip(action, self.low, self.high)

    def encode(self, physical_command: np.ndarray) -> tuple[np.ndarray, bool]:
        command = np.asarray(physical_command, dtype=float)
        if command.shape != (self.dim,):
            raise ValueError("command dimension mismatch")
        representable = bool(
            np.all(command >= self.low) and np.all(command <= self.high)
        )
        clipped = np.clip(command, self.low, self.high)
        if self.normalize_action:
            native = (
                clipped - 0.5 * (self.high + self.low)
            ) / (0.5 * (self.high - self.low))
        else:
            native = clipped
        return native, representable

    def target_after_action(
        self,
        *,
        current_qpos: np.ndarray,
        current_target_qpos: np.ndarray,
        native_action: np.ndarray,
    ) -> np.ndarray:
        q = np.asarray(current_qpos, dtype=float)
        target = np.asarray(current_target_qpos, dtype=float)
        if q.shape != (self.dim,) or target.shape != (self.dim,):
            raise ValueError("controller state dimension mismatch")
        physical = self.decode(native_action)
        if not self.use_delta:
            return physical
        if self.use_target:
            return target + physical
        return q + physical


@dataclass(frozen=True)
class JointTransportCertificate:
    status: JointTransportStatus
    target_native_action: np.ndarray
    source_goal_qpos: np.ndarray
    target_goal_qpos: np.ndarray
    goal_residual: np.ndarray
    residual_norm: float
    required_target_physical_command: np.ndarray
    target_representable: bool
    requires_source_target_state: bool
    requires_target_target_state: bool
    reason: str


def transport_joint_position_action(
    source: JointPositionContract,
    target: JointPositionContract,
    *,
    current_qpos: np.ndarray,
    source_target_qpos: np.ndarray,
    target_target_qpos: np.ndarray,
    source_native_action: np.ndarray,
) -> JointTransportCertificate:
    """Compile one source action into a target native action with a certificate."""
    if source.dim != target.dim:
        raise ValueError("source and target joint dimensions differ")

    q = np.asarray(current_qpos, dtype=float)
    source_target = np.asarray(source_target_qpos, dtype=float)
    target_target = np.asarray(target_target_qpos, dtype=float)
    if q.shape != (source.dim,):
        raise ValueError("current_qpos dimension mismatch")
    if source_target.shape != q.shape or target_target.shape != q.shape:
        raise ValueError("target-state dimension mismatch")

    source_goal = source.target_after_action(
        current_qpos=q,
        current_target_qpos=source_target,
        native_action=np.asarray(source_native_action, dtype=float),
    )

    if not target.use_delta:
        required = source_goal
    elif target.use_target:
        required = source_goal - target_target
    else:
        required = source_goal - q

    target_native, representable = target.encode(required)
    target_goal = target.target_after_action(
        current_qpos=q,
        current_target_qpos=target_target,
        native_action=target_native,
    )
    residual = target_goal - source_goal
    residual_norm = float(np.linalg.norm(residual))

    if representable and residual_norm <= 1e-12:
        status = JointTransportStatus.EXACT
        reason = "target action chart can encode the source controller goal exactly"
    else:
        status = JointTransportStatus.SATURATED
        reason = (
            "the target action chart cannot encode the source goal without clipping"
        )

    return JointTransportCertificate(
        status=status,
        target_native_action=target_native,
        source_goal_qpos=source_goal,
        target_goal_qpos=target_goal,
        goal_residual=residual,
        residual_norm=residual_norm,
        required_target_physical_command=required,
        target_representable=representable,
        requires_source_target_state=bool(source.use_delta and source.use_target),
        requires_target_target_state=bool(target.use_delta and target.use_target),
        reason=reason,
    )
