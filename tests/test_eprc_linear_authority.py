import numpy as np

from research.eprc.linear_authority import (
    LinearActionAuthority,
    certified_support_radius_linear_authority,
    synthesize_policy_consistent_repair,
)


def test_box_is_special_case_of_linear_authority_radius():
    j = np.array([[2.0, 0.0], [0.0, 0.5]])
    a = np.array([0.8, 0.0])
    authority = LinearActionAuthority.from_box(
        np.array([-1.0, -1.0]),
        np.array([1.0, 1.0]),
    )
    cert = certified_support_radius_linear_authority(
        a, j, authority, trust_radius=1.0
    )
    assert np.isclose(cert.authority_radius, 0.1)
    assert np.isclose(cert.certified_radius, 0.1)


def test_constructive_repair_returns_actual_executable_action():
    j = np.array([[1.0, 0.0], [0.0, 0.5]])
    c = np.eye(2)
    a0 = np.array([0.1, -0.2])
    authority = LinearActionAuthority.from_box(-np.ones(2), np.ones(2))

    out = synthesize_policy_consistent_repair(
        j,
        c,
        np.array([0.2, 0.1]),
        nominal_action=a0,
        authority=authority,
        trust_radius=0.5,
    )

    assert out.certified
    assert np.allclose(out.action_delta, j @ out.support_delta)
    assert np.allclose(out.repaired_action, a0 + out.action_delta)
    assert authority.contains(out.repaired_action)
    assert np.allclose(out.physical_repair, [0.2, 0.1], atol=1e-9)


def test_general_linear_authority_rejects_coupled_constraint_violation():
    # Individual coordinates have headroom, but their sum is tightly bounded.
    authority = LinearActionAuthority(
        H=np.array([[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]),
        h=np.array([0.25, 1.0, 1.0]),
    )
    a0 = np.zeros(2)
    j = np.eye(2)

    cert = certified_support_radius_linear_authority(
        a0, j, authority, trust_radius=1.0
    )
    assert np.isclose(cert.authority_radius, 0.25 / np.sqrt(2.0))

    out = synthesize_policy_consistent_repair(
        j,
        np.eye(2),
        np.array([0.2, 0.2]),
        nominal_action=a0,
        authority=authority,
        trust_radius=1.0,
    )
    assert not out.certified
    assert out.separation_margin > 0


def test_arbitrary_invertible_action_chart_preserves_repairability_geometry():
    j = np.array([[1.0, 0.2], [0.1, 0.7]])
    c = np.array([[1.0, 0.3], [0.0, 1.5]])
    a0 = np.array([0.1, -0.2])
    authority = LinearActionAuthority.from_box(
        np.array([-1.0, -0.8]),
        np.array([0.9, 1.1]),
    )

    # Non-diagonal chart: box becomes a general parallelogram in transformed coordinates.
    r = np.array([[1.7, 0.4], [-0.3, 0.8]])
    r_inv = np.linalg.inv(r)

    j_prime = r @ j
    c_prime = c @ r_inv
    a0_prime = r @ a0
    authority_prime = authority.reparameterize(r)

    radius_a = certified_support_radius_linear_authority(
        a0, j, authority, trust_radius=0.6
    )
    radius_b = certified_support_radius_linear_authority(
        a0_prime, j_prime, authority_prime, trust_radius=0.6
    )
    assert np.isclose(radius_a.certified_radius, radius_b.certified_radius)

    target = np.array([0.18, -0.06])
    out_a = synthesize_policy_consistent_repair(
        j,
        c,
        target,
        nominal_action=a0,
        authority=authority,
        trust_radius=0.6,
    )
    out_b = synthesize_policy_consistent_repair(
        j_prime,
        c_prime,
        target,
        nominal_action=a0_prime,
        authority=authority_prime,
        trust_radius=0.6,
    )

    assert out_a.certified == out_b.certified
    assert np.isclose(out_a.residual_norm, out_b.residual_norm, atol=1e-10)
    assert np.isclose(out_a.separation_margin, out_b.separation_margin, atol=1e-10)
    assert np.allclose(out_a.physical_repair, out_b.physical_repair, atol=1e-10)
    assert np.allclose(out_b.action_delta, r @ out_a.action_delta, atol=1e-9)
    assert authority.contains(out_a.repaired_action)
    assert authority_prime.contains(out_b.repaired_action)


def test_policy_image_not_controller_space_determines_impossibility():
    # Controller can command both x and y, but the frozen policy's counterfactual
    # response image only contains x. CRG must reject a requested y correction.
    j = np.array([[1.0], [0.0]])
    c = np.eye(2)
    authority = LinearActionAuthority.from_box(-np.ones(2), np.ones(2))

    out = synthesize_policy_consistent_repair(
        j,
        c,
        np.array([0.0, 0.3]),
        nominal_action=np.zeros(2),
        authority=authority,
        trust_radius=1.0,
    )

    assert not out.certified
    assert out.residual_norm > 0.29
    assert out.separation_margin > 0
    assert "outside policy-consistent" in out.reason
