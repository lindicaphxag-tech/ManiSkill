import numpy as np

from research.eprc.repair_transfer import (
    repair_transfer_certificate,
    transferred_repair,
)


def test_equivalent_physical_contract_authorizes_repair_reuse():
    j = np.array([[1.0, 0.2], [0.1, 0.8]])
    cert = repair_transfer_certificate(
        j,
        j.copy(),
        source_estimation_error=0.005,
        target_estimation_error=0.005,
        target_remainder_lipschitz=0.05,
        disturbance_norm=0.1,
        target_min_authority_singular=0.5,
        representability_margin=0.2,
        error_tolerance=0.01,
    )
    assert cert.authorized
    assert cert.predicted_transfer_error_bound <= cert.error_tolerance


def test_physical_gain_difference_blocks_reuse():
    source = np.eye(2)
    target = 2.0 * np.eye(2)
    cert = repair_transfer_certificate(
        source,
        target,
        source_estimation_error=0.0,
        target_estimation_error=0.0,
        target_remainder_lipschitz=0.0,
        disturbance_norm=0.2,
        target_min_authority_singular=1.0,
        representability_margin=0.5,
        error_tolerance=0.05,
    )
    assert not cert.authorized
    assert cert.operator_gap == 1.0
    assert cert.predicted_transfer_error_bound == 0.2


def test_authority_loss_rejects_even_when_operators_match():
    j = np.eye(2)
    cert = repair_transfer_certificate(
        j,
        j,
        source_estimation_error=0.0,
        target_estimation_error=0.0,
        target_remainder_lipschitz=0.0,
        disturbance_norm=0.1,
        target_min_authority_singular=0.0,
        representability_margin=0.5,
        error_tolerance=1.0,
    )
    assert not cert.authorized
    assert "lost" in cert.reason


def test_unrepresentable_target_rejects_even_with_zero_dec_gap():
    j = np.eye(2)
    cert = repair_transfer_certificate(
        j,
        j,
        source_estimation_error=0.0,
        target_estimation_error=0.0,
        target_remainder_lipschitz=0.0,
        disturbance_norm=0.1,
        target_min_authority_singular=1.0,
        representability_margin=-0.01,
        error_tolerance=1.0,
    )
    assert not cert.authorized
    assert "outside controller authority" in cert.reason


def test_transferred_repair_respects_operator_gap_bound():
    source = np.array([[1.0, 0.2], [0.0, 0.8]])
    target = source + np.array([[0.02, 0.0], [0.0, -0.01]])
    delta = np.array([0.1, -0.2])

    source_repair = transferred_repair(source, delta)
    target_linear = target @ delta
    actual_linear_error = np.linalg.norm(target_linear - source_repair)

    cert = repair_transfer_certificate(
        source,
        target,
        source_estimation_error=0.0,
        target_estimation_error=0.0,
        target_remainder_lipschitz=0.0,
        disturbance_norm=float(np.linalg.norm(delta)),
        target_min_authority_singular=0.5,
        representability_margin=0.5,
        error_tolerance=0.01,
    )
    assert actual_linear_error <= cert.predicted_transfer_error_bound + 1e-12


def test_shape_mismatch_fails_closed():
    cert = repair_transfer_certificate(
        np.eye(2),
        np.eye(3),
        source_estimation_error=0.0,
        target_estimation_error=0.0,
        target_remainder_lipschitz=0.0,
        disturbance_norm=0.1,
        target_min_authority_singular=1.0,
        representability_margin=1.0,
        error_tolerance=1.0,
    )
    assert not cert.authorized
    assert np.isinf(cert.predicted_transfer_error_bound)
