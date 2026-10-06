from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from trace_semantics import StatefulTraceIR


@dataclass(frozen=True)
class AffineContextBinding:
    """Bind a shared runtime context c into one controller's state and memory.

    x = X_c c + x_0
    z = Z_c c + z_0

    The shared context makes cross-controller assumptions explicit. For
    example, source and target controllers can be bound to the same measured
    joint position while only the source target-relative controller consumes a
    stored target reference.
    """

    X_c: np.ndarray
    x_0: np.ndarray
    Z_c: np.ndarray
    z_0: np.ndarray

    def validate_for(self, ir: StatefulTraceIR) -> int:
        X_c = np.asarray(self.X_c, dtype=float)
        x_0 = np.asarray(self.x_0, dtype=float)
        Z_c = np.asarray(self.Z_c, dtype=float)
        z_0 = np.asarray(self.z_0, dtype=float)
        if X_c.ndim != 2 or X_c.shape[0] != ir.state_dim:
            raise ValueError("X_c must map context into controller state")
        context_dim = X_c.shape[1]
        if Z_c.shape != (ir.hidden_dim, context_dim):
            raise ValueError("Z_c must share the context dimension")
        if x_0.shape != (ir.state_dim,):
            raise ValueError("x_0 shape mismatch")
        if z_0.shape != (ir.hidden_dim,):
            raise ValueError("z_0 shape mismatch")
        for value in (X_c, x_0, Z_c, z_0):
            if not np.all(np.isfinite(value)):
                raise ValueError("context binding must be finite")
        return context_dim


@dataclass(frozen=True)
class ContextualTraceMorphismCertificate:
    """Region-level semantic morphism u_t = P u_s + Q c + q."""

    P: np.ndarray
    Q: np.ndarray
    q: np.ndarray
    action_map_residual: float
    context_map_residual: float
    offset_residual: float
    algebraically_exact: bool
    bounded_on_region: bool
    target_region_low: np.ndarray
    target_region_high: np.ndarray
    target_nullity: int
    unique_if_exact: bool
    reason: str

    def transport(self, source_action, context):
        u = np.asarray(source_action, dtype=float)
        c = np.asarray(context, dtype=float)
        if u.shape != (self.P.shape[1],):
            raise ValueError("source action dimension mismatch")
        if c.shape != (self.Q.shape[1],):
            raise ValueError("context dimension mismatch")
        return self.P @ u + self.Q @ c + self.q


def _stack_action_map(ir: StatefulTraceIR) -> np.ndarray:
    return np.concatenate([ir.T_u, ir.G_u, ir.H_u], axis=0)


def _stack_context_map(
    ir: StatefulTraceIR, binding: AffineContextBinding
) -> tuple[np.ndarray, np.ndarray]:
    context_dim = binding.validate_for(ir)
    X_c = np.asarray(binding.X_c, dtype=float)
    x_0 = np.asarray(binding.x_0, dtype=float)
    Z_c = np.asarray(binding.Z_c, dtype=float)
    z_0 = np.asarray(binding.z_0, dtype=float)

    trace_c = ir.T_x @ X_c + ir.T_z @ Z_c
    goal_c = ir.G_x @ X_c + ir.G_z @ Z_c
    hidden_c = ir.H_x @ X_c + ir.H_z @ Z_c
    C = np.concatenate([trace_c, goal_c, hidden_c], axis=0)

    trace_0 = ir.T_x @ x_0 + ir.T_z @ z_0 + ir.t
    goal_0 = ir.G_x @ x_0 + ir.G_z @ z_0 + ir.g
    hidden_0 = ir.H_x @ x_0 + ir.H_z @ z_0 + ir.h
    d = np.concatenate([trace_0, goal_0, hidden_0], axis=0)
    assert C.shape[1] == context_dim
    return C, d


def _affine_box_image(A, b, low, high):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    low = np.asarray(low, dtype=float)
    high = np.asarray(high, dtype=float)
    positive = np.maximum(A, 0.0)
    negative = np.minimum(A, 0.0)
    return (
        b + positive @ low + negative @ high,
        b + positive @ high + negative @ low,
    )


