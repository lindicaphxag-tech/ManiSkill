from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class Decision(str, Enum):
    CERTIFIED_REPAIR = "CERTIFIED_REPAIR"
    CERTIFIED_IMPOSSIBLE = "CERTIFIED_IMPOSSIBLE"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class LinearAuthority:
    H: np.ndarray
    h: np.ndarray

    def __post_init__(self) -> None:
        H = np.asarray(self.H, dtype=float)
        h = np.asarray(self.h, dtype=float)
        if H.ndim != 2 or h.ndim != 1 or H.shape[0] != h.size:
            raise ValueError("authority must satisfy H.shape=[m,n], h.shape=[m]")
        object.__setattr__(self, "H", H)
        object.__setattr__(self, "h", h)

    @classmethod
    def box(cls, low: np.ndarray, high: np.ndarray) -> "LinearAuthority":
        low = np.asarray(low, dtype=float)
        high = np.asarray(high, dtype=float)
        if low.ndim != 1 or high.shape != low.shape or np.any(low > high):
            raise ValueError("invalid box")
        I = np.eye(low.size)
        return cls(np.vstack([I, -I]), np.concatenate([high, -low]))


@dataclass(frozen=True)
class Certificate:
    decision: Decision
    support_delta: np.ndarray
    nominal_residual: float
    worst_case_residual_upper: float
    best_case_residual_lower: float
    operator_uncertainty: float
    certified_radius: float
    reason: str


def product_uncertainty_bound(
    C: np.ndarray,
    J: np.ndarray,
    *,
    epsilon_C: float,
    epsilon_J: float,
) -> float:
    C = np.asarray(C, dtype=float)
    J = np.asarray(J, dtype=float)
    if C.ndim != 2 or J.ndim != 2 or C.shape[1] != J.shape[0]:
        raise ValueError("C and J must compose")
    if epsilon_C < 0 or epsilon_J < 0:
        raise ValueError("uncertainties must be nonnegative")
    return float(
        np.linalg.norm(C, 2) * epsilon_J
        + np.linalg.norm(J, 2) * epsilon_C
        + epsilon_C * epsilon_J
    )


def empirical_operator_envelope(
    maps: np.ndarray,
    *,
    quantile: float = 1.0,
) -> tuple[np.ndarray, float]:
    maps = np.asarray(maps, dtype=float)
    if maps.ndim != 3 or maps.shape[0] == 0:
        raise ValueError("maps must have shape [replicate, output, support]")
    if not 0 < quantile <= 1:
        raise ValueError("quantile must be in (0,1]")
    center = np.mean(maps, axis=0)
    radii = np.asarray([np.linalg.norm(M - center, 2) for M in maps])
    eps = float(np.quantile(radii, quantile, method="higher"))
    return center, eps


def robust_authority_radius(
    nominal_action: np.ndarray,
    J_hat: np.ndarray,
    authority: LinearAuthority,
    *,
    epsilon_J: float,
    trust_radius: float,
    atol: float = 1e-12,
) -> float:
    a0 = np.asarray(nominal_action, dtype=float)
    J = np.asarray(J_hat, dtype=float)
    if a0.ndim != 1 or J.ndim != 2 or J.shape[0] != a0.size:
        raise ValueError("action/J shape mismatch")
    if authority.H.shape[1] != a0.size:
        raise ValueError("authority dimension mismatch")
    if epsilon_J < 0 or trust_radius < 0:
        raise ValueError("negative uncertainty/radius")

    margin = authority.h - authority.H @ a0
    if np.any(margin < -atol):
        return float("-inf")

    worst_slope = (
        np.linalg.norm(authority.H @ J, axis=1)
        + np.linalg.norm(authority.H, axis=1) * epsilon_J
    )
    ratios = np.full(margin.shape, np.inf)
    active = worst_slope > atol
    ratios[active] = np.maximum(margin[active], 0.0) / worst_slope[active]
    return float(min(trust_radius, np.min(ratios)))


def _project_target_to_image_ball(
    G: np.ndarray,
    target: np.ndarray,
    radius: float,
    *,
    atol: float = 1e-12,
) -> np.ndarray:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    if radius == 0 or G.shape[1] == 0:
        return np.zeros(G.shape[1])

    U, s, Vt = np.linalg.svd(G, full_matrices=False)
    coeff = U.T @ target
    nz = s > atol
    inv = np.zeros_like(s)
    inv[nz] = 1.0 / s[nz]
    x = Vt.T @ (inv * coeff)
    if np.linalg.norm(x) <= radius + atol:
        return x

    def x_of(lam: float) -> np.ndarray:
        w = np.zeros_like(s)
        w[nz] = s[nz] / (s[nz] ** 2 + lam)
        return Vt.T @ (w * coeff)

    lo, hi = 0.0, 1.0
    while np.linalg.norm(x_of(hi)) > radius:
        hi *= 2.0
        if hi > 1e18:
            raise RuntimeError("failed to bracket trust-region multiplier")

    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if np.linalg.norm(x_of(mid)) > radius:
            lo = mid
        else:
            hi = mid
    return x_of(hi)


def certify(
    G_hat: np.ndarray,
    target: np.ndarray,
    *,
    epsilon_G: float,
    certified_radius: float,
    tolerance: float,
) -> Certificate:
    G = np.asarray(G_hat, dtype=float)
    d = np.asarray(target, dtype=float)
    if G.ndim != 2 or d.ndim != 1 or G.shape[0] != d.size:
        raise ValueError("G/target shape mismatch")
    if epsilon_G < 0 or tolerance < 0:
        raise ValueError("negative uncertainty/tolerance")

    if certified_radius < 0:
        return Certificate(
            Decision.CERTIFIED_IMPOSSIBLE,
            np.zeros(G.shape[1]),
            float(np.linalg.norm(d)),
            float("inf"),
            float("inf"),
            float(epsilon_G),
            float(certified_radius),
            "nominal action is already outside certified authority",
        )

    x = _project_target_to_image_ball(G, d, certified_radius)
    nominal = float(np.linalg.norm(G @ x - d))
    upper = nominal + epsilon_G * float(np.linalg.norm(x))
    lower = max(0.0, nominal - epsilon_G * certified_radius)

    if upper <= tolerance:
        decision = Decision.CERTIFIED_REPAIR
        reason = "one policy-consistent repair succeeds for every admissible local map"
    elif lower > tolerance:
        decision = Decision.CERTIFIED_IMPOSSIBLE
        reason = "no admissible local map can reach the target within tolerance"
    else:
        decision = Decision.INCONCLUSIVE
        reason = "uncertainty overlaps the repairability boundary; abstain and re-probe"

    return Certificate(
        decision,
        x,
        nominal,
        float(upper),
        float(lower),
        float(epsilon_G),
        float(certified_radius),
        reason,
    )
