from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from runtime import ContractClass, Evidence, Thresholds, compile_contract, verify_certificate


def load_evidence(path: Path) -> tuple[Evidence, list[str], Thresholds]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    evidence_raw = payload["evidence"]
    evidence = Evidence(
        semantics_known=bool(evidence_raw["semantics_known"]),
        provenance_valid=bool(evidence_raw["provenance_valid"]),
        representability_margin=float(evidence_raw["representability_margin"]),
        canonical_command_error=float(evidence_raw["canonical_command_error"]),
        exact_transport_available=bool(evidence_raw["exact_transport_available"]),
        support_stability=float(evidence_raw["support_stability"]),
        held_out_residual=float(evidence_raw["held_out_residual"]),
        transverse_norm=float(evidence_raw["transverse_norm"]),
        certified_repair_radius=float(evidence_raw["certified_repair_radius"]),
        contract_class=ContractClass(evidence_raw["contract_class"]),
        support_ids=tuple(evidence_raw.get("support_ids", [])),
    )
    thresholds_raw = payload.get("thresholds", {})
    thresholds = Thresholds(
        pass_error=float(thresholds_raw.get("pass_error", 1e-6)),
        min_support_stability=float(thresholds_raw.get("min_support_stability", 0.9)),
        max_held_out_residual=float(thresholds_raw.get("max_held_out_residual", 0.05)),
    )
    provenance = [str(x) for x in payload["provenance"]]
    return evidence, provenance, thresholds


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile and independently verify an EPRC executable physical contract evidence bundle."
    )
    parser.add_argument("evidence_json", type=Path)
    parser.add_argument("--expect", choices=["PASS", "TRANSPORT", "REPAIR", "REJECT"])
    args = parser.parse_args()

    evidence, provenance, thresholds = load_evidence(args.evidence_json)
    certificate = compile_contract(
        evidence, provenance_parts=provenance, thresholds=thresholds
    )
    verified = verify_certificate(
        certificate,
        evidence,
        provenance_parts=provenance,
        thresholds=thresholds,
    )
    result = asdict(certificate)
    result["decision"] = certificate.decision.value
    result["contract_class"] = certificate.contract_class.value
    result["verified"] = verified
    print(json.dumps(result, indent=2, sort_keys=True))

    if not verified:
        return 2
    if args.expect is not None and certificate.decision.value != args.expect:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
