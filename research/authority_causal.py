"""Exact finite action-conditioned recovery oracle; synthetic reference only.

A probe changes *both* public observation and latent controller state. This is
a standard small POMDP reference, not a new planning theorem, calibrated native
transition model, distribution-free bound, or real robot safety certificate.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import inf, isclose, isfinite

EPS = 1e-10

@dataclass(frozen=True)
class Probe:
    name: str
    cost: float
    outcomes: tuple[str, ...]
    kernel: tuple[tuple[tuple[float, ...], ...], ...]  # [old][obs][new]

@dataclass(frozen=True)
class Model:
    states: tuple[str, ...]
    prior: tuple[float, ...]
    repairs: tuple[str, ...]
    losses: tuple[tuple[float, ...], ...]  # [repair][hidden state]
    query_cost: float
    probes: tuple[Probe, ...]
    risk_cap: float | None = None  # model-conditional chance of bad repair
    bad_cutoff: float = 0.0
    probe_failure_cap: float | None = None  # one-step cap, NOT trajectory risk
    failures: tuple[bool, ...] = ()

@dataclass(frozen=True)
class Plan:
    kind: str
    name: str
    value: float
    branches: tuple[tuple[str, 'Plan'], ...] = ()

def _isprob(xs):
    return (all(isfinite(x) and x >= 0 for x in xs)
            and isclose(sum(xs), 1., abs_tol=EPS, rel_tol=0.))

def validate(m):
    n = len(m.states)
    if not n or len(set(m.states)) != n or len(m.prior) != n or not _isprob(m.prior):
        raise ValueError("Non-unique states or invalid prior")
    if not m.repairs or len(set(m.repairs)) != len(m.repairs) or len(m.repairs) != len(m.losses):
        raise ValueError("Invalid repairs")
    if any(len(row) != n or any(not isfinite(v) or v < 0 for v in row) for row in m.losses):
        raise ValueError("Invalid loss matrix")
    if not isfinite(m.query_cost) or m.query_cost < 0 or not isfinite(m.bad_cutoff):
        raise ValueError("Invalid native query / loss")
    for cap in (m.risk_cap, m.probe_failure_cap):
        if cap is not None and (not isfinite(cap) or not 0 <= cap <= 1):
            raise ValueError("Invalid chance constraint")
    if m.failures and (len(m.failures) != n or any(type(x) is not bool for x in m.failures)):
        raise ValueError("Invalid failure markers")
    seen = set()
    for p in m.probes:
        if not p.name or p.name == "QUERY" or p.name in seen or p.name in m.repairs:
            raise ValueError("Invalid probe name")
        seen.add(p.name)
        if not isfinite(p.cost) or p.cost < 0 or not p.outcomes or len(set(p.outcomes)) != len(p.outcomes):
            raise ValueError("Invalid probe outcomes/cost")
        if len(p.kernel) != n:
            raise ValueError("Missing old-state transition row")
        for row in p.kernel:
            if len(row) != len(p.outcomes) or any(len(y) != n for y in row):
                raise ValueError("Invalid joint transition dimensions")
            if not _isprob(tuple(v for y in row for v in y)):
                raise ValueError("Invalid joint observation/transition mass")

def next_beliefs(m, p, prior):
    for j, label in enumerate(p.outcomes):
        joint = tuple(sum(prior[i] * p.kernel[i][j][k] for i in range(len(prior)))
                      for k in range(len(prior)))
        probability = sum(joint)
        if probability > 0:
            yield (label, probability, tuple(v / probability for v in joint))

def hazard(m, p, prior):
    flags = m.failures or (False,) * len(m.states)
    return sum(prior[i] * p.kernel[i][j][k]
               for i in range(len(prior))
               for j in range(len(p.outcomes))
               for k in range(len(prior)) if flags[k])

def terminal(m, prior):
    known = sum(prior[i] * min(row[i] for row in m.losses)
                for i in range(len(prior)))
    yield Plan("query", "QUERY", m.query_cost + known)
    for name, losses in zip(m.repairs, m.losses):
        bad = sum(prior[i] for i, loss in enumerate(losses) if loss > m.bad_cutoff)
        if m.risk_cap is None or bad <= m.risk_cap + EPS:
            yield Plan("repair", name, sum(prior[i] * losses[i] for i in range(len(prior))))

def solve(m, horizon, belief=None):
    validate(m)
    if type(horizon) is not int or horizon < 0:
        raise ValueError("Invalid finite horizon")
    b = m.prior if belief is None else tuple(belief)
    if len(b) != len(m.states) or not _isprob(b):
        raise ValueError("Invalid posterior")
    def dp(prior, steps):
        choices = list(terminal(m, prior))
        if steps > 0:
            for p in m.probes:
                if m.probe_failure_cap is not None and hazard(m, p, prior) > m.probe_failure_cap + EPS:
                    continue
                children = tuple((o, mass, dp(after, steps-1))
                                 for o, mass, after in next_beliefs(m, p, prior))
                val = p.cost + sum(mass * child.value for _, mass, child in children)
                choices.append(Plan("probe", p.name, val,
                                    tuple((o, child) for o, _, child in children)))
        return min(choices, key=lambda c: (c.value, c.kind == "probe", c.name))
    return dp(b, horizon)

def all_policy_trees(m, horizon):
    """Independent exhaustive observable policy-tree enumeration for tiny cases."""
    if type(horizon) is not int or horizon < 0:
        raise ValueError("Invalid horizon")
    yield from m.repairs + ("QUERY",)
    if horizon:
        leaves = tuple(all_policy_trees(m, horizon - 1))
        for p in m.probes:
            for paths in product(leaves, repeat=len(p.outcomes)):
                yield (p.name, paths)

def evaluate_tree(m, tree, belief=None):
    validate(m)
    b = m.prior if belief is None else tuple(belief)
    if isinstance(tree, str):
        if tree == "QUERY":
            return m.query_cost + sum(b[i] * min(row[i] for row in m.losses)
                                      for i in range(len(b)))
        if tree not in m.repairs:
            raise ValueError("Unknown repair")
        losses = m.losses[m.repairs.index(tree)]
        bad = sum(b[i] for i, loss in enumerate(losses) if loss > m.bad_cutoff)
        if m.risk_cap is not None and bad > m.risk_cap + EPS:
            return inf
        return sum(b[i] * losses[i] for i in range(len(b)))
    if not isinstance(tree, tuple) or len(tree) != 2:
        raise ValueError("Malformed contingent policy")
    name, paths = tree
    p = next((p for p in m.probes if p.name == name), None)
    if p is None or len(paths) != len(p.outcomes):
        raise ValueError("Unregistered/incomplete probe")
    if m.probe_failure_cap is not None and hazard(m, p, b) > m.probe_failure_cap + EPS:
        return inf
    outcome = {o: (mass, after) for o, mass, after in next_beliefs(m, p, b)}
    return p.cost + sum(outcome[o][0] * evaluate_tree(m, path, outcome[o][1])
                        for o, path in zip(p.outcomes, paths) if o in outcome)

def brute_best(m, horizon):
    validate(m)
    return min(evaluate_tree(m, tree) for tree in all_policy_trees(m, horizon))

def exact_bisimulation_quotient(m):
    """Standard exact partition refinement by terminal loss and joint transitions."""
    validate(m)
    n = len(m.states)
    flags = m.failures or (False,) * n
    labels = [(tuple(loss[i] for loss in m.losses), flags[i]) for i in range(n)]
    def group_signatures(sigs):
        by, groups = {}, []
        for i, sig in enumerate(sigs):
            if sig not in by:
                by[sig] = len(groups)
                groups.append([])
            groups[by[sig]].append(i)
        return tuple(tuple(g) for g in groups)
    groups = group_signatures(labels)
    while True:
        owner = {s: g for g, group in enumerate(groups) for s in group}
        sigs = [(owner[s], labels[s], tuple(
                    tuple(tuple(sum(p.kernel[s][j][next_s] for next_s in group)
                                for group in groups)
                          for j in range(len(p.outcomes)))
                    for p in m.probes))
                for s in range(n)]
        new = group_signatures(sigs)
        if new == groups:
            break
        groups = new
    reduced = tuple(Probe(p.name, p.cost, p.outcomes,
        tuple(tuple(tuple(sum(p.kernel[g[0]][j][dest] for dest in group)
                          for group in groups)
                    for j in range(len(p.outcomes)))
              for g in groups)) for p in m.probes)
    return Model(tuple("{" + ",".join(m.states[s] for s in g) + "}" for g in groups),
                 tuple(sum(m.prior[s] for s in g) for g in groups),
                 m.repairs, tuple(tuple(row[g[0]] for g in groups) for row in m.losses),
                 m.query_cost, reduced, m.risk_cap, m.bad_cutoff,
                 m.probe_failure_cap, tuple(flags[g[0]] for g in groups))

def counterexample():
    # Probe observation describes OLD target; the probe rewrites NEW target to b.
    p = Probe("reset_and_watch", .1, ("old_a", "old_b"),
              (((0., 1.), (0., 0.)), ((0., 0.), (0., 1.))))
    return Model(("a", "b"), (.5, .5), ("repair_a", "repair_b"),
                 ((0., 10.), (10., 0.)), 2., (p,))

if __name__ == "__main__":
    import json
    m = counterexample()
    opt = solve(m, 1)
    print(json.dumps({"scope":"SYNTHETIC_NOT_PHYSX", "name":opt.name,
                      "value":opt.value, "branches":[(o,child.name) for o,child in opt.branches],
                      "exhaustive_value":brute_best(m,1)}, indent=2))
