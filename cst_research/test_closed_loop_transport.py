import numpy as np

from closed_loop_transport import (
    TransportStatus,
    certify_finite_horizon_transport,
    rollout_linear_system,
    synthesize_local_closed_loop_transport,
)


def test_exact_transport_recovers_action_and_state_compensation():
    A_s = np.array([[0.8, 0.0], [0.0, 0.5]])
    B_s = np.array([[1.0], [0.0]])
    A_t = np.array([[0.8, 0.0], [0.0, 0.1]])
    B_t = np.eye(2)

    cert = synthesize_local_closed_loop_transport(A_s, B_s, A_t, B_t)

    assert cert.status is TransportStatus.EXACT
    assert cert.exact_possible
    np.testing.assert_allclose(A_t + B_t @ cert.K_state, A_s, atol=1e-12)
    np.testing.assert_allclose(B_t @ cert.K_action, B_s, atol=1e-12)
    # The hidden/augmented second state needs an explicit handshake term.
    assert abs(cert.K_state[1, 1]) > 0.0


def test_exact_transport_can_be_impossible_even_when_action_dimensions_match():
    A_s = np.zeros((2, 2))
    B_s = np.eye(2)
    A_t = np.zeros((2, 2))
    # Target has two action coordinates, but both only actuate state dimension 0.
    B_t = np.array([[1.0, 1.0], [0.0, 0.0]])

    cert = synthesize_local_closed_loop_transport(
        A_s,
        B_s,
        A_t,
        B_t,
        approximate_relative_tolerance=0.01,
    )

    assert cert.status is TransportStatus.IMPOSSIBLE
    assert not cert.exact_possible
    assert cert.exact_impossibility_lower_bound > 0.9
    assert abs(cert.witness_unmatched_direction[1]) > 0.99


def test_small_unmatched_component_is_explicitly_approximate_not_exact():
    A_s = np.zeros((2, 2))
    A_t = np.zeros((2, 2))
    B_t = np.array([[1.0], [0.0]])
    B_s = np.array([[1.0], [1e-3]])

    cert = synthesize_local_closed_loop_transport(
        A_s,
        B_s,
        A_t,
        B_t,
        approximate_relative_tolerance=1e-2,
    )

    assert cert.status is TransportStatus.APPROXIMATE
    assert not cert.exact_possible
    assert 0.0 < cert.relative_residual < 1e-2


def test_finite_horizon_certificate_upper_bounds_observed_rollout_error():
    A_s = np.array([[0.55]])
    B_s = np.array([[1.0]])
    A_t = np.array([[0.50]])
    B_t = np.array([[0.99]])

    # Force a deliberately approximate adapter by perturbing the synthesized
    # action gain after synthesis through a slightly mismatched source model.
    cert = synthesize_local_closed_loop_transport(
        A_s,
        B_s,
        A_t,
        B_t,
        exact_rtol=1e-12,
    )
    fh = certify_finite_horizon_transport(
        cert,
        A_s,
        B_s,
        A_t,
        B_t,
        horizon=12,
        source_state_radius=2.0,
        source_action_radius=1.0,
    )

    rng = np.random.default_rng(20261006)
    for _ in range(200):
        x0 = rng.uniform(-0.5, 0.5, size=(1,))
        actions = rng.uniform(-1.0, 1.0, size=(12, 1))
        source = rollout_linear_system(A_s, B_s, x0, actions)

        target_actions = []
        x_t = x0.copy()
        target_states = [x_t.copy()]
        for u_s in actions:
            u_t = cert.K_state @ x_t + cert.K_action @ u_s
            target_actions.append(u_t)
            x_t = A_t @ x_t + B_t @ u_t
            target_states.append(x_t.copy())
        target = np.stack(target_states)

        observed = float(np.max(np.linalg.norm(target - source, axis=1)))
        assert observed <= fh.error_bound + 1e-10


def test_projection_residual_is_a_constructive_impossibility_witness():
    A_s = np.zeros((3, 3))
    A_t = np.zeros((3, 3))
    B_s = np.eye(3)
    B_t = np.array([[1.0], [0.0], [0.0]])

    cert = synthesize_local_closed_loop_transport(
        A_s,
        B_s,
        A_t,
        B_t,
        approximate_relative_tolerance=0.0,
    )

    demand = np.concatenate([A_s - A_t, B_s], axis=1)
    requested = demand @ cert.witness_input
    matched = B_t @ (np.linalg.pinv(B_t) @ requested)
    unmatched = requested - matched

    assert cert.status is TransportStatus.IMPOSSIBLE
    assert np.linalg.norm(unmatched) > 0.9
    direction = unmatched / np.linalg.norm(unmatched)
    assert abs(float(direction @ cert.witness_unmatched_direction)) > 0.999999


def test_random_exact_cases_are_recovered_without_tuning():
    rng = np.random.default_rng(9)
    for _ in range(250):
        n = 4
        m_s = 2
        m_t = 4
        B_t = rng.normal(size=(n, m_t))
        while np.linalg.matrix_rank(B_t) < n:
            B_t = rng.normal(size=(n, m_t))
        A_t = rng.normal(scale=0.1, size=(n, n))
        K_x_true = rng.normal(scale=0.2, size=(m_t, n))
        K_u_true = rng.normal(scale=0.2, size=(m_t, m_s))
        A_s = A_t + B_t @ K_x_true
        B_s = B_t @ K_u_true

        cert = synthesize_local_closed_loop_transport(A_s, B_s, A_t, B_t)
        assert cert.status is TransportStatus.EXACT
        np.testing.assert_allclose(A_t + B_t @ cert.K_state, A_s, atol=1e-9)
        np.testing.assert_allclose(B_t @ cert.K_action, B_s, atol=1e-9)
