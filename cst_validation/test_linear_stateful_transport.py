import numpy as np

from linear_stateful_transport import (
    LinearSemanticTransducer,
    StatefulTransportKind,
    synthesize_linear_stateful_transport,
)


def _target_delta_source():
    # z is the previous target. u is the physical target increment.
    # y is the next physical target.
    return LinearSemanticTransducer(
        A=np.array([[1.0]]),
        B=np.array([[1.0]]),
        C=np.array([[1.0]]),
        D=np.array([[1.0]]),
    )


def _absolute_stateless_target():
    # No hidden state. The native action itself is the physical target.
    return LinearSemanticTransducer(
        A=np.empty((0, 0)),
        B=np.empty((0, 1)),
        C=np.empty((1, 0)),
        D=np.array([[1.0]]),
    )


def test_target_delta_to_absolute_has_no_stateless_action_only_solution():
    cert = synthesize_linear_stateful_transport(
        _target_delta_source(),
        _absolute_stateless_target(),
        allow_source_state_feedback=False,
    )

    assert not cert.exact
    assert cert.kind is StatefulTransportKind.NO_LINEAR_SIMULATION
    assert cert.max_abs_residual > 0.0


def test_target_delta_to_absolute_synthesizes_stateful_handshake():
    cert = synthesize_linear_stateful_transport(
        _target_delta_source(),
        _absolute_stateless_target(),
        allow_source_state_feedback=True,
    )

    assert cert.exact
    assert cert.kind is StatefulTransportKind.EXACT
    # u_absolute = previous_target + delta.
    np.testing.assert_allclose(cert.source_state_feedback, [[1.0]], atol=1e-12)
    np.testing.assert_allclose(cert.action_adapter, [[1.0]], atol=1e-12)


def test_same_stateful_controller_uses_identity_relation_and_action():
    source = LinearSemanticTransducer(
        A=np.array([[0.8]]),
        B=np.array([[0.2]]),
        C=np.array([[1.5]]),
        D=np.array([[0.4]]),
    )
    cert = synthesize_linear_stateful_transport(source, source)

    assert cert.exact
    np.testing.assert_allclose(cert.state_relation, [[1.0]], atol=1e-10)
    np.testing.assert_allclose(cert.source_state_feedback, [[0.0]], atol=1e-10)
    np.testing.assert_allclose(cert.action_adapter, [[1.0]], atol=1e-10)


def test_dynamic_closure_rejects_output_only_match():
    # At one step both controllers can expose y=u, but target hidden dynamics
    # integrate u while source hidden state remains fixed.  A claim that only
    # checks output equality would miss the next-step semantic mismatch.
    source = LinearSemanticTransducer(
        A=np.array([[1.0]]),
        B=np.array([[0.0]]),
        C=np.array([[0.0]]),
        D=np.array([[1.0]]),
    )
    target = LinearSemanticTransducer(
        A=np.array([[1.0]]),
        B=np.array([[1.0]]),
        C=np.array([[0.0]]),
        D=np.array([[1.0]]),
    )
    cert = synthesize_linear_stateful_transport(
        source,
        target,
        allow_source_state_feedback=False,
    )

    assert not cert.exact
    assert np.max(np.abs(cert.dynamics_action_residual)) > 0.0


def test_redundant_target_adapter_reports_solution_ambiguity():
    source = LinearSemanticTransducer(
        A=np.empty((0, 0)),
        B=np.empty((0, 1)),
        C=np.empty((1, 0)),
        D=np.array([[1.0]]),
    )
    target = LinearSemanticTransducer(
        A=np.empty((0, 0)),
        B=np.empty((0, 2)),
        C=np.empty((1, 0)),
        D=np.array([[1.0, 1.0]]),
    )
    cert = synthesize_linear_stateful_transport(source, target)

    assert cert.exact
    assert cert.solution_nullity >= 1
    np.testing.assert_allclose(
        target.D @ cert.action_adapter,
        source.D,
        atol=1e-12,
    )


def test_approximation_budget_does_not_relabel_exactness():
    source = LinearSemanticTransducer(
        A=np.empty((0, 0)),
        B=np.empty((0, 1)),
        C=np.empty((2, 0)),
        D=np.eye(2)[:, :1],
    )
    target = LinearSemanticTransducer(
        A=np.empty((0, 0)),
        B=np.empty((0, 1)),
        C=np.empty((2, 0)),
        D=np.array([[0.0], [1.0]]),
    )
    cert = synthesize_linear_stateful_transport(
        source,
        target,
        approximate_tolerance=2.0,
    )

    assert not cert.exact
    assert cert.kind is StatefulTransportKind.APPROXIMATE
