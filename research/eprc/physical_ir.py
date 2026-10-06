from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import inf
from typing import Sequence


class ActionSemantics(str, Enum):
    ABSOLUTE = "absolute"
    DELTA_CURRENT = "delta_current"
    DELTA_TARGET = "delta_target"


class UnrepresentableCommand(ValueError):
    pass


@dataclass(frozen=True)
class ControllerContext:
    current: tuple[float, ...]
    previous_target: tuple[float, ...] | None = None


@dataclass(frozen=True)
class ControllerContract:
    semantics: ActionSemantics
    action_low: tuple[float, ...] | None = None
    action_high: tuple[float, ...] | None = None

    def decode(
        self,
        action: Sequence[float],
        context: ControllerContext,
    ) -> tuple[float, ...]:
        action = tuple(float(x) for x in action)
        _same_dim(action, context.current)

        if self.semantics is ActionSemantics.ABSOLUTE:
            return action
        if self.semantics is ActionSemantics.DELTA_CURRENT:
            return tuple(q + dq for q, dq in zip(context.current, action))
        if self.semantics is ActionSemantics.DELTA_TARGET:
            if context.previous_target is None:
                raise UnrepresentableCommand(
                    "delta-target semantics require previous_target state"
                )
            _same_dim(action, context.previous_target)
            return tuple(q + dq for q, dq in zip(context.previous_target, action))
        raise AssertionError(self.semantics)

    def encode(
        self,
        canonical_target: Sequence[float],
        context: ControllerContext,
    ) -> tuple[tuple[float, ...], float]:
        target = tuple(float(x) for x in canonical_target)
        _same_dim(target, context.current)

        if self.semantics is ActionSemantics.ABSOLUTE:
            action = target
        elif self.semantics is ActionSemantics.DELTA_CURRENT:
            action = tuple(qt - q for qt, q in zip(target, context.current))
        elif self.semantics is ActionSemantics.DELTA_TARGET:
            if context.previous_target is None:
                raise UnrepresentableCommand(
                    "delta-target semantics require previous_target state"
                )
            _same_dim(target, context.previous_target)
            action = tuple(
                qt - qprev for qt, qprev in zip(target, context.previous_target)
            )
        else:
            raise AssertionError(self.semantics)

        margin = self.representability_margin(action)
        if margin < 0:
            raise UnrepresentableCommand(
                f"canonical command lies outside target controller authority (margin={margin})"
            )
        return action, margin

    def representability_margin(self, action: Sequence[float]) -> float:
        action = tuple(float(x) for x in action)
        if self.action_low is None and self.action_high is None:
            return inf
        if self.action_low is None or self.action_high is None:
            raise ValueError("action_low and action_high must be specified together")
        _same_dim(action, self.action_low)
        _same_dim(action, self.action_high)

        margins = []
        for x, lo, hi in zip(action, self.action_low, self.action_high):
            margins.extend((x - lo, hi - x))
        return min(margins)


@dataclass(frozen=True)
class TransportResult:
    source_canonical_target: tuple[float, ...]
    target_action: tuple[float, ...]
    target_representability_margin: float


def transport_action(
    source: ControllerContract,
    target: ControllerContract,
    action: Sequence[float],
    *,
    source_context: ControllerContext,
    target_context: ControllerContext,
) -> TransportResult:
    canonical = source.decode(action, source_context)
    target_action, margin = target.encode(canonical, target_context)
    return TransportResult(
        source_canonical_target=canonical,
        target_action=target_action,
        target_representability_margin=margin,
    )


def _same_dim(a: Sequence[float], b: Sequence[float]) -> None:
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} != {len(b)}")
