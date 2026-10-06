from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RobustRepairWitness:
    """Primal witness for a robustly feasible CRG repair."""
    support_delta: np.ndarray
    nominal_residual: float
    uncertainty_allowance: float
    worst_case_residual_upper: float
    residual_tolerance: float


@dataclass(frozen=True)
class RobustImpossibilityWitness:
    """Dual separation witness for robust CRG impossibility."""
    normal: np.ndarray
    target_projection: float
    nominal_support: float
    uncertainty_support: float
    robust_support: float
    distance_lower_bound: float
    residual_tolerance: float
    margin_over_tolerance: float


def build_repair_witness(
    physical_map_estimate: np.ndarray,
    target_physical_correction: np.ndarray,
    *, certified_radius: float, epsilon_g: float, residual_tolerance: float,
    support_delta: np.ndarray,
) -> RobustRepairWitness:
    g = np.asarray(physical_map_estimate, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    x = np.asarray(support_delta, dtype=float)
    if g.ndim != 2 or d.ndim != 1 or x.ndim != 1:
        raise ValueError("map, target, and support delta dimensions are invalid")
    if g.shape[0] != d.size or g.shape[1] != x.size:
        raise ValueError("map/target/support dimensions do not match")
    if certified_radius < 0 or epsilon_g < 0 or residual_tolerance < 0:
        raise ValueError("radius, uncertainty, and tolerance must be nonnegative")
    if np.linalg.norm(x) > certified_radius + 1e-12:
        raise ValueError("support delta exceeds the certified radius")
    nominal = float(np.linalg.norm(g @ x - d))
    uncertainty = float(epsilon_g * np.linalg.norm(x))
    upper = float(nominal + uncertainty)
    return RobustRepairWitness(x.copy(), nominal, uncertainty, upper, float(residual_tolerance))


def verify_repair_witness(
    physical_map_estimate: np.ndarray, target_physical_correction: np.ndarray,
    *, certified_radius: float, epsilon_g: float, witness: RobustRepairWitness,
    minimum_margin: float = 0.0, atol: float = 1e-9,
) -> bool:
    """Verify a repair without trusting or rerunning the original optimizer."""
    if minimum_margin < 0:
        raise ValueError("minimum_margin must be nonnegative")
    try:
        expected = build_repair_witness(
            physical_map_estimate, target_physical_correction,
            certified_radius=certified_radius, epsilon_g=epsilon_g,
            residual_tolerance=witness.residual_tolerance, support_delta=witness.support_delta,
        )
    except ValueError:
        return False
    for field in ('nominal_residual','uncertainty_allowance','worst_case_residual_upper','residual_tolerance'):
        if not np.isclose(getattr(witness, field), getattr(expected, field), atol=atol, rtol=atol):
            return False
    return bool(expected.worst_case_residual_upper <= expected.residual_tolerance - minimum_margin + atol)


def build_impossibility_witness(
    physical_map_estimate: np.ndarray, target_physical_correction: np.ndarray,
    *, certified_radius: float, epsilon_g: float, residual_tolerance: float,
    normal: np.ndarray, atol: float = 1e-12,
) -> RobustImpossibilityWitness:
    """Build a support-function separation proof for the full map uncertainty ball."""
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
    nominal_support = float(certified_radius * np.linalg.norm(g.T @ unit))
    uncertainty_support = float(certified_radius * epsilon_g)
    robust_support = float(nominal_support + uncertainty_support)
    lower = float(target_projection - robust_support)
    margin = float(lower - residual_tolerance)
    return RobustImpossibilityWitness(unit, target_projection, nominal_support, uncertainty_support, robust_support, lower, float(residual_tolerance), margin)


def verify_impossibility_witness(
    physical_map_estimate: np.ndarray, target_physical_correction: np.ndarray,
    *, certified_radius: float, epsilon_g: float, witness: RobustImpossibilityWitness,
    minimum_margin: float = 1e-10, atol: float = 1e-9,
) -> bool:
    """Verify impossibility from a compact dual witness, without optimization."""
    if minimum_margin < 0:
        raise ValueError("minimum_margin must be nonnegative")
    try:
        expected = build_impossibility_witness(
            physical_map_estimate, target_physical_correction, certified_radius=certified_radius,
            epsilon_g=epsilon_g, residual_tolerance=witness.residual_tolerance, normal=witness.normal,
        )
    except ValueError:
        return False
    if not np.isclose(np.linalg.norm(witness.normal), 1.0, atol=atol):
        return False
    for field in ('target_projection','nominal_support','uncertainty_support','robust_support','distance_lower_bound','residual_tolerance','margin_over_tolerance'):
        if not np.isclose(getattr(witness, field), getattr(expected, field), atol=atol, rtol=atol):
            return False
    return bool(expected.margin_over_tolerance > minimum_margin)
