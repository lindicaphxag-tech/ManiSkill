import numpy as np

from cst_validation.effect_compiler import (
    EffectCommutationKind,
    certify_effect_commuting_transport,
)
from cst_validation.stateful_semantics import (
    JointCommandContract,
    JointCommandMode,
    JointControllerState,
)


def _state(q, target=None):
    q = np.asarray(q, dtype=float)
    if target is None:
        target = q
    return JointControllerState(
        current_qpos=q,
        target_qpos=np.asarray(target, dtype=float),
    )


def test_source_clipping_is_part_of_semantics_not_an_error():
    source = JointCommandContract(
        JointCommandMode.DELTA_CURRENT,
        True,
        -0.1,
        0.1,
    )
    target = JointCommandContract(JointCommandMode.ABSOLUTE, False)

    cert = certify_effect_commuting_transport(
        source,
        target,
        source_state=_state([0.2]),
        target_state=_state([0.2]),
        source_native_action=np.array([3.0]),
    )
    # Source controller itself clips 3 -> 1, so its physical meaning is +0.1.
    assert cert.authorized
    assert cert.kind is EffectCommutationKind.EXACT
    np.testing.assert_allclose(cert.source_effective_target, [0.3])
    np.testing.assert_allclose(cert.target_native_action, [0.3])


def test_target_saturation_is_refused_when_it_changes_physical_goal():
    source = JointCommandContract(JointCommandMode.ABSOLUTE, False)
    target = JointCommandContract(
        JointCommandMode.DELTA_CURRENT,
        True,
        -0.1,
        0.1,
    )

    cert = certify_effect_commuting_transport(
        source,
        target,
        source_state=_state([0.0, 0.0]),
        target_state=_state([0.0, 0.0]),
        source_native_action=np.array([0.05, 0.4]),
    )
    assert not cert.authorized
    assert cert.kind is EffectCommutationKind.TARGET_EFFECT_CHANGES_SEMANTICS
    assert cert.representable_mask.tolist() == [True, False]
    assert cert.changed_coordinates == (1,)
    np.testing.assert_allclose(cert.target_effective_target, [0.05, 0.1])


def test_hidden_target_state_changes_compiled_native_action_but_not_semantics():
    source = JointCommandContract(
        JointCommandMode.DELTA_TARGET,
        True,
        -0.1,
        0.1,
    )
    target = JointCommandContract(JointCommandMode.ABSOLUTE, False)

    a = certify_effect_commuting_transport(
        source,
        target,
        source_state=_state([0.0], target=[0.2]),
        target_state=_state([0.0]),
        source_native_action=np.array([0.5]),
    )
    b = certify_effect_commuting_transport(
        source,
        target,
        source_state=_state([0.0], target=[0.6]),
        target_state=_state([0.0]),
        source_native_action=np.array([0.5]),
    )

    assert a.authorized and b.authorized
    np.testing.assert_allclose(a.target_native_action, [0.25])
    np.testing.assert_allclose(b.target_native_action, [0.65])
    assert not np.allclose(a.target_native_action, b.target_native_action)


def test_same_action_tensor_is_not_semantically_equal_under_different_state():
    delta_target = JointCommandContract(
        JointCommandMode.DELTA_TARGET,
        True,
        -0.1,
        0.1,
    )
    action = np.array([0.4])

    first = certify_effect_commuting_transport(
        delta_target,
        JointCommandContract(JointCommandMode.ABSOLUTE, False),
        source_state=_state([0.0], target=[-0.5]),
        target_state=_state([0.0]),
        source_native_action=action,
    )
    second = certify_effect_commuting_transport(
        delta_target,
        JointCommandContract(JointCommandMode.ABSOLUTE, False),
        source_state=_state([0.0], target=[0.5]),
        target_state=_state([0.0]),
        source_native_action=action,
    )

    np.testing.assert_allclose(first.source_effective_target, [-0.46])
    np.testing.assert_allclose(second.source_effective_target, [0.54])
    assert not np.allclose(
        first.source_effective_target,
        second.source_effective_target,
    )


def test_random_exact_diagrams_close_to_numerical_precision():
    rng = np.random.default_rng(11037)
    source = JointCommandContract(
        JointCommandMode.DELTA_CURRENT,
        True,
        -0.2,
        0.2,
    )
    target = JointCommandContract(JointCommandMode.ABSOLUTE, False)

    for _ in range(2000):
        q = rng.uniform(-1.5, 1.5, size=7)
        native = rng.uniform(-2.5, 2.5, size=7)
        cert = certify_effect_commuting_transport(
            source,
            target,
            source_state=_state(q),
            target_state=_state(q),
            source_native_action=native,
        )
        assert cert.authorized
        assert cert.max_abs_residual <= 1e-12
        np.testing.assert_allclose(
            cert.source_effective_target,
            cert.target_effective_target,
            atol=1e-12,
        )
