"""Exact chance-constrained action-conditioned belief planning (finite reference).

Scope: frozen finite P(h_next,obs|h,probe), additive modeled cost,
probability of EVER hitting an explicit failed state OR making a bad terminal
repair. Failure is absorbing for this planner. Model-conditional, not a
physical safety certificate, novel POMDP theorem, or native PhysX result.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import inf, isclose, isfinite

TOL = 1e-10

@dataclass(frozen=True)
class Probe:
    name: str
    cost: float
    observations: tuple[str, ...]
    kernel: tuple[tuple[tuple[float, ...], ...], ...]  # old, observation, new

@dataclass(frozen=True)
class BudgetModel:
    states: tuple[str, ...]
    initial: tuple[float, ...]
    repairs: tuple[str, ...]
    loss: tuple[tuple[float, ...], ...]
    query_cost: float
    probes: tuple[Probe, ...]
    failed_states: tuple[bool, ...]
    failure_cost: float
    bad_loss_cutoff: float = 0.

@dataclass(frozen=True)
class Option:
    cost: float
    risk: float
    kind: str
    name: str
    children: tuple[tuple[str, 'Option'], ...] = ()

def _prob(v):
    return bool(v) and all(isfinite(x) and x >= 0 for x in v) and isclose(sum(v), 1., rel_tol=0, abs_tol=TOL)

def validate(m: BudgetModel) -> None:
    n = len(m.states)
    if not n or len(set(m.states)) != n or len(m.initial) != n or not _prob(m.initial):
        raise ValueError('Invalid states/prior')
    if not m.repairs or len(set(m.repairs)) != len(m.repairs) or len(m.loss) != len(m.repairs):
        raise ValueError('Invalid repair names')
    if any(len(x) != n or any(not isfinite(y) or y < 0 for y in x) for x in m.loss):
        raise ValueError('Invalid repair loss')
    if len(m.failed_states) != n or any(type(x) is not bool for x in m.failed_states):
        raise ValueError('Explicit boolean failed-state mask required')
    if sum(b for b, fail in zip(m.initial, m.failed_states) if fail) > TOL:
        raise ValueError('Initial state must not have pre-existing unaccounted failure')
    if any(not isfinite(x) or x < 0 for x in (m.query_cost, m.failure_cost)) or not isfinite(m.bad_loss_cutoff):
        raise ValueError('Invalid costs')
    seen = set(m.repairs) | {'QUERY'}
    for p in m.probes:
        if not p.name or p.name in seen or not isfinite(p.cost) or p.cost < 0:
            raise ValueError('Invalid probe identity/cost')
        seen.add(p.name)
        if not p.observations or len(set(p.observations)) != len(p.observations) or len(p.kernel) != n:
            raise ValueError('Malformed probe')
        for i, row in enumerate(p.kernel):
            if len(row) != len(p.observations) or any(len(v) != n for v in row):
                raise ValueError('Malformed kernel shape')
            if not _prob(tuple(q for v in row for q in v)):
                raise ValueError('Not a stochastic joint kernel')
            if m.failed_states[i] and any(v[k] > TOL for v in row for k in range(n) if not m.failed_states[k]):
                raise ValueError('Failure states must remain absorbing')

def terminal_options(m: BudgetModel, belief: tuple[float, ...]) -> list[Option]:
    n = len(belief)
    minimum = tuple(min(m.loss[a][i] for a in range(len(m.repairs))) for i in range(n))
    q_cost = m.query_cost + sum(belief[i] * minimum[i] for i in range(n))
    q_risk = sum(belief[i] for i in range(n) if minimum[i] > m.bad_loss_cutoff)
    result = [Option(q_cost, q_risk, 'query', 'QUERY')]
    for name, row in zip(m.repairs, m.loss):
        value = sum(x*y for x,y in zip(belief, row))
        risk = sum(belief[i] for i in range(n) if row[i] > m.bad_loss_cutoff)
        result.append(Option(value, risk, 'repair', name))
    return result

def _successors(m: BudgetModel, p: Probe, belief: tuple[float, ...]):
    """Return pre-normalized alive branches and immediate failure probability."""
    n = len(belief)
    fail = 0.
    branches = []
    for j, obs in enumerate(p.observations):
        nxt = tuple(sum(belief[i] * p.kernel[i][j][k] for i in range(n)) for k in range(n))
        fail += sum(nxt[k] for k in range(n) if m.failed_states[k])
        alive = tuple(nxt[k] if not m.failed_states[k] else 0. for k in range(n))
        mass = sum(alive)
        if mass > TOL:
            branches.append((obs, mass, tuple(x/mass for x in alive)))
    return fail, branches

def _pareto(options: list[Option]) -> tuple[Option, ...]:
    """Removing any cost/risk-dominated option preserves risk-budget optimum."""
    ordered = sorted(options, key=lambda x: (x.cost, x.risk, x.kind, x.name))
    kept: list[Option] = []
    minrisk = inf
    for opt in ordered:
        if opt.risk < minrisk - TOL:
            kept.append(opt)
            minrisk = opt.risk
    return tuple(kept)

def frontier(m: BudgetModel, horizon: int, belief: tuple[float, ...] | None = None) -> tuple[Option,...]:
    validate(m)
    if type(horizon) is not int or horizon < 0:
        raise ValueError('Horizon must be a nonnegative integer')
    b = m.initial if belief is None else tuple(belief)
    if len(b) != len(m.states) or not _prob(b) or any(b[i] > TOL for i in range(len(b)) if m.failed_states[i]):
        raise ValueError('Posterior invalid or already failed')
    def rec(prior: tuple[float,...], depth: int) -> tuple[Option,...]:
        options = terminal_options(m, prior)
        if depth:
            for p in m.probes:
                probability_failed, branches = _successors(m,p,prior)
                descendants = [rec(after, depth-1) for _, _, after in branches]
                for selected in product(*descendants):
                    cost = p.cost + probability_failed * m.failure_cost
                    risk = probability_failed
                    for (_, mass, _), child in zip(branches, selected):
                        cost += mass * child.cost
                        risk += mass * child.risk
                    options.append(Option(cost, min(risk,1.), 'probe', p.name,
                        tuple((br[0], child) for br, child in zip(branches, selected))))
        return _pareto(options)
    return rec(b, horizon)

def choose(m: BudgetModel, horizon: int, risk_budget: float) -> Option | None:
    if not isfinite(risk_budget) or not 0 <= risk_budget <= 1:
        raise ValueError('Invalid whole-episode risk budget')
    admissible = [o for o in frontier(m,horizon) if o.risk <= risk_budget + TOL]
    return min(admissible, key=lambda x: (x.cost, x.risk, x.name)) if admissible else None

def all_trees(m: BudgetModel, horizon: int):
    """Unpruned full contingent-policy class, separate from Pareto recursion."""
    if type(horizon) is not int or horizon < 0:
        raise ValueError('Bad horizon')
    yield from ('QUERY',) + m.repairs
    if horizon:
        subtrees = tuple(all_trees(m,horizon-1))
        for p in m.probes:
            for combo in product(subtrees, repeat=len(p.observations)):
                yield (p.name,combo)

def evaluate_unpruned(m: BudgetModel, tree) -> tuple[float,float]:
    """Independent joint-mass path enumeration, never calls _pareto/frontier."""
    validate(m)
    def rec(policy, alive):
        total_mass=sum(alive)
        if isinstance(policy,str):
            if policy == 'QUERY':
                mins = tuple(min(row[i] for row in m.loss) for i in range(len(m.states)))
                return (total_mass*m.query_cost + sum(b*x for b,x in zip(alive,mins)),
                        sum(alive[i] for i in range(len(alive)) if mins[i]>m.bad_loss_cutoff))
            if policy not in m.repairs: raise ValueError('Unknown repair')
            row=m.loss[m.repairs.index(policy)]
            return (sum(b*x for b,x in zip(alive,row)),
                    sum(alive[i] for i in range(len(alive)) if row[i]>m.bad_loss_cutoff))
        name, routes = policy
        p=next((p for p in m.probes if p.name==name),None)
        if p is None or len(routes)!=len(p.observations): raise ValueError('Incomplete plan')
        value=total_mass*p.cost
        risk=0.
        for j, route in enumerate(routes):
            nxt = [sum(alive[i]*p.kernel[i][j][k] for i in range(len(alive)))
                   for k in range(len(alive))]
            fails=sum(x for k,x in enumerate(nxt) if m.failed_states[k])
            risk += fails
            value += fails*m.failure_cost
            survivors=tuple(x if not m.failed_states[k] else 0. for k,x in enumerate(nxt))
            if sum(survivors)>0:
                child_cost,child_risk=rec(route,survivors)
                value += child_cost
                risk += child_risk
        return value,risk
    return rec(tree,m.initial)

def exhaustive_choice(m: BudgetModel, horizon: int, risk_budget: float) -> float | None:
    validate(m)
    scores=(cost for tree in all_trees(m,horizon)
            for cost,risk in (evaluate_unpruned(m,tree),)
            if risk <= risk_budget + TOL)
    return min(scores,default=None)

def counterexample():
    """Synthetic two-stage information gain with 8% per-probe failure chance."""
    z=(0.,)*5
    kern=(
      ((0.,0.,.92,0.,.08),z,z),
      ((0.,0.,0.,.92,.08),z,z),
      (z,(0.,0.,.92,0.,.08),z),
      (z,z,(0.,0.,0.,.92,.08)),
      ((0.,0.,0.,0.,1.),z,z),
    )
    return BudgetModel(('A0','B0','A1','B1','FAILED'),(.5,.5,0.,0.,0.),
        ('repair_A','repair_B'), ((0.,10.,0.,10.,0.),(10.,0.,10.,0.,0.)),
        4., (Probe('probe',.5,('unknown','a','b'),kern),),
        (False,False,False,False,True), 1.)

if __name__=='__main__':
    import json
    m=counterexample()
    print(json.dumps({str(cap): {'plan':(p.name if p else None),'cost':(p.cost if p else None),
                           'ever_failure_or_wrong_repair':(p.risk if p else None),
                           'unpruned_optimum': exhaustive_choice(m,2,cap)}
                      for cap in (.1,.2,1.) for p in [choose(m,2,cap)]},indent=2))
