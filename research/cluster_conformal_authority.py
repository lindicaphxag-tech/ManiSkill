"""Cluster-conformal CONTROLLER-HISTORY SETS, not selective risk certification.

Calibration unit: independent reset; within each reset four ACK truths are
CORRELATED, so use the MAX nonconformity over all four physical truths.
For an exchangeable new reset, conformal marginal simultaneous containment
over its FOUR registered truths is >=1-alpha (subject to no score/model tuning
on calibration). This DOES NOT guarantee P(wrong | authorized) <= alpha.
Do not interpret it as robot collision safety or OOD shift guarantee.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class CalibratedSet:
    n_independent_resets: int
    error_budget: float
    rank_index: int
    max_source_nonconformity_threshold: float
    finite_power: bool
    task: str
    probe: str

def cluster_calibrate(records,*,task:str,probe:str,alpha:float)->CalibratedSet:
    """records: iterable of (seed, truth_index, (p0..p3), audit_TRUE_index)."""
    if not 0<alpha<1:raise ValueError("Invalid conformal error budget")
    groups={}
    for seed,truth,prob,target in records:
        if type(seed) is not int or type(truth) is not int or truth not in range(4):
            raise ValueError("Invalid true physical cluster")
        if (not isinstance(prob,(tuple,list)) or len(prob)!=4
            or any(not math.isfinite(p) or p<0 for p in prob)
            or abs(sum(prob)-1)>1e-5
            or type(target) is not int or target not in range(4)):
            raise ValueError("Invalid full probabilistic hypothesis distribution")
        g=groups.setdefault(seed,{})
        if truth in g:raise ValueError("Duplicate physical ACK condition")
        g[truth]=1-float(prob[target])
    n=len(groups)
    if n==0 or any(set(v)!=set(range(4)) for v in groups.values()):
        raise ValueError("Missing repeated ACK truth branches per reset")
    scores=sorted(max(x.values()) for x in groups.values())
    k=math.ceil((n+1)*(1-alpha)-1e-12)
    q=scores[k-1] if k<=n else float("inf")
    return CalibratedSet(n,alpha,k,q,k<=n,task,probe)

def predict_set(prob,certificate:CalibratedSet):
    if not isinstance(prob,(tuple,list)) or len(prob)!=4:
        return (0,1,2,3)
    if any(not math.isfinite(x) or x<0 for x in prob) or abs(sum(prob)-1)>1e-5:
        return (0,1,2,3)
    q=certificate.max_source_nonconformity_threshold
    # Underpowered calibration deliberately includes all histories, no
    # confident singleton. Conformal thresholds are NOT arbitrary tuned scores.
    if not certificate.finite_power:return (0,1,2,3)
    return tuple(i for i,p in enumerate(prob) if 1-p<=q+1e-12)

def choose_authority(prob,certificate:CalibratedSet)->tuple[str,int|None]:
    v=predict_set(prob,certificate)
    return ("AUTHORIZE",v[0]) if len(v)==1 else ("QUERY",None)

def required_resets_for_finite_threshold(alpha):
    if not 0<alpha<1:raise ValueError("Invalid alpha")
    return math.ceil((1-alpha)/alpha-1e-12)
