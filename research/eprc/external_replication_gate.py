from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path


SELF_IDENTITIES = {"lindicaphxag-tech", "fhby"}
DECISIONS = {"CERTIFIED_REPAIR", "CERTIFIED_IMPOSSIBLE", "INCONCLUSIVE"}


@dataclass(frozen=True)
class ExternalReplicationAudit:
    producer: str
    request_count: int
    terminal_certificate_count: int
    policy_query_count_total: int
    reference_query_count_total: int | None
    false_accept_count: int
    false_reject_count: int
    eligible_external_evidence: bool
    query_reduction_fraction: float | None
    evidence_digest: str


def canonical_digest(data: dict) -> str:
    payload = dict(data)
    payload.pop("evidence_digest", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def _immutable_identifier(value: object, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    mutable = {"main", "master", "latest", "head", "HEAD"}
    if text in mutable:
        raise ValueError(f"{name} must be immutable, not {text!r}")
    return text


def validate_external_replication(path: str | Path) -> ExternalReplicationAudit:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "producer",
        "independent",
        "real_frozen_policy",
        "source_repo",
        "source_commit",
        "policy_family",
        "checkpoint",
        "task",
        "controller_representation",
        "protocol_id",
        "request_count",
        "decision_counts",
        "policy_query_count_total",
        "false_accept_count",
        "false_reject_count",
        "execution_evidence",
        "evidence_digest",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"missing external replication fields: {missing}")

    producer = str(data["producer"]).strip()
    if not producer:
        raise ValueError("producer must be non-empty")
    if producer.lower() in SELF_IDENTITIES:
        raise ValueError("self-authored result cannot satisfy the external gate")
    if data["independent"] is not True:
        raise ValueError("independent must be explicitly true")
    if data["real_frozen_policy"] is not True:
        raise ValueError("synthetic-only evidence does not satisfy the external gate")

    _immutable_identifier(data["source_commit"], "source_commit")
    _immutable_identifier(data["checkpoint"], "checkpoint")
    _immutable_identifier(data["protocol_id"], "protocol_id")
    if not str(data["source_repo"]).strip():
        raise ValueError("source_repo must be non-empty")
    if not str(data["policy_family"]).strip():
        raise ValueError("policy_family must be non-empty")
    if not str(data["task"]).strip():
        raise ValueError("task must be non-empty")
    if not str(data["controller_representation"]).strip():
        raise ValueError("controller_representation must be non-empty")

    request_count = int(data["request_count"])
    if request_count <= 0:
        raise ValueError("request_count must be positive")

    counts = data["decision_counts"]
    if not isinstance(counts, dict) or set(counts) != DECISIONS:
        raise ValueError(f"decision_counts keys must be exactly {sorted(DECISIONS)}")
    counts = {k: int(v) for k, v in counts.items()}
    if any(v < 0 for v in counts.values()):
        raise ValueError("decision counts must be non-negative")
    if sum(counts.values()) != request_count:
        raise ValueError("decision_counts must sum to request_count")

    terminal = counts["CERTIFIED_REPAIR"] + counts["CERTIFIED_IMPOSSIBLE"]
    queries = int(data["policy_query_count_total"])
    if queries < 0:
        raise ValueError("policy_query_count_total must be non-negative")

    reference_queries = data.get("fixed_budget_reference_query_count_total")
    reduction = None
    if reference_queries is not None:
        reference_queries = int(reference_queries)
        if reference_queries <= 0:
            raise ValueError("fixed_budget_reference_query_count_total must be positive")
        reduction = 1.0 - queries / reference_queries

    false_accept = int(data["false_accept_count"])
    false_reject = int(data["false_reject_count"])
    if false_accept < 0 or false_reject < 0:
        raise ValueError("false accept/reject counts must be non-negative")
    if false_accept > counts["CERTIFIED_REPAIR"]:
        raise ValueError("false_accept_count exceeds CERTIFIED_REPAIR count")
    if false_reject > counts["CERTIFIED_IMPOSSIBLE"]:
        raise ValueError("false_reject_count exceeds CERTIFIED_IMPOSSIBLE count")

    execution = data["execution_evidence"]
    if not isinstance(execution, dict):
        raise ValueError("execution_evidence must be an object")
    observed = int(execution.get("observed_requests", -1))
    if observed < 0 or observed > request_count:
        raise ValueError("execution_evidence.observed_requests is invalid")
    if observed == 0:
        raise ValueError("result-bearing external evidence requires at least one execution outcome")

    for key in ("support_stability", "held_out_residual"):
        if key in data:
            value = float(data[key])
            if not isfinite(value) or value < 0:
                raise ValueError(f"{key} must be finite and non-negative")

    expected = canonical_digest(data)
    if str(data["evidence_digest"]) != expected:
        raise ValueError("external replication evidence digest mismatch")

    return ExternalReplicationAudit(
        producer=producer,
        request_count=request_count,
        terminal_certificate_count=terminal,
        policy_query_count_total=queries,
        reference_query_count_total=reference_queries,
        false_accept_count=false_accept,
        false_reject_count=false_reject,
        eligible_external_evidence=True,
        query_reduction_fraction=reduction,
        evidence_digest=expected,
    )
