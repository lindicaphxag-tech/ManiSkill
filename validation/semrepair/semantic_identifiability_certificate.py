#!/usr/bin/env python3
"""Evidence-bound semantic identifiability certificate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
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


@dataclass(frozen=True)
class PairSeparability:
    left_hypothesis: str
    right_hypothesis: str
    semantic_linf: float
    primary_linf: float
    primary_separates: bool
    anchor_linf: float | None
    anchor_separates: bool | None
    jointly_separated: bool


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


def _parse_anchor_observables(
    external_anchor: dict[str, Any],
    hypotheses: tuple[HypothesisEvidence, ...],
) -> tuple[dict[str, tuple[float, ...]], float]:
    kind = external_anchor.get("kind")
    evidence_id = external_anchor.get("evidence_id")
    if kind not in VALID_ANCHOR_KINDS:
        raise ValueError(f"unsupported external anchor kind: {kind!r}")
    if not isinstance(evidence_id, str) or not evidence_id.strip():
        raise ValueError("external anchor requires a non-empty evidence_id")

    raw = external_anchor.get("hypothesis_observables")
    if not isinstance(raw, dict):
        raise ValueError(
            "external anchor requires hypothesis_observables bound to every hypothesis"
        )
    ids = {item.hypothesis_id for item in hypotheses}
    if set(raw) != ids:
        missing = sorted(ids - set(raw))
        extra = sorted(set(raw) - ids)
        raise ValueError(
            f"external anchor hypothesis coverage mismatch: missing={missing} extra={extra}"
        )

    parsed: dict[str, tuple[float, ...]] = {}
    dimension: int | None = None
    for hypothesis_id in sorted(ids):
        value = raw[hypothesis_id]
        if not isinstance(value, list) or not value:
            raise ValueError(
                f"anchor observable for {hypothesis_id!r} must be a non-empty list"
            )
        vector = tuple(float(x) for x in value)
        if dimension is None:
            dimension = len(vector)
        elif len(vector) != dimension:
            raise ValueError("all anchor observables must have equal dimension")
        parsed[hypothesis_id] = vector

    tolerance = float(external_anchor.get("tolerance", 0.0))
    if tolerance < 0:
        raise ValueError("external anchor tolerance must be non-negative")
    return parsed, tolerance


def _pair_separability(
    hypotheses: tuple[HypothesisEvidence, ...],
    *,
    observable_tolerance: float,
    semantic_separation: float,
    anchor_observables: dict[str, tuple[float, ...]] | None,
    anchor_tolerance: float | None,
) -> tuple[PairSeparability, ...]:
    rows: list[PairSeparability] = []
    for i, left in enumerate(hypotheses):
        for right in hypotheses[i + 1 :]:
            sem = _linf(left.semantic_target, right.semantic_target)
            if sem < semantic_separation:
                continue
            primary = _linf(left.observable, right.observable)
            primary_separates = primary > observable_tolerance

            anchor_linf = None
            anchor_separates = None
            if anchor_observables is not None:
                anchor_linf = _linf(
                    anchor_observables[left.hypothesis_id],
                    anchor_observables[right.hypothesis_id],
                )
                anchor_separates = anchor_linf > float(anchor_tolerance)

            rows.append(
                PairSeparability(
                    left_hypothesis=left.hypothesis_id,
                    right_hypothesis=right.hypothesis_id,
                    semantic_linf=sem,
                    primary_linf=primary,
                    primary_separates=primary_separates,
                    anchor_linf=anchor_linf,
                    anchor_separates=anchor_separates,
                    jointly_separated=primary_separates or bool(anchor_separates),
                )
            )
    return tuple(rows)


def qualify_identifiability(
    *,
    case: str,
    hypotheses: Iterable[HypothesisEvidence],
    observable_tolerance: float,
    semantic_separation: float,
    external_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    items = tuple(hypotheses)
    if len({item.hypothesis_id for item in items}) != len(items):
        raise ValueError("hypothesis_id values must be unique")

    collisions = find_collisions(
        items,
        observable_tolerance=observable_tolerance,
        semantic_separation=semantic_separation,
    )

    anchor_observables = None
    anchor_tolerance = None
    if external_anchor is not None:
        anchor_observables, anchor_tolerance = _parse_anchor_observables(
            external_anchor, items
        )

    pair_rows = _pair_separability(
        items,
        observable_tolerance=observable_tolerance,
        semantic_separation=semantic_separation,
        anchor_observables=anchor_observables,
        anchor_tolerance=anchor_tolerance,
    )
    unresolved = tuple(row for row in pair_rows if not row.jointly_separated)

    if external_anchor is None:
        if collisions:
            status = "fail"
            decision = "non_identifying_measurement"
            authority = "reject_until_external_semantic_anchor"
            reason = (
                "semantically distinct hypotheses are observationally indistinguishable "
                "within the frozen tolerance"
            )
        else:
            status = "undetermined"
            decision = "finite_search_found_no_collision"
            authority = "reject_until_identifiability_proven_or_externally_anchored"
            reason = (
                "no finite collision was found, but finite search cannot prove "
                "semantic identifiability"
            )
    elif unresolved:
        status = "fail"
        decision = "external_anchor_does_not_resolve_all_semantic_pairs"
        authority = "reject_until_stronger_semantic_anchor"
        reason = (
            "the bound external anchor leaves at least one materially distinct "
            "hypothesis pair observationally indistinguishable"
        )
    else:
        status = "pass"
        decision = "jointly_anchored_identifiability"
        authority = "identifiability_gate_pass"
        reason = (
            "every materially distinct hypothesis pair is separated by the "
            "primary observable or by the bound external semantic anchor"
        )

    canonical = {
        "schema_version": 2,
        "case": case,
        "observable_tolerance": observable_tolerance,
        "semantic_separation": semantic_separation,
        "hypotheses": [asdict(x) for x in items],
        "collisions": [asdict(x) for x in collisions],
        "pair_separability": [asdict(x) for x in pair_rows],
        "unresolved_pairs": [asdict(x) for x in unresolved],
        "external_anchor": external_anchor,
        "status": status,
        "decision": decision,
        "authority": authority,
        "reason": reason,
        "claim_boundary": (
            "Qualifies pairwise semantic identifiability over the declared finite "
            "hypothesis set and evidence channels; does not verify a repair, prove "
            "global identifiability outside that set, or grant execution authority."
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
