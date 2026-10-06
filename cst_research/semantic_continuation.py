from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from reference_semantics import ReferenceKind, ReferenceSemantics


class RuntimeSignal(str, Enum):
    SOURCE_CURRENT_STATE = "source_current_state"
    SOURCE_CONTROLLER_TARGET = "source_controller_target"
    TARGET_CURRENT_STATE = "target_current_state"
    TARGET_CONTROLLER_TARGET = "target_controller_target"


@dataclass(frozen=True)
class DependencyPlan:
    query_captures: tuple[str, ...]
    step_signals: tuple[RuntimeSignal, ...]
    fully_precomputable: bool
    reason: str


@dataclass(frozen=True)
class ContinuationStepResult:
    step: int
    physical_goal: np.ndarray
    target_native_action: np.ndarray
    source_reference: np.ndarray
    target_reference: np.ndarray


@dataclass
class SemanticActionContinuation:
    """A partially evaluated action-transport program.

    Query-time references are captured into this object. Only genuinely future
    execution-owned references remain as explicit step inputs. This avoids
    hidden mutable-cache dependencies such as refreshing a chunk anchor on every
    control tick.
    """

    source_actions: np.ndarray
    source_semantics: ReferenceSemantics
    target_semantics: ReferenceSemantics
    source_chunk_anchor: np.ndarray | None = None
    target_chunk_anchor: np.ndarray | None = None
    source_previous_command: np.ndarray | None = None
    target_previous_command: np.ndarray | None = None

    def __post_init__(self):
        actions = np.asarray(self.source_actions, dtype=float)
        if actions.ndim != 2 or actions.shape[0] == 0:
            raise ValueError("source_actions must be a non-empty [T, D] array")
        if not np.all(np.isfinite(actions)):
            raise ValueError("source_actions must be finite")
        if self.source_semantics.relative_mask.shape != (actions.shape[1],):
            raise ValueError("source semantics dimension mismatch")
        if self.target_semantics.relative_mask.shape != (actions.shape[1],):
            raise ValueError("target semantics dimension mismatch")
        self.source_actions = actions.copy()
        self.source_chunk_anchor = self._optional_vec(
            self.source_chunk_anchor, "source_chunk_anchor"
        )
        self.target_chunk_anchor = self._optional_vec(
            self.target_chunk_anchor, "target_chunk_anchor"
        )
        self.source_previous_command = self._optional_vec(
            self.source_previous_command, "source_previous_command"
        )
        self.target_previous_command = self._optional_vec(
            self.target_previous_command, "target_previous_command"
        )
        self._step = 0

    @property
    def horizon(self) -> int:
        return int(self.source_actions.shape[0])

    @property
    def dim(self) -> int:
        return int(self.source_actions.shape[1])

    def _optional_vec(self, value, name):
        if value is None:
            return None
        out = np.asarray(value, dtype=float)
        if out.shape != (self.dim,):
            raise ValueError(f"{name} dimension mismatch")
        if not np.all(np.isfinite(out)):
            raise ValueError(f"{name} must be finite")
        return out.copy()

    def dependency_plan(self) -> DependencyPlan:
        captures: list[str] = []
        signals: list[RuntimeSignal] = []

        def add_source(kind: ReferenceKind, active: bool):
            if not active or kind is ReferenceKind.ABSOLUTE:
                return
            if kind is ReferenceKind.CHUNK_ANCHOR:
                captures.append("source_chunk_anchor")
            elif kind is ReferenceKind.PREVIOUS_COMMAND:
                captures.append("source_initial_previous_command")
            elif kind is ReferenceKind.CURRENT_STATE:
                signals.append(RuntimeSignal.SOURCE_CURRENT_STATE)
            elif kind is ReferenceKind.CONTROLLER_TARGET:
                signals.append(RuntimeSignal.SOURCE_CONTROLLER_TARGET)
            else:
                raise AssertionError(kind)

        def add_target(kind: ReferenceKind, active: bool):
            if not active or kind is ReferenceKind.ABSOLUTE:
                return
            if kind is ReferenceKind.CHUNK_ANCHOR:
                captures.append("target_chunk_anchor")
            elif kind is ReferenceKind.PREVIOUS_COMMAND:
                captures.append("target_initial_previous_command")
            elif kind is ReferenceKind.CURRENT_STATE:
                signals.append(RuntimeSignal.TARGET_CURRENT_STATE)
            elif kind is ReferenceKind.CONTROLLER_TARGET:
                signals.append(RuntimeSignal.TARGET_CONTROLLER_TARGET)
            else:
                raise AssertionError(kind)

        add_source(
            self.source_semantics.kind,
            bool(np.any(self.source_semantics.relative_mask)),
        )
        add_target(
            self.target_semantics.kind,
            bool(np.any(self.target_semantics.relative_mask)),
        )

        # Stable order and no duplicate runtime reads when source/target names differ
        # only by ownership. Ownership remains explicit in the enum.
        captures_tuple = tuple(dict.fromkeys(captures))
        signals_tuple = tuple(dict.fromkeys(signals))
        return DependencyPlan(
            query_captures=captures_tuple,
            step_signals=signals_tuple,
            fully_precomputable=not signals_tuple,
            reason=(
                "all reference provenance can be captured when the action chunk is created"
                if not signals_tuple
                else "future execution-owned references remain explicit step-time inputs"
            ),
        )

    def validate_query_captures(self) -> None:
        active_source = bool(np.any(self.source_semantics.relative_mask))
        active_target = bool(np.any(self.target_semantics.relative_mask))
        if active_source:
            if (
                self.source_semantics.kind is ReferenceKind.CHUNK_ANCHOR
                and self.source_chunk_anchor is None
            ):
                raise ValueError("missing source_chunk_anchor")
            if (
                self.source_semantics.kind is ReferenceKind.PREVIOUS_COMMAND
                and self.source_previous_command is None
                and self.source_chunk_anchor is None
            ):
                raise ValueError(
                    "source PREVIOUS_COMMAND requires initial previous command or anchor"
                )
        if active_target:
            if (
                self.target_semantics.kind is ReferenceKind.CHUNK_ANCHOR
                and self.target_chunk_anchor is None
            ):
                raise ValueError("missing target_chunk_anchor")
            if (
                self.target_semantics.kind is ReferenceKind.PREVIOUS_COMMAND
                and self.target_previous_command is None
                and self.target_chunk_anchor is None
            ):
                raise ValueError(
                    "target PREVIOUS_COMMAND requires initial previous command or anchor"
                )

    def _runtime_vec(self, value, name):
        if value is None:
            raise ValueError(f"missing runtime signal: {name}")
        out = np.asarray(value, dtype=float)
        if out.shape != (self.dim,):
            raise ValueError(f"{name} dimension mismatch")
        if not np.all(np.isfinite(out)):
            raise ValueError(f"{name} must be finite")
        return out

    def _reference(
        self,
        semantics: ReferenceSemantics,
        *,
        source: bool,
        current_state: np.ndarray | None,
        controller_target: np.ndarray | None,
    ) -> np.ndarray:
        kind = semantics.kind
        if kind is ReferenceKind.ABSOLUTE:
            return np.zeros(self.dim)
        if kind is ReferenceKind.CHUNK_ANCHOR:
            ref = self.source_chunk_anchor if source else self.target_chunk_anchor
            if ref is None:
                raise ValueError(
                    f"missing {'source' if source else 'target'}_chunk_anchor"
                )
            return ref
        if kind is ReferenceKind.PREVIOUS_COMMAND:
            ref = (
                self.source_previous_command
                if source
                else self.target_previous_command
            )
            if ref is None:
                ref = self.source_chunk_anchor if source else self.target_chunk_anchor
            if ref is None:
                raise ValueError("missing previous-command reference")
            return ref
        if kind is ReferenceKind.CURRENT_STATE:
            return self._runtime_vec(
                current_state,
                "source_current_state" if source else "target_current_state",
            )
        if kind is ReferenceKind.CONTROLLER_TARGET:
            return self._runtime_vec(
                controller_target,
                "source_controller_target"
                if source
                else "target_controller_target",
            )
        raise AssertionError(kind)

    @staticmethod
    def _decode(action, ref, semantics):
        goal = np.asarray(action, dtype=float).copy()
        if semantics.kind is not ReferenceKind.ABSOLUTE:
            m = semantics.relative_mask
            goal[m] = ref[m] + goal[m]
        return goal

    @staticmethod
    def _encode(goal, ref, semantics):
        action = np.asarray(goal, dtype=float).copy()
        if semantics.kind is not ReferenceKind.ABSOLUTE:
            m = semantics.relative_mask
            action[m] = action[m] - ref[m]
        return action

    def step(
        self,
        *,
        source_current_state: np.ndarray | None = None,
        source_controller_target: np.ndarray | None = None,
        target_current_state: np.ndarray | None = None,
        target_controller_target: np.ndarray | None = None,
    ) -> ContinuationStepResult:
        if self._step >= self.horizon:
            raise StopIteration("action continuation exhausted")
        self.validate_query_captures()

        source_ref = self._reference(
            self.source_semantics,
            source=True,
            current_state=source_current_state,
            controller_target=source_controller_target,
        )
        goal = self._decode(
            self.source_actions[self._step], source_ref, self.source_semantics
        )

        target_ref = self._reference(
            self.target_semantics,
            source=False,
            current_state=target_current_state,
            controller_target=target_controller_target,
        )
        target_action = self._encode(goal, target_ref, self.target_semantics)

        if self.source_semantics.kind is ReferenceKind.PREVIOUS_COMMAND:
            self.source_previous_command = goal.copy()
        if self.target_semantics.kind is ReferenceKind.PREVIOUS_COMMAND:
            self.target_previous_command = goal.copy()

        result = ContinuationStepResult(
            step=self._step,
            physical_goal=goal.copy(),
            target_native_action=target_action.copy(),
            source_reference=source_ref.copy(),
            target_reference=target_ref.copy(),
        )
        self._step += 1
        return result

    def precompute(self) -> np.ndarray:
        """Materialize all target actions iff no future runtime signal is needed."""
        plan = self.dependency_plan()
        if not plan.fully_precomputable:
            raise RuntimeError(
                "continuation has step-time dependencies: "
                + ", ".join(signal.value for signal in plan.step_signals)
            )
        # Execute a clone so precomputation does not consume this continuation.
        clone = SemanticActionContinuation(
            source_actions=self.source_actions,
            source_semantics=self.source_semantics,
            target_semantics=self.target_semantics,
            source_chunk_anchor=self.source_chunk_anchor,
            target_chunk_anchor=self.target_chunk_anchor,
            source_previous_command=self.source_previous_command,
            target_previous_command=self.target_previous_command,
        )
        return np.stack([clone.step().target_native_action for _ in range(clone.horizon)])
