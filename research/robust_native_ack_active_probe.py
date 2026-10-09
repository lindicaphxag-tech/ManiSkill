"""Bounded active identification of UNKNOWN native target-execution histories.

No torch, numpy, ManiSkill, privileges, simulator or hidden target labels.
An action *selection* mechanism, not a physical-result claim.

Central NEGATIVE IDENTIFIABILITY fact:
    when gain can be zero, every candidate response set contains x_before.
    Thus no bounded native delta can guarantee unique history identification.
    Refuse the public authority route and request a genuine native target getter.

When independently substantiated nonzero gain lower/upper and bounded error
are provided, rank physically allowed known-delivered probes by the minimum
distance between ENTIRE response sets of every pair of complete target
histories, NOT by a single estimated gain center. A probe is permitted only
if these response sets are disjoint by > 2*epsilon + margin. A post-actuation
public observation must THEN select one unique full target history.

Provenance-sensitive, but NOT real robot safety certification:
- "regime_current" is an external assumption and may be wrong;
- workspace axis bounds are not collision, contact, force or trajectory bounds;
- native target action chart must be separately verified;
- an incorrect model may still confidently select the wrong hidden history.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite,sqrt
from typing import Optional, Sequence, Tuple

XYZ=Tuple[float,float,float]
NATIVE6=Tuple[float,float,float,float,float,float]
QUAT=Tuple[float,float,float,float]

def v3(x,name):
    try:r=tuple(float(z) for z in x)
    except (ValueError,TypeError) as e:raise ValueError(name+" must be numeric XYZ") from e
    if len(r)!=3 or not all(isfinite(z) for z in r):
        raise ValueError(name+" must be exactly THREE finite XYZ numbers")
    return r

def dot(x,y):
    return sum(a*b for a,b in zip(x,y))

def sub(x,y):
    return tuple(a-b for a,b in zip(x,y))

def add(x,y):
    return tuple(a+b for a,b in zip(x,y))

def scale(x,a):
    return tuple(a*z for z in x)

def norm(x):
    return sqrt(dot(x,x))

def clip(x):
    return max(0.,min(1.,x))

def dist_points(a,b):
    return norm(sub(a,b))

def min_segments(a0,a1,b0,b1):
    """Exact Euclidean distance between two closed 3D line segments.

    Check the unconstrained 2D optimum when it lies in the unit square and
    all FOUR possible square boundaries with 1D projection and clamping.
    Works for degenerate zero-length and parallel segments too.
    """
    p0,p1,q0,q1=(v3(x,"3D segment") for x in (a0,a1,b0,b1))
    u=sub(p1,p0);v=sub(q1,q0);w=sub(p0,q0)
    aa=dot(u,u);bb=dot(u,v);cc=dot(v,v)
    dd=dot(u,w);ee=dot(v,w)
    pairs=[(0.,0.),(0.,1.),(1.,0.),(1.,1.)]
    if cc>0:
        pairs.extend([(0.,clip(ee/cc)),
                      (1.,clip((ee+bb)/cc))])
    if aa>0:
        pairs.extend([(clip(-dd/aa),0.),
                      (clip((bb-dd)/aa),1.)])
    det=aa*cc-bb*bb
    if det>1e-14*max(aa*cc,1e-18):
        s=(bb*ee-cc*dd)/det
        t=(aa*ee-bb*dd)/det
        if 0<=s<=1 and 0<=t<=1:pairs.append((s,t))
    return min(norm(sub(add(p0,scale(u,s)),add(q0,scale(v,t))))
               for s,t in pairs)

@dataclass(frozen=True)
class NativeHistory:
    history_id: str
    commanded_target_xyz: XYZ
    target_quaternion_xyzw: QUAT

@dataclass(frozen=True)
class KnownNativeProbe:
    label: str
    normalized_arm_6d: NATIVE6
    native_target_delta_xyz_m: XYZ
    extra_native_control_steps: int = 1

@dataclass(frozen=True)
class ResponseContract:
    gain_lower: float
    gain_upper: float
    model_error_radius_m: float
    separation_margin_m: float
    regime_current_and_independently_validated: bool
    verified_native_target_root_translation_chart: bool

@dataclass(frozen=True)
class ProbeRecommendation:
    mode: str  # QUERY_CONTROLLER_TARGET or APPLY_KNOWN_PROBE_AND_OBSERVE
    reason: str
    probe: Optional[KnownNativeProbe]
    worst_pairwise_response_set_gap_m: float
    precomputed_native_hypothesis_positions_xyz: Tuple[XYZ,...]
    candidate_history_ids: Tuple[str,...]
    public_samples_charged_if_executed: int
    additional_physical_native_steps_if_executed: int
    external_model_validity_not_proved_here: bool

@dataclass(frozen=True)
class FinalAuthority:
    mode: str # QUERY_CONTROLLER_TARGET or CONDITIONAL_FULL_HISTORY_IDENTIFICATION
    selected_history_id: Optional[str]
    reason: str
    public_residuals_m: Tuple[float,...]
    authoritative_native_target_getters_charged_if_fallback: int
    not_a_deterministic_robot_safety_guarantee: bool

def _check_histories(histories):
    if not 2<=len(histories)<=16:
        raise ValueError("A finite UNKNOWN-ACK history set must have 2..16 complete native target possibilities")
    seen=set()
    for h in histories:
        if not h.history_id or h.history_id in seen:
            raise ValueError("Every complete target history must have distinct provenance identity")
        seen.add(h.history_id)
        v3(h.commanded_target_xyz,"complete history target")
        try:q=tuple(float(k) for k in h.target_quaternion_xyzw)
        except (TypeError,ValueError) as e:raise ValueError("Malformed full SE3 rotation") from e
        if len(q)!=4 or not all(isfinite(x) for x in q) or abs(dot(q,q)-1.)>1e-3:
            raise ValueError("History orientation must be a normalized complete quaternion")

def _response_endpoints(achieved,target,contract):
    disp=sub(target,achieved)
    return (add(achieved,scale(disp,contract.gain_lower)),
            add(achieved,scale(disp,contract.gain_upper)))

def _min_response_gap(achieved,targets,contract):
    ends=[_response_endpoints(achieved,t,contract) for t in targets]
    return min(min_segments(*(ends[i]+ends[j])) for i in range(len(ends))
               for j in range(i+1,len(ends)))

def _none(reason,ids=(),gap=0.):
    return ProbeRecommendation("QUERY_CONTROLLER_TARGET",reason,None,
                               gap,(),tuple(ids),0,0,True)

def choose_native_probe(
    achieved_xyz: XYZ,
    candidate_complete_histories: Sequence[NativeHistory],
    available_known_delivered_probes: Sequence[KnownNativeProbe],
    response: ResponseContract,
    *,
    max_native_target_perturbation_m: float,
    workspace_lower_xyz: XYZ,
    workspace_upper_xyz: XYZ
) -> ProbeRecommendation:
    """Physically constrained finite-probe *selector*, without any true state.

    A zero lower response gain ALWAYS fails. This is a genuine no-go result,
    independent of whichever candidate action maximizes the test score.
    """
    x=v3(achieved_xyz,"public achieved")
    _check_histories(candidate_complete_histories)
    ids=tuple(h.history_id for h in candidate_complete_histories)
    if not (response.regime_current_and_independently_validated and
            response.verified_native_target_root_translation_chart):
        return _none("UNVERIFIED_CURRENT_RESPONSE_REGIME_OR_ACTION_CHART",ids)
    a,b=response.gain_lower,response.gain_upper
    eps,guard=response.model_error_radius_m,response.separation_margin_m
    if not all(isfinite(t) for t in (a,b,eps,guard,max_native_target_perturbation_m)):
        raise ValueError("Nonfinite measured physics model/gain envelope")
    if not (0<=a<=b<=1 and 0<=eps<1 and 0<=guard<1 and
            max_native_target_perturbation_m>0):
        raise ValueError("Invalid gain, error bound, separation margin, or native motion budget")
    if a==0:
        return _none("ZERO_GAIN_ADMISSIBLE_NO_UNIFORM_IDENTIFIABILITY",ids)
    lo=v3(workspace_lower_xyz,"workspace_lower")
    hi=v3(workspace_upper_xyz,"workspace_upper")
    if any(l>=h for l,h in zip(lo,hi)):
        raise ValueError("Invalid control workspace")
    choices=[]
    for probe in available_known_delivered_probes:
        xyz=v3(probe.native_target_delta_xyz_m,"probe native delta")
        u=tuple(float(z) for z in probe.normalized_arm_6d)
        if len(u)!=6 or any(not isfinite(z) or abs(z)>1 for z in u):
            raise ValueError("Native probe must be feasible finite normalized controller action")
        if not probe.label or probe.extra_native_control_steps!=1:
            raise ValueError("A genuine one-step precommitted known-delivered native candidate is required")
        if norm(xyz)>max_native_target_perturbation_m+1e-9:
            continue
        targets=tuple(add(v3(h.commanded_target_xyz,"history"),xyz)
                      for h in candidate_complete_histories)
        if any(any(y<l-1e-10 or y>h+1e-10 for y,l,h in zip(t,lo,hi)) for t in targets):
            continue
        gap=_min_response_gap(x,targets,response)
        # Utility prioritizes GENUINE worst-case response-set separation; a
        # lower intervention norm only breaks ties. No subjective arbitrary
        # task reward or false collision certificate.
        choices.append((gap,-norm(xyz),probe.label,probe,targets))
    if not choices:
        return _none("NO_PHYSICALLY_BOUNDED_NATIVE_PROBE_FOR_ALL_HISTORY_TARGETS",ids)
    score,cost,label,best,targets=max(choices,key=lambda k:(k[0],k[1],k[2]))
    if score<=2*eps+guard:
        return _none("ALL_BOUNDED_PROBES_HAVE_OVERLAPPING_RESPONSE_UNCERTAINTY_SETS",ids,score)
    return ProbeRecommendation(
        "APPLY_KNOWN_PROBE_AND_OBSERVE",
        "UNIFORM_PAIRWISE_RESPONSE_SET_DISJOINT_UNDER_EXPLICIT_CURRENT_MODEL",
        best,score,targets,ids,2,1,True)

def _segment_dist_to_observation(achieved,obs,target,contract):
    p,q=_response_endpoints(achieved,target,contract)
    direction=sub(q,p)
    den=dot(direction,direction)
    t=clip(dot(sub(obs,p),direction)/den) if den else 0.
    return norm(sub(obs,add(p,scale(direction,t))))

def authorize_after_physical_probe(
    recommendation: ProbeRecommendation,
    before_public_xyz: XYZ,
    observed_after_public_xyz: XYZ,
    *,
    known_delivered_native_probe_ACK: bool,
    response: ResponseContract
) -> FinalAuthority:
    """The decision may only be taken AFTER a true physically applied probe.

    No hidden controller target can enter this branch. The selected history
    is STILL conditional on the response model being correct at t4.
    """
    def query(reason,rs=()):
        return FinalAuthority("QUERY_CONTROLLER_TARGET",None,reason,tuple(rs),1,True)
    if recommendation.mode!="APPLY_KNOWN_PROBE_AND_OBSERVE":
        return query("NO_MODEL_SEPARATING_KNOWN_ACTUATION")
    if not known_delivered_native_probe_ACK:
        return query("PROBE_DELIVERY_UNCERTAIN_NO_PUBLIC_AUTHORIZATION")
    if not (response.regime_current_and_independently_validated and
            response.verified_native_target_root_translation_chart):
        return query("RESPONSE_ASSUMPTIONS_NO_LONGER_CONFIRMED")
    before=v3(before_public_xyz,"before_public")
    after=v3(observed_after_public_xyz,"after_public")
    if not recommendation.precomputed_native_hypothesis_positions_xyz:
        raise ValueError("Impossible authorized probe without prior full target history")
    residuals=tuple(_segment_dist_to_observation(before,after,t,response)
                    for t in recommendation.precomputed_native_hypothesis_positions_xyz)
    eps=response.model_error_radius_m
    allowed=[i for i,z in enumerate(residuals) if z<=eps+1e-12]
    if len(allowed)!=1:
        return query("POSTPHYSX_RESPONSE_NONUNIQUE_OR_MODEL_INVALID",residuals)
    i=allowed[0]
    if any(z<=eps+response.separation_margin_m for j,z in enumerate(residuals) if j!=i):
        return query("MODEL_HISTORY_WINNER_NOT_SEPARATED",residuals)
    return FinalAuthority(
        "CONDITIONAL_FULL_HISTORY_IDENTIFICATION",
        recommendation.candidate_history_ids[i],
        "EMPIRICAL_RESPONSE_VALIDITY_REQUIRED_NOT_CERTIFIED_ROBOT_SAFETY",
        residuals,0,True)
