import json

import pytest

from research.eprc.external_replication_gate import (
    canonical_digest,
    validate_external_replication,
)


def _record():
    d = {
        "producer": "independent-lab",
        "independent": True,
        "real_frozen_policy": True,
        "source_repo": "https://github.com/example/robot-policy",
        "source_commit": "0123456789abcdef0123456789abcdef01234567",
        "policy_family": "DiffusionPolicy",
        "checkpoint": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "task": "PushT-v0",
        "controller_representation": "absolute_xy",
        "protocol_id": "crg-replication-v1-2026-10-06",
        "request_count": 20,
        "decision_counts": {
            "CERTIFIED_REPAIR": 8,
            "CERTIFIED_IMPOSSIBLE": 7,
            "INCONCLUSIVE": 5,
        },
        "policy_query_count_total": 120,
        "fixed_budget_reference_query_count_total": 200,
        "false_accept_count": 1,
        "false_reject_count": 1,
        "execution_evidence": {
            "observed_requests": 15,
            "artifact": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        },
        "support_stability": 0.94,
        "held_out_residual": 0.04,
    }
    d["evidence_digest"] = canonical_digest(d)
    return d


def test_result_bearing_independent_record_triggers_external_evidence_gate(tmp_path):
    d = _record()
    p = tmp_path / "record.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    audit = validate_external_replication(p)
    assert audit.eligible_external_evidence
    assert audit.request_count == 20
    assert audit.terminal_certificate_count == 15
    assert audit.query_reduction_fraction == pytest.approx(0.4)


def test_negative_result_is_still_valid_external_evidence(tmp_path):
    d = _record()
    d["false_accept_count"] = d["decision_counts"]["CERTIFIED_REPAIR"]
    d["false_reject_count"] = d["decision_counts"]["CERTIFIED_IMPOSSIBLE"]
    d["evidence_digest"] = canonical_digest(d)
    p = tmp_path / "negative.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    audit = validate_external_replication(p)
    assert audit.eligible_external_evidence


def test_self_authored_record_cannot_trigger_external_gate(tmp_path):
    d = _record()
    d["producer"] = "lindicaphxag-tech"
    d["evidence_digest"] = canonical_digest(d)
    p = tmp_path / "self.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="self-authored"):
        validate_external_replication(p)


def test_synthetic_only_record_cannot_trigger_external_gate(tmp_path):
    d = _record()
    d["real_frozen_policy"] = False
    d["evidence_digest"] = canonical_digest(d)
    p = tmp_path / "synthetic.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="synthetic-only"):
        validate_external_replication(p)


def test_mutation_after_sealing_is_rejected(tmp_path):
    d = _record()
    d["policy_query_count_total"] = 1
    p = tmp_path / "tampered.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        validate_external_replication(p)
