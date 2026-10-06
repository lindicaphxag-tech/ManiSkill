import numpy as np

from closed_loop_transport import (
    LinearClosedLoopModel,
    certify_finite_horizon_deviation,
    synthesize_closed_loop_transport,
)


def test_identical_models_need_identity_action_transport_only():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[2.0]]))

    cert = synthesize_closed_loop_transport(source, target)

    assert cert.exact
    np.testing.assert_allclose(cert.state_gain, [[0.0]], atol=1e-12)
    np.testing.assert_allclose(cert.action_gain, [[0.5]], atol=1e-12)
    np.testing.assert_allclose(cert.state_residual, 0.0, atol=1e-12)
    np.testing.assert_allclose(cert.action_residual, 0.0, atol=1e-12)


def test_state_feedback_compensates_controller_dynamics_mismatch():
    # Source x' = 0.9 x + u.
    # Target x' = 0.5 x + 2 u_tgt.
    # u_tgt = 0.2 x + 0.5 u exactly reconstructs the source step.
    source = LinearClosedLoopModel(A=np.array([[0.9]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.5]]), B=np.array([[2.0]]))

    cert = synthesize_closed_loop_transport(source, target)

    assert cert.exact
    np.testing.assert_allclose(cert.state_gain, [[0.2]], atol=1e-12)
    np.testing.assert_allclose(cert.action_gain, [[0.5]], atol=1e-12)


def test_rank_deficient_target_returns_structural_impossibility_witness():
    # Target can affect only x[0]. Source can directly affect x[1].
    source = LinearClosedLoopModel(A=np.zeros((2, 2)), B=np.eye(2))
    target = LinearClosedLoopModel(
        A=np.zeros((2, 2)),
        B=np.array([[1.0], [0.0]]),
    )

    cert = synthesize_closed_loop_transport(source, target)

    assert not cert.exact
    assert cert.unavoidable_operator_residual > 0.99
    assert np.linalg.norm(cert.witness_residual) > 0.99

    requested = np.concatenate([source.A - target.A, source.B], axis=1)
    witness = np.concatenate([cert.witness_state, cert.witness_action])
    # The returned witness is an actual requested source direction.
    np.testing.assert_allclose(
        cert.witness_residual,
        (np.eye(2) - target.B @ np.linalg.pinv(target.B))
        @ requested
        @ witness,
        atol=1e-12,
    )


def test_dynamics_mismatch_can_be_structurally_unrepresentable_even_with_no_action_mismatch():
    source = LinearClosedLoopModel(
        A=np.array([[1.0, 0.0], [0.0, 0.5]]),
        B=np.array([[1.0], [0.0]]),
    )
    target = LinearClosedLoopModel(
        A=np.array([[1.0, 0.0], [0.0, 0.1]]),
        B=np.array([[1.0], [0.0]]),
    )

    cert = synthesize_closed_loop_transport(source, target)

    assert not cert.exact
    assert cert.max_action_residual_norm <= 1e-12
    assert cert.max_state_residual_norm > 0.39
    assert cert.unavoidable_operator_residual > 0.39


def test_redundant_target_uses_minimum_norm_adapter():
    source = LinearClosedLoopModel(A=np.zeros((1, 1)), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(
        A=np.zeros((1, 1)),
        B=np.array([[1.0, 1.0]]),
    )

    cert = synthesize_closed_loop_transport(source, target)

    assert cert.exact
    np.testing.assert_allclose(cert.action_gain[:, 0], [0.5, 0.5], atol=1e-12)


def test_exact_transport_has_zero_finite_horizon_error_from_same_initial_state():
    source = LinearClosedLoopModel(A=np.array([[0.8]]), B=np.array([[1.0]]))
    target = LinearClosedLoopModel(A=np.array([[0.5]]), B=np.array([[2.0]]))
    transport = synthesize_closed_loop_transport(source, target)

    horizon = certify_finite_horizon_deviation(
        source,
        target,
        transport,
        horizon=50,
        source_state_radius=2.0,
        source_action_radius=1.0,
        initial_error_bound=0.0,
    )

    assert horizon.exact_if_same_initial_state
    assert horizon.final_error_bound <= 1e-12
    np.testing.assert_allclose(horizon.trajectory_error_bounds, 0.0, atol=1e-12)


def test_contracting_approximate_transport_has_geometric_error_bound():
    # Target cannot produce the second coordinate exactly, but its propagated
    # error is contractive.
    source = LinearClosedLoopModel(
        A=np.diag([0.5, 0.25]),
        B=np.eye(2),
    )
    target = LinearClosedLoopModel(
        A=np.diag([0.5, 0.25]),
        B=np.array([[1.0], [0.0]]),
    )
    transport = synthesize_closed_loop_transport(source, target)

    horizon = certify_finite_horizon_deviation(
        source,
        target,
        transport,
        horizon=8,
        source_state_radius=1.0,
        source_action_radius=0.2,
    )

    assert not transport.exact
    assert horizon.contraction_factor < 1.0
    assert horizon.per_step_model_defect_bound > 0.0
    assert np.all(np.diff(horizon.trajectory_error_bounds) >= -1e-12)

    delta = horizon.per_step_model_defect_bound
    rho = horizon.contraction_factor
    expected = delta * (1.0 - rho**8) / (1.0 - rho)
    np.testing.assert_allclose(horizon.final_error_bound, expected, rtol=1e-12, atol=1e-12)


def test_random_exact_reparameterizations_remain_exact():
    rng = np.random.default_rng(20261006)
    for _ in range(200):
        n = 4
        m = 4
        B_target = rng.normal(size=(n, m))
        while np.linalg.matrix_rank(B_target) < n:
            B_target = rng.normal(size=(n, m))
        Kx_true = rng.normal(scale=0.1, size=(m, n))
        Ku_true = rng.normal(scale=0.1, size=(m, m))
        A_target = rng.normal(scale=0.2, size=(n, n))
        A_source = A_target + B_target @ Kx_true
        B_source = B_target @ Ku_true

        cert = synthesize_closed_loop_transport(
            LinearClosedLoopModel(A=A_source, B=B_source),
            LinearClosedLoopModel(A=A_target, B=B_target),
        )

        assert cert.exact
        assert cert.unavoidable_operator_residual < 1e-9
