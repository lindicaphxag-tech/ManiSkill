from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .stateful_semantics import (
    JointCommandContract,
    JointControllerState,
    command_to_target_qpos,
    target_qpos_to_native_action,
)


class EffectCommutationKind(str, Enum):
    """Why a source->target controller transport is or is not authorized."""

    EXACT = "exact"
    TARGET_EFFECT_CHANGES_SEMANTICS = "target_effect_changes_semantics"
    SEMANTIC_RESIDUAL = "semantic_residual"


@dataclass(frozen=True)
class EffectCommutationCertificate:
    """Proof-carrying one-step controller transport.

    The certificate closes the semantic diagram

        source native --source effects--> source physical target
              |                                  |
              | compile                          | equality
              v                                  v
        target native --target effects--> target physical target

    where normalization and saturation are part of each controller's effects.
    """

    kind: EffectCommutationKind
    authorized: bool
    source_effective_target: np.ndarray
    target_native_action: np.ndarray
    target_effective_target: np.ndarray
    representable_mask: np.ndarray
    semantic_residual: np.ndarray
    max_abs_residual: float
    changed_coordinates: tuple[int, ...]
    reason: str


def certify_effect_commuting_transport(
    source_contract: JointCommandContract,
    target_contract: JointCommandContract,
    *,
    source_state: JointControllerState,
    target_state: JointControllerState,
    source_native_action: np.ndarray,
    atol: float = 1e-10,
) -> EffectCommutationCertificate:
    """Compile and certify a stateful transport including controller effects.

    Source-side clipping is part of source meaning: e.g. a normalized action
    3.0 means the same thing as 1.0 to a controller that clips to [-1, 1].
    Target-side clipping is acceptable only if it leaves the requested physical
    target unchanged. Otherwise the compiler refuses rather than silently
    claiming action-space conversion success.
    """
    source_target = command_to_target_qpos(
        source_contract,
        source_state,
        source_native_action,
    )
    target_native, representable = target_qpos_to_native_action(
        target_contract,
        target_state,
        source_target,
    )
    target_target = command_to_target_qpos(
        target_contract,
        target_state,
        target_native,
    )

    residual = target_target - source_target
    max_abs = float(np.max(np.abs(residual)))
    changed = tuple(int(i) for i in np.flatnonzero(np.abs(residual) > atol))

    if not np.all(representable):
        kind = EffectCommutationKind.TARGET_EFFECT_CHANGES_SEMANTICS
        reason = (
            "target preprocessing would saturate at least one coordinate and "
            "change the requested physical target"
        )
        authorized = False
    elif max_abs > atol:
        kind = EffectCommutationKind.SEMANTIC_RESIDUAL
        reason = (
            "target decode does not reconstruct the source effective physical target"
        )
        authorized = False
    else:
        kind = EffectCommutationKind.EXACT
        reason = (
            "source and target preprocessing effects commute with transport "
            "at the declared physical target"
        )
        authorized = True

    return EffectCommutationCertificate(
        kind=kind,
        authorized=authorized,
        source_effective_target=source_target,
        target_native_action=target_native,
        target_effective_target=target_target,
        representable_mask=representable,
        semantic_residual=residual,
        max_abs_residual=max_abs,
        changed_coordinates=changed,
        reason=reason,
    )
