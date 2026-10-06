from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Iterable


class Decision(str, Enum):
    PASS = "PASS"
    TRANSPORT = "TRANSPORT"
    REPAIR = "REPAIR"
    REJECT = "REJECT"


class ContractClass(str, Enum):
    DIRECT = "DIRECT"
    COMMON_EQUIVARIANT = "COMMON_EQUIVARIANT"
    RELATIONAL_INVARIANT = "RELATIONAL_INVARIANT"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Evidence:
    semantics_known: bool
    provenance_valid: bool
    representability_margin: float
    canonical_command_error: float
    exact_transport_available: bool
    support_stability: float
    held_out_residual: float
    transverse_norm: float
    certified_repair_radius: float
    contract_class: ContractClass
    support_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Thresholds:
    pass_error: float = 1e-6
    min_support_stability: float = 0.9
    max_held_out_residual: float = 0.05


@dataclass(frozen=True)
class Certificate:
    decision: Decision
    contract_class: ContractClass
    support_ids: tuple[str, ...]
    support_stability: float
    held_out_residual: float
    representability_margin: float
    canonical_command_error: float
    transverse_norm: float
    certified_repair_radius: float
    provenance_digest: str
    reason: str


def provenance_digest(parts: Iterable[str]) -> str:
    canonical = "\n".join(parts).encode("utf-8")
    return sha256(canonical).hexdigest()


def compile_contract(
    evidence: Evidence,
    *,
    provenance_parts: Iterable[str],
    thresholds: Thresholds = Thresholds(),
) -> Certificate:
    digest = provenance_digest(provenance_parts)

    def cert(decision: Decision, reason: str) -> Certificate:
        return Certificate(
            decision=decision,
            contract_class=evidence.contract_class,
            support_ids=evidence.support_ids,
            support_stability=evidence.support_stability,
            held_out_residual=evidence.held_out_residual,
            representability_margin=evidence.representability_margin,
            canonical_command_error=evidence.canonical_command_error,
            transverse_norm=evidence.transverse_norm,
            certified_repair_radius=evidence.certified_repair_radius,
            provenance_digest=digest,
            reason=reason,
        )

    if not evidence.semantics_known:
        return cert(Decision.REJECT, "action semantics are unresolved")
    if not evidence.provenance_valid:
        return cert(Decision.REJECT, "runtime provenance is invalid")
    if evidence.representability_margin < 0:
        return cert(Decision.REJECT, "target controller cannot represent the requested physical command")

    if evidence.canonical_command_error <= thresholds.pass_error:
        return cert(Decision.PASS, "canonical physical command is already valid")

    if evidence.exact_transport_available:
        return cert(Decision.TRANSPORT, "an exact semantics-preserving transport is available")

    if evidence.contract_class is ContractClass.UNKNOWN:
        return cert(Decision.REJECT, "local physical contract class is unresolved")
    if evidence.support_stability < thresholds.min_support_stability:
        return cert(Decision.REJECT, "physical support identity is unstable")
    if evidence.held_out_residual > thresholds.max_held_out_residual:
        return cert(Decision.REJECT, "held-out intervention residual exceeds the repair gate")
    if evidence.certified_repair_radius <= 0:
        return cert(Decision.REJECT, "no positive certified repair radius is available")
    if evidence.transverse_norm > evidence.certified_repair_radius:
        return cert(Decision.REJECT, "requested correction lies outside the certified repair region")

    return cert(Decision.REPAIR, "bounded semantics-aware repair is admissible")


def verify_certificate(
    certificate: Certificate,
    evidence: Evidence,
    *,
    provenance_parts: Iterable[str],
    thresholds: Thresholds = Thresholds(),
) -> bool:
    expected = compile_contract(
        evidence,
        provenance_parts=provenance_parts,
        thresholds=thresholds,
    )
    return certificate == expected


def contract_agreement(classes: Iterable[ContractClass]) -> bool:
    classes = tuple(classes)
    if not classes:
        return False
    if any(c is ContractClass.UNKNOWN for c in classes):
        return False
    return len(set(classes)) == 1
