"""Cluster-split conformal response-transfer screening for paired A/B requests.

This provides *marginal whole-state coverage* under exchangeable calibration
and future state clusters, NOT a per-action or worst-case physical guarantee.
It is intentionally distinct from deterministic robust CRG certification.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from math import ceil, isfinite

import numpy as np


class ScreenDecision(str, Enum):
    STATISTICALLY_SIMILAR = "STATISTICALLY_SIMILAR"
    STATISTICALLY_DISTINCT = "STATISTICALLY_DISTINCT"
    ABSTAIN_UNCERTAIN = "ABSTAIN_UNCERTAIN"
    REJECT_INVALID_LOCAL_MODEL = "REJECT_INVALID_LOCAL_MODEL"


@dataclass(frozen=True)
class CalibratedStateEnvelope:
    radius: float
    alpha: float
    k_order_statistic: int
    n_calibration_states: int
    calibration_state_ids: tuple[str, ...]
    calibration_digest: str
    coverage_interpretation: str = (
        "State-block split conformal marginal coverage under exchangeable "
        "state clusters and a fully fixed score/policy/protocol; not "
        "conditional, physical safety, or deterministic certification"
    )


@dataclass(frozen=True)
class ScreenResult:
    decision: ScreenDecision
    nominal_disagreement: float | None
    interval_lower: float | None
    interval_upper: float | None
    tolerance: float
    marginal_state_coverage_target: float
    deterministically_certified: bool
    externally_verified: bool
    reason: str


def _predict_gap(pair: dict) -> float:
    a = np.asarray(pair["map_a"], dtype=float)
    b = np.asarray(pair["map_b"], dtype=float)
    h = np.asarray(pair["support_delta"], dtype=float)
    if (
        a.ndim != 2 or b.shape != a.shape or h.ndim != 1
        or a.shape[1] != h.size or not a.size
    ):
        raise ValueError("invalid, unaligned canonical physical support/response charts")
    if not (np.isfinite(a).all() and np.isfinite(b).all() and np.isfinite(h).all()):
        raise ValueError("nonfinite physical response map or intervention")
    val = float(np.linalg.norm((a-b) @ h))
    if not isfinite(val):
        raise ValueError("nonfinite predicted response disagreement")
    return val


def _true_gap(pair: dict) -> float:
    a = np.asarray(pair["observed_response_a"], dtype=float)
    b = np.asarray(pair["observed_response_b"], dtype=float)
    if a.ndim != 1 or a.shape != b.shape or not a.size:
        raise ValueError("invalid observed response pair")
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("nonfinite observed policy response")
    val = float(np.linalg.norm(a-b))
    if not isfinite(val):
        raise ValueError("nonfinite true policy response disagreement")
    return val


def _validate_group(group: dict) -> None:
    records = group.get("pairs")
    if not isinstance(records, list) or len(records) != 2:
        raise ValueError("each state cluster needs exactly A and B held-outs")
    if [pair.get("heldout_id") for pair in records] != ["A", "B"]:
        raise ValueError("paired held-outs must be A then B (no filtering)")
    # The two held-out probes must be evaluated against the SAME identified
    # local policy maps. Different maps within one state silently create a
    # pseudoreplicated test of two fitted models rather than two requests.
    for field in ("map_a", "map_b"):
        a = np.asarray(records[0][field], dtype=float)
        b = np.asarray(records[1][field], dtype=float)
        if a.shape != b.shape or not np.array_equal(a, b):
            raise ValueError("A/B within one restored state must share identified policy maps")


def fit_state_block_envelope(
    calibration_states: list[dict],
    *,
    alpha: float = 0.1,
    source_protocol_digest: str,
) -> CalibratedStateEnvelope:
    """Fit max-A/B nonconformity over WHOLE states.

    For n exchangeable calibration state-block maxima and one future state
    maximum, kth order-statistic at k=ceil((n+1)(1-alpha)) yields >=1-alpha
    marginal coverage when k<=n, with usual split-conformal exchangeability
    and fixed pre-calibration model/score assumptions. No hidden state
    exclusion or calibration/test overlap is allowed.
    """
    if not isfinite(float(alpha)) or not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    if not isinstance(source_protocol_digest, str) or len(source_protocol_digest) != 64:
        raise ValueError("source_protocol_digest must be an immutable SHA-256 hex digest")
    try:
        int(source_protocol_digest, 16)
    except ValueError as error:
        raise ValueError("nonhex source_protocol_digest") from error
    n = len(calibration_states)
    k = ceil((n+1)*(1-alpha)-1e-12)
    if n < 2 or k > n:
        raise ValueError(
            "insufficient independent state calibration clusters for requested alpha"
        )
    state_ids = [str(g.get("state_id", "")).strip() for g in calibration_states]
    if not all(state_ids) or len(set(state_ids)) != n:
        raise ValueError("missing or duplicate calibration state IDs")
    scores = []
    for group in calibration_states:
        _validate_group(group)
        errors = [abs(_predict_gap(p)-_true_gap(p)) for p in group["pairs"]]
        scores.append(max(errors))
    radius = float(sorted(scores)[k-1])
    if not isfinite(radius):
        raise ValueError("nonfinite calibration radius")
    manifest = {
        "schema": "state-block-transfer-calibration-v1",
        "state_ids": state_ids,
        "scores": scores,
        "alpha": alpha,
        "k": k,
        "source_protocol_digest": source_protocol_digest,
    }
    digest = sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return CalibratedStateEnvelope(
        radius=radius,
        alpha=alpha,
        k_order_statistic=k,
        n_calibration_states=n,
        calibration_state_ids=tuple(state_ids),
        calibration_digest=digest,
    )


def screen_new_state_pair(
    envelope: CalibratedStateEnvelope,
    *,
    test_state_id: str,
    pair: dict,
    trusted_response_tolerance: float,
    local_model_a_admissible: bool,
    local_model_b_admissible: bool,
    support_admissible: bool,
    controller_authority_admissible: bool,
) -> ScreenResult:
    """Make a real abstain/transfer decision without seeing test outcomes."""
    if not isfinite(float(trusted_response_tolerance)) or trusted_response_tolerance < 0:
        raise ValueError("invalid response tolerance")
    state_id = str(test_state_id).strip()
    if not state_id or state_id in envelope.calibration_state_ids:
        raise ValueError("missing test identity or calibration/test leakage")
    def result(decision, low, high, nominal, reason):
        return ScreenResult(
            decision, nominal, low, high, float(trusted_response_tolerance),
            1-envelope.alpha, False, False, reason,
        )
    if not all(x is True for x in (
        local_model_a_admissible, local_model_b_admissible,
        support_admissible, controller_authority_admissible,
    )):
        return result(
            ScreenDecision.REJECT_INVALID_LOCAL_MODEL, None, None, None,
            "missing locality, controller-authority or physical-support evidence",
        )
    nominal = _predict_gap(pair)
    low, high = max(0.0, nominal-envelope.radius), nominal+envelope.radius
    if high <= trusted_response_tolerance:
        return result(
            ScreenDecision.STATISTICALLY_SIMILAR, low, high, nominal,
            "only marginal whole-state coverage; NOT a certified safe transfer",
        )
    if low > trusted_response_tolerance:
        return result(
            ScreenDecision.STATISTICALLY_DISTINCT, low, high, nominal,
            "only marginal whole-state coverage; NOT a certified impossibility",
        )
    return result(
        ScreenDecision.ABSTAIN_UNCERTAIN, low, high, nominal,
        "state-calibrated interval straddles the application tolerance",
    )


def audit_heldout_state(
    envelope: CalibratedStateEnvelope,
    state: dict,
    decisions: list[ScreenResult],
) -> dict:
    """After predictions are frozen, audit both outcomes as ONE state unit."""
    _validate_group(state)
    if len(decisions) != 2:
        raise ValueError("both A/B decisions needed, even if rejected")
    sid = str(state.get("state_id", "")).strip()
    if not sid or sid in envelope.calibration_state_ids:
        raise ValueError("calibration/test overlap or missing state identity")
    observed = []
    false_authorizations = 0
    for pair, pred in zip(state["pairs"], decisions, strict=True):
        gap = _true_gap(pair)
        observed.append(gap)
        if pred.decision is ScreenDecision.STATISTICALLY_SIMILAR and gap > pred.tolerance:
            false_authorizations += 1
        if pred.decision is ScreenDecision.STATISTICALLY_DISTINCT and gap <= pred.tolerance:
            false_authorizations += 1
    # Marginal target is over *states*, not each of the 2 observations.
    errors = [abs(_true_gap(p)-_predict_gap(p)) for p in state["pairs"]]
    return {
        "state_id": sid,
        "state_block_covered": max(errors) <= envelope.radius,
        "decisions": [pred.decision.value for pred in decisions],
        "observed_response_gaps": observed,
        "false_authorizations": false_authorizations,
        "denominator_observations": 2,
        "denominator_state_clusters": 1,
        "external_validation": False,
    }
