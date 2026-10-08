import copy

import numpy as np
import pytest

from research.eprc.real_policy.aggregate_cross_policy_prospective_bank import (
    FROZEN_GATE,
    FROZEN_PAIR_COUNT,
    FROZEN_SEEDS,
    FROZEN_LEROBOT_COMMIT,
    FROZEN_RESTORE_AMENDMENT,
    FROZEN_REVISIONS,
    FROZEN_HELDOUTS,
    validate_frozen_state_provenance,
)


def test_cross_policy_bank_constants_match_frozen_manifest():
    assert FROZEN_SEEDS == (17, 29, 43, 59, 71, 89, 101, 131, 151, 181)
    assert FROZEN_PAIR_COUNT == 20
    assert FROZEN_GATE.min_pairs == 20
    assert np.isclose(FROZEN_GATE.min_dec_spearman, 0.50)
    assert np.isclose(FROZEN_GATE.required_spearman_margin, 0.10)



def _frozen_state(seed=29):
    return {
        "schema": "eprc-cross-policy-state-v1",
        "reset_seed": seed,
        "state_restore_protocol": FROZEN_RESTORE_AMENDMENT,
        "lerobot_commit": FROZEN_LEROBOT_COMMIT,
        "probe_epsilon": 0.125,
        "physical_probe": [2.0, 2.0, 0.01],
        "randomness_seeds": [123, 456, 789],
        "heldouts": copy.deepcopy(FROZEN_HELDOUTS),
        "policies": {
            name: {"model_id": model_id, "revision": revision, "replicate_count": 3}
            for name, (model_id, revision) in FROZEN_REVISIONS.items()
        },
        "pairs": [
            {"pair_id": f"seed-{seed}-{h}", "reset_seed": seed,
             "heldout_id": h, "a": {}, "b": {}}
            for h in ("A", "B")
        ],
    }


def test_bank_accepts_uniform_amended_restore_version():
    validate_frozen_state_provenance(_frozen_state(), 29)


@pytest.mark.parametrize("changed_field", [
    "state_restore_protocol", "lerobot_commit", "probe_epsilon",
    "physical_probe", "randomness_seeds", "heldouts",
])
def test_bank_rejects_mixed_provenance(changed_field):
    data = _frozen_state()
    data[changed_field] = "reset-fresh-space-exact-readback-v1"
    with pytest.raises(RuntimeError, match="drift"):
        validate_frozen_state_provenance(data, 29)


def test_bank_rejects_wrong_checkpoint_identity():
    data = _frozen_state()
    data["policies"]["vqbet"]["revision"] = "latest"
    with pytest.raises(RuntimeError, match="checkpoint identity"):
        validate_frozen_state_provenance(data, 29)


def test_bank_rejects_seed_and_pair_swap():
    data = _frozen_state(29)
    with pytest.raises(RuntimeError, match="reset_seed drift"):
        validate_frozen_state_provenance(data, 43)
    data["pairs"][0]["heldout_id"] = "B"
    with pytest.raises(RuntimeError, match="pair identity"):
        validate_frozen_state_provenance(data, 29)
