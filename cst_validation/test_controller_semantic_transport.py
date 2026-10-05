import numpy as np

from controller_semantic_transport import (
    AffineActionChart,
    DriveSignature,
    JointPositionMode,
    JointPositionSemantics,
    transport_joint_position_action,
    transport_joint_position_sequence,
)


def _norm(low, high):
    return AffineActionChart(np.asarray(low, float), np.asarray(high, float), True)


def test_absolute_and_current_delta_transport_exactly_when_representable():
    source = JointPositionSemantics(
        JointPositionMode.DELTA_CURRENT,
        _norm([-0.1, -0.2], [0.1, 0.2]),
    )
    target = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-2.0, -2.0], [2.0, 2.0]),
    )
    cert = transport_joint_position_action(
        source=source,
        target=target,
        source_native_action=np.array([0.5, -0.5]),
        current_qpos=np.array([0.2, -0.3]),
    )
    np.testing.assert_allclose(cert.canonical_source_target, [0.25, -0.4])
    np.testing.assert_allclose(cert.reconstructed_target, [0.25, -0.4])
    assert cert.goal_equivalent
    assert np.all(cert.representable_mask)


def test_target_relative_delta_requires_hidden_target_state():
    source = JointPositionSemantics(
        JointPositionMode.DELTA_TARGET,
        _norm([-0.1], [0.1]),
    )
    target = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-2.0], [2.0]),
    )
    try:
        transport_joint_position_action(
            source=source,
            target=target,
            source_native_action=np.array([0.5]),
            current_qpos=np.array([0.0]),
        )
    except ValueError as exc:
        assert "previous_target_qpos" in str(exc)
    else:
        raise AssertionError("missing hidden target state must be rejected")


def test_current_relative_and_target_relative_are_not_semantically_interchangeable():
    delta_current = JointPositionSemantics(
        JointPositionMode.DELTA_CURRENT,
        _norm([-0.1], [0.1]),
    )
    delta_target = JointPositionSemantics(
        JointPositionMode.DELTA_TARGET,
        _norm([-0.1], [0.1]),
    )
    current = np.array([0.2])
    previous_target = np.array([0.5])
    source_action = np.array([0.5])  # physical +0.05 from current

    cert = transport_joint_position_action(
        source=delta_current,
        target=delta_target,
        source_native_action=source_action,
        current_qpos=current,
        target_previous_target_qpos=previous_target,
    )

    # Desired source goal is 0.25. Target-relative controller must command
    # -0.25 from its stored target 0.50, which is outside +/-0.1 and therefore
    # cannot be represented exactly. Naively copying +0.5 would be profoundly
    # wrong even though both action spaces are called "delta".
    np.testing.assert_allclose(cert.canonical_source_target, [0.25])
    assert not cert.goal_equivalent
    assert not cert.representable_mask[0]


def test_no_silent_clipping_when_target_chart_cannot_represent_goal():
    source = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-2.0], [2.0]),
    )
    target = JointPositionSemantics(
        JointPositionMode.DELTA_CURRENT,
        _norm([-0.05], [0.05]),
    )
    cert = transport_joint_position_action(
        source=source,
        target=target,
        source_native_action=np.array([0.5]),  # physical absolute goal 1.0
        current_qpos=np.array([0.0]),
    )
    assert not cert.goal_equivalent
    assert cert.target_native_action[0] > 1.0
    assert "outside" in cert.reason


def test_goal_equivalence_does_not_imply_drive_equivalence():
    sem = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-1.0, -1.0], [1.0, 1.0]),
    )
    drive_a = DriveSignature(
        stiffness=np.array([100.0, 100.0]),
        damping=np.array([10.0, 10.0]),
        force_limit=np.array([50.0, 50.0]),
        friction=np.array([0.0, 0.0]),
    )
    drive_b = DriveSignature(
        stiffness=np.array([200.0, 100.0]),
        damping=np.array([10.0, 10.0]),
        force_limit=np.array([50.0, 50.0]),
        friction=np.array([0.0, 0.0]),
    )
    cert = transport_joint_position_action(
        source=sem,
        target=sem,
        source_native_action=np.array([0.1, -0.2]),
        current_qpos=np.zeros(2),
        source_drive=drive_a,
        target_drive=drive_b,
    )
    assert cert.goal_equivalent
    assert cert.drive_equivalent is False
    assert "drive semantics differ" in cert.reason


