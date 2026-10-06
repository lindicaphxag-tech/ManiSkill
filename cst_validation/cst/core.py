from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


Mode = Literal["absolute", "delta_current", "delta_target", "relative_latched"]


class MissingControllerStateError(ValueError):
    """Raised when exact conversion needs controller state that is unavailable."""


@dataclass(frozen=True)
class JointControllerContext:
    q_current: np.ndarray | None = None
    q_target: np.ndarray | None = None
    q_latched: np.ndarray | None = None


@dataclass(frozen=True)
class EncodeResult:
    action: np.ndarray
    representable: bool
    saturation: np.ndarray
    reason: str


@dataclass(frozen=True)
class TransportCertificate:
    exact: bool
    representable: bool
    semantic_residual: float
    source_mode: str
    target_mode: str
    source_required_state: tuple[str, ...]
    target_required_state: tuple[str, ...]
    reason: str


def _vector(value, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 1 or out.size == 0:
        raise ValueError(f"{name} must be a non-empty 1D array")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


@dataclass(frozen=True)
class JointGoalChart:
    """Native controller action chart for one joint-position goal semantics.

    The semantic object is the physical joint-position goal q_goal, not the
    native tensor stored in a dataset.

    Modes:
      - absolute: native physical action is q_goal;
      - delta_current: physical delta is relative to measured q_current;
      - delta_target: physical delta is relative to the controller's internal
        target q_target;
      - relative_latched: every action in a chunk is relative to one state
        latched at prediction/chunk start.

    If normalized=True, lower/upper are the physical values represented by
    native actions -1 and +1.
    """

    mode: Mode
    normalized: bool = False
    lower: np.ndarray | float | None = None
    upper: np.ndarray | float | None = None

    @property
    def semantic_space(self) -> str:
        return "joint_position_goal"

    @property
    def required_state(self) -> tuple[str, ...]:
        if self.mode == "absolute":
            return ()
        if self.mode == "delta_current":
            return ("q_current",)
        if self.mode == "delta_target":
            return ("q_target",)
        if self.mode == "relative_latched":
            return ("q_latched",)
        raise ValueError(f"unknown mode {self.mode}")

    def _bounds(self, dim: int) -> tuple[np.ndarray | None, np.ndarray | None]:
        if self.lower is None and self.upper is None:
            if self.normalized:
                raise ValueError("normalized charts require physical lower/upper bounds")
            return None, None
        if self.lower is None or self.upper is None:
            raise ValueError("lower and upper must be provided together")
        low = np.broadcast_to(np.asarray(self.lower, dtype=float), (dim,)).copy()
        high = np.broadcast_to(np.asarray(self.upper, dtype=float), (dim,)).copy()
        if (
            np.any(~np.isfinite(low))
            or np.any(~np.isfinite(high))
            or np.any(high <= low)
        ):
            raise ValueError("invalid physical action bounds")
        return low, high

    def _physical_from_native(self, action: np.ndarray) -> np.ndarray:
        native = _vector(action, "action")
        low, high = self._bounds(native.size)
        if not self.normalized:
            return native
        clipped = np.clip(native, -1.0, 1.0)
        return 0.5 * (high + low) + 0.5 * (high - low) * clipped

    def _native_from_physical(self, physical: np.ndarray) -> EncodeResult:
        value = _vector(physical, "physical action")
        low, high = self._bounds(value.size)
        if low is None:
            return EncodeResult(
                action=value.copy(),
                representable=True,
                saturation=np.zeros_like(value, dtype=bool),
                reason="unbounded physical chart",
            )

        saturation = np.logical_or(value < low, value > high)
        representable = not bool(np.any(saturation))
        if self.normalized:
            native = (value - 0.5 * (high + low)) / (0.5 * (high - low))
        else:
            native = value.copy()
        return EncodeResult(
            action=native,
            representable=representable,
            saturation=saturation,
            reason=(
                "physical command lies inside target chart"
                if representable
                else "physical command lies outside target chart"
            ),
        )

    @staticmethod
    def _state(
        context: JointControllerContext,
        name: str,
        dim: int,
        mode: str,
    ) -> np.ndarray:
        value = getattr(context, name)
        if value is None:
            raise MissingControllerStateError(f"{mode} chart requires {name}")
        out = _vector(value, name)
        if out.size != dim:
            raise ValueError(f"{name} dimension mismatch")
        return out

    def decode(
        self,
        action: np.ndarray,
        context: JointControllerContext,
    ) -> np.ndarray:
        physical = self._physical_from_native(action)
        if self.mode == "absolute":
            return physical
        if self.mode == "delta_current":
            return (
                self._state(context, "q_current", physical.size, self.mode)
                + physical
            )
        if self.mode == "delta_target":
            return (
                self._state(context, "q_target", physical.size, self.mode)
                + physical
            )
        if self.mode == "relative_latched":
            return (
                self._state(context, "q_latched", physical.size, self.mode)
                + physical
            )
        raise ValueError(f"unknown mode {self.mode}")

    def encode(
        self,
        q_goal: np.ndarray,
        context: JointControllerContext,
    ) -> EncodeResult:
        goal = _vector(q_goal, "q_goal")
        if self.mode == "absolute":
            physical = goal
        elif self.mode == "delta_current":
            physical = goal - self._state(
                context, "q_current", goal.size, self.mode
            )
        elif self.mode == "delta_target":
            physical = goal - self._state(
                context, "q_target", goal.size, self.mode
            )
        elif self.mode == "relative_latched":
            physical = goal - self._state(
                context, "q_latched", goal.size, self.mode
            )
        else:
            raise ValueError(f"unknown mode {self.mode}")
        return self._native_from_physical(physical)


def exact_transport_identifiable(
    chart: JointGoalChart,
    context: JointControllerContext,
) -> tuple[bool, tuple[str, ...]]:
    """Check whether all controller state required by one chart is observed."""
    missing = tuple(
        name for name in chart.required_state if getattr(context, name) is None
    )
    return len(missing) == 0, missing


def transport_action(
    source_chart: JointGoalChart,
    target_chart: JointGoalChart,
    source_action: np.ndarray,
    source_context: JointControllerContext,
    target_context: JointControllerContext,
    *,
    tolerance: float = 1e-10,
) -> tuple[EncodeResult, TransportCertificate]:
    """Transport an action through a shared physical joint-goal semantics.

    T_{s->t} = E_t o D_s.

    The returned certificate is fail-closed: if the target chart cannot
    represent the decoded physical goal, exact transport is false rather than
    clipping silently.
    """
    q_goal = source_chart.decode(source_action, source_context)
    encoded = target_chart.encode(q_goal, target_context)
    if not encoded.representable:
        return encoded, TransportCertificate(
            exact=False,
            representable=False,
            semantic_residual=float("inf"),
            source_mode=source_chart.mode,
            target_mode=target_chart.mode,
            source_required_state=source_chart.required_state,
            target_required_state=target_chart.required_state,
            reason=encoded.reason,
        )

    reconstructed = target_chart.decode(encoded.action, target_context)
    residual = float(np.linalg.norm(reconstructed - q_goal))
    exact = residual <= tolerance
    return encoded, TransportCertificate(
        exact=exact,
        representable=True,
        semantic_residual=residual,
        source_mode=source_chart.mode,
        target_mode=target_chart.mode,
        source_required_state=source_chart.required_state,
        target_required_state=target_chart.required_state,
        reason=(
            "semantic joint-position goal is preserved"
            if exact
            else "target chart round-trip exceeds tolerance"
        ),
    )
