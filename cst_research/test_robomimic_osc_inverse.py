import numpy as np

from robomimic_osc_inverse import (
    OSCActionChart,
    OSCInverseStatus,
    convert_absolute_action_with_remainder,
    forward_delta_to_absolute_goal,
    inverse_absolute_goal_to_delta,
    matrix_to_rotvec,
    orientation_distance,
    rotvec_to_matrix,
)


def _chart():
    return OSCActionChart(
        input_min=np.array([-1.0] * 6),
        input_max=np.array([1.0] * 6),
        output_min=np.array([-0.05, -0.05, -0.05, -0.5, -0.5, -0.5]),
        output_max=np.array([0.05, 0.05, 0.05, 0.5, 0.5, 0.5]),
    )


def test_so3_round_trip_random_rotvecs():
    rng = np.random.default_rng(270)
    for _ in range(500):
        v = rng.normal(size=3)
        v *= rng.uniform(0.0, np.pi - 1e-4) / max(np.linalg.norm(v), 1e-12)
        R = rotvec_to_matrix(v)
        recovered = matrix_to_rotvec(R)
        assert orientation_distance(rotvec_to_matrix(recovered), R) < 1e-8


def test_delta_absolute_delta_round_trip_achieved_mode():
    chart = _chart()
    achieved_pos = np.array([0.4, -0.2, 0.1])
    achieved_ori = rotvec_to_matrix(np.array([0.2, -0.1, 0.3]))
    desired_pos = np.array([9.0, 9.0, 9.0])
    desired_ori = np.eye(3)
    action = np.array([0.6, -0.2, 0.4, 0.3, -0.4, 0.2])

    goal = forward_delta_to_absolute_goal(
        chart,
        action,
        achieved_position=achieved_pos,
        achieved_orientation=achieved_ori,
        desired_position=desired_pos,
        desired_orientation=desired_ori,
        goal_update_mode="achieved",
    )
    cert = inverse_absolute_goal_to_delta(
        chart,
        goal.position,
        goal.orientation,
        achieved_position=achieved_pos,
        achieved_orientation=achieved_ori,
        desired_position=desired_pos,
        desired_orientation=desired_ori,
        goal_update_mode="achieved",
    )

    assert cert.status is OSCInverseStatus.EXACT
    np.testing.assert_allclose(cert.native_delta_action, action, atol=1e-9)


def test_desired_mode_is_stateful_and_uses_previous_goal_not_achieved_pose():
    chart = _chart()
    achieved_pos = np.array([0.0, 0.0, 0.0])
    achieved_ori = np.eye(3)
    desired_pos = np.array([0.7, -0.4, 0.2])
    desired_ori = rotvec_to_matrix(np.array([0.3, 0.2, -0.1]))
    action = np.array([0.2, 0.4, -0.6, -0.1, 0.2, 0.3])

    goal = forward_delta_to_absolute_goal(
        chart,
        action,
        achieved_position=achieved_pos,
        achieved_orientation=achieved_ori,
        desired_position=desired_pos,
        desired_orientation=desired_ori,
        goal_update_mode="desired",
    )
    cert = inverse_absolute_goal_to_delta(
        chart,
        goal.position,
        goal.orientation,
        achieved_position=achieved_pos,
        achieved_orientation=achieved_ori,
        desired_position=desired_pos,
        desired_orientation=desired_ori,
        goal_update_mode="desired",
    )

    assert cert.status is OSCInverseStatus.EXACT
    assert cert.uses_desired_goal_memory
    np.testing.assert_allclose(cert.native_delta_action, action, atol=1e-9)

    wrong = inverse_absolute_goal_to_delta(
        chart,
        goal.position,
        goal.orientation,
        achieved_position=achieved_pos,
        achieved_orientation=achieved_ori,
        desired_position=desired_pos,
        desired_orientation=desired_ori,
        goal_update_mode="achieved",
    )
    assert wrong.status is OSCInverseStatus.SATURATED or not np.allclose(
        wrong.native_delta_action, action, atol=1e-5
    )


def test_orientation_inverse_uses_group_composition_not_rotvec_subtraction():
    chart = _chart()
    base = rotvec_to_matrix(np.array([0.35, -0.2, 0.25]))
    delta = np.array([0.15, 0.25, -0.3])
    goal = rotvec_to_matrix(delta) @ base

    cert = inverse_absolute_goal_to_delta(
        chart,
        np.zeros(3),
        goal,
        achieved_position=np.zeros(3),
        achieved_orientation=base,
        desired_position=np.zeros(3),
        desired_orientation=np.eye(3),
        goal_update_mode="achieved",
    )

    expected_native, representable = chart.encode_delta(
        np.concatenate([np.zeros(3), delta])
    )
    assert representable
    assert cert.status is OSCInverseStatus.EXACT
    np.testing.assert_allclose(cert.native_delta_action, expected_native, atol=1e-8)

    naive = matrix_to_rotvec(goal) - matrix_to_rotvec(base)
    assert np.linalg.norm(naive - delta) > 1e-3


def test_unrepresentable_absolute_goal_is_explicitly_saturated():
    chart = _chart()
    cert = inverse_absolute_goal_to_delta(
        chart,
        np.array([0.2, 0.0, 0.0]),
        np.eye(3),
        achieved_position=np.zeros(3),
        achieved_orientation=np.eye(3),
        desired_position=np.zeros(3),
        desired_orientation=np.eye(3),
        goal_update_mode="achieved",
    )
    assert cert.status is OSCInverseStatus.SATURATED
    assert not cert.representable
    assert cert.position_residual_norm > 0.1


def test_gripper_and_other_remainder_is_preserved_exactly():
    chart = _chart()
    action_abs = np.array([0.01, -0.02, 0.03, 0.1, -0.2, 0.3, -1.0, 0.25])
    converted, cert = convert_absolute_action_with_remainder(
        chart,
        action_abs,
        achieved_position=np.zeros(3),
        achieved_orientation=np.eye(3),
        desired_position=np.zeros(3),
        desired_orientation=np.eye(3),
        goal_update_mode="achieved",
    )
    assert cert.status is OSCInverseStatus.EXACT
    np.testing.assert_allclose(converted[-2:], action_abs[-2:])


def test_random_executable_goal_round_trip_property():
    rng = np.random.default_rng(20261006)
    chart = _chart()
    for mode in ("achieved", "desired"):
        for _ in range(1000):
            achieved_pos = rng.uniform(-1.0, 1.0, 3)
            desired_pos = rng.uniform(-1.0, 1.0, 3)
            achieved_ori = rotvec_to_matrix(rng.uniform(-0.6, 0.6, 3))
            desired_ori = rotvec_to_matrix(rng.uniform(-0.6, 0.6, 3))
            action = rng.uniform(-0.95, 0.95, 6)
            goal = forward_delta_to_absolute_goal(
                chart,
                action,
                achieved_position=achieved_pos,
                achieved_orientation=achieved_ori,
                desired_position=desired_pos,
                desired_orientation=desired_ori,
                goal_update_mode=mode,
            )
            cert = inverse_absolute_goal_to_delta(
                chart,
                goal.position,
                goal.orientation,
                achieved_position=achieved_pos,
                achieved_orientation=achieved_ori,
                desired_position=desired_pos,
                desired_orientation=desired_ori,
                goal_update_mode=mode,
            )
            assert cert.status is OSCInverseStatus.EXACT
            np.testing.assert_allclose(cert.native_delta_action, action, atol=1e-8)
