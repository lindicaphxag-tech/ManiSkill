"""Prospective target-memory robust correction WITH actual native SO3 action constraint.

Novelty candidate relative to this fork's original finite midpoint search:
search the representable native XYZ-Euler unit ball instead of interpreting
an infeasible geodesic midpoint as a no-action verdict. Exact verification of
ALL hypotheses is mandatory before authorizing any action. Local optimization
is NOT a global infeasibility certificate, physical collision/IK guarantee,
authoritative target read, or original mathematics theorem.
"""
import warnings
from itertools import combinations
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation
from research.multi_ack_se3_bounded import common_multi_history_command
from research.two_history_se3_robust import CommonCommand, Reason

BLOCKED = {
    Reason.REFUSE_INCOMPLETE_HYPOTHESES,
    Reason.REFUSE_STALE_OR_UNTRUSTED,
    Reason.REFUSE_UNVERIFIED_CONTROLLER,
    Reason.REFUSE_POSITION_BUDGET,
}

def reachable_common_history_command(histories, desired, *, pos_lower, pos_upper,
        rot_lower, position_budget_m, rotation_budget_rad, hypotheses_complete,
        trusted_provenance, age_steps, max_age_steps,
        root_translation_root_left_rotation_verified, numeric_guard=1e-9):
    kw=dict(pos_lower=pos_lower,pos_upper=pos_upper,rot_lower=rot_lower,
            position_budget_m=position_budget_m,rotation_budget_rad=rotation_budget_rad,
            hypotheses_complete=hypotheses_complete,trusted_provenance=trusted_provenance,
            age_steps=age_steps,max_age_steps=max_age_steps,
            root_translation_root_left_rotation_verified=root_translation_root_left_rotation_verified,
            numeric_guard=numeric_guard)
    old=common_multi_history_command(histories,desired,**kw)
    if old.authorized or old.reason in BLOCKED:
        return old
    if old.reason not in (Reason.REFUSE_UNREPRESENTABLE_ROTATION,Reason.REFUSE_ROTATION_BUDGET):
        return old
    if not (hypotheses_complete is True and trusted_provenance is True
            and root_translation_root_left_rotation_verified is True
            and age_steps<=max_age_steps):
        return old
    low=np.broadcast_to(np.asarray(pos_lower,dtype=float),(3,))
    high=np.broadcast_to(np.asarray(pos_upper,dtype=float),(3,))
    scale=np.broadcast_to(np.asarray(rot_lower,dtype=float),(3,))
    pp=np.asarray([p.position for p in histories],dtype=float)
    goal=np.asarray(desired.position,dtype=float)
    if (not np.isfinite(pp).all() or not np.isfinite(goal).all()
        or np.any(low>=high) or np.any(abs(scale)<1e-10)):
        raise ValueError("invalid native command chart")
    center=(pp.min(axis=0)+pp.max(axis=0))*.5
    displacement=np.clip(goal-center,low,high)
    normpos=2*(displacement-low)/(high-low)-1
    maxpos=float(np.max(np.abs(pp+displacement-goal)))
    if not np.isfinite(maxpos) or maxpos+numeric_guard>=position_budget_m:
        return old
    rots=[Rotation.from_quat(h.quaternion_xyzw) for h in histories]
    g=Rotation.from_quat(desired.quaternion_xyzw)
    half_diameter=max((float((a.inv()*b).magnitude())*.5 for a,b in combinations(rots,2)),default=0.)
    if half_diameter+numeric_guard>=rotation_budget_rad:
        return old

    def objective(u):
        u=np.asarray(u,dtype=float)
        if not np.isfinite(u).all() or u.shape!=(3,) or np.linalg.norm(u)>=1-numeric_guard:
            return float("inf")
        A=Rotation.from_euler("XYZ",u*scale)
        return max(float((g.inv()*(A*r)).magnitude()) for r in rots)

    # Baseline candidate family; projected INTO actual admissible native set.
    # This includes physical zero action, not just all geodesic midpoints.
    mids=list(rots)+[a*(a.inv()*b)**.5 for a,b in combinations(rots,2)]
    qq=np.asarray([r.as_quat() for r in rots])
    qq=np.where((qq@qq[0])[:,None]<0.,-qq,qq)
    v=qq.sum(axis=0)
    if np.linalg.norm(v)>1e-10:
        mids.append(Rotation.from_quat(v/np.linalg.norm(v)))
    starts=[np.zeros(3)]
    for m in mids:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",UserWarning)
            e=(g*m.inv()).as_euler("XYZ")/scale
        if np.isfinite(e).all():
            mag=float(np.linalg.norm(e))
            if mag>0:
                e=e*min(1.,(1.-1e-5)/mag)
            starts.append(np.asarray(e,dtype=float))
    best_u=None
    best=float("inf")
    def consider(u):
        nonlocal best_u,best
        u=np.asarray(u,dtype=float)
        if not np.isfinite(u).all():
            return
        mag=float(np.linalg.norm(u))
        if mag>=1-1e-5:
            u=u*((1-1e-5)/max(mag,1e-12))
        error=objective(u)
        if np.isfinite(error) and error<best:
            best_u,best=u.copy(),float(error)
    for u in starts:consider(u)
    # Slow search runs ONLY when no source-verifiable candidate meets budget.
    if best+numeric_guard>=rotation_budget_rad:
        for start in starts:
            def smooth_objective(v):
                v=np.asarray(v,dtype=float)
                mag=float(np.linalg.norm(v))
                clipped=v*min(1.,(1.-1e-5)/max(mag,1e-12))
                return objective(clipped)+2.*max(mag-(1.-1e-5),0.)**2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore",RuntimeWarning)
                opt=minimize(smooth_objective,start,method="Powell",
                             options={"maxiter":120,"xtol":1e-5,"ftol":1e-7})
            consider(opt.x)
            if best+numeric_guard<rotation_budget_rad:
                break
    if best_u is None or best+numeric_guard>=rotation_budget_rad:
        # Search incompleteness is explicit: no mathematical impossibility claim.
        return old
    full=np.r_[normpos,best_u]
    if (np.max(abs(full[:3]))>1+1e-7 or
        np.linalg.norm(full[3:])>=1-numeric_guard or not np.isfinite(full).all()):
        raise RuntimeError("invalid physical action candidate")
    # Independent source-controller forward equation: certify every history.
    exact=Rotation.from_euler("XYZ",full[3:]*scale)
    worst=max(float((g.inv()*(exact*r)).magnitude()) for r in rots)
    if worst+numeric_guard>=rotation_budget_rad:
        return old
    return CommonCommand(
        reason=Reason.AUTHORIZE_BOUNDED_SETPOINT,
        normalized_6d=tuple(map(float,full)),
        worst_position_inf_m=maxpos,
        worst_orientation_geodesic_rad=worst,
        hypotheses=len(histories),
        position_saturation_excess_m=tuple(map(float,np.abs(goal-center-displacement))),
        explanation="Local native-SO3 reachable set search; exact every-hypothesis target audit. "
            "NOT a physical safety guarantee or proof of globally optimal action.",
    )
