import numpy as np

from research.eprc.scale_limit_certificate import (
    ScaleLimitStatus,
    certify_scale_limit,
)


def _rep(value: float, n: int = 5):
    return np.repeat(np.array([[[value]]], dtype=float), n, axis=0)


def test_four_scale_geometric_convergence_yields_conditional_tail_bound():
    # Centers approach 1.0 with a 1/4 drift contraction.
    out = certify_scale_limit(
        [_rep(1.4), _rep(1.1), _rep(1.025), _rep(1.00625)],
        q_max=0.5,
        min_contraction_ratios=2,
    )

    assert out.status is ScaleLimitStatus.CONVERGENCE_SUPPORTED
    assert np.allclose(out.center_drifts, [0.3, 0.075, 0.01875])
    assert max(out.robust_contraction_upper) <= 0.5
    np.testing.assert_allclose(
        [out.conditional_tail_bound], [0.01875], rtol=1e-12, atol=1e-12
    )


def test_repeatable_vq_like_noncontraction_is_rejected():
    out = certify_scale_limit(
        [_rep(0.0), _rep(3.01265), _rep(6.4626463053)],
        q_max=0.75,
        min_contraction_ratios=1,
    )

    assert out.status is ScaleLimitStatus.NONCONTRACTING
    assert out.conditional_tail_bound is None
    assert out.robust_contraction_lower[0] > 1.0


def test_stochastic_overlap_prevents_false_convergence_claim():
    coarse = np.array([[[1.4]], [[0.6]], [[1.2]], [[0.8]], [[1.0]]])
    fine = np.array([[[1.15]], [[0.85]], [[1.10]], [[0.90]], [[1.0]]])
    finer = np.array([[[1.04]], [[0.96]], [[1.02]], [[0.98]], [[1.0]]])
    finest = np.array([[[1.01]], [[0.99]], [[1.005]], [[0.995]], [[1.0]]])

    out = certify_scale_limit(
        [coarse, fine, finer, finest],
        q_max=0.75,
        min_contraction_ratios=2,
    )

    assert out.status is ScaleLimitStatus.STOCHASTICALLY_UNRESOLVED
    assert out.conditional_tail_bound is None


def test_three_scales_are_not_enough_for_default_strong_support():
    out = certify_scale_limit(
        [_rep(1.4), _rep(1.1), _rep(1.025)],
        q_max=0.75,
    )
    assert out.status is ScaleLimitStatus.STOCHASTICALLY_UNRESOLVED
