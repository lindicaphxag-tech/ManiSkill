import numpy as np

from controller_semantic_ir import (
    AffineControllerIR,
    compile_affine_transport,
    normalized_joint_position_ir,
)


def test_compiler_derives_delta_current_to_absolute_conversion():
    source = normalized_joint_position_ir(
        mode="delta_current",
        physical_low=np.array([-0.1, -0.2]),
        physical_high=np.array([0.1, 0.2]),
    )
    target = normalized_joint_position_ir(
        mode="absolute",
        physical_low=np.array([-2.0, -2.0]),
        physical_high=np.array([2.0, 2.0]),
    )
    cert = compile_affine_transport(
        source=source,
        target=target,
        source_action=np.array([0.5, -0.5]),
        source_state=np.array([0.2, -0.3]),
        source_hidden=np.zeros(2),
        target_state=np.array([0.2, -0.3]),
        target_hidden=np.zeros(2),
    )
    np.testing.assert_allclose(cert.source_goal, [0.25, -0.4], atol=1e-12)
    np.testing.assert_allclose(cert.reconstructed_goal, cert.source_goal, atol=1e-12)
    np.testing.assert_allclose(cert.target_action, [0.125, -0.2], atol=1e-12)
    assert cert.bounded_representable
    assert cert.unique_if_exact


def test_compiler_exposes_current_vs_target_hidden_state_difference():
    source = normalized_joint_position_ir(
        mode="delta_current",
        physical_low=np.array([-0.1]),
        physical_high=np.array([0.1]),
    )
    target = normalized_joint_position_ir(
        mode="delta_target",
        physical_low=np.array([-0.1]),
        physical_high=np.array([0.1]),
    )
    cert = compile_affine_transport(
        source=source,
        target=target,
        source_action=np.array([0.5]),
        source_state=np.array([0.2]),
        source_hidden=np.array([0.0]),
        target_state=np.array([0.2]),
        target_hidden=np.array([0.5]),
    )
    # Source wants 0.25; target-relative controller would need -0.25 from its
    # stored target 0.50, i.e. native -2.5 outside [-1,1].
    np.testing.assert_allclose(cert.target_action, [-2.5], atol=1e-12)
    assert cert.algebraically_representable
    assert not cert.bounded_representable
    assert cert.native_margin[0] < 0


def test_rank_deficient_target_reports_unrepresentable_goal():
    source = AffineControllerIR(
        U=np.eye(2),
        X=np.zeros((2, 0)),
        Z=np.zeros((2, 0)),
        b=np.zeros(2),
        native_low=-np.ones(2),
        native_high=np.ones(2),
    )
    target = AffineControllerIR(
        U=np.array([[1.0], [0.0]]),
        X=np.zeros((2, 0)),
        Z=np.zeros((2, 0)),
        b=np.zeros(2),
        native_low=np.array([-1.0]),
        native_high=np.array([1.0]),
    )
    cert = compile_affine_transport(
        source=source,
        target=target,
        source_action=np.array([0.2, 0.7]),
        source_state=np.empty(0),
        source_hidden=np.empty(0),
        target_state=np.empty(0),
        target_hidden=np.empty(0),
    )
    assert cert.target_rank == 1
    assert not cert.algebraically_representable
    assert cert.residual_norm > 0.6


def test_redundant_target_reports_nonunique_exact_transport():
    source = AffineControllerIR(
        U=np.array([[1.0]]),
        X=np.zeros((1, 0)),
        Z=np.zeros((1, 0)),
        b=np.zeros(1),
        native_low=np.array([-1.0]),
        native_high=np.array([1.0]),
    )
    target = AffineControllerIR(
        U=np.array([[1.0, 1.0]]),
        X=np.zeros((1, 0)),
        Z=np.zeros((1, 0)),
        b=np.zeros(1),
        native_low=-np.ones(2),
        native_high=np.ones(2),
    )
    cert = compile_affine_transport(
        source=source,
        target=target,
        source_action=np.array([0.8]),
        source_state=np.empty(0),
        source_hidden=np.empty(0),
        target_state=np.empty(0),
        target_hidden=np.empty(0),
    )
    assert cert.algebraically_representable
    assert cert.bounded_representable
    assert cert.target_nullity == 1
    assert not cert.unique_if_exact
    np.testing.assert_allclose(cert.target_action, [0.4, 0.4], atol=1e-12)


def test_unique_exact_solution_outside_bounds_is_refused():
    source = AffineControllerIR(
        U=np.array([[1.0]]),
        X=np.zeros((1, 0)),
        Z=np.zeros((1, 0)),
        b=np.zeros(1),
        native_low=np.array([-2.0]),
        native_high=np.array([2.0]),
    )
    target = AffineControllerIR(
        U=np.array([[0.1]]),
        X=np.zeros((1, 0)),
        Z=np.zeros((1, 0)),
        b=np.zeros(1),
        native_low=np.array([-1.0]),
        native_high=np.array([1.0]),
    )
    cert = compile_affine_transport(
        source=source,
        target=target,
        source_action=np.array([0.5]),
        source_state=np.empty(0),
        source_hidden=np.empty(0),
        target_state=np.empty(0),
        target_hidden=np.empty(0),
    )
    assert cert.algebraically_representable
    assert not cert.bounded_representable
    assert cert.unique_if_exact
    assert cert.target_action[0] == 5.0


def test_random_full_rank_affine_compiler_reconstructs_exact_goals():
    rng = np.random.default_rng(20261006)
    for _ in range(300):
        D = 3
        U_source = rng.normal(size=(D, D))
        while abs(np.linalg.det(U_source)) < 0.2:
            U_source = rng.normal(size=(D, D))
        U_target = rng.normal(size=(D, D))
        while abs(np.linalg.det(U_target)) < 0.2:
            U_target = rng.normal(size=(D, D))

        source = AffineControllerIR(
            U=U_source,
            X=rng.normal(scale=0.1, size=(D, D)),
            Z=rng.normal(scale=0.1, size=(D, D)),
            b=rng.normal(scale=0.1, size=D),
            native_low=-np.full(D, 100.0),
            native_high=np.full(D, 100.0),
        )
        target = AffineControllerIR(
            U=U_target,
            X=rng.normal(scale=0.1, size=(D, D)),
            Z=rng.normal(scale=0.1, size=(D, D)),
            b=rng.normal(scale=0.1, size=D),
            native_low=-np.full(D, 100.0),
            native_high=np.full(D, 100.0),
        )
        cert = compile_affine_transport(
            source=source,
            target=target,
            source_action=rng.normal(size=D),
            source_state=rng.normal(size=D),
            source_hidden=rng.normal(size=D),
            target_state=rng.normal(size=D),
            target_hidden=rng.normal(size=D),
        )
        assert cert.algebraically_representable
        np.testing.assert_allclose(
            cert.reconstructed_goal,
            cert.source_goal,
            atol=1e-9,
            rtol=1e-9,
        )
