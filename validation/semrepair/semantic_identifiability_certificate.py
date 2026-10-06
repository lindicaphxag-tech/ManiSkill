#!/usr/bin/env python3
"""Evidence-bound semantic identifiability certificate."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

VALID_ANCHOR_KINDS = {
    "repository_native_semantic_oracle",
    "explicit_named_index_map",
    "independent_physical_measurement",
    "formal_injectivity_proof",
}


@dataclass(frozen=True)
class HypothesisEvidence:
    hypothesis_id: str
    observable: tuple[float, ...]
    semantic_target: tuple[float, ...]
    evidence_id: str


@dataclass(frozen=True)
class IdentifiabilityCollision:
    left_hypothesis: str
    right_hypothesis: str
    observable_linf: float
    semantic_linf: float
    left_evidence_id: str
    right_evidence_id: str


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must have equal dimension")
    if not left:
        return 0.0
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def find_collisions(
    hypotheses: Iterable[HypothesisEvidence],
    *,
    observable_tolerance: float,
    semantic_separation: float,
) -> tuple[IdentifiabilityCollision, ...]:
    if observable_tolerance < 0:
        raise ValueError("observable_tolerance must be non-negative")
    if semantic_separation <= 0:
        raise ValueError("semantic_separation must be positive")

    items = tuple(hypotheses)
    collisions: list[IdentifiabilityCollision] = []
    for i, left in enumerate(items):
        for right in items[i + 1 :]:
            obs = _linf(left.observable, right.observable)
            sem = _linf(left.semantic_target, right.semantic_target)
            if obs <= observable_tolerance and sem >= semantic_separation:
                collisions.append(
                    IdentifiabilityCollision(
                        left_hypothesis=left.hypothesis_id,
                        right_hypothesis=right.hypothesis_id,
                        observable_linf=obs,
                        semantic_linf=sem,
                        left_evidence_id=left.evidence_id,
                        right_evidence_id=right.evidence_id,
                    )
                )
    return tuple(collisions)


def qualify_identifiability(
    *,
    case: str,
    hypotheses: Iterable[HypothesisEvidence],
    observable_tolerance: float,
    semantic_separation: float,
    external_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    items = tuple(hypotheses)
    collisions = find_collisions(
        items,
        observable_tolerance=observable_tolerance,
        semantic_separation=semantic_separation,
    )

    if collisions:
        status = "fail"
        decision = "non_identifying_measurement"
        authority = "reject_until_external_semantic_anchor"
        reason = (
            "semantically distinct hypotheses are observationally indistinguishable "
            "within the frozen tolerance"
        )
    elif external_anchor is None:
        status = "undetermined"
        decision = "finite_search_found_no_collision"
        authority = "reject_until_identifiability_proven_or_externally_anchored"
        reason = (
            "no finite collision was found, but finite search cannot prove "
            "semantic identifiability"
        )
    else:
        kind = external_anchor.get("kind")
        evidence_id = external_anchor.get("evidence_id")
        if kind not in VALID_ANCHOR_KINDS:
            raise ValueError(f"unsupported external anchor kind: {kind!r}")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError("external anchor requires a non-empty evidence_id")
        status = "pass"
        decision = "externally_anchored_identifiability"
        authority = "identifiability_gate_pass"
        reason = (
            "finite search found no collision and an independent semantic "
            "anchor/proof is bound to the certificate"
        )

    canonical = {
        "schema_version": 1,
        "case": case,
        "observable_tolerance": observable_tolerance,
        "semantic_separation": semantic_separation,
        "hypotheses": [asdict(x) for x in items],
        "collisions": [asdict(x) for x in collisions],
        "external_anchor": external_anchor,
        "status": status,
        "decision": decision,
        "authority": authority,
        "reason": reason,
        "claim_boundary": (
            "Qualifies semantic identifiability of an evidence channel; "
            "does not verify a repair or grant execution authority."
        ),
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    canonical["certificate_sha256"] = hashlib.sha256(encoded).hexdigest()
    return canonical


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    hypotheses = tuple(
        HypothesisEvidence(
            hypothesis_id=item["hypothesis_id"],
            observable=tuple(float(x) for x in item["observable"]),
            semantic_target=tuple(float(x) for x in item["semantic_target"]),
            evidence_id=item["evidence_id"],
        )
        for item in payload["hypotheses"]
    )
    report = qualify_identifiability(
        case=payload["case"],
        hypotheses=hypotheses,
        observable_tolerance=float(payload["observable_tolerance"]),
        semantic_separation=float(payload["semantic_separation"]),
        external_anchor=payload.get("external_anchor"),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
