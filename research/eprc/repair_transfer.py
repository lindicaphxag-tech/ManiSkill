from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RepairTransferCertificate:
    operator_gap: float
    source_estimation_error: float
    target_estimation_error: float
    target_remainder_lipschitz: float
    disturbance_norm: float
    target_min_authority_singular: float
    representability_margin: float
    predicted_transfer_error_bound: float
    error_tolerance: float
    authorized: bool
    reason: str


def repair_transfer_certificate(
    source_j_phys_est: np.ndarray,
    target_j_phys_est: np.ndarray,
    *,
    source_estimation_error: float,
    target_estimation_error: float,
    target_remainder_lipschitz: float,
    disturbance_norm: float,
    target_min_authority_singular: float,
    representability_margin: float,
    error_tolerance: float,
    min_authority_singular: float = 1e-8,
) -> RepairTransferCertificate:
    """Authorize reuse of a source-policy linear repair on a target policy.

    For true target response Delta y_B = J_B delta_s + r_B with
    ||r_B|| <= 0.5 L_B ||delta_s||^2, reusing hat J_A delta_s is bounded by

    (||hat J_B-hat J_A||_2 + 2 eps_A + eps_B)||delta_s||
    + 0.5 L_B ||delta_s||^2.

    The inequality is standard perturbation analysis. The runtime contribution
    is using intervention-identified physical-operator mismatch plus controller
    authority to fail closed on cross-policy repair reuse.
    """

    a = np.asarray(source_j_phys_est, dtype=float)
    b = np.asarray(target_j_phys_est, dtype=float)

    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("physical response operators must be matrices")
    if a.shape != b.shape:
        return RepairTransferCertificate(
            operator_gap=float("inf"),
            source_estimation_error=float(source_estimation_error),
            target_estimation_error=float(target_estimation_error),
            target_remainder_lipschitz=float(target_remainder_lipschitz),
            disturbance_norm=float(disturbance_norm),
            target_min_authority_singular=float(target_min_authority_singular),
            representability_margin=float(representability_margin),
            predicted_transfer_error_bound=float("inf"),
            error_tolerance=float(error_tolerance),
            authorized=False,
            reason="canonical physical operator shapes differ",
        )

    for name, value in {
        "source_estimation_error": source_estimation_error,
        "target_estimation_error": target_estimation_error,
        "target_remainder_lipschitz": target_remainder_lipschitz,
        "disturbance_norm": disturbance_norm,
        "error_tolerance": error_tolerance,
    }.items():
        if value < 0:
            raise ValueError(f"{name} must be non-negative")

    gap = float(np.linalg.norm(b - a, ord=2))
    r = float(disturbance_norm)
    bound = (
        gap + 2.0 * float(source_estimation_error) + float(target_estimation_error)
    ) * r + 0.5 * float(target_remainder_lipschitz) * r * r

    if representability_margin < 0:
        authorized = False
        reason = "target physical command is outside controller authority"
    elif target_min_authority_singular < min_authority_singular:
        authorized = False
        reason = "target controller has lost a required local physical direction"
    elif bound > error_tolerance:
        authorized = False
        reason = "predicted cross-policy repair error exceeds tolerance"
    else:
        authorized = True
        reason = "cross-policy repair reuse is certified within tolerance"

    return RepairTransferCertificate(
        operator_gap=gap,
        source_estimation_error=float(source_estimation_error),
        target_estimation_error=float(target_estimation_error),
        target_remainder_lipschitz=float(target_remainder_lipschitz),
        disturbance_norm=r,
        target_min_authority_singular=float(target_min_authority_singular),
        representability_margin=float(representability_margin),
        predicted_transfer_error_bound=float(bound),
        error_tolerance=float(error_tolerance),
        authorized=authorized,
        reason=reason,
    )


def transferred_repair(
    source_j_phys_est: np.ndarray,
    support_delta: np.ndarray,
) -> np.ndarray:
    j = np.asarray(source_j_phys_est, dtype=float)
    delta = np.asarray(support_delta, dtype=float)
    if j.ndim != 2 or delta.ndim != 1 or j.shape[1] != delta.shape[0]:
        raise ValueError("operator/support dimensions are incompatible")
    return j @ delta
