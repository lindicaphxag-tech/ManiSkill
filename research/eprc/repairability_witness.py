from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RepairabilitySeparationWitness:
    """Dual witness that a target lies outside a centered CRG repair set.

    For K = {G xi : ||xi||_2 <= r}, the support function is
        h_K(n) = r ||G^T n||_2.
    Therefore any nonzero n satisfying
        n^T d - h_K(n) > 0
    is a complete separation witness that d is not in K.
    """

    normal: np.ndarray
    target_projection: float
    repair_set_support: float
    margin: float


def build_separation_witness(
    physical_repair_map: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    certified_radius: float,
    normal: np.ndarray,
    atol: float = 1e-12,
) -> RepairabilitySeparationWitness:
    g = np.asarray(physical_repair_map, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    n = np.asarray(normal, dtype=float)

    if g.ndim != 2 or d.ndim != 1 or n.ndim != 1:
        raise ValueError("map, target, and normal dimensions are invalid")
    if g.shape[0] != d.size or n.size != d.size:
        raise ValueError("physical dimensions do not match")
    if certified_radius < 0:
        raise ValueError("certified_radius must be nonnegative")

    norm = float(np.linalg.norm(n))
    if norm <= atol:
        raise ValueError("separation normal must be nonzero")
    unit = n / norm

    target_projection = float(unit @ d)
    repair_set_support = float(
        certified_radius * np.linalg.norm(g.T @ unit)
    )
    margin = float(target_projection - repair_set_support)

    return RepairabilitySeparationWitness(
        normal=unit,
        target_projection=target_projection,
        repair_set_support=repair_set_support,
        margin=margin,
    )


def verify_separation_witness(
    physical_repair_map: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    certified_radius: float,
    witness: RepairabilitySeparationWitness,
    minimum_margin: float = 1e-10,
    atol: float = 1e-9,
) -> bool:
    """Independently verify a CRG impossibility witness.

    The verifier does not run the repair optimizer. It only checks the support
    inequality induced by the supplied dual normal.
    """

    if minimum_margin < 0:
        raise ValueError("minimum_margin must be nonnegative")

    try:
        expected = build_separation_witness(
            physical_repair_map,
            target_physical_correction,
            certified_radius=certified_radius,
            normal=witness.normal,
        )
    except ValueError:
        return False

    if not np.isclose(np.linalg.norm(witness.normal), 1.0, atol=atol):
        return False
    if not np.isclose(
        witness.target_projection, expected.target_projection, atol=atol, rtol=atol
    ):
        return False
    if not np.isclose(
        witness.repair_set_support, expected.repair_set_support, atol=atol, rtol=atol
    ):
        return False
    if not np.isclose(witness.margin, expected.margin, atol=atol, rtol=atol):
        return False

    return bool(expected.margin > minimum_margin)
