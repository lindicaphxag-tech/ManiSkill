import pytest

from cst.semantic_types import (
    ControllerSemanticType,
    TransportKind,
    classify_transport,
    joint_position_semantic_type,
)


def test_absolute_to_delta_current_is_stateful_exact_not_tensor_exact():
    source = joint_position_semantic_type(
        update_mode="absolute",
        normalized=True,
    )
    target = joint_position_semantic_type(
        update_mode="delta_current",
        normalized=True,
    )
    result = classify_transport(source, target)
    assert result.kind is TransportKind.STATEFUL_EXACT
    assert result.required_source_state == frozenset()
    assert result.required_target_state == frozenset({"current_qpos"})


def test_delta_target_requires_target_qpos_state():
    source = joint_position_semantic_type(
        update_mode="delta_target",
        normalized=True,
    )
    target = joint_position_semantic_type(
        update_mode="absolute",
        normalized=False,
    )
    result = classify_transport(source, target)
    assert result.kind is TransportKind.STATEFUL_EXACT
    assert result.required_source_state == frozenset({"target_qpos"})


def test_normalization_does_not_split_physical_semantic_family():
    a = joint_position_semantic_type(
        update_mode="absolute",
        normalized=True,
    )
    b = joint_position_semantic_type(
        update_mode="absolute",
        normalized=False,
    )
    result = classify_transport(a, b)
    assert result.kind is TransportKind.EXACT


@pytest.mark.parametrize(
    "target",
    [
        ControllerSemanticType(
            goal_space="joint_velocity",
            update_mode="absolute",
            frame="joint_coordinates",
            parameterization="qvel",
        ),
        ControllerSemanticType(
            goal_space="cartesian_pose",
            update_mode="delta_current",
            frame="base",
            parameterization="xyz_euler",
        ),
    ],
)
def test_cross_goal_space_never_gets_exact_authority(target):
    source = joint_position_semantic_type(
        update_mode="absolute",
        normalized=True,
    )
    result = classify_transport(source, target)
    assert result.kind is TransportKind.APPROXIMATE_REQUIRED


def test_frame_mismatch_requires_explicit_transform():
    source = ControllerSemanticType(
        goal_space="cartesian_pose",
        update_mode="absolute",
        frame="world",
        parameterization="xyz_euler",
    )
    target = ControllerSemanticType(
        goal_space="cartesian_pose",
        update_mode="absolute",
        frame="robot_base",
        parameterization="xyz_euler",
    )
    result = classify_transport(source, target)
    assert result.kind is TransportKind.APPROXIMATE_REQUIRED
    assert "frames differ" in result.reason


def test_rotation_chart_mismatch_is_not_silently_exact():
    source = ControllerSemanticType(
        goal_space="cartesian_pose",
        update_mode="delta_current",
        frame="robot_base",
        parameterization="axis_angle",
        hidden_state=frozenset({"current_pose"}),
    )
    target = ControllerSemanticType(
        goal_space="cartesian_pose",
        update_mode="delta_current",
        frame="robot_base",
        parameterization="xyz_euler",
        hidden_state=frozenset({"current_pose"}),
    )
    result = classify_transport(source, target)
    assert result.kind is TransportKind.APPROXIMATE_REQUIRED
    assert "parameterizations differ" in result.reason


def test_same_endpoint_but_different_interpolation_is_not_trace_exact():
    source = joint_position_semantic_type(
        update_mode="absolute",
        normalized=True,
        interpolation="none",
    )
    target = joint_position_semantic_type(
        update_mode="absolute",
        normalized=True,
        interpolation="linear",
    )
    result = classify_transport(source, target)
    assert result.kind is TransportKind.APPROXIMATE_REQUIRED
    assert "interpolation" in result.reason
