import numpy as np

from research.eprc.contract_signature import (
    contract_signature,
    contracts_equivalent,
    semantically_lift_jacobian,
    signature_distance,
)


def test_signature_is_invariant_to_invertible_action_reparameterization():
    # Physical response J_phys is the object we care about.
    j_phys = np.array([[1.0, 0.0], [0.3, 2.0], [0.0, 0.5]])

    # Policy/controller A exposes physical command coordinates directly.
    j_a = j_phys.copy()
    lift_a = np.eye(3)

    # Policy/controller B uses a different invertible action chart a_b = R a_phys.
    r = np.array([[2.0, 0.2, 0.0], [0.0, 0.5, 0.1], [0.0, 0.0, 1.5]])
    j_b = r @ j_phys
    lift_b = np.linalg.inv(r)

    lifted_a = semantically_lift_jacobian(j_a, lift_a)
    lifted_b = semantically_lift_jacobian(j_b, lift_b)
    assert np.allclose(lifted_a, lifted_b)
    assert contracts_equivalent(j_a, lift_a, j_b, lift_b)


def test_raw_action_jacobians_can_look_different_while_physical_contract_matches():
    j_phys = np.array([[1.0, 0.0], [0.0, 1.0]])
    r = np.array([[4.0, 1.0], [0.0, 0.25]])

    j_a = j_phys
    j_b = r @ j_phys

    raw_distance = signature_distance(contract_signature(j_a), contract_signature(j_b))
    assert raw_distance > 0.5

    assert contracts_equivalent(j_a, np.eye(2), j_b, np.linalg.inv(r))


def test_different_physical_response_subspaces_are_not_equivalent():
    j_a = np.array([[1.0], [0.0], [0.0]])
    j_b = np.array([[0.0], [1.0], [0.0]])

    assert not contracts_equivalent(j_a, np.eye(3), j_b, np.eye(3), tolerance=1e-8)


def test_physical_gain_change_is_not_erased_by_signature():
    j = np.array([[1.0, 0.2], [0.0, 2.0], [0.0, 0.0]])
    a = contract_signature(j)
    b = contract_signature(7.5 * j)
    assert signature_distance(a, b) > 1.0
    assert not contracts_equivalent(j, np.eye(3), 7.5 * j, np.eye(3))


def test_support_axis_swap_is_a_real_contract_change_after_canonicalization():
    # Same output subspace, singular spectrum and gain, but x-support and
    # y-support cause different physical command directions.
    j_identity = np.eye(2)
    j_swapped = np.array([[0.0, 1.0], [1.0, 0.0]])

    a = contract_signature(j_identity)
    b = contract_signature(j_swapped)

    assert np.allclose(a.response_projector, b.response_projector)
    assert np.allclose(a.singular_values_normalized, b.singular_values_normalized)
    assert np.isclose(a.frobenius_gain, b.frobenius_gain)
    assert signature_distance(a, b) > 1.0
    assert not contracts_equivalent(
        j_identity, np.eye(2), j_swapped, np.eye(2), tolerance=1e-8
    )
