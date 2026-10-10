"""Controller-memory recoverability contracts for research, independent of physics runtime.

This is a formal finite-hypothesis reference for ManiSkill-style ROOT-translation
and LEFT-root-relative SO(3) target semantics. It does NOT infer hidden controller
targets from achieved end-effector poses, nor certify IK, collision or contact.
Native write requires a separately verified privileged setter.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from math import acos, isfinite, sqrt

MAX_HYPOTHESES = 16

def _vector(x, size):
    v=tuple(float(t) for t in x)
    if len(v)!=size or not all(isfinite(t) for t in v):
        raise ValueError("Finite fixed-size vector required")
    return v

def _quat(q):
    q=_vector(q,4)
    n=sqrt(sum(x*x for x in q))
    if n<=1e-14:raise ValueError("Zero rotation quaternion")
    return tuple(x/n for x in q)

def _qmul(p,q):
    x,y,z,w=p
    a,b,c,d=q
    return _quat((w*a+x*d+y*c-z*b,w*b-x*c+y*d+z*a,w*c+x*b-y*a+z*d,w*d-x*a-y*b-z*c))

def _angle(p,q):
    dot=min(1.0,abs(sum(x*y for x,y in zip(p,q))))
    return 2*acos(dot)

@dataclass(frozen=True)
class Target:
    position: tuple[float,float,float]
    quaternion_xyzw: tuple[float,float,float,float]
    def __post_init__(self):
        object.__setattr__(self,"position",_vector(self.position,3))
        object.__setattr__(self,"quaternion_xyzw",_quat(self.quaternion_xyzw))

@dataclass(frozen=True)
class Belief:
    """Finite explicit hypotheses, not a probability distribution."""
    hypotheses: tuple[Target,...]
    def __post_init__(self):
        if not 1<=len(self.hypotheses)<=MAX_HYPOTHESES:
            raise ValueError("Requires 1..16 native target hypotheses")
        if not all(isinstance(h,Target) for h in self.hypotheses):
            raise TypeError("Target type/provenance required")

@dataclass(frozen=True)
class Diameter:
    translation_linf_m: float
    rotation_geodesic_rad: float

@dataclass(frozen=True)
class RecoveryEffect:
    operation: str
    belief_after: Belief
    before: Diameter
    after: Diameter
    privileged_reads: int
    privileged_writes: int
    changed_physical_target: bool
    exact_memory_identity_restored: bool
    scope: str

def diameter(belief):
    if not isinstance(belief,Belief):raise TypeError("Explicit belief required")
    pairs=list(combinations(belief.hypotheses,2))
    return Diameter(
        max((max(abs(a-b) for a,b in zip(x.position,y.position)) for x,y in pairs),default=0.),
        max((_angle(x.quaternion_xyzw,y.quaternion_xyzw) for x,y in pairs),default=0.))

def relative_target_command(belief, *, root_translation_m, root_left_rotation_xyzw,
                            verified_native_frame:bool):
    """For EXACT root-relative target actions, memory diameter cannot contract."""
    if verified_native_frame is not True:
        raise ValueError("Controller action chart is not independently verified")
    t=_vector(root_translation_m,3);q=_quat(root_left_rotation_xyzw)
    before=diameter(belief)
    after_belief=Belief(tuple(Target(tuple(p+d for p,d in zip(h.position,t)),
                                    _qmul(q,h.quaternion_xyzw))
                              for h in belief.hypotheses))
    after=diameter(after_belief)
    if (abs(before.translation_linf_m-after.translation_linf_m)>1e-9
        or abs(before.rotation_geodesic_rad-after.rotation_geodesic_rad)>1e-7):
        raise ArithmeticError("Native group-action relative-distance invariant violated")
    return RecoveryEffect("RELATIVE_NATIVE_TARGET",after_belief,before,after,
        0,0,any(abs(x)>1e-12 for x in t) or _angle(q,(0,0,0,1))>1e-12,
        len(after_belief.hypotheses)==1,
        "Known SE3 root-relative target action: belief support is transported, not identified")

def public_observation_without_validated_likelihood(belief):
    """No post-hoc pruning from public achieved movement without valid likelihood."""
    d=diameter(belief)
    return RecoveryEffect("PUBLIC_OBSERVATION_ONLY",belief,d,d,0,0,False,
        len(belief.hypotheses)==1,"Public sensing cannot silently become controller authority")

def trusted_target_read(belief,*,verified_native_target:Target,provenance_attested:bool):
    """Changes knowledge but does NOT mutate hidden controller target."""
    if provenance_attested is not True or not isinstance(verified_native_target,Target):
        raise ValueError("Trusted getter provenance and actual target required")
    after=Belief((verified_native_target,))
    return RecoveryEffect("TRUSTED_NATIVE_TARGET_READ",after,diameter(belief),
                          diameter(after),1,0,False,True,
                          "Epistemic collapse only; physical controller state is unchanged")

def privileged_public_reanchor(belief, *,public_achieved:Target,
                               internal_write_verified:bool,controller_contract_verified:bool):
    """Simulator-internal privileged write, NOT a hardware actuator primitive."""
    if (internal_write_verified is not True or controller_contract_verified is not True
        or not isinstance(public_achieved,Target)):
        raise ValueError("No state collapse without real setter success and trusted chart")
    after=Belief((public_achieved,))
    return RecoveryEffect("PRIVILEGED_NATIVE_TARGET_WRITE",after,diameter(belief),
                          diameter(after),0,1,True,True,
                          "Target rewritten using public achieved pose; IK/task outcome unverified")
