import numpy as np

from research.eprc.active_minimal_certificate import (
    plan_minimal_certificate_probes,
)
from research.eprc.certificate_directed_probing import ProbeInformation
from research.eprc.robust_repairability import RobustRepairDecision


def test_request_conditioned_plan_certifies_repair_with_fewer_probes_than_round_robin():
    g = np.eye(2)
    d = np.array([0.45, 0.0])
    info = ProbeInformation(np.eye(2), beta=0.2)
    candidates = np.eye(2)

    plan = plan_minimal_certificate_probes(
        g,
        d,
        probe_information=info,
        certified_radius=0.5,
        residual_tolerance=0.05,
        candidate_probes=candidates,
        max_additional_probes=8,
    )

    assert plan.initial_certificate.decision is RobustRepairDecision.INCONCLUSIVE
    assert plan.final_certificate.decision is RobustRepairDecision.CERTIFIED_REPAIR
    assert len(plan.steps) == 3
    assert all(np.allclose(step.probe, [1.0, 0.0]) for step in plan.steps)
    assert plan.symmetric_policy_evaluations == 6

    # A fixed e1,e2 round-robin needs five probes before e1 has been observed
    # three additional times. The request-conditioned plan stops at three.
    assert len(plan.steps) < 5


def test_plan_switches_axes_to_certify_impossibility():
    g = np.eye(2)
    d = np.array([0.68, 0.0])
    info = ProbeInformation(np.eye(2), beta=0.2)

    plan = plan_minimal_certificate_probes(
        g,
        d,
        probe_information=info,
        certified_radius=0.5,
        residual_tolerance=0.1,
        candidate_probes=np.eye(2),
        max_additional_probes=4,
    )

    assert plan.initial_certificate.decision is RobustRepairDecision.INCONCLUSIVE
    assert plan.final_certificate.decision is RobustRepairDecision.CERTIFIED_IMPOSSIBLE
    assert len(plan.steps) == 2
    # One observation on each axis raises the minimum information eigenvalue.
    assert {tuple(step.probe) for step in plan.steps} == {(1.0, 0.0), (0.0, 1.0)}
    assert plan.symmetric_policy_evaluations == 4


def test_already_certified_request_uses_zero_new_policy_queries():
    plan = plan_minimal_certificate_probes(
        np.eye(2),
        np.array([0.1, 0.0]),
        probe_information=ProbeInformation(100.0 * np.eye(2), beta=0.1),
        certified_radius=0.5,
        residual_tolerance=0.02,
        candidate_probes=np.eye(2),
        max_additional_probes=5,
    )

    assert plan.final_certificate.decision is RobustRepairDecision.CERTIFIED_REPAIR
    assert plan.steps == ()
    assert plan.symmetric_policy_evaluations == 0
    assert not plan.exhausted_budget


def test_budget_exhaustion_stays_explicitly_inconclusive():
    plan = plan_minimal_certificate_probes(
        np.eye(2),
        np.array([0.45, 0.0]),
        probe_information=ProbeInformation(np.eye(2), beta=0.2),
        certified_radius=0.5,
        residual_tolerance=0.05,
        candidate_probes=np.eye(2),
        max_additional_probes=1,
    )

    assert plan.final_certificate.decision is RobustRepairDecision.INCONCLUSIVE
    assert plan.exhausted_budget
    assert plan.symmetric_policy_evaluations == 2
