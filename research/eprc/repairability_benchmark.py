from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class RepairabilityTrial:
    crg_margin: float
    recovered: bool
    perturbation_norm: float
    controller_headroom: float
    raw_response_norm: float


@dataclass(frozen=True)
class BinaryMetrics:
    auc: float
    false_accept_rate: float
    true_accept_rate: float
    coverage: float
    accepted_success_rate: float


def _auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """AUC by pairwise ordering; exact and dependency-free for small evidence sets."""

    pos = scores[labels]
    neg = scores[~labels]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    wins = 0.0
    for p in pos:
        wins += float(np.sum(p > neg))
        wins += 0.5 * float(np.sum(p == neg))
    return wins / (len(pos) * len(neg))


def summarize_zero_threshold(
    trials: Iterable[RepairabilityTrial],
) -> BinaryMetrics:
    rows = tuple(trials)
    if not rows:
        raise ValueError("at least one trial is required")

    scores = np.array([r.crg_margin for r in rows], dtype=float)
    labels = np.array([r.recovered for r in rows], dtype=bool)
    accepted = scores >= 0.0

    false_accept = np.logical_and(accepted, ~labels)
    true_accept = np.logical_and(accepted, labels)

    accepted_n = int(np.sum(accepted))
    return BinaryMetrics(
        auc=float(_auc(scores, labels)),
        false_accept_rate=float(np.mean(false_accept)),
        true_accept_rate=float(np.mean(true_accept)),
        coverage=float(np.mean(accepted)),
        accepted_success_rate=(
            float(np.mean(labels[accepted])) if accepted_n else float("nan")
        ),
    )


def baseline_auc(
    trials: Iterable[RepairabilityTrial],
) -> dict[str, float]:
    rows = tuple(trials)
    labels = np.array([r.recovered for r in rows], dtype=bool)

    # Larger scores must mean "more likely recoverable".
    return {
        "crg_margin": _auc(
            np.array([r.crg_margin for r in rows], dtype=float), labels
        ),
        "negative_perturbation_norm": _auc(
            -np.array([r.perturbation_norm for r in rows], dtype=float), labels
        ),
        "controller_headroom": _auc(
            np.array([r.controller_headroom for r in rows], dtype=float), labels
        ),
        "negative_raw_response_norm": _auc(
            -np.array([r.raw_response_norm for r in rows], dtype=float), labels
        ),
    }


def paired_bootstrap_auc_delta(
    trials: Iterable[RepairabilityTrial],
    *,
    baseline: str,
    samples: int = 2000,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Paired bootstrap CI for CRG AUC minus one frozen scalar baseline."""

    rows = tuple(trials)
    if len(rows) < 4:
        raise ValueError("at least four trials are required")
    if baseline not in {
        "negative_perturbation_norm",
        "controller_headroom",
        "negative_raw_response_norm",
    }:
        raise ValueError("unknown baseline")

    rng = np.random.default_rng(seed)
    deltas: list[float] = []

    for _ in range(samples):
        idx = rng.integers(0, len(rows), len(rows))
        sample_rows = tuple(rows[i] for i in idx)
        labels = np.array([r.recovered for r in sample_rows], dtype=bool)
        if np.all(labels) or not np.any(labels):
            continue
        scores = baseline_auc(sample_rows)
        deltas.append(scores["crg_margin"] - scores[baseline])

    if not deltas:
        return float("nan"), float("nan"), float("nan")

    arr = np.sort(np.asarray(deltas))
    return (
        float(np.mean(arr)),
        float(np.quantile(arr, 0.025)),
        float(np.quantile(arr, 0.975)),
    )
