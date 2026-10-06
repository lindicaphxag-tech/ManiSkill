from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from trace_semantics import StatefulTraceIR


@dataclass(frozen=True)
class AffineStateBinding:
    """Bind a shared exogenous context c to one controller's measured state.

    x = X_c c + x_0

    Controller-owned memory is intentionally *not* folded into this binding.
    Relational CST treats memory as an independent transducer state and learns
    an explicit cross-controller relation z_t = R z_s + r.
    """

    X_c: np.ndarray
    x_0: np.ndarray

    def validate_for(self, ir: StatefulTraceIR) -> int:
        X_c = np.asarray(self.X_c, dtype=float)
        x_0 = np.asarray(self.x_0, dtype=float)
        if X_c.ndim != 2 or X_c.shape[0] != ir.state_dim:
            raise ValueError("X_c must map shared context into controller state")
        if x_0.shape != (ir.state_dim,):
            raise ValueError("x_0 shape mismatch")
        if not np.all(np.isfinite(X_c)) or not np.all(np.isfinite(x_0)):
            raise ValueError("state binding must be finite")
        return int(X_c.shape[1])


@dataclass(frozen=True)
class RelationalSequenceMorphismCertificate:
    """Affine transducer morphism valid for arbitrary-length command sequences.

    Target command:
        u_t = P u_s + Q c + K z_s + q

    Hidden-state relation:
        z_t = R z_s + r

    If the observable coefficient identities and hidden-update closure hold,
    then one-step relation preservation implies arbitrary-horizon preservation
    by induction, for every source action/context/hidden state in the declared
    region.  This certifies controller-command traces/goals only, not plant or
    contact trajectories.
    """

    P: np.ndarray
    Q: np.ndarray
    K: np.ndarray
    q: np.ndarray
    R: np.ndarray
    r: np.ndarray
    trace_residual: float
    goal_residual: float
    hidden_closure_residual: float
    algebraically_exact: bool
    bounded_on_region: bool
    target_action_region_low: np.ndarray
    target_action_region_high: np.ndarray
    solver_rank: int
    solver_nullity: int
    requires_target_hidden_initialization: bool
    reason: str

    def transport(self, source_action, context, source_hidden):
        u = np.asarray(source_action, dtype=float)
        c = np.asarray(context, dtype=float)
        z = np.asarray(source_hidden, dtype=float)
        if u.shape != (self.P.shape[1],):
            raise ValueError("source action dimension mismatch")
        if c.shape != (self.Q.shape[1],):
            raise ValueError("context dimension mismatch")
        if z.shape != (self.K.shape[1],):
            raise ValueError("source hidden dimension mismatch")
        return self.P @ u + self.Q @ c + self.K @ z + self.q

    def map_hidden(self, source_hidden):
        z = np.asarray(source_hidden, dtype=float)
        if z.shape != (self.R.shape[1],):
            raise ValueError("source hidden dimension mismatch")
        return self.R @ z + self.r


def shared_state_binding(d: int, context_dim: int | None = None) -> AffineStateBinding:
    context_dim = d if context_dim is None else int(context_dim)
    if context_dim < d:
        raise ValueError("context_dim must be >= state dimension")
    X_c = np.zeros((d, context_dim))
    X_c[:, :d] = np.eye(d)
    return AffineStateBinding(X_c=X_c, x_0=np.zeros(d))


def _affine_box_image(A, b, low, high):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    low = np.asarray(low, dtype=float)
    high = np.asarray(high, dtype=float)
    pos = np.maximum(A, 0.0)
    neg = np.minimum(A, 0.0)
    return (
        b + pos @ low + neg @ high,
        b + pos @ high + neg @ low,
    )


def _validate_transducer(ir: StatefulTraceIR) -> None:
    if ir.H_u.shape[0] != ir.hidden_dim:
        raise ValueError(
            "sequence morphism requires next-hidden dimension to equal hidden input dimension"
        )


def _unpack(theta, *, nt, ns, cdim, hs, ht):
    cursor = 0

    def take(shape):
        nonlocal cursor
        n = int(np.prod(shape))
        out = theta[cursor : cursor + n].reshape(shape)
        cursor += n
        return out

    P = take((nt, ns))
    Q = take((nt, cdim))
    K = take((nt, hs))
    q = take((nt,))
    R = take((ht, hs))
    r = take((ht,))
    if cursor != len(theta):
        raise AssertionError("parameter unpack mismatch")
    return P, Q, K, q, R, r


def _parameter_count(*, nt, ns, cdim, hs, ht):
    return nt * ns + nt * cdim + nt * hs + nt + ht * hs + ht


