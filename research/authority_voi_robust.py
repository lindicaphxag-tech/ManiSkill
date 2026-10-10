"""Finite minimax sensitivity check over a PREDECLARED sensor-kernel set.

This is a one-step synthetic strong comparator, NOT a calibrated confidence
set, hardware safety certificate, or demonstration of native robot probing.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import inf
from research.authority_voi import Model, Probe, EPS, one_step_plan, validate

@dataclass(frozen=True)
class RobustPlan:
    probe_name: str
    worst_expected_loss: float
    action_per_outcome: tuple[str, ...]
    candidate_models: int

def _same_contract(models: tuple[Model, ...]) -> None:
    if not models:
        raise ValueError("At least one explicit frozen model is required")
    for m in models:
        validate(m)
    ref=models[0]
    for m in models[1:]:
        if (m.states,m.prior,m.actions,m.action_loss,m.query_cost,
            m.risk_cap,m.bad_loss_cutoff)!=(ref.states,ref.prior,ref.actions,
            ref.action_loss,ref.query_cost,ref.risk_cap,ref.bad_loss_cutoff):
            raise ValueError("Model family changes authority, costs, or prior")
        if tuple((p.name,p.cost,p.outcomes) for p in m.probes)!=tuple(
           (p.name,p.cost,p.outcomes) for p in ref.probes):
            raise ValueError("Model family changes probe identity/cost/outcomes")

def outcome_policy_cost(model:Model, probe_name:str,
                        action_per_outcome:tuple[str,...])->float:
    """Score one FROZEN observable contingent policy under a chosen model."""
    validate(model)
    p=next((x for x in model.probes if x.name==probe_name),None)
    if p is None:
        raise ValueError("Unregistered probe")
    if len(action_per_outcome)!=len(p.outcomes):
        raise ValueError("Incomplete contingent policy")
    total=p.cost
    for j,chosen in enumerate(action_per_outcome):
        joint=tuple(prob*p.likelihood[h][j]
                    for h,prob in enumerate(model.prior))
        mass=sum(joint)
        if mass<=0:
            continue
        if chosen=="QUERY":
            total+=mass*model.query_cost
            total+=sum(joint[h]*min(row[h] for row in model.action_loss)
                       for h in range(len(model.states)))
        elif chosen in model.actions:
            losses=model.action_loss[model.actions.index(chosen)]
            bad=sum(joint[h] for h in range(len(model.states))
                    if losses[h]>model.bad_loss_cutoff)/mass
            if model.risk_cap is not None and bad>model.risk_cap+EPS:
                return inf
            total+=sum(joint[h]*losses[h] for h in range(len(model.states)))
        else:
            raise ValueError("Unknown repair action")
    return total

def minimax_plan(models:tuple[Model,...])->RobustPlan:
    """Exhaustive model-set worst loss over all sensor-contingent policies."""
    _same_contract(models)
    m=models[0]
    baseline=one_step_plan(m)
    best=RobustPlan("none",baseline.expected_total_loss,
                    (baseline.decisions[0][1].action or "QUERY",),len(models))
    for p in m.probes:
        for candidate in product(m.actions+("QUERY",),repeat=len(p.outcomes)):
            worst=max(outcome_policy_cost(model,p.name,candidate)
                      for model in models)
            if worst<best.worst_expected_loss-EPS:
                best=RobustPlan(p.name,worst,tuple(candidate),len(models))
    return best

def shifted_sensor_pair()->tuple[Model,Model]:
    """CONSTRUCTED sensor label flip; no native/PhysX readings were used."""
    def make(correct:float)->Model:
        p=Probe("signal",.1,("signal_a","signal_b"),
                ((correct,1-correct),(1-correct,correct)))
        return Model(("h_a","h_b"),(.5,.5),("repair_a","repair_b"),
                     ((0.,10.),(10.,0.)),2.,(p,),risk_cap=.1)
    return make(.95),make(.05)
