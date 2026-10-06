import numpy as np

from jit_reference_adapter import JustInTimeReferenceAdapter
from reference_semantics import ReferenceKind, ReferenceSemantics


def sem(kind, dim=1, mask=None):
    if mask is None:
        mask = np.ones(dim, dtype=bool)
    return ReferenceSemantics(kind=kind, relative_mask=np.asarray(mask, dtype=bool))


def test_chunk_anchor_to_current_state_jit_preserves_goal_trace():
    source_actions = np.array([[1.0], [2.0], [3.0]])
    adapter = JustInTimeReferenceAdapter(
        sem(ReferenceKind.CHUNK_ANCHOR),
        sem(ReferenceKind.CURRENT_STATE),
        source_chunk_anchor=np.array([10.0]),
    )

    current = np.array([10.0])
    target_actions = []
    goals = []
    for action in source_actions:
        out = adapter.step(action, current_state=current)
        target_actions.append(out.target_native_action.copy())
        goals.append(out.physical_goal.copy())
        # Ideal current-state-relative controller reaches the encoded goal.
        current = current + out.target_native_action

    np.testing.assert_allclose(np.asarray(goals)[:, 0], [11.0, 12.0, 13.0])
    np.testing.assert_allclose(np.asarray(target_actions)[:, 0], [1.0, 1.0, 1.0])
    np.testing.assert_allclose(current, [13.0])


def test_copying_chunk_relative_numbers_into_current_state_delta_drifts():
    # Same source chunk as above, but naively copy its native numbers.
    current = 10.0
    reached = []
    for delta in [1.0, 2.0, 3.0]:
        current = current + delta
        reached.append(current)
    assert reached == [11.0, 13.0, 16.0]
    assert max(abs(a - b) for a, b in zip(reached, [11.0, 12.0, 13.0])) == 3.0


def test_controller_target_target_is_encoded_just_in_time():
    adapter = JustInTimeReferenceAdapter(
        sem(ReferenceKind.CHUNK_ANCHOR),
        sem(ReferenceKind.CONTROLLER_TARGET),
        source_chunk_anchor=np.array([10.0]),
    )
    targets = [np.array([10.0]), np.array([10.5]), np.array([11.5])]
    actions = []
    for source_action, controller_target in zip(
        np.array([[1.0], [2.0], [3.0]]), targets
    ):
        out = adapter.step(
            source_action,
            current_state=np.array([0.0]),
            target_controller_target=controller_target,
        )
        actions.append(float(out.target_native_action[0]))
        assert out.max_abs_goal_error == 0.0
    np.testing.assert_allclose(actions, [1.0, 1.5, 1.5])


def test_mixed_relative_arm_absolute_gripper_is_preserved():
    mask = np.array([True, True, False])
    adapter = JustInTimeReferenceAdapter(
        sem(ReferenceKind.CHUNK_ANCHOR, 3, mask),
        sem(ReferenceKind.CURRENT_STATE, 3, mask),
        source_chunk_anchor=np.array([1.0, 2.0, 999.0]),
    )
    out = adapter.step(
        np.array([0.2, -0.1, 0.8]),
        current_state=np.array([1.1, 1.9, -123.0]),
    )
    np.testing.assert_allclose(out.physical_goal, [1.2, 1.9, 0.8])
    np.testing.assert_allclose(out.target_native_action, [0.1, 0.0, 0.8])


def test_previous_command_source_can_feed_absolute_target():
    adapter = JustInTimeReferenceAdapter(
        sem(ReferenceKind.PREVIOUS_COMMAND),
        sem(ReferenceKind.ABSOLUTE),
        source_previous_command=np.array([10.0]),
    )
    goals = []
    for action in np.array([[1.0], [2.0], [-0.5]]):
        out = adapter.step(action, current_state=np.array([0.0]))
        goals.append(float(out.target_native_action[0]))
    np.testing.assert_allclose(goals, [11.0, 13.0, 12.5])


def test_random_jit_bridge_preserves_chunk_anchor_goals_under_moving_state():
    rng = np.random.default_rng(20261006)
    max_error = 0.0
    traces = 1000
    horizon = 8
    dim = 6
    for _ in range(traces):
        anchor = rng.normal(size=dim)
        source_actions = rng.normal(scale=0.2, size=(horizon, dim))
        current = anchor + rng.normal(scale=0.05, size=dim)
        adapter = JustInTimeReferenceAdapter(
            sem(ReferenceKind.CHUNK_ANCHOR, dim),
            sem(ReferenceKind.CURRENT_STATE, dim),
            source_chunk_anchor=anchor,
        )
        for action in source_actions:
            out = adapter.step(action, current_state=current)
            expected = anchor + action
            max_error = max(
                max_error,
                float(np.max(np.abs(out.reconstructed_target_goal - expected))),
            )
            # Exercise changing execution state rather than perfect tracking.
            current = expected + rng.normal(scale=0.03, size=dim)

    assert max_error < 1e-12
