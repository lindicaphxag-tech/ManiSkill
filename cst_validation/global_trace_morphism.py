from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from trace_semantics import StatefulTraceIR


@dataclass(frozen=True)
class GlobalTraceMorphismCertificate:
    """Affine source-action to target-action morphism for one controller context."""

    P: np.ndarray
    q: np.ndarray
    semantic_map_residual: float
    semantic_offset_residual: float
    algebraically_exact: bool
    bounded_for_source_box: bool
    target_box_low: np.ndarray
    target_box_high: np.ndarray
    target_nullity: int
    unique_if_exact: bool
    reason: str

    def transport(self, source_action: np.ndarray) -> np.ndarray:
        source_action = np.asarray(source_action, dtype=float)
        if source_action.shape != (self.P.shape[1],):
            raise ValueError("source action dimension mismatch")
        return self.P @ source_action + self.q


def _semantic_map(ir: StatefulTraceIR) -> np.ndarray:
    return np.concatenate([ir.T_u, ir.G_u, ir.H_u], axis=0)


def _semantic_offset(ir: StatefulTraceIR, state, hidden) -> np.ndarray:
    x = np.asarray(state, dtype=float)
    z = np.asarray(hidden, dtype=float)
    if x.shape != (ir.state_dim,) or z.shape != (ir.hidden_dim,):
        raise ValueError("controller context dimension mismatch")
    trace = ir.T_x @ x + ir.T_z @ z + ir.t
    goal = ir.G_x @ x + ir.G_z @ z + ir.g
    nxt = ir.H_x @ x + ir.H_z @ z + ir.h
    return np.concatenate([trace, goal, nxt], axis=0)


def _affine_box_image(P, q, low, high):
    """Exact coordinate-wise bounds of affine map P u + q over a box."""
    P = np.asarray(P, dtype=float)
    q = np.asarray(q, dtype=float)
    low = np.asarray(low, dtype=float)
    high = np.asarray(high, dtype=float)
    positive = np.maximum(P, 0.0)
    negative = np.minimum(P, 0.0)
    out_low = q + positive @ low + negative @ high
    out_high = q + positive @ high + negative @ low
    return out_low, out_high


def compile_global_trace_morphism(
    *,
    source: StatefulTraceIR,
    target: StatefulTraceIR,
    source_state: np.ndarray,
    source_hidden: np.ndarray,
    target_state: np.ndarray,
    target_hidden: np.ndarray,
    atol: float = 1e-9,
    rtol: float = 1e-9,
) -> GlobalTraceMorphismCertificate:
    """Compile one analytic transport valid for the whole source native box.

    The certificate proves an affine identity for the controller semantic
    observables (substep trace, endpoint goal, next reference) at one fixed
    source/target controller context. It then computes exact interval bounds of
    the target action over the full source action box.

    This is a controller-command certificate, not a plant/contact safety proof.
    """
    if source.trace_steps != target.trace_steps:
        raise ValueError("trace_steps mismatch")
    if source.trace_width != target.trace_width:
        raise ValueError("trace width mismatch")
    if source.goal_dim != target.goal_dim:
        raise ValueError("goal dimension mismatch")
    if source.H_u.shape[0] != target.H_u.shape[0]:
        raise ValueError("next-reference dimension mismatch")

    Ms = _semantic_map(source)
    Mt = _semantic_map(target)
    cs = _semantic_offset(source, source_state, source_hidden)
    ct = _semantic_offset(target, target_state, target_hidden)

    pinv = np.linalg.pinv(Mt)
    P = pinv @ Ms
    q = pinv @ (cs - ct)

    map_error = Mt @ P - Ms
    offset_error = Mt @ q + ct - cs
    map_residual = float(np.linalg.norm(map_error, ord="fro"))
    offset_residual = float(np.linalg.norm(offset_error))
    map_scale = max(float(np.linalg.norm(Ms, ord="fro")), 1.0)
    offset_scale = max(float(np.linalg.norm(cs)), 1.0)
    exact = bool(
        map_residual <= atol + rtol * map_scale
        and offset_residual <= atol + rtol * offset_scale
    )

    box_low, box_high = _affine_box_image(
        P, q, source.native_low, source.native_high
    )
    bounded = bool(
        exact
        and np.all(box_low >= target.native_low - atol)
        and np.all(box_high <= target.native_high + atol)
    )

    rank = int(np.linalg.matrix_rank(Mt))
    nullity = int(target.action_dim - rank)
    unique = bool(exact and nullity == 0)

    if not exact:
        reason = (
            "no affine target-action morphism preserves the complete controller "
            "semantic map and context offset"
        )
    elif not bounded:
        reason = (
            "semantic morphism is algebraically exact but leaves target native "
            "bounds for part of the source action box"
        )
    elif unique:
        reason = (
            "one unique affine morphism preserves trace, goal, and next "
            "reference over the entire source action box"
        )
    else:
        reason = (
            "an exact bounded affine morphism exists, but target semantic "
            "nullspace makes it non-unique"
        )

    return GlobalTraceMorphismCertificate(
        P=P,
        q=q,
        semantic_map_residual=map_residual,
        semantic_offset_residual=offset_residual,
        algebraically_exact=exact,
        bounded_for_source_box=bounded,
        target_box_low=box_low,
        target_box_high=box_high,
        target_nullity=nullity,
        unique_if_exact=unique,
        reason=reason,
    )


def verify_global_morphism_sample(
    certificate: GlobalTraceMorphismCertificate,
    *,
    source: StatefulTraceIR,
    target: StatefulTraceIR,
    source_action: np.ndarray,
    source_state: np.ndarray,
    source_hidden: np.ndarray,
    target_state: np.ndarray,
    target_hidden: np.ndarray,
) -> float:
    """Return semantic residual for a concrete action under a compiled morphism."""
    u_target = certificate.transport(source_action)
    s_trace, s_goal, s_next = source.evaluate(
        source_action, source_state, source_hidden
    )
    t_trace, t_goal, t_next = target.evaluate(
        u_target, target_state, target_hidden
    )
    source_sem = np.concatenate([s_trace, s_goal, s_next])
    target_sem = np.concatenate([t_trace, t_goal, t_next])
    return float(np.linalg.norm(target_sem - source_sem))