def test_target_relative_sequence_updates_hidden_target_not_measured_state():
    source = JointPositionSemantics(
        JointPositionMode.DELTA_TARGET,
        _norm([-0.1], [0.1]),
    )
    target = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-2.0], [2.0]),
    )

    # Robot lags badly at q=0.0, but source controller's stored target advances
    # from 0.2 -> 0.25 -> 0.30. Correct conversion must follow target memory.
    result = transport_joint_position_sequence(
        source=source,
        target=target,
        source_native_actions=np.array([[0.5], [0.5]]),
        current_qpos_sequence=np.array([[0.0], [0.0]]),
        source_initial_target_qpos=np.array([0.2]),
    )
    assert result.all_goal_equivalent
    goals = [c.canonical_source_target[0] for c in result.certificates]
    np.testing.assert_allclose(goals, [0.25, 0.30])


def test_identical_drive_signatures_promote_goal_to_drive_equivalence():
    sem = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-1.0], [1.0]),
    )
    drive = DriveSignature(
        stiffness=np.array([100.0]),
        damping=np.array([10.0]),
        force_limit=np.array([50.0]),
        friction=np.array([0.0]),
    )
    cert = transport_joint_position_action(
        source=sem,
        target=sem,
        source_native_action=np.array([0.2]),
        current_qpos=np.array([0.0]),
        source_drive=drive,
        target_drive=drive,
    )
    assert cert.goal_equivalent
    assert cert.drive_equivalent is True


def test_representability_margin_is_positive_inside_and_negative_outside():
    source = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-2.0, -2.0], [2.0, 2.0]),
    )
    target = JointPositionSemantics(
        JointPositionMode.DELTA_CURRENT,
        _norm([-0.1, -0.1], [0.1, 0.1]),
    )
    inside = transport_joint_position_action(
        source=source,
        target=target,
        source_native_action=np.array([0.01, 0.01]),
        current_qpos=np.array([0.0, 0.0]),
    )
    assert np.all(inside.normalized_representability_margin > 0.0)

    outside = transport_joint_position_action(
        source=source,
        target=target,
        source_native_action=np.array([0.5, 0.0]),
        current_qpos=np.array([0.0, 0.0]),
    )
    assert outside.normalized_representability_margin[0] < 0.0
    assert not outside.goal_equivalent


def test_random_exact_transport_reconstructs_goal_whenever_target_is_representable():
    rng = np.random.default_rng(20261006)
    modes = (
        JointPositionMode.ABSOLUTE,
        JointPositionMode.DELTA_CURRENT,
        JointPositionMode.DELTA_TARGET,
    )
    for _ in range(500):
        source_mode = modes[int(rng.integers(0, len(modes)))]
        target_mode = modes[int(rng.integers(0, len(modes)))]
        source = JointPositionSemantics(
            source_mode,
            _norm([-0.5, -0.5], [0.5, 0.5]),
        )
        target = JointPositionSemantics(
            target_mode,
            _norm([-1.0, -1.0], [1.0, 1.0]),
        )
        current = rng.uniform(-0.25, 0.25, size=2)
        source_prev = rng.uniform(-0.25, 0.25, size=2)
        target_prev = rng.uniform(-0.25, 0.25, size=2)
        source_native = rng.uniform(-0.8, 0.8, size=2)

        cert = transport_joint_position_action(
            source=source,
            target=target,
            source_native_action=source_native,
            current_qpos=current,
            source_previous_target_qpos=(
                source_prev
                if source_mode is JointPositionMode.DELTA_TARGET
                else None
            ),
            target_previous_target_qpos=(
                target_prev
                if target_mode is JointPositionMode.DELTA_TARGET
                else None
            ),
        )
        if np.all(cert.representable_mask):
            assert cert.goal_equivalent
            np.testing.assert_allclose(
                cert.reconstructed_target,
                cert.canonical_source_target,
                atol=1e-10,
                rtol=0.0,
            )


def test_naively_copying_delta_current_into_delta_target_has_tracking_lag_error():
    current = np.array([0.2, -0.1])
    previous_target = np.array([0.5, 0.3])
    physical_delta = np.array([0.02, -0.04])

    desired_current_relative_goal = current + physical_delta
    naive_target_relative_goal = previous_target + physical_delta

    # The semantic error from copying the same physical delta is exactly the
    # controller tracking lag, independent of the chosen delta.
    np.testing.assert_allclose(
        naive_target_relative_goal - desired_current_relative_goal,
        previous_target - current,
        atol=1e-12,
    )
