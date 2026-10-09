"""Command-amplitude-conditioned public proprioception envelope.

Training uses only previous fixed native scale=1.0 calibration. The scaled
applied center is a FALSIFIABLE affine hypothesis, not an attested physics
model or learned online sensor/collision-safety guarantee.
"""
from __future__ import annotations
from copy import deepcopy
from math import isfinite
from research.cross_robot_online_proprio_classifier import decide,ADDITIVE_RADIUS_M,LABELS

def predict(delta_public_xyz,model,amplitude,mode):
    if mode=="frozen_scale1":
        return decide(delta_public_xyz,model)
    if mode!="command_affine":
        raise ValueError("Unknown registered inference treatment")
    if type(amplitude) not in (float,int) or not isfinite(amplitude) or not (0<amplitude<=1):
        raise ValueError("Registered, finite physically realizable amplitude required")
    if set(model.get("class_models",{}))!=set(LABELS) or model.get("radius_margin_m")!=ADDITIVE_RADIUS_M:
        raise ValueError("Original untouched scale1 controller empirical model required")
    m=deepcopy(model)
    held=m["class_models"]["held"]["mean_public_motion_m"]
    applied=m["class_models"]["applied"]["mean_public_motion_m"]
    m["class_models"]["applied"]["mean_public_motion_m"]=[
        float(held[i])+amplitude*(float(applied[i])-float(held[i])) for i in range(3)
    ]
    # Crucially leave both original training radii unchanged, no fitting to
    # the new test conditions or truth labels. This may FAIL or abstain.
    z=decide(delta_public_xyz,m)
    z["hypothesis"]="fixed_prior_calibration_affine_native_amplitude_interpolation"
    z["original_training_envelopes_unmodified"]=True
    return z
