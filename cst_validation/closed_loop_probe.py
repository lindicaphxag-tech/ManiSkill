from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

try:
    from .closed_loop_certificate import (
        LocalClosedLoopTransportCertificate,
        synthesize_local_closed_loop_transport,
    )
except ImportError:  # Allow direct execution from cst_validation/.
    from closed_loop_certificate import (
        LocalClosedLoopTransportCertificate,
        synthesize_local_closed_loop_transport,
    )


ArrayQuery = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class EffectJacobianEstimate:
    jacobian: np.ndarray
    coarse_jacobian: np.ndarray
    scale_instability: float
    epsilon: float
    stable: bool
    query_count: int
    reason: str


@dataclass(frozen=True)
class HeldoutTransportWitness:
    accepted: bool
    max_abs_residual: float
    max_l2_residual: float
    mean_l2_residual: float
    worst_source_action: np.ndarray
    predicted_target_action: np.ndarray
    source_observable: np.ndarray
    target_observable: np.ndarray
    num_cases: int
    tolerance: float
    reason: str


@dataclass(frozen=True)
class BlackBoxClosedLoopCertificate:
    authorized: bool
    source_estimate: EffectJacobianEstimate
    target_estimate: EffectJacobianEstimate
    local_transport: LocalClosedLoopTransportCertificate | None
    heldout: HeldoutTransportWitness | None
    reason: str


