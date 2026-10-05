import numpy as np

from cst.core import JointControllerContext, JointGoalChart
from cst.reachability import (
    certify_joint_goal_horizon,
    construct_delta_target_sequence,
)


def test_delta_current_proves_one_step_impossible_and_needs_feedback():
    chart = JointGoalChart(
        "delta_current",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )
    cert = certify_joint_goal_horizon(
        chart,
        np.array([0.35]),
        JointControllerContext(q_current=np.array([0.0])),
    )
    assert cert.status == "multi_step_semantic_possible"
    assert not cert.one_step_exact
    assert cert.min_semantic_steps == 4
    assert cert.requires_intermediate_state_feedback


def test_delta_target_minimum_horizon_is_constructive_at_e1():
    chart = JointGoalChart(
        "delta_target",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )
    context = JointControllerContext(q_target=np.array([0.0, 0.2]))
    goal = np.array([0.35, -0.05])

    seq = construct_delta_target_sequence(chart, goal, context)

    assert seq.certificate.min_semantic_steps == 4
    assert not seq.certificate.requires_intermediate_state_feedback
    assert seq.native_actions.shape == (4, 2)
    np.testing.assert_allclose(seq.semantic_goals[-1], goal, atol=1e-12)

    q_target = context.q_target.copy()
    for action in seq.native_actions:
        q_target = chart.decode(
            action,
            JointControllerContext(q_target=q_target),
        )
    np.testing.assert_allclose(q_target, goal, atol=1e-12)


def test_absolute_out_of_range_is_not_fixed_by_repetition():
    chart = JointGoalChart(
        "absolute",
        normalized=True,
        lower=-1.0,
        upper=1.0,
    )
    cert = certify_joint_goal_horizon(
        chart,
        np.array([2.0]),
        JointControllerContext(),
    )
    assert cert.status == "unrepresentable"
    assert cert.min_semantic_steps is None
    assert not cert.requires_intermediate_state_feedback


def test_asymmetric_increment_box_has_directional_horizon():
    chart = JointGoalChart(
        "delta_target",
        normalized=True,
        lower=np.array([-0.05, -0.2]),
        upper=np.array([0.2, 0.1]),
    )
    cert = certify_joint_goal_horizon(
        chart,
        np.array([0.39, -0.39]),
        JointControllerContext(q_target=np.zeros(2)),
    )
    # +0.39 needs 2 steps in joint 0; -0.39 needs 2 steps in joint 1.
    assert cert.min_semantic_steps == 2


def test_unreachable_direction_is_fail_closed():
    chart = JointGoalChart(
        "delta_target",
        normalized=True,
        lower=0.0,
        upper=0.1,
    )
    cert = certify_joint_goal_horizon(
        chart,
        np.array([-0.1]),
        JointControllerContext(q_target=np.array([0.0])),
    )
    assert cert.status == "unrepresentable"
    assert cert.min_semantic_steps is None


def test_one_step_exact_is_not_overstated_as_multi_step():
    chart = JointGoalChart(
        "delta_current",
        normalized=True,
        lower=-0.2,
        upper=0.2,
    )
    cert = certify_joint_goal_horizon(
        chart,
        np.array([0.15, -0.05]),
        JointControllerContext(q_current=np.zeros(2)),
    )
    assert cert.status == "one_step_exact"
    assert cert.min_semantic_steps == 1
    assert not cert.requires_intermediate_state_feedback
