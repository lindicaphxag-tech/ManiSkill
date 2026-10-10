"""Finite-grid, reset-cluster confidence calibration for controller authorization.

Each independent task reset contains ALL correlated ACK truths. Endpoint is
any wrong authorization in a whole reset, conditional on any authorization.
Assumes iid resets within frozen task strata and frozen public scoring / grid.
Not per-action risk, contact safety, or distribution-shift certification.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, isfinite, lgamma, log

@dataclass(frozen=True)
class Cell:
    truth: str
    public_score: float
    correct_afterrun: bool

@dataclass(frozen=True)
class Cluster:
    task: str
    seed: int
    truths: tuple[Cell, ...]

@dataclass(frozen=True)
class Bound:
    task: str
    threshold: float
    n_resets: int
    n_any_authorized: int
    n_any_wrong: int
    upper_unconditional_wrong: float
    lower_any_authorized: float
    upper_conditional_wrong: float

@dataclass(frozen=True)
class Gate:
    certified: bool
    threshold: float | None
    bounds: tuple[Bound,...]
    delta: float
    reason: str

def _tail(n,k,p,high):
    if p==0: return float((0>=k) if high else (0<=k))
    if p==1: return float((n>=k) if high else (n<=k))
    terms=range(k,n+1) if high else range(k+1)
    r,q=log(p),log(1-p);ln=lgamma(n+1)
    v=[ln-lgamma(i+1)-lgamma(n-i+1)+i*r+(n-i)*q for i in terms]
    m=max(v)
    return min(1.,exp(m)*sum(exp(x-m) for x in v))

def cp_upper(k:int,n:int,alpha:float)->float:
    if not(type(k) is int and type(n) is int and 0<=k<=n and n>=1 and 0<alpha<1):
        raise ValueError('bad Clopper-Pearson arguments')
    if k==n:return 1.
    if k==0:return 1.-alpha**(1./n)
    lo,hi=0.,1.
    for _ in range(55):
        mid=(lo+hi)/2
        if _tail(n,k,mid,False)>alpha:lo=mid
        else:hi=mid
    return (lo+hi)/2

def cp_lower(k:int,n:int,alpha:float)->float:
    if not(type(k) is int and type(n) is int and 0<=k<=n and n>=1 and 0<alpha<1):
        raise ValueError('bad Clopper-Pearson arguments')
    if k==0:return 0.
    if k==n:return alpha**(1./n)
    lo,hi=0.,1.
    for _ in range(55):
        mid=(lo+hi)/2
        if _tail(n,k,mid,True)<alpha:lo=mid
        else:hi=mid
    return (lo+hi)/2

def _partition(clusters,tasks,grid):
    if not tasks or len(set(tasks))!=len(tasks) or not grid or len(set(grid))!=len(grid) or any(not isfinite(x) for x in grid):
        raise ValueError('predeclared task/grid required')
    by={t:[] for t in tasks};seen=set();pattern=None
    for c in clusters:
        key=(c.task,c.seed)
        if c.task not in by or type(c.seed) is not int or key in seen or not c.truths:
            raise ValueError('unregistered/repeated/missing reset')
        seen.add(key)
        truths=tuple(v.truth for v in c.truths)
        if len(set(truths))!=len(truths) or (pattern is not None and pattern!=truths):
            raise ValueError('missing or reordered correlated truth conditions')
        pattern=truths
        if any(not isfinite(v.public_score) or type(v.correct_afterrun) is not bool for v in c.truths):
            raise ValueError('invalid public score or truth label')
        by[c.task].append(c)
    if any(not x for x in by.values()):raise ValueError('missing task population')
    return by

def calibrate(clusters:tuple[Cluster,...],*,tasks:tuple[str,...],grid:tuple[float,...],
              delta:float=.05,conditional_cap:float=.1,min_coverage:float=.2)->Gate:
    """Bonferroni simultaneous CP over 2 tails, tasks, frozen grid.

    W=P(any wrong in reset), C=P(any authorize in reset),
    hence P(wrong reset|authorized reset)=W/C<=U_CP(W)/L_CP(C).
    """
    by=_partition(clusters,tasks,grid)
    if not 0<delta<1 or not 0<conditional_cap<1 or not 0<=min_coverage<1:
        raise ValueError('invalid gate budgets')
    eta=delta/(2*len(tasks)*len(grid))
    eligible=[]
    for th in grid:
        bs=[]
        for task,rows in by.items():
            n=len(rows)
            a=sum(any(x.public_score>=th for x in c.truths) for c in rows)
            k=sum(any(not x.correct_afterrun and x.public_score>=th for x in c.truths) for c in rows)
            u=cp_upper(k,n,eta);low=cp_lower(a,n,eta)
            bs.append(Bound(task,th,n,a,k,u,low,min(1.,u/low) if low>0 else 1.))
        bounds=tuple(bs)
        if all(b.upper_conditional_wrong<=conditional_cap and b.lower_any_authorized>=min_coverage for b in bounds):
            eligible.append((th,bounds))
    if not eligible:
        return Gate(False,None,(),delta,'NO_CERTIFIABLE_NONTRIVIAL_AUTHORITY_ALWAYS_QUERY')
    th,bs=max(eligible,key=lambda x:(min(y.lower_any_authorized for y in x[1]),
              sum(y.n_any_authorized for y in x[1]),x[0]))
    return Gate(True,th,bs,delta,'FINITE_GRID_RESET_CLUSTER_CALIBRATED')

def decide(public_score:float,gate:Gate)->str:
    """No truth at runtime. Any non-finite score or failed gate queries."""
    return ('AUTHORIZE' if isfinite(public_score) and gate.certified
            and public_score>=gate.threshold else 'QUERY')

if __name__=='__main__':
    import json
    from dataclasses import asdict
    data=tuple(Cluster(t,i,(Cell('held',1.,True),Cell('applied',1.,True)))
               for t in ('pull','stack') for i in range(128))
    print(json.dumps(asdict(calibrate(data,tasks=('pull','stack'),grid=(0.,.25,.5,1.))),indent=2))
