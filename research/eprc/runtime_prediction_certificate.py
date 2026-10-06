from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class RuntimePredictionDecision(str, Enum):
    CERTIFIED_PREDICTION = "CERTIFIED_PREDICTION"
    INCONCLUSIVE = "INCONCLUSIVE"
    REFUSE_OUTSIDE_CERTIFIED_REGION = "REFUSE_OUTSIDE_CERTIFIED_REGION"


@dataclass(frozen=True)
class RuntimePredictionCertificate:
    """Oracle-free certificate for one local frozen-policy response prediction."""

    decision: RuntimePredictionDecision
    support_delta: np.ndarray
    predicted_correction: np.ndarray
    support_norm: float
    certified_radius: float
    epsilon_g: float
    worst_case_prediction_error: float
    residual_tolerance: float
    reason: str


def certify_runtime_prediction(
    physical_map_estimate: np.ndarray,
    support_delta: np.ndarray,
    *,
    epsilon_g: float,
    certified_radius: float,
    residual_tolerance: float,
    atol: float = 1e-12,
) -> RuntimePredictionCertificate:
    g = np.asarray(physical_map_estimate, dtype=float)
    xi = np.asarray(support_delta, dtype=float)

    if g.ndim != 2 or xi.ndim != 1 or g.shape[1] != xi.size:
        raise ValueError("physical map / support delta dimensions differ")
    if epsilon_g < 0 or residual_tolerance < 0:
        raise ValueError("epsilon_g and residual_tolerance must be non-negative")

    predicted = g @ xi
    support_norm = float(np.linalg.norm(xi))

    if certified_radius < 0 or support_norm > certified_radius + atol:
        return RuntimePredictionCertificate(
            decision=RuntimePredictionDecision.REFUSE_OUTSIDE_CERTIFIED_REGION,
            support_delta=xi.copy(),
            predicted_correction=predicted,
            support_norm=support_norm,
            certified_radius=float(certified_radius),
            epsilon_g=float(epsilon_g),
            worst_case_prediction_error=float("inf"),
            residual_tolerance=float(residual_tolerance),
            reason=(
                "requested disturbance lies outside the certified local "
                "repairability/authority region"
            ),
        )

    error_bound = float(epsilon_g * support_norm)
    if error_bound <= residual_tolerance + atol:
        decision = RuntimePredictionDecision.CERTIFIED_PREDICTION
        reason = (
            "operator-norm map uncertainty certifies the predicted correction "
            "without a fresh policy oracle"
        )
    else:
        decision = RuntimePredictionDecision.INCONCLUSIVE
        reason = (
            "local map is admissible but its uncertainty is too large to "
            "certify this request at the frozen tolerance"
        )

    return RuntimePredictionCertificate(
        decision=decision,
        support_delta=xi.copy(),
        predicted_correction=predicted,
        support_norm=support_norm,
        certified_radius=float(certified_radius),
        epsilon_g=float(epsilon_g),
        worst_case_prediction_error=error_bound,
        residual_tolerance=float(residual_tolerance),
        reason=reason,
    )


def verify_runtime_prediction_certificate(
    physical_map_estimate: np.ndarray,
    *,
    certificate: RuntimePredictionCertificate,
    atol: float = 1e-9,
) -> bool:
    """Verify the certificate without calling the frozen policy."""

    try:
        expected = certify_runtime_prediction(
            physical_map_estimate,
            certificate.support_delta,
            epsilon_g=certificate.epsilon_g,
            certified_radius=certificate.certified_radius,
            residual_tolerance=certificate.residual_tolerance,
        )
    except ValueError:
        return False

    if expected.decision is not certificate.decision:
        return False
    if not np.allclose(
        expected.predicted_correction,
        certificate.predicted_correction,
        atol=atol,
        rtol=atol,
    ):
        return False

    for field in (
        "support_norm",
        "certified_radius",
        "epsilon_g",
        "residual_tolerance",
    ):
        if not np.isclose(
            getattr(expected, field),
            getattr(certificate, field),
            atol=atol,
            rtol=atol,
        ):
            return False

    if np.isinf(expected.worst_case_prediction_error):
        if not np.isinf(certificate.worst_case_prediction_error):
            return False
    elif not np.isclose(
        expected.worst_case_prediction_error,
        certificate.worst_case_prediction_error,
        atol=atol,
        rtol=atol,
    ):
        return False

    return True
