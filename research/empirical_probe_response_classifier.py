"""Pilot empirical public achieved-response interval disambiguator.

Empirical frozen per-task envelopes come from DISJOINT historic calibration
episodes, not externally attested physical contracts. Any output is a
statistical *hypothesis*, not a certified hidden controller state. Decision
uses public before/after XYZ and action-history candidate targets only.
"""
from __future__ import annotations
from math import isfinite,sqrt

EPSILON_BY_TASK={
    "pull_cube":0.006944262561376447,
    "stack_cube":0.00719087965534261,
}
CALIBRATION_TRAIN_SEEDS={
    "pull_cube":(140001,140002,140003,140004),
    "stack_cube":(150001,150002,150003,150004),
}


def _xyz(values):
    try:
        a=tuple(float(v) for v in values)
    except (TypeError,ValueError) as e:
        raise ValueError("Finite public achieved/target XYZ required") from e
    if len(a)!=3 or not all(isfinite(v) for v in a):
        raise ValueError("Exactly three finite XYZ coordinates required")
    return a


def _segment_min_distance(before,after,goal):
    # Known model form x_after=x_before+alpha*(goal-x_before)+error,
    # alpha in [0,1]. This model's physical envelope is NOT attested.
    d=tuple(p-q for p,q in zip(goal,before))
    dy=tuple(p-q for p,q in zip(after,before))
    length2=sum(z*z for z in d)
    alpha=(sum(a*b for a,b in zip(d,dy))/length2) if length2 else 0.0
    alpha=max(0.0,min(1.0,alpha))
    pred=tuple(p+alpha*v for p,v in zip(before,d))
    return sqrt(sum((p-y)**2 for p,y in zip(pred,after))),alpha


def classify_empirical_public_response(before_xyz,after_xyz,
                                       held_goal_xyz,applied_goal_xyz,*,
                                       task):
    if task not in EPSILON_BY_TASK:
        raise ValueError("Unknown frozen task calibration")
    before,after,h,a=map(_xyz,(before_xyz,after_xyz,
                                held_goal_xyz,applied_goal_xyz))
    eps=EPSILON_BY_TASK[task]
    dh,alpha_h=_segment_min_distance(before,after,h)
    da,alpha_a=_segment_min_distance(before,after,a)
    feasible_h=dh<=eps+1e-12
    feasible_a=da<=eps+1e-12
    label=("held" if feasible_h and not feasible_a
           else "applied" if feasible_a and not feasible_h else None)
    status=("UNIQUE_EMPIRICAL_FIT" if label else
            "ABSTAIN_TWO_PLAUSIBLE_HISTORIES" if feasible_h and feasible_a else
            "REFUSE_EMPIRICAL_MODEL_FALSIFIED")
    return dict(
        label=label,status=status,
        hold_distance_m=dh,applied_distance_m=da,
        target_separation_m=sqrt(sum((p-q)**2 for p,q in zip(h,a))),
        decision_margin_m=abs(dh-da),
        empirical_response_epsilon_m=eps,
        empirical_response_gain_range=[0.0,1.0],
        held_compatible=feasible_h,
        applied_compatible=feasible_a,
        fitted_alpha_held=alpha_h,
        fitted_alpha_applied=alpha_a,
        evidence_type="achieved_EE_xyz_after_one_native_zero_arm_delta",
        historical_training_source_only=True,
        independent_physical_model_attested=False,
        certification_claim=False,
    )
