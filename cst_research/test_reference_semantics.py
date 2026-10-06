import numpy as np

from reference_semantics import (
    ReferenceKind,
    ReferenceSemantics,
    decode_reference_trace,
    transport_reference_semantics,
)


def sem(kind, d=1):
    return ReferenceSemantics(kind=kind, relative_mask=np.ones(d, dtype=bool))


def test_same_numbers_mean_different_goals_for_chunk_relative_and_sequential_delta():
    actions = np.array([[1.0], [2.0], [3.0]])
    states = np.array([[10.0], [10.5], [11.0]])
    anchor = np.array([10.0])

    relative = decode_reference_trace(
        actions,
        sem(ReferenceKind.CHUNK_ANCHOR),
        current_states=states,
        chunk_anchor=anchor,
    )
    sequential = decode_reference_trace(
        actions,
        sem(ReferenceKind.PREVIOUS_COMMAND),
        current_states=states,
        chunk_anchor=anchor,
    )

    np.testing.assert_allclose(relative.goals[:, 0], [11.0, 12.0, 13.0])
    np.testing.assert_allclose(sequential.goals[:, 0], [11.0, 13.0, 16.0])


def test_current_state_delta_differs_from_chunk_anchor_when_robot_moves():
    actions = np.array([[1.0], [1.0], [1.0]])
    states = np.array([[10.0], [10.4], [10.9]])
    anchor = np.array([10.0])

    current = decode_reference_trace(
        actions,
        sem(ReferenceKind.CURRENT_STATE),
        current_states=states,
    )
    chunk = decode_reference_trace(
        actions,
        sem(ReferenceKind.CHUNK_ANCHOR),
        current_states=states,
        chunk_anchor=anchor,
    )

    np.testing.assert_allclose(current.goals[:, 0], [11.0, 11.4, 11.9])
    np.testing.assert_allclose(chunk.goals[:, 0], [11.0, 11.0, 11.0])


def test_chunk_relative_to_absolute_transport_is_exact():
    actions = np.array([[0.2, -0.1], [0.4, 0.3], [-0.2, 0.5]])
    states = np.array([[1.0, 2.0], [1.1, 1.9], [1.2, 2.1]])
    anchor = np.array([1.0, 2.0])

    out = transport_reference_semantics(
        actions,
        sem(ReferenceKind.CHUNK_ANCHOR, 2),
        sem(ReferenceKind.ABSOLUTE, 2),
        current_states=states,
        source_chunk_anchor=anchor,
    )

    assert out.exact
    np.testing.assert_allclose(
        out.target_actions,
        [[1.2, 1.9], [1.4, 2.3], [0.8, 2.5]],
    )


def test_chunk_relative_to_sequential_delta_requires_stateful_reencoding():
    actions = np.array([[1.0], [2.0], [3.0]])
    states = np.array([[10.0], [10.0], [10.0]])
    anchor = np.array([10.0])

    out = transport_reference_semantics(
        actions,
        sem(ReferenceKind.CHUNK_ANCHOR),
        sem(ReferenceKind.PREVIOUS_COMMAND),
        current_states=states,
        source_chunk_anchor=anchor,
        target_chunk_anchor=anchor,
    )

    assert out.exact
    # Source goals are 11, 12, 13. Sequential encoding must therefore be
    # +1, +1, +1 rather than copying the source values +1, +2, +3.
    np.testing.assert_allclose(out.target_actions[:, 0], [1.0, 1.0, 1.0])


def test_controller_target_reference_is_not_previous_command_by_definition():
    actions = np.array([[0.5], [0.5], [0.5]])
    states = np.zeros((3, 1))
    controller_targets = np.array([[1.0], [1.2], [1.25]])

    decoded = decode_reference_trace(
        actions,
        sem(ReferenceKind.CONTROLLER_TARGET),
        current_states=states,
        controller_targets_before=controller_targets,
    )
    previous_command = decode_reference_trace(
        actions,
        sem(ReferenceKind.PREVIOUS_COMMAND),
        current_states=states,
        initial_previous_command=np.array([1.0]),
    )

    np.testing.assert_allclose(decoded.goals[:, 0], [1.5, 1.7, 1.75])
    np.testing.assert_allclose(previous_command.goals[:, 0], [1.5, 2.0, 2.5])


def test_absolute_gripper_can_be_masked_while_arm_is_relative():
    semantics = ReferenceSemantics(
        kind=ReferenceKind.CHUNK_ANCHOR,
        relative_mask=np.array([True, True, False]),
    )
    actions = np.array([[0.1, -0.2, 0.8], [0.3, 0.4, -0.5]])
    states = np.array([[1.0, 2.0, 0.0], [1.1, 2.1, 0.0]])
    decoded = decode_reference_trace(
        actions,
        semantics,
        current_states=states,
        chunk_anchor=np.array([1.0, 2.0, 123.0]),
    )

    np.testing.assert_allclose(
        decoded.goals,
        [[1.1, 1.8, 0.8], [1.3, 2.4, -0.5]],
    )
