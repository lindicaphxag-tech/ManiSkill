from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .contract_signature import contract_signature, signature_distance
from .local_chart_equivalence import local_chart_certificate


@dataclass(frozen=True)
class BilateralChartCertificate:
    action_locally_invertible: bool
    support_locally_invertible: bool
    action_condition_number: float
    support_condition_number: float


def canonicalize_dec_jacobian(
    raw_action_wrt_support_chart: np.ndarray,
    action_chart_to_physical: np.ndarray,
    physical_support_to_support_chart: np.ndarray,
) -> np.ndarray:
    """Lift both action and support coordinates into canonical physical spaces.

    raw_action_wrt_support_chart = da_chart / dxi_chart
    action_chart_to_physical      = dy_phys / da_chart
    physical_support_to_support_chart = dxi_chart / ds_phys

    Therefore J_phys = (dy/da) (da/dxi) (dxi/ds).
    """

    raw = np.asarray(raw_action_wrt_support_chart, dtype=float)
    a_lift = np.asarray(action_chart_to_physical, dtype=float)
    s_lift = np.asarray(physical_support_to_support_chart, dtype=float)
    if raw.ndim != 2 or a_lift.ndim != 2 or s_lift.ndim != 2:
        raise ValueError("all Jacobians must be 2D")
    if a_lift.shape[1] != raw.shape[0]:
        raise ValueError("action chart dimensions are incompatible")
    if raw.shape[1] != s_lift.shape[0]:
        raise ValueError("support chart dimensions are incompatible")
    return a_lift @ raw @ s_lift


def bilateral_chart_certificate(
    action_chart_jacobian: np.ndarray,
    support_chart_jacobian: np.ndarray,
) -> BilateralChartCertificate:
    a = local_chart_certificate(action_chart_jacobian)
    s = local_chart_certificate(support_chart_jacobian)
    return BilateralChartCertificate(
        action_locally_invertible=a.locally_invertible,
        support_locally_invertible=s.locally_invertible,
        action_condition_number=a.condition_number,
        support_condition_number=s.condition_number,
    )


def bilateral_contracts_equivalent(
    raw_a: np.ndarray,
    action_lift_a: np.ndarray,
    support_lift_a: np.ndarray,
    raw_b: np.ndarray,
    action_lift_b: np.ndarray,
    support_lift_b: np.ndarray,
    *,
    tolerance: float = 1e-7,
) -> bool:
    j_a = canonicalize_dec_jacobian(raw_a, action_lift_a, support_lift_a)
    j_b = canonicalize_dec_jacobian(raw_b, action_lift_b, support_lift_b)
    return signature_distance(contract_signature(j_a), contract_signature(j_b)) <= tolerance
