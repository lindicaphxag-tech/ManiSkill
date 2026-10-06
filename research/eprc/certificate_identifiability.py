from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf

import numpy as np

from .certificate_directed_probing import ProbeInformation


@dataclass(frozen=True)
class OptimalProbe:
    probe: np.ndarray
    variance_before: float
    variance_after: float
    variance_reduction: float


@dataclass(frozen=True)
class RepairIdentifiabilityBudget:
    nominal_residual: float
    residual_tolerance: float
    uncertainty_slack: float
    required_directional_variance: float
    current_directional_variance: float
    repeated_probe_count_estimate: int | None
    symmetric_policy_evaluations_estimate: int | None
    information_only: bool


def optimal_continuous_directional_probe(
    probe_information: ProbeInformation,
    target_direction: np.ndarray,
    *,
    max_probe_norm: float = 1.0,
    atol: float = 1e-12,
) -> OptimalProbe:
    """Closed-form one-step probe minimizing directional posterior radius.

    With information matrix V and a rank-one update V' = V + z z^T,
    Sherman-Morrison gives

        x^T V'^-1 x
        = x^T V^-1 x
          - (x^T V^-1 z)^2 / (1 + z^T V^-1 z).

    Under ||z||_2 <= m, the maximizing direction is

        z* ∝ (V + m^2 I)^-1 x,

    with ||z*|| = m unless x=0.
    """

    if max_probe_norm <= 0:
        raise ValueError("max_probe_norm must be positive")

    V = probe_information.information
    x = np.asarray(target_direction, dtype=float)
    if x.ndim != 1 or x.size != V.shape[0]:
        raise ValueError("target direction dimension mismatch")

    Vinv_x = np.linalg.solve(V, x)
    before = float(x @ Vinv_x)

    if np.linalg.norm(x) <= atol:
        return OptimalProbe(
            probe=np.zeros_like(x),
            variance_before=before,
            variance_after=before,
            variance_reduction=0.0,
        )

    raw = np.linalg.solve(V + (max_probe_norm**2) * np.eye(V.shape[0]), x)
    raw_norm = float(np.linalg.norm(raw))
    if raw_norm <= atol:
        return OptimalProbe(
            probe=np.zeros_like(x),
            variance_before=before,
            variance_after=before,
            variance_reduction=0.0,
        )

    z = max_probe_norm * raw / raw_norm
    next_info = probe_information.update(z)
    after = float(x @ np.linalg.solve(next_info.information, x))
    return OptimalProbe(
        probe=z,
        variance_before=before,
        variance_after=after,
        variance_reduction=float(before - after),
    )


def repeated_probe_count_for_directional_radius(
    probe_information: ProbeInformation,
    target_direction: np.ndarray,
    probe: np.ndarray,
    *,
    target_radius: float,
    atol: float = 1e-12,
) -> int | None:
    """Exact repeated-rank-one count under a fixed map/information model.

    Returns the smallest integer k >= 0 such that repeatedly observing the same
    probe z makes

        beta * sqrt(x^T (V + k z z^T)^-1 x) <= target_radius.

    Returns None when repetition of that single probe can never meet the target.
    """

    if target_radius < 0:
        raise ValueError("target_radius must be nonnegative")

    V = probe_information.information
    beta = float(probe_information.beta)
    x = np.asarray(target_direction, dtype=float)
    z = np.asarray(probe, dtype=float)
    if x.ndim != 1 or z.ndim != 1 or x.size != V.shape[0] or z.size != V.shape[0]:
        raise ValueError("dimension mismatch")

    if beta == 0:
        return 0

    Vinv_x = np.linalg.solve(V, x)
    Vinv_z = np.linalg.solve(V, z)
    A = float(x @ Vinv_x)
    current_radius = beta * np.sqrt(max(0.0, A))
    if current_radius <= target_radius + atol:
        return 0

    T = (target_radius / beta) ** 2
    B = float(x @ Vinv_z) ** 2
    C = float(z @ Vinv_z)
    deficit = A - T
    denom = B - C * deficit

    if denom <= atol:
        return None

    k_real = deficit / denom
    k = max(0, int(ceil(k_real - atol)))

    # Guard the algebra with a direct check and correct rare floating boundary
    # cases without changing the closed-form estimate.
    def radius_after(count: int) -> float:
        info = V + count * np.outer(z, z)
        var = float(x @ np.linalg.solve(info, x))
        return beta * np.sqrt(max(0.0, var))

    while k > 0 and radius_after(k - 1) <= target_radius + atol:
        k -= 1
    while radius_after(k) > target_radius + atol:
        k += 1
        if k > 10_000_000:
            return None
    return k


def repair_identifiability_budget(
    probe_information: ProbeInformation,
    support_delta: np.ndarray,
    *,
    nominal_residual: float,
    residual_tolerance: float,
    max_probe_norm: float = 1.0,
) -> RepairIdentifiabilityBudget:
    """Information-only budget needed to certify a fixed nominal repair.

    This freezes the current map estimate and asks only how much directional
    uncertainty must shrink. Future observations may change the map, so the
    result is a planning estimate, not an execution certificate.
    """

    if nominal_residual < 0 or residual_tolerance < 0:
        raise ValueError("residuals/tolerance must be nonnegative")

    x = np.asarray(support_delta, dtype=float)
    beta = float(probe_information.beta)
    current_var = float(x @ np.linalg.solve(probe_information.information, x))
    slack = float(residual_tolerance - nominal_residual)

    if slack < 0:
        return RepairIdentifiabilityBudget(
            nominal_residual=float(nominal_residual),
            residual_tolerance=float(residual_tolerance),
            uncertainty_slack=slack,
            required_directional_variance=0.0,
            current_directional_variance=current_var,
            repeated_probe_count_estimate=None,
            symmetric_policy_evaluations_estimate=None,
            information_only=True,
        )

    if beta == 0:
        required_var = inf
        count = 0
    else:
        required_var = float((slack / beta) ** 2)
        target_radius = slack
        optimum = optimal_continuous_directional_probe(
            probe_information, x, max_probe_norm=max_probe_norm
        )
        count = repeated_probe_count_for_directional_radius(
            probe_information,
            x,
            optimum.probe,
            target_radius=target_radius,
        )

    return RepairIdentifiabilityBudget(
        nominal_residual=float(nominal_residual),
        residual_tolerance=float(residual_tolerance),
        uncertainty_slack=slack,
        required_directional_variance=required_var,
        current_directional_variance=current_var,
        repeated_probe_count_estimate=count,
        symmetric_policy_evaluations_estimate=None if count is None else 2 * count,
        information_only=True,
    )
