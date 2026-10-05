import numpy as np
import pytest

from cst.core import (
    JointControllerContext,
    JointGoalChart,
    MissingControllerStateError,
    exact_transport_identifiable,
    transport_action,
)


def test_delta_current_to_absolute_exactly_preserves_joint_goal():
    source = JointGoalChart(
        "delta_current", normalized=True, lower=-0.1, upper=0.1
    )
    target = JointGoalChart("absolute", normalized=False)
    result, cert = transport_action(
        source,
        target,
        np.array([0.5, -0.5]),
        JointControllerContext(q_current=np.array([0.2, -0.3])),
        JointControllerContext(),
    )
    assert cert.exact and cert.representable
    np.testing.assert_allclose(result.action, [0.25, -0.35], atol=1e-12)


def test_absolute_to_normalized_delta_current_round_trip():
    source = JointGoalChart("absolute")
    target = JointGoalChart(
        "delta_current", normalized=True, lower=-0.2, upper=0.2
    )
    result, cert = transport_action(
        source,
        target,
        np.array([0.4, -0.1]),
        JointControllerContext(),
        JointControllerContext(q_current=np.array([0.3, 0.0])),
    )
    assert cert.exact
    np.testing.assert_allclose(result.action, [0.5, -0.5], atol=1e-12)


def test_delta_target_is_not_identifiable_without_controller_target_state():
    chart = JointGoalChart(
        "delta_target", normalized=True, lower=-0.1, upper=0.1
    )
    identifiable, missing = exact_transport_identifiable(
        chart, JointControllerContext(q_current=np.zeros(2))
    )
    assert not identifiable
    assert missing == ("q_target",)
    with pytest.raises(MissingControllerStateError):
        chart.decode(
            np.zeros(2),
            JointControllerContext(q_current=np.zeros(2)),
        )


def test_same_native_delta_target_action_can_mean_different_goals():
    chart = JointGoalChart(
        "delta_target", normalized=False, lower=-0.2, upper=0.2
    )
    action = np.array([0.05, -0.02])
    first = chart.decode(
        action, JointControllerContext(q_target=np.array([0.1, 0.2]))
    )
    second = chart.decode(
        action, JointControllerContext(q_target=np.array([0.4, 0.2]))
    )
    assert not np.allclose(first, second)


def test_target_representability_fails_closed_instead_of_silent_clipping():
    source = JointGoalChart("absolute")
    target = JointGoalChart(
        "delta_current", normalized=True, lower=-0.1, upper=0.1
    )
    result, cert = transport_action(
        source,
        target,
        np.array([1.0]),
        JointControllerContext(),
        JointControllerContext(q_current=np.array([0.0])),
    )
    assert not cert.exact
    assert not cert.representable
    assert result.saturation.tolist() == [True]
    assert result.action[0] > 1.0


def test_delta_target_conversion_is_exact_when_hidden_target_is_observed():
    source = JointGoalChart(
        "delta_target", normalized=True, lower=-0.1, upper=0.1
    )
    target = JointGoalChart("absolute")
    result, cert = transport_action(
        source,
        target,
        np.array([0.5]),
        JointControllerContext(q_target=np.array([0.3])),
        JointControllerContext(),
    )
    assert cert.exact
    np.testing.assert_allclose(result.action, [0.35], atol=1e-12)
