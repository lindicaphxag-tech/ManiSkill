import numpy as np

from research.crg_core.active_probe import (
    ProbeDesign,
    certify_with_design,
    select_candidate_directed_probe,
    weakest_observed_probe,
)
from research.crg_core.core import Decision


def test_candidate_directed_probe_targets_uncertain_repair_direction():
    design = ProbeDesign(np.diag([10.0, 1.0]), beta=0.2)
    candidates = np.eye(2)
    probe, reduction = select_candidate_directed_probe(
        design, np.array([0.0, 1.0]), candidates
    )
    assert np.allclose(probe, [0.0, 1.0])
    assert reduction > 0


def test_weakest_probe_targets_minimum_information_eigenvector():
    design = ProbeDesign(np.diag([8.0, 2.0, 0.5]), beta=0.1)
    z = weakest_observed_probe(design)
    assert np.allclose(np.abs(z), [0.0, 0.0, 1.0])


def test_certificate_directed_probes_resolve_inconclusive_repair():
    G = np.eye(2)
    d = np.array([0.45, 0.0])
    design = ProbeDesign(np.eye(2), beta=0.2)

    before = certify_with_design(
        G, d, design=design, certified_radius=0.5, tolerance=0.05
    )
    assert before.decision is Decision.INCONCLUSIVE

    for _ in range(4):
        design = design.after_probe(np.array([1.0, 0.0]))

    after = certify_with_design(
        G, d, design=design, certified_radius=0.5, tolerance=0.05
    )
    assert after.candidate_uncertainty < before.candidate_uncertainty
    assert after.decision is Decision.CERTIFIED_REPAIR


def test_far_target_remains_certified_impossible():
    design = ProbeDesign(np.eye(2), beta=0.1)
    cert = certify_with_design(
        np.eye(2),
        np.array([2.0, 0.0]),
        design=design,
        certified_radius=0.5,
        tolerance=0.1,
    )
    assert cert.decision is Decision.CERTIFIED_IMPOSSIBLE
