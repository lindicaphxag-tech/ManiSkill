import numpy as np

from research.eprc.robust_repairability import RobustRepairDecision
from research.eprc.structured_repairability import (
    first_order_regularity_gate,
    structured_repairability_certificate,
    verify_common_repair,
)


def test_vqbet_observed_scale_ladder_rejects_first_order_authorization():
    # Frozen prospective run 37460144187.
    d1 = 3.0126126299191625
    d2 = 3.449988245022615

    # Scalar 1x1 maps are enough to reproduce the exact operator drifts.
    coarse = np.array([[0.0]])
    fine = np.array([[d1]])
    finer = np.array([[d1 + d2]])
    out = first_order_regularity_gate(
        coarse, fine, finer, contraction_threshold=0.75
    )
    assert np.isclose(out.coarse_fine_drift, d1)
    assert np.isclose(out.fine_finer_drift, d2)
    assert np.isclose(out.contraction_ratio, d2 / d1)
    assert not out.first_order_supported


def test_common_repair_is_stronger_than_per_model_repair_and_can_be_verified():
    maps = np.stack([
        np.eye(2),
        np.diag([1.02, 0.98]),
    ])
    d = np.array([0.20, -0.10])
    cert = structured_repairability_certificate(
        maps, d, radius=0.5, residual_tolerance=0.01
    )
    assert cert.decision is RobustRepairDecision.CERTIFIED_REPAIR
    assert cert.common_repair_verified
    assert np.all(cert.individually_repairable)
    assert verify_common_repair(
        maps,
        d,
        cert.common_support_delta,
        radius=0.5,
        residual_tolerance=0.01,
    )


def test_forall_exists_does_not_imply_exists_forall():
    # Under G1 the repair is +0.5; under G2 it is -0.5. Every model is
    # individually repairable, but the runtime cannot execute both at once.
    maps = np.array([[[1.0]], [[-1.0]]])
    d = np.array([0.5])
    cert = structured_repairability_certificate(
        maps, d, radius=1.0, residual_tolerance=1e-6
    )

    assert np.all(cert.individually_repairable)
    assert cert.decision is RobustRepairDecision.INCONCLUSIVE
    assert cert.quantifier_gap
    assert not cert.common_repair_verified


def test_one_impossible_hypothesis_proves_robust_impossibility():
    maps = np.array([
        [[1.0], [0.0]],
        [[0.0], [1.0]],
    ])
    d = np.array([0.5, 0.5])
    cert = structured_repairability_certificate(
        maps, d, radius=0.6, residual_tolerance=0.1
    )

    assert cert.decision is RobustRepairDecision.CERTIFIED_IMPOSSIBLE
    assert cert.impossible_hypothesis_index is not None
    assert cert.impossibility_witness is not None
    assert cert.impossibility_witness.margin > 0.1


def test_common_candidate_failure_without_proof_stays_inconclusive():
    # Each map can realize the target, but with different latent corrections.
    maps = np.array([[[1.0]], [[2.0]]])
    d = np.array([1.0])
    cert = structured_repairability_certificate(
        maps, d, radius=1.0, residual_tolerance=0.05
    )
    assert np.all(cert.individually_repairable)
    assert cert.decision is RobustRepairDecision.INCONCLUSIVE
    assert cert.quantifier_gap