def compile_relational_sequence_morphism(
    *,
    source: StatefulTraceIR,
    target: StatefulTraceIR,
    source_binding: AffineStateBinding,
    target_binding: AffineStateBinding,
    context_low: np.ndarray,
    context_high: np.ndarray,
    source_hidden_low: np.ndarray,
    source_hidden_high: np.ndarray,
    atol: float = 1e-9,
    rtol: float = 1e-9,
) -> RelationalSequenceMorphismCertificate:
    """Compile a cross-controller transducer relation by linear constraint solving.

    Unlike one-step CST, source and target controller memories need not share a
    numeric representation. The compiler solves simultaneously for an action
    interface and an affine memory relation, then verifies relation closure
    under the hidden-state update.
    """
    _validate_transducer(source)
    _validate_transducer(target)
    if source.trace_steps != target.trace_steps:
        raise ValueError("trace_steps mismatch")
    if source.trace_width != target.trace_width:
        raise ValueError("trace width mismatch")
    if source.goal_dim != target.goal_dim:
        raise ValueError("goal dimension mismatch")

    cdim_s = source_binding.validate_for(source)
    cdim_t = target_binding.validate_for(target)
    if cdim_s != cdim_t:
        raise ValueError("source and target must share context dimension")
    cdim = cdim_s

    context_low = np.asarray(context_low, dtype=float)
    context_high = np.asarray(context_high, dtype=float)
    zlow = np.asarray(source_hidden_low, dtype=float)
    zhigh = np.asarray(source_hidden_high, dtype=float)
    if context_low.shape != (cdim,) or context_high.shape != (cdim,):
        raise ValueError("context bounds shape mismatch")
    if zlow.shape != (source.hidden_dim,) or zhigh.shape != (source.hidden_dim,):
        raise ValueError("source hidden bounds shape mismatch")
    if np.any(context_high < context_low) or np.any(zhigh < zlow):
        raise ValueError("region bounds must be ordered")

    Xs = np.asarray(source_binding.X_c, dtype=float)
    xs0 = np.asarray(source_binding.x_0, dtype=float)
    Xt = np.asarray(target_binding.X_c, dtype=float)
    xt0 = np.asarray(target_binding.x_0, dtype=float)

    ns, nt = source.action_dim, target.action_dim
    hs, ht = source.hidden_dim, target.hidden_dim
    nvars = _parameter_count(nt=nt, ns=ns, cdim=cdim, hs=hs, ht=ht)

    def residual(theta):
        P, Q, K, q, R, r = _unpack(
            theta, nt=nt, ns=ns, cdim=cdim, hs=hs, ht=ht
        )
        pieces = []

        def observable(Otu, Otx, Otz, ot, Osu, Osx, Osz, os):
            pieces.extend(
                [
                    (Otu @ P - Osu).ravel(),
                    (Otu @ Q + Otx @ Xt - Osx @ Xs).ravel(),
                    (Otu @ K + Otz @ R - Osz).ravel(),
                    (
                        Otu @ q + Otx @ xt0 + Otz @ r + ot
                        - (Osx @ xs0 + os)
                    ).ravel(),
                ]
            )

        observable(
            target.T_u, target.T_x, target.T_z, target.t,
            source.T_u, source.T_x, source.T_z, source.t,
        )
        observable(
            target.G_u, target.G_x, target.G_z, target.g,
            source.G_u, source.G_x, source.G_z, source.g,
        )

        # Hidden relation closure:
        #   H_t(u_t, x_t, z_t) == R H_s(u_s, x_s, z_s) + r
        pieces.extend(
            [
                (target.H_u @ P - R @ source.H_u).ravel(),
                (
                    target.H_u @ Q + target.H_x @ Xt
                    - R @ source.H_x @ Xs
                ).ravel(),
                (
                    target.H_u @ K + target.H_z @ R
                    - R @ source.H_z
                ).ravel(),
                (
                    target.H_u @ q
                    + target.H_x @ xt0
                    + target.H_z @ r
                    + target.h
                    - R @ (source.H_x @ xs0 + source.h)
                    - r
                ).ravel(),
            ]
        )
        return np.concatenate(pieces)

    zero = np.zeros(nvars)
    b = residual(zero)
    columns = []
    for i in range(nvars):
        basis = np.zeros(nvars)
        basis[i] = 1.0
        columns.append(residual(basis) - b)
    A = np.stack(columns, axis=1)
    theta, _, rank, _ = np.linalg.lstsq(A, -b, rcond=None)
    P, Q, K, q, R, r = _unpack(
        theta, nt=nt, ns=ns, cdim=cdim, hs=hs, ht=ht
    )

    # Report observable and closure residuals separately.
    def obs_residual(Otu, Otx, Otz, ot, Osu, Osx, Osz, os):
        blocks = [
            Otu @ P - Osu,
            Otu @ Q + Otx @ Xt - Osx @ Xs,
            Otu @ K + Otz @ R - Osz,
            (
                Otu @ q + Otx @ xt0 + Otz @ r + ot
                - (Osx @ xs0 + os)
            )[:, None],
        ]
        return float(np.linalg.norm(np.concatenate(blocks, axis=1), ord="fro"))

    trace_res = obs_residual(
        target.T_u, target.T_x, target.T_z, target.t,
        source.T_u, source.T_x, source.T_z, source.t,
    )
    goal_res = obs_residual(
        target.G_u, target.G_x, target.G_z, target.g,
        source.G_u, source.G_x, source.G_z, source.g,
    )
    closure = np.concatenate(
        [
            (target.H_u @ P - R @ source.H_u).ravel(),
            (
                target.H_u @ Q + target.H_x @ Xt
                - R @ source.H_x @ Xs
            ).ravel(),
            (
                target.H_u @ K + target.H_z @ R - R @ source.H_z
            ).ravel(),
            (
                target.H_u @ q
                + target.H_x @ xt0
                + target.H_z @ r
                + target.h
                - R @ (source.H_x @ xs0 + source.h)
                - r
            ).ravel(),
        ]
    )
    closure_res = float(np.linalg.norm(closure))

    scale = max(
        float(np.linalg.norm(source.T_u, ord="fro")),
        float(np.linalg.norm(source.G_u, ord="fro")),
        float(np.linalg.norm(source.H_u, ord="fro")),
        1.0,
    )
    tol = atol + rtol * scale
    exact = bool(trace_res <= tol and goal_res <= tol and closure_res <= tol)

    combined = np.concatenate([P, Q, K], axis=1)
    low = np.concatenate([source.native_low, context_low, zlow])
    high = np.concatenate([source.native_high, context_high, zhigh])
    region_low, region_high = _affine_box_image(combined, q, low, high)
    bounded = bool(
        exact
        and np.all(region_low >= target.native_low - atol)
        and np.all(region_high <= target.native_high + atol)
    )

    nullity = int(nvars - rank)
    if not exact:
        reason = (
            "no affine action-interface / hidden-relation pair satisfies trace, "
            "goal, and hidden-update closure"
        )
    elif not bounded:
        reason = (
            "transducer morphism is exact but target action bounds are violated "
            "inside the declared action/context/hidden region"
        )
    else:
        reason = (
            "trace/goal equality and hidden-relation closure hold over the full "
            "declared region; relation composes over arbitrary sequence length"
        )

    return RelationalSequenceMorphismCertificate(
        P=P, Q=Q, K=K, q=q, R=R, r=r,
        trace_residual=trace_res,
        goal_residual=goal_res,
        hidden_closure_residual=closure_res,
        algebraically_exact=exact,
        bounded_on_region=bounded,
        target_action_region_low=region_low,
        target_action_region_high=region_high,
        solver_rank=int(rank),
        solver_nullity=nullity,
        requires_target_hidden_initialization=bool(target.hidden_dim),
        reason=reason,
    )


