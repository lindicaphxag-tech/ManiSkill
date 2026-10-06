from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from trace_semantics import StatefulTraceIR


class ControllerSemanticOracle(Protocol):
    """Resettable one-control-period black-box semantic oracle.

    A query must be referentially transparent with respect to its explicit
    native action, measured state and controller hidden state.  The oracle may
    wrap a real controller, but it must restore those inputs before each query.
    """

    action_dim: int
    state_dim: int
    hidden_dim: int
    trace_steps: int
    native_low: np.ndarray
    native_high: np.ndarray

    def query(
        self,
        action: np.ndarray,
        state: np.ndarray,
        hidden: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return flattened command trace, endpoint goal and next hidden state."""
        ...


@dataclass(frozen=True)
class AffineIdentificationCertificate:
    ir: StatefulTraceIR | None
    accepted: bool
    fit_query_count: int
    validation_query_count: int
    max_trace_relative_residual: float
    max_goal_relative_residual: float
    max_hidden_relative_residual: float
    affine_rank: int
    parameter_dim: int
    reason: str


def _vector(value, dim: int, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.shape != (dim,):
        raise ValueError(f"{name} must have shape ({dim},)")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _query_vector(oracle: ControllerSemanticOracle, v: np.ndarray):
    na, nx, nz = oracle.action_dim, oracle.state_dim, oracle.hidden_dim
    action = v[:na]
    state = v[na : na + nx]
    hidden = v[na + nx :]
    trace, goal, next_hidden = oracle.query(action, state, hidden)
    trace = np.asarray(trace, dtype=float).reshape(-1)
    goal = np.asarray(goal, dtype=float).reshape(-1)
    next_hidden = np.asarray(next_hidden, dtype=float).reshape(-1)
    if len(trace) % oracle.trace_steps:
        raise ValueError("oracle trace dimension is not divisible by trace_steps")
    if len(next_hidden) != nz:
        raise ValueError("oracle next-hidden dimension must equal hidden_dim")
    if not all(np.all(np.isfinite(x)) for x in (trace, goal, next_hidden)):
        raise ValueError("oracle returned non-finite semantics")
    return trace, goal, next_hidden


def _relative_residual(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(
        np.linalg.norm(actual - predicted)
        / max(float(np.linalg.norm(actual)), 1.0)
    )


def identify_affine_trace_ir(
    oracle: ControllerSemanticOracle,
    *,
    state_center: np.ndarray,
    state_radius: np.ndarray,
    hidden_center: np.ndarray,
    hidden_radius: np.ndarray,
    validation_samples: int = 64,
    validation_seed: int = 20261006,
    max_relative_residual: float = 1e-8,
    name: str = "identified-controller",
) -> AffineIdentificationCertificate:
    """Identify and independently validate an affine StatefulTraceIR.

    Identification uses one center query and one axis probe per explicit
    semantic input dimension.  Validation then samples fresh points from the
    declared action/state/hidden box.  A nonlinear, clipped, hysteretic or
    otherwise misspecified controller is rejected rather than silently forced
    into an affine converter.

    This is system identification machinery, not a claim that affine
    identification itself is novel.  Its CST role is to eliminate hand-written
    controller formulas from the semantic-certification pipeline.
    """
    na, nx, nz = int(oracle.action_dim), int(oracle.state_dim), int(oracle.hidden_dim)
    if min(na, nx, nz) < 0 or na <= 0:
        raise ValueError("invalid oracle dimensions")
    if oracle.trace_steps <= 0:
        raise ValueError("trace_steps must be positive")
    if validation_samples <= 0:
        raise ValueError("validation_samples must be positive")
    if max_relative_residual < 0 or not np.isfinite(max_relative_residual):
        raise ValueError("max_relative_residual must be finite and non-negative")

    low = _vector(oracle.native_low, na, "native_low")
    high = _vector(oracle.native_high, na, "native_high")
    if np.any(high <= low):
        raise ValueError("native_high must exceed native_low")
    xc = _vector(state_center, nx, "state_center")
    xr = _vector(state_radius, nx, "state_radius")
    zc = _vector(hidden_center, nz, "hidden_center")
    zr = _vector(hidden_radius, nz, "hidden_radius")
    if np.any(xr <= 0) or np.any(zr <= 0):
        raise ValueError("state/hidden radii must be positive")

    uc = 0.5 * (low + high)
    ur = 0.5 * (high - low)
    center = np.concatenate([uc, xc, zc])
    radii = np.concatenate([ur, xr, zr])
    n = len(center)

    y0_parts = _query_vector(oracle, center)
    y0 = np.concatenate(y0_parts)
    columns = []
    fit_queries = 1
    for i in range(n):
        step = 0.5 * radii[i]
        if step <= 0:
            raise ValueError("identification probe radius must be positive")
        probe = center.copy()
        probe[i] += step
        yi = np.concatenate(_query_vector(oracle, probe))
        columns.append((yi - y0) / step)
        fit_queries += 1
    A = np.stack(columns, axis=1)
    b = y0 - A @ center

    trace_dim = len(y0_parts[0])
    goal_dim = len(y0_parts[1])
    hidden_dim = len(y0_parts[2])
    trace_A = A[:trace_dim]
    goal_A = A[trace_dim : trace_dim + goal_dim]
    hidden_A = A[trace_dim + goal_dim :]
    trace_b = b[:trace_dim]
    goal_b = b[trace_dim : trace_dim + goal_dim]
    hidden_b = b[trace_dim + goal_dim :]

    su = slice(0, na)
    sx = slice(na, na + nx)
    sz = slice(na + nx, n)

    ir = StatefulTraceIR(
        T_u=trace_A[:, su],
        T_x=trace_A[:, sx],
        T_z=trace_A[:, sz],
        t=trace_b,
        G_u=goal_A[:, su],
        G_x=goal_A[:, sx],
        G_z=goal_A[:, sz],
        g=goal_b,
        H_u=hidden_A[:, su],
        H_x=hidden_A[:, sx],
        H_z=hidden_A[:, sz],
        h=hidden_b,
        native_low=low,
        native_high=high,
        trace_steps=int(oracle.trace_steps),
        name=name,
    )

    rng = np.random.default_rng(validation_seed)
    max_trace = max_goal = max_hidden = 0.0
    for _ in range(validation_samples):
        u = rng.uniform(low, high)
        x = rng.uniform(xc - xr, xc + xr)
        z = rng.uniform(zc - zr, zc + zr)
        actual_trace, actual_goal, actual_hidden = oracle.query(u, x, z)
        actual_trace = np.asarray(actual_trace, dtype=float).reshape(-1)
        actual_goal = np.asarray(actual_goal, dtype=float).reshape(-1)
        actual_hidden = np.asarray(actual_hidden, dtype=float).reshape(-1)
        pred_trace, pred_goal, pred_hidden = ir.evaluate(u, x, z)
        max_trace = max(max_trace, _relative_residual(actual_trace, pred_trace))
        max_goal = max(max_goal, _relative_residual(actual_goal, pred_goal))
        max_hidden = max(max_hidden, _relative_residual(actual_hidden, pred_hidden))

    accepted = max(max_trace, max_goal, max_hidden) <= max_relative_residual
    if accepted:
        reason = (
            "independent held-out probes are consistent with one affine "
            "controller-semantic transducer over the declared region"
        )
    else:
        reason = (
            "held-out semantic probes reject a single affine controller model; "
            "use a piecewise/nonlinear model or shrink the declared region"
        )

    return AffineIdentificationCertificate(
        ir=ir if accepted else None,
        accepted=accepted,
        fit_query_count=fit_queries,
        validation_query_count=validation_samples,
        max_trace_relative_residual=max_trace,
        max_goal_relative_residual=max_goal,
        max_hidden_relative_residual=max_hidden,
        affine_rank=int(np.linalg.matrix_rank(A)),
        parameter_dim=n,
        reason=reason,
    )
