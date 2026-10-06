from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .repairability_witness import (
    RepairabilitySeparationWitness,
    build_separation_witness,
    verify_separation_witness,
)
from .robust_repairability import RobustRepairDecision


@dataclass(frozen=True)
class LocalRegularityGate:
    coarse_fine_drift: float
    fine_finer_drift: float
    contraction_ratio: float
    first_order_supported: bool
    reason: str


@dataclass(frozen=True)
class StructuredRepairCertificate:
    decision: RobustRepairDecision
    common_support_delta: np.ndarray
    per_hypothesis_residuals: np.ndarray
    worst_common_residual: float
    per_hypothesis_best_residuals: np.ndarray
    individually_repairable: np.ndarray
    common_repair_verified: bool
    impossible_hypothesis_index: int | None
    impossibility_witness: RepairabilitySeparationWitness | None
    quantifier_gap: bool
    reason: str


def first_order_regularity_gate(
    coarse_map: np.ndarray,
    fine_map: np.ndarray,
    finer_map: np.ndarray,
    *,
    contraction_threshold: float,
    atol: float = 1e-12,
) -> LocalRegularityGate:
    """Gate first-order authorization using a frozen multi-scale contraction rule."""

    gc = np.asarray(coarse_map, dtype=float)
    gf = np.asarray(fine_map, dtype=float)
    gff = np.asarray(finer_map, dtype=float)
    if gc.shape != gf.shape or gf.shape != gff.shape or gc.ndim != 2:
        raise ValueError("all physical maps must be shape-aligned 2D matrices")
    if contraction_threshold <= 0:
        raise ValueError("contraction_threshold must be positive")

    d1 = float(np.linalg.norm(gc - gf, ord=2))
    d2 = float(np.linalg.norm(gf - gff, ord=2))
    if d1 <= atol:
        q = 0.0 if d2 <= atol else float("inf")
    else:
        q = d2 / d1

    supported = bool(q <= contraction_threshold)
    return LocalRegularityGate(
        coarse_fine_drift=d1,
        fine_finer_drift=d2,
        contraction_ratio=float(q),
        first_order_supported=supported,
        reason=(
            "multi-scale response contracts under the frozen first-order gate"
            if supported
            else "multi-scale response does not contract; first-order repair authorization is rejected"
        ),
    )


def _least_squares_in_ball(
    g: np.ndarray,
    d: np.ndarray,
    radius: float,
    *,
    atol: float = 1e-12,
) -> np.ndarray:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    if radius == 0 or g.shape[1] == 0:
        return np.zeros(g.shape[1], dtype=float)

    u, s, vt = np.linalg.svd(g, full_matrices=False)
    coeff = u.T @ d
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


def verify_common_repair(
    physical_map_hypotheses: np.ndarray,
    target: np.ndarray,
    support_delta: np.ndarray,
    *,
    radius: float,
    residual_tolerance: float,
    atol: float = 1e-9,
) -> bool:
    """Independent sufficient verifier for exists-xi / for-all-map repair."""

    maps = np.asarray(physical_map_hypotheses, dtype=float)
    d = np.asarray(target, dtype=float)
    xi = np.asarray(support_delta, dtype=float)
    if maps.ndim != 3 or d.ndim != 1 or xi.ndim != 1:
        return False
    if maps.shape[1] != d.size or maps.shape[2] != xi.size:
        return False
    if radius < 0 or residual_tolerance < 0:
        return False
    if np.linalg.norm(xi) > radius + atol:
        return False
    residuals = np.linalg.norm(maps @ xi - d[None, :], axis=1)
    return bool(np.max(residuals) <= residual_tolerance + atol)


