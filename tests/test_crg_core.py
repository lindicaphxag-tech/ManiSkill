import numpy as np

from research.crg_core.core import (
    Decision,
    LinearAuthority,
    certify,
    empirical_operator_envelope,
    product_uncertainty_bound,
    robust_authority_radius,
)


def test_exact_map_certifies_repair():
    cert = certify(
        np.eye(2),
        np.array([0.2, -0.1]),
        epsilon_G=0.0,
        certified_radius=0.5,
        tolerance=1e-10,
    )
    assert cert.decision is Decision.CERTIFIED_REPAIR


def test_uncertainty_creates_honest_abstention_band():
    cert = certify(
        np.eye(2),
        np.array([0.45, 0.0]),
        epsilon_G=0.20,
        certified_radius=0.5,
        tolerance=0.05,
    )
    assert cert.nominal_residual < 1e-10
    assert cert.decision is Decision.INCONCLUSIVE


def test_far_target_is_impossible_even_under_favorable_model_error():
    cert = certify(
        np.eye(2),
        np.array([2.0, 0.0]),
        epsilon_G=0.10,
        certified_radius=0.5,
        tolerance=0.10,
    )
    assert cert.best_case_residual_lower > 0.10
    assert cert.decision is Decision.CERTIFIED_IMPOSSIBLE


def test_uncertain_j_shrinks_authority():
    A = LinearAuthority.box(np.array([-1.0, -1.0]), np.array([1.0, 1.0]))
    exact = robust_authority_radius(
        np.zeros(2), np.eye(2), A, epsilon_J=0.0, trust_radius=10.0
    )
    uncertain = robust_authority_radius(
        np.zeros(2), np.eye(2), A, epsilon_J=0.5, trust_radius=10.0
    )
    assert np.isclose(exact, 1.0)
    assert np.isclose(uncertain, 2.0 / 3.0)


def test_product_bound_includes_interaction_term():
    C = np.diag([2.0, 1.0])
    J = np.diag([1.0, 3.0])
    got = product_uncertainty_bound(C, J, epsilon_C=0.2, epsilon_J=0.1)
    expected = np.linalg.norm(C, 2) * 0.1 + np.linalg.norm(J, 2) * 0.2 + 0.02
    assert np.isclose(got, expected)


def test_empirical_envelope_contains_every_observed_replicate():
    maps = np.array([
        [[1.0, 0.0], [0.0, 1.0]],
        [[1.1, 0.0], [0.0, 0.9]],
        [[0.9, 0.0], [0.0, 1.1]],
    ])
    center, eps = empirical_operator_envelope(maps, quantile=1.0)
    assert all(np.linalg.norm(M - center, 2) <= eps + 1e-12 for M in maps)