def compile_contextual_trace_morphism(
    *,
    source: StatefulTraceIR,
    target: StatefulTraceIR,
    source_binding: AffineContextBinding,
    target_binding: AffineContextBinding,
    context_low: np.ndarray,
    context_high: np.ndarray,
    atol: float = 1e-9,
    rtol: float = 1e-9,
) -> ContextualTraceMorphismCertificate:
    """Compile one affine morphism valid over actions and a context region.

    Let the shared context be c. After applying the explicit source/target
    bindings, semantic equality has the form

        A_s u_s + C_s c + d_s
          = A_t u_t + C_t c + d_t.

    CST compiles u_t = P u_s + Q c + q and verifies the three coefficient
    identities. It then propagates the complete source-action/context box
    through the affine morphism and checks target native bounds exactly,
    coordinate by coordinate.
    """
    if source.trace_steps != target.trace_steps:
        raise ValueError("trace_steps mismatch")
    if source.trace_width != target.trace_width:
        raise ValueError("trace width mismatch")
    if source.goal_dim != target.goal_dim:
        raise ValueError("goal dimension mismatch")
    if source.H_u.shape[0] != target.H_u.shape[0]:
        raise ValueError("next-reference dimension mismatch")

    source_dim = source_binding.validate_for(source)
    target_dim = target_binding.validate_for(target)
    if source_dim != target_dim:
        raise ValueError("source and target bindings must share context dimension")
    context_low = np.asarray(context_low, dtype=float)
    context_high = np.asarray(context_high, dtype=float)
    if context_low.shape != (source_dim,) or context_high.shape != (source_dim,):
        raise ValueError("context bounds shape mismatch")
    if np.any(context_high < context_low):
        raise ValueError("context_high must be >= context_low")

    As = _stack_action_map(source)
    At = _stack_action_map(target)
    Cs, ds = _stack_context_map(source, source_binding)
    Ct, dt = _stack_context_map(target, target_binding)

    pinv = np.linalg.pinv(At)
    P = pinv @ As
    Q = pinv @ (Cs - Ct)
    q = pinv @ (ds - dt)

    action_error = At @ P - As
    context_error = At @ Q + Ct - Cs
    offset_error = At @ q + dt - ds

    action_res = float(np.linalg.norm(action_error, ord="fro"))
    context_res = float(np.linalg.norm(context_error, ord="fro"))
    offset_res = float(np.linalg.norm(offset_error))
    action_scale = max(float(np.linalg.norm(As, ord="fro")), 1.0)
    context_scale = max(float(np.linalg.norm(Cs, ord="fro")), 1.0)
    offset_scale = max(float(np.linalg.norm(ds)), 1.0)
    exact = bool(
        action_res <= atol + rtol * action_scale
        and context_res <= atol + rtol * context_scale
        and offset_res <= atol + rtol * offset_scale
    )

    combined = np.concatenate([P, Q], axis=1)
    combined_low = np.concatenate([source.native_low, context_low])
    combined_high = np.concatenate([source.native_high, context_high])
    region_low, region_high = _affine_box_image(
        combined, q, combined_low, combined_high
    )
    bounded = bool(
        exact
        and np.all(region_low >= target.native_low - atol)
        and np.all(region_high <= target.native_high + atol)
    )

    rank = int(np.linalg.matrix_rank(At))
    nullity = int(target.action_dim - rank)
    unique = bool(exact and nullity == 0)

    if not exact:
        reason = (
            "target action channel cannot reproduce source action/context "
            "controller semantics over the declared affine region"
        )
    elif not bounded:
        reason = (
            "semantic identity is exact but part of the source-action/context "
            "region maps outside target native bounds"
        )
    elif unique:
        reason = (
            "unique affine action/context morphism preserves trace, goal, and "
            "next reference over the full declared region"
        )
    else:
        reason = (
            "exact bounded region morphism exists with target semantic "
            "nullspace freedom"
        )

    return ContextualTraceMorphismCertificate(
        P=P,
        Q=Q,
        q=q,
        action_map_residual=action_res,
        context_map_residual=context_res,
        offset_residual=offset_res,
        algebraically_exact=exact,
        bounded_on_region=bounded,
        target_region_low=region_low,
        target_region_high=region_high,
        target_nullity=nullity,
        unique_if_exact=unique,
        reason=reason,
    )


def shared_current_qpos_binding(d: int, context_dim: int | None = None):
    """Context c begins with the D current joint positions; hidden ref is zero."""
    context_dim = d if context_dim is None else int(context_dim)
    if context_dim < d:
        raise ValueError("context_dim must be at least d")
    X_c = np.zeros((d, context_dim))
    X_c[:, :d] = np.eye(d)
    return AffineContextBinding(
        X_c=X_c,
        x_0=np.zeros(d),
        Z_c=np.zeros((d, context_dim)),
        z_0=np.zeros(d),
    )
