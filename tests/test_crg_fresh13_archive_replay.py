"""Prospective evidence-integrity regressions: original values must not move."""
import json
import shutil

import pytest

from research.crg_core.evidence.conformal_fresh_13state_v1.replay_archive import (
    HERE, replay_archive,
)


def _copy_archive(tmp_path):
    for path in HERE.iterdir():
        if path.is_file() and (path.suffix in (".json", ".py")):
            shutil.copy2(path, tmp_path / path.name)
    return tmp_path


def test_exact_original_pilot_replay_and_corrected_transfer_authorization():
    out = replay_archive()
    assert out["original_source_replayed"]
    assert out["every_non_digest_original_field_numerically_checked"]
    assert out["original_calibration_digest_preserved"] == "0af1b474c7a2c457c2b9496cc46e74b7294e15673b5134ecca1aa1715162437e"
    assert len(out["recomputed_calibration_digest"]) == 64
    assert isinstance(out["calibration_digest_byte_exact"], bool)
    assert out["research_verdict"] == "ZERO_UTILITY_NO_TRANSFER"
    assert out["n_calibration_state_clusters"] == 9
    assert out["n_test_state_clusters"] == 4
    assert out["n_dependent_test_requests"] == 8
    assert out["policy_query_count"] == 702
    assert out["stability_counts"]["diffusion_stable_test"] == 0
    assert out["stability_counts"]["vqbet_stable_test"] == 3
    assert out["stability_counts"]["both_stable_test"] == 0
    assert out["uncertainty_radius_exceeds_tolerance"]
    assert out["similar_transfer_cannot_be_authorized_even_without_validity_gate"]
    assert out["corrected_transfer_accounting"]["statistics"]["transfer_authorized_count"] == 0
    assert out["corrected_transfer_accounting"]["statistics"]["invalid_model_rejections"] == 8
    assert out["corrected_transfer_accounting"]["utility_outcome"] == "ZERO_UTILITY_NO_TRANSFER"
    assert out["not_an_independent_external_replication"]


def test_missing_state_cannot_be_silently_dropped(tmp_path):
    root = _copy_archive(tmp_path)
    (root / "state-271.json").unlink()
    with pytest.raises(ValueError, match="frozen intended state missing"):
        replay_archive(root)


def test_tampered_raw_test_outcome_is_rejected(tmp_path):
    root = _copy_archive(tmp_path)
    f = root / "state-263.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    d["pairs"][0]["a"]["heldout_physical_response"][0] += 1.0
    f.write_text(json.dumps(d))
    with pytest.raises(AssertionError, match="original_aggregate"):
        replay_archive(root)


def test_changed_frozen_application_tolerance_is_rejected(tmp_path):
    root = _copy_archive(tmp_path)
    f = root / "protocol_frozen.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    d["physical_response_tolerance_abs_xy"] = 3.0
    f.write_text(json.dumps(d))
    with pytest.raises(ValueError, match="protocol edited"):
        replay_archive(root)


def test_forged_original_aggregate_cannot_be_promoted(tmp_path):
    root = _copy_archive(tmp_path)
    f = root / "aggregate_original.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    d["authorized_requests"] = 8
    f.write_text(json.dumps(d))
    with pytest.raises(AssertionError, match="original_aggregate"):
        replay_archive(root)
