from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .core import Decision, _project_target_to_image_ball


@dataclass(frozen=True)
class ProbeDesign:
    """Ellipsoidal support-space uncertainty design.

    Assumption:
      ||(G_true-G_hat) x||_2 <= beta * sqrt(x^T V^{-1} x)
    for every support direction x of interest.
    """

    information: np.ndarray
    beta: float

    def __post_init__(self) -> None:
        V = np.asarray(self.information, dtype=float)
        if V.ndim != 2 or V.shape[0] != V.shape[1]:
            raise ValueError("information must be square")
        if self.beta < 0:
            raise ValueError("beta must be nonnegative")
        if np.min(np.linalg.eigvalsh(V)) <= 0:
            raise ValueError("information must be positive definite")
        object.__setattr__(self, "information", V)

    def directional_radius(self, x: np.ndarray) -> float:
        x = np.asarray(x, dtype=float)
        if x.ndim != 1 or x.size != self.information.shape[0]:
            raise ValueError("direction dimension mismatch")
        solved = np.linalg.solve(self.information, x)
        return float(self.beta * np.sqrt(max(0.0, x @ solved)))

    def uniform_radius_on_ball(self, radius: float) -> float:
        if radius < 0:
            raise ValueError("radius must be nonnegative")
        lam_min = float(np.min(np.linalg.eigvalsh(self.information)))
        return float(self.beta * radius / np.sqrt(lam_min))

    def after_probe(self, z: np.ndarray) -> "ProbeDesign":
        z = np.asarray(z, dtype=float)
        if z.ndim != 1 or z.size != self.information.shape[0]:
            raise ValueError("probe dimension mismatch")
        return ProbeDesign(self.information + np.outer(z, z), self.beta)


@dataclass(frozen=True)
class DesignCertificate:
    decision: Decision
    support_delta: np.ndarray
    nominal_residual: float
    candidate_uncertainty: float
    uniform_set_uncertainty: float
    worst_case_residual_upper: float
    best_case_residual_lower: float


def certify_with_design(
    G_hat: np.ndarray,
    target: np.ndarray,
    *,
    design: ProbeDesign,
    certified_radius: float,
    tolerance: float,
) -> DesignCertificate:
    G = np.asarray(G_hat, dtype=float)
    d = np.asarray(target, dtype=float)
    if G.ndim != 2 or d.ndim != 1 or G.shape[0] != d.size:
        raise ValueError("G/target shape mismatch")
    if G.shape[1] != design.information.shape[0]:
        raise ValueError("design/support dimension mismatch")
    if certified_radius < 0 or tolerance < 0:
        raise ValueError("radius/tolerance must be nonnegative")

    x = _project_target_to_image_ball(G, d, certified_radius)
    nominal = float(np.linalg.norm(G @ x - d))
    candidate_u = design.directional_radius(x)
    uniform_u = design.uniform_radius_on_ball(certified_radius)
    upper = nominal + candidate_u
    lower = max(0.0, nominal - uniform_u)

    if upper <= tolerance:
        decision = Decision.CERTIFIED_REPAIR
    elif lower > tolerance:
        decision = Decision.CERTIFIED_IMPOSSIBLE
    else:
        decision = Decision.INCONCLUSIVE

    return DesignCertificate(
        decision=decision,
        support_delta=x,
        nominal_residual=nominal,
        candidate_uncertainty=candidate_u,
        uniform_set_uncertainty=uniform_u,
        worst_case_residual_upper=float(upper),
        best_case_residual_lower=float(lower),
    )


def variance_reduction_for_direction(
    design: ProbeDesign,
    target_direction: np.ndarray,
    probe: np.ndarray,
) -> float:
    """Exact Sherman-Morrison reduction in x^T V^{-1} x after one probe."""

    x = np.asarray(target_direction, dtype=float)
    z = np.asarray(probe, dtype=float)
    V = design.information
    if x.ndim != 1 or z.ndim != 1 or x.size != V.shape[0] or z.size != V.shape[0]:
        raise ValueError("dimension mismatch")

    Vinv_x = np.linalg.solve(V, x)
    Vinv_z = np.linalg.solve(V, z)
    numerator = float(x @ Vinv_z) ** 2
    denominator = 1.0 + float(z @ Vinv_z)
    return numerator / denominator


def select_candidate_directed_probe(
    design: ProbeDesign,
    target_direction: np.ndarray,
    candidates: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Choose the supplied probe that most shrinks uncertainty on one repair."""

    cand = np.asarray(candidates, dtype=float)
    if cand.ndim != 2 or cand.shape[1] != design.information.shape[0]:
        raise ValueError("candidates must have shape [n, support_dim]")
    if cand.shape[0] == 0:
        raise ValueError("at least one candidate is required")

    reductions = np.asarray(
        [
            variance_reduction_for_direction(design, target_direction, z)
            for z in cand
        ]
    )
    i = int(np.argmax(reductions))
    return cand[i].copy(), float(reductions[i])


def weakest_observed_probe(design: ProbeDesign) -> np.ndarray:
    """E-optimal one-step direction: probe the least-observed support axis."""

    values, vectors = np.linalg.eigh(design.information)
    z = vectors[:, int(np.argmin(values))]
    return z / np.linalg.norm(z)
