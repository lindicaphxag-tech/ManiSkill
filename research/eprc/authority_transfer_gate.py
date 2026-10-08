from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from json import dumps
from typing import Iterable

import numpy as np

from .support_restricted_authority import support_restricted_authority


@dataclass(frozen=True)
class AuthorityTrial:
    source_physical_jacobian: np.ndarray
    target_action_to_physical_jacobian: np.ndarray
    transport_succeeded: bool
    global_rank_flag: bool
    clipping_flag: bool


@dataclass(frozen=True)
class AuthorityGate:
    min_trials: int = 20
    max_exact_residual: float = 1e-6
    min_projection_auc: float = 0.75
    required_auc_margin: float = 0.05


@dataclass(frozen=True)
class AuthorityGateResult:
    gate_digest: str
    n_trials: int
    projection_auc: float
    global_rank_auc: float
    clipping_auc: float
    passed: bool
    reason: str


def gate_digest(gate: AuthorityGate) -> str:
    payload = dumps(asdict(gate), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def _auc_lower_score_means_success(scores: Iterable[float], success: Iterable[bool]) -> float:
    scores = np.asarray(tuple(scores), dtype=float)
    labels = np.asarray(tuple(success), dtype=bool)
    pos = scores[labels]
    neg = scores[~labels]
    if len(pos) == 0 or len(neg) == 0:
        raise ValueError("AUC requires both successes and failures")
    wins = 0.0
    total = 0
    for p in pos:
        for n in neg:
            total += 1
            if p < n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / total


def evaluate_authority_gate(
    trials: Iterable[AuthorityTrial],
    *,
    gate: AuthorityGate = AuthorityGate(),
) -> AuthorityGateResult:
    trials = tuple(trials)
    digest = gate_digest(gate)
    if len(trials) < gate.min_trials:
        return AuthorityGateResult(
            gate_digest=digest,
            n_trials=len(trials),
            projection_auc=float("nan"),
            global_rank_auc=float("nan"),
            clipping_auc=float("nan"),
            passed=False,
            reason=f"insufficient held-out trials: {len(trials)} < {gate.min_trials}",
        )

    projection = []
    global_rank = []
    clipping = []
    labels = []
    for trial in trials:
        cert = support_restricted_authority(
            trial.source_physical_jacobian,
            trial.target_action_to_physical_jacobian,
        ).certificate
        projection.append(cert.relative_projection_residual)
        # Lower score should mean success for all predictors.
        global_rank.append(float(not trial.global_rank_flag))
        clipping.append(float(trial.clipping_flag))
        labels.append(trial.transport_succeeded)

    auc_projection = _auc_lower_score_means_success(projection, labels)
    auc_global = _auc_lower_score_means_success(global_rank, labels)
    auc_clip = _auc_lower_score_means_success(clipping, labels)
    best_baseline = max(auc_global, auc_clip)

    passed = (
        auc_projection >= gate.min_projection_auc
        and auc_projection >= best_baseline + gate.required_auc_margin
    )
    return AuthorityGateResult(
        gate_digest=digest,
        n_trials=len(trials),
        projection_auc=auc_projection,
        global_rank_auc=auc_global,
        clipping_auc=auc_clip,
        passed=passed,
        reason=(
            "support-restricted authority prospectively predicts transport success"
            if passed
            else "support-restricted authority failed the frozen predictive margin"
        ),
    )
