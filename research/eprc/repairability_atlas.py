from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .robust_repairability import (
    PhysicalMapUncertainty,
    RobustRepairDecision,
    RobustRepairCertificate,
    robust_repair_certificate,
)


@dataclass(frozen=True)
class PolicyRepairSet:
    name: str
    physical_map: np.ndarray
    operator_uncertainty: float
    certified_radius: float
    switch_cost: float = 0.0

    def __post_init__(self) -> None:
        g = np.asarray(self.physical_map, dtype=float)
        if g.ndim != 2:
            raise ValueError("physical_map must be 2D")
        if self.operator_uncertainty < 0:
            raise ValueError("operator_uncertainty must be nonnegative")
        if self.switch_cost < 0:
            raise ValueError("switch_cost must be nonnegative")
        object.__setattr__(self, "physical_map", g)


class AtlasDecision(str, Enum):
    ROUTE = "ROUTE"
    CERTIFIED_IMPOSSIBLE = "CERTIFIED_IMPOSSIBLE"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class AtlasRoute:
    decision: AtlasDecision
    selected_policy: str | None
    certificate: RobustRepairCertificate | None
    per_policy: dict[str, RobustRepairCertificate]
    reason: str


def nominal_repair_set_contains(
    outer_map: np.ndarray,
    outer_radius: float,
    inner_map: np.ndarray,
    inner_radius: float,
    *,
    atol: float = 1e-9,
) -> bool:
    """Check K(inner) subset K(outer) for centered linear image balls.

    K(G,r) = {G x : ||x||_2 <= r}.

    Containment holds iff the inner image lies in the outer image and the
    minimum-norm outer preimage required for every inner point fits inside the
    outer radius.
    """

    A = np.asarray(outer_map, dtype=float)
    B = np.asarray(inner_map, dtype=float)
    if A.ndim != 2 or B.ndim != 2 or A.shape[0] != B.shape[0]:
        raise ValueError("maps must be 2D with common physical output dimension")
    if outer_radius < 0 or inner_radius < 0:
        return False

    A_pinv = np.linalg.pinv(A)
    projection_residual = np.linalg.norm(B - A @ A_pinv @ B, ord=2)
    scale = max(1.0, np.linalg.norm(B, ord=2))
    if projection_residual > atol * scale:
        return False

    required_outer_radius = (
        float(inner_radius) * float(np.linalg.norm(A_pinv @ B, ord=2))
    )
    return required_outer_radius <= outer_radius + atol


def route_by_repairability(
    policies: list[PolicyRepairSet],
    target_physical_correction: np.ndarray,
    *,
    residual_tolerance: float,
    switch_cost_weight: float = 1.0,
) -> AtlasRoute:
    """Route only through robust physical repairability certificates.

    Policies must already be expressed in the same canonical physical-command
    space. Raw task score/history is deliberately not used.
    """

    if not policies:
        raise ValueError("at least one policy is required")
    d = np.asarray(target_physical_correction, dtype=float)

    certs: dict[str, RobustRepairCertificate] = {}
    repairable: list[tuple[float, PolicyRepairSet, RobustRepairCertificate]] = []

    for p in policies:
        cert = robust_repair_certificate(
            p.physical_map,
            d,
            physical_map_uncertainty=PhysicalMapUncertainty(
                p.operator_uncertainty
            ),
            certified_radius=p.certified_radius,
            residual_tolerance=residual_tolerance,
        )
        certs[p.name] = cert
        if cert.decision is RobustRepairDecision.CERTIFIED_REPAIR:
            score = (
                cert.worst_case_residual_upper
                + switch_cost_weight * p.switch_cost
            )
            repairable.append((score, p, cert))

    if repairable:
        repairable.sort(key=lambda row: (row[0], row[1].name))
        _, chosen, cert = repairable[0]
        return AtlasRoute(
            decision=AtlasDecision.ROUTE,
            selected_policy=chosen.name,
            certificate=cert,
            per_policy=certs,
            reason="selected the lowest-cost policy with a robust repair certificate",
        )

    decisions = {c.decision for c in certs.values()}
    if decisions == {RobustRepairDecision.CERTIFIED_IMPOSSIBLE}:
        return AtlasRoute(
            decision=AtlasDecision.CERTIFIED_IMPOSSIBLE,
            selected_policy=None,
            certificate=None,
            per_policy=certs,
            reason="every policy in the atlas certifies the target outside its local repairability set",
        )

    return AtlasRoute(
        decision=AtlasDecision.INCONCLUSIVE,
        selected_policy=None,
        certificate=None,
        per_policy=certs,
        reason="no policy certifies repair and at least one policy remains uncertain",
    )
