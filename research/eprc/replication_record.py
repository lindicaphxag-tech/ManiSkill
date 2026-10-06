from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from pathlib import Path


ALLOWED_DECISIONS = {"PASS", "TRANSPORT", "REPAIR", "REJECT"}
ALLOWED_OUTCOMES = {"success", "failure", "not_executed"}


@dataclass(frozen=True)
class ReplicationAudit:
    producer: str
    evidence_digest: str
    decision: str
    execution_outcome: str
    independent: bool


def canonical_evidence_digest(data: dict) -> str:
    payload = dict(data)
    payload.pop("evidence_digest", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def validate_replication_record(path: str | Path) -> ReplicationAudit:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "producer",
        "independent",
        "source_repo",
        "source_commit",
        "policy_family",
        "checkpoint",
        "controller_representation",
        "intervention_protocol",
        "support_stability",
        "held_out_residual",
        "representability_margin",
        "decision",
        "execution_outcome",
        "evidence_digest",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"missing replication fields: {missing}")

    producer = str(data["producer"]).strip()
    if not producer:
        raise ValueError("producer must be non-empty")
    independent = bool(data["independent"])
    if not independent:
        raise ValueError("replication record must explicitly attest independence")
    if producer.lower() in {"lindicaphxag-tech", "fhby"}:
        raise ValueError("self-authored evidence is not an independent replication")

    if not str(data["source_repo"]).strip() or not str(data["source_commit"]).strip():
        raise ValueError("source repository and immutable commit are required")
    if not str(data["policy_family"]).strip() or not str(data["checkpoint"]).strip():
        raise ValueError("policy family and immutable checkpoint are required")
    if not str(data["controller_representation"]).strip():
        raise ValueError("controller representation is required")
    if not str(data["intervention_protocol"]).strip():
        raise ValueError("intervention protocol is required")

    stability = float(data["support_stability"])
    residual = float(data["held_out_residual"])
    margin = float(data["representability_margin"])
    if not 0.0 <= stability <= 1.0:
        raise ValueError("support_stability must lie in [0, 1]")
    if residual < 0.0:
        raise ValueError("held_out_residual must be non-negative")
    if not isfinite(margin):
        raise ValueError("representability_margin must be finite")

    decision = str(data["decision"])
    outcome = str(data["execution_outcome"])
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"invalid decision: {decision}")
    if outcome not in ALLOWED_OUTCOMES:
        raise ValueError(f"invalid execution_outcome: {outcome}")

    expected = canonical_evidence_digest(data)
    if str(data["evidence_digest"]) != expected:
        raise ValueError("replication evidence digest mismatch")

    return ReplicationAudit(
        producer=producer,
        evidence_digest=expected,
        decision=decision,
        execution_outcome=outcome,
        independent=True,
    )
