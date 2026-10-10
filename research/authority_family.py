"""Small-model worst-case episode-risk comparator for a frozen kernel family.

A common observation-contingent policy must be valid under EVERY listed model.
This is enumerative sensitivity analysis, not a confidence region or formal
safety certification under unlisted models. Keep horizons small.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from research.authority_budget import BudgetModel, validate, all_trees, evaluate_unpruned, TOL

@dataclass(frozen=True)
class FamilyDecision:
    policy: object
    worst_cost: float
    worst_risk: float
    per_model_costs: tuple[float,...]
    per_model_risks: tuple[float,...]
    policies_evaluated: int

def _family(models: tuple[BudgetModel,...]):
    if not models: raise ValueError('No models')
    for m in models:validate(m)
    a=models[0]
    fixed=lambda m:(m.states,m.initial,m.repairs,m.loss,m.query_cost,
                    m.failed_states,m.failure_cost,m.bad_loss_cutoff,
                    tuple((p.name,p.cost,p.observations) for p in m.probes))
    for m in models[1:]:
        if fixed(m)!=fixed(a):
            raise ValueError('Family only varies causal transition probabilities')

def family_choice(models: tuple[BudgetModel,...],horizon: int,budget: float)->FamilyDecision | None:
    _family(models)
    if type(horizon) is not int or not 0<=horizon<=2 or not isfinite(budget) or not 0<=budget<=1:
        raise ValueError('Exhaustive family comparison limited to horizon 0..2 and valid budgets')
    best=None
    count=0
    for tree in all_trees(models[0],horizon):
        count+=1
        values=tuple(evaluate_unpruned(m,tree) for m in models)
        risk=max(v[1] for v in values)
        if risk>budget+TOL:continue
        cost=max(v[0] for v in values)
        if best is None or cost<best.worst_cost-TOL or (
            abs(cost-best.worst_cost)<=TOL and risk<best.worst_risk-TOL):
            best=FamilyDecision(tree,cost,risk,tuple(v[0] for v in values),
                                tuple(v[1] for v in values),0)
    return None if best is None else FamilyDecision(best.policy,best.worst_cost,
        best.worst_risk,best.per_model_costs,best.per_model_risks,count)

def altered_failure_rate(m:BudgetModel, rate:float)->BudgetModel:
    """Diagnostic source-independent SHIFT ONLY; not fitted to real PhysX."""
    from dataclasses import replace
    if not 0<=rate<=1:raise ValueError('Invalid shifted failure probability')
    new=[]
    for p in m.probes:
        rows=[]
        for i,row in enumerate(p.kernel):
            if m.failed_states[i]:
                rows.append(row)
                continue
            original_success=sum(v[k] for v in row for k in range(len(m.states))
                                 if not m.failed_states[k])
            original_failure=1-original_success
            updated=[]
            for sub in row:
                updated.append(tuple(
                    (v*(1-rate)/original_success if original_success else 0.)
                    if not m.failed_states[k] else
                    (v*rate/original_failure if original_failure else 0.)
                    for k,v in enumerate(sub)))
            rows.append(tuple(updated))
        new.append(replace(p,kernel=tuple(rows)))
    return replace(m,probes=tuple(new))
