from types import SimpleNamespace

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from robomimic_reverse_actions import (
    OSCActionContract,
    ReverseStatus,
    absolute_pose_to_delta_action,
    compose_delta_with_pose,
    convert_robot_absolute_action,
    extract_osc_baseline_pose,
    extract_osc_contract,
    inverse_scale_physical_delta,
    scale_native_delta,
)


def _contract(goal_update_mode="achieved"):
    return OSCActionContract(
        input_min=np.full(6, -1.0),
        input_max=np.full(6, 1.0),
        output_min=np.array([-0.05, -0.05, -0.05, -0.5, -0.5, -0.5]),
        output_max=np.array([0.05, 0.05, 0.05, 0.5, 0.5, 0.5]),
        goal_update_mode=goal_update_mode,
    )


def test_inverse_scaling_is_exact_inside_controller_range():
    contract = _contract()
    rng = np.random.default_rng(270)
    for _ in range(1000):
        native = rng.uniform(-1.0, 1.0, size=6)
        physical = scale_native_delta(native, contract)
        recovered, representable, mask = inverse_scale_physical_delta(
            physical, contract
        )
        assert representable
        assert not np.any(mask)
        np.testing.assert_allclose(recovered, native, atol=1e-12)


def test_orientation_inverse_matches_robosuite_left_composition():
    contract = _contract()
    rng = np.random.default_rng(707)
    for _ in range(500):
        achieved_pos = rng.uniform(-0.3, 0.3, size=3)
        achieved_ori = Rotation.random(random_state=rng).as_matrix()
        native_delta = rng.uniform(-0.8, 0.8, size=6)
        physical = scale_native_delta(native_delta, contract)
        absolute = compose_delta_with_pose(
            achieved_pos, achieved_ori, physical
        )

        cert = absolute_pose_to_delta_action(
            absolute,
            achieved_position=achieved_pos,
            achieved_orientation=achieved_ori,
            contract=contract,
        )

        assert cert.status is ReverseStatus.EXACT
        np.testing.assert_allclose(
            cert.native_delta_action, native_delta, atol=1e-10
        )
        assert cert.residual_norm < 1e-10


def test_desired_goal_mode_uses_previous_desired_pose_not_achieved_pose():
    contract = _contract(goal_update_mode="desired")
    achieved_pos = np.array([0.0, 0.0, 0.0])
    achieved_ori = np.eye(3)
    desired_pos = np.array([0.2, -0.1, 0.3])
    desired_ori = Rotation.from_rotvec([0.2, 0.0, -0.1]).as_matrix()

    native_delta = np.array([0.2, -0.2, 0.4, 0.2, 0.1, -0.2])
    absolute = compose_delta_with_pose(
        desired_pos,
        desired_ori,
        scale_native_delta(native_delta, contract),
    )

    cert = absolute_pose_to_delta_action(
        absolute,
        achieved_position=achieved_pos,
        achieved_orientation=achieved_ori,
        desired_position=desired_pos,
        desired_orientation=desired_ori,
        contract=contract,
    )

    np.testing.assert_allclose(cert.native_delta_action, native_delta, atol=1e-10)


def test_out_of_range_absolute_goal_is_saturated_with_evidence():
    contract = _contract()
    absolute = np.array([0.2, 0.0, 0.0, 0.0, 0.0, 0.0])
    cert = absolute_pose_to_delta_action(
        absolute,
        achieved_position=np.zeros(3),
        achieved_orientation=np.eye(3),
        contract=contract,
    )

    assert cert.status is ReverseStatus.SATURATED
    assert not cert.representable
    assert cert.saturation_mask[0]
    assert cert.residual_norm > 0.1


def test_robot_action_preserves_gripper_and_other_remainder():
    contract = _contract()
    action = np.array([0.01, 0.0, 0.0, 0.1, 0.0, 0.0, -0.7, 0.25])
    converted, cert = convert_robot_absolute_action(
        action,
        achieved_position=np.zeros(3),
        achieved_orientation=np.eye(3),
        contract=contract,
    )
    assert cert.status is ReverseStatus.EXACT
    np.testing.assert_allclose(converted[6:], [-0.7, 0.25])


class _CurrentBaseController:
    input_min = np.full(6, -1.0)
    input_max = np.full(6, 1.0)
    output_min = np.full(6, -0.5)
    output_max = np.full(6, 0.5)
    _goal_update_mode = "achieved"
    input_ref_frame = "base"
    ref_pos = np.array([2.0, 3.0, 4.0])
    ref_ori_mat = np.eye(3)

    def update(self, force=False):
        assert force

    def world_to_origin_frame(self, value):
        return np.asarray(value) - np.array([1.0, 1.0, 1.0])

    def goal_origin_to_eef_pose(self):
        pose = np.eye(4)
        pose[:3, :3] = Rotation.from_rotvec([0.1, 0.2, 0.3]).as_matrix()
        return pose


def test_current_robosuite_base_frame_runtime_extraction():
    controller = _CurrentBaseController()
    contract = extract_osc_contract(controller)
    position, orientation = extract_osc_baseline_pose(controller)

    assert contract.goal_update_mode == "achieved"
    np.testing.assert_allclose(position, [1.0, 2.0, 3.0])
    np.testing.assert_allclose(
        orientation,
        Rotation.from_rotvec([0.1, 0.2, 0.3]).as_matrix(),
        atol=1e-12,
    )


class _LegacyController:
    input_min = np.full(6, -1.0)
    input_max = np.full(6, 1.0)
    output_min = np.full(6, -0.5)
    output_max = np.full(6, 0.5)
    ee_pos = np.array([0.1, 0.2, 0.3])
    ee_ori_mat = Rotation.from_rotvec([0.2, -0.1, 0.0]).as_matrix()

    def update(self, force=False):
        assert force


def test_legacy_robosuite_world_frame_runtime_extraction():
    controller = _LegacyController()
    position, orientation = extract_osc_baseline_pose(controller)
    np.testing.assert_allclose(position, controller.ee_pos)
    np.testing.assert_allclose(orientation, controller.ee_ori_mat)


def test_desired_mode_refuses_missing_controller_memory():
    with pytest.raises(ValueError, match="desired goal-update mode"):
        absolute_pose_to_delta_action(
            np.zeros(6),
            achieved_position=np.zeros(3),
            achieved_orientation=np.eye(3),
            contract=_contract(goal_update_mode="desired"),
        )
