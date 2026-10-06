import itertools

import numpy as np

from maniskill_joint_contract import (
    JointPositionContract,
    JointTransportStatus,
    transport_joint_position_action,
)


def _contract(mode, normalized=True, bound=0.2):
    if mode == "absolute":
        return JointPositionContract(
            use_delta=False,
            use_target=False,
            normalize_action=normalized,
            low=np.array([-2.0, -2.0]),
            high=np.array([2.0, 2.0]),
        )
    if mode == "delta_current":
        return JointPositionContract(
            use_delta=True,
            use_target=False,
            normalize_action=normalized,
            low=np.array([-bound, -bound]),
            high=np.array([bound, bound]),
        )
    if mode == "delta_target":
        return JointPositionContract(
            use_delta=True,
            use_target=True,
            normalize_action=normalized,
            low=np.array([-bound, -bound]),
            high=np.array([bound, bound]),
        )
    raise ValueError(mode)


def test_issue_429_delta_current_to_absolute_case_is_exact():
    source = _contract("delta_current", normalized=True, bound=0.1)
    target = _contract("absolute", normalized=False)
    cert = transport_joint_position_action(
        source,
        target,
        current_qpos=np.array([0.2, -0.3]),
        source_target_qpos=np.array([0.2, -0.3]),
        target_target_qpos=np.array([0.2, -0.3]),
        source_native_action=np.array([0.5, -0.5]),
    )

    assert cert.status is JointTransportStatus.EXACT
    np.testing.assert_allclose(cert.source_goal_qpos, [0.25, -0.35])
    np.testing.assert_allclose(cert.target_native_action, [0.25, -0.35])
    assert cert.residual_norm == 0.0


def test_delta_target_requires_controller_memory_to_transport():
    source = _contract("delta_target", normalized=True, bound=0.2)
    target = _contract("absolute", normalized=True)
    cert = transport_joint_position_action(
        source,
        target,
        current_qpos=np.array([0.0, 0.0]),
        source_target_qpos=np.array([0.7, -0.4]),
        target_target_qpos=np.array([0.0, 0.0]),
        source_native_action=np.array([0.5, -0.5]),
    )

    assert cert.status is JointTransportStatus.EXACT
    assert cert.requires_source_target_state
    np.testing.assert_allclose(cert.source_goal_qpos, [0.8, -0.5])


def test_target_delta_target_requires_target_memory_handshake():
    source = _contract("absolute", normalized=True)
    target = _contract("delta_target", normalized=True, bound=0.5)
    cert = transport_joint_position_action(
        source,
        target,
        current_qpos=np.array([0.0, 0.0]),
        source_target_qpos=np.array([0.0, 0.0]),
        target_target_qpos=np.array([0.4, -0.2]),
        source_native_action=np.array([0.25, -0.25]),
    )

    assert cert.requires_target_target_state
    assert cert.status is JointTransportStatus.SATURATED


def test_saturation_is_reported_instead_of_hidden_by_clipping():
    source = _contract("absolute", normalized=False)
    target = _contract("delta_current", normalized=True, bound=0.1)
    cert = transport_joint_position_action(
        source,
        target,
        current_qpos=np.array([0.0, 0.0]),
        source_target_qpos=np.array([0.0, 0.0]),
        target_target_qpos=np.array([0.0, 0.0]),
        source_native_action=np.array([1.0, -1.0]),
    )

    assert cert.status is JointTransportStatus.SATURATED
    assert not cert.target_representable
    assert cert.residual_norm > 1.0


def test_random_pair_matrix_is_exact_whenever_required_command_is_in_range():
    rng = np.random.default_rng(429)
    modes = ["absolute", "delta_current", "delta_target"]
    normalizations = [False, True]

    checked = 0
    exact = 0
    saturated = 0
    for src_mode, tgt_mode, src_norm, tgt_norm in itertools.product(
        modes, modes, normalizations, normalizations
    ):
        source = _contract(src_mode, normalized=src_norm, bound=0.5)
        target = _contract(tgt_mode, normalized=tgt_norm, bound=0.5)
        for _ in range(100):
            q = rng.uniform(-0.5, 0.5, size=2)
            source_target = rng.uniform(-0.5, 0.5, size=2)
            target_target = rng.uniform(-0.5, 0.5, size=2)
            if src_norm:
                action = rng.uniform(-1.0, 1.0, size=2)
            else:
                action = rng.uniform(source.low, source.high)

            cert = transport_joint_position_action(
                source,
                target,
                current_qpos=q,
                source_target_qpos=source_target,
                target_target_qpos=target_target,
                source_native_action=action,
            )
            checked += 1
            if cert.target_representable:
                assert cert.status is JointTransportStatus.EXACT
                assert cert.residual_norm < 1e-10
                exact += 1
            else:
                assert cert.status is JointTransportStatus.SATURATED
                saturated += 1

    assert checked == 3600
    assert exact > 0
    assert saturated > 0
