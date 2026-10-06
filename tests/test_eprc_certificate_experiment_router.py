from research.eprc.certificate_experiment_router import (
    EvidenceBottleneck,
    ExperimentKind,
    experiment_can_address,
    route_certificate_resolving_experiment,
)
from research.eprc.robust_repairability import RobustRepairDecision


def test_real_vqbet_negative_routes_to_smaller_scale_not_more_directional_probes():
    route = route_certificate_resolving_experiment(
        decision=RobustRepairDecision.INCONCLUSIVE,
        stochastic_radius=0.0,
        scale_drift_radius=3.0126126299191625,
        candidate_directional_uncertainty=1.0836521336592604,
        global_directional_uncertainty=1.0836521336592604,
    )
    assert route.bottleneck is EvidenceBottleneck.LOCALITY_SCALE
    assert route.experiment is ExperimentKind.SHRINK_SYMMETRIC_SCALE
    assert not experiment_can_address(
        ExperimentKind.TARGET_REPAIR_DIRECTION,
        EvidenceBottleneck.LOCALITY_SCALE,
    )


def test_stochastic_bottleneck_requests_paired_repeats():
    route = route_certificate_resolving_experiment(
        decision=RobustRepairDecision.INCONCLUSIVE,
        stochastic_radius=0.7,
        scale_drift_radius=0.2,
        candidate_directional_uncertainty=0.1,
        global_directional_uncertainty=0.15,
    )
    assert route.bottleneck is EvidenceBottleneck.STOCHASTIC_REPEATABILITY
    assert route.experiment is ExperimentKind.REPEAT_PAIRED_RANDOMNESS


def test_candidate_direction_bottleneck_requests_targeted_probe():
    route = route_certificate_resolving_experiment(
        decision=RobustRepairDecision.INCONCLUSIVE,
        stochastic_radius=0.1,
        scale_drift_radius=0.2,
        candidate_directional_uncertainty=0.8,
        global_directional_uncertainty=0.4,
    )
    assert route.bottleneck is EvidenceBottleneck.CANDIDATE_DIRECTION
    assert route.experiment is ExperimentKind.TARGET_REPAIR_DIRECTION


def test_global_coverage_bottleneck_requests_weakest_direction():
    route = route_certificate_resolving_experiment(
        decision=RobustRepairDecision.INCONCLUSIVE,
        stochastic_radius=0.1,
        scale_drift_radius=0.2,
        candidate_directional_uncertainty=0.3,
        global_directional_uncertainty=0.9,
    )
    assert route.bottleneck is EvidenceBottleneck.GLOBAL_DIRECTIONAL_COVERAGE
    assert route.experiment is ExperimentKind.PROBE_WEAKEST_DIRECTION


def test_authority_bottleneck_refuses_to_spend_more_probe_queries():
    route = route_certificate_resolving_experiment(
        decision=RobustRepairDecision.INCONCLUSIVE,
        stochastic_radius=9.0,
        scale_drift_radius=9.0,
        candidate_directional_uncertainty=9.0,
        global_directional_uncertainty=9.0,
        authority_is_bottleneck=True,
    )
    assert route.bottleneck is EvidenceBottleneck.CONTROLLER_AUTHORITY
    assert route.experiment is ExperimentKind.REPLAN_CONTROLLER_AUTHORITY


def test_resolved_certificate_stops_even_if_old_uncertainty_numbers_are_large():
    route = route_certificate_resolving_experiment(
        decision=RobustRepairDecision.CERTIFIED_REPAIR,
        stochastic_radius=2.0,
        scale_drift_radius=3.0,
        candidate_directional_uncertainty=4.0,
        global_directional_uncertainty=5.0,
    )
    assert route.experiment is ExperimentKind.STOP
