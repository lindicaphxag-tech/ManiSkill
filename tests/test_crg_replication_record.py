import json

import pytest

from research.crg_core.replication_record import canonical_digest, validate_replication_record


def _record():
    d = {
        "producer": "independent-lab",
        "independent": True,
        "real_frozen_policy": True,
        "source_repo": "https://github.com/example/robot-policy",
        "source_commit": "0123456789abcdef0123456789abcdef01234567",
        "checkpoint": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "policy_family": "DiffusionPolicy",
        "task": "PushT-v0",
        "controller_representation": "absolute_xy",
        "protocol_id": "crg-replication-v1",
        "request_count": 20,
        "decision_counts": {
            "CERTIFIED_REPAIR": 8,
            "CERTIFIED_IMPOSSIBLE": 7,
            "INCONCLUSIVE": 5,
        },
        "policy_query_count": 120,
        "false_accept_count": 1,
        "false_reject_count": 1,
        "observed_execution_count": 15,
    }
    d["evidence_digest"] = canonical_digest(d)
    return d


def test_self_declared_result_is_schema_valid_not_independently_verified(tmp_path):
    d = _record()
    p = tmp_path / "record.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    out = validate_replication_record(p)
    assert out.schema_valid
    assert out.claimed_independent
    assert not out.independence_verified
    assert not out.eligible_external_evidence
    assert out.terminal_count == 15


def test_negative_result_is_schema_valid_pending_audit(tmp_path):
    d = _record()
    d["false_accept_count"] = 8
    d["false_reject_count"] = 7
    d["evidence_digest"] = canonical_digest(d)
    p = tmp_path / "negative.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    out = validate_replication_record(p)
    assert out.schema_valid
    assert not out.eligible_external_evidence


def test_self_authored_record_is_rejected(tmp_path):
    d = _record()
    d["producer"] = "lindicaphxag-tech"
    d["evidence_digest"] = canonical_digest(d)
    p = tmp_path / "self.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="self-authored"):
        validate_replication_record(p)


def test_tampering_after_seal_is_rejected(tmp_path):
    d = _record()
    p = tmp_path / "tampered.json"
    d["evidence_digest"] = canonical_digest(d)
    d["policy_query_count"] = 1
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        validate_replication_record(p)


def test_renamed_producer_and_resealed_record_cannot_claim_independence(tmp_path):
    d = _record()
    d["producer"] = "unverified-third-party-name"
    d["policy_query_count"] = 999
    d["evidence_digest"] = canonical_digest(d)
    p = tmp_path / "self_resealed.json"
    p.write_text(json.dumps(d), encoding="utf-8")

    out = validate_replication_record(p)
    assert out.schema_valid
    assert not out.independence_verified
    assert not out.eligible_external_evidence