def verify_sequence(
    certificate: RelationalSequenceMorphismCertificate,
    *,
    source: StatefulTraceIR,
    target: StatefulTraceIR,
    source_binding: AffineStateBinding,
    target_binding: AffineStateBinding,
    source_actions: np.ndarray,
    contexts: np.ndarray,
    source_hidden_initial: np.ndarray,
):
    """Execute a finite witness of the inductive transducer relation."""
    actions = np.asarray(source_actions, dtype=float)
    contexts = np.asarray(contexts, dtype=float)
    if actions.ndim != 2 or actions.shape[1] != source.action_dim:
        raise ValueError("source_actions shape mismatch")
    if contexts.ndim != 2 or contexts.shape[0] != actions.shape[0]:
        raise ValueError("contexts shape mismatch")

    zs = np.asarray(source_hidden_initial, dtype=float).copy()
    zt = certificate.map_hidden(zs)
    max_trace = 0.0
    max_goal = 0.0
    max_relation = 0.0
    target_actions = []

    for us, c in zip(actions, contexts, strict=True):
        xs = source_binding.X_c @ c + source_binding.x_0
        xt = target_binding.X_c @ c + target_binding.x_0
        ut = certificate.transport(us, c, zs)
        st, sg, zs_next = source.evaluate(us, xs, zs)
        tt, tg, zt_next = target.evaluate(ut, xt, zt)

        max_trace = max(max_trace, float(np.linalg.norm(tt - st)))
        max_goal = max(max_goal, float(np.linalg.norm(tg - sg)))
        expected_zt_next = certificate.map_hidden(zs_next)
        max_relation = max(
            max_relation, float(np.linalg.norm(zt_next - expected_zt_next))
        )
        target_actions.append(ut)
        zs = zs_next
        zt = zt_next

    return {
        "max_trace_residual": max_trace,
        "max_goal_residual": max_goal,
        "max_hidden_relation_residual": max_relation,
        "target_actions": np.asarray(target_actions),
    }
