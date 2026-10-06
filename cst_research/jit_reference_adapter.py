from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from reference_semantics import ReferenceKind, ReferenceSemantics


@dataclass(frozen=True)
class JITStepResult:
    step: int
    source_native_action: np.ndarray
    source_reference: np.ndarray
    physical_goal: np.ndarray
    target_reference: np.ndarray
    target_native_action: np.ndarray
    reconstructed_target_goal: np.ndarray
    max_abs_goal_error: float


class JustInTimeReferenceAdapter:
    """Stateful step-time adapter between reference-semantic action interfaces.

    The adapter is intentionally executed at the control step rather than when
    an entire action chunk is produced. This makes future measured state and
    controller-owned target state available when the target native action is
    encoded.
    """

    def __init__(
        self,
        source_semantics: ReferenceSemantics,
        target_semantics: ReferenceSemantics,
        *,
        source_chunk_anchor: np.ndarray | None = None,
        target_chunk_anchor: np.ndarray | None = None,
        source_previous_command: np.ndarray | None = None,
        target_previous_command: np.ndarray | None = None,
    ):
        if source_semantics.relative_mask.shape != target_semantics.relative_mask.shape:
            raise ValueError("source and target dimensions differ")
        self.source_semantics = source_semantics
        self.target_semantics = target_semantics
        self.dim = int(source_semantics.relative_mask.size)
        self.source_chunk_anchor = self._optional_vec(source_chunk_anchor, "source_chunk_anchor")
        self.target_chunk_anchor = self._optional_vec(target_chunk_anchor, "target_chunk_anchor")
        self.source_previous_command = self._optional_vec(
            source_previous_command, "source_previous_command"
        )
        self.target_previous_command = self._optional_vec(
            target_previous_command, "target_previous_command"
        )
        self.step_index = 0

    def _optional_vec(self, value, name):
        if value is None:
            return None
        out = np.asarray(value, dtype=float)
        if out.shape != (self.dim,):
            raise ValueError(f"{name} dimension mismatch")
        return out.copy()

    def _vec(self, value, name):
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
        current_state: np.ndarray,
        controller_target: np.ndarray | None,
        source: bool,
    ) -> np.ndarray:
        kind = semantics.kind
        if kind is ReferenceKind.ABSOLUTE:
            return np.zeros(self.dim)
        if kind is ReferenceKind.CURRENT_STATE:
            return current_state
        if kind is ReferenceKind.CHUNK_ANCHOR:
            ref = self.source_chunk_anchor if source else self.target_chunk_anchor
            if ref is None:
                raise ValueError("chunk-anchor semantics require a captured anchor")
            return ref
        if kind is ReferenceKind.PREVIOUS_COMMAND:
            ref = (
                self.source_previous_command
                if source
                else self.target_previous_command
            )
            if ref is None:
                fallback = self.source_chunk_anchor if source else self.target_chunk_anchor
                if fallback is None:
                    raise ValueError(
                        "previous-command semantics require previous command or anchor"
                    )
                ref = fallback
            return ref
        if kind is ReferenceKind.CONTROLLER_TARGET:
            if controller_target is None:
                raise ValueError(
                    "controller-target semantics require runtime controller target"
                )
            return controller_target
        raise AssertionError(kind)

    @staticmethod
    def _decode(
        action: np.ndarray,
        reference: np.ndarray,
        semantics: ReferenceSemantics,
    ) -> np.ndarray:
        goal = action.copy()
        if semantics.kind is not ReferenceKind.ABSOLUTE:
            mask = semantics.relative_mask
            goal[mask] = reference[mask] + action[mask]
        return goal

    @staticmethod
    def _encode(
        goal: np.ndarray,
        reference: np.ndarray,
        semantics: ReferenceSemantics,
    ) -> np.ndarray:
        action = goal.copy()
        if semantics.kind is not ReferenceKind.ABSOLUTE:
            mask = semantics.relative_mask
            action[mask] = goal[mask] - reference[mask]
        return action

    def step(
        self,
        source_native_action: np.ndarray,
        *,
        current_state: np.ndarray,
        source_controller_target: np.ndarray | None = None,
        target_controller_target: np.ndarray | None = None,
    ) -> JITStepResult:
        source_action = self._vec(source_native_action, "source_native_action")
        state = self._vec(current_state, "current_state")
        source_target = (
            None
            if source_controller_target is None
            else self._vec(source_controller_target, "source_controller_target")
        )
        target_target = (
            None
            if target_controller_target is None
            else self._vec(target_controller_target, "target_controller_target")
        )

        source_ref = self._reference(
            self.source_semantics,
            current_state=state,
            controller_target=source_target,
            source=True,
        )
        goal = self._decode(source_action, source_ref, self.source_semantics)

        target_ref = self._reference(
            self.target_semantics,
            current_state=state,
            controller_target=target_target,
            source=False,
        )
        target_action = self._encode(goal, target_ref, self.target_semantics)
        reconstructed = self._decode(
            target_action, target_ref, self.target_semantics
        )
        err = float(np.max(np.abs(reconstructed - goal)))

        if self.source_semantics.kind is ReferenceKind.PREVIOUS_COMMAND:
            self.source_previous_command = goal.copy()
        if self.target_semantics.kind is ReferenceKind.PREVIOUS_COMMAND:
            self.target_previous_command = goal.copy()

        result = JITStepResult(
            step=self.step_index,
            source_native_action=source_action.copy(),
            source_reference=source_ref.copy(),
            physical_goal=goal.copy(),
            target_reference=target_ref.copy(),
            target_native_action=target_action.copy(),
            reconstructed_target_goal=reconstructed.copy(),
            max_abs_goal_error=err,
        )
        self.step_index += 1
        return result
