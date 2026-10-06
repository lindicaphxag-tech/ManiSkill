from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.optimize import lsq_linear


class TraceEquivalenceKind(str, Enum):
    EXACT_TRACE = "exact_trace"
    GOAL_ONLY = "goal_only"
    BOUNDED_APPROXIMATION = "bounded_approximation"
    UNREPRESENTABLE = "unrepresentable"


@dataclass(frozen=True)
class StatefulTraceIR:
    """Affine one-control-period semantics of a controller.

    For native action u, measured state x and controller memory z:

        trace = T_u u + T_x x + T_z z + t
        goal = G_u u + G_x x + G_z z + g
        z_next = H_u u + H_x x + H_z z + h

    trace is the flattened sequence of low-level drive targets over all
    simulation substeps. This certifies controller-command semantics only,
    not physical plant or contact-trajectory equivalence.
    """

    T_u: np.ndarray
    T_x: np.ndarray
    T_z: np.ndarray
    t: np.ndarray
    G_u: np.ndarray
    G_x: np.ndarray
    G_z: np.ndarray
    g: np.ndarray
    H_u: np.ndarray
    H_x: np.ndarray
    H_z: np.ndarray
    h: np.ndarray
    native_low: np.ndarray
    native_high: np.ndarray
    trace_steps: int
    name: str = ""

    def __post_init__(self) -> None:
        names = (
            "T_u", "T_x", "T_z", "t", "G_u", "G_x", "G_z", "g",
            "H_u", "H_x", "H_z", "h", "native_low", "native_high"
        )
        arrays = {name: np.asarray(getattr(self, name), dtype=float) for name in names}
        T_u = arrays["T_u"]
        if T_u.ndim != 2:
            raise ValueError("T_u must have shape [trace_dim, action_dim]")
        trace_dim, action_dim = T_u.shape
        T_x, T_z, t = arrays["T_x"], arrays["T_z"], arrays["t"]
        if T_x.ndim != 2 or T_x.shape[0] != trace_dim:
            raise ValueError("T_x must share trace dimension")
        if T_z.ndim != 2 or T_z.shape[0] != trace_dim:
            raise ValueError("T_z must share trace dimension")
        if t.shape != (trace_dim,):
            raise ValueError("t must have shape [trace_dim]")

        G_u, G_x, G_z, g = arrays["G_u"], arrays["G_x"], arrays["G_z"], arrays["g"]
        if G_u.ndim != 2 or G_u.shape[1] != action_dim:
            raise ValueError("G_u must share action dimension")
        goal_dim = G_u.shape[0]
        if G_x.shape != (goal_dim, T_x.shape[1]):
            raise ValueError("G_x shape mismatch")
        if G_z.shape != (goal_dim, T_z.shape[1]):
            raise ValueError("G_z shape mismatch")
        if g.shape != (goal_dim,):
            raise ValueError("g must have shape [goal_dim]")

        H_u, H_x, H_z, h = arrays["H_u"], arrays["H_x"], arrays["H_z"], arrays["h"]
        if H_u.ndim != 2 or H_u.shape[1] != action_dim:
            raise ValueError("H_u must share action dimension")
        hidden_next_dim = H_u.shape[0]
        if H_x.shape != (hidden_next_dim, T_x.shape[1]):
            raise ValueError("H_x shape mismatch")
        if H_z.shape != (hidden_next_dim, T_z.shape[1]):
            raise ValueError("H_z shape mismatch")
        if h.shape != (hidden_next_dim,):
            raise ValueError("h must have shape [hidden_next_dim]")

        low, high = arrays["native_low"], arrays["native_high"]
        if low.shape != (action_dim,) or high.shape != (action_dim,):
            raise ValueError("native bounds must match action dimension")
        if np.any(high <= low):
            raise ValueError("native_high must exceed native_low")
        if self.trace_steps <= 0:
            raise ValueError("trace_steps must be positive")
        if trace_dim % self.trace_steps:
            raise ValueError("trace dimension must be divisible by trace_steps")
        for value in arrays.values():
            if not np.all(np.isfinite(value)):
                raise ValueError("IR arrays must be finite")
        for key, value in arrays.items():
            object.__setattr__(self, key, value)

    @property
    def action_dim(self) -> int:
        return int(self.T_u.shape[1])

    @property
    def state_dim(self) -> int:
        return int(self.T_x.shape[1])

    @property
    def hidden_dim(self) -> int:
        return int(self.T_z.shape[1])

    @property
    def goal_dim(self) -> int:
        return int(self.G_u.shape[0])

    @property
    def trace_width(self) -> int:
        return int(self.T_u.shape[0] // self.trace_steps)

    def evaluate(self, u, x, z):
        u = np.asarray(u, dtype=float)
        x = np.asarray(x, dtype=float)
        z = np.asarray(z, dtype=float)
        if u.shape != (self.action_dim,):
            raise ValueError("action dimension mismatch")
        if x.shape != (self.state_dim,):
            raise ValueError("state dimension mismatch")
        if z.shape != (self.hidden_dim,):
            raise ValueError("hidden-state dimension mismatch")
        trace = self.T_u @ u + self.T_x @ x + self.T_z @ z + self.t
        goal = self.G_u @ u + self.G_x @ x + self.G_z @ z + self.g
        next_hidden = self.H_u @ u + self.H_x @ x + self.H_z @ z + self.h
        return trace, goal, next_hidden


@dataclass(frozen=True)
class TraceTransportCertificate:
    kind: TraceEquivalenceKind
    target_action: np.ndarray
    source_trace: np.ndarray
    target_trace: np.ndarray
    source_goal: np.ndarray
    target_goal: np.ndarray
    source_next_hidden: np.ndarray
    target_next_hidden: np.ndarray
    trace_residual_norm: float
    trace_relative_residual: float
    max_substep_trace_error: float
    goal_residual_norm: float
    hidden_residual_norm: float
    bounded_solver_success: bool
    bounded_representable: bool
    target_rank: int
    target_nullity: int
    native_margin: np.ndarray
    reason: str


def _margin(action, low, high):
    width = high - low
    return np.minimum((action - low) / width, (high - action) / width)


def compile_trace_transport(
    *,
    source,
    target,
    source_action,
    source_state,
    source_hidden,
    target_state,
    target_hidden,
    trace_weight=1.0,
    goal_weight=1.0,
    hidden_weight=1.0,
    atol=1e-9,
    rtol=1e-9,
):
    """Compile bounded target action and classify semantic equivalence strength."""
    if source.trace_steps != target.trace_steps:
        raise ValueError("source and target trace_steps must match")
    if source.trace_width != target.trace_width:
        raise ValueError("source and target trace widths must match")
    if source.goal_dim != target.goal_dim:
        raise ValueError("source and target goal dimensions must match")
    if source.H_u.shape[0] != target.H_u.shape[0]:
        raise ValueError("source and target next-hidden dimensions must match")
    for value, name in (
        (trace_weight, "trace_weight"),
        (goal_weight, "goal_weight"),
        (hidden_weight, "hidden_weight"),
    ):
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and non-negative")
    if trace_weight == goal_weight == hidden_weight == 0:
        raise ValueError("at least one semantic observable must be weighted")

    source_trace, source_goal, source_next = source.evaluate(
        source_action, source_state, source_hidden
    )
    tx = np.asarray(target_state, dtype=float)
    tz = np.asarray(target_hidden, dtype=float)
    trace_offset = target.T_x @ tx + target.T_z @ tz + target.t
    goal_offset = target.G_x @ tx + target.G_z @ tz + target.g
    hidden_offset = target.H_x @ tx + target.H_z @ tz + target.h

    blocks, rhs_blocks = [], []
    for weight, matrix, desired in (
        (trace_weight, target.T_u, source_trace - trace_offset),
        (goal_weight, target.G_u, source_goal - goal_offset),
        (hidden_weight, target.H_u, source_next - hidden_offset),
    ):
        if weight > 0:
            scale = np.sqrt(weight)
            blocks.append(scale * matrix)
            rhs_blocks.append(scale * desired)

    A = np.concatenate(blocks, axis=0)
    rhs = np.concatenate(rhs_blocks, axis=0)
    solve = lsq_linear(
        A,
        rhs,
        bounds=(target.native_low, target.native_high),
        lsmr_tol="auto",
        tol=max(atol, 1e-12),
    )
    u_target = np.asarray(solve.x, dtype=float)
    target_trace, target_goal, target_next = target.evaluate(
        u_target, target_state, target_hidden
    )

    trace_diff = target_trace - source_trace
    trace_norm = float(np.linalg.norm(trace_diff))
    trace_scale = max(float(np.linalg.norm(source_trace)), 1.0)
    trace_rel = trace_norm / trace_scale
    per_step = trace_diff.reshape(source.trace_steps, source.trace_width)
    max_substep = float(np.max(np.linalg.norm(per_step, axis=1)))

    goal_norm = float(np.linalg.norm(target_goal - source_goal))
    hidden_norm = float(np.linalg.norm(target_next - source_next))
    goal_scale = max(float(np.linalg.norm(source_goal)), 1.0)
    hidden_scale = max(float(np.linalg.norm(source_next)), 1.0)
    trace_ok = trace_norm <= atol + rtol * trace_scale
    goal_ok = goal_norm <= atol + rtol * goal_scale
    hidden_ok = hidden_norm <= atol + rtol * hidden_scale
    bounded_exact = bool(solve.success and trace_ok and goal_ok and hidden_ok)

    rank = int(np.linalg.matrix_rank(A))
    nullity = int(target.action_dim - rank)

    if bounded_exact:
        kind = TraceEquivalenceKind.EXACT_TRACE
        reason = "full drive-target trace, endpoint goal, and next controller reference match"
    elif solve.success and goal_ok:
        kind = TraceEquivalenceKind.GOAL_ONLY
        reason = "endpoint goal matches but trace and/or next controller reference differs"
    elif solve.success:
        kind = TraceEquivalenceKind.BOUNDED_APPROXIMATION
        reason = "closest bounded semantic transport is not exact"
    else:
        kind = TraceEquivalenceKind.UNREPRESENTABLE
        reason = "bounded semantic transport solver failed"

    return TraceTransportCertificate(
        kind=kind,
        target_action=u_target,
        source_trace=source_trace,
        target_trace=target_trace,
        source_goal=source_goal,
        target_goal=target_goal,
        source_next_hidden=source_next,
        target_next_hidden=target_next,
        trace_residual_norm=trace_norm,
        trace_relative_residual=trace_rel,
        max_substep_trace_error=max_substep,
        goal_residual_norm=goal_norm,
        hidden_residual_norm=hidden_norm,
        bounded_solver_success=bool(solve.success),
        bounded_representable=bounded_exact,
        target_rank=rank,
        target_nullity=nullity,
        native_margin=_margin(u_target, target.native_low, target.native_high),
        reason=reason,
    )


def joint_position_trace_ir(
    *,
    mode,
    physical_low,
    physical_high,
    sim_steps,
    interpolate,
    normalized=True,
    name="",
):
    """Exact affine trace IR for absolute/current-delta/target-delta joint control."""
    low = np.asarray(physical_low, dtype=float)
    high = np.asarray(physical_high, dtype=float)
    if low.ndim != 1 or high.shape != low.shape:
        raise ValueError("physical bounds must have shape [D]")
    if np.any(high <= low):
        raise ValueError("physical_high must exceed physical_low")
    if sim_steps <= 0:
        raise ValueError("sim_steps must be positive")

    d = low.shape[0]
    if normalized:
        U = np.diag(0.5 * (high - low))
        b = 0.5 * (high + low)
        native_low = -np.ones(d)
        native_high = np.ones(d)
    else:
        U = np.eye(d)
        b = np.zeros(d)
        native_low = low.copy()
        native_high = high.copy()

    zeros = np.zeros((d, d))
    if mode == "absolute":
        G_u, G_x, G_z, g = U, zeros, zeros, b
    elif mode == "delta_current":
        G_u, G_x, G_z, g = U, np.eye(d), zeros, b
    elif mode == "delta_target":
        G_u, G_x, G_z, g = U, zeros, np.eye(d), b
    else:
        raise ValueError("unknown joint-position mode")

    H_u, H_x, H_z, h = G_u.copy(), G_x.copy(), G_z.copy(), g.copy()
    rows_u, rows_x, rows_z, rows_b = [], [], [], []
    for step in range(1, sim_steps + 1):
        if interpolate:
            alpha = step / sim_steps
            rows_u.append(alpha * G_u)
            rows_x.append((1.0 - alpha) * np.eye(d) + alpha * G_x)
            rows_z.append(alpha * G_z)
            rows_b.append(alpha * g)
        else:
            rows_u.append(G_u)
            rows_x.append(G_x)
            rows_z.append(G_z)
            rows_b.append(g)

    return StatefulTraceIR(
        T_u=np.concatenate(rows_u, axis=0),
        T_x=np.concatenate(rows_x, axis=0),
        T_z=np.concatenate(rows_z, axis=0),
        t=np.concatenate(rows_b, axis=0),
        G_u=G_u,
        G_x=G_x,
        G_z=G_z,
        g=g,
        H_u=H_u,
        H_x=H_x,
        H_z=H_z,
        h=h,
        native_low=native_low,
        native_high=native_high,
        trace_steps=sim_steps,
        name=name or f"{mode}:{'interp' if interpolate else 'hold'}",
    )
