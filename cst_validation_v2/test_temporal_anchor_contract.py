import numpy as np
import pytest

from temporal_anchor_contract import (
    absolute_actions_with_contract,
    relative_actions_with_contract,
    resolve_temporal_anchor,
    select_temporal_anchor,
)


def test_negative_history_resolves_current_to_last_slot():
    contract = resolve_temporal_anchor([-150, -120, -90, -60, -30, 0])
    assert contract.anchor_index == 5


def test_future_window_resolves_current_to_first_slot():
    contract = resolve_temporal_anchor([0, 4, 8, 12])
    assert contract.anchor_index == 0


def test_missing_or_duplicate_current_refuses():
    with pytest.raises(ValueError):
        resolve_temporal_anchor([-2, -1])
    with pytest.raises(ValueError):
        resolve_temporal_anchor([-1, 0, 0])


def test_relative_conversion_uses_semantic_current_not_array_slot_zero():
    history = np.array([[[10.0, 20.0], [11.0, 21.0], [12.0, 22.0]]])
    actions = np.array([[[13.0, 25.0], [14.0, 28.0]]])
    contract = resolve_temporal_anchor([-2, -1, 0])
    relative = relative_actions_with_contract(actions, history, contract)
    np.testing.assert_allclose(relative, [[[1.0, 3.0], [2.0, 6.0]]])
    wrong_oldest = actions - history[:, :1, :]
    assert not np.allclose(relative, wrong_oldest)


def test_wrong_anchor_can_roundtrip_and_still_be_semantically_wrong():
    history = np.array([[[0.0], [10.0]]])
    actions = np.array([[[12.0], [13.0]]])

    # A hard-coded slot-zero implementation yields [12,13] and can invert
    # itself perfectly, so a plain round-trip test is insufficient.
    wrong_relative = actions - history[:, :1, :]
    wrong_recovered = wrong_relative + history[:, :1, :]
    np.testing.assert_allclose(wrong_recovered, actions)

    contract = resolve_temporal_anchor([-1, 0])
    correct = relative_actions_with_contract(actions, history, contract)
    np.testing.assert_allclose(correct, [[[2.0], [3.0]]])
    assert not np.allclose(correct, wrong_relative)
    np.testing.assert_allclose(
        absolute_actions_with_contract(correct, history, contract), actions
    )


def test_anchor_selection_accepts_batched_and_unbatched_histories():
    contract = resolve_temporal_anchor([-1, 0])
    unbatched = np.array([[1.0, 2.0], [3.0, 4.0]])
    batched = unbatched[None]
    np.testing.assert_allclose(select_temporal_anchor(unbatched, contract), [3.0, 4.0])
    np.testing.assert_allclose(select_temporal_anchor(batched, contract), [[3.0, 4.0]])
