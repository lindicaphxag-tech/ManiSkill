from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .robust_repairability import RobustRepairDecision


class EvidenceBottleneck(str, Enum):
    TERMINAL = "TERMINAL"
    INFORMATION_LIMITED = "INFORMATION_LIMITED"
    STOCHASTIC_LIMITED = "STOCHASTIC_LIMITED"
    LOCALITY_LIMITED = "LOCALITY_LIMITED"
    MIXED_UNCERTAINTY = "MIXED_UNCERTAINTY"


@dataclass(frozen=True)
class EvidenceAction:
    bottleneck: EvidenceBottleneck
    recommended_action: str
    additional_same_scale_queries_authorized: bool
    rationale: str


def route_inconclusive_certificate(
    *,
    robust_decision: RobustRepairDecision,
    planned_decision: RobustRepairDecision,
    stochastic_radius: float,
    scale_drift_radius: float,
    atol: float = 1e-12,
) -> EvidenceAction:
    """Route the *cause* of an unresolved robust repairability certificate.

    The key distinction is whether more observations can plausibly reduce the
    uncertainty source currently blocking a decision.

    - If the robust certificate is already terminal, stop.
    - If an information-only AMRC plan predicts a terminal certificate, execute
      only those planned probes.
    - If finite-difference scale drift dominates and AMRC remains inconclusive,
      more same-scale repeats cannot remove the observed locality/model bias.
      Shrink the physical trust region or fit a richer local model instead.
    - If stochastic variation dominates, control/repeat randomness before
      changing model order.
    - If the two sources are comparable, separate them experimentally rather
      than attributing the failure to one source.
    """

    if stochastic_radius < 0 or scale_drift_radius < 0:
        raise ValueError("uncertainty radii must be nonnegative")

    if robust_decision is not RobustRepairDecision.INCONCLUSIVE:
        return EvidenceAction(
            bottleneck=EvidenceBottleneck.TERMINAL,
            recommended_action="stop probing; use the existing robust certificate",
            additional_same_scale_queries_authorized=False,
            rationale="the current robust certificate is already decisive",
        )

    if planned_decision is not RobustRepairDecision.INCONCLUSIVE:
        return EvidenceAction(
            bottleneck=EvidenceBottleneck.INFORMATION_LIMITED,
            recommended_action=(
                "execute only the certificate-directed probes in the frozen AMRC plan, "
                "then recompute the physical map and certificate"
            ),
            additional_same_scale_queries_authorized=True,
            rationale=(
                "the information-only update is predicted to cross a certificate boundary"
            ),
        )

    if scale_drift_radius > stochastic_radius + atol:
        return EvidenceAction(
            bottleneck=EvidenceBottleneck.LOCALITY_LIMITED,
            recommended_action=(
                "do not spend more same-scale repeat queries; reduce physical probe scale "
                "and trust radius, or fit/validate a higher-order local response model"
            ),
            additional_same_scale_queries_authorized=False,
            rationale=(
                "finite-difference scale drift dominates repeated-probe variation and "
                "the information-only AMRC plan still cannot resolve the certificate"
            ),
        )

    if stochastic_radius > scale_drift_radius + atol:
        return EvidenceAction(
            bottleneck=EvidenceBottleneck.STOCHASTIC_LIMITED,
            recommended_action=(
                "increase paired stochastic replicates or control policy randomness before "
                "changing the local response model"
            ),
            additional_same_scale_queries_authorized=True,
            rationale=(
                "repeated-probe variation dominates finite-difference scale drift"
            ),
        )

    return EvidenceAction(
        bottleneck=EvidenceBottleneck.MIXED_UNCERTAINTY,
        recommended_action=(
            "run a factorial probe-scale x randomness diagnostic; do not attribute the "
            "inconclusive certificate to sampling or locality alone"
        ),
        additional_same_scale_queries_authorized=False,
        rationale="stochastic and locality uncertainty are indistinguishable at current resolution",
    )
