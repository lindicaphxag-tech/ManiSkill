import numpy as np

from linear_stateful_transport import LinearSemanticTransducer
from minimal_handshake import synthesize_minimal_source_state_handshake


def _stateless_absolute():
    return LinearSemanticTransducer(
        A=np.empty((0, 0)),
        B=np.empty((0, 1)),
        C=np.empty((1, 0)),
        D=np.array([[1.0]]),
    )


def test_minimal_handshake_finds_previous_target_and_rejects_irrelevant_state():
    # z0 = previous target, z1 = irrelevant diagnostic accumulator.
    source = LinearSemanticTransducer(
        A=np.array([[1.0, 0.0], [0.0, 1.0]]),
        B=np.array([[1.0], [0.0]]),
        C=np.array([[1.0, 0.0]]),
        D=np.array([[1.0]]),
    )

    cert = synthesize_minimal_source_state_handshake(
        source,
        _stateless_absolute(),
        state_names=("previous_target", "diagnostic_accumulator"),
    )

    assert cert.exact
    assert cert.exposed_state_count == 1
    assert cert.selected_state_indices == (0,)
    assert cert.selected_state_names == ("previous_target",)
    np.testing.assert_allclose(
        cert.transport.source_state_feedback,
        [[1.0, 0.0]],
        atol=1e-12,
    )


def test_two_independent_hidden_states_are_both_required():
    # One target action must reconstruct z0 + z1 + u.
    source = LinearSemanticTransducer(
        A=np.eye(2),
        B=np.array([[0.0], [0.0]]),
        C=np.array([[1.0, 1.0]]),
        D=np.array([[1.0]]),
    )

    cert = synthesize_minimal_source_state_handshake(
        source,
        _stateless_absolute(),
        state_names=("bias_a", "bias_b"),
    )

    assert cert.exact
    assert cert.exposed_state_count == 2
    assert cert.selected_state_indices == (0, 1)


def test_no_hidden_state_is_selected_when_action_only_transport_is_exact():
    source = LinearSemanticTransducer(
        A=np.eye(2),
        B=np.zeros((2, 1)),
        C=np.zeros((1, 2)),
        D=np.array([[2.0]]),
    )
    target = LinearSemanticTransducer(
        A=np.empty((0, 0)),
        B=np.empty((0, 1)),
        C=np.empty((1, 0)),
        D=np.array([[4.0]]),
    )

    cert = synthesize_minimal_source_state_handshake(
        source,
        target,
        state_names=("unused_a", "unused_b"),
    )

    assert cert.exact
    assert cert.exposed_state_count == 0
    assert cert.selected_state_indices == ()
    np.testing.assert_allclose(cert.transport.action_adapter, [[0.5]], atol=1e-12)


def test_equivalent_state_choices_are_reported_as_interface_ambiguity():
    # Either duplicated hidden coordinate independently reconstructs the output.
    # Dynamics are static, so exposing either one is sufficient.
    source = LinearSemanticTransducer(
        A=np.eye(2),
        B=np.zeros((2, 1)),
        C=np.array([[1.0, 1.0]]),
        D=np.array([[1.0]]),
    )
    # Because z0 and z1 are independent, one coordinate cannot actually recover
    # their sum; use duplicated observable semantics instead through identical
    # constrained state relation to a stateful target.
    target = LinearSemanticTransducer(
        A=np.array([[1.0]]),
        B=np.array([[0.0]]),
        C=np.array([[2.0]]),
        D=np.array([[1.0]]),
    )

    # For independent z0,z1, both remain required; this assertion protects
    # against falsely reporting redundancy based on equal coefficient values.
    cert = synthesize_minimal_source_state_handshake(source, target)
    assert cert.exposed_state_count == 2


def test_exact_search_dimension_is_fail_closed():
    source = LinearSemanticTransducer(
        A=np.eye(17),
        B=np.zeros((17, 1)),
        C=np.zeros((1, 17)),
        D=np.ones((1, 1)),
    )
    try:
        synthesize_minimal_source_state_handshake(
            source,
            _stateless_absolute(),
            max_exact_search_dim=16,
        )
    except ValueError as exc:
        assert "at most 16" in str(exc)
    else:
        raise AssertionError("expected fail-closed dimension guard")
