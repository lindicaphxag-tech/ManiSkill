import numpy as np

from research.eprc.robust_repairability import (
    PhysicalMapUncertainty,
    RobustRepairDecision,
    robust_repair_certificate,
)
from research.eprc.robust_repairability_witness import (
    RobustSeparationWitness,
    build_robust_separation_witness,
    verify_robust_separation_witness,
)


def test_robust_dual_witness_proves_impossibility_for_entire_map_ball():
    g = np.array([[1.0]])
    d = np.array([0.8])
    radius = 0.5
    eps = 0.1
    tau = 0.1

    cert = robust_repair_certificate(
        g,
        d,
        physical_map_uncertainty=PhysicalMapUncertainty(eps),
        certified_radius=radius,
        residual_tolerance=tau,
    )
    assert cert.decision is RobustRepairDecision.CERTIFIED_IMPOSSIBLE

    normal = d - cert.nominal_physical_repair
    witness = build_robust_separation_witness(
        g,
        d,
        certified_radius=radius,
        epsilon_g=eps,
        residual_tolerance=tau,
        normal=normal,
    )

    # Nominal set reaches 0.5, uncertainty can expand it by at most 0.05.
    assert np.isclose(witness.robust_support, 0.55)
    assert np.isclose(witness.distance_lower_bound, 0.25)
    assert np.isclose(witness.margin_over_tolerance, 0.15)
    assert verify_robust_separation_witness(
        g,
        d,
        certified_radius=radius,
        epsilon_g=eps,
        residual_tolerance=tau,
        witness=witness,
    )


def test_uncertainty_can_destroy_nominal_impossibility_certificate():
    g = np.array([[1.0]])
    d = np.array([0.8])
    radius = 0.5
    tau = 0.1

    nominal_like = build_robust_separation_witness(
        g,
        d,
        certified_radius=radius,
        epsilon_g=0.0,
        residual_tolerance=tau,
        normal=np.array([1.0]),
    )
    uncertain = build_robust_separation_witness(
        g,
        d,
        certified_radius=radius,
        epsilon_g=0.5,
        residual_tolerance=tau,
        normal=np.array([1.0]),
    )

    assert nominal_like.margin_over_tolerance > 0
    assert uncertain.margin_over_tolerance < 0
    assert not verify_robust_separation_witness(
        g,
        d,
        certified_radius=radius,
        epsilon_g=0.5,
        residual_tolerance=tau,
        witness=uncertain,
    )


def test_forged_robust_margin_is_rejected():
    g = np.array([[1.0]])
    d = np.array([0.8])
    valid = build_robust_separation_witness(
        g,
        d,
        certified_radius=0.5,
        epsilon_g=0.1,
        residual_tolerance=0.1,
        normal=np.array([1.0]),
    )
    forged = RobustSeparationWitness(
        normal=valid.normal,
        target_projection=valid.target_projection,
        nominal_support=valid.nominal_support,
        uncertainty_support=valid.uncertainty_support,
        robust_support=valid.robust_support,
        distance_lower_bound=valid.distance_lower_bound,
        residual_tolerance=valid.residual_tolerance,
        margin_over_tolerance=valid.margin_over_tolerance + 0.5,
    )

    assert not verify_robust_separation_witness(
        g,
        d,
        certified_radius=0.5,
        epsilon_g=0.1,
        residual_tolerance=tau,
        witness=forged,
    )


def test_attacker_cannot_lower_tolerance_inside_witness():
    """One signed normal cannot override the actual held-out decision tolerance."""
    g = np.array([[1.0]])
    d = np.array([0.8])
    # With r=0.5 and eps=0.1, distance lower bound is 0.25.
    # A claimed tau=0.1 would prove impossibility, but the *trusted*
    # application allows tau=0.3, so impossibility must be rejected.
    forged = build_robust_separation_witness(
        g, d, certified_radius=0.5, epsilon_g=0.1,
        residual_tolerance=0.1, normal=np.array([1.0]),
    )
    assert forged.margin_over_tolerance > 0
    assert not verify_robust_separation_witness(
        g, d, certified_radius=0.5, epsilon_g=0.1,
        residual_tolerance=0.3, witness=forged,
    )
    assert verify_robust_separation_witness(
        g, d, certified_radius=0.5, epsilon_g=0.1,
        residual_tolerance=0.1, witness=forged,
    )


def test_nonfinite_physical_map_and_tolerance_fail_closed():
    g = np.array([[1.0]])
    d = np.array([0.8])
    witness = build_robust_separation_witness(
        g, d, certified_radius=0.5, epsilon_g=0.1,
        residual_tolerance=0.1, normal=np.array([1.0]),
    )
    assert not verify_robust_separation_witness(
        np.array([[np.nan]]), d, certified_radius=0.5, epsilon_g=0.1,
        residual_tolerance=0.1, witness=witness,
    )
    assert not verify_robust_separation_witness(
        g, d, certified_radius=0.5, epsilon_g=0.1,
        residual_tolerance=float("nan"), witness=witness,
    )
