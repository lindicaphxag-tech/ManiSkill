import numpy as np

from research.eprc.repairability_atlas import (
    AtlasDecision,
    PolicyRepairSet,
    nominal_repair_set_contains,
    route_by_repairability,
)


def test_nominal_repairability_dominance_for_nested_image_balls():
    outer = np.eye(2)
    inner = 0.5 * np.eye(2)
    assert nominal_repair_set_contains(outer, 1.0, inner, 1.0)
    assert not nominal_repair_set_contains(inner, 1.0, outer, 1.0)


def test_dominance_fails_when_inner_has_unavailable_physical_direction():
    outer = np.array([[1.0], [0.0]])
    inner = np.array([[0.0], [1.0]])
    assert not nominal_repair_set_contains(outer, 1.0, inner, 1.0)


def test_atlas_routes_to_policy_that_can_robustly_repair_target():
    policies = [
        PolicyRepairSet("weak", 0.1 * np.eye(2), 0.01, 0.5, switch_cost=0.0),
        PolicyRepairSet("strong", np.eye(2), 0.01, 0.5, switch_cost=0.1),
    ]
    route = route_by_repairability(
        policies,
        np.array([0.4, 0.0]),
        residual_tolerance=0.02,
    )
    assert route.decision is AtlasDecision.ROUTE
    assert route.selected_policy == "strong"


def test_atlas_certifies_impossibility_only_when_every_policy_does():
    policies = [
        PolicyRepairSet("a", np.eye(2), 0.01, 0.2),
        PolicyRepairSet("b", 0.5 * np.eye(2), 0.01, 0.2),
    ]
    route = route_by_repairability(
        policies,
        np.array([2.0, 0.0]),
        residual_tolerance=0.05,
    )
    assert route.decision is AtlasDecision.CERTIFIED_IMPOSSIBLE
    assert route.selected_policy is None


def test_atlas_preserves_abstention_if_any_policy_is_unresolved():
    policies = [
        PolicyRepairSet("uncertain", np.eye(2), 0.2, 0.5),
        PolicyRepairSet("too_small", 0.1 * np.eye(2), 0.01, 0.2),
    ]
    route = route_by_repairability(
        policies,
        np.array([0.45, 0.0]),
        residual_tolerance=0.05,
    )
    assert route.decision is AtlasDecision.INCONCLUSIVE
