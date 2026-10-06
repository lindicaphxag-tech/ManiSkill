import numpy as np

from certified_transport import TransportAuthority, compile_certified_affine_transport
from controller_semantic_ir import AffineControllerIR, normalized_joint_position_ir


def _empty(dim):
    return np.zeros((dim, 0))


def test_exact_joint_chart_transport_gets_exact_semantic_authority():
    source = normalized_joint_position_ir(
        mode="delta_current",
        physical_low=np.array([-0.2, -0.2]),
        physical_high=np.array([0.2, 0.2]),
    )
    target = normalized_joint_position_ir(
        mode="absolute",
        physical_low=np.array([-2.0, -2.0]),
        physical_high=np.array([2.0, 2.0]),
    )
    cert = compile_certified_affine_transport(
        source=source, target=target,
        source_action=np.array([0.5, -0.5]),
        source_state=np.array([0.1, -0.1]), source_hidden=np.zeros(2),
        target_state=np.array([0.1, -0.1]), target_hidden=np.zeros(2),
    )
    assert cert.authority is TransportAuthority.EXACT_SEMANTIC
    assert cert.executable_action is not None


def test_redundant_target_only_gets_observable_exact_authority():
    source = AffineControllerIR(
        U=np.eye(2), X=_empty(2), Z=_empty(2), b=np.zeros(2),
        native_low=-np.ones(2), native_high=np.ones(2),
    )
    target = AffineControllerIR(
        U=np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0]]),
        X=_empty(2), Z=_empty(2), b=np.zeros(2),
        native_low=-np.ones(3), native_high=np.ones(3),
    )
    cert = compile_certified_affine_transport(
        source=source, target=target,
        source_action=np.array([0.2, -0.1]),
        source_state=np.empty(0), source_hidden=np.empty(0),
        target_state=np.empty(0), target_hidden=np.empty(0),
    )
    assert cert.authority is TransportAuthority.OBSERVABLE_EXACT
    assert cert.structure.target_kernel_dim == 1


def test_structural_unrepresentability_refuses_even_when_one_action_fits():
    source = AffineControllerIR(
        U=np.eye(2), X=_empty(2), Z=_empty(2), b=np.zeros(2),
        native_low=-np.ones(2), native_high=np.ones(2),
    )
    target = AffineControllerIR(
        U=np.array([[1.0], [0.0]]), X=_empty(2), Z=_empty(2), b=np.zeros(2),
        native_low=-np.ones(1), native_high=np.ones(1),
    )
    cert = compile_certified_affine_transport(
        source=source, target=target,
        source_action=np.array([0.4, 0.0]),
        source_state=np.empty(0), source_hidden=np.empty(0),
        target_state=np.empty(0), target_hidden=np.empty(0),
    )
    assert cert.instance.bounded_representable
    assert cert.authority is TransportAuthority.REFUSE
    assert cert.executable_action is None


def test_out_of_bounds_exact_algebraic_solution_is_not_executed():
    source = AffineControllerIR(
        U=np.array([[1.0]]), X=_empty(1), Z=_empty(1), b=np.zeros(1),
        native_low=np.array([-2.0]), native_high=np.array([2.0]),
    )
    target = AffineControllerIR(
        U=np.array([[0.1]]), X=_empty(1), Z=_empty(1), b=np.zeros(1),
        native_low=np.array([-1.0]), native_high=np.array([1.0]),
    )
    cert = compile_certified_affine_transport(
        source=source, target=target,
        source_action=np.array([0.5]),
        source_state=np.empty(0), source_hidden=np.empty(0),
        target_state=np.empty(0), target_hidden=np.empty(0),
    )
    assert cert.instance.algebraically_representable
    assert not cert.instance.bounded_representable
    assert cert.authority is TransportAuthority.APPROXIMATE_ONLY
    assert cert.executable_action is None


def test_random_invertible_pairs_get_exact_authority():
    rng = np.random.default_rng(20261006)
    for _ in range(200):
        dim = 3
        us = rng.normal(size=(dim, dim))
        ut = rng.normal(size=(dim, dim))
        while abs(np.linalg.det(us)) < 0.25:
            us = rng.normal(size=(dim, dim))
        while abs(np.linalg.det(ut)) < 0.25:
            ut = rng.normal(size=(dim, dim))
        source = AffineControllerIR(
            U=us, X=np.zeros((dim, dim)), Z=np.zeros((dim, dim)), b=np.zeros(dim),
            native_low=-np.full(dim, 100.0), native_high=np.full(dim, 100.0),
        )
        target = AffineControllerIR(
            U=ut, X=np.zeros((dim, dim)), Z=np.zeros((dim, dim)), b=np.zeros(dim),
            native_low=-np.full(dim, 100.0), native_high=np.full(dim, 100.0),
        )
        cert = compile_certified_affine_transport(
            source=source, target=target,
            source_action=rng.normal(size=dim),
            source_state=rng.normal(size=dim), source_hidden=rng.normal(size=dim),
            target_state=rng.normal(size=dim), target_hidden=rng.normal(size=dim),
        )
        assert cert.authority is TransportAuthority.EXACT_SEMANTIC
