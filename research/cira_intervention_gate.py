"""CIRA v0: selective intervention gate using matched task outcomes, not information gain.

This is an experimental research reference, NOT verified task improvement.
The independent unit is the original reset cluster, NOT its repeated ACK arms.
Action-model validation must come from a disjoint physical-data pipeline.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import exp, isfinite, log, sqrt, lgamma
from statistics import mean
from pathlib import Path
import argparse
import json

@dataclass(frozen=True)
class Weights:
    success: float = 1.
    wrong_authority: float = 1.
    privileged_read: float = .02
    extra_step: float = .01
    max_reads: int = 1
    max_extra_steps: int = 1

    def validate(self):
        if (any(not isfinite(x) or x < 0 for x in (self.success,self.wrong_authority,
             self.privileged_read,self.extra_step)) or self.success <= 0
             or self.max_reads < 0 or self.max_extra_steps < 0):
            raise ValueError("Invalid bounded utility")

    @property
    def paired_radius(self):
        # Each paired utility difference is bounded in [-radius,+radius].
        return (self.success+self.wrong_authority+self.privileged_read*self.max_reads
                +self.extra_step*self.max_extra_steps)

@dataclass(frozen=True)
class Outcome:
    success: bool
    wrong_authority: bool
    reads: int
    extra_steps: int

    def utility(self,w):
        if (type(self.success) is not bool or type(self.wrong_authority) is not bool
            or type(self.reads) is not int or type(self.extra_steps) is not int
            or not 0 <= self.reads <= w.max_reads
            or not 0 <= self.extra_steps <= w.max_extra_steps):
            raise ValueError("Invalid or unbounded task outcome")
        return (w.success*self.success-w.wrong_authority*self.wrong_authority
                -w.privileged_read*self.reads-w.extra_step*self.extra_steps)

@dataclass(frozen=True)
class Pair:
    truth: str
    zero: Outcome
    active: Outcome
    matched_public_sensor_budget: bool
    matched_pre_action_state: bool

@dataclass(frozen=True)
class ResetCluster:
    task: str
    controller: str
    reset_id: int
    pairs: tuple[Pair,...]

@dataclass(frozen=True)
class Candidate:
    name: str
    controller: str
    native_action_contract_sha: str
    response_model_contract_sha: str
    independent_fit_reset_ids: tuple[int,...]
    clusters: tuple[ResetCluster,...]
    independently_validated_response_model: bool

@dataclass(frozen=True)
class Decision:
    task: str
    controller: str
    selected: str
    authority: str
    reason: str
    diagnostics: tuple[dict,...]

def cp_upper(k,n,alpha):
    """One-sided Clopper-Pearson upper bound for ANY wrong in an original reset."""
    if type(k) is not int or type(n) is not int or not(0<=k<=n and n>0 and 0<alpha<1):
        raise ValueError("Invalid binomial parameters")
    if k==n:return 1.
    if k==0:return 1.-alpha**(1./n)
    def cdf(p):
        vals=[lgamma(n+1)-lgamma(i+1)-lgamma(n-i+1)+i*log(p)
              +(n-i)*log(1-p) for i in range(k+1)]
        m=max(vals)
        return exp(m)*sum(exp(z-m) for z in vals)
    lo,hi=0.,1.
    for _ in range(64):
        mid=(lo+hi)/2
        if cdf(mid)>alpha:lo=mid
        else:hi=mid
    return (lo+hi)/2

def evaluate(*,candidates,task,controller,live_action_contract_sha,
             weights=Weights(),delta=.05,max_wrong_reset_risk=.1,
             min_utility_gain=0.,min_independent_resets=32,
             required_truths=("0","1","2","3")):
    """Selective probe arbitration; full native-target authority ALWAYS requires a separate gate.

    Under exchangeable independent reset clusters and frozen actions, union-bound
    one-sided Hoeffding paired reward and CP any-wrong risk simultaneously.
    Fail closed to a ZERO physical step + trusted target QUERY. Neither operation
    is assumed physically safe or costless.
    """
    weights.validate()
    if (not task or not controller or not live_action_contract_sha or
        not 0<delta<1 or not 0<=max_wrong_reset_risk<1 or
        not isfinite(min_utility_gain) or min_independent_resets<2 or
        not required_truths or len(set(required_truths))!=len(required_truths) or
        len({c.name for c in candidates})!=len(candidates)):
        raise ValueError("Invalid frozen specification")
    if not candidates:return Decision(task,controller,"ZERO","QUERY","NO_CANDIDATES",())
    alpha=delta/(2*len(candidates))
    diag=[]
    eligible=[]
    for c in candidates:
        errors=[]
        if c.controller!=controller or not c.name or c.name=="ZERO":
            errors.append("CONTROLLER_OR_NAME_MISMATCH")
        if not c.native_action_contract_sha or c.native_action_contract_sha!=live_action_contract_sha:
            errors.append("NATIVE_ACTION_CONTRACT_MISMATCH")
        if not c.response_model_contract_sha or not c.independently_validated_response_model:
            errors.append("ACTION_RESPONSE_MODEL_NOT_INDEPENDENTLY_VALIDATED")
        if not c.independent_fit_reset_ids or len(set(c.independent_fit_reset_ids))!=len(c.independent_fit_reset_ids):
            errors.append("MODEL_FIT_PROVENANCE_MISSING")
        clusters=tuple(x for x in c.clusters if x.task==task and x.controller==controller)
        keys=[(r.task,r.controller,r.reset_id) for r in clusters]
        if len(set(keys))!=len(keys):errors.append("DUPLICATED_RESET_CLUSTER")
        if any(r.reset_id in c.independent_fit_reset_ids for r in clusters):
            errors.append("MODEL_FIT_CALIBRATION_LEAKAGE")
        if len(clusters)<min_independent_resets:errors.append("INSUFFICIENT_INDEPENDENT_RESETS")
        deltas=[]
        wrong_resets=0
        for r in clusters:
            truth_ids=[p.truth for p in r.pairs]
            if (len(r.pairs)!=len(required_truths) or len(set(truth_ids))!=len(truth_ids)
                or set(truth_ids)!=set(required_truths)):
                errors.append("INCOMPLETE_ACK_PAIRING")
                continue
            if not all(p.matched_pre_action_state and p.matched_public_sensor_budget for p in r.pairs):
                errors.append("UNMATCHED_SENSING_OR_INITIAL_STATE")
                continue
            try:
                deltas.append(mean(p.active.utility(weights)-p.zero.utility(weights) for p in r.pairs))
            except ValueError:
                errors.append("INVALID_OUTCOME")
                continue
            wrong_resets+=any(p.active.wrong_authority for p in r.pairs)
        n=len(deltas)
        if n:
            lower=mean(deltas)-weights.paired_radius*sqrt(2*log(1/alpha)/n)
            upper=cp_upper(wrong_resets,n,alpha)
            if lower<=min_utility_gain:errors.append("NO_CONFIDENT_POSITIVE_TASK_ADVANTAGE")
            if upper>max_wrong_reset_risk:errors.append("UNCERTIFIED_COMPLETE_STATE_AUTHORITY_RISK")
        else:
            lower=upper=None
            errors.append("NO_VALID_PAIRED_CLUSTERS")
        row=dict(candidate=c.name,n_independent_resets=n,
                 n_correlated_truth_cells=sum(len(r.pairs) for r in clusters),
                 mean_paired_delta=mean(deltas) if deltas else None,
                 utility_gain_lower_bound=lower,wrong_authority_resets=wrong_resets,
                 wrong_reset_risk_upper_bound=upper,alpha_per_statement=alpha,
                 rejection_reasons=sorted(set(errors)))
        diag.append(row)
        if not errors:eligible.append(row)
    if not eligible:
        return Decision(task,controller,"ZERO","QUERY",
                        "NO_ACTIVELY_BENEFICIAL_RISK_CERTIFIED_ACTION",tuple(diag))
    best=max(eligible,key=lambda row:(row["utility_gain_lower_bound"],row["candidate"]))
    return Decision(task,controller,best["candidate"],"QUERY",
                    "PROBE_SUPPORTED_BUT_COMPLETE_STATE_REQUIRES_SEPARATE_AUTHORITY_GATE",
                    tuple(diag))

def from_source_audit(path,*,arm,fit_reset_ids,controller="FROZEN_PPO_NATIVE",
                      action_sha,response_model_sha="",response_model_validated=False):
    """Consume *externally SHA-verified* 384-row archive, for descriptive analysis ONLY.

    The converter itself cannot prove SHA provenance; accept only after the
    original audit_active_probe_full_task_physx.py verified all producer shards.
    The Oct-10 historical data may NOT be reused as a prospective test set.
    """
    body=json.loads(Path(path).read_text())
    if (body.get("status")!="REAL_COMPLETED_NEW_FREEZE_PPO_TASK_SOURCE_AUDITED"
        or body.get("physically_executed_original_controller_worlds")!=2560
        or body.get("new_independent_reset_clusters")!=32
        or body.get("four_actual_ACK_truths_per_reset")!=4):
        raise ValueError("Wrong PhysX source schema")
    rows=body["all_full_actual_PPO_task_outcomes"]
    if len(rows)!=384:raise ValueError("Incomplete original rows")
    groups={}
    for r in rows:
        if r["arm"]==arm:groups.setdefault((r["task"],r["seed"]),[]).append(r)
    if len(groups)!=32:raise ValueError("Incomplete original reset set")
    clusters=[]
    for (task,reset_id),rr in sorted(groups.items()):
        if set(int(v["truth"]) for v in rr)!={0,1,2,3}:
            raise ValueError("Incomplete ACK source")
        pairs=[]
        for r in rr:
            z=Outcome(bool(r["zero_success"]),bool(r["zero_wrong"]),
                      int(r["zero_privileged_reads"]),0)
            x=Outcome(bool(r["x_success"]),bool(r["x_wrong"]),
                      int(r["x_privileged_reads"]),1)
            pairs.append(Pair(str(r["truth"]),z,x,True,True))
        clusters.append(ResetCluster(task,controller,int(reset_id),tuple(pairs)))
    return Candidate("X",controller,action_sha,response_model_sha,fit_reset_ids,
                     tuple(clusters),response_model_validated)

def main():
    p=argparse.ArgumentParser(description="Historical-only retrospective CIRA gate")
    p.add_argument("--source-audit",required=True)
    p.add_argument("--arm",default="fault_public_t3_fourhistory_or_t4_query")
    p.add_argument("--contract-sha",required=True)
    args=p.parse_args()
    c=from_source_audit(args.source_audit,arm=args.arm,fit_reset_ids=(),
                        action_sha=args.contract_sha)
    for task in ("pull_cube","stack_cube"):
        d=evaluate(candidates=(c,),task=task,controller=c.controller,
                   live_action_contract_sha=args.contract_sha)
        print(json.dumps({"historical_only":True,**asdict(d)},sort_keys=True))

if __name__=="__main__":main()
