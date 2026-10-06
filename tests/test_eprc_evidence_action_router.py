from research.eprc.evidence_action_router import (
    EvidenceBottleneck,
    route_inconclusive_certificate,
)
from research.eprc.robust_repairability import RobustRepairDecision


def test_vqbet_like_scale_drift_blocks_useless_same_scale_queries():
    out = route_inconclusive_certificate(
        robust_decision=RobustRepairDecision.INCONCLUSIVE,
        planned_decision=RobustRepairDecision.INCONCLUSIVE,
        stochastic_radius=0.0,
        scale_drift_radius=3.0126,
    )
    assert out.bottleneck is EvidenceBottleneck.LOCALITY_LIMITED
    assert not out.additional_same_scale_queries_authorized
    assert "higher-order" in out.recommended_action


def test_amrc_resolution_authorizes_only_targeted_information_queries():
    out = route_inconclusive_certificate(
        robust_decision=RobustRepairDecision.INCONCLUSIVE,
        planned_decision=RobustRepairDecision.CERTIFIED_REPAIR,
        stochastic_radius=0.4,
        scale_drift_radius=0.1,
    )
    assert out.bottleneck is EvidenceBottleneck.INFORMATION_LIMITED
    assert out.additional_same_scale_queries_authorized


def test_terminal_certificate_stops_probing():
    out = route_inconclusive_certificate(
        robust_decision=RobustRepairDecision.CERTIFIED_IMPOSSIBLE,
        planned_decision=RobustRepairDecision.CERTIFIED_IMPOSSIBLE,
        stochastic_radius=1.0,
        scale_drift_radius=2.0,
    )
    assert out.bottleneck is EvidenceBottleneck.TERMINAL
    assert not out.additional_same_scale_queries_authorized


def test_stochastic_dominance_routes_to_repeatability_control():
    out = route_inconclusive_certificate(
        robust_decision=RobustRepairDecision.INCONCLUSIVE,
        planned_decision=RobustRepairDecision.INCONCLUSIVE,
        stochastic_radius=0.8,
        scale_drift_radius=0.2,
    )
    assert out.bottleneck is EvidenceBottleneck.STOCHASTIC_LIMITED
    assert out.additional_same_scale_queries_authorized


def test_equal_uncertainty_fails_closed_as_mixed():
    out = route_inconclusive_certificate(
        robust_decision=RobustRepairDecision.INCONCLUSIVE,
        planned_decision=RobustRepairDecision.INCONCLUSIVE,
        stochastic_radius=0.2,
        scale_drift_radius=0.2,
    )
    assert out.bottleneck is EvidenceBottleneck.MIXED_UNCERTAINTY
    assert not out.additional_same_scale_queries_authorized
