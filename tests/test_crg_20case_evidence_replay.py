import copy
import json

import pytest

from research.crg_core.evidence.pusht_cross_policy_20case_v2.replay import (
    replay, ROOT
)


def test_full_negative_result_is_replayed_without_sample_exclusion():
    result = replay()
    assert result["archived_result_replayed_exactly"]
    assert result["original_primary_passed"] is False
    assert result["n_independent_state_clusters"] == 10
    assert result["n_dependent_heldout_observations"] == 20
    assert result["policy_queries"] == 540
    assert result["frozen_correlations"]["dec_spearman"] < 0.5
    assert result["frozen_correlations"]["dec_spearman"] < result["frozen_correlations"]["raw_spearman"]
    assert len(result["exploratory_cluster_sensitivity"]["leave_one_state_out"]) == 10


def test_any_missing_state_or_changed_frozen_gate_is_rejected(tmp_path):
    for p in ROOT.iterdir():
        if p.suffix == ".json":
            (tmp_path/p.name).write_bytes(p.read_bytes())
    (tmp_path/"state-131.json").unlink()
    with pytest.raises(FileNotFoundError):
        replay(tmp_path)
    (tmp_path/"state-131.json").write_bytes((ROOT/"state-131.json").read_bytes())
    result=json.loads((tmp_path/"primary_result.json").read_text())
    result["primary_gate"]["dec_spearman"]=0.9
    (tmp_path/"primary_result.json").write_text(json.dumps(result))
    with pytest.raises(AssertionError):
        replay(tmp_path)
