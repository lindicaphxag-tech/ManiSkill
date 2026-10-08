"""Budgeted, request-directed paired stochastic policy-response probing.

Purpose: replace a brittle *full Jacobian* gate for a concrete requested
perturbation h with directly measured paired counterfactual responses.

Concentration is a **statistical mean-response statement**, conditional on
an externally justified almost-sure coordinate contrast bound, IID random
seeds, correct observation/physical charts, and frozen policies. Observed
sample ranges do NOT justify the population bound. Never call this a
deterministic collision-safety certificate.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import ceil, isfinite, log, sqrt
from typing import Callable, Mapping, Sequence

import numpy as np


class ResponseProbeDecision(str, Enum):
    STATISTICAL_MEAN_SIMILAR = "STATISTICAL_MEAN_SIMILAR"
    STATISTICAL_MEAN_DISTINCT = "STATISTICAL_MEAN_DISTINCT"
    ABSTAIN_BUDGET_EXHAUSTED = "ABSTAIN_BUDGET_EXHAUSTED"
    REJECT_UNSUPPORTED_ASSUMPTIONS = "REJECT_UNSUPPORTED_ASSUMPTIONS"


@dataclass(frozen=True)
class PairedProbeRound:
    seed: int
    query_count: int
    response_contrast: tuple[float, ...]
    mean_contrast_norm: float
    confidence_radius: float
    mean_gap_lower: float
    mean_gap_upper: float


@dataclass(frozen=True)
class PairedProbeResult:
    decision: ResponseProbeDecision
    seeds_used: tuple[int, ...]
    total_policy_queries: int
    max_policy_queries: int
    confidence_level_if_assumptions_hold: float | None
    response_tolerance: float
    final_mean_gap_lower: float | None
    final_mean_gap_upper: float | None
    rounds: tuple[PairedProbeRound, ...]
    deterministic_safety_guarantee: bool = False
    externally_validated: bool = False
    explanation: str = ""


def _unsupported(
    *,
    tolerance: float,
    budget: int,
    reason: str,
    rounds: Sequence[PairedProbeRound] = (),
) -> PairedProbeResult:
    return PairedProbeResult(
        ResponseProbeDecision.REJECT_UNSUPPORTED_ASSUMPTIONS,
        tuple(r.seed for r in rounds), 4 * len(rounds), budget, None,
        float(tolerance), None, None, tuple(rounds), False, False, reason,
    )


def probe_pairwise_mean_response(
    sample_four_actions: Callable[[int, np.ndarray], Mapping[str, Sequence[float]]],
    physical_request: Sequence[float],
    *,
    prespecified_iid_seed_draws: Sequence[int],
    hard_coordinate_contrast_bound: float | None,
    max_policy_queries: int,
    response_tolerance: float,
    alpha: float = 0.1,
    physical_charts_aligned: bool,
    controller_authority_valid: bool,
    population_bound_independently_justified: bool,
    iid_seed_draw_design_attested: bool,
) -> PairedProbeResult:
    """Sequentially sample four actions per seed; stop only on strong evidence.

    For seed z, one round measures:
      X(z) = [pi_A(h,z)-pi_A(0,z)] - [pi_B(h,z)-pi_B(0,z)].
    All FOUR actions use the same state and per-policy matched RNG seed.
    The objective is ||E_z X(z)||, NOT E_z||X(z)||.

    Assuming IID z, frozen policies, and all population X_j in [-B,+B],
    Hoeffding + union bound across d coordinates and all t<=N gives:
      ||E X - sample_mean_t||_2
           <= sqrt(d)*B*sqrt(2*ln(2*d*N/alpha)/t)
    simultaneously for all t<=N with probability >=1-alpha.
    This is a conservative finite-horizon confidence sequence; it needs
    an EXTERNAL hard bound B valid for all possible RNG draws, not a
    fitted range, three-replicate q95, or output clipping inferred from
    observed samples.

    Bounds concern the stochastic first-action *mean* response at one
    physical request. They do NOT guarantee one rollout is safe, infer
    a full Jacobian, certify cross-state transfer, or bound collisions.
    """
    h = np.asarray(physical_request, dtype=float)
    budget = int(max_policy_queries) if isinstance(max_policy_queries, int) else 0
    if budget < 4 or budget % 4:
        raise ValueError("policy query budget must be a positive multiple of four")
    if not isfinite(response_tolerance) or response_tolerance < 0:
        raise ValueError("response tolerance must be finite and nonnegative")
    if not isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between 0 and 1")
    rounds: list[PairedProbeRound] = []
    if h.ndim != 1 or not h.size or not np.isfinite(h).all():
        return _unsupported(tolerance=response_tolerance, budget=budget,
                            reason="invalid physical request")
    if (
        not physical_charts_aligned
        or not controller_authority_valid
        or not population_bound_independently_justified
        or not iid_seed_draw_design_attested
        or hard_coordinate_contrast_bound is None
        or not isfinite(float(hard_coordinate_contrast_bound))
        or float(hard_coordinate_contrast_bound) <= 0
    ):
        return _unsupported(
            tolerance=response_tolerance, budget=budget,
            reason="missing physical chart/authority, population bound or IID seed evidence",
        )
    N = budget // 4
    seeds = tuple(prespecified_iid_seed_draws)
    if (
        len(seeds) != N or len(set(seeds)) != len(seeds)
        or any(not isinstance(s, int) or isinstance(s, bool) or s < 0 for s in seeds)
    ):
        raise ValueError("freeze exactly N distinct nonnegative IID-drawn seeds before probing")
    B = float(hard_coordinate_contrast_bound)
    center = None
    dimension = None
    delta = None
    for t, seed in enumerate(seeds, 1):
        raw = sample_four_actions(seed, h.copy())
        if not isinstance(raw, Mapping) or set(raw) != {
            "baseline_a", "perturbed_a", "baseline_b", "perturbed_b"
        }:
            return _unsupported(
                tolerance=response_tolerance, budget=budget,
                reason="four paired actions or provenance keys missing",
                rounds=rounds,
            )
        arrays = [np.asarray(raw[key], dtype=float) for key in (
            "baseline_a", "perturbed_a", "baseline_b", "perturbed_b"
        )]
        if any(a.ndim != 1 or a.size == 0 for a in arrays):
            return _unsupported(tolerance=response_tolerance, budget=budget,
                                reason="actions must be finite one-dimensional vectors",
                                rounds=rounds)
        if len({a.shape for a in arrays}) != 1 or any(not np.isfinite(a).all() for a in arrays):
            return _unsupported(tolerance=response_tolerance, budget=budget,
                                reason="action dimensions differ or contain nonfinite values",
                                rounds=rounds)
        if dimension is None:
            dimension = arrays[0].size
            center = np.zeros(dimension, dtype=float)
        elif arrays[0].size != dimension:
            return _unsupported(tolerance=response_tolerance, budget=budget,
                                reason="physical action chart dimension changed",
                                rounds=rounds)
        contrast = (arrays[1] - arrays[0]) - (arrays[3] - arrays[2])
        # Observed violations invalidate any claimed population support,
        # but no amount of observed compliance *proves* a population bound.
        if not np.isfinite(contrast).all() or np.max(np.abs(contrast)) > B:
            return _unsupported(
                tolerance=response_tolerance, budget=budget,
                reason="observed contrast exceeds attested population hard bound",
                rounds=rounds,
            )
        center += (contrast - center) / t
        if not np.isfinite(center).all():
            return _unsupported(tolerance=response_tolerance, budget=budget,
                                reason="floating overflow in mean contrast",
                                rounds=rounds)
        radius = sqrt(dimension) * B * sqrt(2 * log(2 * dimension * N / alpha) / t)
        norm = float(np.linalg.norm(center))
        low, high = max(0.0, norm-radius), norm+radius
        round_result = PairedProbeRound(
            seed, 4*t, tuple(float(v) for v in contrast),
            norm, radius, low, high,
        )
        rounds.append(round_result)
        if high <= response_tolerance:
            decision = ResponseProbeDecision.STATISTICAL_MEAN_SIMILAR
        elif low > response_tolerance:
            decision = ResponseProbeDecision.STATISTICAL_MEAN_DISTINCT
        else:
            continue
        return PairedProbeResult(
            decision, tuple(s for s in seeds[:t]), 4*t, budget,
            1-alpha, response_tolerance, low, high, tuple(rounds),
            False, False,
            "Conditional anytime Hoeffding mean-response decision; not one-action safety",
        )
    last = rounds[-1]
    return PairedProbeResult(
        ResponseProbeDecision.ABSTAIN_BUDGET_EXHAUSTED,
        seeds, budget, budget, 1-alpha, response_tolerance,
        last.mean_gap_lower, last.mean_gap_upper, tuple(rounds),
        False, False,
        "No valid mean-response decision within the frozen query budget",
    )
