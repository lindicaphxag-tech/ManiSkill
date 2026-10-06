import math

import numpy as np

from research.eprc.local_model_admissibility import (
    LocalModelStatus,
    assess_first_order_admissibility,
)


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
    assert not out.same_scale_queries_authorized
    assert out.contraction_ratio < 0.75
    assert out.observed_convergence_order > 1.0


def test_repeatable_but_noncontracting_map_rejects_first_order_model():
    # Mirrors the mechanism of the public VQ-BeT witness: zero repeated-probe
    # noise but larger drift at the smaller perturbation scale.
    coarse = np.array([[0.0, 0.0], [0.0, 0.0]])
    fine_center = np.array([[3.0, 0.0], [0.0, 0.0]])
    finer_center = np.array([[6.45, 0.0], [0.0, 0.0]])
    fine = np.repeat(fine_center[None, ...], 5, axis=0)
    finer = np.repeat(finer_center[None, ...], 5, axis=0)

    out = assess_first_order_admissibility(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
    )

    assert out.status is LocalModelStatus.FIRST_ORDER_REJECTED
    assert not out.first_order_crg_authorized
    assert not out.same_scale_queries_authorized
    assert out.contraction_ratio > 1.0
    assert out.observed_convergence_order < 0.0


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
