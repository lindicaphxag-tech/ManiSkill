import numpy as np
import pytest

from cst import (
    ControllerState,
    JointPositionChart,
    native_copy_semantic_residual,
    transport_joint_position_action,
)


def chart(mode, lower, upper, normalized=True):
    return JointPositionChart(
        mode=mode,
        lower=np.asarray(lower, dtype=float),
        upper=np.asarray(upper, dtype=float),
        normalized=normalized,
    )


def test_absolute_and_delta_current_transport_same_physical_goal():
    source = chart("delta_current", [-0.2, -0.4], [0.2, 0.4])
    target = chart("absolute", [-2.0, -1.0], [2.0, 3.0])
    source_state = ControllerState(current_qpos=np.array([0.2, -0.3]))
    target_state = ControllerState(current_qpos=np.array([0.2, -0.3]))

    cert = transport_joint_position_action(
        source_chart=source,
        source_state=source_state,
        source_action=np.array([0.5, -0.5]),
        target_chart=target,
        target_state=target_state,
    )

    assert cert.accepted
    np.testing.assert_allclose(cert.source_goal, [0.3, -0.5], atol=1e-12)
    np.testing.assert_allclose(cert.reconstructed_goal, cert.source_goal, atol=1e-12)
    assert cert.semantic_residual == pytest.approx(0.0)


def test_naive_native_copy_exposes_double_interpretation():
    source = chart("delta_current", [-0.1], [0.1])
    target = chart("absolute", [-2.0], [2.0])
    source_state = ControllerState(current_qpos=np.array([0.2]))
    target_state = ControllerState(current_qpos=np.array([0.2]))
    source_action = np.array([0.5])

    residual = native_copy_semantic_residual(
        source_action=source_action,
        source_chart=source,
        source_state=source_state,
        target_chart=target,
        target_state=target_state,
    )
    assert residual == pytest.approx(0.75)

    cert = transport_joint_position_action(
        source_chart=source,
        source_state=source_state,
        source_action=source_action,
        target_chart=target,
        target_state=target_state,
    )
    assert cert.accepted
    np.testing.assert_allclose(cert.reconstructed_goal, [0.25], atol=1e-12)


def test_delta_target_requires_hidden_controller_target_state():
    target_delta = chart("delta_target", [-0.2], [0.2])
    with pytest.raises(ValueError, match="prior target_qpos"):
        target_delta.decode(
            np.array([0.5]),
            state=ControllerState(current_qpos=np.array([0.0])),
        )


def test_delta_target_and_delta_current_are_not_state_free_synonyms():
    source = chart("delta_target", [-0.2], [0.2])
    target = chart("delta_current", [-0.2], [0.2])
    source_state = ControllerState(
        current_qpos=np.array([0.0]),
        target_qpos=np.array([0.5]),
    )
    target_state = ControllerState(current_qpos=np.array([0.0]))

    cert = transport_joint_position_action(
        source_chart=source,
        source_state=source_state,
        source_action=np.array([0.5]),
        target_chart=target,
        target_state=target_state,
    )

    assert not cert.accepted
    assert not cert.target_representable
    assert "outside" in cert.reason


def test_transport_fails_closed_on_target_saturation():
    source = chart("absolute", [-2.0], [2.0])
    target = chart("delta_current", [-0.1], [0.1])
    state = ControllerState(current_qpos=np.array([0.0]))

    cert = transport_joint_position_action(
        source_chart=source,
        source_state=state,
        source_action=np.array([0.8]),
        target_chart=target,
        target_state=state,
    )

    assert not cert.accepted
    assert cert.target_action[0] > 1.0


def test_exact_transport_is_semantically_path_independent():
    absolute = chart("absolute", [-2.0], [2.0])
    delta_current = chart("delta_current", [-0.5], [0.5])
    delta_target = chart("delta_target", [-0.5], [0.5])

    source_state = ControllerState(current_qpos=np.array([0.1]))
    middle_state = ControllerState(current_qpos=np.array([0.1]))
    final_state = ControllerState(
        current_qpos=np.array([0.1]),
        target_qpos=np.array([0.2]),
    )
    action = np.array([0.2])

    direct = transport_joint_position_action(
        source_chart=absolute,
        source_state=source_state,
        source_action=action,
        target_chart=delta_target,
        target_state=final_state,
    )
    first = transport_joint_position_action(
        source_chart=absolute,
        source_state=source_state,
        source_action=action,
        target_chart=delta_current,
        target_state=middle_state,
    )
    assert first.accepted
    second = transport_joint_position_action(
        source_chart=delta_current,
        source_state=middle_state,
        source_action=first.target_action,
        target_chart=delta_target,
        target_state=final_state,
    )

    assert direct.accepted and second.accepted
    np.testing.assert_allclose(
        direct.reconstructed_goal,
        second.reconstructed_goal,
        atol=1e-12,
    )
    np.testing.assert_allclose(direct.reconstructed_goal, [0.4], atol=1e-12)


def test_unnormalized_chart_is_a_valid_native_parameterization():
    source = chart("absolute", [-1.0], [1.0], normalized=False)
    target = chart("absolute", [-2.0], [2.0], normalized=True)
    state = ControllerState(current_qpos=np.array([0.0]))

    cert = transport_joint_position_action(
        source_chart=source,
        source_state=state,
        source_action=np.array([0.4]),
        target_chart=target,
        target_state=state,
    )
    assert cert.accepted
    np.testing.assert_allclose(cert.target_action, [0.2], atol=1e-12)
