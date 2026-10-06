import math

import numpy as np

from research.crg_core.local_model import (
    LocalModelStatus,
    ScaleLimitStatus,
    assess_first_order_admissibility,
    certify_scale_limit,
)


def _rep(value: float, n: int = 5):
    return np.repeat(np.array([[[value]]], dtype=float), n, axis=0)


def test_contracting_scale_ladder_authorizes_first_order_crg():
    coarse = np.array([[1.4, 0.0], [0.0, 1.4]])
    fine = np.repeat(np.array([[[1.1, 0.0], [0.0, 1.1]]]), 5, axis=0)
    finer = np.repeat(np.array([[[1.025, 0.0], [0.0, 1.025]]]), 5, axis=0)
    out = assess_first_order_admissibility(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
    )
    assert out.status is LocalModelStatus.FIRST_ORDER_ADMISSIBLE
    assert out.first_order_crg_authorized
    assert out.contraction_ratio < 0.75
    assert out.observed_convergence_order > 1.0


def test_repeatable_but_noncontracting_map_rejects_first_order_model():
    coarse = np.array([[0.0, 0.0], [0.0, 0.0]])
    fine = np.repeat(np.array([[[3.0, 0.0], [0.0, 0.0]]]), 5, axis=0)
    finer = np.repeat(np.array([[[6.45, 0.0], [0.0, 0.0]]]), 5, axis=0)
    out = assess_first_order_admissibility(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
    )
    assert out.status is LocalModelStatus.FIRST_ORDER_REJECTED
    assert not out.first_order_crg_authorized
    assert not out.same_scale_queries_authorized
    assert out.contraction_ratio > 1.0


def test_stochastic_dominance_routes_to_more_same_scale_evidence():
    coarse = np.array([[1.0]])
    fine = np.array([[[0.5]], [[1.5]], [[0.7]], [[1.3]], [[1.0]]])
    finer = np.array([[[0.6]], [[1.4]], [[0.8]], [[1.2]], [[1.0]]])
    out = assess_first_order_admissibility(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
        stochastic_dominance_ratio=2.0,
    )
    assert out.status is LocalModelStatus.STOCHASTICALLY_UNRESOLVED
    assert out.same_scale_queries_authorized
    assert not out.first_order_crg_authorized


def test_flat_multiscale_map_is_admissible():
    coarse = np.eye(2)
    fine = np.repeat(np.eye(2)[None, ...], 5, axis=0)
    finer = np.repeat(np.eye(2)[None, ...], 5, axis=0)
    out = assess_first_order_admissibility(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
    )
    assert out.status is LocalModelStatus.FIRST_ORDER_ADMISSIBLE
    assert math.isinf(out.observed_convergence_order)


def test_four_scale_geometric_convergence_yields_tail_bound():
    out = certify_scale_limit(
        [_rep(1.4), _rep(1.1), _rep(1.025), _rep(1.00625)],
        q_max=0.5,
        min_contraction_ratios=2,
    )
    assert out.status is ScaleLimitStatus.CONVERGENCE_SUPPORTED
    assert np.allclose(out.center_drifts, [0.3, 0.075, 0.01875])
    assert max(out.robust_contraction_upper) <= 0.5
    np.testing.assert_allclose([out.conditional_tail_bound], [0.01875], rtol=1e-12, atol=1e-12)


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
