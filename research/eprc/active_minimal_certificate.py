from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .certificate_directed_probing import (
    ActiveRepairCertificate,
    ProbeInformation,
    certify_with_probe_information,
)
from .robust_repairability import RobustRepairDecision


@dataclass(frozen=True)
class ProbePlanStep:
    probe: np.ndarray
    decision_after_probe: RobustRepairDecision
    worst_case_residual_upper: float
    best_case_residual_lower: float
    ambiguity_to_decision: float


@dataclass(frozen=True)
class MinimalCertificatePlan:
    initial_certificate: ActiveRepairCertificate
    final_certificate: ActiveRepairCertificate
    steps: tuple[ProbePlanStep, ...]
    exhausted_budget: bool
    symmetric_policy_evaluations: int


def _decision_ambiguity(cert: ActiveRepairCertificate, tolerance: float) -> float:
    """Distance to the nearest valid certificate boundary.

    For an inconclusive certificate, either the robust upper bound must fall to
    <= tolerance (repair) or the robust lower bound must rise to > tolerance
    (impossible). Smaller is therefore better.
    """

    if cert.decision is not RobustRepairDecision.INCONCLUSIVE:
        return 0.0
    repair_gap = max(0.0, cert.worst_case_residual_upper - tolerance)
    impossible_gap = max(0.0, tolerance - cert.best_case_residual_lower)
    return float(min(repair_gap, impossible_gap))


def _normalize_candidates(candidate_probes: np.ndarray) -> np.ndarray:
    z = np.asarray(candidate_probes, dtype=float)
    if z.ndim != 2 or z.shape[0] == 0:
        raise ValueError("candidate_probes must have shape [n, support_dim]")
    norms = np.linalg.norm(z, axis=1)
    if np.any(norms <= 0):
        raise ValueError("candidate probes must be nonzero")
    return z / norms[:, None]


def plan_minimal_certificate_probes(
    physical_map_estimate: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    probe_information: ProbeInformation,
    certified_radius: float,
    residual_tolerance: float,
    candidate_probes: np.ndarray,
    max_additional_probes: int,
) -> MinimalCertificatePlan:
    """Greedily plan only the probes needed to resolve one repair request.

    This is deliberately *request-conditioned*. It does not try to identify the
    full Jacobian uniformly. At each step it simulates the information update
    from each admissible probe and chooses the one that gets closest to either a
    robust REPAIR or robust IMPOSSIBLE certificate.

    A symmetric physical intervention (+eps z, -eps z) costs two black-box
    policy evaluations; the returned accounting is incremental and excludes any
    baseline query already available to the caller.
    """

    if max_additional_probes < 0:
        raise ValueError("max_additional_probes must be nonnegative")

    g = np.asarray(physical_map_estimate, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    candidates = _normalize_candidates(candidate_probes)
    if candidates.shape[1] != probe_information.information.shape[0]:
        raise ValueError("candidate probe dimension mismatch")

    current_info = probe_information
    initial = certify_with_probe_information(
        g,
        d,
        probe_information=current_info,
        certified_radius=certified_radius,
        residual_tolerance=residual_tolerance,
    )
    current = initial
    steps: list[ProbePlanStep] = []

    for _ in range(max_additional_probes):
        if current.decision is not RobustRepairDecision.INCONCLUSIVE:
            break

        scored = []
        for idx, probe in enumerate(candidates):
            next_info = current_info.update(probe)
            cert = certify_with_probe_information(
                g,
                d,
                probe_information=next_info,
                certified_radius=certified_radius,
                residual_tolerance=residual_tolerance,
            )
            ambiguity = _decision_ambiguity(cert, residual_tolerance)

            # Lexicographic preference:
            # 1) a probe that immediately certifies;
            # 2) smaller distance to either certificate boundary;
            # 3) narrower robust uncertainty band;
            # 4) deterministic candidate order.
            certified_rank = 0 if cert.decision is not RobustRepairDecision.INCONCLUSIVE else 1
            band_width = cert.worst_case_residual_upper - cert.best_case_residual_lower
            scored.append(
                (
                    certified_rank,
                    ambiguity,
                    band_width,
                    idx,
                    probe,
                    next_info,
                    cert,
                )
            )

        _, ambiguity, _, _, probe, current_info, current = min(
            scored, key=lambda x: (x[0], x[1], x[2], x[3])
        )
        steps.append(
            ProbePlanStep(
                probe=probe.copy(),
                decision_after_probe=current.decision,
                worst_case_residual_upper=current.worst_case_residual_upper,
                best_case_residual_lower=current.best_case_residual_lower,
                ambiguity_to_decision=float(ambiguity),
            )
        )

    exhausted = (
        current.decision is RobustRepairDecision.INCONCLUSIVE
        and len(steps) >= max_additional_probes
    )
    return MinimalCertificatePlan(
        initial_certificate=initial,
        final_certificate=current,
        steps=tuple(steps),
        exhausted_budget=bool(exhausted),
        symmetric_policy_evaluations=2 * len(steps),
    )
