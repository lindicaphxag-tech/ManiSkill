import numpy as np

from research.eprc.linear_authority import LinearActionAuthority
from research.eprc.repairability_decomposition import (
    RepairabilityBottleneck,
    decompose_repairability,
)


def box(n):
    return LinearActionAuthority.from_box(-np.ones(n), np.ones(n))


def test_robot_limited_when_controller_cannot_express_target_direction():
    c = np.array([[1.0], [0.0]])
    j = np.array([[1.0]])
    result = decompose_repairability(
        j,
        c,
        np.array([0.0, 1.0]),
        nominal_action=np.zeros(1),
        authority=box(1),
        trust_radius=1.0,
    )
    assert result.bottleneck is RepairabilityBottleneck.ROBOT_LIMITED
    assert result.controller_image_residual > 0.9


def test_policy_limited_when_controller_can_but_frozen_policy_response_cannot():
    c = np.eye(2)
    j = np.array([[1.0], [0.0]])
    result = decompose_repairability(
        j,
        c,
        np.array([0.0, 0.4]),
        nominal_action=np.zeros(2),
        authority=box(2),
        trust_radius=1.0,
    )
    assert result.bottleneck is RepairabilityBottleneck.POLICY_LIMITED
    assert result.controller_image_residual < 1e-10
    assert result.policy_image_residual > 0.39
    assert result.policy_restriction_gap > 0.39


def test_authority_limited_is_distinct_from_policy_limited():
    c = np.eye(2)
    j = np.eye(2)
    a0 = np.array([0.9, 0.0])
    result = decompose_repairability(
        j,
        c,
        np.array([0.3, 0.0]),
        nominal_action=a0,
        authority=box(2),
        trust_radius=1.0,
    )
    assert result.policy_image_residual < 1e-10
    assert result.bottleneck is RepairabilityBottleneck.AUTHORITY_LIMITED
    assert result.authority_radius < result.minimum_required_support_radius


def test_model_limited_is_distinct_from_controller_authority():
    c = np.eye(2)
    j = np.eye(2)
    result = decompose_repairability(
        j,
        c,
        np.array([0.4, 0.0]),
        nominal_action=np.zeros(2),
        authority=box(2),
        trust_radius=0.2,
    )
    assert result.authority_radius > result.minimum_required_support_radius
    assert result.bottleneck is RepairabilityBottleneck.MODEL_LIMITED


def test_certified_case_has_positive_support_radius_slack():
    c = np.eye(2)
    j = np.eye(2)
    result = decompose_repairability(
        j,
        c,
        np.array([0.2, -0.1]),
        nominal_action=np.zeros(2),
        authority=box(2),
        trust_radius=0.5,
    )
    assert result.bottleneck is RepairabilityBottleneck.CERTIFIED
    assert result.support_radius_slack > 0


def test_policy_restriction_gap_is_nonnegative_under_random_fixtures():
    rng = np.random.default_rng(7)
    for _ in range(50):
        c = rng.normal(size=(4, 3))
        j = rng.normal(size=(3, 2))
        d = rng.normal(size=4)
        out = decompose_repairability(
            j,
            c,
            d,
            nominal_action=np.zeros(3),
            authority=box(3),
            trust_radius=1.0,
        )
        assert out.policy_restriction_gap >= -1e-12
        assert out.policy_image_residual + 1e-10 >= out.controller_image_residual
