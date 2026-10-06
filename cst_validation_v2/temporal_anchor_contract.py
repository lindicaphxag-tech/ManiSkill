from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class TemporalAnchorContract:
    """Bind a stacked observation slot to the physical prediction instant."""

    delta_indices: tuple[int, ...]
    anchor_delta: int
    anchor_index: int


def resolve_temporal_anchor(
    delta_indices: Sequence[int],
    *,
    anchor_delta: int = 0,
) -> TemporalAnchorContract:
    """Resolve the unique stacked slot representing one semantic time offset.

    Relative action semantics need a physical reference instant. The array
    position is an implementation detail; the delta value is the semantic
    identity. Refuse missing or duplicate anchors instead of guessing that
    slot zero means "current".
    """
    deltas = tuple(int(x) for x in delta_indices)
    if not deltas:
        raise ValueError("delta_indices must be non-empty")
    matches = [i for i, delta in enumerate(deltas) if delta == int(anchor_delta)]
    if len(matches) != 1:
        raise ValueError(
            f"anchor delta {anchor_delta} must occur exactly once; got {matches}"
        )
    return TemporalAnchorContract(
        delta_indices=deltas,
        anchor_delta=int(anchor_delta),
        anchor_index=matches[0],
    )


def select_temporal_anchor(
    stacked_state: np.ndarray,
    contract: TemporalAnchorContract,
) -> np.ndarray:
    """Select semantic anchor state from shape [B,T,D] or [T,D]."""
    state = np.asarray(stacked_state)
    if state.ndim not in (2, 3):
        raise ValueError("stacked_state must have shape [T,D] or [B,T,D]")
    time_axis = 0 if state.ndim == 2 else 1
    if state.shape[time_axis] != len(contract.delta_indices):
        raise ValueError("state history length does not match delta-index contract")
    return np.take(state, contract.anchor_index, axis=time_axis)


def relative_actions_with_contract(
    actions: np.ndarray,
    stacked_state: np.ndarray,
    contract: TemporalAnchorContract,
) -> np.ndarray:
    """Subtract the semantically named anchor rather than a hard-coded slot."""
    action = np.asarray(actions, dtype=float)
    anchor = np.asarray(select_temporal_anchor(stacked_state, contract), dtype=float)
    if action.ndim == 3:
        anchor = anchor[:, None, :]
    return action - anchor


def absolute_actions_with_contract(
    relative_actions: np.ndarray,
    stacked_state: np.ndarray,
    contract: TemporalAnchorContract,
) -> np.ndarray:
    relative = np.asarray(relative_actions, dtype=float)
    anchor = np.asarray(select_temporal_anchor(stacked_state, contract), dtype=float)
    if relative.ndim == 3:
        anchor = anchor[:, None, :]
    return relative + anchor
