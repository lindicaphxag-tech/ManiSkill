import numpy as np

from semantic_morphism import (
    SemanticMorphismKind,
    analyze_linear_semantic_morphism,
    transport_shared_observable,
)


def test_identity_charts_are_exact_equivalence():
    cert = analyze_linear_semantic_morphism(np.eye(3), np.eye(3))
    assert cert.kind is SemanticMorphismKind.EXACT_EQUIVALENCE
    assert cert.source_kernel_dim == 0
    assert cert.target_kernel_dim == 0
    assert cert.images_equal


def test_joint_to_eef_is_projection_when_fk_jacobian_has_nullspace():
    # Local 7-DoF joint semantics mapped to a 6-DoF task observable.
    J = np.concatenate([np.eye(6), np.ones((6, 1)) * 0.1], axis=1)
    cert = analyze_linear_semantic_morphism(J, np.eye(6))
    assert cert.kind is SemanticMorphismKind.SOURCE_PROJECTION
    assert cert.source_rank == 6
    assert cert.source_kernel_dim == 1
    assert cert.target_kernel_dim == 0


def test_eef_to_joint_has_target_ambiguity_under_redundant_kinematics():
    J = np.concatenate([np.eye(6), np.ones((6, 1)) * 0.1], axis=1)
    cert = analyze_linear_semantic_morphism(np.eye(6), J)
    assert cert.kind is SemanticMorphismKind.TARGET_AMBIGUITY
    assert cert.source_kernel_dim == 0
    assert cert.target_kernel_dim == 1


def test_singular_joint_target_cannot_represent_arbitrary_eef_motion():
    J = np.diag([1.0, 1.0, 1.0, 1.0, 1.0, 0.0])
    cert = analyze_linear_semantic_morphism(np.eye(6), J)
    assert cert.kind is SemanticMorphismKind.LOCALLY_UNREPRESENTABLE
    assert cert.source_image_in_target_residual > 0.0


def test_projection_and_ambiguity_can_coexist():
    # Both semantic spaces contain invisible directions relative to one shared
    # scalar observable.
    A = np.array([[1.0, 0.0]])
    B = np.array([[1.0, 1.0, 0.0]])
    cert = analyze_linear_semantic_morphism(A, B)
    assert cert.kind is SemanticMorphismKind.PROJECTION_AND_AMBIGUITY
    assert cert.source_kernel_dim == 1
    assert cert.target_kernel_dim == 2


def test_faithful_embedding_is_not_bidirectional_equivalence():
    A = np.array([[1.0], [0.0]])
    B = np.eye(2)
    cert = analyze_linear_semantic_morphism(A, B)
    assert cert.kind is SemanticMorphismKind.FAITHFUL_EMBEDDING
    assert not cert.images_equal


def test_transport_reports_minimum_norm_target_and_exact_shared_observable():
    J = np.concatenate([np.eye(6), np.ones((6, 1)) * 0.1], axis=1)
    source_eef = np.array([0.2, -0.1, 0.3, 0.01, -0.02, 0.04])
    result = transport_shared_observable(source_eef, np.eye(6), J)
    assert result.exact
    np.testing.assert_allclose(
        result.reconstructed_observable,
        source_eef,
        atol=1e-10,
    )
    assert result.target_semantic.shape == (7,)


def test_random_full_row_rank_joint_to_eef_is_consistently_projection():
    rng = np.random.default_rng(20261006)
    for _ in range(300):
        J = rng.normal(size=(6, 7))
        while np.linalg.matrix_rank(J) < 6:
            J = rng.normal(size=(6, 7))
        cert = analyze_linear_semantic_morphism(J, np.eye(6))
        assert cert.kind is SemanticMorphismKind.SOURCE_PROJECTION
        assert cert.source_kernel_dim == 1
