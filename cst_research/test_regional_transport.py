import numpy as np

from regional_transport import (
    LinearizationSample,
    RegionalStatus,
    counterexample_guided_regional_synthesis,
    synthesize_shared_regional_adapter,
)


def _sample(point, A_s, B_s, A_t, B_t):
    return LinearizationSample(
        point=np.asarray(point, dtype=float),
        source_A=np.asarray(A_s, dtype=float),
        source_B=np.asarray(B_s, dtype=float),
        target_A=np.asarray(A_t, dtype=float),
        target_B=np.asarray(B_t, dtype=float),
    )


def test_one_adapter_can_be_exact_across_many_linearizations():
    rng = np.random.default_rng(20261006)
    K_x = np.array([[0.2, -0.1], [0.05, 0.3]])
    K_u = np.array([[1.1], [-0.4]])
    samples = []
    for i in range(20):
        A_t = rng.normal(scale=0.05, size=(2, 2))
        B_t = np.eye(2) + rng.normal(scale=0.01, size=(2, 2))
        A_s = A_t + B_t @ K_x
        B_s = B_t @ K_u
        samples.append(_sample([i], A_s, B_s, A_t, B_t))

    cert = synthesize_shared_regional_adapter(samples)

    assert cert.status is RegionalStatus.EXACT_ON_SAMPLES
    assert cert.max_relative_residual < 1e-10
    np.testing.assert_allclose(cert.K_state, K_x, atol=1e-9)
    np.testing.assert_allclose(cert.K_action, K_u, atol=1e-9)


def test_pointwise_exact_does_not_imply_one_region_wide_adapter():
    # At each state, target B=1 can exactly realize the source demand.
    # But the required state compensation changes sign, so no single K_x fits.
    samples = [
        _sample(
            [-1.0],
            [[0.5]],
            [[1.0]],
            [[0.0]],
            [[1.0]],
        ),
        _sample(
            [1.0],
            [[-0.5]],
            [[1.0]],
            [[0.0]],
            [[1.0]],
        ),
    ]

    for one in samples:
        local = synthesize_shared_regional_adapter([one])
        assert local.status is RegionalStatus.EXACT_ON_SAMPLES

    regional = synthesize_shared_regional_adapter(
        samples,
        approximate_relative_tolerance=0.1,
    )
    assert regional.status is RegionalStatus.INCONSISTENT
    assert regional.max_relative_residual > 0.4


def test_cegis_finds_hidden_worst_case_and_adds_it():
    compatible = [
        _sample([x], [[0.2]], [[1.0]], [[0.0]], [[1.0]])
        for x in (-1.0, -0.5, 0.0, 0.5)
    ]
    hidden_counterexample = _sample(
        [1.0],
        [[-0.8]],
        [[1.0]],
        [[0.0]],
        [[1.0]],
    )
    pool = compatible + [hidden_counterexample]

    trace = counterexample_guided_regional_synthesis(
        pool,
        seed_sample_index=0,
        tolerance=0.05,
    )

    assert trace.certificate.worst_sample_index in range(len(pool))
    assert 4 in trace.selected_sample_indices
    assert trace.max_residual_history[0] > 10 * 0.05
    assert not trace.converged
    assert trace.certificate.status is RegionalStatus.INCONSISTENT


def test_cegis_converges_when_sparse_constraints_define_shared_adapter():
    K_x = np.array([[0.3]])
    K_u = np.array([[0.7]])
    samples = []
    for x, b in [(-1.0, 0.8), (-0.5, 1.1), (0.0, 1.4), (0.5, 0.9), (1.0, 1.2)]:
        B_t = np.array([[b]])
        A_t = np.array([[0.1 + 0.02 * x]])
        A_s = A_t + B_t @ K_x
        B_s = B_t @ K_u
        samples.append(_sample([x], A_s, B_s, A_t, B_t))

    trace = counterexample_guided_regional_synthesis(
        samples,
        seed_sample_index=2,
        tolerance=1e-9,
    )

    assert trace.converged
    assert trace.iterations == 1
    assert trace.certificate.max_relative_residual < 1e-10


def test_regional_certificate_reports_worst_unmatched_physical_direction():
    samples = [
        _sample(
            [0.0],
            np.zeros((2, 2)),
            np.eye(2),
            np.zeros((2, 2)),
            np.array([[1.0], [0.0]]),
        )
    ]
    cert = synthesize_shared_regional_adapter(
        samples,
        approximate_relative_tolerance=0.01,
    )

    assert cert.status is RegionalStatus.INCONSISTENT
    assert abs(cert.worst_unmatched_direction[1]) > 0.99
