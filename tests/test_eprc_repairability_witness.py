import numpy as np

from research.eprc.repairability_geometry import synthesize_repair
from research.eprc.repairability_witness import (
    RepairabilitySeparationWitness,
    build_separation_witness,
    verify_separation_witness,
)


def test_out_of_image_target_has_independently_verifiable_witness():
    g = np.array([[1.0], [0.0]])
    d = np.array([0.2, 0.3])
    witness = build_separation_witness(
        g, d, certified_radius=1.0, normal=np.array([0.0, 1.0])
    )

    assert witness.margin > 0.29
    assert verify_separation_witness(
        g, d, certified_radius=1.0, witness=witness
    )


def test_authority_limited_target_has_positive_dual_gap():
    g = np.array([[1.0]])
    d = np.array([0.5])
    witness = build_separation_witness(
        g, d, certified_radius=0.1, normal=np.array([1.0])
    )

    assert np.isclose(witness.repair_set_support, 0.1)
    assert np.isclose(witness.target_projection, 0.5)
    assert np.isclose(witness.margin, 0.4)
    assert verify_separation_witness(
        g, d, certified_radius=0.1, witness=witness
    )


def test_optimizer_residual_can_be_transported_into_dual_witness():
    j = np.array([[1.0], [0.0]])
    c = np.eye(2)
    d = np.array([0.2, 0.3])
    out = synthesize_repair(
        j,
        c,
        d,
        nominal_action=np.zeros(2),
        action_low=-np.ones(2),
        action_high=np.ones(2),
        trust_radius=1.0,
    )
    witness = build_separation_witness(
        c @ j,
        d,
        certified_radius=out.certified_radius,
        normal=out.separation_normal,
    )

    assert verify_separation_witness(
        c @ j,
        d,
        certified_radius=out.certified_radius,
        witness=witness,
    )


def test_forged_margin_is_rejected_without_running_optimizer():
    g = np.array([[1.0], [0.0]])
    d = np.array([0.2, 0.3])
    valid = build_separation_witness(
        g, d, certified_radius=1.0, normal=np.array([0.0, 1.0])
    )
    forged = RepairabilitySeparationWitness(
        normal=valid.normal,
        target_projection=valid.target_projection,
        repair_set_support=valid.repair_set_support,
        margin=valid.margin + 1.0,
    )

    assert not verify_separation_witness(
        g, d, certified_radius=1.0, witness=forged
    )


def test_inside_target_has_no_positive_separation_witness_along_target():
    g = np.eye(2)
    d = np.array([0.2, 0.1])
    witness = build_separation_witness(
        g, d, certified_radius=0.5, normal=d
    )

    assert witness.margin <= 0
    assert not verify_separation_witness(
        g, d, certified_radius=0.5, witness=witness
    )
