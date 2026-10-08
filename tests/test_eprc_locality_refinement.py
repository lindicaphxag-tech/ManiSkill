import numpy as np

from research.eprc.locality_refinement import evaluate_locality_refinement


def test_contracting_scale_ladder_authorizes_smaller_local_model():
    fine = np.repeat(np.diag([1.2, 1.0])[None, :, :], 5, axis=0)
    finer = np.repeat(np.diag([1.1, 1.0])[None, :, :], 5, axis=0)
    coarse = np.diag([1.6, 1.0])

    out, uncertainty = evaluate_locality_refinement(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
        contraction_threshold=0.75,
        refined_trust_radius=0.125,
    )

    assert np.isclose(out.coarse_fine_drift, 0.4)
    assert np.isclose(out.fine_finer_drift, 0.1)
    assert np.isclose(out.contraction_ratio, 0.25)
    assert out.contracting
    assert out.finer_stochastic_radius == 0.0
    assert np.isclose(uncertainty.epsilon_g, 0.1)
    assert out.recommended_trust_radius == 0.125


def test_noncontracting_scale_ladder_rejects_first_order_locality():
    fine = np.repeat(np.diag([1.2, 1.0])[None, :, :], 5, axis=0)
    finer = np.repeat(np.diag([0.7, 1.0])[None, :, :], 5, axis=0)
    coarse = np.diag([1.6, 1.0])

    out, _ = evaluate_locality_refinement(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
    )

    assert out.contraction_ratio > 0.75
    assert not out.contracting
    assert "reject" in out.reason


def test_finer_stochasticity_can_dominate_refined_uncertainty():
    fine = np.repeat(np.eye(2)[None, :, :], 5, axis=0)
    finer = np.stack([
        np.diag([0.8, 1.0]),
        np.diag([1.2, 1.0]),
        np.eye(2),
    ])
    coarse = np.diag([1.1, 1.0])

    out, uncertainty = evaluate_locality_refinement(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
        contraction_threshold=2.0,
    )

    assert out.finer_stochastic_radius > 0
    assert uncertainty.epsilon_g >= out.finer_stochastic_radius


def test_shape_mismatch_fails_closed():
    import pytest

    with pytest.raises(ValueError):
        evaluate_locality_refinement(
            coarse_map=np.eye(2),
            fine_map_replicates=np.zeros((5, 2, 2)),
            finer_map_replicates=np.zeros((5, 3, 2)),
        )
