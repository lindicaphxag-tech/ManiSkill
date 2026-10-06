import numpy as np

from research.eprc.effect_space_contract import (
    compile_effect_space_transport,
    effect_contract_distance,
    lift_to_effect_space,
)


def test_different_physical_command_dimensions_can_share_one_effect_contract():
    # Embodiment A exposes xyz-like physical commands; task effect keeps x/y.
    j_phys_a = np.array(
        [
            [1.0, 0.2],
            [0.1, 0.8],
            [0.4, 0.3],
        ]
    )
    e_a = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    # Embodiment B has four physical coordinates with different internal mixing.
    j_phys_b = np.array(
        [
            [1.0, 0.2],
            [0.1, 0.8],
            [2.0, -1.0],
            [0.5, 0.5],
        ]
    )
    e_b = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ]
    )

    assert j_phys_a.shape[0] != j_phys_b.shape[0]
    assert np.allclose(
        lift_to_effect_space(j_phys_a, e_a),
        lift_to_effect_space(j_phys_b, e_b),
    )
    assert effect_contract_distance(j_phys_a, e_a, j_phys_b, e_b) < 1e-10


def test_cross_embodiment_transport_can_succeed_despite_global_nullspaces():
    source_effect = np.array([[1.0, 0.2], [0.3, 0.9]])

    # Target has three action coordinates, four physical coordinates, but only
    # two task-effect coordinates matter. Several physical/action nullspaces are irrelevant.
    l_target = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 0.0],
        ]
    )
    e_target = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ]
    )

    result = compile_effect_space_transport(source_effect, l_target, e_target)
    assert result.exact_on_effect_subspace
    assert result.relative_effect_residual < 1e-10
    assert np.allclose(result.reconstructed_effect_jacobian, source_effect)


def test_missing_task_effect_direction_rejects_cross_embodiment_transport():
    source_effect = np.array([[1.0, 0.0], [0.0, 1.0]])
    l_target = np.array([[1.0], [0.0], [0.0]])
    e_target = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    result = compile_effect_space_transport(source_effect, l_target, e_target)
    assert not result.exact_on_effect_subspace
    assert result.relative_effect_residual > 0.5