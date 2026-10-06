import numpy as np

from research.eprc.linear_authority import LinearActionAuthority
from research.eprc.robust_repairability import (
    FactorUncertainty,
    PhysicalMapUncertainty,
    RobustRepairDecision,
    empirical_operator_envelope,
    propagate_physical_map_uncertainty,
    robust_repair_certificate,
    robust_support_radius_linear_authority,
)


def test_zero_uncertainty_certifies_nominally_exact_repair():
    g = np.eye(2)
    d = np.array([0.2, -0.1])
    cert = robust_repair_certificate(
        g,
        d,
        physical_map_uncertainty=PhysicalMapUncertainty(0.0),
        certified_radius=0.5,
        residual_tolerance=1e-10,
    )
    assert cert.decision is RobustRepairDecision.CERTIFIED_REPAIR
    assert cert.worst_case_residual_upper < 1e-10


def test_model_uncertainty_can_turn_nominal_repair_into_inconclusive():
    g = np.eye(2)
    d = np.array([0.45, 0.0])
    cert = robust_repair_certificate(
        g,
        d,
        physical_map_uncertainty=PhysicalMapUncertainty(0.20),
        certified_radius=0.5,
        residual_tolerance=0.05,
    )
    assert cert.nominal_residual_norm < 1e-10
    assert cert.worst_case_residual_upper > 0.05
    assert cert.decision is RobustRepairDecision.INCONCLUSIVE


def test_far_outside_target_is_certified_impossible_despite_uncertainty():
    g = np.eye(2)
    d = np.array([2.0, 0.0])
    cert = robust_repair_certificate(
        g,
        d,
        physical_map_uncertainty=PhysicalMapUncertainty(0.10),
        certified_radius=0.5,
        residual_tolerance=0.10,
    )
    assert cert.best_case_residual_lower > 0.10
    assert cert.decision is RobustRepairDecision.CERTIFIED_IMPOSSIBLE


def test_uncertain_jacobian_shrinks_action_authority_radius():
    authority = LinearActionAuthority.from_box(
        np.array([-1.0, -1.0]), np.array([1.0, 1.0])
    )
    a0 = np.array([0.0, 0.0])
    j = np.eye(2)

    exact = robust_support_radius_linear_authority(
        a0, j, authority, epsilon_j=0.0, trust_radius=10.0
    )
    uncertain = robust_support_radius_linear_authority(
        a0, j, authority, epsilon_j=0.5, trust_radius=10.0
    )

    assert np.isclose(exact.certified_radius, 1.0)
    assert uncertain.certified_radius < exact.certified_radius
    assert np.isclose(uncertain.certified_radius, 2.0 / 3.0)


def test_factor_uncertainty_propagation_matches_product_bound():
    c = np.array([[2.0, 0.0], [0.0, 1.0]])
    j = np.array([[1.0, 0.0], [0.0, 3.0]])
    u = FactorUncertainty(epsilon_c=0.2, epsilon_j=0.1)
    out = propagate_physical_map_uncertainty(c, j, u)
    expected = np.linalg.norm(c, 2) * 0.1 + np.linalg.norm(j, 2) * 0.2 + 0.2 * 0.1
    assert np.isclose(out.epsilon_g, expected)


def test_empirical_operator_envelope_contains_observed_replicates():
    reps = np.array(
        [
            [[1.0, 0.0], [0.0, 1.0]],
            [[1.1, 0.0], [0.0, 0.9]],
            [[0.9, 0.0], [0.0, 1.1]],
        ]
    )
    center, envelope = empirical_operator_envelope(reps, quantile=1.0)
    for rep in reps:
        assert np.linalg.norm(rep - center, 2) <= envelope.epsilon_g + 1e-12
