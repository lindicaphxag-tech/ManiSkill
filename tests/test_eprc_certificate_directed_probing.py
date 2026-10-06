import numpy as np

from research.eprc.certificate_directed_probing import (
    ProbeInformation,
    certify_with_probe_information,
    select_candidate_directed_probe,
    weakest_observed_probe,
)
from research.eprc.robust_repairability import RobustRepairDecision


def test_candidate_directed_probe_chooses_uncertain_repair_axis():
    info = ProbeInformation(np.diag([10.0, 1.0]), beta=0.2)
    probe, gain = select_candidate_directed_probe(
        info, np.array([0.0, 1.0]), np.eye(2)
    )
    assert np.allclose(probe, [0.0, 1.0])
    assert gain > 0


def test_weakest_observed_probe_hits_minimum_information_axis():
    info = ProbeInformation(np.diag([8.0, 2.0, 0.5]), beta=0.1)
    probe = weakest_observed_probe(info)
    assert np.allclose(np.abs(probe), [0.0, 0.0, 1.0])


def test_targeted_probes_turn_abstention_into_repair_certificate():
    g = np.eye(2)
    d = np.array([0.45, 0.0])
    info = ProbeInformation(np.eye(2), beta=0.2)

    before = certify_with_probe_information(
        g,
        d,
        probe_information=info,
        certified_radius=0.5,
        residual_tolerance=0.05,
    )
    assert before.decision is RobustRepairDecision.INCONCLUSIVE

    for _ in range(4):
        info = info.update(np.array([1.0, 0.0]))

    after = certify_with_probe_information(
        g,
        d,
        probe_information=info,
        certified_radius=0.5,
        residual_tolerance=0.05,
    )
    assert after.candidate_uncertainty < before.candidate_uncertainty
    assert after.decision is RobustRepairDecision.CERTIFIED_REPAIR


def test_far_target_is_impossible_under_uniform_design_bound():
    info = ProbeInformation(np.eye(2), beta=0.1)
    cert = certify_with_probe_information(
        np.eye(2),
        np.array([2.0, 0.0]),
        probe_information=info,
        certified_radius=0.5,
        residual_tolerance=0.1,
    )
    assert cert.decision is RobustRepairDecision.CERTIFIED_IMPOSSIBLE
