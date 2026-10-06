from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .linear_authority import LinearActionAuthority


class RobustRepairDecision(str, Enum):
    CERTIFIED_REPAIR = "CERTIFIED_REPAIR"
    CERTIFIED_IMPOSSIBLE = "CERTIFIED_IMPOSSIBLE"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class PhysicalMapUncertainty:
    """Operator-norm uncertainty for G = C J.

    Assumes ||G_true - G_hat||_2 <= epsilon_g.
    """

    epsilon_g: float

    def __post_init__(self) -> None:
        if self.epsilon_g < 0:
            raise ValueError("epsilon_g must be non-negative")


@dataclass(frozen=True)
class FactorUncertainty:
    """Separate operator-norm uncertainty bounds for C and J."""

    epsilon_c: float
    epsilon_j: float

    def __post_init__(self) -> None:
        if self.epsilon_c < 0 or self.epsilon_j < 0:
            raise ValueError("uncertainty bounds must be non-negative")


@dataclass(frozen=True)
class RobustAuthorityRadius:
    trust_radius: float
    authority_radius: float
    certified_radius: float
    limiting_constraint: int | None


@dataclass(frozen=True)
class RobustRepairCertificate:
    decision: RobustRepairDecision
    support_delta: np.ndarray
    nominal_physical_repair: np.ndarray
    nominal_residual_norm: float
    worst_case_residual_upper: float
    best_case_residual_lower: float
    physical_map_uncertainty: float
    robust_certified_radius: float
    reason: str


def propagate_physical_map_uncertainty(
    action_to_physical_jacobian: np.ndarray,
    action_support_jacobian: np.ndarray,
    factor_uncertainty: FactorUncertainty,
) -> PhysicalMapUncertainty:
    """Conservative product perturbation bound.

    For G = C J, with ||dC|| <= eps_c and ||dJ|| <= eps_j,

      ||(C+dC)(J+dJ) - CJ||
      <= ||C|| eps_j + ||J|| eps_c + eps_c eps_j.
    """

    c = np.asarray(action_to_physical_jacobian, dtype=float)
    j = np.asarray(action_support_jacobian, dtype=float)
    if c.ndim != 2 or j.ndim != 2 or c.shape[1] != j.shape[0]:
        raise ValueError("C and J must be composable matrices")

    eps = (
        np.linalg.norm(c, ord=2) * factor_uncertainty.epsilon_j
        + np.linalg.norm(j, ord=2) * factor_uncertainty.epsilon_c
        + factor_uncertainty.epsilon_c * factor_uncertainty.epsilon_j
    )
    return PhysicalMapUncertainty(float(eps))


def empirical_operator_envelope(
    physical_map_replicates: np.ndarray,
    *,
    quantile: float = 1.0,
) -> tuple[np.ndarray, PhysicalMapUncertainty]:
    """Build an empirical operator-norm envelope from repeated probes.

    This is an empirical envelope, not a formal statistical confidence interval.
    quantile=1.0 returns the observed max-distance envelope.
    """

    reps = np.asarray(physical_map_replicates, dtype=float)
    if reps.ndim != 3 or reps.shape[0] == 0:
        raise ValueError("replicates must have shape [n, physical_dim, support_dim]")
    if not 0 < quantile <= 1:
        raise ValueError("quantile must lie in (0, 1]")

    center = np.mean(reps, axis=0)
    radii = np.asarray(
        [np.linalg.norm(rep - center, ord=2) for rep in reps], dtype=float
    )
    eps = float(np.quantile(radii, quantile, method="higher"))
    return center, PhysicalMapUncertainty(eps)


def robust_support_radius_linear_authority(
    nominal_action: np.ndarray,
    action_support_jacobian: np.ndarray,
    authority: LinearActionAuthority,
    *,
    epsilon_j: float,
    trust_radius: float,
    atol: float = 1e-12,
) -> RobustAuthorityRadius:
    """Support-space radius safe for every J within an operator-norm ball.

    For each authority row H_i,

      H_i (a0 + J_true xi)
      <= H_i a0
         + (||H_i J_hat|| + ||H_i|| epsilon_j) ||xi||.

    Therefore the returned radius guarantees H(a0 + J_true xi) <= h for all
    admissible J_true.
    """

    a0 = np.asarray(nominal_action, dtype=float)
    j = np.asarray(action_support_jacobian, dtype=float)
    if epsilon_j < 0 or trust_radius < 0:
        raise ValueError("epsilon_j and trust_radius must be non-negative")
    if a0.ndim != 1 or j.ndim != 2 or j.shape[0] != a0.size:
        raise ValueError("action/J dimensions differ")
    if authority.H.shape[1] != a0.size:
        raise ValueError("authority/action dimensions differ")

    margins = authority.h - authority.H @ a0
    if np.any(margins < -atol):
        return RobustAuthorityRadius(
            trust_radius=float(trust_radius),
            authority_radius=float("-inf"),
            certified_radius=float("-inf"),
            limiting_constraint=int(np.argmin(margins)),
        )

    nominal_row = np.linalg.norm(authority.H @ j, axis=1)
    uncertainty_row = np.linalg.norm(authority.H, axis=1) * float(epsilon_j)
    worst_row = nominal_row + uncertainty_row

    ratios = np.full(margins.shape, np.inf, dtype=float)
    active = worst_row > atol
    ratios[active] = np.maximum(margins[active], 0.0) / worst_row[active]

    limiting = int(np.argmin(ratios)) if np.any(np.isfinite(ratios)) else None
    authority_radius = float(np.min(ratios)) if ratios.size else float("inf")
    return RobustAuthorityRadius(
        trust_radius=float(trust_radius),
        authority_radius=authority_radius,
        certified_radius=float(min(trust_radius, authority_radius)),
        limiting_constraint=limiting,
    )


