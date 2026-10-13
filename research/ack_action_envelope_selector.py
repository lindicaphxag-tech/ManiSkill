"""Conditional native ACK probe selection with per-action response envelopes.

This comparison only means anything when independent *fresh* physical
calibration attests each action's bounds. The source-derived candidate checks
native-action consistency; caller booleans alone do NOT prove an envelope.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

from research.ack_native_probe_source_adapter import NativeProbeProposal
from research.ack_robust_active_probe import Choice, choose_probe


@dataclass(frozen=True)
class ActionEnvelope:
    gain_min: float
    gain_max: float
    absolute_error_bound_m: float
    externally_attested_on_disjoint_calibration: bool
    calibration_source_id: str


@dataclass(frozen=True)
class NativeSelection:
    name: str | None
    native_action: tuple[float, ...] | None
    conditional_gap_m: float
    score: float
    reason: str
    attempted: int
    # Neither this model nor an attestation flag checks motion/contact safety.
    physical_safety_certified: bool = False


def choose_under_action_envelopes(
    before_xyz: Sequence[float],
    histories: Sequence[str],
    proposals: Sequence[NativeProbeProposal],
    envelopes: Mapping[str, ActionEnvelope],
    *,
    maximum_declared_cost: float,
    numerical_guard_m: float = 1e-9,
) -> NativeSelection:
    """Compare eligible actions by robust worst-pair separation per cost.

    Every candidate is constrained by the same actual native command across
    all histories and carries an action-specific, externally established
    response envelope. Never silently reuse a zero-probe envelope to
    certify a nonlinear/contact-conditioned nonzero probe.
    """
    seen: set[str] = set()
    best: tuple[float, float, str, NativeProbeProposal, Choice] | None = None
    attempted = 0
    if not isfinite(maximum_declared_cost) or maximum_declared_cost <= 0:
        raise ValueError("invalid declared cost budget")
    for proposal in proposals:
        if not isinstance(proposal, NativeProbeProposal):
            raise TypeError("native proposals must be source-constrained")
        if proposal.name in seen:
            raise ValueError("duplicate candidate name")
        seen.add(proposal.name)
        env = envelopes.get(proposal.name)
        if env is None:
            continue
        if not isinstance(env, ActionEnvelope):
            raise TypeError("typed per-action response envelope required")
        if not all(isfinite(v) for v in (
            env.gain_min, env.gain_max, env.absolute_error_bound_m
        )) or not (0 <= env.gain_min <= env.gain_max <= 1
                  and env.absolute_error_bound_m >= 0):
            raise ValueError("invalid candidate-specific bounds")
        if (env.externally_attested_on_disjoint_calibration is not True or
                not isinstance(env.calibration_source_id, str) or
                not env.calibration_source_id.strip()):
            continue
        attempted += 1
        result = choose_probe(
            before_xyz, histories, [proposal.candidate],
            alpha_min=env.gain_min, alpha_max=env.gain_max,
            model_and_sensor_error_m=env.absolute_error_bound_m,
            numerical_guard_m=numerical_guard_m,
            maximum_cost=maximum_declared_cost,
            response_envelope_independently_attested=True,
        )
        if result.candidate is None:
            continue
        value = (result.score, result.certified_gap_m, proposal.name,
                 proposal, result)
        if best is None or value[:3] > best[:3]:
            best = value
    if best is None:
        return NativeSelection(None, None, 0.0, 0.0,
            "no source-constrained candidate with a valid, separating "
            "individually attested response envelope", attempted)
    _, _, _, proposal, result = best
    return NativeSelection(
        proposal.name, proposal.native_action,
        result.certified_gap_m, result.score,
        "conditional action-specific response tubes are pairwise disjoint",
        attempted,
    )
