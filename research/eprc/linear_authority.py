from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LinearActionAuthority:
    """Local action authority represented as H a <= h."""

    H: np.ndarray
    h: np.ndarray

    def __post_init__(self) -> None:
        hmat = np.asarray(self.H, dtype=float)
        hvec = np.asarray(self.h, dtype=float)
        if hmat.ndim != 2 or hvec.ndim != 1 or hmat.shape[0] != hvec.size:
            raise ValueError("authority must satisfy H.shape == [n_constraints, action_dim] and h.shape == [n_constraints]")
        object.__setattr__(self, "H", hmat)
        object.__setattr__(self, "h", hvec)

    @classmethod
    def from_box(cls, low: np.ndarray, high: np.ndarray) -> "LinearActionAuthority":
        lo = np.asarray(low, dtype=float)
        hi = np.asarray(high, dtype=float)
        if lo.ndim != 1 or hi.shape != lo.shape:
            raise ValueError("low/high must be shape-aligned vectors")
        if np.any(lo > hi):
            raise ValueError("low must not exceed high")
        eye = np.eye(lo.size)
        return cls(
            H=np.vstack([eye, -eye]),
            h=np.concatenate([hi, -lo]),
        )

    def contains(self, action: np.ndarray, *, atol: float = 1e-10) -> bool:
        a = np.asarray(action, dtype=float)
        if a.ndim != 1 or a.size != self.H.shape[1]:
            raise ValueError("action dimension mismatch")
        return bool(np.all(self.H @ a <= self.h + atol))

    def reparameterize(self, action_chart_jacobian: np.ndarray) -> "LinearActionAuthority":
        """Push authority into coordinates a' = R a.

        H a <= h becomes H R^{-1} a' <= h.
        """

        r = np.asarray(action_chart_jacobian, dtype=float)
        if r.ndim != 2 or r.shape[0] != r.shape[1] or r.shape[0] != self.H.shape[1]:
            raise ValueError("action chart Jacobian must be square and match action dimension")
        return LinearActionAuthority(self.H @ np.linalg.inv(r), self.h.copy())


@dataclass(frozen=True)
class LinearAuthorityRadius:
    trust_radius: float
    authority_radius: float
    certified_radius: float
    limiting_constraint: int | None
    minimum_constraint_margin: float


@dataclass(frozen=True)
class PolicyConsistentRepair:
    certified: bool
    support_delta: np.ndarray
    action_delta: np.ndarray
    repaired_action: np.ndarray
    physical_repair: np.ndarray
    residual: np.ndarray
    residual_norm: float
    certified_radius: float
    normalized_radius_usage: float
    separation_normal: np.ndarray
    separation_margin: float
    reason: str


def certified_support_radius_linear_authority(
    nominal_action: np.ndarray,
    action_support_jacobian: np.ndarray,
    authority: LinearActionAuthority,
    *,
    trust_radius: float,
    atol: float = 1e-12,
) -> LinearAuthorityRadius:
    """Largest centered L2 support ball guaranteed inside linear action authority.

    For every constraint row H_i and support perturbation ||xi|| <= r,

        H_i (a0 + J xi)
        <= H_i a0 + r ||H_i J||_2.

    Therefore the exact largest centered support ball contained in all local
    linear constraints is min_i (h_i - H_i a0) / ||H_i J||_2, intersected with
    the model trust radius.
    """

    a = np.asarray(nominal_action, dtype=float)
    j = np.asarray(action_support_jacobian, dtype=float)
    if a.ndim != 1 or j.ndim != 2 or j.shape[0] != a.size:
        raise ValueError("nominal action and action-support Jacobian dimensions differ")
    if authority.H.shape[1] != a.size:
        raise ValueError("authority/action dimensions differ")
    if trust_radius < 0:
        raise ValueError("trust_radius must be nonnegative")

    margins = authority.h - authority.H @ a
    if np.any(margins < -atol):
        return LinearAuthorityRadius(
            trust_radius=float(trust_radius),
            authority_radius=float("-inf"),
            certified_radius=float("-inf"),
            limiting_constraint=int(np.argmin(margins)),
            minimum_constraint_margin=float(np.min(margins)),
        )

    support_rows = authority.H @ j
    row_norms = np.linalg.norm(support_rows, axis=1)
    ratios = np.full(margins.shape, np.inf, dtype=float)
    active = row_norms > atol
    ratios[active] = np.maximum(margins[active], 0.0) / row_norms[active]

    limiting = int(np.argmin(ratios)) if np.any(np.isfinite(ratios)) else None
    authority_radius = float(np.min(ratios)) if ratios.size else float("inf")
    return LinearAuthorityRadius(
        trust_radius=float(trust_radius),
        authority_radius=authority_radius,
        certified_radius=float(min(trust_radius, authority_radius)),
        limiting_constraint=limiting,
        minimum_constraint_margin=float(np.min(margins)) if margins.size else float("inf"),
    )


