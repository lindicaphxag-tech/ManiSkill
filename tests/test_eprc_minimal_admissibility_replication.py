import json
from pathlib import Path

import numpy as np

from research.eprc.run_minimal_admissibility_replication import central_map


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
