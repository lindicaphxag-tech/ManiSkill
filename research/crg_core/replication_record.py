from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path


DECISIONS = {"CERTIFIED_REPAIR", "CERTIFIED_IMPOSSIBLE", "INCONCLUSIVE"}
SELF_IDENTITIES = {"lindicaphxag-tech", "fhby"}


def canonical_digest(payload: dict) -> str:
    data = dict(payload)
    data.pop("evidence_digest", None)
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReplicationAudit:
    producer: str
    request_count: int
    terminal_count: int
    policy_query_count: int
    false_accept_count: int
    false_reject_count: int
    observed_execution_count: int
    schema_valid: bool
    claimed_independent: bool
    independence_verified: bool
    eligible_external_evidence: bool
    evidence_digest: str


def validate_replication_record(path: str | Path) -> ReplicationAudit:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "producer",
        "independent",
        "real_frozen_policy",
        "source_repo",
        "source_commit",
        "checkpoint",
        "policy_family",
        "task",
        "controller_representation",
        "protocol_id",
        "request_count",
        "decision_counts",
        "policy_query_count",
        "false_accept_count",
        "false_reject_count",
        "observed_execution_count",
        "evidence_digest",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"missing fields: {missing}")

    producer = str(data["producer"]).strip()
    if not producer:
        raise ValueError("producer must be non-empty")
    if producer.lower() in SELF_IDENTITIES:
        raise ValueError("self-authored record does not count as external evidence")
    if data["independent"] is not True:
        raise ValueError("independent must be true")
    if data["real_frozen_policy"] is not True:
        raise ValueError("synthetic-only record does not satisfy the external gate")

    for key in ("source_repo", "source_commit", "checkpoint", "policy_family", "task", "controller_representation", "protocol_id"):
        if not str(data[key]).strip():
            raise ValueError(f"{key} must be non-empty")
    if data["source_commit"] in {"main", "master", "HEAD", "latest"}:
        raise ValueError("source_commit must be immutable")

    request_count = int(data["request_count"])
    if request_count <= 0:
        raise ValueError("request_count must be positive")

    counts = data["decision_counts"]
    if set(counts) != DECISIONS:
        raise ValueError(f"decision_counts keys must be exactly {sorted(DECISIONS)}")
    counts = {k: int(v) for k, v in counts.items()}
    if any(v < 0 for v in counts.values()):
        raise ValueError("decision counts must be non-negative")
    if sum(counts.values()) != request_count:
        raise ValueError("decision counts must sum to request_count")

    queries = int(data["policy_query_count"])
    false_accept = int(data["false_accept_count"])
    false_reject = int(data["false_reject_count"])
    observed = int(data["observed_execution_count"])
    if min(queries, false_accept, false_reject, observed) < 0:
        raise ValueError("counts must be non-negative")
    if false_accept > counts["CERTIFIED_REPAIR"]:
        raise ValueError("false_accept_count exceeds CERTIFIED_REPAIR count")
    if false_reject > counts["CERTIFIED_IMPOSSIBLE"]:
        raise ValueError("false_reject_count exceeds CERTIFIED_IMPOSSIBLE count")
    if observed == 0 or observed > request_count:
        raise ValueError("observed_execution_count must be in [1, request_count]")

    digest = canonical_digest(data)
    if str(data["evidence_digest"]) != digest:
        raise ValueError("evidence digest mismatch")

    return ReplicationAudit(
        producer=producer,
        request_count=request_count,
        terminal_count=counts["CERTIFIED_REPAIR"] + counts["CERTIFIED_IMPOSSIBLE"],
        policy_query_count=queries,
        false_accept_count=false_accept,
        false_reject_count=false_reject,
        observed_execution_count=observed,
        # A self-declared producer name, independent=True, and a self-computed
        # SHA-256 digest are not independent attestation. The offline validator
        # checks internal consistency only; reviewer-side source provenance and
        # actual execution evidence must be verified separately.
        schema_valid=True,
        claimed_independent=True,
        independence_verified=False,
        eligible_external_evidence=False,
        evidence_digest=digest,
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    print(json.dumps(asdict(validate_replication_record(args.record)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