def _least_squares_in_ball(
    g: np.ndarray,
    target: np.ndarray,
    radius: float,
    *,
    atol: float = 1e-12,
) -> np.ndarray:
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if radius == 0 or g.shape[1] == 0:
        return np.zeros(g.shape[1], dtype=float)

    u, s, vt = np.linalg.svd(g, full_matrices=False)
    coeff = u.T @ target
    nz = s > atol
    inv = np.zeros_like(s)
    inv[nz] = 1.0 / s[nz]
    xi = vt.T @ (inv * coeff)
    if np.linalg.norm(xi) <= radius + atol:
        return xi

    def point(lam: float) -> np.ndarray:
        w = np.zeros_like(s)
        w[nz] = s[nz] / (s[nz] ** 2 + lam)
        return vt.T @ (w * coeff)

    lo, hi = 0.0, 1.0
    while np.linalg.norm(point(hi)) > radius:
        hi *= 2.0
        if hi > 1e18:
            raise RuntimeError("failed to bracket trust-region multiplier")

    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if np.linalg.norm(point(mid)) > radius:
            lo = mid
        else:
            hi = mid
    return point(hi)


def robust_repair_certificate(
    physical_map_estimate: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    physical_map_uncertainty: PhysicalMapUncertainty,
    certified_radius: float,
    residual_tolerance: float,
) -> RobustRepairCertificate:
    """Three-way worst-case repairability certificate.

    Let K_hat = {G_hat xi : ||xi|| <= r} and assume
    ||G_true - G_hat||_2 <= eps.

    A candidate xi is CERTIFIED_REPAIR when

      ||G_hat xi - d|| + eps ||xi|| <= tau,

    which upper-bounds its residual for every admissible G_true.

    Let dist_hat = dist(d, K_hat). Since every admissible K_true is within
    Hausdorff distance at most eps*r from K_hat, repair is
    CERTIFIED_IMPOSSIBLE when

      dist_hat - eps*r > tau.

    Otherwise the evidence is INCONCLUSIVE.
    """

    g = np.asarray(physical_map_estimate, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    eps = float(physical_map_uncertainty.epsilon_g)

    if g.ndim != 2 or d.ndim != 1 or g.shape[0] != d.size:
        raise ValueError("physical map / target dimensions differ")
    if certified_radius < 0:
        return RobustRepairCertificate(
            decision=RobustRepairDecision.CERTIFIED_IMPOSSIBLE,
            support_delta=np.zeros(g.shape[1], dtype=float),
            nominal_physical_repair=np.zeros_like(d),
            nominal_residual_norm=float(np.linalg.norm(d)),
            worst_case_residual_upper=float("inf"),
            best_case_residual_lower=float("inf"),
            physical_map_uncertainty=eps,
            robust_certified_radius=float(certified_radius),
            reason="nominal action is outside certified authority",
        )
    if residual_tolerance < 0:
        raise ValueError("residual_tolerance must be non-negative")

    xi = _least_squares_in_ball(g, d, certified_radius)
    nominal_repair = g @ xi
    nominal_residual = float(np.linalg.norm(nominal_repair - d))
    worst_upper = nominal_residual + eps * float(np.linalg.norm(xi))
    best_lower = max(0.0, nominal_residual - eps * certified_radius)

    if worst_upper <= residual_tolerance:
        decision = RobustRepairDecision.CERTIFIED_REPAIR
        reason = "one policy-consistent repair satisfies the residual tolerance for every admissible local physical map"
    elif best_lower > residual_tolerance:
        decision = RobustRepairDecision.CERTIFIED_IMPOSSIBLE
        reason = "even the most favorable admissible local physical map cannot place the target inside the residual tolerance"
    else:
        decision = RobustRepairDecision.INCONCLUSIVE
        reason = "model uncertainty overlaps the repairability boundary; collect more probes or replan"

    return RobustRepairCertificate(
        decision=decision,
        support_delta=xi,
        nominal_physical_repair=nominal_repair,
        nominal_residual_norm=nominal_residual,
        worst_case_residual_upper=float(worst_upper),
        best_case_residual_lower=float(best_lower),
        physical_map_uncertainty=eps,
        robust_certified_radius=float(certified_radius),
        reason=reason,
    )
