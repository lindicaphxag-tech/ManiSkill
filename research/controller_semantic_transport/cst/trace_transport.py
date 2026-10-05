from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class TraceTransportStep:
    iteration: int
    action: np.ndarray
    residual_norm: float
    relative_residual: float
    jacobian_condition: float
    accepted_step: bool


@dataclass(frozen=True)
class TraceTransportCertificate:
    accepted: bool
    action: np.ndarray
    source_trace: np.ndarray
    matched_trace: np.ndarray
    residual_norm: float
    relative_residual: float
    improvement_ratio: float
    jacobian_condition: float
    saturation_margin: float
    iterations: int
    query_count: int
    reason: str
    history: tuple[TraceTransportStep, ...]


def _flatten_trace(trace: np.ndarray) -> np.ndarray:
    trace = np.asarray(trace, dtype=float)
    if trace.size == 0 or not np.all(np.isfinite(trace)):
        raise ValueError("trace must be finite and non-empty")
    return trace.reshape(-1)


def _saturation_margin(action: np.ndarray, low: np.ndarray, high: np.ndarray) -> float:
    span = high - low
    left = (action - low) / span
    right = (high - action) / span
    return float(np.min(np.minimum(left, right)))


def _finite_difference_jacobian(
    oracle: Callable[[np.ndarray], np.ndarray],
    action: np.ndarray,
    *,
    low: np.ndarray,
    high: np.ndarray,
    probe_fraction: float,
) -> tuple[np.ndarray, int]:
    dim = action.size
    base_span = high - low
    columns = []
    queries = 0

    for j in range(dim):
        h = float(probe_fraction * base_span[j])
        if h <= 0 or not np.isfinite(h):
            raise ValueError("every action dimension must have positive finite span")

        plus = action.copy()
        minus = action.copy()
        plus[j] = min(high[j], action[j] + h)
        minus[j] = max(low[j], action[j] - h)
        denom = plus[j] - minus[j]
        if denom <= 0:
            raise ValueError("finite-difference probe collapsed at an action bound")

        y_plus = _flatten_trace(oracle(plus))
        y_minus = _flatten_trace(oracle(minus))
        queries += 2
        if y_plus.shape != y_minus.shape:
            raise ValueError("trace oracle changed output shape across probes")
        columns.append((y_plus - y_minus) / denom)

    return np.stack(columns, axis=1), queries


