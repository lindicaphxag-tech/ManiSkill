import numpy as np

from closed_loop_certificate import (
    ClosedLoopTransportKind,
    certify_finite_horizon_behavior,
    synthesize_local_closed_loop_transport,
)


def test_exact_transport_recovers_scaled_target_chart():
    source = np.eye(2)
    target = 2.0 * np.eye(2)

    cert = synthesize_local_closed_loop_transport(source, target)

    assert cert.kind is ClosedLoopTransportKind.EXACT
    np.testing.assert_allclose(cert.adapter, 0.5 * np.eye(2), atol=1e-12)
    np.testing.assert_allclose(cert.reconstructed_source_effect, source, atol=1e-12)
    assert cert.worst_case_unit_action_lower_bound < 1e-12


def test_redundant_target_uses_minimum_norm_exact_adapter():
    # Three target coordinates can reproduce a two-dimensional source effect.
    source = np.eye(2)
    target = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])

    cert = synthesize_local_closed_loop_transport(source, target)

    assert cert.exact
    np.testing.assert_allclose(target @ cert.adapter, source, atol=1e-12)
    # Moore-Penrose solution is orthogonal to the target nullspace.
    null = np.array([1.0, 1.0, -1.0])
    np.testing.assert_allclose(null @ cert.adapter, np.zeros(2), atol=1e-12)


def test_missing_target_direction_produces_impossibility_witness():
    source = np.eye(2)
    target = np.array([[1.0], [0.0]])

    cert = synthesize_local_closed_loop_transport(source, target)

    assert cert.kind is ClosedLoopTransportKind.LOCALLY_UNREPRESENTABLE
    np.testing.assert_allclose(
        cert.irreducible_residual,
        np.array([[0.0, 0.0], [0.0, 1.0]]),
        atol=1e-12,
    )
    assert np.isclose(cert.worst_case_unit_action_lower_bound, 1.0)


def test_declared_approximation_budget_is_separate_from_exactness():
    source = np.eye(2)
    target = np.array([[1.0], [0.0]])

    cert = synthesize_local_closed_loop_transport(
        source,
        target,
        approximate_tolerance=1.1,
    )

    assert not cert.exact
    assert cert.kind is ClosedLoopTransportKind.APPROXIMATE


def test_augmented_hidden_state_exposes_false_physical_only_equivalence():
    # Physical-only observation sees both as identical: both move x by u.
    physical_source = np.array([[1.0]])
    physical_target = np.array([[1.0]])
    physical = synthesize_local_closed_loop_transport(
        physical_source,
        physical_target,
    )
    assert physical.exact

    # Augment the observable with controller-owned target state z.
    # Source updates (x,z) by (u,u), target can only update (x,z) by (u,0).
    augmented_source = np.array([[1.0], [1.0]])
    augmented_target = np.array([[1.0], [0.0]])
    augmented = synthesize_local_closed_loop_transport(
        augmented_source,
        augmented_target,
    )

    assert not augmented.exact
    assert augmented.kind is ClosedLoopTransportKind.LOCALLY_UNREPRESENTABLE
    assert augmented.worst_case_unit_action_lower_bound > 0.0


def test_contractive_horizon_bound_matches_geometric_recurrence():
    source = np.eye(2)
    target = np.array([[1.0], [0.0]])
    local = synthesize_local_closed_loop_transport(source, target)

    cert = certify_finite_horizon_behavior(
        local,
        contraction_factor=0.5,
        action_norm_bounds=np.ones(4),
    )

    np.testing.assert_allclose(
        cert.error_upper_bounds,
        [0.0, 1.0, 1.5, 1.75, 1.875],
        atol=1e-12,
    )
    assert np.isclose(cert.final_error_upper_bound, 1.875)
    assert np.isclose(cert.asymptotic_error_upper_bound, 2.0)
    assert cert.contractive


def test_exact_local_transport_has_zero_bound_without_model_slack():
    local = synthesize_local_closed_loop_transport(np.eye(3), np.eye(3))
    cert = certify_finite_horizon_behavior(
        local,
        contraction_factor=0.9,
        action_norm_bounds=np.array([1.0, 2.0, 3.0, 4.0]),
    )
    np.testing.assert_allclose(cert.error_upper_bounds, np.zeros(5), atol=1e-12)


def test_model_slack_is_not_hidden_inside_transport_claim():
    local = synthesize_local_closed_loop_transport(np.eye(1), np.eye(1))
    cert = certify_finite_horizon_behavior(
        local,
        contraction_factor=0.5,
        action_norm_bounds=np.ones(3),
        model_slack_bounds=np.array([0.2, 0.1, 0.0]),
    )
    np.testing.assert_allclose(
        cert.error_upper_bounds,
        [0.0, 0.2, 0.2, 0.1],
        atol=1e-12,
    )


def test_noncontractive_system_reports_no_asymptotic_certificate():
    local = synthesize_local_closed_loop_transport(
        np.eye(2),
        np.array([[1.0], [0.0]]),
    )
    cert = certify_finite_horizon_behavior(
        local,
        contraction_factor=1.0,
        action_norm_bounds=np.ones(3),
    )
    np.testing.assert_allclose(cert.error_upper_bounds, [0.0, 1.0, 2.0, 3.0])
    assert not cert.contractive
    assert cert.asymptotic_error_upper_bound is None
