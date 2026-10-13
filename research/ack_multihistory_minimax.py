"""Exact finite-history, binary-signal robust ACK decision rules.

Mathematical solver only; not evidence of physically calibrated likelihoods,
robot safety, task-success improvement, or upstream robotics adoption.

For frozen deterministic decoder g:{0,1}->H, uncertain signal rates q_i
in [lo_i,hi_i], bounded-simplex prior p, and true-vs-selected loss C:
  sup_q R(g,p,q) = sum_i p_i [C[i,g(0)] +
    (hi_i if C[i,g(1)]>=C[i,g(0)] else lo_i) *
    (C[i,g(1)]-C[i,g(0)])].
The remaining sup_p is exact greedy allocation of a unit probability mass
over bounded simplex coordinates, in descending order of per-history loss.
Enumerate |H|^2 fixed decoders; no runtime optimization dependency.
Expected loss is not a per-decision safety certificate.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


def _interval(v: Sequence[float]) -> tuple[float, float]:
    if len(v) != 2:
        raise ValueError("expected lower/upper bounds")
    a, b = float(v[0]), float(v[1])
    if not (isfinite(a) and isfinite(b) and 0 <= a <= b <= 1):
        raise ValueError("invalid probability interval")
    return a, b


def _prior_worst_case(loss: Sequence[float], bounds: Sequence[tuple[float, float]]) -> float:
    """Solve max w.p subject to lower<=p<=upper and sum(p)=1 exactly."""
    lo_sum = sum(a for a, _ in bounds)
    hi_sum = sum(b for _, b in bounds)
    if lo_sum > 1 + 1e-10 or hi_sum < 1 - 1e-10:
        raise ValueError("bounded prior simplex is empty")
    left = 1.0 - lo_sum
    out = sum(float(w) * lo for w, (lo, _) in zip(loss, bounds))
    for i in sorted(range(len(loss)), key=lambda j: (-loss[j], j)):
        amount = min(max(0.0, left), bounds[i][1] - bounds[i][0])
        out += amount * float(loss[i])
        left -= amount
    if left > 2e-9:
        raise ValueError("bounded prior simplex is numerically infeasible")
    return float(out)


@dataclass(frozen=True)
class RobustBinaryProbe:
    name: str
    signal_one_by_history: Mapping[str, tuple[float, float]]
    declared_cost: float
    # External validation is required; booleans/digests cannot authenticate it.
    source_replayed: bool
    independent_calibration_attested: bool
    cost_calibration_attested: bool
    external_evidence_id: str


@dataclass(frozen=True)
class MultiHistoryACKDecision:
    mode: str
    probe_name: str | None
    decoder_on_zero: str | None
    decoder_on_one: str | None
    worst_case_error_loss: float
    total_declared_cost: float
    no_probe_risk: float
    examined_probes: int
    physical_safety_certified: bool = False


def choose_minimax_ack_decision(
    histories: Sequence[str],
    prior_bounds: Mapping[str, Sequence[float]],
    loss_by_true_history: Mapping[str, Mapping[str, float]],
    probes: Sequence[RobustBinaryProbe],
    *,
    abstain_cost: float,
    trusted_readback_cost: float | None,
    risk_cap: float,
    independently_calibrated_prior: bool,
    authoritative_readback_attested: bool,
) -> MultiHistoryACKDecision:
    """Freeze a decision rule BEFORE the observation Z arrives.

    All losses must share units with actuation, readback and abstention costs.
    Caller-attested booleans do NOT authenticate any physical source.
    Before deployment, verify separate original reset cohorts, full-family
    simultaneous calibration, native action replay and actual physical costs.
    """
    hs = tuple(histories)
    if len(hs) < 2 or len(set(hs)) != len(hs) or any(
        not isinstance(h, str) or not h for h in hs
    ):
        raise ValueError("at least two distinct nonempty histories required")
    if set(prior_bounds) != set(hs) or set(loss_by_true_history) != set(hs):
        raise ValueError("history/prior/loss identity mismatch")
    priors = [_interval(prior_bounds[h]) for h in hs]
    if not (sum(p[0] for p in priors) <= 1 + 1e-10 <=
            sum(p[1] for p in priors) + 1e-10):
        raise ValueError("bounded prior simplex is empty")
    matrix = []
    for h in hs:
        row = loss_by_true_history[h]
        if set(row) != set(hs):
            raise ValueError("cost matrix must define each true/predicted history")
        numbers = [float(row[d]) for d in hs]
        if any(not isfinite(x) or x < 0 for x in numbers):
            raise ValueError("loss matrix must be finite and nonnegative")
        matrix.append(numbers)
    if any(matrix[i][i] != 0 for i in range(len(hs))):
        raise ValueError("correct-history classification must have zero loss")
    abstain = float(abstain_cost)
    cap = float(risk_cap)
    if not (isfinite(abstain) and abstain > 0 and isfinite(cap) and cap >= 0):
        raise ValueError("invalid abstention cost or classification risk cap")
    if trusted_readback_cost is not None and not (
        isfinite(float(trusted_readback_cost)) and float(trusted_readback_cost) > 0
    ):
        raise ValueError("invalid readback cost")
    baseline = min(
        (_prior_worst_case([matrix[i][j] for i in range(len(hs))], priors), j)
        for j in range(len(hs))
    )
    no_probe_risk, baseline_idx = baseline
    # Ties prefer abstention, no action, readback, then physical probe.
    options = [(abstain, 0, "ABSTAIN", None, None, None, 0.0)]
    if trusted_readback_cost is not None and authoritative_readback_attested is True:
        options.append((float(trusted_readback_cost), 2, "READBACK",
                        None, None, None, 0.0))
    examined = 0
    if independently_calibrated_prior is True:
        if no_probe_risk <= cap:
            options.append((no_probe_risk, 1, "NO_PROBE", None,
                            hs[baseline_idx], hs[baseline_idx], no_probe_risk))
        seen = set()
        for probe in probes:
            if not isinstance(probe, RobustBinaryProbe):
                raise TypeError("typed probe evidence required")
            if not isinstance(probe.name, str) or not probe.name or probe.name in seen:
                raise ValueError("duplicate or empty prospective candidate name")
            seen.add(probe.name)
            if set(probe.signal_one_by_history) != set(hs):
                raise ValueError("conditional signal intervals must cover all histories")
            q = [_interval(probe.signal_one_by_history[h]) for h in hs]
            if not (probe.source_replayed is True
                    and probe.independent_calibration_attested is True
                    and probe.cost_calibration_attested is True
                    and isinstance(probe.external_evidence_id, str)
                    and probe.external_evidence_id.strip()):
                continue
            cost = float(probe.declared_cost)
            if not isfinite(cost) or cost <= 0:
                raise ValueError("nonpositive or nonfinite declared action cost")
            examined += 1
            best = None
            for z0 in range(len(hs)):
                for z1 in range(len(hs)):
                    per_history = [
                        matrix[i][z0] +
                        (q[i][1] if matrix[i][z1] >= matrix[i][z0] else q[i][0]) *
                        (matrix[i][z1] - matrix[i][z0])
                        for i in range(len(hs))
                    ]
                    worst = _prior_worst_case(per_history, priors)
                    if best is None or (worst, z0, z1) < best:
                        best = (worst, z0, z1)
            assert best is not None
            risk, z0, z1 = best
            if risk <= cap:
                options.append((cost + risk, 3, "PROBE", probe.name,
                                hs[z0], hs[z1], risk))
    total, _, mode, name, z0, z1, risk = min(
        options, key=lambda row: (row[0], row[1], row[3] or "")
    )
    return MultiHistoryACKDecision(
        mode, name, z0, z1, float(risk), float(total),
        float(no_probe_risk), examined
    )
