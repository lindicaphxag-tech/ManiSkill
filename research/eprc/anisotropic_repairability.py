from __future__ import annotations

from dataclasses import dataclass
from math import inf

import numpy as np

from .repairability_geometry import _bounded_least_squares_l2_ball


@dataclass(frozen=True)
class DirectionalLocalityProfile:
    coarse_fine_drift: np.ndarray
    fine_finer_drift: np.ndarray
    contraction_ratio: np.ndarray
    stable_direction: np.ndarray
    directional_radii: np.ndarray


@dataclass(frozen=True)
class AnisotropicAuthorityCertificate:
    requested_radii: np.ndarray
    authority_scale: float
    certified_radii: np.ndarray
    limiting_action_dim: int | None


@dataclass(frozen=True)
class AnisotropicRepair:
    normalized_support_delta: np.ndarray
    support_delta: np.ndarray
    physical_repair: np.ndarray
    residual: np.ndarray
    residual_norm: float
    repairable: bool
    certified_radii: np.ndarray
    reason: str


def directional_locality_profile(
    *,
    coarse_map: np.ndarray,
    fine_map: np.ndarray,
    finer_map: np.ndarray,
    fine_radius: float,
    finer_radius: float,
    contraction_threshold: float = 0.75,
    unstable_radius: float = 0.0,
    atol: float = 1e-12,
) -> DirectionalLocalityProfile:
    """Build an axis-wise locality gate from a frozen three-scale ladder.

    Each support column is treated as one physical intervention direction.
    A direction is admitted to the first-order repair set only when its
    fine->finer drift contracts relative to coarse->fine drift.

    This is an empirical locality gate, not a theorem about unobserved states.
    """

    gc = np.asarray(coarse_map, dtype=float)
    gf = np.asarray(fine_map, dtype=float)
    gff = np.asarray(finer_map, dtype=float)
    if gc.ndim != 2 or gf.shape != gc.shape or gff.shape != gc.shape:
        raise ValueError("coarse/fine/finer maps must share [physical,support] shape")
    if fine_radius <= 0 or finer_radius <= 0:
        raise ValueError("probe radii must be positive")
    if finer_radius >= fine_radius:
        raise ValueError("finer_radius must be smaller than fine_radius")
    if contraction_threshold <= 0:
        raise ValueError("contraction_threshold must be positive")
    if unstable_radius < 0:
        raise ValueError("unstable_radius must be nonnegative")

    d1 = np.linalg.norm(gc - gf, axis=0)
    d2 = np.linalg.norm(gf - gff, axis=0)

    ratio = np.empty_like(d1)
    for i, (a, b) in enumerate(zip(d1, d2)):
        if a <= atol:
            ratio[i] = 0.0 if b <= atol else inf
        else:
            ratio[i] = b / a

    stable = ratio <= contraction_threshold
    radii = np.where(stable, float(finer_radius), float(unstable_radius))

    return DirectionalLocalityProfile(
        coarse_fine_drift=d1,
        fine_finer_drift=d2,
        contraction_ratio=ratio,
        stable_direction=stable,
        directional_radii=radii,
    )


