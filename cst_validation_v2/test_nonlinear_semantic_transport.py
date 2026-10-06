import numpy as np

from nonlinear_semantic_transport import (
    compile_nonlinear_transport,
    planar_cartesian_chart,
    planar_two_link_joint_chart,
)
from semantic_morphism import SemanticMorphismKind


EMPTY = np.empty(0)


def test_joint_to_cartesian_preserves_exact_end_effector_goal():
    joint = planar_two_link_joint_chart()
    cart = planar_cartesian_chart()
    q = np.array([0.7, -0.9])
    cert = compile_nonlinear_transport(
        source=joint, target=cart,
        source_action=q, source_state=EMPTY, source_hidden=EMPTY,
        target_state=EMPTY, target_hidden=EMPTY,
    )
    assert cert.exact
    np.testing.assert_allclose(cert.target_action, cert.source_goal, atol=1e-8)
    assert cert.local_structure.kind is SemanticMorphismKind.EXACT_EQUIVALENCE


def test_cartesian_to_joint_detects_multiple_inverse_branches():
    cart = planar_cartesian_chart()
    joint = planar_two_link_joint_chart()
    desired = np.array([1.0, 0.5])
    starts = [
        np.array([0.0, 1.5]),
        np.array([1.0, -1.5]),
        np.array([-1.0, 1.5]),
        np.array([1.5, -1.0]),
    ]
    cert = compile_nonlinear_transport(
        source=cart, target=joint,
        source_action=desired, source_state=EMPTY, source_hidden=EMPTY,
        target_state=EMPTY, target_hidden=EMPTY,
        initial_guesses=starts,
    )
    assert cert.exact
    assert cert.distinct_exact_solutions >= 2
    np.testing.assert_allclose(cert.reconstructed_goal, desired, atol=1e-7)
    assert "globally ambiguous" in cert.reason


def test_unreachable_cartesian_goal_refuses():
    cart = planar_cartesian_chart(limit=4.0)
    joint = planar_two_link_joint_chart()
    cert = compile_nonlinear_transport(
        source=cart, target=joint,
        source_action=np.array([3.0, 0.0]),
        source_state=EMPTY, source_hidden=EMPTY,
        target_state=EMPTY, target_hidden=EMPTY,
        initial_guesses=[np.array([0.0, 0.0]), np.array([1.0, -1.0])],
    )
    assert not cert.exact
    assert cert.target_action is None
    assert cert.residual_norm > 0.9
    assert "refuse" in cert.reason


def test_singular_stretched_arm_exposes_local_rank_loss():
    joint = planar_two_link_joint_chart()
    cart = planar_cartesian_chart()
    cert = compile_nonlinear_transport(
        source=joint, target=cart,
        source_action=np.array([0.0, 0.0]),
        source_state=EMPTY, source_hidden=EMPTY,
        target_state=EMPTY, target_hidden=EMPTY,
    )
    assert cert.exact
    assert cert.local_structure.kind is SemanticMorphismKind.SOURCE_PROJECTION
    assert cert.local_structure.source_rank == 1


def test_cartesian_to_joint_regular_solution_is_locally_well_conditioned_enough():
    cart = planar_cartesian_chart()
    joint = planar_two_link_joint_chart()
    cert = compile_nonlinear_transport(
        source=cart, target=joint,
        source_action=np.array([0.5, 1.0]),
        source_state=EMPTY, source_hidden=EMPTY,
        target_state=EMPTY, target_hidden=EMPTY,
        initial_guesses=[np.array([0.2, 1.6]), np.array([1.2, -1.6])],
    )
    assert cert.exact
    assert cert.target_local_rank == 2
    assert np.isfinite(cert.target_local_condition)
    assert cert.native_margin is not None


def test_target_joint_limits_can_make_reachable_geometry_unavailable():
    cart = planar_cartesian_chart()
    limited = planar_two_link_joint_chart(joint_limit=0.2)
    desired = np.array([0.0, 2.0])
    cert = compile_nonlinear_transport(
        source=cart, target=limited,
        source_action=desired, source_state=EMPTY, source_hidden=EMPTY,
        target_state=EMPTY, target_hidden=EMPTY,
    )
    assert not cert.exact
    assert cert.target_action is None
