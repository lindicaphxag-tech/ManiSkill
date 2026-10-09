"""Risk/coverage authority certificate for hidden robot controller target memory.

Scope: exact Clopper-Pearson under independent/exchangeable calibration
task/reset states WITHIN task, fixed public features, fixed finite threshold grid.
Bonferroni simultaneous task x grid x (risk,coverage) protects calibration
threshold selection. This is NOT physical safety under distribution shift.
Runtime never receives the original commanded-target label.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import comb,ceil,isfinite,log
from typing import Optional,Sequence

def _cdf_leq(k:int,n:int,p:float)->float:
    if k<0:return 0.
    if k>=n:return 1.
    if p<=0:return 1.
    if p>=1:return 0.
    return sum(comb(n,j)*p**j*(1.-p)**(n-j) for j in range(k+1))

def upper_cp(k:int,n:int,tail:float)->float:
    """One-sided exact upper P(error | authorized), NOT posterior belief."""
    if not (type(k) is int and type(n) is int and 0<=k<=n and n>=0 and 0<tail<1):
        raise ValueError("Invalid binomial count/tail")
    if n==0 or k==n:return 1.
    lo,hi=0.,1.
    for _ in range(65):
        mid=(lo+hi)/2
        if _cdf_leq(k,n,mid)>tail:lo=mid
        else:hi=mid
    return hi

def lower_cp(k:int,n:int,tail:float)->float:
    """One-sided exact lower P(authorized), making all-read fail."""
    if not (type(k) is int and type(n) is int and 0<=k<=n and n>=0 and 0<tail<1):
        raise ValueError("Invalid binomial count/tail")
    if n==0 or k==0:return 0.
    lo,hi=0.,1.
    for _ in range(65):
        mid=(lo+hi)/2
        if 1-_cdf_leq(k-1,n,mid)<tail:lo=mid
        else:hi=mid
    return lo

@dataclass(frozen=True)
class LabelledCalibration:
    task:str
    reset_id:int
    score:float
    original_candidate_was_authorized:bool
    true_history_matches_candidate:bool  # calibration audit ONLY
    actual_fault_truth:str # frozen source provenance, not a run-time signal

@dataclass(frozen=True)
class StratumBound:
    task:str
    n:int
    accepted:int
    wrong:int
    risk_upper:float
    coverage_lower:float

@dataclass(frozen=True)
class RiskCertificate:
    certified:bool
    threshold:Optional[float]
    risk_cap:float
    minimum_coverage:float
    failure_probability:float
    tested_thresholds:tuple[float,...]
    tasks:tuple[str,...]
    score_contract:str
    selected_bounds:tuple[StratumBound,...]
    reason:str
    assumptions:tuple[str,...]=(
      "One independent reset observation per task/reset ID; exchangeability within task",
      "Finite threshold grid, task groups and scoring frozen before calibration labels",
      "Privileged true target used ONLY for off-line calibration",
      "No contact/controller/source distribution shift to deployment",
      "Guarantee is conditional hidden-history error among authorized labels, not hardware safety",
    )

def native_public_score(candidate_residuals_m:Sequence[float],
                        epsilon_m:float,margin_m:float,
                        selected_index:int,original_admitted:bool)->float:
    """A deterministic FULLY PUBLIC score; an old rejection cannot be reversed.
    s=min[(eps-r_selected)/eps, (r_second-eps-margin)/eps].
    """
    rs=tuple(float(x) for x in candidate_residuals_m)
    if (len(rs) not in (2,4) or type(selected_index) is not int
        or selected_index not in range(len(rs))
        or any(not isfinite(x) or x<0 for x in rs)
        or not all(isfinite(x) for x in (epsilon_m,margin_m))
        or epsilon_m<=0 or margin_m<0 or type(original_admitted) is not bool):
        raise ValueError("Invalid public source residual geometry")
    if not original_admitted:return float("-inf")
    winner=rs[selected_index]
    second=min(x for i,x in enumerate(rs) if i!=selected_index)
    return min((epsilon_m-winner)/epsilon_m,
               (second-epsilon_m-margin_m)/epsilon_m)

def _validate(rows,tasks,thresholds,risk,coverage,delta):
    if (not tasks or len(set(tasks))!=len(tasks) or not thresholds
        or len(set(thresholds))!=len(thresholds)
        or tuple(sorted(thresholds))!=thresholds
        or any(not isfinite(x) or x<0 for x in thresholds)
        or not 0<risk<1 or not 0<coverage<1 or not 0<delta<1):
        raise ValueError("Unfrozen grid/tasks or invalid risk/coverage controls")
    seen=set()
    allowed=("held/held","held/applied","applied/held","applied/applied")
    for row in rows:
        if (not isinstance(row,LabelledCalibration) or row.task not in tasks
            or type(row.reset_id) is not int or row.reset_id<0
            or type(row.original_candidate_was_authorized) is not bool
            or type(row.true_history_matches_candidate) is not bool
            or (not isfinite(row.score) and row.score!=float("-inf"))
            or row.actual_fault_truth not in allowed
            or (row.task,row.reset_id) in seen):
            raise ValueError("Missing/duplicate label, original trial or malformed audit truth")
        seen.add((row.task,row.reset_id))
    if any(not any(r.task==task for r in rows) for task in tasks):
        raise ValueError("Every registered task stratum needs calibration records")

def calibrate_authority(rows:Sequence[LabelledCalibration],*,
                       tasks:Sequence[str],thresholds:Sequence[float],
                       risk_cap:float,minimum_coverage:float,
                       delta:float=.05)->RiskCertificate:
    """Exact simultaneous selective risk upper AND acceptance coverage lower.
    Each of |tasks|*|grid| tests has two tails δ/(2|tasks||grid|).
    Empirical threshold selection cannot invalidate their union coverage,
    conditional on fixed grid and within-task independently sampled trials.
    """
    tasks=tuple(tasks); thresholds=tuple(float(x) for x in thresholds)
    rows=tuple(rows)
    _validate(rows,tasks,thresholds,risk_cap,minimum_coverage,delta)
    groups={t:[r for r in rows if r.task==t] for t in tasks}
    tail=delta/(2*len(tasks)*len(thresholds))
    eligible=[]
    for threshold in thresholds:
        bounds=[]
        for task in tasks:
            rr=groups[task]
            admitted=[r for r in rr if r.original_candidate_was_authorized
                      and r.score>=threshold]
            n=len(rr);a=len(admitted)
            wrong=sum(not r.true_history_matches_candidate for r in admitted)
            bounds.append(StratumBound(task,n,a,wrong,
                           upper_cp(wrong,a,tail),lower_cp(a,n,tail)))
        if all(b.risk_upper<=risk_cap and b.coverage_lower>=minimum_coverage
               for b in bounds):
            eligible.append((min(b.accepted/b.n for b in bounds),
                             sum(b.accepted for b in bounds)/len(rows),
                             -threshold,threshold,tuple(bounds)))
    if not eligible:
        return RiskCertificate(False,None,risk_cap,minimum_coverage,delta,
            thresholds,tasks,"frozen-public-residual-v1",(),
            "NO_NONTRIVIAL_THRESHOLD_CERTIFIED__AUTHORITY_READ_MANDATORY")
    _,_,_,threshold,bounds=max(eligible)
    return RiskCertificate(True,threshold,risk_cap,minimum_coverage,delta,
        thresholds,tasks,"frozen-public-residual-v1",bounds,
        "UNION_CORRECTED_TASK_EXCHANGEABILITY_CONDITIONAL_CERTIFICATE")

def authorize_online(score:float,task:str,
                     candidate_was_originally_admitted:bool,
                     public_information_attested:bool,
                     certificate:RiskCertificate)->bool:
    """Only public source fields and a FROZEN certificate. No true label."""
    if type(candidate_was_originally_admitted) is not bool or type(public_information_attested) is not bool:
        raise ValueError("Runtime flags must be explicit booleans")
    return bool(certificate.certified and certificate.threshold is not None
                and task in certificate.tasks and public_information_attested
                and candidate_was_originally_admitted
                and isfinite(score) and score>=certificate.threshold)

def required_zero_error_authorizations(*,risk_cap:float,delta:float,
                 threshold_count:int,task_count:int)->int:
    """Per-task MIN accepted calibration count with ZERO errors, not resets."""
    if not (0<risk_cap<1 and 0<delta<1 and
            type(threshold_count) is int and type(task_count) is int
            and threshold_count>0 and task_count>0):
        raise ValueError("Invalid prospective sample parameters")
    return ceil(log(delta/(2*threshold_count*task_count))/log(1-risk_cap))
