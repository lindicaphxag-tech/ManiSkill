"""Public-translation evidence -> unique COMPLETE target-history candidate.

A public XYZ motion observation can discriminate a full SE(3) hypothesis
when a single physically feasible member remains, EVEN IF discarded
hypotheses have other orientations.  This is conditional on the empirical
XYZ response model and COMPLETE, trusted history candidates.  It is NOT
a generic SO(3) observation, hardware safety certificate or new theorem.
"""
from __future__ import annotations
import math
from typing import Sequence

EPS_MARGIN_M=0.002
EPS_NUMERIC_M=1e-12
NORM_ERROR_MAX=1e-3


def choose_full_pose_history_from_public_xyz(
    residual_m:Sequence[float],
    target_quaternions_xyzw:Sequence[Sequence[float]],
    response_epsilon_m:float,
    *,
    historical_margin_m:float=EPS_MARGIN_M,
    histories_complete:bool=True,
    provenance_trusted:bool=True,
    action_chart_verified:bool=True,
):
    if not(histories_complete and provenance_trusted and action_chart_verified):
        return dict(authorized=False,index=None,reason="INSUFFICIENT_OR_UNTRUSTED_HISTORY")
    if not (2<=len(residual_m)<=16 and len(residual_m)==len(target_quaternions_xyzw)
            and isinstance(response_epsilon_m,(float,int)) and
            math.isfinite(response_epsilon_m) and 0<=response_epsilon_m<=.25
            and historical_margin_m==EPS_MARGIN_M):
        return dict(authorized=False,index=None,reason="INVALID_FIXED_MODEL_OR_HYPOTHESES")
    if not all(isinstance(x,(float,int)) and math.isfinite(x) and x>=0 for x in residual_m):
        return dict(authorized=False,index=None,reason="NONFINITE_PUBLIC_RESPONSE")
    for quat in target_quaternions_xyzw:
        if (len(quat)!=4 or
            not all(isinstance(q,(float,int)) and math.isfinite(q) for q in quat)
            or abs(math.sqrt(sum(float(q)*q for q in quat))-1)>NORM_ERROR_MAX):
            return dict(authorized=False,index=None,reason="INVALID_SURVIVING_OR_DISCARDED_FULL_POSE")
    viable=[i for i,d in enumerate(residual_m) if d<=response_epsilon_m+EPS_NUMERIC_M]
    if len(viable)!=1:
        return dict(authorized=False,index=None,
                    reason="AMBIGUOUS_OR_MODEL_FALSIFIED_PUBLIC_XYZ",viable=viable)
    candidate=viable[0]
    if any(d<=response_epsilon_m+historical_margin_m for i,d in enumerate(residual_m)
           if i!=candidate):
        return dict(authorized=False,index=None,reason="INSUFFICIENT_RESIDUAL_CLEARANCE",
                    viable=viable)
    # The winning index addresses one entire full TargetPose; SO(3) of the
    # eliminated targets is irrelevant to history identity *if* the public
    # translation model is correct.  Never synthesize any new orientation.
    return dict(authorized=True,index=candidate,
                reason="UNIQUE_POSITION_SURVIVOR_INHERITS_COMPLETE_SE3_HISTORY",
                viable=viable,orientation_evidence="INHERITED_FROM_UNIQUE_HISTORY_NOT_PUBLICLY_MEASURED")
