import numpy as np

from cst_validation.stateful_semantics import (
    JointCommandContract,
    JointCommandMode,
    JointControllerState,
    advance_target_state,
    compile_joint_transport,
)


def _state(current, target=None):
    current = np.asarray(current, dtype=float)
    if target is None:
        target = current
    return JointControllerState(current, np.asarray(target, dtype=float))


def test_delta_current_to_absolute_is_exact_when_target_is_representable():
    source = JointCommandContract(
        JointCommandMode.DELTA_CURRENT, True, -0.1, 0.1
    )
    target = JointCommandContract(JointCommandMode.ABSOLUTE, False)
    result = compile_joint_transport(
        source,
        target,
        source_state=_state([0.2, -0.3]),
        target_state=_state([0.2, -0.3]),
        source_native_action=np.array([0.5, -0.5]),
    )
    assert result.exact
    np.testing.assert_allclose(result.source_target_qpos, [0.25, -0.35])
    np.testing.assert_allclose(result.target_native_action, [0.25, -0.35])
    np.testing.assert_allclose(result.target_residual, 0.0, atol=1e-12)


def test_absolute_to_delta_current_refuses_unrepresentable_jump():
    source = JointCommandContract(JointCommandMode.ABSOLUTE, False)
    target = JointCommandContract(
        JointCommandMode.DELTA_CURRENT, True, -0.1, 0.1
    )
    result = compile_joint_transport(
        source,
        target,
        source_state=_state([0.0, 0.0]),
        target_state=_state([0.0, 0.0]),
        source_native_action=np.array([0.05, 0.5]),
    )
    assert not result.exact
    assert result.representable_mask.tolist() == [True, False]
    np.testing.assert_allclose(result.target_target_qpos, [0.05, 0.1])


def test_delta_target_conversion_depends_on_hidden_previous_target():
    source = JointCommandContract(
        JointCommandMode.DELTA_TARGET, True, -0.1, 0.1
    )
    target = JointCommandContract(JointCommandMode.ABSOLUTE, False)
    action = np.array([0.5])

    first = compile_joint_transport(
        source,
        target,
        source_state=_state([0.0], target=[0.2]),
        target_state=_state([0.0]),
        source_native_action=action,
    )
    second = compile_joint_transport(
        source,
        target,
        source_state=_state([0.0], target=[0.6]),
        target_state=_state([0.0]),
        source_native_action=action,
    )

    assert first.source_requires_target_state
    np.testing.assert_allclose(first.target_native_action, [0.25])
    np.testing.assert_allclose(second.target_native_action, [0.65])
    assert not np.allclose(first.target_native_action, second.target_native_action)


def test_delta_target_to_delta_target_preserves_state_machine_relation():
    source = JointCommandContract(
        JointCommandMode.DELTA_TARGET, True, -0.2, 0.2
    )
    target = JointCommandContract(
        JointCommandMode.DELTA_TARGET, True, -0.5, 0.5
    )
    source_state = _state([0.0, 0.0], target=[0.1, -0.2])
    target_state = _state([0.0, 0.0], target=[0.1, -0.2])

    for native in (
        np.array([0.25, -0.10]),
        np.array([-0.20, 0.15]),
        np.array([0.05, 0.20]),
    ):
        cert = compile_joint_transport(
            source,
            target,
            source_state=source_state,
            target_state=target_state,
            source_native_action=native,
        )
        assert cert.exact
        np.testing.assert_allclose(
            cert.source_target_qpos,
            cert.target_target_qpos,
            atol=1e-12,
        )
        # Advance both hidden target states to the common physical target.
        source_state = advance_target_state(
            source_state, cert.source_target_qpos
        )
        target_state = advance_target_state(
            target_state, cert.target_target_qpos
        )
        np.testing.assert_allclose(
            source_state.target_qpos,
            target_state.target_qpos,
            atol=1e-12,
        )


def test_state_mismatch_breaks_naive_delta_target_action_copy():
    source = JointCommandContract(
        JointCommandMode.DELTA_TARGET, True, -0.1, 0.1
    )
    target = JointCommandContract(
        JointCommandMode.DELTA_TARGET, True, -0.1, 0.1
    )
    source_state = _state([0.0], target=[0.4])
    target_state = _state([0.0], target=[-0.2])
    native = np.array([0.5])

    source_target = 0.45
    naive_target = -0.15
    assert not np.isclose(source_target, naive_target)

    cert = compile_joint_transport(
        source,
        target,
        source_state=source_state,
        target_state=target_state,
        source_native_action=native,
    )
    # Exact semantic repair requires a +0.65 jump on a +/-0.1 target-delta
    # controller, so the compiler must refuse rather than silently copy.
    assert not cert.exact
    assert cert.target_requires_target_state


def test_randomized_exact_delta_current_to_absolute_transport():
    rng = np.random.default_rng(20261006)
    source = JointCommandContract(
        JointCommandMode.DELTA_CURRENT, True, -0.1, 0.1
    )
    target = JointCommandContract(JointCommandMode.ABSOLUTE, False)

    for _ in range(1000):
        q = rng.uniform(-1.5, 1.5, size=7)
        action = rng.uniform(-1.0, 1.0, size=7)
        cert = compile_joint_transport(
            source,
            target,
            source_state=_state(q),
            target_state=_state(q),
            source_native_action=action,
        )
        assert cert.exact
        expected = q + 0.1 * action
        np.testing.assert_allclose(cert.target_native_action, expected, atol=1e-12)