def structured_repairability_certificate(
    physical_map_hypotheses: np.ndarray,
    target: np.ndarray,
    *,
    radius: float,
    residual_tolerance: float,
) -> StructuredRepairCertificate:
    """Fail-closed certificate over a finite physical-map hypothesis set.

    The runtime-valid quantifier is

        exists xi  such that  for every G in hypotheses:
            ||G xi - d|| <= tau.

    This is strictly stronger than checking each hypothesis independently:

        for every G there exists xi_G.

    The implementation certifies a common repair with an independently checkable
    witness. It certifies impossibility when one hypothesis alone has a valid
    separation witness beyond tau. All remaining cases are INCONCLUSIVE.
    """

    maps = np.asarray(physical_map_hypotheses, dtype=float)
    d = np.asarray(target, dtype=float)
    if maps.ndim != 3 or maps.shape[0] == 0:
        raise ValueError("hypotheses must have shape [n_maps, physical_dim, support_dim]")
    if d.ndim != 1 or maps.shape[1] != d.size:
        raise ValueError("target physical dimension mismatch")
    if radius < 0 or residual_tolerance < 0:
        raise ValueError("radius and residual_tolerance must be nonnegative")

    n_maps, p_dim, s_dim = maps.shape

    # Common candidate minimizes aggregate squared residual. Passing the
    # independent max-residual verifier is sufficient for robust execution.
    stacked_g = maps.reshape(n_maps * p_dim, s_dim)
    stacked_d = np.tile(d, n_maps)
    common_xi = _least_squares_in_ball(stacked_g, stacked_d, radius)
    common_residuals = np.linalg.norm(maps @ common_xi - d[None, :], axis=1)
    common_ok = verify_common_repair(
        maps,
        d,
        common_xi,
        radius=radius,
        residual_tolerance=residual_tolerance,
    )

    best_residuals = []
    individual_xis = []
    for g in maps:
        xi_i = _least_squares_in_ball(g, d, radius)
        individual_xis.append(xi_i)
        best_residuals.append(float(np.linalg.norm(g @ xi_i - d)))
    best = np.asarray(best_residuals)
    individually = best <= residual_tolerance

    if common_ok:
        return StructuredRepairCertificate(
            decision=RobustRepairDecision.CERTIFIED_REPAIR,
            common_support_delta=common_xi,
            per_hypothesis_residuals=common_residuals,
            worst_common_residual=float(np.max(common_residuals)),
            per_hypothesis_best_residuals=best,
            individually_repairable=individually,
            common_repair_verified=True,
            impossible_hypothesis_index=None,
            impossibility_witness=None,
            quantifier_gap=False,
            reason="one support correction satisfies every observed physical-map hypothesis",
        )

    # Strong impossibility: if even one admissible map individually cannot meet
    # tau, no forall-map robust repair can exist. Carry a dual witness.
    for idx, (g, xi_i, best_i) in enumerate(zip(maps, individual_xis, best)):
        if best_i <= residual_tolerance:
            continue
        residual = d - g @ xi_i
        if np.linalg.norm(residual) <= 1e-12:
            continue
        witness = build_separation_witness(
            g, d, certified_radius=radius, normal=residual
        )
        if verify_separation_witness(
            g,
            d,
            certified_radius=radius,
            witness=witness,
            minimum_margin=residual_tolerance,
        ):
            return StructuredRepairCertificate(
                decision=RobustRepairDecision.CERTIFIED_IMPOSSIBLE,
                common_support_delta=common_xi,
                per_hypothesis_residuals=common_residuals,
                worst_common_residual=float(np.max(common_residuals)),
                per_hypothesis_best_residuals=best,
                individually_repairable=individually,
                common_repair_verified=False,
                impossible_hypothesis_index=idx,
                impossibility_witness=witness,
                quantifier_gap=False,
                reason="at least one admissible physical-map hypothesis independently proves the target outside its repair set",
            )

    quantifier_gap = bool(np.all(individually) and not common_ok)
    return StructuredRepairCertificate(
        decision=RobustRepairDecision.INCONCLUSIVE,
        common_support_delta=common_xi,
        per_hypothesis_residuals=common_residuals,
        worst_common_residual=float(np.max(common_residuals)),
        per_hypothesis_best_residuals=best,
        individually_repairable=individually,
        common_repair_verified=False,
        impossible_hypothesis_index=None,
        impossibility_witness=None,
        quantifier_gap=quantifier_gap,
        reason=(
            "each observed map is individually repairable, but no common repair has been certified; forall-map/exists-repair evidence is insufficient"
            if quantifier_gap
            else "no common repair is certified and no single-hypothesis impossibility witness is available"
        ),
    )
