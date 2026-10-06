from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from json import dumps
from math import inf
from typing import Iterable

import numpy as np

from .bilateral_chart_invariance import canonicalize_dec_jacobian
from .contract_signature import contract_signature, signature_distance


@dataclass(frozen=True)
class PolicyCase:
    raw_action_jacobian: np.ndarray
    action_to_physical_jacobian: np.ndarray
    support_ids: tuple[str, ...]
    static_representation: str
    coarse_contract_class: str
    runtime_decision: str
    physical_support_to_support_chart_jacobian: np.ndarray | None = None
    heldout_physical_response: np.ndarray | None = None


@dataclass(frozen=True)
class PairScores:
    dec_distance: float
    raw_distance: float
    support_distance: float
    static_metadata_distance: float
    coarse_class_distance: float
    decisions_agree: bool
    heldout_response_distance: float = float("nan")


@dataclass(frozen=True)
class ProspectiveGate:
    min_pairs: int = 20
    min_dec_auc: float = 0.70
    required_auc_margin: float = 0.05


@dataclass(frozen=True)
class GateResult:
    gate_digest: str
    n_pairs: int
    dec_auc: float
    raw_auc: float
    support_auc: float
    static_metadata_auc: float
    coarse_class_auc: float
    passed: bool
    reason: str


def gate_digest(gate: ProspectiveGate) -> str:
    canonical = dumps(asdict(gate), sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


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


def _relative_response_distance(
    a: np.ndarray | None,
    b: np.ndarray | None,
) -> float:
    """External held-out target: distance between fresh physical responses.

    The held-out response is never used to identify the DEC. It comes from a
    fresh policy/environment query at a disturbance excluded from the probe set.
    """

    if a is None or b is None:
        return float("nan")
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        return float("inf")
    denom = max(float(np.linalg.norm(a)), float(np.linalg.norm(b)), 1e-12)
    return float(np.linalg.norm(a - b) / denom)


def _jaccard_distance(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    union = sa | sb
    if not union:
        return 0.0
    return 1.0 - len(sa & sb) / len(union)


def score_pair(a: PolicyCase, b: PolicyCase) -> PairScores:
    support_a = (
        np.eye(a.raw_action_jacobian.shape[1])
        if a.physical_support_to_support_chart_jacobian is None
        else a.physical_support_to_support_chart_jacobian
    )
    support_b = (
        np.eye(b.raw_action_jacobian.shape[1])
        if b.physical_support_to_support_chart_jacobian is None
        else b.physical_support_to_support_chart_jacobian
    )
    phys_a = canonicalize_dec_jacobian(
        a.raw_action_jacobian,
        a.action_to_physical_jacobian,
        support_a,
    )
    phys_b = canonicalize_dec_jacobian(
        b.raw_action_jacobian,
        b.action_to_physical_jacobian,
        support_b,
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
        heldout_response_distance=_relative_response_distance(
            a.heldout_physical_response, b.heldout_physical_response
        ),
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
            gate_digest=gate_digest(gate),
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
        gate_digest=gate_digest(gate),
        n_pairs=len(pairs),
        dec_auc=metrics["dec"],
        raw_auc=metrics["raw"],
        support_auc=metrics["support"],
        static_metadata_auc=metrics["static"],
        coarse_class_auc=metrics["class"],
        passed=passed,
        reason=reason,
    )


@dataclass(frozen=True)
class ResponseProspectiveGate:
    min_pairs: int = 20
    min_dec_spearman: float = 0.50
    required_spearman_margin: float = 0.10


@dataclass(frozen=True)
class ResponseGateResult:
    gate_digest: str
    n_pairs: int
    dec_spearman: float
    raw_spearman: float
    support_spearman: float
    static_metadata_spearman: float
    coarse_class_spearman: float
    passed: bool
    reason: str


def response_gate_digest(gate: ResponseProspectiveGate) -> str:
    canonical = dumps(asdict(gate), sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _average_ranks(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or np.any(np.isnan(values)):
        raise ValueError("rank input must be one-dimensional and non-NaN")
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and values[order[j]] == values[order[i]]:
            j += 1
        average = 0.5 * (i + j - 1) + 1.0
        ranks[order[i:j]] = average
        i = j
    return ranks


def spearman_correlation(x: Iterable[float], y: Iterable[float]) -> float:
    """Spearman rank correlation without an external statistics dependency."""

    x = np.asarray(tuple(x), dtype=float)
    y = np.asarray(tuple(y), dtype=float)
    if x.shape != y.shape or x.ndim != 1 or len(x) < 2:
        raise ValueError("Spearman inputs must be equal-length one-dimensional arrays")
    rx = _average_ranks(x)
    ry = _average_ranks(y)
    rx = rx - np.mean(rx)
    ry = ry - np.mean(ry)
    denom = float(np.linalg.norm(rx) * np.linalg.norm(ry))
    if denom == 0.0:
        return 0.0
    return float(np.dot(rx, ry) / denom)


def evaluate_response_gate(
    pairs: Iterable[PairScores],
    *,
    gate: ResponseProspectiveGate = ResponseProspectiveGate(),
) -> ResponseGateResult:
    """Primary scientific gate: predict fresh held-out physical response geometry.

    This avoids circularity: PASS/TRANSPORT/REPAIR/REJECT decisions may use DEC,
    whereas the fresh held-out response is external evidence not used to fit the
    contract.
    """

    pairs = tuple(pairs)
    digest = response_gate_digest(gate)
    if len(pairs) < gate.min_pairs:
        return ResponseGateResult(
            gate_digest=digest,
            n_pairs=len(pairs),
            dec_spearman=float("nan"),
            raw_spearman=float("nan"),
            support_spearman=float("nan"),
            static_metadata_spearman=float("nan"),
            coarse_class_spearman=float("nan"),
            passed=False,
            reason=f"insufficient held-out pairs: {len(pairs)} < {gate.min_pairs}",
        )

    target = np.asarray([p.heldout_response_distance for p in pairs], dtype=float)
    if np.any(np.isnan(target)) or np.any(np.isinf(target)):
        return ResponseGateResult(
            gate_digest=digest,
            n_pairs=len(pairs),
            dec_spearman=float("nan"),
            raw_spearman=float("nan"),
            support_spearman=float("nan"),
            static_metadata_spearman=float("nan"),
            coarse_class_spearman=float("nan"),
            passed=False,
            reason="held-out physical response evidence is missing or dimensionally incompatible",
        )

    metrics = {
        "dec": spearman_correlation([p.dec_distance for p in pairs], target),
        "raw": spearman_correlation([p.raw_distance for p in pairs], target),
        "support": spearman_correlation([p.support_distance for p in pairs], target),
        "static": spearman_correlation(
            [p.static_metadata_distance for p in pairs], target
        ),
        "class": spearman_correlation([p.coarse_class_distance for p in pairs], target),
    }
    best_baseline = max(metrics["raw"], metrics["support"], metrics["static"], metrics["class"])
    passed = (
        metrics["dec"] >= gate.min_dec_spearman
        and metrics["dec"] >= best_baseline + gate.required_spearman_margin
    )
    return ResponseGateResult(
        gate_digest=digest,
        n_pairs=len(pairs),
        dec_spearman=metrics["dec"],
        raw_spearman=metrics["raw"],
        support_spearman=metrics["support"],
        static_metadata_spearman=metrics["static"],
        coarse_class_spearman=metrics["class"],
        passed=passed,
        reason=(
            "DEC prospectively predicts fresh held-out physical response geometry"
            if passed
            else "DEC failed the frozen held-out response prediction margin"
        ),
    )
