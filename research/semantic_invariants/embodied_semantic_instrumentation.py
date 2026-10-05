"""Minimum instrumentation planning for hidden semantic transport faults.

A single end-to-end trace can be insufficient when wrong semantic transports
cancel.  This module generalizes the one-chain observability check to a finite,
frozen family of fault hypotheses.

Given:

- one *reference* semantic transport chain;
- a set of candidate faulty chains with the same named boundaries; and
- an external observation at the final output,

the planner identifies hypotheses whose final transport is indistinguishable
from the reference, computes every internal boundary that would distinguish each
such hypothesis, and solves the exact minimum hitting-set problem over those
boundary sets.

The result is a constructive instrumentation certificate: the smallest set of
internal taps needed to make every frozen hidden hypothesis observable, together
with a canonical basis witness for each hidden hypothesis.

This is deliberately a finite-hypothesis guarantee.  It does not claim that the
selected taps diagnose arbitrary unknown faults outside the frozen family.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from typing import Sequence

from .embodied_semantic_transport import (
    MonomialSemanticTransport,
    SemanticTransportFactor,
)


@dataclass(frozen=True)
class SemanticTransportScenario:
    name: str
    factors: tuple[SemanticTransportFactor, ...]
    evidence_id: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("scenario name must be non-empty")
        if not self.factors:
            raise ValueError("scenario requires at least one factor")
        if not self.evidence_id:
            raise ValueError("scenario requires evidence_id")


@dataclass(frozen=True)
class ScenarioTapWitness:
    scenario: str
    after_factor: str
    basis_index: int
    reference_output: tuple[float, ...]
    candidate_output: tuple[float, ...]
    residual_linf: float


@dataclass(frozen=True)
class HiddenScenarioObservability:
    scenario: str
    distinguishing_taps: tuple[str, ...]
    witness: ScenarioTapWitness


@dataclass(frozen=True)
class SemanticInstrumentationCertificate:
    reference_name: str
    factor_names: tuple[str, ...]
    candidate_names: tuple[str, ...]
    externally_distinguishable: tuple[str, ...]
    externally_hidden: tuple[HiddenScenarioObservability, ...]
    minimum_internal_taps: tuple[str, ...]
    hypothesis_count: int
    hidden_hypothesis_count: int
    digest: str

    @property
    def needs_internal_instrumentation(self) -> bool:
        return bool(self.externally_hidden)


def _same_transport(
    left: MonomialSemanticTransport,
    right: MonomialSemanticTransport,
    *,
    atol: float,
) -> bool:
    if left.dimension != right.dimension:
        return False
    if left.source_for_output != right.source_for_output:
        return False
    return all(
        abs(float(a) - float(b)) <= atol
        for a, b in zip(left.scale, right.scale, strict=True)
    )


def _prefixes(
    factors: Sequence[SemanticTransportFactor],
) -> tuple[MonomialSemanticTransport, ...]:
    items = tuple(factors)
    if not items:
        raise ValueError("at least one factor is required")
    dimension = items[0].transport.dimension
    if any(item.transport.dimension != dimension for item in items):
        raise ValueError("all factors must have the same dimension")

    out: list[MonomialSemanticTransport] = []
    prefix = MonomialSemanticTransport.identity(dimension)
    for factor in items:
        prefix = prefix.then(factor.transport)
        out.append(prefix)
    return tuple(out)


def _basis(dimension: int, index: int) -> tuple[float, ...]:
    return tuple(1.0 if i == index else 0.0 for i in range(dimension))


def _residual_linf(
    left: Sequence[float],
    right: Sequence[float],
) -> float:
    return max(abs(float(a) - float(b)) for a, b in zip(left, right, strict=True))


def _basis_witness(
    *,
    scenario: str,
    after_factor: str,
    reference: MonomialSemanticTransport,
    candidate: MonomialSemanticTransport,
    atol: float,
) -> ScenarioTapWitness:
    if reference.dimension != candidate.dimension:
        raise ValueError("reference/candidate dimensions differ")
    for index in range(reference.dimension):
        probe = _basis(reference.dimension, index)
        expected = reference.apply(probe)
        observed = candidate.apply(probe)
        residual = _residual_linf(expected, observed)
        if residual > atol:
            return ScenarioTapWitness(
                scenario=scenario,
                after_factor=after_factor,
                basis_index=index,
                reference_output=expected,
                candidate_output=observed,
                residual_linf=residual,
            )
    raise RuntimeError(
        "non-equivalent monomial transports had no distinguishing basis vector"
    )


def _minimum_hitting_set(
    universe: tuple[int, ...],
    requirements: Sequence[frozenset[int]],
) -> tuple[int, ...]:
    if not requirements:
        return ()
    if any(not req for req in requirements):
        raise ValueError("hidden scenario has no distinguishing internal boundary")

    for size in range(1, len(universe) + 1):
        for combo in combinations(universe, size):
            selected = set(combo)
            if all(selected & set(req) for req in requirements):
                return combo
    raise RuntimeError("no instrumentation set covers all hidden hypotheses")


def _factor_signature(factor: SemanticTransportFactor) -> dict:
    return {
        "name": factor.name,
        "source_for_output": list(factor.transport.source_for_output),
        "scale": list(factor.transport.scale),
        "evidence_id": factor.evidence_id,
    }


def _certificate_digest(
    *,
    reference: SemanticTransportScenario,
    candidates: Sequence[SemanticTransportScenario],
    atol: float,
    selected_taps: Sequence[str],
) -> str:
    payload = {
        "reference": {
            "name": reference.name,
            "evidence_id": reference.evidence_id,
            "factors": [_factor_signature(item) for item in reference.factors],
        },
        "candidates": [
            {
                "name": scenario.name,
                "evidence_id": scenario.evidence_id,
                "factors": [_factor_signature(item) for item in scenario.factors],
            }
            for scenario in candidates
        ],
        "atol": atol,
        "selected_taps": list(selected_taps),
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def plan_minimum_semantic_instrumentation(
    *,
    reference: SemanticTransportScenario,
    candidates: Sequence[SemanticTransportScenario],
    atol: float = 0.0,
) -> SemanticInstrumentationCertificate:
    """Compute an exact minimum internal tap set for a frozen fault family.

    Candidate chains whose final transport differs from the reference are
    already externally distinguishable and require no internal tap.

    A candidate is *externally hidden* when its final transport matches the
    reference while at least one internal prefix differs.  For each hidden
    candidate, every differing non-final prefix is a valid distinguishing tap.
    The planner then computes the minimum-cardinality hitting set over those tap
    sets, with lexicographic tie-breaking by boundary order.

    The final boundary is excluded from the tap universe because it is the
    external observation point and, by definition, carries no information for
    an externally hidden candidate.
    """

    if atol < 0:
        raise ValueError("atol must be non-negative")

    candidate_items = tuple(candidates)
    if not candidate_items:
        raise ValueError("at least one candidate scenario is required")

    factor_names = tuple(item.name for item in reference.factors)
    if len(set(factor_names)) != len(factor_names):
        raise ValueError("reference factor names must be unique")
    if len(factor_names) < 2:
        raise ValueError("instrumentation planning requires at least two boundaries")

    ref_prefixes = _prefixes(reference.factors)
    dimension = ref_prefixes[0].dimension

    externally_distinguishable: list[str] = []
    hidden_raw: list[
        tuple[
            SemanticTransportScenario,
            tuple[int, ...],
            tuple[MonomialSemanticTransport, ...],
        ]
    ] = []

    for scenario in candidate_items:
        names = tuple(item.name for item in scenario.factors)
        if names != factor_names:
            raise ValueError(
                f"scenario {scenario.name!r} factor names/order do not match reference"
            )
        prefixes = _prefixes(scenario.factors)
        if any(prefix.dimension != dimension for prefix in prefixes):
            raise ValueError(f"scenario {scenario.name!r} dimension mismatch")

        if not _same_transport(prefixes[-1], ref_prefixes[-1], atol=atol):
            externally_distinguishable.append(scenario.name)
            continue

        differing = tuple(
            index
            for index in range(len(factor_names) - 1)
            if not _same_transport(
                prefixes[index],
                ref_prefixes[index],
                atol=atol,
            )
        )

        # If every prefix, including the final prefix, matches, this candidate
        # is semantically equivalent to the reference for the supported
        # transport model and does not constitute a hidden transport fault.
        if not differing:
            continue

        hidden_raw.append((scenario, differing, prefixes))

    universe = tuple(range(len(factor_names) - 1))
    requirements = tuple(frozenset(item[1]) for item in hidden_raw)
    selected_indices = _minimum_hitting_set(universe, requirements)
    selected_names = tuple(factor_names[index] for index in selected_indices)

    hidden: list[HiddenScenarioObservability] = []
    for scenario, differing, prefixes in hidden_raw:
        tap_index = next(index for index in selected_indices if index in differing)
        witness = _basis_witness(
            scenario=scenario.name,
            after_factor=factor_names[tap_index],
            reference=ref_prefixes[tap_index],
            candidate=prefixes[tap_index],
            atol=atol,
        )
        hidden.append(
            HiddenScenarioObservability(
                scenario=scenario.name,
                distinguishing_taps=tuple(
                    factor_names[index] for index in differing
                ),
                witness=witness,
            )
        )

    hidden_sorted = tuple(sorted(hidden, key=lambda item: item.scenario))
    external_sorted = tuple(sorted(externally_distinguishable))

    return SemanticInstrumentationCertificate(
        reference_name=reference.name,
        factor_names=factor_names,
        candidate_names=tuple(item.name for item in candidate_items),
        externally_distinguishable=external_sorted,
        externally_hidden=hidden_sorted,
        minimum_internal_taps=selected_names,
        hypothesis_count=len(candidate_items),
        hidden_hypothesis_count=len(hidden_sorted),
        digest=_certificate_digest(
            reference=reference,
            candidates=candidate_items,
            atol=atol,
            selected_taps=selected_names,
        ),
    )
