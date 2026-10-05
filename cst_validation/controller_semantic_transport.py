from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class JointPositionMode(str, Enum):
    """Semantic reference used by a joint-position action."""

    ABSOLUTE = "absolute"
    DELTA_CURRENT = "delta_current"
    DELTA_TARGET = "delta_target"


@dataclass(frozen=True)
class AffineActionChart:
    """Map between a controller's native action and physical joint units.

    If normalized=True, native actions live in [-1, 1] and are mapped affinely
    into [low, high]. If normalized=False, native actions already use physical
    joint units and low/high only define the representable range.
    """

    low: np.ndarray
    high: np.ndarray
    normalized: bool = True

    def __post_init__(self) -> None:
        low = np.asarray(self.low, dtype=float)
        high = np.asarray(self.high, dtype=float)
        if low.ndim != 1 or high.shape != low.shape:
            raise ValueError("low/high must have identical one-dimensional shape")
        if not np.all(np.isfinite(low)) or not np.all(np.isfinite(high)):
            raise ValueError("action-chart bounds must be finite")
        if np.any(high <= low):
            raise ValueError("every high bound must exceed low")
        object.__setattr__(self, "low", low)
        object.__setattr__(self, "high", high)

    @property
    def dimension(self) -> int:
        return int(self.low.shape[0])

    def decode(self, native_action: np.ndarray, *, clip_native: bool = False) -> np.ndarray:
        native = np.asarray(native_action, dtype=float)
        if native.shape != self.low.shape:
            raise ValueError("native action shape does not match action chart")
        if not np.all(np.isfinite(native)):
            raise ValueError("native action must be finite")
        if not self.normalized:
            return native.copy()
        if clip_native:
            native = np.clip(native, -1.0, 1.0)
        return 0.5 * (self.high + self.low) + 0.5 * (self.high - self.low) * native

    def encode(self, physical: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Encode physical units without silently clipping.

        Returns (native_action, representable_mask). Callers decide whether a
        non-representable target should refuse, clip, or replan.
        """
        value = np.asarray(physical, dtype=float)
        if value.shape != self.low.shape:
            raise ValueError("physical action shape does not match action chart")
        if not np.all(np.isfinite(value)):
            raise ValueError("physical action must be finite")
        representable = np.logical_and(value >= self.low, value <= self.high)
        if self.normalized:
            native = (value - 0.5 * (self.high + self.low)) / (
                0.5 * (self.high - self.low)
            )
        else:
            native = value.copy()
        return native, representable


@dataclass(frozen=True)
class JointPositionSemantics:
    mode: JointPositionMode
    chart: AffineActionChart

    def canonical_target(
        self,
        native_action: np.ndarray,
        *,
        current_qpos: np.ndarray,
        previous_target_qpos: np.ndarray | None = None,
    ) -> np.ndarray:
        """Decode one native action into its physical absolute target q*."""
        current = np.asarray(current_qpos, dtype=float)
        if current.shape != (self.chart.dimension,):
            raise ValueError("current_qpos shape does not match controller")
        command = self.chart.decode(native_action, clip_native=True)

        if self.mode is JointPositionMode.ABSOLUTE:
            return command
        if self.mode is JointPositionMode.DELTA_CURRENT:
            return current + command
        if previous_target_qpos is None:
            raise ValueError("delta_target semantics requires previous_target_qpos")
        previous = np.asarray(previous_target_qpos, dtype=float)
        if previous.shape != current.shape:
            raise ValueError("previous_target_qpos shape does not match controller")
        return previous + command

    def physical_command_for_target(
        self,
        target_qpos: np.ndarray,
        *,
        current_qpos: np.ndarray,
        previous_target_qpos: np.ndarray | None = None,
    ) -> np.ndarray:
        """Return the physical command before native action encoding."""
        target = np.asarray(target_qpos, dtype=float)
        current = np.asarray(current_qpos, dtype=float)
        if target.shape != (self.chart.dimension,) or current.shape != target.shape:
            raise ValueError("target/current shape does not match controller")
        if self.mode is JointPositionMode.ABSOLUTE:
            return target
        if self.mode is JointPositionMode.DELTA_CURRENT:
            return target - current
        if previous_target_qpos is None:
            raise ValueError("delta_target semantics requires previous_target_qpos")
        previous = np.asarray(previous_target_qpos, dtype=float)
        if previous.shape != target.shape:
            raise ValueError("previous_target_qpos shape does not match controller")
        return target - previous

    def encode_target(
        self,
        target_qpos: np.ndarray,
        *,
        current_qpos: np.ndarray,
        previous_target_qpos: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Encode a desired physical absolute target into this controller."""
        target = np.asarray(target_qpos, dtype=float)
        current = np.asarray(current_qpos, dtype=float)
        if target.shape != (self.chart.dimension,) or current.shape != target.shape:
            raise ValueError("target/current shape does not match controller")

        physical_command = self.physical_command_for_target(
            target,
            current_qpos=current,
            previous_target_qpos=previous_target_qpos,
        )
        return self.chart.encode(physical_command)


@dataclass(frozen=True)
class DriveSignature:
    """Low-level PD drive semantics relevant after a target is chosen."""

    stiffness: np.ndarray
    damping: np.ndarray
    force_limit: np.ndarray
    friction: np.ndarray

    def __post_init__(self) -> None:
        arrays = [
            np.asarray(self.stiffness, dtype=float),
            np.asarray(self.damping, dtype=float),
            np.asarray(self.force_limit, dtype=float),
            np.asarray(self.friction, dtype=float),
        ]
        shape = arrays[0].shape
        if len(shape) != 1 or any(item.shape != shape for item in arrays):
            raise ValueError("all drive arrays must share one-dimensional shape")
        if any(not np.all(np.isfinite(item)) for item in arrays):
            raise ValueError("drive parameters must be finite")
        object.__setattr__(self, "stiffness", arrays[0])
        object.__setattr__(self, "damping", arrays[1])
        object.__setattr__(self, "force_limit", arrays[2])
        object.__setattr__(self, "friction", arrays[3])

    def exact_match(self, other: "DriveSignature", *, atol: float = 1e-12) -> bool:
        return all(
            np.allclose(left, right, atol=atol, rtol=0.0)
            for left, right in (
                (self.stiffness, other.stiffness),
                (self.damping, other.damping),
                (self.force_limit, other.force_limit),
                (self.friction, other.friction),
            )
        )


@dataclass(frozen=True)
class SemanticTransportCertificate:
    target_native_action: np.ndarray
    target_physical_command: np.ndarray
    canonical_source_target: np.ndarray
    reconstructed_target: np.ndarray
    goal_residual: float
    representable_mask: np.ndarray
    normalized_representability_margin: np.ndarray
    goal_equivalent: bool
    drive_equivalent: bool | None
    requires_source_memory: bool
    requires_target_memory: bool
    reason: str


def _normalized_margin(
    physical_command: np.ndarray,
    *,
    low: np.ndarray,
    high: np.ndarray,
) -> np.ndarray:
    """Signed distance to the nearest action bound, normalized by range.

    Positive values are representable with headroom, zero lies on a bound, and
    negative values quantify how far the requested command lies outside the
    target chart.
    """
    command = np.asarray(physical_command, dtype=float)
    width = np.asarray(high, dtype=float) - np.asarray(low, dtype=float)
    left = (command - low) / width
    right = (high - command) / width
    return np.minimum(left, right)


def transport_joint_position_action(
    *,
    source: JointPositionSemantics,
    target: JointPositionSemantics,
    source_native_action: np.ndarray,
    current_qpos: np.ndarray,
    source_previous_target_qpos: np.ndarray | None = None,
    target_previous_target_qpos: np.ndarray | None = None,
    source_drive: DriveSignature | None = None,
    target_drive: DriveSignature | None = None,
    atol: float = 1e-10,
) -> SemanticTransportCertificate:
    """Transport one action by preserving its physical controller goal.

    The function refuses to call a conversion exact when the target action chart
    cannot represent the source goal. No clipping is hidden inside the
    certificate.
    """
    if source.chart.dimension != target.chart.dimension:
        raise ValueError("source and target controller dimensions must match")

    source_target = source.canonical_target(
        source_native_action,
        current_qpos=current_qpos,
        previous_target_qpos=source_previous_target_qpos,
    )
    target_physical_command = target.physical_command_for_target(
        source_target,
        current_qpos=current_qpos,
        previous_target_qpos=target_previous_target_qpos,
    )
    target_native, representable = target.chart.encode(target_physical_command)
    margin = _normalized_margin(
        target_physical_command,
        low=target.chart.low,
        high=target.chart.high,
    )
    reconstructed = target.canonical_target(
        target_native,
        current_qpos=current_qpos,
        previous_target_qpos=target_previous_target_qpos,
    )
    residual = float(np.linalg.norm(reconstructed - source_target))
    goal_equivalent = bool(np.all(representable) and residual <= atol)

    drive_equivalent: bool | None
    if source_drive is None and target_drive is None:
        drive_equivalent = None
    elif source_drive is None or target_drive is None:
        drive_equivalent = False
    else:
        drive_equivalent = bool(
            goal_equivalent and source_drive.exact_match(target_drive, atol=atol)
        )

    if not np.all(representable):
        reason = "source goal is outside the target controller's representable action set"
    elif residual > atol:
        reason = "target native action does not reconstruct the source physical goal"
    elif drive_equivalent is False:
        reason = (
            "physical target is preserved, but low-level drive semantics differ; "
            "goal-equivalence does not imply drive-equivalence"
        )
    else:
        reason = "source physical goal is exactly representable in the target action chart"

    return SemanticTransportCertificate(
        target_native_action=target_native,
        target_physical_command=target_physical_command,
        canonical_source_target=source_target,
        reconstructed_target=reconstructed,
        goal_residual=residual,
        representable_mask=representable,
        normalized_representability_margin=margin,
        goal_equivalent=goal_equivalent,
        drive_equivalent=drive_equivalent,
        requires_source_memory=source.mode is JointPositionMode.DELTA_TARGET,
        requires_target_memory=target.mode is JointPositionMode.DELTA_TARGET,
        reason=reason,
    )


@dataclass(frozen=True)
class SequenceTransportResult:
    native_actions: np.ndarray
    certificates: tuple[SemanticTransportCertificate, ...]
    all_goal_equivalent: bool


def transport_joint_position_sequence(
    *,
    source: JointPositionSemantics,
    target: JointPositionSemantics,
    source_native_actions: np.ndarray,
    current_qpos_sequence: np.ndarray,
    source_initial_target_qpos: np.ndarray | None = None,
    target_initial_target_qpos: np.ndarray | None = None,
    atol: float = 1e-10,
) -> SequenceTransportResult:
    """Transport a sequence while evolving target-relative hidden state.

    current_qpos_sequence[t] is the physical joint state at the beginning of
    policy step t. For DELTA_TARGET controllers, hidden target state evolves
    according to the decoded canonical target, not the measured qpos.
    """
    actions = np.asarray(source_native_actions, dtype=float)
    currents = np.asarray(current_qpos_sequence, dtype=float)
    if actions.ndim != 2 or actions.shape[1] != source.chart.dimension:
        raise ValueError("source_native_actions must have shape [T, D]")
    if currents.shape != actions.shape:
        raise ValueError("current_qpos_sequence must match [T, D]")
    if target.chart.dimension != source.chart.dimension:
        raise ValueError("source and target controller dimensions must match")

    source_memory = (
        None
        if source_initial_target_qpos is None
        else np.asarray(source_initial_target_qpos, dtype=float).copy()
    )
    target_memory = (
        None
        if target_initial_target_qpos is None
        else np.asarray(target_initial_target_qpos, dtype=float).copy()
    )

    transported: list[np.ndarray] = []
    certificates: list[SemanticTransportCertificate] = []
    for action, current in zip(actions, currents, strict=True):
        cert = transport_joint_position_action(
            source=source,
            target=target,
            source_native_action=action,
            current_qpos=current,
            source_previous_target_qpos=source_memory,
            target_previous_target_qpos=target_memory,
            atol=atol,
        )
        transported.append(cert.target_native_action)
        certificates.append(cert)

        # A target-relative controller stores its latest target, even if the
        # robot has not physically reached that target yet.
        if source.mode is JointPositionMode.DELTA_TARGET:
            source_memory = cert.canonical_source_target.copy()
        if target.mode is JointPositionMode.DELTA_TARGET:
            target_memory = cert.canonical_source_target.copy()

    return SequenceTransportResult(
        native_actions=np.stack(transported, axis=0),
        certificates=tuple(certificates),
        all_goal_equivalent=all(item.goal_equivalent for item in certificates),
    )
