import numpy as np

from research.eprc.repairability_geometry import (
    certified_support_radius,
    synthesize_repair,
)


def test_authority_shrinks_counterfactual_trust_region():
    j = np.array([[2.0, 0.0], [0.0, 0.5]])
    r = certified_support_radius(
        nominal_action=np.array([0.8, 0.0]),
        action_support_jacobian=j,
        action_low=np.array([-1.0, -1.0]),
        action_high=np.array([1.0, 1.0]),
        trust_radius=1.0,
    )
    # First action coordinate has only 0.2 headroom and row norm 2 => r <= 0.1.
    assert np.isclose(r.authority_radius, 0.1)
    assert np.isclose(r.certified_radius, 0.1)
    assert r.limiting_action_dim == 0


def test_constructs_exact_repair_inside_certified_ellipsoid():
    j = np.eye(2)
    c = np.eye(2)
    out = synthesize_repair(
        j,
        c,
        np.array([0.2, -0.1]),
        nominal_action=np.zeros(2),
        action_low=-np.ones(2),
        action_high=np.ones(2),
        trust_radius=0.5,
    )
    assert out.repairable
    assert out.residual_norm < 1e-10
    assert np.allclose(out.physical_repair, [0.2, -0.1])


def test_proves_unrepairable_when_target_has_out_of_image_component():
    # Only physical x can be changed by policy-consistent counterfactual repair.
    j = np.array([[1.0], [0.0]])
    c = np.eye(2)
    out = synthesize_repair(
        j,
        c,
        np.array([0.2, 0.3]),
        nominal_action=np.zeros(2),
        action_low=-np.ones(2),
        action_high=np.ones(2),
        trust_radius=1.0,
    )
    assert not out.repairable
    assert out.residual_norm > 0.29
    assert out.separation_margin > 0


def test_proves_unrepairable_when_authority_is_too_small():
    j = np.array([[1.0]])
    c = np.array([[1.0]])
    out = synthesize_repair(
        j,
        c,
        np.array([0.5]),
        nominal_action=np.array([0.9]),
        action_low=np.array([-1.0]),
        action_high=np.array([1.0]),
        trust_radius=1.0,
    )
    assert np.isclose(out.certified_radius, 0.1)
    assert not out.repairable
    assert np.isclose(out.physical_repair[0], 0.1, atol=1e-8)
    assert out.separation_margin > 0


def test_scaled_action_chart_preserves_physical_repairability_when_bounds_transform():
    # Chart A is physical action. Chart B is a normalized/reparameterized action
    # a_B = R a_A, with correspondingly transformed diagonal authority.
    j_a = np.array([[1.0, 0.2], [0.1, 0.5]])
    c_a = np.eye(2)
    a_a = np.array([0.1, -0.2])
    lo_a = np.array([-1.0, -1.0])
    hi_a = np.array([1.0, 1.0])

    r = np.diag([2.0, 0.5])
    j_b = r @ j_a
    c_b = np.linalg.inv(r)
    a_b = r @ a_a
    lo_b = r @ lo_a
    hi_b = r @ hi_a

    d = np.array([0.2, 0.05])
    out_a = synthesize_repair(
        j_a, c_a, d,
        nominal_action=a_a,
        action_low=lo_a,
        action_high=hi_a,
        trust_radius=0.4,
    )
    out_b = synthesize_repair(
        j_b, c_b, d,
        nominal_action=a_b,
        action_low=lo_b,
        action_high=hi_b,
        trust_radius=0.4,
    )

    assert np.isclose(out_a.certified_radius, out_b.certified_radius)
    assert np.allclose(out_a.physical_repair, out_b.physical_repair, atol=1e-8)
    assert np.isclose(out_a.residual_norm, out_b.residual_norm, atol=1e-8)
