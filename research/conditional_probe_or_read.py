"""Fail-closed action-conditioned probe-or-read planning INTERFACE.

This is NOT a learned response model or safe real-robot controller. Caller
must supply a trained, independently audited forward-response set with
hypothesis-complete conservative response radii and a verified native
controller admissibility/robot task loss contract. With no trustworthy
predictions the correct output is an authoritative read request.

For each possible hidden controller target history h, the calibrated response
set is B(mu(a,h), r(a,h)) in achieved XYZ. If two balls overlap, a single
measurement may correspond to either history; an arbitrary probe cannot
force disambiguation. ALL response balls must be pairwise disjoint with an
additional sensor tolerance for this simple one-step interface.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Literal

@dataclass(frozen=True)
class ResponseBall:
    full_target_history_id: str
    predicted_public_after_xyz: tuple[float,float,float]
    model_uncertainty_radius_m: float

@dataclass(frozen=True)
class ProbeOption:
    name: str
    shared_native_6d_action: tuple[float,float,float,float,float,float]
    action_chart_valid_for_all_histories: bool
    trusted_response_model_provenance: bool
    source_distribution_coverage_attested: bool
    trusted_calibration_validity: bool
    calibrated_response_balls: tuple[ResponseBall,...]
    maximum_native_target_position_error_m: float
    maximum_native_target_orientation_error_rad: float
    conservative_task_regret_bound: float
    incremental_physical_probe_cost: float
    incremental_public_sensing_cost: float

@dataclass(frozen=True)
class ProbeDecision:
    mode: Literal["READ_TRUE_TARGET","TAKE_CONDITIONAL_PROBE"]
    candidate_probe_name: str|None
    worst_pairwise_response_separation_lower_m: float|None
    additional_cost_over_native_no_probe: float
    reason: str
    no_robot_safety_guarantee: bool=True

def _finite_nonnegative(x:float)->bool:
    return type(x) in (float,int) and isfinite(x) and x>=0

def _euclidean(x,y):
    return sqrt(sum((a-b)**2 for a,b in zip(x,y)))

def _validate(p:ProbeOption, histories:tuple[str,...])->float|None:
    if (not p.name or not isinstance(p,ProbeOption)
        or type(p.action_chart_valid_for_all_histories) is not bool
        or type(p.trusted_response_model_provenance) is not bool
        or type(p.source_distribution_coverage_attested) is not bool
        or type(p.trusted_calibration_validity) is not bool
        or any(type(x) not in (float,int) or not isfinite(x) for x in p.shared_native_6d_action)
        or len(p.shared_native_6d_action)!=6
        or not all(_finite_nonnegative(x) for x in (
          p.maximum_native_target_position_error_m,
          p.maximum_native_target_orientation_error_rad,
          p.conservative_task_regret_bound,
          p.incremental_physical_probe_cost,
          p.incremental_public_sensing_cost))):
        return None
    if not (p.action_chart_valid_for_all_histories
            and p.trusted_response_model_provenance
            and p.source_distribution_coverage_attested
            and p.trusted_calibration_validity
            and len(p.calibrated_response_balls)==len(histories)):
        return None
    obs={q.full_target_history_id:q for q in p.calibrated_response_balls}
    if (len(obs)!=len(histories) or set(obs)!=set(histories)
        or any(not q.full_target_history_id or
               len(q.predicted_public_after_xyz)!=3 or
               any(type(x) not in (float,int) or not isfinite(x)
                   for x in q.predicted_public_after_xyz) or
               not _finite_nonnegative(q.model_uncertainty_radius_m)
               for q in obs.values())):
        return None
    vals=tuple(obs[h] for h in histories)
    return min(_euclidean(a.predicted_public_after_xyz,b.predicted_public_after_xyz)
               -a.model_uncertainty_radius_m-b.model_uncertainty_radius_m
               for i,a in enumerate(vals) for b in vals[i+1:])

def choose_probe_or_read(*, histories:tuple[str,...],
                         proposed_probes:tuple[ProbeOption,...],
                         authoritative_read_cost:float,
                         sensor_separation_margin_m:float,
                         maximum_target_position_error_m:float,
                         maximum_target_orientation_error_rad:float,
                         maximum_incremental_task_regret:float)->ProbeDecision:
    """Nominal conditional separation, NOT physical safety or confidence.

    Select cheapest (probe + public sensor) proven-separated option only if
    its entire incremental budget is STRICTLY below an authoritative read
    and ALL full-history command bounds are already trustworthy.
    Model calibration/out-of-distribution attestation must come from
    separate physical data, not source audit-only target labels online.
    """
    if (len(histories)<2 or len(set(histories))!=len(histories)
        or any(not x or type(x) is not str for x in histories)
        or len({p.name for p in proposed_probes})!=len(proposed_probes)
        or not all(_finite_nonnegative(x) for x in (
           authoritative_read_cost,sensor_separation_margin_m,
           maximum_target_position_error_m,maximum_target_orientation_error_rad,
           maximum_incremental_task_regret))):
        raise ValueError("Probe comparison requires complete unique full-target IDs and explicit budgets")
    eligible=[]
    for p in proposed_probes:
        sep=_validate(p,histories)
        if sep is None:
            continue
        total=p.incremental_physical_probe_cost+p.incremental_public_sensing_cost
        if (sep>sensor_separation_margin_m
            and p.maximum_native_target_position_error_m<=maximum_target_position_error_m
            and p.maximum_native_target_orientation_error_rad<=maximum_target_orientation_error_rad
            and p.conservative_task_regret_bound<=maximum_incremental_task_regret
            and total<authoritative_read_cost):
            eligible.append((total,-sep,p.name,sep))
    if not eligible:
        return ProbeDecision("READ_TRUE_TARGET",None,None,authoritative_read_cost,
            "NO_SOURCE_ATTESTED_TASK_ADMISSIBLE_AND_GENUINELY_SEPARATING_PROBE")
    total,_,name,sep=min(eligible)
    return ProbeDecision("TAKE_CONDITIONAL_PROBE",name,sep,total,
        "CONDITIONAL_ALL_FULL_HISTORY_RESPONSE_BALLS_SEPARATED__REVERIFY_AFTER_ACTUAL_STEP")
