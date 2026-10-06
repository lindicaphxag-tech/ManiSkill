import json
from pathlib import Path

import numpy as np

from research.eprc.run_minimal_admissibility_replication import (
    central_map,
    directional_locality_payload,
)


def test_central_map_recovers_linear_canonical_response():
    g = np.array([[1.0, 0.2], [-0.4, 2.0]])

    def query(delta, seed):
        del seed
        return g @ delta

    out = central_map(query, support_dim=2, radius=0.25, seed=7)
    assert np.allclose(out, g)


def test_paired_randomness_cancels_seed_specific_offset():
    g = np.array([[1.0, -0.3]])

    def query(delta, seed):
        return g @ delta + np.array([float(seed)])

    a = central_map(query, support_dim=2, radius=0.5, seed=11)
    b = central_map(query, support_dim=2, radius=0.5, seed=29)
    assert np.allclose(a, g)
    assert np.allclose(b, g)


def test_directional_payload_preserves_stable_axes_when_global_map_is_mixed():
    coarse = np.array([[1.4, 0.0], [0.0, 1.0]])
    fine_center = np.array([[1.2, 0.0], [0.0, 1.3]])
    finer_center = np.array([[1.1, 0.0], [0.0, 1.8]])

    fine = np.stack([fine_center, fine_center, fine_center, fine_center, fine_center])
    finer = np.stack(
        [finer_center, finer_center, finer_center, finer_center, finer_center]
    )

    out = directional_locality_payload(
        coarse=coarse,
        fine_replicates=fine,
        finer_replicates=finer,
        fine_radius=0.25,
        finer_radius=0.125,
        contraction_threshold=0.75,
    )

    assert out["stable_direction"] == [True, False]
    assert np.allclose(out["directional_radii"], [0.125, 0.0])
    assert np.allclose(out["contraction_ratio"], [0.5, 5.0 / 3.0])
    assert np.allclose(out["finer_stochastic_radius_per_direction"], [0.0, 0.0])


def test_directional_payload_uses_json_null_for_nonfinite_ratio():
    coarse = np.array([[1.0]])
    fine = np.ones((5, 1, 1))
    finer = 2.0 * np.ones((5, 1, 1))

    out = directional_locality_payload(
        coarse=coarse,
        fine_replicates=fine,
        finer_replicates=finer,
        fine_radius=0.25,
        finer_radius=0.125,
        contraction_threshold=0.75,
    )

    assert out["contraction_ratio"] == [None]
    assert out["stable_direction"] == [False]
    assert out["directional_radii"] == [0.0]
