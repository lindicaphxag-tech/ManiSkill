import copy
import json
import subprocess
import sys

import numpy as np
import pytest

from research.crg_core.clustered_evidence_audit import audit_clustered_scores


def _groups(n=10):
    out = []
    for i in range(n):
        dec = (i + 1) / (n + 1)
        pairs = []
        for heldout_id, offset in (("A", -0.02), ("B", 0.03)):
            pairs.append({
                "heldout_id": heldout_id,
                "dec_distance": dec,
                "raw_distance": (i * 7) % n / n,
                "support_distance": 1.0,
                "static_metadata_distance": 1.0,
                "coarse_class_distance": 0.0,
                "heldout_response_distance": dec + offset,
            })
        out.append({"state_id": i + 100, "pairs": pairs})
    return out


def test_audit_counts_ten_independent_states_not_twenty_independent_samples():
    result = audit_clustered_scores(_groups(), bootstrap_replicates=128,
                                    permutation_replicates=128)
    assert result["n_restored_state_clusters"] == 10
    assert result["n_dependent_heldout_pairs"] == 20
    assert result["effective_independent_state_units"] == 10
    assert result["same_state_dec_is_shared"]
    assert result["observed_correlations"]["dec_distance"] > 0.95
    assert len(result["leave_one_state_out"]) == 10
    assert result["status"] == "POSTHOC_EXPLORATORY_NOT_PREREGISTERED"


def test_resampling_is_reproducible_with_fixed_seed():
    a = audit_clustered_scores(_groups(), bootstrap_replicates=128,
                               permutation_replicates=128)
    b = audit_clustered_scores(_groups(), bootstrap_replicates=128,
                               permutation_replicates=128)
    assert a == b


def test_pair_switch_and_within_state_predictor_drift_are_rejected():
    groups = _groups()
    groups[0]["pairs"] = groups[0]["pairs"][::-1]
    with pytest.raises(ValueError, match="A then B"):
        audit_clustered_scores(groups, bootstrap_replicates=128, permutation_replicates=128)
    groups = _groups()
    groups[0]["pairs"][1]["dec_distance"] += 0.01
    with pytest.raises(ValueError, match="different DEC"):
        audit_clustered_scores(groups, bootstrap_replicates=128, permutation_replicates=128)


def test_infinite_values_and_missing_states_fail_closed():
    groups = _groups()
    groups[2]["pairs"][0]["heldout_response_distance"] = np.inf
    with pytest.raises(ValueError, match="nonfinite"):
        audit_clustered_scores(groups, bootstrap_replicates=128, permutation_replicates=128)
    with pytest.raises(ValueError, match="three restored"):
        audit_clustered_scores(_groups(2), bootstrap_replicates=128, permutation_replicates=128)


def test_cli_outputs_exploratory_status(tmp_path):
    p = tmp_path / "pairs.json"
    p.write_text(json.dumps({"schema": "crg-paired-score-groups-v1", "groups": _groups()}))
    result = subprocess.run([
        sys.executable, "-m", "research.crg_core.clustered_evidence_audit",
        str(p),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["n_restored_state_clusters"] == 10
    assert payload["status"].startswith("POSTHOC_EXPLORATORY")
