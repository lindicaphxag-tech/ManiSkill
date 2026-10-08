import numpy as np

from research.eprc.effect_identification import estimate_effect_jacobian


def test_black_box_effect_identification_recovers_local_jacobian():
    base = np.array([0.3, -0.4, 0.2])
    a = np.array([[1.2, -0.3, 0.5], [0.1, 0.8, -0.7]])

    def effect(x):
        # Smooth nonlinear map with known local Jacobian A + diag-like cubic term.
        return a @ x + np.array([0.2 * x[0] ** 3, -0.1 * x[1] ** 3])

    expected = a.copy()
    expected[0, 0] += 0.6 * base[0] ** 2
    expected[1, 1] += -0.3 * base[1] ** 2

    probes = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, -1.0],
            [1.0, -1.0, 1.0],
        ]
    )
    held = np.array([[0.5, -1.0, 0.2], [-0.4, 0.3, 1.0]])

    estimate, cert = estimate_effect_jacobian(
        effect, base, probes, held, epsilon=1e-5, max_held_out_residual=1e-4
    )

    assert cert.locally_valid
    assert cert.held_out_residual < 1e-4
    assert np.allclose(estimate, expected, atol=1e-7)


def test_ill_conditioned_probe_design_is_rejected():
    def effect(x):
        return np.array([x[0] + 2 * x[1]])

    probes = np.array([[1.0, 0.0], [1.0, 1e-12], [2.0, 1e-12]])
    held = np.array([[0.0, 1.0]])
    _, cert = estimate_effect_jacobian(
        effect,
        np.zeros(2),
        probes,
        held,
        epsilon=1e-5,
        max_condition_number=1e6,
    )
    assert not cert.locally_valid
    assert cert.probe_condition_number > 1e6


def test_large_probe_region_can_fail_held_out_locality_gate():
    def effect(x):
        return np.array([np.sin(4.0 * x[0]) + x[1]])

    base = np.array([0.6, 0.0])
    probes = np.array([[1.0, 0.0], [0.0, 1.0]])
    held = np.array([[0.5, 1.0], [-0.3, 0.4]])

    # A very large epsilon asks one linearization to explain a visibly curved region.
    _, cert = estimate_effect_jacobian(
        effect,
        base,
        probes,
        held,
        epsilon=0.6,
        max_held_out_residual=0.01,
    )
    assert not cert.locally_valid
    assert cert.held_out_residual > 0.01


def test_underdetermined_probe_subspace_cannot_certify_full_effect_map():
    # Three action dimensions but probes only span the first two. Training and
    # held-out residual can both be exactly zero inside that subspace, yet the
    # third action direction is completely unidentified.
    def effect(x):
        return np.array([x[0] + 2.0 * x[1] + 7.0 * x[2]])

    probes = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    held = np.array([[1.0, 1.0, 0.0], [-0.5, 0.2, 0.0]])

    _, cert = estimate_effect_jacobian(
        effect,
        np.zeros(3),
        probes,
        held,
        epsilon=1e-5,
        max_held_out_residual=1e-8,
    )

    assert cert.training_residual < 1e-10
    assert cert.held_out_residual < 1e-10
    assert cert.probe_rank == 2
    assert not cert.full_action_rank
    assert not cert.locally_valid
