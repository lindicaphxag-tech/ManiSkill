"""Robust binary execution-ACK probe versus trusted target readback.

A calibrated binary public signal Z has interval-uncertain probabilities
P(Z=1 | ACK held/applied, action). Minimax post-observation classification
risk can be computed exactly with a small linear program. This is NOT a
physical-response calibration, hardware safety guarantee, or new PhysX result.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.optimize import linprog

from research.ack_native_probe_source_adapter import NativeProbeProposal


@dataclass(frozen=True)
class BinaryProbeEvidence:
    proposal: NativeProbeProposal
    p_signal_held: tuple[float, float]
    p_signal_applied: tuple[float, float]
    independent_holdout_calibration_attested: bool
    calibrated_cost_attested: bool
    calibration_receipt: str


@dataclass(frozen=True)
class RobustRiskDecision:
    decision: str
    name: str | None
    native_action: tuple[float, ...] | None
    total_worst_case_loss: float
    worst_classification_loss: float
    prior_without_probe_loss: float
    guaranteed_information_value: float
    considered_valid_probes: int
    reason: str
    physical_safety_certified: bool = False
    signal_zero_decision: str | None = None
    signal_one_decision: str | None = None
    no_probe_history_decision: str | None = None


def _interval(values: Sequence[float]) -> tuple[float, float]:
    if len(values) != 2:
        raise ValueError("probability bound must be a pair")
    a, b = float(values[0]), float(values[1])
    if not (isfinite(a) and isfinite(b) and 0 <= a <= b <= 1):
        raise ValueError("interval probabilities must lie within [0,1]")
    return a, b


def robust_binary_posterior_risk(
    prior_applied: float,
    p_signal_held: Sequence[float],
    p_signal_applied: Sequence[float],
    *,
    false_applied_cost: float = 1.0,
    false_held_cost: float = 1.0,
) -> tuple[float, float]:
    """Exact worst-case binary Bayes risk, then no-observation Bayes risk.

    Let a=P(held)*C(false applied), b=P(applied)*C(false held), and
    q0=P(Z=1|held), q1=P(Z=1|applied). For known q,
      R(q0,q1)=min(a*q0,b*q1)+min(a*(1-q0),b*(1-q1)).
    Maximizing this concave piecewise-linear function over a rectangle
    CANNOT generally be done by evaluating only rectangle corners.
    The small LP maximizes t1+t0 with
      t1<=a*q0, t1<=b*q1,
      t0<=a*(1-q0), t0<=b*(1-q1).
    """
    prior, fp, fn = map(float, (
        prior_applied, false_applied_cost, false_held_cost
    ))
    q0, q1 = _interval(p_signal_held), _interval(p_signal_applied)
    if not (isfinite(prior) and 0 <= prior <= 1
            and isfinite(fp) and fp > 0 and isfinite(fn) and fn > 0):
        raise ValueError("invalid prior or false-authority loss")
    a, b = (1 - prior) * fp, prior * fn
    unprobed = min(a, b)
    if unprobed == 0:
        return 0.0, 0.0
    result = linprog(
        [0, 0, -1, -1],
        A_ub=[[-a, 0, 1, 0], [0, -b, 1, 0],
              [a, 0, 0, 1], [0, b, 0, 1]],
        b_ub=[0, 0, a, b],
        bounds=[q0, q1, (0, None), (0, None)],
        method="highs",
        options={"primal_feasibility_tolerance": 1e-9,
                 "dual_feasibility_tolerance": 1e-9},
    )
    if not result.success or not np.isfinite(result.fun):
        raise RuntimeError("cannot validate robust binary ACK risk LP")
    # Never credit information gain from an approximate LP solve.
    worst = float(np.clip(-result.fun + 1e-9 * max(1, a, b), 0, unprobed))
    return worst, unprobed


def robust_binary_decision_rule(
    prior_applied: float,
    p_signal_held: Sequence[float],
    p_signal_applied: Sequence[float],
    *,
    false_applied_cost: float = 1.0,
    false_held_cost: float = 1.0,
) -> tuple[str, str, float]:
    """Freeze ONE deployable deterministic observation-to-history mapping.

    Evaluate the four fixed binary decoders against worst permissible
    observation probabilities, without seeing their true distributions.
    For this rectangular independent binary model, the lowest fixed-decoder
    worst-case loss equals the linear program's maximum Bayes loss;
    numerically cross-check instead of assuming clairvoyant decoding.
    This EXPECTED error loss is not a per-decision physical safety bound.
    """
    prior, fp, fn = map(float, (
        prior_applied, false_applied_cost, false_held_cost
    ))
    held_lo, held_hi = _interval(p_signal_held)
    applied_lo, applied_hi = _interval(p_signal_applied)
    if not (isfinite(prior) and 0 <= prior <= 1
            and isfinite(fp) and fp > 0 and isfinite(fn) and fn > 0):
        raise ValueError("invalid prior or decision loss")
    a, b = (1 - prior) * fp, prior * fn
    # The two outputs are specified for Z=0 and Z=1, respectively.
    rules = [
        (b, "HELD", "HELD"),
        (a, "APPLIED", "APPLIED"),
        (a * held_hi + b * (1 - applied_lo), "HELD", "APPLIED"),
        (a * (1 - held_lo) + b * applied_hi, "APPLIED", "HELD"),
    ]
    best = min(rules, key=lambda row: row[0])
    lp_bound, _ = robust_binary_posterior_risk(
        prior, (held_lo, held_hi), (applied_lo, applied_hi),
        false_applied_cost=fp, false_held_cost=fn,
    )
    if abs(best[0] - lp_bound) > 2e-7 * max(1, a, b):
        raise RuntimeError("robust decoder/LP mismatch: refuse ACK authority")
    return best[1], best[2], max(float(best[0]), float(lp_bound))


def robust_binary_decision_rule_prior_interval(
    prior_applied_interval: Sequence[float],
    p_signal_held: Sequence[float],
    p_signal_applied: Sequence[float],
    *,
    false_applied_cost: float = 1.0,
    false_held_cost: float = 1.0,
) -> tuple[str, str, float]:
    """Minimax fixed binary decoder under BOTH prior and signal uncertainty.

    All four deterministic Z->ACK rules are enumerated BEFORE seeing Z.
    For a fixed rule the expected loss is separately affine in prior p,
    q_held and q_applied, so its maximum over the rectangular uncertainty
    set occurs at vertices. This is a conservative deterministic policy,
    not a claim about randomized minimax strategies or physical safety.
    """
    p0, p1 = _interval(prior_applied_interval)
    h0, h1 = _interval(p_signal_held)
    a0, a1 = _interval(p_signal_applied)
    fp, fn = float(false_applied_cost), float(false_held_cost)
    if not (isfinite(fp) and fp > 0 and isfinite(fn) and fn > 0):
        raise ValueError("invalid cost for false ACK authority")

    rules = [
        ("HELD", "HELD", p1 * fn),
        ("APPLIED", "APPLIED", (1 - p0) * fp),
        (
            "HELD", "APPLIED",
            max((1 - p) * fp * h1 + p * fn * (1 - a0)
                for p in (p0, p1)),
        ),
        (
            "APPLIED", "HELD",
            max((1 - p) * fp * (1 - h0) + p * fn * a1
                for p in (p0, p1)),
        ),
    ]
    zero, one, risk = min(rules, key=lambda row: row[2])
    return zero, one, float(risk)


def decide_probe_vs_readback(
    *,
    prior_applied: float,
    false_applied_cost: float,
    false_held_cost: float,
    candidates: Sequence[BinaryProbeEvidence],
    abstain_cost: float,
    trusted_readback_cost: float | None,
    prior_externally_calibrated: bool,
    readback_state_authoritative_attested: bool,
    maximum_acceptable_wrong_classification_risk: float,
    prior_applied_interval: tuple[float, float] | None = None,
) -> RobustRiskDecision:
    """Select future probe/readback/no-probe/abstention by robust expected loss.

    Returns an action selection, never a guessed ACK history. Independent
    calibration and admissibility must be authenticated by external evidence;
    booleans and free-form receipts are only declared provenance.
    """
    prior, fp, fn, abstain, limit = map(float, (
        prior_applied, false_applied_cost, false_held_cost, abstain_cost,
        maximum_acceptable_wrong_classification_risk,
    ))
    if not (isfinite(prior) and 0 <= prior <= 1
            and isfinite(fp) and fp > 0 and isfinite(fn) and fn > 0
            and isfinite(abstain) and abstain > 0
            and isfinite(limit) and limit >= 0):
        raise ValueError("invalid prior, decision costs, or risk cap")
    # A point prior may be badly wrong after a deployment shift. An optional
    # independently attested interval must contain that nominal estimate;
    # the entire interval is then used for every risk and budget decision.
    prior_lo, prior_hi = (
        _interval(prior_applied_interval)
        if prior_applied_interval is not None else (prior, prior)
    )
    if not prior_lo <= prior <= prior_hi:
        raise ValueError("nominal prior is outside declared prior interval")
    if trusted_readback_cost is not None:
        readback_cost = float(trusted_readback_cost)
        if not isfinite(readback_cost) or readback_cost <= 0:
            raise ValueError("readback must have finite strictly positive cost")
    else:
        readback_cost = None
    # Worst-case no-observation risk for ONE fixed history decision.
    # An observer cannot choose a different MAP history after learning p.
    held_no_probe_loss = prior_hi * fn
    applied_no_probe_loss = (1 - prior_lo) * fp
    baseline = min(held_no_probe_loss, applied_no_probe_loss)
    no_probe_guess = (
        "HELD" if held_no_probe_loss <= applied_no_probe_loss else "APPLIED"
    )
    choices = [
        (abstain, 0.0, "ABSTAIN", None, None, "no trusted data/action")
    ]
    if readback_cost is not None and readback_state_authoritative_attested is True:
        choices.append((readback_cost, 0.0, "READBACK", None, None,
                        "explicit authoritative commanded-target query"))
    examined = 0
    if prior_externally_calibrated is True:
        if baseline <= limit:
            choices.append((baseline, baseline, "NO_PROBE", None, None,
                            "declared prior risk permits no extra sensing"))
        names: set[str] = set()
        for evidence in candidates:
            if not isinstance(evidence, BinaryProbeEvidence):
                raise TypeError("typed binary probe evidence required")
            proposal = evidence.proposal
            if not isinstance(proposal, NativeProbeProposal):
                raise TypeError("source-replayed native command required")
            if proposal.name in names:
                raise ValueError("duplicate prospective probe name")
            names.add(proposal.name)
            q0, q1 = _interval(evidence.p_signal_held), _interval(
                evidence.p_signal_applied
            )
            if not (
                proposal.source_kinematics_verified is True
                and proposal.candidate.controller_mapping_attested is True
                and proposal.candidate.physical_admissibility_attested is True
                and evidence.independent_holdout_calibration_attested is True
                and evidence.calibrated_cost_attested is True
                and isinstance(evidence.calibration_receipt, str)
                and evidence.calibration_receipt.strip()
            ):
                continue
            cost = float(proposal.candidate.cost)
            if not isfinite(cost) or cost <= 0:
                raise ValueError("invalid calibrated probe cost")
            if prior_applied_interval is None:
                worst, _ = robust_binary_posterior_risk(
                    prior, q0, q1, false_applied_cost=fp, false_held_cost=fn,
                )
            else:
                _, _, worst = robust_binary_decision_rule_prior_interval(
                    (prior_lo, prior_hi), q0, q1,
                    false_applied_cost=fp, false_held_cost=fn,
                )
            examined += 1
            if worst > limit:
                continue
            choices.append((
                cost + worst, worst, "PROBE", proposal.name,
                proposal.native_action, "conditional calibrated binary signal"
            ))
    # If robust losses are tied, prefer not acting.
    order = {"ABSTAIN": 0, "NO_PROBE": 1, "READBACK": 2, "PROBE": 3}
    total, error, decision, name, action, reason = min(
        choices, key=lambda row: (row[0], order[row[2]], row[3] or "")
    )
    # Commit the actual observation decoding rule BEFORE seeing a signal.
    signal_zero = signal_one = None
    if decision == "PROBE":
        chosen = next(e for e in candidates if e.proposal.name == name)
        if prior_applied_interval is None:
            signal_zero, signal_one, decoder_risk = robust_binary_decision_rule(
                prior, chosen.p_signal_held, chosen.p_signal_applied,
                false_applied_cost=fp, false_held_cost=fn,
            )
        else:
            signal_zero, signal_one, decoder_risk = (
                robust_binary_decision_rule_prior_interval(
                    (prior_lo, prior_hi),
                    chosen.p_signal_held, chosen.p_signal_applied,
                    false_applied_cost=fp, false_held_cost=fn,
                )
            )
        if decoder_risk > limit + 2e-7 * max(1, fp, fn):
            raise RuntimeError("selected probe decoder exceeds risk cap")
    return RobustRiskDecision(
        decision, name, action, float(total), float(error), float(baseline),
        float(max(0, baseline - error)) if decision == "PROBE" else 0.0,
        examined, reason, signal_zero_decision=signal_zero,
        signal_one_decision=signal_one,
        no_probe_history_decision=no_probe_guess if decision == "NO_PROBE" else None,
    )