def solve_counterfactual_trace_transport(
    *,
    source_trace: np.ndarray,
    target_oracle: Callable[[np.ndarray], np.ndarray],
    initial_action: np.ndarray,
    action_low: np.ndarray,
    action_high: np.ndarray,
    probe_fraction: float = 1e-3,
    damping: float = 1e-4,
    trust_fraction: float = 0.25,
    max_iterations: int = 8,
    max_relative_residual: float = 0.05,
    max_jacobian_condition: float = 1e6,
    min_saturation_margin: float = 0.01,
    min_improvement_ratio: float = 0.20,
) -> TraceTransportCertificate:
    """Compile a source controller trace into a target-controller action.

    The caller must make target_oracle a genuine counterfactual experiment:
    every query restores the same simulator state and controller hidden state.

    A low residual alone is insufficient for authority. The final action must
    remain away from saturation and the local action-to-trace Jacobian must
    not be excessively ill-conditioned.
    """
    source = _flatten_trace(source_trace)
    action = np.asarray(initial_action, dtype=float).copy()
    low = np.asarray(action_low, dtype=float)
    high = np.asarray(action_high, dtype=float)
    if action.ndim != 1 or low.shape != action.shape or high.shape != action.shape:
        raise ValueError("action and bounds must share one flat action shape")
    if not np.all(np.isfinite(action)) or not np.all(np.isfinite(low)) or not np.all(np.isfinite(high)):
        raise ValueError("action and bounds must be finite")
    if np.any(high <= low):
        raise ValueError("every upper action bound must exceed the lower bound")
    if np.any(action < low) or np.any(action > high):
        raise ValueError("initial action must lie inside the target action box")
    if not (0 < probe_fraction < 0.5):
        raise ValueError("probe_fraction must lie in (0, 0.5)")
    if damping <= 0 or trust_fraction <= 0:
        raise ValueError("damping and trust_fraction must be positive")
    if max_iterations < 1:
        raise ValueError("max_iterations must be positive")

    first = _flatten_trace(target_oracle(action))
    query_count = 1
    if first.shape != source.shape:
        raise ValueError("source and target traces must have matching flattened shape")
    source_scale = max(float(np.linalg.norm(source)), 1e-12)
    initial_residual = float(np.linalg.norm(first - source))
    best_action = action.copy()
    best_trace = first.copy()
    best_residual = initial_residual
    history: list[TraceTransportStep] = []

    for iteration in range(max_iterations):
        current_trace = _flatten_trace(target_oracle(action))
        query_count += 1
        residual = source - current_trace

        jacobian, fd_queries = _finite_difference_jacobian(
            target_oracle,
            action,
            low=low,
            high=high,
            probe_fraction=probe_fraction,
        )
        query_count += fd_queries
        if jacobian.shape[0] != source.size:
            raise ValueError("target trace dimensionality changed during optimization")

        singular_values = np.linalg.svd(jacobian, compute_uv=False)
        if singular_values.size == 0 or singular_values[0] <= 1e-15:
            condition = np.inf
        else:
            condition = float(singular_values[0] / max(singular_values[-1], 1e-15))

        lhs = jacobian.T @ jacobian + damping * np.eye(action.size)
        rhs = jacobian.T @ residual
        try:
            delta = np.linalg.solve(lhs, rhs)
        except np.linalg.LinAlgError:
            delta = np.linalg.lstsq(lhs, rhs, rcond=None)[0]

        max_step = trust_fraction * (high - low)
        delta = np.clip(delta, -max_step, max_step)
        candidate = np.clip(action + delta, low, high)
        candidate_trace = _flatten_trace(target_oracle(candidate))
        query_count += 1
        candidate_residual = float(np.linalg.norm(candidate_trace - source))
        current_residual = float(np.linalg.norm(current_trace - source))

        accepted_step = candidate_residual < current_residual
        if accepted_step:
            action = candidate
            current_trace = candidate_trace
            current_residual = candidate_residual

        if current_residual < best_residual:
            best_residual = current_residual
            best_action = action.copy()
            best_trace = current_trace.copy()

        history.append(
            TraceTransportStep(
                iteration=iteration,
                action=action.copy(),
                residual_norm=current_residual,
                relative_residual=current_residual / source_scale,
                jacobian_condition=condition,
                accepted_step=accepted_step,
            )
        )

        if current_residual / source_scale <= max_relative_residual:
            break

    final_jacobian, fd_queries = _finite_difference_jacobian(
        target_oracle,
        best_action,
        low=low,
        high=high,
        probe_fraction=probe_fraction,
    )
    query_count += fd_queries
    singular_values = np.linalg.svd(final_jacobian, compute_uv=False)
    if singular_values.size == 0 or singular_values[0] <= 1e-15:
        final_condition = np.inf
    else:
        final_condition = float(singular_values[0] / max(singular_values[-1], 1e-15))

    relative = best_residual / source_scale
    improvement = (
        0.0
        if initial_residual <= 1e-15
        else (initial_residual - best_residual) / initial_residual
    )
    margin = _saturation_margin(best_action, low, high)

    failures = []
    if relative > max_relative_residual:
        failures.append("trace residual exceeds the frozen relative limit")
    if not np.isfinite(final_condition) or final_condition > max_jacobian_condition:
        failures.append("target action-to-trace Jacobian is ill-conditioned")
    if margin < min_saturation_margin:
        failures.append("target action is too close to saturation")
    if initial_residual > 1e-15 and improvement < min_improvement_ratio:
        failures.append("optimization does not materially improve over the initial action")

    accepted = not failures
    reason = (
        "trace match passes residual, conditioning, saturation, and improvement gates"
        if accepted
        else "; ".join(failures)
    )

    return TraceTransportCertificate(
        accepted=accepted,
        action=best_action,
        source_trace=source,
        matched_trace=best_trace,
        residual_norm=best_residual,
        relative_residual=relative,
        improvement_ratio=float(improvement),
        jacobian_condition=final_condition,
        saturation_margin=margin,
        iterations=len(history),
        query_count=query_count,
        reason=reason,
        history=tuple(history),
    )
