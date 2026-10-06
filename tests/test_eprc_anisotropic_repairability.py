import numpy as np

from research.eprc.anisotropic_repairability import (
    anisotropic_map_uncertainty_bound,
    certify_anisotropic_authority,
    directional_locality_profile,
    synthesize_anisotropic_repair,
)


def test_directional_gate_keeps_only_contracting_support_axes():
    # x derivative converges; y derivative diverges as scale shrinks.
    coarse = np.array([[1.40, 0.0], [0.0, 1.00]])
    fine = np.array([[1.20, 0.0], [0.0, 1.30]])
    finer = np.array([[1.10, 0.0], [0.0, 1.80]])

    p = directional_locality_profile(
        coarse_map=coarse,
        fine_map=fine,
        finer_map=finer,
        fine_radius=0.25,
        finer_radius=0.125,
        contraction_threshold=0.75,
    )

    assert np.allclose(p.contraction_ratio, [0.5, 5.0 / 3.0])
    assert p.stable_direction.tolist() == [True, False]
    assert np.allclose(p.directional_radii, [0.125, 0.0])


def test_anisotropic_set_is_less_conservative_than_min_radius_ball():
    # First support direction is trusted much farther than the second.
    g = np.eye(2)
    target = np.array([0.45, 0.0])

    aniso = synthesize_anisotropic_repair(
        g,
        target,
        certified_radii=np.array([0.5, 0.1]),
        residual_tolerance=1e-10,
    )
    ball_like = synthesize_anisotropic_repair(
        g,
        target,
        certified_radii=np.array([0.1, 0.1]),
        residual_tolerance=1e-10,
    )

    assert aniso.repairable
    assert not ball_like.repairable
    assert aniso.residual_norm < ball_like.residual_norm


def test_controller_authority_scales_whole_locality_ellipsoid():
    a0 = np.array([0.9])
    j = np.array([[1.0, 1.0]])
    cert = certify_anisotropic_authority(
        a0,
        j,
        np.array([-1.0]),
        np.array([1.0]),
        np.array([0.4, 0.1]),
    )

    expected = 0.1 / np.sqrt(0.4**2 + 0.1**2)
    assert np.isclose(cert.authority_scale, expected)
    assert np.allclose(cert.certified_radii, expected * np.array([0.4, 0.1]))


def test_unstable_direction_is_fail_closed_not_silently_repaired():
    g = np.eye(2)
    out = synthesize_anisotropic_repair(
        g,
        np.array([0.0, 0.2]),
        certified_radii=np.array([0.5, 0.0]),
        residual_tolerance=0.01,
    )
    assert not out.repairable
    assert out.residual_norm > 0.19
    assert "failed the locality gate" in out.reason


def test_anisotropic_uncertainty_bound_tracks_directional_radius():
    eps = np.array([0.2, 1.0, 0.5])
    radii = np.array([0.5, 0.0, 0.1])
    bound = anisotropic_map_uncertainty_bound(eps, radii)
    assert np.isclose(bound, np.sqrt((0.2 * 0.5) ** 2 + (0.5 * 0.1) ** 2))
