from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .robust_repairability import RobustRepairDecision, _least_squares_in_ball


@dataclass(frozen=True)
class ProbeInformation:
    information: np.ndarray
    beta: float

    def __post_init__(self) -> None:
        V = np.asarray(self.information, dtype=float)
        if V.ndim != 2 or V.shape[0] != V.shape[1]:
            raise ValueError("information must be square")
        if np.min(np.linalg.eigvalsh(V)) <= 0:
            raise ValueError("information must be positive definite")
        if self.beta < 0:
            raise ValueError("beta must be nonnegative")
        object.__setattr__(self, "information", V)

    def directional_radius(self, direction: np.ndarray) -> float:
        x = np.asarray(direction, dtype=float)
        solved = np.linalg.solve(self.information, x)
        return float(self.beta * np.sqrt(max(0.0, x @ solved)))

    def uniform_ball_radius(self, support_radius: float) -> float:
        lam_min = float(np.min(np.linalg.eigvalsh(self.information)))
        return float(self.beta * support_radius / np.sqrt(lam_min))

    def update(self, probe: np.ndarray) -> "ProbeInformation":
        z = np.asarray(probe, dtype=float)
        if z.ndim != 1 or z.size != self.information.shape[0]:
            raise ValueError("probe dimension mismatch")
        return ProbeInformation(self.information + np.outer(z, z), self.beta)


@dataclass(frozen=True)
class ActiveRepairCertificate:
    decision: RobustRepairDecision
    support_delta: np.ndarray
    nominal_residual: float
    candidate_uncertainty: float
    set_uncertainty: float
    worst_case_residual_upper: float
    best_case_residual_lower: float


def certify_with_probe_information(
    physical_map_estimate: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    probe_information: ProbeInformation,
    certified_radius: float,
    residual_tolerance: float,
) -> ActiveRepairCertificate:
    g = np.asarray(physical_map_estimate, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    if g.ndim != 2 or d.ndim != 1 or g.shape[0] != d.size:
        raise ValueError("map/target shape mismatch")
    if g.shape[1] != probe_information.information.shape[0]:
        raise ValueError("probe information/support dimension mismatch")
    if certified_radius < 0 or residual_tolerance < 0:
        raise ValueError("radius/tolerance must be nonnegative")

    xi = _least_squares_in_ball(g, d, certified_radius)
    nominal = float(np.linalg.norm(g @ xi - d))
    candidate_uncertainty = probe_information.directional_radius(xi)
    set_uncertainty = probe_information.uniform_ball_radius(certified_radius)
    upper = nominal + candidate_uncertainty
    lower = max(0.0, nominal - set_uncertainty)

    if upper <= residual_tolerance:
        decision = RobustRepairDecision.CERTIFIED_REPAIR
    elif lower > residual_tolerance:
        decision = RobustRepairDecision.CERTIFIED_IMPOSSIBLE
    else:
        decision = RobustRepairDecision.INCONCLUSIVE

    return ActiveRepairCertificate(
        decision=decision,
        support_delta=xi,
        nominal_residual=nominal,
        candidate_uncertainty=candidate_uncertainty,
        set_uncertainty=set_uncertainty,
        worst_case_residual_upper=float(upper),
        best_case_residual_lower=float(lower),
    )


def probe_variance_reduction(
    probe_information: ProbeInformation,
    target_direction: np.ndarray,
    probe: np.ndarray,
) -> float:
    """Sherman-Morrison reduction in x^T V^-1 x after observing probe z."""

    V = probe_information.information
    x = np.asarray(target_direction, dtype=float)
    z = np.asarray(probe, dtype=float)
    if x.ndim != 1 or z.ndim != 1 or x.size != V.shape[0] or z.size != V.shape[0]:
        raise ValueError("dimension mismatch")

    Vinv_z = np.linalg.solve(V, z)
    numerator = float(x @ Vinv_z) ** 2
    denominator = 1.0 + float(z @ Vinv_z)
    return numerator / denominator


def select_candidate_directed_probe(
    probe_information: ProbeInformation,
    blocked_repair_direction: np.ndarray,
    candidate_probes: np.ndarray,
) -> tuple[np.ndarray, float]:
    candidates = np.asarray(candidate_probes, dtype=float)
    if candidates.ndim != 2 or candidates.shape[1] != probe_information.information.shape[0]:
        raise ValueError("candidate probes must have shape [n, support_dim]")
    if candidates.shape[0] == 0:
        raise ValueError("at least one candidate probe is required")

    reductions = np.asarray(
        [
            probe_variance_reduction(
                probe_information, blocked_repair_direction, probe
            )
            for probe in candidates
        ],
        dtype=float,
    )
    best = int(np.argmax(reductions))
    return candidates[best].copy(), float(reductions[best])


def weakest_observed_probe(probe_information: ProbeInformation) -> np.ndarray:
    """One-step E-optimal direction for the global impossibility bound."""

    values, vectors = np.linalg.eigh(probe_information.information)
    probe = vectors[:, int(np.argmin(values))]
    return probe / np.linalg.norm(probe)
