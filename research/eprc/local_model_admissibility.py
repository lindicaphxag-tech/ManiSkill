from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import inf, log

import numpy as np

from .robust_repairability import empirical_operator_envelope


class LocalModelStatus(str, Enum):
    FIRST_ORDER_ADMISSIBLE = "FIRST_ORDER_ADMISSIBLE"
    STOCHASTICALLY_UNRESOLVED = "STOCHASTICALLY_UNRESOLVED"
    FIRST_ORDER_REJECTED = "FIRST_ORDER_REJECTED"


@dataclass(frozen=True)
class LocalModelAdmissibility:
    status: LocalModelStatus
    coarse_fine_drift: float
    fine_finer_drift: float
    fine_stochastic_radius: float
    finer_stochastic_radius: float
    contraction_ratio: float
    observed_convergence_order: float
    same_scale_queries_authorized: bool
    first_order_crg_authorized: bool
    route: str
    reason: str


def assess_first_order_admissibility(
    *,
    coarse_map: np.ndarray,
    fine_map_replicates: np.ndarray,
    finer_map_replicates: np.ndarray,
    scale_ratio: float = 2.0,
    contraction_threshold: float = 0.75,
    stochastic_dominance_ratio: float = 1.0,
    quantile: float = 1.0,
    atol: float = 1e-12,
) -> LocalModelAdmissibility:
    """Decide whether a first-order local repair model is empirically admissible.

    The gate separates two causes of an unstable derivative estimate:

    * stochastic uncertainty: repeated same-scale probes disagree;
    * locality/model-order failure: repeated probes agree, but derivative
      estimates do not contract as the physical perturbation scale shrinks.

    Only the latter is evidence against the first-order model itself.
    """

    if scale_ratio <= 1:
        raise ValueError("scale_ratio must be > 1")
    if contraction_threshold <= 0:
        raise ValueError("contraction_threshold must be positive")
    if stochastic_dominance_ratio < 0:
        raise ValueError("stochastic_dominance_ratio must be nonnegative")

    coarse = np.asarray(coarse_map, dtype=float)
    fine = np.asarray(fine_map_replicates, dtype=float)
    finer = np.asarray(finer_map_replicates, dtype=float)

    if fine.ndim != 3 or finer.ndim != 3 or fine.shape[1:] != finer.shape[1:]:
        raise ValueError("fine/finer replicates must have compatible [n,p,s] shape")
    if coarse.shape != fine.shape[1:]:
        raise ValueError("coarse map shape must match replicate map shape")

    fine_center, fine_noise = empirical_operator_envelope(fine, quantile=quantile)
    finer_center, finer_noise = empirical_operator_envelope(finer, quantile=quantile)

    d1 = float(np.linalg.norm(coarse - fine_center, ord=2))
    d2 = float(np.linalg.norm(fine_center - finer_center, ord=2))

    if d1 <= atol:
        ratio = 0.0 if d2 <= atol else inf
    else:
        ratio = d2 / d1

    if d1 <= atol and d2 <= atol:
        order = inf
    elif d1 <= atol:
        order = -inf
    elif d2 <= atol:
        order = inf
    else:
        order = log(d1 / d2) / log(scale_ratio)

    noise = max(float(fine_noise.epsilon_g), float(finer_noise.epsilon_g))
    locality_signal = max(d1, d2)

    if noise > atol and locality_signal <= stochastic_dominance_ratio * noise:
        return LocalModelAdmissibility(
            status=LocalModelStatus.STOCHASTICALLY_UNRESOLVED,
            coarse_fine_drift=d1,
            fine_finer_drift=d2,
            fine_stochastic_radius=float(fine_noise.epsilon_g),
            finer_stochastic_radius=float(finer_noise.epsilon_g),
            contraction_ratio=float(ratio),
            observed_convergence_order=float(order),
            same_scale_queries_authorized=True,
            first_order_crg_authorized=False,
            route="COLLECT_SAME_SCALE_REPLICATES",
            reason=(
                "scale-to-scale drift is not distinguishable from repeated-probe "
                "stochastic variation; gather more paired same-scale evidence before "
                "judging local model order"
            ),
        )

    if ratio <= contraction_threshold:
        return LocalModelAdmissibility(
            status=LocalModelStatus.FIRST_ORDER_ADMISSIBLE,
            coarse_fine_drift=d1,
            fine_finer_drift=d2,
            fine_stochastic_radius=float(fine_noise.epsilon_g),
            finer_stochastic_radius=float(finer_noise.epsilon_g),
            contraction_ratio=float(ratio),
            observed_convergence_order=float(order),
            same_scale_queries_authorized=False,
            first_order_crg_authorized=True,
            route="FIRST_ORDER_CRG",
            reason=(
                "multi-scale derivative drift contracts beyond the frozen threshold "
                "and is not stochastic-dominated"
            ),
        )

    return LocalModelAdmissibility(
        status=LocalModelStatus.FIRST_ORDER_REJECTED,
        coarse_fine_drift=d1,
        fine_finer_drift=d2,
        fine_stochastic_radius=float(fine_noise.epsilon_g),
        finer_stochastic_radius=float(finer_noise.epsilon_g),
        contraction_ratio=float(ratio),
        observed_convergence_order=float(order),
        same_scale_queries_authorized=False,
        first_order_crg_authorized=False,
        route="REQUERY_OR_RICHER_LOCAL_MODEL",
        reason=(
            "repeated probes are sufficiently stable to expose scale behavior, but "
            "the derivative estimate does not contract as perturbations shrink; "
            "additional same-scale queries would create false confidence"
        ),
    )
