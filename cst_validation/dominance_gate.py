from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .closed_loop_transport import ClosedLoopTransportCertificate, LinearClosedLoopModel


@dataclass(frozen=True)
class QuadraticRemainderEnvelope:
    """Empirical local envelope ||f(x,u)-f_hat(x,u)|| <= c ||[x,u]||^2.

    This is a calibration artifact over a declared box, not a global formal
    bound on an unknown nonlinear simulator.
    """

    coefficient: float
    state_abs_limit: np.ndarray
    action_abs_limit: np.ndarray
    sample_count: int
    max_observed_residual: float
    min_sample_radius: float


@dataclass(frozen=True)
class DominanceGateCertificate:
    use_transport: bool
    inside_calibration_domain: bool
    target_action: np.ndarray
    fallback_action: np.ndarray
    predicted_transport_mismatch: float
    predicted_fallback_mismatch: float
    transport_upper_bound: float
    fallback_lower_bound: float
    certified_margin: float
    source_remainder_bound: float
    target_transport_remainder_bound: float
    target_fallback_remainder_bound: float
    reason: str


def _vector(value, name: str) -> np.ndarray:
    out=np.asarray(value,dtype=float)
    if out.ndim!=1 or out.size==0 or not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be a finite non-empty vector")
    return out


def model_next(model: LinearClosedLoopModel, state, action) -> np.ndarray:
    x=_vector(state,"state")
    u=_vector(action,"action")
    A=np.asarray(model.A,dtype=float)
    B=np.asarray(model.B,dtype=float)
    if A.shape!=(x.size,x.size) or B.shape!=(x.size,u.size):
        raise ValueError("model dimensions do not match state/action")
    return A@x+B@u


def calibrate_quadratic_remainder(
    model: LinearClosedLoopModel,
    states: np.ndarray,
    actions: np.ndarray,
    observed_next_states: np.ndarray,
    *,
    min_sample_radius: float=1e-6,
) -> QuadraticRemainderEnvelope:
    states=np.asarray(states,dtype=float)
    actions=np.asarray(actions,dtype=float)
    observed=np.asarray(observed_next_states,dtype=float)
    if states.ndim!=2 or actions.ndim!=2 or observed.ndim!=2:
        raise ValueError("states, actions and observed_next_states must be rank-2")
    if states.shape[0]!=actions.shape[0] or states.shape!=observed.shape:
        raise ValueError("calibration arrays have incompatible shapes")
    if states.shape[0]==0:
        raise ValueError("calibration set must be non-empty")
    if min_sample_radius<=0:
        raise ValueError("min_sample_radius must be positive")

    coeff=0.0
    max_res=0.0
    used=0
    for x,u,y in zip(states,actions,observed):
        radius=float(np.linalg.norm(np.concatenate([x,u])))
        if radius<min_sample_radius:
            continue
        residual=float(np.linalg.norm(y-model_next(model,x,u)))
        coeff=max(coeff,residual/(radius*radius))
        max_res=max(max_res,residual)
        used+=1
    if used==0:
        raise ValueError("no calibration sample exceeded min_sample_radius")

    return QuadraticRemainderEnvelope(
        coefficient=float(coeff),
        state_abs_limit=np.max(np.abs(states),axis=0),
        action_abs_limit=np.max(np.abs(actions),axis=0),
        sample_count=used,
        max_observed_residual=float(max_res),
        min_sample_radius=float(min_sample_radius),
    )


def remainder_bound(
    envelope: QuadraticRemainderEnvelope,
    state: np.ndarray,
    action: np.ndarray,
) -> tuple[float,bool]:
    x=_vector(state,"state")
    u=_vector(action,"action")
    if x.shape!=envelope.state_abs_limit.shape or u.shape!=envelope.action_abs_limit.shape:
        raise ValueError("query dimensions differ from calibration envelope")
    inside=bool(
        np.all(np.abs(x)<=envelope.state_abs_limit+1e-15)
        and np.all(np.abs(u)<=envelope.action_abs_limit+1e-15)
    )
    radius_sq=float(np.dot(x,x)+np.dot(u,u))
    return float(envelope.coefficient*radius_sq),inside


def certify_calibrated_dominance(
    source_model: LinearClosedLoopModel,
    target_model: LinearClosedLoopModel,
    transport: ClosedLoopTransportCertificate,
    *,
    state: np.ndarray,
    source_action: np.ndarray,
    source_envelope: QuadraticRemainderEnvelope,
    target_envelope: QuadraticRemainderEnvelope,
    fallback_action: np.ndarray | None=None,
) -> DominanceGateCertificate:
    """Enable transport only when calibrated error intervals are disjoint.

    We compare the same declared source behavior at the current state.

        desired_hat = f_src_hat(x, u_src)
        adapted_hat = f_tgt_hat(x, T(x,u_src))
        fallback_hat = f_tgt_hat(x, u_fallback)

    Calibration envelopes give empirical remainder radii. Transport is enabled
    only when the adapted upper error bound is strictly below the fallback
    lower error bound. Outside the calibration box the gate fails closed.
    """

    x=_vector(state,"state")
    u_src=_vector(source_action,"source_action")
    u_adapt=np.asarray(transport.state_gain@x+transport.action_gain@u_src,dtype=float)
    u_fallback=u_src.copy() if fallback_action is None else _vector(fallback_action,"fallback_action")

    desired=model_next(source_model,x,u_src)
    adapted=model_next(target_model,x,u_adapt)
    fallback=model_next(target_model,x,u_fallback)

    d_adapt=float(np.linalg.norm(adapted-desired))
    d_fallback=float(np.linalg.norm(fallback-desired))

    eps_s,inside_s=remainder_bound(source_envelope,x,u_src)
    eps_ta,inside_ta=remainder_bound(target_envelope,x,u_adapt)
    eps_tf,inside_tf=remainder_bound(target_envelope,x,u_fallback)
    inside=bool(inside_s and inside_ta and inside_tf)

    upper=d_adapt+eps_s+eps_ta
    lower=max(0.0,d_fallback-eps_s-eps_tf)
    margin=lower-upper
    use=bool(inside and margin>0.0)

    if not inside:
        reason="query leaves the frozen nonlinear calibration domain; transport is refused"
    elif use:
        reason="adapted worst-case calibrated error is below fallback best-case calibrated error"
    else:
        reason="calibrated error intervals overlap; transport advantage is not established"

    return DominanceGateCertificate(
        use_transport=use,
        inside_calibration_domain=inside,
        target_action=u_adapt,
        fallback_action=u_fallback,
        predicted_transport_mismatch=d_adapt,
        predicted_fallback_mismatch=d_fallback,
        transport_upper_bound=float(upper),
        fallback_lower_bound=float(lower),
        certified_margin=float(margin),
        source_remainder_bound=float(eps_s),
        target_transport_remainder_bound=float(eps_ta),
        target_fallback_remainder_bound=float(eps_tf),
        reason=reason,
    )
