import numpy as np

from research.eprc.real_policy.aggregate_cross_policy_prospective_bank import (
    FROZEN_GATE,
    FROZEN_PAIR_COUNT,
    FROZEN_SEEDS,
)


def test_cross_policy_bank_constants_match_frozen_manifest():
    assert FROZEN_SEEDS == (17, 29, 43, 59, 71, 89, 101, 131, 151, 181)
    assert FROZEN_PAIR_COUNT == 20
    assert FROZEN_GATE.min_pairs == 20
    assert np.isclose(FROZEN_GATE.min_dec_spearman, 0.50)
    assert np.isclose(FROZEN_GATE.required_spearman_margin, 0.10)
