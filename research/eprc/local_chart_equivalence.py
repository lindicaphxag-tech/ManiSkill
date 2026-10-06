from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .contract_signature import contracts_equivalent


@dataclass(frozen=True)
class LocalChartCertificate:
    minimum_singular_value: float
    condition_number: float
    locally_invertible: bool


def local_chart_certificate(
    chart_jacobian: np.ndarray,
    *,
    min_singular_value: float = 1e-8,
    max_condition_number: float = 1e8,
) -> LocalChartCertificate:
    j = np.asarray(chart_jacobian, dtype=float)
    if j.ndim != 2 or j.shape[0] != j.shape[1]:
        raise ValueError("local action chart Jacobian must be square")
    s = np.linalg.svd(j, compute_uv=False)
    minimum = float(s.min()) if s.size else 0.0
    maximum = float(s.max()) if s.size else 0.0
    condition = float("inf") if minimum == 0.0 else maximum / minimum
    invertible = (
        minimum >= min_singular_value and condition <= max_condition_number
    )
    return LocalChartCertificate(
        minimum_singular_value=minimum,
        condition_number=condition,
        locally_invertible=invertible,
    )


def cubic_chart_jacobian(action_phys: np.ndarray, beta: np.ndarray) -> np.ndarray:
    """Jacobian of h(a)=a+beta*a^3 at a physical action point."""

    a = np.asarray(action_phys, dtype=float)
    beta = np.asarray(beta, dtype=float)
    if a.shape != beta.shape:
        raise ValueError("action and beta must have the same shape")
    return np.diag(1.0 + 3.0 * beta * a**2)


def nonlinear_reparameterized_jacobians(
    jacobian_phys: np.ndarray,
    action_phys: np.ndarray,
    beta: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, LocalChartCertificate]:
    """Return raw chart-B CASJ and its semantic lift for a nonlinear local chart."""

    dh = cubic_chart_jacobian(action_phys, beta)
    cert = local_chart_certificate(dh)
    if not cert.locally_invertible:
        raise ValueError("action chart is not a stable local diffeomorphism")
    j_b = dh @ np.asarray(jacobian_phys, dtype=float)
    lift_b = np.linalg.inv(dh)
    return j_b, lift_b, cert


def verify_local_diffeomorphism_invariance(
    jacobian_phys: np.ndarray,
    action_phys: np.ndarray,
    beta: np.ndarray,
    *,
    tolerance: float = 1e-8,
) -> bool:
    j_phys = np.asarray(jacobian_phys, dtype=float)
    j_b, lift_b, _ = nonlinear_reparameterized_jacobians(
        j_phys, action_phys, beta
    )
    return contracts_equivalent(
        j_phys, np.eye(j_phys.shape[0]), j_b, lift_b, tolerance=tolerance
    )
