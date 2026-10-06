import numpy as np

from state_handshake import (
    HandshakeStatus,
    synthesize_controller_state_handshake,
    verify_handshake_rollout,
)


def test_exact_handshake_allows_target_to_have_extra_hidden_state():
    # Source has one state. Target has an extra hidden/filter state that does
    # not affect the physical output.
    A_s = np.array([[0.5]])
    B_s = np.array([[1.0]])
    C_s = np.array([[1.0]])

    A_t = np.array([[0.5, 0.0], [0.0, 0.2]])
    B_t = np.array([[1.0], [0.0]])
    C_t = np.array([[1.0, 0.0]])

    cert = synthesize_controller_state_handshake(
        A_s, B_s, C_s, A_t, B_t, C_t
    )

    assert cert.status is HandshakeStatus.EXACT
    assert cert.state_map.shape == (2, 1)
    np.testing.assert_allclose(C_t @ cert.state_map, C_s, atol=1e-10)


def test_handshake_maps_controller_memory_not_just_action_coordinates():
    # Source has physical q plus a remembered target r. Target uses the same
    # physical output but a differently scaled internal reference coordinate.
    A_s = np.array([[0.7, 0.2], [0.0, 1.0]])
    B_s = np.array([[0.5], [1.0]])
    C_s = np.array([[1.0, 0.0]])

    H_true = np.array([[1.0, 0.0], [0.0, 2.0]])
    A_t = H_true @ A_s @ np.linalg.inv(H_true)
    B_t = np.eye(2)
    C_t = C_s @ np.linalg.inv(H_true)

    cert = synthesize_controller_state_handshake(
        A_s, B_s, C_s, A_t, B_t, C_t
    )

    assert cert.status is HandshakeStatus.EXACT
    np.testing.assert_allclose(C_t @ cert.state_map, C_s, atol=1e-9)
    np.testing.assert_allclose(
        A_t @ cert.state_map + B_t @ cert.state_feedback,
        cert.state_map @ A_s,
        atol=1e-9,
    )
    np.testing.assert_allclose(
        B_t @ cert.action_map,
        cert.state_map @ B_s,
        atol=1e-9,
    )


def test_exact_handshake_preserves_outputs_over_rollout():
    A_s = np.array([[0.6]])
    B_s = np.array([[0.4]])
    C_s = np.array([[1.0]])
    A_t = np.array([[0.2, 0.0], [0.0, 0.1]])
    B_t = np.eye(2)
    C_t = np.array([[1.0, 0.0]])

    cert = synthesize_controller_state_handshake(
        A_s, B_s, C_s, A_t, B_t, C_t
    )
    assert cert.status is HandshakeStatus.EXACT

    actions = np.array([[0.2], [-0.5], [1.0], [0.0], [0.3]])
    y_s, y_t = verify_handshake_rollout(
        cert,
        A_s,
        B_s,
        C_s,
        A_t,
        B_t,
        C_t,
        np.array([0.7]),
        actions,
    )
    np.testing.assert_allclose(y_t, y_s, atol=1e-9)


def test_output_incompatibility_is_not_hidden_by_action_fitting():
    A_s = np.array([[0.5]])
    B_s = np.array([[1.0]])
    C_s = np.array([[1.0]])

    A_t = np.array([[0.5]])
    B_t = np.array([[1.0]])
    C_t = np.array([[0.0]])

    cert = synthesize_controller_state_handshake(
        A_s,
        B_s,
        C_s,
        A_t,
        B_t,
        C_t,
        approximate_relative_tolerance=0.01,
    )
    assert cert.status is HandshakeStatus.IMPOSSIBLE
    assert cert.output_residual > 0.9


def test_random_conjugate_systems_have_exact_handshakes():
    rng = np.random.default_rng(42)
    for _ in range(100):
        n = 3
        m = 2
        H = rng.normal(size=(n, n))
        while abs(np.linalg.det(H)) < 0.2:
            H = rng.normal(size=(n, n))
        A_s = rng.normal(scale=0.1, size=(n, n))
        B_s = rng.normal(scale=0.2, size=(n, m))
        C_s = rng.normal(size=(2, n))

        H_inv = np.linalg.inv(H)
        A_t = H @ A_s @ H_inv
        B_t = np.eye(n)
        C_t = C_s @ H_inv

        cert = synthesize_controller_state_handshake(
            A_s, B_s, C_s, A_t, B_t, C_t
        )
        assert cert.status is HandshakeStatus.EXACT
        assert cert.relative_residual < 1e-9