def _solve_l2_ball_least_squares(
    physical_map: np.ndarray,
    target: np.ndarray,
    radius: float,
    *,
    atol: float = 1e-12,
) -> np.ndarray:
    """Solve min ||G xi - d||_2 subject to ||xi||_2 <= radius."""

    g = np.asarray(physical_map, dtype=float)
    d = np.asarray(target, dtype=float)
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    if radius == 0 or g.shape[1] == 0:
        return np.zeros(g.shape[1], dtype=float)

    u, s, vt = np.linalg.svd(g, full_matrices=False)
    coeff = u.T @ d
    nz = s > atol

    inv = np.zeros_like(s)
    inv[nz] = 1.0 / s[nz]
    unconstrained = vt.T @ (inv * coeff)
    if np.linalg.norm(unconstrained) <= radius + atol:
        return unconstrained

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


def synthesize_policy_consistent_repair(
    action_support_jacobian: np.ndarray,
    action_to_physical_jacobian: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    nominal_action: np.ndarray,
    authority: LinearActionAuthority,
    trust_radius: float,
    residual_tolerance: float = 1e-8,
) -> PolicyConsistentRepair:
    """Synthesize a repair restricted to the intervention-identified policy image."""

    j = np.asarray(action_support_jacobian, dtype=float)
    c = np.asarray(action_to_physical_jacobian, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    a0 = np.asarray(nominal_action, dtype=float)

    if j.ndim != 2 or c.ndim != 2 or c.shape[1] != j.shape[0]:
        raise ValueError("semantic lift and action-support Jacobian do not compose")
    if a0.ndim != 1 or a0.size != j.shape[0]:
        raise ValueError("nominal action dimension mismatch")
    if d.ndim != 1 or d.size != c.shape[0]:
        raise ValueError("physical correction dimension mismatch")

    radius = certified_support_radius_linear_authority(
        a0, j, authority, trust_radius=trust_radius
    )
    if radius.certified_radius < 0:
        zeros = np.zeros(j.shape[1], dtype=float)
        return PolicyConsistentRepair(
            certified=False,
            support_delta=zeros,
            action_delta=np.zeros(j.shape[0], dtype=float),
            repaired_action=a0.copy(),
            physical_repair=np.zeros_like(d),
            residual=d.copy(),
            residual_norm=float(np.linalg.norm(d)),
            certified_radius=radius.certified_radius,
            normalized_radius_usage=float("inf"),
            separation_normal=d.copy(),
            separation_margin=float("inf"),
            reason="nominal action violates local action authority",
        )

    g = c @ j
    xi = _solve_l2_ball_least_squares(g, d, radius.certified_radius)
    action_delta = j @ xi
    repaired_action = a0 + action_delta
    physical_repair = g @ xi
    residual = d - physical_repair
    residual_norm = float(np.linalg.norm(residual))

    n = residual
    support_bound = radius.certified_radius * float(np.linalg.norm(g.T @ n))
    separation_margin = float(n @ d - support_bound)
    usage = (
        0.0
        if radius.certified_radius == 0 and np.linalg.norm(xi) == 0
        else float(np.linalg.norm(xi) / radius.certified_radius)
        if radius.certified_radius > 0
        else float("inf")
    )

    inside_authority = authority.contains(repaired_action, atol=1e-9)
    certified = residual_norm <= residual_tolerance and inside_authority
    if certified:
        reason = "exact policy-consistent repair lies inside certified linear action authority"
    elif not inside_authority:
        reason = "synthesized repair violates action authority"
    elif separation_margin > residual_tolerance:
        reason = "requested correction lies outside policy-consistent certified repairability set"
    else:
        reason = "nearest certified policy-consistent repair leaves nonzero residual"

    return PolicyConsistentRepair(
        certified=certified,
        support_delta=xi,
        action_delta=action_delta,
        repaired_action=repaired_action,
        physical_repair=physical_repair,
        residual=residual,
        residual_norm=residual_norm,
        certified_radius=radius.certified_radius,
        normalized_radius_usage=usage,
        separation_normal=n,
        separation_margin=separation_margin,
        reason=reason,
    )
