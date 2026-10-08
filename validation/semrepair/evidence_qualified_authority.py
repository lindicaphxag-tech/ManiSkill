#!/usr/bin/env python3
"""Evidence-qualified, context-bound repair authority.

This module intentionally does not accept caller-supplied verdict booleans.
Authority is derived from certificate payloads whose canonical digests are
recomputed and whose case/context identities must agree.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Mapping

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class EvidenceBundle:
    case_id: str
    context_digest: str
    effect_policy_id: str
    measurement_certificate: Mapping[str, Any]
    repair_certificate: Mapping[str, Any] | None = None
    interaction_certificate: Mapping[str, Any] | None = None
    execution_certificate: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class PreDispatchDecision:
    authorized: bool
    stage: str
    reasons: tuple[str, ...]
    case_id: str
    context_digest: str
    evidence_digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CommitDecision:
    state: str
    reasons: tuple[str, ...]
    predispatch_digest: str
    post_effect_certificate_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty")
    return value


def _digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def certificate_digest(payload: Mapping[str, Any]) -> str:
    """Canonical digest excluding the self-hash field itself."""
    canonical = dict(payload)
    canonical.pop("certificate_sha256", None)
    return _digest(canonical)


def seal_certificate(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Utility for tests/evidence generation; sealing is integrity, not trust."""
    out = dict(payload)
    out["certificate_sha256"] = certificate_digest(out)
    return out


def _verify_certificate(
    payload: Mapping[str, Any],
    *,
    expected_type: str,
    case_id: str,
    context_digest: str,
) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ValueError(f"{expected_type} certificate must be a mapping")
    cert = dict(payload)
    cert_id = _nonempty(str(cert.get("certificate_sha256", "")), "certificate_sha256")
    if not _HEX64.fullmatch(cert_id):
        raise ValueError(f"{expected_type} certificate_sha256 must be lowercase hex sha256")
    actual = certificate_digest(cert)
    if actual != cert_id:
        raise ValueError(
            f"{expected_type} certificate digest mismatch: expected {cert_id}, got {actual}"
        )
    if cert.get("certificate_type") != expected_type:
        raise ValueError(
            f"expected certificate_type={expected_type!r}, got {cert.get('certificate_type')!r}"
        )
    if cert.get("case_id") != case_id:
        raise ValueError(f"{expected_type} certificate case_id mismatch")
    if cert.get("context_digest") != context_digest:
        raise ValueError(f"{expected_type} certificate context_digest mismatch")
    issuer = cert.get("issuer_id")
    _nonempty(str(issuer or ""), f"{expected_type}.issuer_id")
    return cert


def _bundle_digest(bundle: EvidenceBundle) -> str:
    payload = {
        "case_id": bundle.case_id,
        "context_digest": bundle.context_digest,
        "effect_policy_id": bundle.effect_policy_id,
        "measurement_certificate_sha256": bundle.measurement_certificate.get(
            "certificate_sha256"
        ),
        "repair_certificate_sha256": (
            bundle.repair_certificate or {}
        ).get("certificate_sha256"),
        "interaction_certificate_sha256": (
            bundle.interaction_certificate or {}
        ).get("certificate_sha256"),
        "execution_certificate_sha256": (
            bundle.execution_certificate or {}
        ).get("certificate_sha256"),
    }
    return _digest(payload)


