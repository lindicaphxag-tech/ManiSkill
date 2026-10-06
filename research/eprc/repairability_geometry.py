from __future__ import annotations

from dataclasses import dataclass
from math import inf

import numpy as np


@dataclass(frozen=True)
class RepairabilityRadius:
    trust_radius: float
    authority_radius: float
    certified_radius: float
    limiting_action_dim: int | None


@dataclass(frozen=True)
class RepairSynthesis:
    latent_repair: np.ndarray
    physical_repair: np.ndarray
    residual: np.ndarray
    residual_norm: float
    certified_radius: float
    repairable: bool
    separation_normal: np.ndarray
    separation_margin: float
    reason: str


def certified_support_radius(
    nominal_action: np.ndarray,
    action_support_jacobian: np.ndarray,
    action_low: np.ndarray,
    action_high: np.ndarray,
    *,
    trust_radius: float,
    atol: float = 1e-12,
) -> RepairabilityRadius:
    """Largest L2 support-space ball guaranteed to remain inside action authority.

    For ||xi||_2 <= r, row-wise Cauchy-Schwarz gives
        |J_i xi| <= ||J_i||_2 r.
    Therefore r <= margin_i / ||J_i||_2 is sufficient for every action bound.
    """

    a = np.asarray(nominal_action, dtype=float)
    j = np.asarray(action_support_jacobian, dtype=float)
    lo = np.asarray(action_low, dtype=float)
    hi = np.asarray(action_high, dtype=float)

    if j.ndim != 2:
        raise ValueError("action_support_jacobian must be 2D")
    if a.ndim != 1 or lo.shape != a.shape or hi.shape != a.shape:
        raise ValueError("action vectors must be 1D and shape-aligned")
    if j.shape[0] != a.size:
        raise ValueError("Jacobian action dimension does not match nominal action")
    if np.any(lo > hi):
        raise ValueError("action_low must not exceed action_high")
    if np.any(a < lo - atol) or np.any(a > hi + atol):
        return RepairabilityRadius(
            trust_radius=float(trust_radius),
            authority_radius=-inf,
            certified_radius=-inf,
            limiting_action_dim=None,
        )
    if trust_radius < 0:
        raise ValueError("trust_radius must be non-negative")

    margins = np.minimum(a - lo, hi - a)
    row_norms = np.linalg.norm(j, axis=1)

    ratios = np.full_like(margins, np.inf, dtype=float)
    active = row_norms > atol
    ratios[active] = margins[active] / row_norms[active]

    limiting = int(np.argmin(ratios)) if np.any(np.isfinite(ratios)) else None
    authority_radius = float(np.min(ratios)) if ratios.size else inf
    certified = float(min(trust_radius, authority_radius))

    return RepairabilityRadius(
        trust_radius=float(trust_radius),
        authority_radius=authority_radius,
        certified_radius=certified,
        limiting_action_dim=limiting,
    )


def _bounded_least_squares_l2_ball(
    g: np.ndarray,
    target: np.ndarray,
    radius: float,
    *,
    atol: float = 1e-12,
) -> np.ndarray:
    """Solve min ||G xi - target||_2 subject to ||xi||_2 <= radius."""

    if radius < 0:
        raise ValueError("radius must be non-negative")
    if radius == 0 or g.shape[1] == 0:
        return np.zeros(g.shape[1], dtype=float)

    u, s, vt = np.linalg.svd(g, full_matrices=False)
    coeff = u.T @ target

    inv = np.zeros_like(s)
    nz = s > atol
    inv[nz] = 1.0 / s[nz]
    xi_ls = vt.T @ (inv * coeff)
    if np.linalg.norm(xi_ls) <= radius + atol:
        return xi_ls

    # Trust-region KKT solution:
    # xi(lambda) = V diag(s/(s^2+lambda)) U^T target,
    # choose lambda >= 0 such that ||xi|| = radius.
    def xi_for(lam: float) -> np.ndarray:
        weights = np.zeros_like(s)
        weights[nz] = s[nz] / (s[nz] ** 2 + lam)
        return vt.T @ (weights * coeff)

    lo, hi = 0.0, 1.0
    while np.linalg.norm(xi_for(hi)) > radius:
        hi *= 2.0
        if hi > 1e18:
            raise RuntimeError("failed to bracket trust-region multiplier")

    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if np.linalg.norm(xi_for(mid)) > radius:
            lo = mid
        else:
            hi = mid

    return xi_for(hi)


def synthesize_repair(
    action_support_jacobian: np.ndarray,
    action_to_physical_jacobian: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    nominal_action: np.ndarray,
    action_low: np.ndarray,
    action_high: np.ndarray,
    trust_radius: float,
    residual_tolerance: float = 1e-8,
) -> RepairSynthesis:
    """Construct the nearest certified repair and an outside-set certificate.

    Certified repair set:
        K = { C J xi : ||xi||_2 <= r_cert }

    where r_cert is the largest support-space ball guaranteed to satisfy both
    the local trust region and the controller's action box.
    """

    j = np.asarray(action_support_jacobian, dtype=float)
    c = np.asarray(action_to_physical_jacobian, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)

    if c.ndim != 2 or j.ndim != 2:
        raise ValueError("Jacobians must be 2D")
    if c.shape[1] != j.shape[0]:
        raise ValueError("semantic lift and action-support Jacobian are incompatible")
    if d.ndim != 1 or d.size != c.shape[0]:
        raise ValueError("target physical correction dimension mismatch")

    radius = certified_support_radius(
        nominal_action,
        j,
        action_low,
        action_high,
        trust_radius=trust_radius,
    )
    if radius.certified_radius < 0:
        zero = np.zeros(j.shape[1], dtype=float)
        return RepairSynthesis(
            latent_repair=zero,
            physical_repair=np.zeros_like(d),
            residual=d.copy(),
            residual_norm=float(np.linalg.norm(d)),
            certified_radius=radius.certified_radius,
            repairable=False,
            separation_normal=d.copy(),
            separation_margin=float("inf"),
            reason="nominal action already violates controller authority",
        )

    g = c @ j
    xi = _bounded_least_squares_l2_ball(g, d, radius.certified_radius)
    repaired = g @ xi
    residual = d - repaired
    residual_norm = float(np.linalg.norm(residual))

    # K is a centered ellipsoid image. Its support function is
    # h_K(v) = r ||G^T v||. For projection residual n=d-p, a positive
    # n^T d - h_K(n) separates d from K.
    n = residual
    support_bound = radius.certified_radius * float(np.linalg.norm(g.T @ n))
    separation_margin = float(n @ d - support_bound)

    repairable = residual_norm <= residual_tolerance
    if repairable:
        reason = "target correction lies inside the certified repairability set"
    elif separation_margin > residual_tolerance:
        reason = "target correction is outside the certified repairability set"
    else:
        reason = "nearest certified repair leaves non-zero residual"

    return RepairSynthesis(
        latent_repair=xi,
        physical_repair=repaired,
        residual=residual,
        residual_norm=residual_norm,
        certified_radius=radius.certified_radius,
        repairable=repairable,
        separation_normal=n,
        separation_margin=separation_margin,
        reason=reason,
    )