def _vector(value, *, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 1 or out.size == 0:
        raise ValueError(f"{name} must be a non-empty vector")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def estimate_effect_jacobian(
    query: ArrayQuery,
    action0: np.ndarray,
    *,
    epsilon: float,
    max_scale_instability: float = 0.15,
) -> EffectJacobianEstimate:
    """Estimate an executable-effect Jacobian with two-scale central differences.

    query(action) must return the same declared augmented observable for every
    call and must restore all relevant physical/controller state between
    counterfactual queries.  The estimator does not assume how that restoration
    is implemented.
    """
    u0 = _vector(action0, name="action0")
    if epsilon <= 0 or not np.isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    if max_scale_instability < 0 or not np.isfinite(max_scale_instability):
        raise ValueError("max_scale_instability must be finite and non-negative")

    columns_fine: list[np.ndarray] = []
    columns_coarse: list[np.ndarray] = []
    observable_dim: int | None = None
    query_count = 0

    for j in range(u0.size):
        axis = np.zeros_like(u0)
        axis[j] = 1.0

        plus = _vector(query(u0 + epsilon * axis), name="query output")
        minus = _vector(query(u0 - epsilon * axis), name="query output")
        coarse_plus = _vector(query(u0 + 2.0 * epsilon * axis), name="query output")
        coarse_minus = _vector(query(u0 - 2.0 * epsilon * axis), name="query output")
        query_count += 4

        if observable_dim is None:
            observable_dim = plus.size
        if (
            plus.size != observable_dim
            or minus.size != observable_dim
            or coarse_plus.size != observable_dim
            or coarse_minus.size != observable_dim
        ):
            raise ValueError("query output dimension changed across probes")

        columns_fine.append((plus - minus) / (2.0 * epsilon))
        columns_coarse.append((coarse_plus - coarse_minus) / (4.0 * epsilon))

    fine = np.column_stack(columns_fine)
    coarse = np.column_stack(columns_coarse)
    denom = max(float(np.linalg.norm(fine, ord="fro")), 1e-12)
    instability = float(np.linalg.norm(fine - coarse, ord="fro") / denom)
    stable = bool(instability <= max_scale_instability)
    return EffectJacobianEstimate(
        jacobian=fine,
        coarse_jacobian=coarse,
        scale_instability=instability,
        epsilon=float(epsilon),
        stable=stable,
        query_count=query_count,
        reason=(
            "two-scale executable-effect Jacobian is stable"
            if stable
            else "finite-difference effect changes too much across probe scales"
        ),
    )


def validate_adapter_on_heldout(
    source_query: ArrayQuery,
    target_query: ArrayQuery,
    *,
    source_action0: np.ndarray,
    target_action0: np.ndarray,
    adapter: np.ndarray,
    heldout_source_deltas: np.ndarray,
    tolerance: float,
) -> HeldoutTransportWitness:
    """Falsify a local adapter on perturbations excluded from Jacobian fitting."""
    source0 = _vector(source_action0, name="source_action0")
    target0 = _vector(target_action0, name="target_action0")
    K = np.asarray(adapter, dtype=float)
    deltas = np.asarray(heldout_source_deltas, dtype=float)
    if K.shape[1] != source0.size or K.shape[0] != target0.size:
        raise ValueError("adapter dimensions do not match source/target actions")
    if deltas.ndim != 2 or deltas.shape[1] != source0.size or deltas.shape[0] == 0:
        raise ValueError("heldout_source_deltas must have shape [N, source_dim]")
    if tolerance < 0 or not np.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative")

    source_base = _vector(source_query(source0), name="source baseline")
    target_base = _vector(target_query(target0), name="target baseline")
    if source_base.shape != target_base.shape:
        raise ValueError("source and target observables differ in shape")

    l2_residuals: list[float] = []
    max_abs = 0.0
    worst_index = 0
    worst_source = source0.copy()
    worst_target = target0.copy()
    worst_source_obs = source_base.copy()
    worst_target_obs = target_base.copy()

    for i, delta in enumerate(deltas):
        src_action = source0 + delta
        tgt_action = target0 + K @ delta
        src_obs = _vector(source_query(src_action), name="source heldout")
        tgt_obs = _vector(target_query(tgt_action), name="target heldout")
        if src_obs.shape != source_base.shape or tgt_obs.shape != target_base.shape:
            raise ValueError("heldout observable dimension changed")

        # Compare counterfactual *effects* relative to each controller baseline.
        residual = (tgt_obs - target_base) - (src_obs - source_base)
        l2 = float(np.linalg.norm(residual))
        this_max_abs = float(np.max(np.abs(residual)))
        l2_residuals.append(l2)
        max_abs = max(max_abs, this_max_abs)
        if l2 >= l2_residuals[worst_index]:
            worst_index = i
            worst_source = src_action.copy()
            worst_target = tgt_action.copy()
            worst_source_obs = src_obs.copy()
            worst_target_obs = tgt_obs.copy()

    l2_array = np.asarray(l2_residuals)
    worst_l2 = float(np.max(l2_array))
    accepted = bool(worst_l2 <= tolerance)
    return HeldoutTransportWitness(
        accepted=accepted,
        max_abs_residual=max_abs,
        max_l2_residual=worst_l2,
        mean_l2_residual=float(np.mean(l2_array)),
        worst_source_action=worst_source,
        predicted_target_action=worst_target,
        source_observable=worst_source_obs,
        target_observable=worst_target_obs,
        num_cases=int(deltas.shape[0]),
        tolerance=float(tolerance),
        reason=(
            "all held-out executable effects remain within the frozen tolerance"
            if accepted
            else "a held-out counterexample violates the frozen transport tolerance"
        ),
    )


def certify_black_box_closed_loop_transport(
    source_query: ArrayQuery,
    target_query: ArrayQuery,
    *,
    source_action0: np.ndarray,
    target_action0: np.ndarray,
    source_epsilon: float,
    target_epsilon: float,
    heldout_source_deltas: np.ndarray,
    heldout_tolerance: float,
    max_scale_instability: float = 0.15,
    local_atol: float = 1e-10,
    local_rtol: float = 1e-10,
) -> BlackBoxClosedLoopCertificate:
    """Estimate, synthesize, and falsify a controller transport without gradients."""
    source_est = estimate_effect_jacobian(
        source_query,
        source_action0,
        epsilon=source_epsilon,
        max_scale_instability=max_scale_instability,
    )
    target_est = estimate_effect_jacobian(
        target_query,
        target_action0,
        epsilon=target_epsilon,
        max_scale_instability=max_scale_instability,
    )
    if not source_est.stable or not target_est.stable:
        return BlackBoxClosedLoopCertificate(
            authorized=False,
            source_estimate=source_est,
            target_estimate=target_est,
            local_transport=None,
            heldout=None,
            reason="refused because at least one executable-effect Jacobian is scale-unstable",
        )

    local = synthesize_local_closed_loop_transport(
        source_est.jacobian,
        target_est.jacobian,
        atol=local_atol,
        rtol=local_rtol,
    )
    heldout = validate_adapter_on_heldout(
        source_query,
        target_query,
        source_action0=source_action0,
        target_action0=target_action0,
        adapter=local.adapter,
        heldout_source_deltas=heldout_source_deltas,
        tolerance=heldout_tolerance,
    )
    authorized = bool(local.exact and heldout.accepted)
    return BlackBoxClosedLoopCertificate(
        authorized=authorized,
        source_estimate=source_est,
        target_estimate=target_est,
        local_transport=local,
        heldout=heldout,
        reason=(
            "local image inclusion and held-out counterfactual validation both pass"
            if authorized
            else "transport refused by local representability or held-out falsification"
        ),
    )
