"""Blind OOD public ACK response model: NEVER a physical safety certificate.

Model parameters are copied EXACTLY from previously source-audited Panda /
xArm6 empirical ZERO-probe calibration. No new test truth may update them.
The predictor uses PUBLIC before/after achieved XYZ and candidate targets
inferred only from dispatched native command hypotheses.
"""
from __future__ import annotations
from math import isfinite, sqrt

FROZEN_GAIN={
    "panda":(0.37494315058733085,0.5524096427079828,0.0036915112144919183),
    "xarm6_robotiq":(0.3424149619624357,0.45933938582528905,0.0025842081111425498)
}
PRIOR_PHYSX_PUBLIC_MODEL_GIT_BLOB="8b3e11cf342170984093321993eb4dc9bf168ffc"

def _vec(x):
    try: y=tuple(float(v) for v in x)
    except (ValueError, TypeError, OverflowError) as err:
        raise ValueError("XYZ requires finite numeric triples") from err
    if len(y)!=3 or not all(isfinite(v) for v in y):
        raise ValueError("XYZ requires finite numeric triples")
    return y

def _dist(a,b):
    return sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def response_segment_residual(before_xyz,after_xyz,target_xyz,lo,hi):
    x,y,t=map(_vec,(before_xyz,after_xyz,target_xyz))
    if not 0 <= lo <= hi <= 1: raise ValueError("Invalid gain range")
    d=tuple(tj-xj for xj,tj in zip(x,t))
    denom=sum(v*v for v in d)
    alpha=sum((yj-xj)*v for yj,xj,v in zip(y,x,d))/denom if denom else lo
    alpha=max(lo,min(hi,alpha))
    pred=tuple(xj+alpha*v for xj,v in zip(x,d))
    return _dist(y,pred),alpha

def predict_ood_public_history(*,robot,public_before_xyz,public_after_xyz,
                               applied_history_target_xyz,held_history_target_xyz):
    if robot not in FROZEN_GAIN: raise ValueError("Unknown robot calibration")
    lo,hi,eps=FROZEN_GAIN[robot]
    residuals={}
    gains={}
    for name,target in (("applied",applied_history_target_xyz),
                        ("held",held_history_target_xyz)):
        residuals[name],gains[name]=response_segment_residual(
            public_before_xyz,public_after_xyz,target,lo,hi)
    fit=[name for name in ("applied","held") if residuals[name]<=eps+1e-9]
    label=fit[0] if len(fit)==1 else None
    return dict(label=label, status=("UNIQUE_EMPIRICAL_FIT" if label else
                     "ABSTAIN_OVERLAP" if fit else "MODEL_FALSIFIED"),
                matching_histories=fit, residuals_m=residuals,
                fitted_gain_by_hypothesis=gains, frozen_epsilon_m=eps,
                frozen_gain_range=[lo,hi],
                model_source_sha=PRIOR_PHYSX_PUBLIC_MODEL_GIT_BLOB,
                no_privileged_state_reads_for_inference=True,
                no_deterministic_physical_certificate=True)
