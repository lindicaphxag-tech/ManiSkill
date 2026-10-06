from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RobustSeparationWitness:
    """Dual witness for robust CRG impossibility.

    Assume ||G_true - G_hat||_2 <= epsilon_g and
        K_true = {G_true xi : ||xi||_2 <= r}.

    For unit normal n,
        sup_{y in K_true} n^T y
        <= r (||G_hat^T n||_2 + epsilon_g).

    Hence if
        n^T d - r (||G_hat^T n|| + epsilon_g) > tau,
    every admissible repair set remains farther than tau from target d.
    """

    normal: np.ndarray
    target_projection: float
    nominal_support: float
    uncertainty_support: float
    robust_support: float
    distance_lower_bound: float
    residual_tolerance: float
    margin_over_tolerance: float


def build_robust_separation_witness(
    physical_map_estimate: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    certified_radius: float,
    epsilon_g: float,
    residual_tolerance: float,
    normal: np.ndarray,
    atol: float = 1e-12,
) -> RobustSeparationWitness:
    g = np.asarray(physical_map_estimate, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    n = np.asarray(normal, dtype=float)

    if g.ndim != 2 or d.ndim != 1 or n.ndim != 1:
        raise ValueError("map, target, and normal dimensions are invalid")
    if g.shape[0] != d.size or n.size != d.size:
        raise ValueError("physical dimensions do not match")
    if certified_radius < 0 or epsilon_g < 0 or residual_tolerance < 0:
        raise ValueError("radius, uncertainty, and tolerance must be nonnegative")

    norm = float(np.linalg.norm(n))
    if norm <= atol:
        raise ValueError("separation normal must be nonzero")
    unit = n / norm

    target_projection = float(unit @ d)
    nominal_support = float(
        certified_radius * np.linalg.norm(g.T @ unit)
    )
    uncertainty_support = float(certified_radius * epsilon_g)
    robust_support = float(nominal_support + uncertainty_support)
    distance_lower_bound = float(target_projection - robust_support)
    margin = float(distance_lower_bound - residual_tolerance)

    return RobustSeparationWitness(
        normal=unit,
        target_projection=target_projection,
        nominal_support=nominal_support,
        uncertainty_support=uncertainty_support,
        robust_support=robust_support,
        distance_lower_bound=distance_lower_bound,
        residual_tolerance=float(residual_tolerance),
        margin_over_tolerance=margin,
    )


def verify_robust_separation_witness(
    physical_map_estimate: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    certified_radius: float,
    epsilon_g: float,
    witness: RobustSeparationWitness,
    minimum_margin: float = 1e-10,
    atol: float = 1e-9,
) -> bool:
    """Verify robust impossibility without running the repair optimizer."""

    if minimum_margin < 0:
        raise ValueError("minimum_margin must be nonnegative")

    try:
        expected = build_robust_separation_witness(
            physical_map_estimate,
            target_physical_correction,
            certified_radius=certified_radius,
            epsilon_g=epsilon_g,
            residual_tolerance=witness.residual_tolerance,
            normal=witness.normal,
        )
    except ValueError:
        return False

    if not np.isclose(np.linalg.norm(witness.normal), 1.0, atol=atol):
        return False

    scalar_fields = (
        "target_projection",
        "nominal_support",
        "uncertainty_support",
        "robust_support",
        "distance_lower_bound",
        "residual_tolerance",
        "margin_over_tolerance",
    )
    for field in scalar_fields:
        if not np.isclose(
            getattr(witness, field),
            getattr(expected, field),
            atol=atol,
            rtol=atol,
        ):
            return False

    return bool(expected.margin_over_tolerance > minimum_margin)
