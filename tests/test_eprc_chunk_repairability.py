import numpy as np

from research.eprc.chunk_repairability import (
    build_chunk_authority,
    certify_chunk_repair,
)
from research.eprc.robust_repairability import RobustRepairDecision


def _authority():
    return build_chunk_authority(
        horizon=3,
        action_low=np.array([-1.0]),
        action_high=np.array([1.0]),
        previous_action=np.array([0.0]),
        max_step_delta=np.array([0.4]),
        max_jerk=np.array([0.3]),
        previous_delta=np.array([0.0]),
    )


def test_chunk_authority_accepts_smooth_chunk_and_rejects_jump():
    auth = _authority()
    assert auth.contains(np.array([[0.1], [0.2], [0.25]]))
    assert not auth.contains(np.array([[0.1], [0.9], [0.9]]))


def test_chunk_crg_certifies_smooth_policy_consistent_repair():
    auth = _authority()
    nominal = np.zeros((3, 1))

    # One support scalar moves the whole chunk smoothly.
    J = np.array([[0.2], [0.3], [0.35]])
    C = np.eye(3)
    target = J[:, 0] * 0.5

    out = certify_chunk_repair(
        J,
        C,
        target,
        nominal_chunk=nominal,
        chunk_authority=auth,
        epsilon_j=0.0,
        epsilon_g=0.0,
        trust_radius=1.0,
        residual_tolerance=1e-9,
    )
    assert out.certificate.decision is RobustRepairDecision.CERTIFIED_REPAIR
    assert auth.contains(out.repaired_chunk)


def test_temporal_authority_can_make_structurally_reachable_target_impossible():
    auth = _authority()
    nominal = np.zeros((3, 1))

    # Structurally the map can produce this direction, but doing so requires
    # support magnitude beyond the robust temporal-authority radius.
    J = np.array([[0.2], [0.8], [0.8]])
    C = np.eye(3)
    target = J[:, 0] * 2.0

    out = certify_chunk_repair(
        J,
        C,
        target,
        nominal_chunk=nominal,
        chunk_authority=auth,
        epsilon_j=0.0,
        epsilon_g=0.0,
        trust_radius=10.0,
        residual_tolerance=0.05,
    )
    assert out.certificate.decision is RobustRepairDecision.CERTIFIED_IMPOSSIBLE
    assert out.authority_limiting_label is not None


def test_uncertain_chunk_map_can_force_abstention():
    auth = _authority()
    nominal = np.zeros((3, 1))
    J = np.array([[0.2], [0.3], [0.35]])
    C = np.eye(3)
    target = J[:, 0] * 0.5

    out = certify_chunk_repair(
        J,
        C,
        target,
        nominal_chunk=nominal,
        chunk_authority=auth,
        epsilon_j=0.1,
        epsilon_g=0.2,
        trust_radius=1.0,
        residual_tolerance=0.02,
    )
    assert out.certificate.decision is RobustRepairDecision.INCONCLUSIVE
