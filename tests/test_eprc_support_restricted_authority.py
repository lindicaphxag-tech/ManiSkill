import numpy as np

from research.eprc.support_restricted_authority import (
    global_full_rank_required,
    support_restricted_authority,
)


def test_global_rank_loss_can_be_irrelevant_to_current_support_contract():
    # Target controller cannot move physical z, so it is globally rank deficient.
    target_lift = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.0, 0.0],
        ]
    )
    assert not global_full_rank_required(target_lift)

    # Current support perturbations require only x/y physical responses.
    j_phys = np.array(
        [
            [1.0, 0.2],
            [0.3, 0.7],
            [0.0, 0.0],
        ]
    )
    result = support_restricted_authority(j_phys, target_lift)

    assert result.certificate.target_authority_rank == 2
    assert result.certificate.source_response_rank == 2
    assert result.certificate.exact_on_support
    assert result.certificate.relative_projection_residual < 1e-10
    assert np.allclose(result.reconstructed_physical_jacobian, j_phys)


def test_lost_task_relevant_direction_rejects_exact_transport():
    target_lift = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.0, 0.0],
        ]
    )
    # The support response now requires physical z authority.
    j_phys = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.0, 0.4],
        ]
    )
    result = support_restricted_authority(j_phys, target_lift)

    assert not result.certificate.exact_on_support
    assert result.certificate.relative_projection_residual > 0.1


def test_redundant_controller_uses_minimum_norm_transport():
    # Three target action coordinates command a two-dimensional physical space.
    target_lift = np.array(
        [
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
        ]
    )
    j_phys = np.array(
        [
            [1.0, 0.2],
            [0.3, 0.8],
        ]
    )
    result = support_restricted_authority(j_phys, target_lift)

    assert result.certificate.exact_on_support
    assert np.allclose(target_lift @ result.target_action_support_jacobian, j_phys)

    # Pseudoinverse returns the minimum-Frobenius-norm exact response.
    null = np.array([[1.0], [1.0], [-1.0]])
    assert np.allclose(target_lift @ null, 0.0)
    alternative = result.target_action_support_jacobian + null @ np.ones((1, 2))
    assert np.linalg.norm(result.target_action_support_jacobian) <= np.linalg.norm(alternative)


def test_zero_response_is_trivially_representable_even_with_zero_authority():
    target_lift = np.zeros((3, 2))
    j_phys = np.zeros((3, 4))
    result = support_restricted_authority(j_phys, target_lift)

    assert result.certificate.exact_on_support
    assert result.certificate.source_response_rank == 0
    assert result.certificate.target_authority_rank == 0