def certify_anisotropic_authority(
    nominal_action: np.ndarray,
    action_support_jacobian: np.ndarray,
    action_low: np.ndarray,
    action_high: np.ndarray,
    directional_radii: np.ndarray,
    *,
    atol: float = 1e-12,
) -> AnisotropicAuthorityCertificate:
    """Shrink an axis-aligned support ellipsoid until controller bounds are safe.

    Requested set:
        xi = R u, ||u||_2 <= 1, R=diag(r_i).

    For action row j_i,
        max_{||u||<=1} |j_i R u| = ||j_i R||_2.

    A single scale alpha in [0,1] is chosen so every action bound remains valid,
    preserving the data-driven anisotropy while respecting controller authority.
    """

    a = np.asarray(nominal_action, dtype=float)
    j = np.asarray(action_support_jacobian, dtype=float)
    lo = np.asarray(action_low, dtype=float)
    hi = np.asarray(action_high, dtype=float)
    radii = np.asarray(directional_radii, dtype=float)

    if j.ndim != 2 or a.ndim != 1 or j.shape[0] != a.size:
        raise ValueError("action/J dimensions differ")
    if lo.shape != a.shape or hi.shape != a.shape:
        raise ValueError("action bounds must match nominal action")
    if radii.ndim != 1 or radii.size != j.shape[1]:
        raise ValueError("directional_radii must match support dimension")
    if np.any(radii < 0):
        raise ValueError("directional radii must be nonnegative")
    if np.any(lo > hi):
        raise ValueError("invalid action bounds")
    if np.any(a < lo - atol) or np.any(a > hi + atol):
        return AnisotropicAuthorityCertificate(
            requested_radii=radii,
            authority_scale=-inf,
            certified_radii=np.full_like(radii, -inf),
            limiting_action_dim=None,
        )

    margins = np.minimum(a - lo, hi - a)
    scaled_rows = j * radii[None, :]
    row_norms = np.linalg.norm(scaled_rows, axis=1)

    ratios = np.full(a.shape, np.inf, dtype=float)
    active = row_norms > atol
    ratios[active] = margins[active] / row_norms[active]
    limiting = int(np.argmin(ratios)) if np.any(np.isfinite(ratios)) else None
    authority_scale = min(1.0, float(np.min(ratios)) if ratios.size else 1.0)

    return AnisotropicAuthorityCertificate(
        requested_radii=radii,
        authority_scale=authority_scale,
        certified_radii=authority_scale * radii,
        limiting_action_dim=limiting,
    )


def synthesize_anisotropic_repair(
    physical_repair_map: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    certified_radii: np.ndarray,
    residual_tolerance: float,
) -> AnisotropicRepair:
    """Nearest repair inside an anisotropic, locality-certified support ellipsoid."""

    g = np.asarray(physical_repair_map, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    radii = np.asarray(certified_radii, dtype=float)

    if g.ndim != 2 or d.ndim != 1 or g.shape[0] != d.size:
        raise ValueError("repair map / target dimensions differ")
    if radii.ndim != 1 or radii.size != g.shape[1]:
        raise ValueError("certified_radii must match support dimension")
    if residual_tolerance < 0:
        raise ValueError("residual_tolerance must be nonnegative")
    if np.any(radii < 0):
        zero = np.zeros(g.shape[1], dtype=float)
        return AnisotropicRepair(
            normalized_support_delta=zero,
            support_delta=zero,
            physical_repair=np.zeros_like(d),
            residual=d.copy(),
            residual_norm=float(np.linalg.norm(d)),
            repairable=False,
            certified_radii=radii,
            reason="nominal action is outside controller authority",
        )

    R = np.diag(radii)
    g_ball = g @ R
    u = _bounded_least_squares_l2_ball(g_ball, d, 1.0)
    xi = R @ u
    repaired = g @ xi
    residual = d - repaired
    residual_norm = float(np.linalg.norm(residual))

    if residual_norm <= residual_tolerance:
        reason = "target lies inside the anisotropic locality-and-authority repair set"
    else:
        blocked = np.flatnonzero(radii == 0.0)
        if blocked.size:
            reason = (
                "target remains outside the certified repair set; at least one "
                "physical support direction failed the locality gate"
            )
        else:
            reason = "target remains outside the anisotropic certified repair set"

    return AnisotropicRepair(
        normalized_support_delta=u,
        support_delta=xi,
        physical_repair=repaired,
        residual=residual,
        residual_norm=residual_norm,
        repairable=residual_norm <= residual_tolerance,
        certified_radii=radii,
        reason=reason,
    )


def anisotropic_map_uncertainty_bound(
    per_direction_map_uncertainty: np.ndarray,
    certified_radii: np.ndarray,
) -> float:
    """Operator bound after anisotropic support scaling.

    If column i of map error has Euclidean norm <= eps_i and xi=R u with
    ||u||_2<=1, then

        ||E R u|| <= ||E R||_F <= sqrt(sum_i (eps_i r_i)^2).

    The Frobenius bound is conservative but independently checkable.
    """

    eps = np.asarray(per_direction_map_uncertainty, dtype=float)
    radii = np.asarray(certified_radii, dtype=float)
    if eps.ndim != 1 or radii.shape != eps.shape:
        raise ValueError("uncertainty and radii must be aligned vectors")
    if np.any(eps < 0) or np.any(radii < 0):
        raise ValueError("uncertainty and radii must be nonnegative")
    return float(np.linalg.norm(eps * radii))
