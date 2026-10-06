from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .robust_repairability import RobustRepairDecision


class EvidenceBottleneck(str, Enum):
    NONE = "NONE"
    LOCALITY_SCALE = "LOCALITY_SCALE"
    STOCHASTIC_REPEATABILITY = "STOCHASTIC_REPEATABILITY"
    CANDIDATE_DIRECTION = "CANDIDATE_DIRECTION"
    GLOBAL_DIRECTIONAL_COVERAGE = "GLOBAL_DIRECTIONAL_COVERAGE"
    CONTROLLER_AUTHORITY = "CONTROLLER_AUTHORITY"


class ExperimentKind(str, Enum):
    STOP = "STOP"
    SHRINK_SYMMETRIC_SCALE = "SHRINK_SYMMETRIC_SCALE"
    REPEAT_PAIRED_RANDOMNESS = "REPEAT_PAIRED_RANDOMNESS"
    TARGET_REPAIR_DIRECTION = "TARGET_REPAIR_DIRECTION"
    PROBE_WEAKEST_DIRECTION = "PROBE_WEAKEST_DIRECTION"
    REPLAN_CONTROLLER_AUTHORITY = "REPLAN_CONTROLLER_AUTHORITY"


@dataclass(frozen=True)
class ExperimentRoutingDecision:
    bottleneck: EvidenceBottleneck
    experiment: ExperimentKind
    dominant_uncertainty: float
    reason: str


def route_certificate_resolving_experiment(
    *,
    decision: RobustRepairDecision,
    stochastic_radius: float,
    scale_drift_radius: float,
    candidate_directional_uncertainty: float,
    global_directional_uncertainty: float,
    authority_is_bottleneck: bool = False,
    dominance_atol: float = 1e-12,
) -> ExperimentRoutingDecision:
    """Route an inconclusive repair certificate to the experiment that can
    actually interrogate its dominant uncertainty source.

    The key invariant is *non-substitutability*: evidence collected for one
    uncertainty mechanism must not be credited as shrinking another.

    - locality/finite-difference drift -> smaller symmetric perturbation scale;
    - policy stochasticity -> paired repeated policy queries;
    - uncertainty along the candidate repair direction -> targeted probe;
    - poor global support coverage -> weakest-information-direction probe;
    - controller authority bottleneck -> no amount of probing fixes authority.

    This is a routing rule, not a statistical guarantee that one experiment will
    be sufficient to resolve the certificate.
    """

    vals = {
        EvidenceBottleneck.LOCALITY_SCALE: float(scale_drift_radius),
        EvidenceBottleneck.STOCHASTIC_REPEATABILITY: float(stochastic_radius),
        EvidenceBottleneck.CANDIDATE_DIRECTION: float(candidate_directional_uncertainty),
        EvidenceBottleneck.GLOBAL_DIRECTIONAL_COVERAGE: float(global_directional_uncertainty),
    }
    if any(v < 0 for v in vals.values()):
        raise ValueError("uncertainty radii must be nonnegative")

    if decision is not RobustRepairDecision.INCONCLUSIVE:
        return ExperimentRoutingDecision(
            bottleneck=EvidenceBottleneck.NONE,
            experiment=ExperimentKind.STOP,
            dominant_uncertainty=0.0,
            reason="certificate is already resolved; additional probing is not justified",
        )

    if authority_is_bottleneck:
        return ExperimentRoutingDecision(
            bottleneck=EvidenceBottleneck.CONTROLLER_AUTHORITY,
            experiment=ExperimentKind.REPLAN_CONTROLLER_AUTHORITY,
            dominant_uncertainty=0.0,
            reason="controller authority is the active bottleneck; more policy probing cannot create missing actuation authority",
        )

    # Deterministic priority only breaks numerical ties. Locality comes first
    # because treating curvature as reducible statistical uncertainty is the
    # most dangerous silent failure mode.
    priority = (
        EvidenceBottleneck.LOCALITY_SCALE,
        EvidenceBottleneck.STOCHASTIC_REPEATABILITY,
        EvidenceBottleneck.CANDIDATE_DIRECTION,
        EvidenceBottleneck.GLOBAL_DIRECTIONAL_COVERAGE,
    )
    maximum = max(vals.values())
    if maximum <= dominance_atol:
        return ExperimentRoutingDecision(
            bottleneck=EvidenceBottleneck.NONE,
            experiment=ExperimentKind.STOP,
            dominant_uncertainty=maximum,
            reason="no measured uncertainty source is large enough to justify another probe",
        )

    bottleneck = next(
        b for b in priority if abs(vals[b] - maximum) <= dominance_atol
    )
    experiment = {
        EvidenceBottleneck.LOCALITY_SCALE: ExperimentKind.SHRINK_SYMMETRIC_SCALE,
        EvidenceBottleneck.STOCHASTIC_REPEATABILITY: ExperimentKind.REPEAT_PAIRED_RANDOMNESS,
        EvidenceBottleneck.CANDIDATE_DIRECTION: ExperimentKind.TARGET_REPAIR_DIRECTION,
        EvidenceBottleneck.GLOBAL_DIRECTIONAL_COVERAGE: ExperimentKind.PROBE_WEAKEST_DIRECTION,
    }[bottleneck]

    reasons = {
        EvidenceBottleneck.LOCALITY_SCALE:
            "finite-difference scale drift dominates; collect a smaller symmetric physical perturbation before adding directional samples",
        EvidenceBottleneck.STOCHASTIC_REPEATABILITY:
            "paired-policy stochastic variation dominates; repeat the same intervention under frozen state and controlled randomness",
        EvidenceBottleneck.CANDIDATE_DIRECTION:
            "uncertainty along the requested repair direction dominates; target that support direction",
        EvidenceBottleneck.GLOBAL_DIRECTIONAL_COVERAGE:
            "global support coverage dominates the impossibility bound; probe the weakest information direction",
    }
    return ExperimentRoutingDecision(
        bottleneck=bottleneck,
        experiment=experiment,
        dominant_uncertainty=maximum,
        reason=reasons[bottleneck],
    )


def experiment_can_address(
    experiment: ExperimentKind,
    bottleneck: EvidenceBottleneck,
) -> bool:
    """Fail-closed provenance rule for evidence updates."""

    allowed = {
        EvidenceBottleneck.NONE: {ExperimentKind.STOP},
        EvidenceBottleneck.LOCALITY_SCALE: {ExperimentKind.SHRINK_SYMMETRIC_SCALE},
        EvidenceBottleneck.STOCHASTIC_REPEATABILITY: {ExperimentKind.REPEAT_PAIRED_RANDOMNESS},
        EvidenceBottleneck.CANDIDATE_DIRECTION: {ExperimentKind.TARGET_REPAIR_DIRECTION},
        EvidenceBottleneck.GLOBAL_DIRECTIONAL_COVERAGE: {ExperimentKind.PROBE_WEAKEST_DIRECTION},
        EvidenceBottleneck.CONTROLLER_AUTHORITY: {ExperimentKind.REPLAN_CONTROLLER_AUTHORITY},
    }
    return experiment in allowed[bottleneck]
