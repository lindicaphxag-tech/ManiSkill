"""Controller-independent decision-only achieved-pose observation probe.

One external achieved XYZ reading, two target hypotheses already generated
from acknowledged command history. This is a HEURISTIC, not a safe controller
identification certificate. No private target getter or simulator dependency.
"""
from __future__ import annotations
from math import dist, isfinite

MARGIN_M=0.002

def pure_classification(observed_xyz,held_xyz,applied_xyz,*,margin=MARGIN_M):
    poses=(observed_xyz,held_xyz,applied_xyz)
    try:
        p,h,a=(tuple(float(v) for v in x) for x in poses)
    except (TypeError,ValueError) as e:
        raise ValueError("Finite XYZ evidence required") from e
    if any(len(x)!=3 or not all(isfinite(v) for v in x) for x in (p,h,a)):
        raise ValueError("Finite XYZ-only evidence required")
    if not (isfinite(margin) and margin>0):
        raise ValueError("Positive independent observation margin required")
    dh=dist(p,h)
    da=dist(p,a)
    sep=dist(h,a)
    advantage=abs(dh-da)
    label=None if sep<=margin or advantage<margin else (
        "applied" if da<dh else "held")
    return dict(label=label,hold_distance_m=dh,applied_distance_m=da,
                target_separation_m=sep,decision_margin_m=advantage,
                evidence_type="achieved_EE_xyz_after_one_native_zero_arm_delta")
