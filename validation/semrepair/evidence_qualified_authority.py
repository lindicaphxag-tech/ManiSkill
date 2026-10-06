#!/usr/bin/env python3
"""Evidence-qualified repair authority."""

from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json
from typing import Any, Mapping

@dataclass(frozen=True)
class AuthorityInput:
    case: str
    measurement_certificate_id: str
    measurement_qualified: bool
    repair_certificate_id: str
    repair_verified: bool
    interaction_certificate_id: str
    interaction_authorized: bool
    execution_evidence_id: str
    execution_non_regressive: bool
    effect_policy_id: str

@dataclass(frozen=True)
class PreDispatchDecision:
    authorized: bool
    stage: str
    reasons: tuple[str, ...]
    input_digest: str
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class CommitDecision:
    state: str
    reasons: tuple[str, ...]
    predispatch_digest: str
    post_effect_evidence_id: str | None
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def _nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty")
    return value

def _digest(value: Mapping[str, Any]) -> str:
    encoded=json.dumps(dict(value),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

def authorize_pre_dispatch(request: AuthorityInput) -> PreDispatchDecision:
    for field in (
        "case","measurement_certificate_id","repair_certificate_id",
        "interaction_certificate_id","execution_evidence_id","effect_policy_id"
    ):
        _nonempty(getattr(request, field), field)
    digest=_digest(asdict(request))
    if not request.measurement_qualified:
        return PreDispatchDecision(False,"measurement_qualification",(
            "evidence channel is not qualified: repeatability without semantic identifiability cannot authorize a repair",
        ),digest)
    if not request.repair_verified:
        return PreDispatchDecision(False,"local_repair_verification",(
            "local repair certificate is not verified",
        ),digest)
    if not request.interaction_authorized:
        return PreDispatchDecision(False,"repair_interaction",(
            "requested repair is not authorized by the interaction certificate; a compensating bundle may require atomic activation",
        ),digest)
    if not request.execution_non_regressive:
        return PreDispatchDecision(False,"execution_effect",(
            "semantic correctness is insufficient: qualified execution evidence shows regression",
        ),digest)
    return PreDispatchDecision(True,"dispatch_authorized",(),digest)

def decide_commit(
    decision: PreDispatchDecision,
    *,
    post_effect_evidence_id: str | None,
    effect_observed: bool | None,
) -> CommitDecision:
    if not decision.authorized:
        return CommitDecision("aborted",("pre-dispatch authority was denied",),decision.input_digest,post_effect_evidence_id)
    if effect_observed is None:
        return CommitDecision("ambiguous",("post-effect evidence is missing or inconclusive",),decision.input_digest,post_effect_evidence_id)
    if not post_effect_evidence_id:
        return CommitDecision("ambiguous",("effect observation has no bound evidence identity",),decision.input_digest,None)
    if not effect_observed:
        return CommitDecision("aborted",("post-effect evidence contradicts the authorized effect",),decision.input_digest,post_effect_evidence_id)
    return CommitDecision("committed",(),decision.input_digest,post_effect_evidence_id)

def from_mapping(payload: Mapping[str, Any]) -> AuthorityInput:
    return AuthorityInput(
        case=str(payload["case"]),
        measurement_certificate_id=str(payload["measurement_certificate_id"]),
        measurement_qualified=bool(payload["measurement_qualified"]),
        repair_certificate_id=str(payload["repair_certificate_id"]),
        repair_verified=bool(payload["repair_verified"]),
        interaction_certificate_id=str(payload["interaction_certificate_id"]),
        interaction_authorized=bool(payload["interaction_authorized"]),
        execution_evidence_id=str(payload["execution_evidence_id"]),
        execution_non_regressive=bool(payload["execution_non_regressive"]),
        effect_policy_id=str(payload["effect_policy_id"]),
    )
