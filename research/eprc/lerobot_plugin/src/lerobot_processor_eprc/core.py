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


@dataclass(frozen=True)
class Thresholds:
    pass_error: float = 1e-6
    min_support_stability: float = 0.9
    max_held_out_residual: float = 0.05


def provenance_digest(parts: Iterable[str]) -> str:
    return sha256("\n".join(parts).encode("utf-8")).hexdigest()


def compile_evidence(
    evidence: dict,
    *,
    provenance_parts: Iterable[str],
    thresholds: Thresholds,
) -> dict:
    def cert(decision: Decision, reason: str) -> dict:
        return {
            "decision": decision.value,
            "reason": reason,
            "provenance_digest": provenance_digest(provenance_parts),
            "contract_class": evidence.get("contract_class", "UNKNOWN"),
            "support_ids": list(evidence.get("support_ids", [])),
            "support_stability": float(evidence.get("support_stability", 0.0)),
            "held_out_residual": float(evidence.get("held_out_residual", float("inf"))),
            "representability_margin": float(
                evidence.get("representability_margin", float("-inf"))
            ),
            "canonical_command_error": float(
                evidence.get("canonical_command_error", float("inf"))
            ),
            "transverse_norm": float(evidence.get("transverse_norm", float("inf"))),
            "certified_repair_radius": float(
                evidence.get("certified_repair_radius", 0.0)
            ),
        }

    if not bool(evidence.get("semantics_known", False)):
        return cert(Decision.REJECT, "action semantics are unresolved")
    if not bool(evidence.get("provenance_valid", False)):
        return cert(Decision.REJECT, "runtime provenance is invalid")
    if float(evidence.get("representability_margin", float("-inf"))) < 0:
        return cert(
            Decision.REJECT,
            "target controller cannot represent the requested physical command",
        )
    if float(evidence.get("canonical_command_error", float("inf"))) <= thresholds.pass_error:
        return cert(Decision.PASS, "canonical physical command is already valid")
    if bool(evidence.get("exact_transport_available", False)):
        return cert(
            Decision.TRANSPORT,
            "an exact semantics-preserving transport is available",
        )
    if evidence.get("contract_class", "UNKNOWN") == "UNKNOWN":
        return cert(Decision.REJECT, "local physical contract class is unresolved")
    if float(evidence.get("support_stability", 0.0)) < thresholds.min_support_stability:
        return cert(Decision.REJECT, "physical support identity is unstable")
    if float(evidence.get("held_out_residual", float("inf"))) > thresholds.max_held_out_residual:
        return cert(
            Decision.REJECT,
            "held-out intervention residual exceeds the repair gate",
        )
    if float(evidence.get("certified_repair_radius", 0.0)) <= 0:
        return cert(Decision.REJECT, "no positive certified repair radius is available")
    if float(evidence.get("transverse_norm", float("inf"))) > float(
        evidence.get("certified_repair_radius", 0.0)
    ):
        return cert(
            Decision.REJECT,
            "requested correction lies outside the certified repair region",
        )

    return cert(Decision.REPAIR, "bounded semantics-aware repair is admissible")
