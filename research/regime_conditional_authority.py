"""Regime-conditional, decision-critical PUBLIC probing for unknown execution ACK.

Research-stage, stdlib-only source algorithm. This module does NOT actuate
robots, certify contact/force safety, estimate trustworthy coverage from data,
or report physical task performance. Its response tubes MUST be calibrated on
genuinely independent physical training states and revalidated after shifts.
A public motion sample can NEVER be substituted for controller-private target.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import acos, isfinite, sqrt
from typing import Optional, Tuple

Vec3 = Tuple[float,float,float]
Quat = Tuple[float,float,float,float]

def _finite(v):
    return all(type(x) in (int,float) and isfinite(x) for x in v)

def _q(q:Quat)->Quat:
    if len(q)!=4 or not _finite(q):raise ValueError("Invalid public SO(3) quaternion")
    norm=sqrt(sum(a*a for a in q))
    if norm<1e-10:raise ValueError("Near-zero quaternion")
    return tuple(a/norm for a in q)

def _so3(a:Quat,b:Quat)->float:
    aa=_q(a);bb=_q(b)
    overlap=min(1.0,abs(sum(x*y for x,y in zip(aa,bb))))
    return 2.0*acos(overlap)

def _xyz(a:Vec3,b:Vec3)->float:
    if len(a)!=3 or len(b)!=3 or not _finite(a) or not _finite(b):
        raise ValueError("Public XYZ must contain finite physical positions")
    return sqrt(sum((x-y)**2 for x,y in zip(a,b)))

@dataclass(frozen=True)
class Probe:
    probe_id:str
    native_six_dim:Tuple[float,float,float,float,float,float]
    all_history_abi_setpoint_bound_verified:bool
    known_delivery_command_supported:bool
    max_nominal_action_norm:float
    declared_sensor_sample_events:int
    def __post_init__(self):
        if not self.probe_id or len(self.native_six_dim)!=6 or not _finite(self.native_six_dim):
            raise ValueError("No authenticated native 6D public probe")
        if type(self.declared_sensor_sample_events) is not int or self.declared_sensor_sample_events<2:
            raise ValueError("Before AND after public observation events are mandatory")
        if type(self.max_nominal_action_norm) not in (float,int) or not isfinite(self.max_nominal_action_norm) or self.max_nominal_action_norm<0:
            raise ValueError("Untrusted native actuation budget")

@dataclass(frozen=True)
class ResponseTube:
    """Public response distribution SUPPORT, NOT a true posterior probability.

    One entry per original complete SE(3) history, per post-ACK response
    regime, and per known-delivered candidate public probe. Orientation is
    public achieved end-effector orientation, NOT controller target memory.
    """
    probe_id:str
    history_id:str
    regime_id:str
    expected_public_xyz:Vec3
    expected_public_quat_xyzw:Quat
    radius_xyz_m:float
    radius_so3_rad:float
    def __post_init__(self):
        if not all((self.probe_id,self.history_id,self.regime_id)):
            raise ValueError("Missing native provenance of history/regime/probe")
        _xyz(self.expected_public_xyz,(0.0,0.0,0.0))
        _q(self.expected_public_quat_xyzw)
        if not all(type(x) in (float,int) and isfinite(x) and x>=0 for x in (self.radius_xyz_m,self.radius_so3_rad)):
            raise ValueError("Untrusted physical response radius")

@dataclass(frozen=True)
class CandidatePlan:
    probe_id:Optional[str]
    decision:str
    conservative_min_sep_ratio:float
    predicted_sensor_sample_events:int
    inquiry_reason:str
    original_history_ids:Tuple[str,...]
    origin_model_source_disjoint_from_test:bool

@dataclass(frozen=True)
class PublicMotion:
    probe_id:str
    observed_after_xyz:Vec3
    observed_after_quat_xyzw:Quat
    delivery_confirmed:bool
    final_observation_step:int
    actual_public_sensor_sample_events:int
    def __post_init__(self):
        _xyz(self.observed_after_xyz,(0.0,0.0,0.0))
        _q(self.observed_after_quat_xyzw)
        if type(self.final_observation_step) is not int or self.final_observation_step<0:
            raise ValueError("Invalid actual native physical observation step")
        if type(self.actual_public_sensor_sample_events) is not int or self.actual_public_sensor_sample_events<0:
            raise ValueError("Unaccounted real public sensing")

@dataclass(frozen=True)
class PublicDecision:
    selected_history_id:Optional[str]
    action:str
    reason:str
    public_history_candidates_consistent:Tuple[str,...]
    actual_sensor_sample_events:int
    authoritative_private_reads_required:int
    empirical_model_validity_guaranteed:bool=False
    hardware_safety_guaranteed:bool=False

class RegimeConditionalAuthority:
    def __init__(self,history_ids:Tuple[str,...],response_regime_ids:Tuple[str,...],
                 probes:Tuple[Probe,...],tubes:Tuple[ResponseTube,...],
                 *,registered_contract_verified:bool,
                 history_complete_and_fresh:bool,
                 independent_calibration_witness_available:bool,
                 max_native_probe_norm:float=1.0,
                 min_validity_separation_margin_xyz_m:float=0.002,
                 min_validity_separation_margin_so3_rad:float=0.02,
                 max_observation_lag_steps:int=0):
        if not history_ids or len(set(history_ids))!=len(history_ids):
            raise ValueError("Invalid original complete SE3 histories")
        if not response_regime_ids or len(set(response_regime_ids))!=len(response_regime_ids):
            raise ValueError("No physically plausible response regime support")
        if not probes or len({p.probe_id for p in probes})!=len(probes):
            raise ValueError("Probe proposals absent or not unique")
        if type(max_observation_lag_steps) is not int or max_observation_lag_steps<0:
            raise ValueError("Stale evidence bound malformed")
        vals=(max_native_probe_norm,min_validity_separation_margin_xyz_m,min_validity_separation_margin_so3_rad)
        if not all(type(v) in (int,float) and isfinite(v) and v>0 for v in vals):
            raise ValueError("Invalid action/response validity margins")
        self.histories=history_ids
        self.regimes=response_regime_ids
        self.probes={p.probe_id:p for p in probes}
        self.responses={}
        for r in tubes:
            key=(r.probe_id,r.history_id,r.regime_id)
            if key in self.responses:raise ValueError("Duplicated physically trained response hypothesis")
            if r.history_id not in history_ids or r.regime_id not in response_regime_ids or r.probe_id not in self.probes:
                raise ValueError("Response refers to out-of-contract history/regime/probe")
            self.responses[key]=r
        self.trusted=bool(registered_contract_verified and history_complete_and_fresh
                          and independent_calibration_witness_available)
        self.max_probe_norm=max_native_probe_norm
        self.margin_xyz=min_validity_separation_margin_xyz_m
        self.margin_so3=min_validity_separation_margin_so3_rad
        self.max_lag=max_observation_lag_steps

    def _measure_sep_ratio(self,a:ResponseTube,b:ResponseTube):
        # Nonintersecting response tubes in EITHER public measured DOF:
        # single SO3 component is physically different from XYZ, but it is
        # not necessarily statistically independent of camera/robot sensing.
        p=_xyz(a.expected_public_xyz,b.expected_public_xyz)
        theta=_so3(a.expected_public_quat_xyzw,b.expected_public_quat_xyzw)
        p_limit=a.radius_xyz_m+b.radius_xyz_m+self.margin_xyz
        theta_limit=a.radius_so3_rad+b.radius_so3_rad+self.margin_so3
        return max(p/p_limit,theta/theta_limit)

    def _worst_pair_sep_ratio(self,probe_id:str)->float:
        # Unknown current controller response regime must be a competing
        # possibility; refusing to fit the regime on TEST target truths.
        worst=float("inf")
        for i,h1 in enumerate(self.histories):
            for h2 in self.histories[i+1:]:
                for regime1 in self.regimes:
                    for regime2 in self.regimes:
                        a=self.responses[(probe_id,h1,regime1)]
                        b=self.responses[(probe_id,h2,regime2)]
                        worst=min(worst,self._measure_sep_ratio(a,b))
        return worst

    def choose_probe(self)->CandidatePlan:
        if not self.trusted:
            return CandidatePlan(None,"READ_AUTHORITATIVE",0.0,0,
                                 "Untrusted complete history, chart or separately trained observation model",self.histories,False)
        if len(self.histories)==1:
            return CandidatePlan(None,"UNIQUE_HISTORY",float("inf"),0,
                                 "No ambiguous execution history",self.histories,True)
        ranked=[]
        for probe in self.probes.values():
            if not probe.all_history_abi_setpoint_bound_verified or not probe.known_delivery_command_supported:
                continue
            if probe.max_nominal_action_norm>self.max_probe_norm:
                continue
            if any((probe.probe_id,h,r) not in self.responses for h in self.histories for r in self.regimes):
                continue  # missing support must not be filled by optimistic defaults
            margin=self._worst_pair_sep_ratio(probe.probe_id)
            ranked.append((margin,-probe.max_nominal_action_norm,probe.probe_id))
        if not ranked:
            return CandidatePlan(None,"READ_AUTHORITATIVE",0.0,0,
                                 "No native probe with all history/regime response predictions and bounded action",self.histories,True)
        score,_,winner=max(ranked)
        if score<=1.0:
            return CandidatePlan(None,"READ_AUTHORITATIVE",score,0,
                                 "All valid candidates overlap under at least one physical response regime",self.histories,True)
        return CandidatePlan(winner,"EXECUTE_KNOWN_DELIVERED_PROBE",score,
                             self.probes[winner].declared_sensor_sample_events,
                             "Hypotheses predicted distinguishable under each listed response regime; still contingent on model support",
                             self.histories,True)

    def authorize_from_real_public_motion(self,plan:CandidatePlan,obs:PublicMotion,*,current_step:int)->PublicDecision:
        reads=1
        if not self.trusted:
            return PublicDecision(None,"READ","UNTRUSTED_MODEL_OR_CONTROLLER",(),obs.actual_public_sensor_sample_events,reads)
        if plan.decision!="EXECUTE_KNOWN_DELIVERED_PROBE" or plan.probe_id is None:
            return PublicDecision(None,"READ","NO_PHYSICALLY_VALID_DISCRIMINATING_PROBE",(),obs.actual_public_sensor_sample_events,reads)
        if obs.probe_id!=plan.probe_id or not obs.delivery_confirmed:
            return PublicDecision(None,"READ","ACTUAL_PUBLIC_PROBE_DELIVERY_NOT_CONFIRMED",(),obs.actual_public_sensor_sample_events,reads)
        if (type(current_step) is not int or current_step<obs.final_observation_step or
            current_step-obs.final_observation_step>self.max_lag):
            return PublicDecision(None,"READ","STALE_PHYSICAL_PUBLIC_EVIDENCE",(),obs.actual_public_sensor_sample_events,reads)
        if obs.actual_public_sensor_sample_events<plan.predicted_sensor_sample_events:
            return PublicDecision(None,"READ","INCOMPLETE_ACTUAL_PUBLIC_SENSOR_TRANSCRIPT",(),obs.actual_public_sensor_sample_events,reads)
        if plan.conservative_min_sep_ratio<=1.0:
            return PublicDecision(None,"READ","PREDICTION_TUBES_OVERLAP",(),obs.actual_public_sensor_sample_events,reads)
        surviving=[]
        for h in self.histories:
            if any(
                _xyz(obs.observed_after_xyz, self.responses[(plan.probe_id,h,r)].expected_public_xyz)
                   <=self.responses[(plan.probe_id,h,r)].radius_xyz_m
                and _so3(obs.observed_after_quat_xyzw,self.responses[(plan.probe_id,h,r)].expected_public_quat_xyzw)
                   <=self.responses[(plan.probe_id,h,r)].radius_so3_rad
                for r in self.regimes
            ):
                surviving.append(h)
        if len(surviving)!=1:
            return PublicDecision(None,"READ",
                "MODEL_UNSUPPORTED" if len(surviving)==0 else "AMBIGUOUS_PUBLIC_RESPONSE",
                tuple(surviving),obs.actual_public_sensor_sample_events,reads)
        # This is validity ONLY under an externally calibrated, correct
        # physical response tube; it is not a safety or misclassification certificate.
        return PublicDecision(surviving[0],"AUTHORIZE_EMPIRICAL",
             "UNIQUE_COMPLETE_HISTORY_WITHIN_ALL_SUPPORTED_PUBLIC_RESPONSE_TUBES",
             tuple(surviving),obs.actual_public_sensor_sample_events,0)
