import numpy as np

from research.eprc.locality_uncertainty import empirical_locality_envelope


def test_scale_drift_prevents_false_zero_uncertainty_when_rng_is_deterministic():
    fine = np.repeat(np.eye(2)[None, :, :], 5, axis=0)
    coarse = np.diag([1.3, 1.0])

    center, uncertainty, breakdown = empirical_locality_envelope(fine, coarse)

    assert np.allclose(center, np.eye(2))
    assert breakdown.stochastic_radius == 0.0
    assert np.isclose(breakdown.scale_drift_radius, 0.3)
    assert np.isclose(uncertainty.epsilon_g, 0.3)


def test_stochastic_variation_dominates_when_larger_than_scale_drift():
    fine = np.stack(
        [
            np.eye(2),
            np.diag([1.2, 1.0]),
            np.diag([0.8, 1.0]),
        ]
    )
    center = fine.mean(axis=0)
    coarse = center + 0.01 * np.eye(2)

    _, uncertainty, breakdown = empirical_locality_envelope(fine, coarse)

    assert breakdown.stochastic_radius > breakdown.scale_drift_radius
    assert np.isclose(uncertainty.epsilon_g, breakdown.stochastic_radius)


def test_shape_mismatch_fails_closed():
    fine = np.repeat(np.eye(2)[None, :, :], 3, axis=0)
    coarse = np.eye(3)

    try:
        empirical_locality_envelope(fine, coarse)
    except ValueError as exc:
        assert "shape" in str(exc)
    else:
        raise AssertionError("expected shape mismatch to fail")
