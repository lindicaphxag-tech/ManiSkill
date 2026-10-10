"""Finite one-step exact decision oracle for hidden-controller repair.

This is a SYNTHETIC strong comparator. It is neither a new POMDP theorem
nor robot safety evidence. A probe is assumed to reveal observations without
changing state, action losses, or the subsequent controller dynamics.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import isclose, isfinite, log2
from typing import Optional

EPS = 1e-12

@dataclass(frozen=True)
class Probe:
    name: str
    cost: float
    outcomes: tuple[str, ...]
    likelihood: tuple[tuple[float, ...], ...]

@dataclass(frozen=True)
class Model:
    states: tuple[str, ...]
    prior: tuple[float, ...]
    actions: tuple[str, ...]
    action_loss: tuple[tuple[float, ...], ...]
    query_cost: float
    probes: tuple[Probe, ...] = ()
    risk_cap: Optional[float] = None
    bad_loss_cutoff: float = 0.0

@dataclass(frozen=True)
class Decision:
    kind: str
    action: Optional[str]
    conditional_expected_loss: float
    conditional_bad_probability: float

@dataclass(frozen=True)
class Plan:
    name: str
    expected_total_loss: float
    decisions: tuple[tuple[str, Decision], ...]
    information_gain_bits: float
    measurement_cost: float

def _probabilities(p, *, tag):
    if not p or any(not isfinite(x) or x < 0 for x in p) or not isclose(
        sum(p), 1.0, rel_tol=0, abs_tol=1e-10
    ):
        raise ValueError(f"Invalid normalized probabilities: {tag}")

def validate(model: Model) -> None:
    n = len(model.states)
    if not n or len(set(model.states)) != n:
        raise ValueError("States must be nonempty and unique")
    _probabilities(model.prior, tag="prior")
    if len(model.prior) != n:
        raise ValueError("Prior length mismatch")
    if not model.actions or len(set(model.actions)) != len(model.actions):
        raise ValueError("Actions must be unique")
    if len(model.actions) != len(model.action_loss):
        raise ValueError("Action/loss count mismatch")
    if any(len(row) != n or any(not isfinite(x) or x < 0 for x in row)
           for row in model.action_loss):
        raise ValueError("Action losses must be finite and nonnegative")
    if not isfinite(model.query_cost) or model.query_cost < 0:
        raise ValueError("Invalid query cost")
    if model.risk_cap is not None and not 0 <= model.risk_cap <= 1:
        raise ValueError("Invalid risk cap")
    if not isfinite(model.bad_loss_cutoff):
        raise ValueError("Invalid loss cutoff")
    names = set()
    for p in model.probes:
        if not p.name or p.name == "none" or p.name in names:
            raise ValueError("Invalid or repeated probe name")
        names.add(p.name)
        if not isfinite(p.cost) or p.cost < 0 or not p.outcomes or len(set(p.outcomes)) != len(p.outcomes):
            raise ValueError("Invalid probe costs/outcomes")
        if len(p.likelihood) != n:
            raise ValueError("Likelihood must have one row per state")
        for row in p.likelihood:
            if len(row) != len(p.outcomes):
                raise ValueError("Likelihood outcome length mismatch")
            _probabilities(row, tag=p.name)

def _optimal_continuation(model: Model, posterior: tuple[float, ...]) -> Decision:
    known_state_optimal = sum(prob * min(row[h] for row in model.action_loss)
                              for h, prob in enumerate(posterior))
    best = Decision("query", None, model.query_cost + known_state_optimal, 0.0)
    for name, losses in zip(model.actions, model.action_loss):
        err = sum(prob for prob, loss in zip(posterior, losses)
                  if loss > model.bad_loss_cutoff)
        if model.risk_cap is not None and err > model.risk_cap + EPS:
            continue
        value = sum(prob * loss for prob, loss in zip(posterior, losses))
        if value < best.conditional_expected_loss - EPS:
            best = Decision("action", name, value, err)
    return best

def _entropy(p):
    return -sum(v * log2(v) for v in p if v > 0)

def one_step_plan(model: Model, probe: Optional[Probe] = None) -> Plan:
    validate(model)
    if probe is None:
        d = _optimal_continuation(model, model.prior)
        return Plan("none", d.conditional_expected_loss, (("no_observation", d),), 0.0, 0.0)
    if probe not in model.probes:
        raise ValueError("Probe is not a frozen candidate")
    decisions = []
    value = probe.cost
    post_entropy = 0.0
    for j, obs in enumerate(probe.outcomes):
        joint = tuple(model.prior[i] * probe.likelihood[i][j]
                      for i in range(len(model.states)))
        mass = sum(joint)
        if mass == 0:
            continue
        posterior = tuple(v / mass for v in joint)
        d = _optimal_continuation(model, posterior)
        value += mass * d.conditional_expected_loss
        post_entropy += mass * _entropy(posterior)
        decisions.append((obs, d))
    return Plan(probe.name, value, tuple(decisions),
                max(0., _entropy(model.prior) - post_entropy), probe.cost)

def select_plan(model: Model) -> Plan:
    choices = (one_step_plan(model),) + tuple(one_step_plan(model, p)
                                            for p in model.probes)
    return min(choices, key=lambda x: (x.expected_total_loss, x.measurement_cost, x.name))

def entropy_heuristic(model: Model) -> Plan:
    candidates = (one_step_plan(model, p) for p in model.probes)
    return max(candidates, key=lambda x: (x.information_gain_bits, -x.measurement_cost),
               default=one_step_plan(model))

def brute_policy_cost(model: Model, probe: Optional[Probe]) -> float:
    """Independent exhaustive enumeration of observation-contingent policies."""
    validate(model)
    if probe is None:
        return _optimal_continuation(model, model.prior).conditional_expected_loss
    best = float("inf")
    for rule in product(range(len(model.actions) + 1), repeat=len(probe.outcomes)):
        total = probe.cost
        for j, action_idx in enumerate(rule):
            joint = [model.prior[i] * probe.likelihood[i][j]
                     for i in range(len(model.states))]
            mass = sum(joint)
            if mass <= 0:
                continue
            if action_idx == len(model.actions):
                total += mass * model.query_cost
                total += sum(joint[h] * min(row[h] for row in model.action_loss)
                             for h in range(len(model.states)))
            else:
                losses = model.action_loss[action_idx]
                err = sum(joint[h] for h in range(len(model.states))
                          if losses[h] > model.bad_loss_cutoff) / mass
                if model.risk_cap is not None and err > model.risk_cap + EPS:
                    total = float("inf")
                    break
                total += sum(joint[h] * losses[h]
                             for h in range(len(model.states)))
        best = min(best, total)
    return best

def quotient_model(model: Model) -> Model:
    """Merge EXACTLY equal action-loss and probe-likelihood signatures only."""
    validate(model)
    signatures = {}
    groups = []
    for h in range(len(model.states)):
        signature = (tuple(row[h] for row in model.action_loss),
                     tuple(p.likelihood[h] for p in model.probes))
        if signature not in signatures:
            signatures[signature] = len(groups)
            groups.append([])
        groups[signatures[signature]].append(h)
    return Model(
        tuple("{" + ",".join(model.states[h] for h in group) + "}" for group in groups),
        tuple(sum(model.prior[h] for h in group) for group in groups),
        model.actions,
        tuple(tuple(row[group[0]] for group in groups) for row in model.action_loss),
        model.query_cost,
        tuple(Probe(p.name, p.cost, p.outcomes,
                    tuple(p.likelihood[group[0]] for group in groups))
              for p in model.probes),
        model.risk_cap,
        model.bad_loss_cutoff,
    )

def authority_counterexample(*, risk_cap: Optional[float] = 1.0) -> Model:
    """Constructed 8-state diagnostic, NOT a measured robotics outcome."""
    nuisance = Probe(
        "identity_within_group", .2, tuple(f"n{i}" for i in range(4)),
        tuple(tuple(float(i % 4 == j) for j in range(4)) for i in range(8)),
    )
    relevant = Probe(
        "repair_group", .2, ("low", "high"),
        tuple((1., 0.) if i < 4 else (0., 1.) for i in range(8)),
    )
    return Model(
        tuple(f"h{i}" for i in range(8)), (1/8,) * 8,
        ("repair_low", "repair_high"),
        ((0.,) * 4 + (10.,) * 4, (10.,) * 4 + (0.,) * 4),
        2., (nuisance, relevant), risk_cap,
    )

if __name__ == "__main__":
    import json
    from dataclasses import asdict
    m = authority_counterexample()
    print(json.dumps({
        "kind": "CONSTRUCTED_SYNTHETIC_NOT_PHYSX",
        "optimal": asdict(select_plan(m)),
        "entropy": asdict(entropy_heuristic(m)),
        "no_probe": asdict(one_step_plan(m)),
        "exhaustive_oracle_agreement": all(abs(one_step_plan(m, p).expected_total_loss -
                                               brute_policy_cost(m, p)) < 1e-9
                                          for p in m.probes),
    }, indent=2))
