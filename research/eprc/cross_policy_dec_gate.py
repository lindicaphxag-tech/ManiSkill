from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Iterable

import numpy as np

from .contract_signature import contract_signature, semantically_lift_jacobian, signature_distance


@dataclass(frozen=True)
class PolicyCase:
    raw_action_jacobian: np.ndarray
    action_to_physical_jacobian: np.ndarray
    support_ids: tuple[str, ...]
    static_representation: str
    coarse_contract_class: str
    runtime_decision: str


@dataclass(frozen=True)
class PairScores:
    dec_distance: float
    raw_distance: float
    support_distance: float
    static_metadata_distance: float
    coarse_class_distance: float
    decisions_agree: bool


@dataclass(frozen=True)
class ProspectiveGate:
    min_pairs: int = 20
    min_dec_auc: float = 0.70
    required_auc_margin: float = 0.05


@dataclass(frozen=True)
class GateResult:
    n_pairs: int
    dec_auc: float
    raw_auc: float
    support_auc: float
    static_metadata_auc: float
    coarse_class_auc: float
    passed: bool
    reason: str


def _normalized_raw_distance(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        return inf
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0 if na == nb else inf
    return float(np.linalg.norm(a / na - b / nb))


def _jaccard_distance(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    union = sa | sb
    if not union:
        return 0.0
    return 1.0 - len(sa & sb) / len(union)


def score_pair(a: PolicyCase, b: PolicyCase) -> PairScores:
    phys_a = semantically_lift_jacobian(
        a.raw_action_jacobian, a.action_to_physical_jacobian
    )
    phys_b = semantically_lift_jacobian(
        b.raw_action_jacobian, b.action_to_physical_jacobian
    )
    dec = signature_distance(contract_signature(phys_a), contract_signature(phys_b))

    return PairScores(
        dec_distance=dec,
        raw_distance=_normalized_raw_distance(
            a.raw_action_jacobian, b.raw_action_jacobian
        ),
        support_distance=_jaccard_distance(a.support_ids, b.support_ids),
        static_metadata_distance=float(
            a.static_representation != b.static_representation
        ),
        coarse_class_distance=float(
            a.coarse_contract_class != b.coarse_contract_class
        ),
        decisions_agree=a.runtime_decision == b.runtime_decision,
    )


def auc_for_distance(scores: Iterable[float], labels_agree: Iterable[bool]) -> float:
    """Pairwise AUC: smaller distance should rank agreement above disagreement."""

    scores = np.asarray(tuple(scores), dtype=float)
    labels = np.asarray(tuple(labels_agree), dtype=bool)
    positives = scores[labels]
    negatives = scores[~labels]
    if len(positives) == 0 or len(negatives) == 0:
        raise ValueError("AUC requires both agreement and disagreement pairs")

    wins = 0.0
    total = 0
    for p in positives:
        for n in negatives:
            total += 1
            if p < n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / total


def evaluate_gate(
    pairs: Iterable[PairScores],
    *,
    gate: ProspectiveGate = ProspectiveGate(),
) -> GateResult:
    pairs = tuple(pairs)
    if len(pairs) < gate.min_pairs:
        return GateResult(
            n_pairs=len(pairs),
            dec_auc=float("nan"),
            raw_auc=float("nan"),
            support_auc=float("nan"),
            static_metadata_auc=float("nan"),
            coarse_class_auc=float("nan"),
            passed=False,
            reason=f"insufficient held-out pairs: {len(pairs)} < {gate.min_pairs}",
        )

    labels = [p.decisions_agree for p in pairs]
    metrics = {
        "dec": auc_for_distance([p.dec_distance for p in pairs], labels),
        "raw": auc_for_distance([p.raw_distance for p in pairs], labels),
        "support": auc_for_distance([p.support_distance for p in pairs], labels),
        "static": auc_for_distance([p.static_metadata_distance for p in pairs], labels),
        "class": auc_for_distance([p.coarse_class_distance for p in pairs], labels),
    }
    best_baseline = max(
        metrics["raw"], metrics["support"], metrics["static"], metrics["class"]
    )
    passed = (
        metrics["dec"] >= gate.min_dec_auc
        and metrics["dec"] >= best_baseline + gate.required_auc_margin
    )
    reason = (
        "DEC prospectively outperforms frozen baselines"
        if passed
        else "DEC failed the pre-registered discrimination margin"
    )

    return GateResult(
        n_pairs=len(pairs),
        dec_auc=metrics["dec"],
        raw_auc=metrics["raw"],
        support_auc=metrics["support"],
        static_metadata_auc=metrics["static"],
        coarse_class_auc=metrics["class"],
        passed=passed,
        reason=reason,
    )
