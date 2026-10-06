import json

import pytest

from research.eprc.replication_record import (
    canonical_evidence_digest,
    validate_replication_record,
)


def _record():
    data = {
        "producer": "independent-lab",
        "independent": True,
        "source_repo": "https://github.com/example/robot-policy",
        "source_commit": "0123456789abcdef",
        "policy_family": "DiffusionPolicy",
        "checkpoint": "sha256:abc",
        "controller_representation": "joint_delta_position",
        "intervention_protocol": "translate support A by +2 cm x, frozen seeds 1-5",
        "support_stability": 0.96,
        "held_out_residual": 0.03,
        "representability_margin": 0.14,
        "decision": "REPAIR",
        "execution_outcome": "success",
    }
    data["evidence_digest"] = canonical_evidence_digest(data)
    return data


def test_independent_record_is_digest_bound(tmp_path):
    data = _record()
    path = tmp_path / "record.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = validate_replication_record(path)
    assert result.independent
    assert result.producer == "independent-lab"


def test_tampering_after_digest_is_rejected(tmp_path):
    data = _record()
    data["held_out_residual"] = 0.9
    path = tmp_path / "record.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        validate_replication_record(path)


def test_self_authored_record_cannot_claim_independence(tmp_path):
    data = _record()
    data["producer"] = "lindicaphxag-tech"
    data["evidence_digest"] = canonical_evidence_digest(data)
    path = tmp_path / "record.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="self-authored"):
        validate_replication_record(path)