def authorize_pre_dispatch(bundle: EvidenceBundle) -> PreDispatchDecision:
    case_id = _nonempty(bundle.case_id, "case_id")
    context = _nonempty(bundle.context_digest, "context_digest")
    if not _HEX64.fullmatch(context):
        raise ValueError("context_digest must be lowercase hex sha256")
    _nonempty(bundle.effect_policy_id, "effect_policy_id")

    measurement = _verify_certificate(
        bundle.measurement_certificate,
        expected_type="measurement",
        case_id=case_id,
        context_digest=context,
    )
    evidence_digest = _bundle_digest(bundle)

    if not (
        measurement.get("measurement_qualified") is True
        and measurement.get("decision") == "measurement_qualified"
    ):
        return PreDispatchDecision(
            False,
            "measurement_qualification",
            (
                "measurement certificate does not establish a qualified, "
                "identifying and repeatable evidence channel",
            ),
            case_id,
            context,
            evidence_digest,
        )

    if bundle.repair_certificate is None:
        return PreDispatchDecision(
            False,
            "local_repair_verification",
            ("verified repair certificate is missing",),
            case_id,
            context,
            evidence_digest,
        )
    repair = _verify_certificate(
        bundle.repair_certificate,
        expected_type="repair",
        case_id=case_id,
        context_digest=context,
    )
    if repair.get("status") != "verified":
        return PreDispatchDecision(
            False,
            "local_repair_verification",
            ("repair certificate status is not verified",),
            case_id,
            context,
            evidence_digest,
        )

    if bundle.interaction_certificate is None:
        return PreDispatchDecision(
            False,
            "repair_interaction",
            ("interaction authorization certificate is missing",),
            case_id,
            context,
            evidence_digest,
        )
    interaction = _verify_certificate(
        bundle.interaction_certificate,
        expected_type="interaction",
        case_id=case_id,
        context_digest=context,
    )
    if interaction.get("authorized") is not True:
        return PreDispatchDecision(
            False,
            "repair_interaction",
            (
                "requested repair set is not authorized by the interaction "
                "certificate; a compensating bundle may require atomic activation",
            ),
            case_id,
            context,
            evidence_digest,
        )

    if bundle.execution_certificate is None:
        return PreDispatchDecision(
            False,
            "execution_effect",
            ("execution non-regression certificate is missing",),
            case_id,
            context,
            evidence_digest,
        )
    execution = _verify_certificate(
        bundle.execution_certificate,
        expected_type="execution",
        case_id=case_id,
        context_digest=context,
    )
    if execution.get("non_regressive") is not True:
        return PreDispatchDecision(
            False,
            "execution_effect",
            (
                "semantic correctness is insufficient: bound execution evidence "
                "does not establish non-regression",
            ),
            case_id,
            context,
            evidence_digest,
        )

    return PreDispatchDecision(
        True,
        "dispatch_authorized",
        (),
        case_id,
        context,
        evidence_digest,
    )


def decide_commit(
    decision: PreDispatchDecision,
    *,
    post_effect_certificate: Mapping[str, Any] | None,
) -> CommitDecision:
    if not decision.authorized:
        return CommitDecision(
            "aborted",
            ("pre-dispatch authority was denied",),
            decision.evidence_digest,
            None,
        )
    if post_effect_certificate is None:
        return CommitDecision(
            "ambiguous",
            ("post-effect evidence is missing",),
            decision.evidence_digest,
            None,
        )

    cert = _verify_certificate(
        post_effect_certificate,
        expected_type="post_effect",
        case_id=decision.case_id,
        context_digest=decision.context_digest,
    )
    cert_id = str(cert["certificate_sha256"])
    observed = cert.get("effect_observed")
    if observed is None:
        return CommitDecision(
            "ambiguous",
            ("post-effect certificate is inconclusive",),
            decision.evidence_digest,
            cert_id,
        )
    if observed is not True:
        return CommitDecision(
            "aborted",
            ("post-effect certificate contradicts the authorized effect",),
            decision.evidence_digest,
            cert_id,
        )
    return CommitDecision(
        "committed",
        (),
        decision.evidence_digest,
        cert_id,
    )


def from_mapping(payload: Mapping[str, Any]) -> EvidenceBundle:
    legacy_fields = {
        "measurement_qualified",
        "repair_verified",
        "interaction_authorized",
        "execution_non_regressive",
    }
    present = sorted(legacy_fields & set(payload))
    if present:
        raise ValueError(
            "caller-supplied verdict booleans are not authority; "
            f"replace legacy fields with certificate payloads: {present}"
        )
    return EvidenceBundle(
        case_id=str(payload["case_id"]),
        context_digest=str(payload["context_digest"]),
        effect_policy_id=str(payload["effect_policy_id"]),
        measurement_certificate=payload["measurement_certificate"],
        repair_certificate=payload.get("repair_certificate"),
        interaction_certificate=payload.get("interaction_certificate"),
        execution_certificate=payload.get("execution_certificate"),
    )
