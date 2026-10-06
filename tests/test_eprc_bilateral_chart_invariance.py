import numpy as np

from research.eprc.bilateral_chart_invariance import (
    bilateral_chart_certificate,
    bilateral_contracts_equivalent,
    canonicalize_dec_jacobian,
)
from research.eprc.contract_signature import contract_signature, signature_distance


def test_action_and_support_coordinate_changes_cancel_after_bilateral_lifting():
    j_phys = np.array([[1.0, 0.2], [0.4, 1.7], [0.1, -0.3]])

    # Local action coordinate map a' = h(a).
    dh = np.array([[2.0, 0.2, 0.0], [0.0, 0.5, 0.1], [0.0, 0.0, 1.4]])
    # Local support coordinate map xi' = g(s).
    dg = np.array([[3.0, 0.4], [0.2, 0.7]])

    # Raw derivative in the transformed charts:
    # da'/dxi' = Dh (dy/ds) Dg^{-1} for identity canonical base charts.
    raw_prime = dh @ j_phys @ np.linalg.inv(dg)
    recovered = canonicalize_dec_jacobian(
        raw_prime, np.linalg.inv(dh), dg
    )
    assert np.allclose(recovered, j_phys, atol=1e-10)
    assert bilateral_contracts_equivalent(
        j_phys, np.eye(3), np.eye(2),
        raw_prime, np.linalg.inv(dh), dg,
    )


def test_raw_dec_distance_can_be_large_before_support_and_action_lifting():
    j_phys = np.array([[1.0, 0.0], [0.0, 2.0]])
    dh = np.array([[4.0, 0.5], [0.0, 0.3]])
    dg = np.array([[0.25, 0.1], [0.0, 2.0]])
    raw_prime = dh @ j_phys @ np.linalg.inv(dg)
    assert signature_distance(
        contract_signature(j_phys), contract_signature(raw_prime)
    ) > 1.0
    assert bilateral_contracts_equivalent(
        j_phys, np.eye(2), np.eye(2),
        raw_prime, np.linalg.inv(dh), dg,
    )


def test_noninvertible_support_chart_blocks_equivalence_claim():
    action_chart = np.eye(2)
    support_chart = np.array([[1.0, 0.0], [0.0, 0.0]])
    cert = bilateral_chart_certificate(action_chart, support_chart)
    assert cert.action_locally_invertible
    assert not cert.support_locally_invertible
