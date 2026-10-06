import numpy as np

from closed_loop_probe import (
    certify_black_box_closed_loop_transport,
    estimate_effect_jacobian,
    validate_adapter_on_heldout,
)


def test_two_scale_estimator_recovers_linear_effect_exactly():
    matrix = np.array([[2.0, -1.0], [0.5, 3.0]])
    bias = np.array([0.3, -0.2])

    est = estimate_effect_jacobian(
        lambda u: matrix @ u + bias,
        np.array([0.2, -0.4]),
        epsilon=1e-3,
    )

    np.testing.assert_allclose(est.jacobian, matrix, atol=1e-10)
    assert est.stable
    assert est.query_count == 8


def test_two_scale_estimator_rejects_nonlinear_scale_instability():
    def query(u):
        return np.array([u[0] ** 3])

    est = estimate_effect_jacobian(
        query,
        np.array([0.0]),
        epsilon=0.5,
        max_scale_instability=0.1,
    )

    assert not est.stable
    assert est.scale_instability > 0.1


def test_heldout_validation_compares_effects_not_controller_offsets():
    source = lambda u: np.array([2.0 * u[0] + 10.0])
    target = lambda u: np.array([4.0 * u[0] - 7.0])
    adapter = np.array([[0.5]])

    witness = validate_adapter_on_heldout(
        source,
        target,
        source_action0=np.array([0.1]),
        target_action0=np.array([-0.2]),
        adapter=adapter,
        heldout_source_deltas=np.array([[0.2], [-0.3], [0.7]]),
        tolerance=1e-10,
    )

    assert witness.accepted
    assert witness.max_l2_residual < 1e-10


def test_black_box_pipeline_certifies_exact_scaled_controller_pair():
    source = lambda u: np.array([u[0], 2.0 * u[1]])
    target = lambda u: np.array([2.0 * u[0], u[1]])

    cert = certify_black_box_closed_loop_transport(
        source,
        target,
        source_action0=np.zeros(2),
        target_action0=np.zeros(2),
        source_epsilon=1e-3,
        target_epsilon=1e-3,
        heldout_source_deltas=np.array(
            [[0.2, -0.1], [-0.3, 0.4], [0.7, 0.2]]
        ),
        heldout_tolerance=1e-9,
    )

    assert cert.authorized
    np.testing.assert_allclose(
        cert.local_transport.adapter,
        np.array([[0.5, 0.0], [0.0, 2.0]]),
        atol=1e-9,
    )


def test_black_box_pipeline_refuses_missing_executable_direction():
    source = lambda u: np.array([u[0], u[1]])
    target = lambda u: np.array([u[0], 0.0])

    cert = certify_black_box_closed_loop_transport(
        source,
        target,
        source_action0=np.zeros(2),
        target_action0=np.zeros(2),
        source_epsilon=1e-3,
        target_epsilon=1e-3,
        heldout_source_deltas=np.array([[0.0, 0.2], [0.1, -0.3]]),
        heldout_tolerance=1e-6,
    )

    assert not cert.authorized
    assert cert.local_transport is not None
    assert not cert.local_transport.exact
    assert cert.heldout is not None
    assert not cert.heldout.accepted


def test_heldout_counterexample_blocks_locally_linear_but_globally_bad_adapter():
    source = lambda u: np.array([u[0]])
    target = lambda u: np.array([u[0] + 3.0 * u[0] ** 3])

    cert = certify_black_box_closed_loop_transport(
        source,
        target,
        source_action0=np.zeros(1),
        target_action0=np.zeros(1),
        source_epsilon=1e-4,
        target_epsilon=1e-4,
        heldout_source_deltas=np.array([[0.5], [-0.5]]),
        heldout_tolerance=0.05,
        max_scale_instability=0.15,
    )

    assert cert.local_transport is not None
    assert cert.local_transport.exact
    assert cert.heldout is not None
    assert not cert.heldout.accepted
    assert not cert.authorized
