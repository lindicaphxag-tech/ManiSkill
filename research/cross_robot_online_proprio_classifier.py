"""Online physical response identification using PUBLIC achieved end-effector XYZ only.

Train on prior physical executed/held histories; test on wholly different
precommitted seed ranges. Coordinates are achieved(t3) - achieved(t1), so
calibrating on absolute robot starting xyz cannot exploit the seed layout.
"""
from __future__ import annotations
import hashlib
import json
import math

ADDITIVE_RADIUS_M=0.002
LABELS=("applied","held")

def _xyz(v):
    if not isinstance(v,(list,tuple)) or len(v)!=3:
        raise ValueError("three public achieved XYZ coordinates are required")
    a=tuple(float(x) for x in v)
    if not all(math.isfinite(x) for x in a):
        raise ValueError("public pose must be finite")
    return a

def _norm(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def train(records,robot):
    if len(records)!=16:
        raise ValueError("exactly eight labelled calibration seeds per truth required")
    seeds={}
    for r in records:
        if r.get("robot")!=robot or r.get("truth") not in LABELS:
            raise ValueError("cross-robot or unknown physical truth leaked into calibration")
        key=(int(r["seed"]),r["truth"])
        if key in seeds:
            raise ValueError("duplicate calibration physical truth")
        seeds[key]=_xyz(r["delta_public_xyz"])
    cal_seeds={seed for seed,_ in seeds}
    if len(cal_seeds)!=8 or any((seed,t) not in seeds for seed in cal_seeds for t in LABELS):
        raise ValueError("paired seed-complete calibration required")
    params={}
    for t in LABELS:
        x=[seeds[(seed,t)] for seed in sorted(cal_seeds)]
        mean=tuple(sum(v[i] for v in x)/8 for i in range(3))
        max_residual=max(_norm(v,mean) for v in x)
        params[t]={"mean_public_motion_m":list(mean),
                   "max_calibration_residual_m":max_residual,
                   "envelope_radius_m":max_residual+ADDITIVE_RADIUS_M}
    return {"schema":"online_ack_cross_robot_empirical_envelope_v1",
            "robot":robot,"training_seeds":sorted(cal_seeds),"n_samples":16,
            "radius_margin_m":ADDITIVE_RADIUS_M,
            "class_models":params,
            "training_sha256":hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest(),
            "not_a_safety_certificate":True}

def decide(delta_public_xyz,model):
    x=_xyz(delta_public_xyz)
    if model.get("radius_margin_m")!=ADDITIVE_RADIUS_M or set(model.get("class_models",{}))!=set(LABELS):
        raise ValueError("unknown or modified calibration fit")
    distances={}
    compatible=[]
    for t in LABELS:
        p=model["class_models"][t]
        v=_xyz(p["mean_public_motion_m"])
        d=_norm(x,v)
        r=p["envelope_radius_m"]
        if not isinstance(r,(float,int)) or not math.isfinite(r) or r<=0:
            raise ValueError("unattested calibration radius")
        distances[t]=d
        if d <= r:
            compatible.append(t)
    label=compatible[0] if len(compatible)==1 else None
    return {"label":label,"status":"ONE_COMPATIBLE_PUBLIC_RESPONSE" if label else
            "ABSTAIN_NONE_OR_BOTH_COMPATIBLE",
            "compatible_histories":compatible,
            "public_motion_xyz_m":list(x),"distance_to_calibrated_center_m":distances,
            "private_target_getter_calls_at_decision":0,
            "calibrated_likelihood_not_attested":True}
