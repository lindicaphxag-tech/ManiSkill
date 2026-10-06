import numpy as np
import pytest

from cst.core import JointControllerContext, JointGoalChart
from cst.provenance import (
    reconstruct_joint_goal_trace,
    sequence_state_requirement,
)


def _chart(mode):
    return JointGoalChart(
        mode=mode,
        normalized=True,
        lower=np.array([-0.1, -0.2]),
        upper=np.array([0.1, 0.2]),
    )


def test_absolute_sequence_needs_no_hidden_reference_state():
    chart = JointGoalChart(
        mode="absolute",
        normalized=False,
        lower=None,
        upper=None,
    )
    actions = np.array([[0.2, -0.3], [0.4, 0.1]])
    result = reconstruct_joint_goal_trace(chart, actions)
    np.testing.assert_allclose(result.semantic_goals, actions)
    assert result.requirement.required_initial_state == ()
    assert result.requirement.required_per_step_state == ()


def test_delta_current_refuses_action_only_reconstruction():
    chart = _chart("delta_current")
    actions = np.array([[0.5, -0.5], [0.0, 1.0]])
    req = sequence_state_requirement(chart)
    assert req.required_per_step_state == ("q_current",)
    with pytest.raises(ValueError, match="q_current at every step"):
        reconstruct_joint_goal_trace(chart, actions)


def test_delta_current_decodes_with_measured_reference_trace():
    chart = _chart("delta_current")
    actions = np.array([[0.5, -0.5], [0.0, 1.0]])
    current = np.array([[0.2, -0.3], [0.24, -0.38]])
    result = reconstruct_joint_goal_trace(
        chart,
        actions,
        q_current_trace=current,
    )
    np.testing.assert_allclose(
        result.semantic_goals,
        [[0.25, -0.4], [0.24, -0.18]],
        atol=1e-12,
    )


def test_delta_target_reconstructs_entire_reference_trace_from_one_initial_state():
    chart = _chart("delta_target")
    actions = np.array([[0.5, -0.5], [0.0, 1.0], [-1.0, 0.0]])
    result = reconstruct_joint_goal_trace(
        chart,
        actions,
        initial_context=JointControllerContext(q_target=np.array([0.2, -0.3])),
    )
    np.testing.assert_allclose(
        result.reference_trace,
        [[0.2, -0.3], [0.25, -0.4], [0.25, -0.2]],
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.semantic_goals,
        [[0.25, -0.4], [0.25, -0.2], [0.15, -0.2]],
        atol=1e-12,
    )
    assert result.requirement.required_initial_state == ("q_target",)
    assert result.requirement.required_per_step_state == ()
    assert result.requirement.recursively_reconstructible == ("q_target",)


def test_delta_target_refuses_without_initial_reference():
    chart = _chart("delta_target")
    with pytest.raises(ValueError, match="initial q_target"):
        reconstruct_joint_goal_trace(chart, np.zeros((2, 2)))


def test_relative_latched_chunk_reconstructs_from_one_fixed_reference():
    chart = _chart("relative_latched")
    actions = np.array([[0.5, -0.5], [0.0, 1.0], [-1.0, 0.0]])
    result = reconstruct_joint_goal_trace(
        chart,
        actions,
        initial_context=JointControllerContext(
            q_latched=np.array([0.2, -0.3])
        ),
    )
    np.testing.assert_allclose(
        result.reference_trace,
        [[0.2, -0.3], [0.2, -0.3], [0.2, -0.3]],
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.semantic_goals,
        [[0.25, -0.4], [0.2, -0.1], [0.1, -0.3]],
        atol=1e-12,
    )
    assert result.requirement.required_initial_state == ("q_latched",)
    assert result.requirement.required_per_step_state == ()
    assert result.requirement.recursively_reconstructible == ()


def test_relative_latched_refuses_without_chunk_reference():
    chart = _chart("relative_latched")
    with pytest.raises(ValueError, match="q_latched"):
        reconstruct_joint_goal_trace(chart, np.zeros((2, 2)))
