"""Finite *dynamic* controller-ACK authority shield, exact model-only minimax.

Key difference from authority_probe_minimax.py: probe actions really transition
hidden states. Repair obligation is evaluated AFTER the probe, not copied from
the pre-probe state. A modeled transition into a forbidden state vetoes a probe.

This is not a new POMDP algorithm or a guarantee for an actual robot: safety,
transition completeness, getter atomicity, and costs are UNVERIFIED inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from typing import Any, Mapping


@dataclass(frozen=True)
class DynamicProbe:
    name: str
    cost: int
    # Per-state complete possible (observed symbol, next hidden state) pairs.
    transitions: Mapping[str, tuple[tuple[str, str], ...]]


@dataclass(frozen=True)
class DynamicContract:
    repair_by_state: Mapping[str, str]
    initial_states: tuple[str, ...]
    forbidden_states: tuple[str, ...]
    probes: tuple[DynamicProbe, ...]
    read_cost: int
    horizon: int


def _validated(m: DynamicContract) -> tuple[str, ...]:
    states = set(m.repair_by_state)
    if not states or any(not isinstance(s, str) or not s or
                         not isinstance(r, str) or not r
                         for s, r in m.repair_by_state.items()):
        raise ValueError("invalid finite state or repair mapping")
    if (type(m.read_cost) is not int or m.read_cost <= 0 or
            type(m.horizon) is not int or m.horizon < 0):
        raise ValueError("read cost must be positive and horizon nonnegative integers")
    init, forbidden = set(m.initial_states), set(m.forbidden_states)
    if (not init or not init <= states or not forbidden <= states or
            init & forbidden or
            len(init) != len(m.initial_states) or
            len(forbidden) != len(m.forbidden_states)):
        raise ValueError("unsafe or incomplete initial/forbidden state registry")
    seen = set()
    for probe in m.probes:
        if not isinstance(probe.name, str) or not probe.name or probe.name in seen:
            raise ValueError("duplicate or invalid probe")
        seen.add(probe.name)
        if type(probe.cost) is not int or probe.cost <= 0:
            raise ValueError("probe action cost must be strictly positive")
        if set(probe.transitions) != states:
            raise ValueError("incomplete state-to-transition semantics")
        for state in states:
            rows = probe.transitions[state]
            if not isinstance(rows, tuple) or not rows or len(set(rows)) != len(rows):
                raise ValueError("empty, duplicate or invalid transition support")
            for item in rows:
                if (not isinstance(item, tuple) or len(item) != 2 or
                        not isinstance(item[0], str) or not item[0] or
                        item[1] not in states):
                    raise ValueError("unknown next hidden state or observation")
    return tuple(sorted(init))


def model_digest(m: DynamicContract) -> str:
    _validated(m)
    doc = {
        "repair_by_state": sorted(m.repair_by_state.items()),
        "initial_states": sorted(m.initial_states),
        "forbidden_states": sorted(m.forbidden_states),
        "read_cost": m.read_cost,
        "horizon": m.horizon,
        "probes": [
            {"name": p.name, "cost": p.cost,
             "transitions": [(s, sorted([list(x) for x in p.transitions[s]]))
                             for s in sorted(m.repair_by_state)]}
            for p in sorted(m.probes, key=lambda p: p.name)
        ],
    }
    return hashlib.sha256(json.dumps(doc, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def successors(m: DynamicContract, p: DynamicProbe,
               belief: tuple[str, ...]) -> dict[str, tuple[str, ...]] | None:
    """None = inadmissible: even one feasible transition reaches forbidden."""
    forbidden = set(m.forbidden_states)
    all_pairs = [pair for s in belief for pair in p.transitions[s]]
    if any(nxt in forbidden for _, nxt in all_pairs):
        return None
    observations = sorted({obs for obs, _ in all_pairs})
    return {o: tuple(sorted({nxt for obs, nxt in all_pairs if obs == o}))
            for o in observations}


def synthesize(m: DynamicContract) -> dict[str, Any]:
    init = _validated(m)
    @lru_cache(maxsize=None)
    def opt(belief: tuple[str, ...], h: int) -> tuple[int, dict[str, Any]]:
        repairs = {m.repair_by_state[s] for s in belief}
        if len(repairs) == 1:
            repair = next(iter(repairs))
            return 0, {"kind": "authorize", "repair": repair,
                       "belief": list(belief), "remaining_cost": 0}
        cost = m.read_cost
        selected: dict[str, Any] = {
            "kind": "read", "belief": list(belief), "remaining_cost": cost
        }
        if h:
            for p in sorted(m.probes, key=lambda p: p.name):
                if p.cost >= cost:
                    continue
                next_b = successors(m, p, belief)
                if next_b is None:
                    continue
                branches = {obs: opt(b, h - 1) for obs, b in next_b.items()}
                candidate = p.cost + max(v for v, _ in branches.values())
                if candidate < cost:
                    cost = candidate
                    selected = {
                        "kind": "probe", "probe": p.name, "belief": list(belief),
                        "branches": {obs: decision for obs, (_, decision) in branches.items()},
                        "remaining_cost": cost,
                    }
        return cost, selected

    cost, root = opt(init, m.horizon)
    certificate = {
        "schema": "dynamic_controller_authority_minimax_v1",
        "model_sha256": model_digest(m),
        "model_only": True,
        "worst_abstract_cost": cost,
        "root": root,
        "limitations": [
            "unverified_physical_transition_completeness",
            "unverified_real_actuation_cost",
            "unverified_atomic_authoritative_read",
            "unverified_robot_contact_safety",
            "no_general_pomdp_novelty_claim",
            "no_independent_adoption",
        ],
    }
    check(m, certificate)
    return certificate


def check(m: DynamicContract, certificate: Mapping[str, Any]) -> dict[str, int | bool]:
    """Separate structural/authority checker, not planner-dependent."""
    initial = _validated(m)
    if (certificate.get("schema") != "dynamic_controller_authority_minimax_v1" or
            certificate.get("model_sha256") != model_digest(m)):
        raise ValueError("wrong or stale model identity")
    probes = {p.name: p for p in m.probes}
    counters = {"read_leaves": 0, "authorized_leaves": 0,
                "checked_probe_branches": 0, "vetoed_unsafe_probes_in_model": 0}

    def verify(node: Mapping[str, Any], belief: tuple[str, ...], h: int) -> int:
        if not isinstance(node, Mapping) or node.get("belief") != list(belief):
            raise ValueError("incorrect dynamic posterior / belief")
        if set(belief) & set(m.forbidden_states):
            raise ValueError("forbidden state reachable in decision certificate")
        kind = node.get("kind")
        if kind == "read":
            counters["read_leaves"] += 1
            value = m.read_cost
        elif kind == "authorize":
            if (not isinstance(node.get("repair"), str) or
                    any(m.repair_by_state[s] != node["repair"] for s in belief)):
                raise ValueError("wrong repair authorization after physical transition")
            counters["authorized_leaves"] += 1
            value = 0
        elif kind == "probe":
            if h == 0:
                raise ValueError("probe depth budget exceeded")
            p = probes.get(node.get("probe"))
            if p is None:
                raise ValueError("unknown probe")
            next_b = successors(m, p, belief)
            if next_b is None:
                raise ValueError("unsafe probe can change latent state into forbidden")
            choices = node.get("branches")
            if not isinstance(choices, dict) or set(choices) != set(next_b):
                raise ValueError("missing modeled response/hidden transition")
            child_cost = []
            for obs, b in next_b.items():
                child_cost.append(verify(choices[obs], b, h - 1))
                counters["checked_probe_branches"] += 1
            value = p.cost + max(child_cost)
        else:
            raise ValueError("unknown node type")
        if type(node.get("remaining_cost")) is not int or node["remaining_cost"] != value:
            raise ValueError("falsified cumulative worst cost")
        return value

    value = verify(certificate["root"], initial, m.horizon)
    if (type(certificate.get("worst_abstract_cost")) is not int or
            certificate["worst_abstract_cost"] != value):
        raise ValueError("invalid certificate root worst-case bound")
    return {"checked_initial_states": len(initial), "model_only": True,
            "worst_abstract_cost": value, **counters}


def brute_force_value(m: DynamicContract) -> int:
    """Independent uncached optimality oracle for small finite-model tests."""
    initial = _validated(m)
    def walk(belief: tuple[str, ...], h: int) -> int:
        if len({m.repair_by_state[s] for s in belief}) == 1:
            return 0
        cost = m.read_cost
        if h:
            for p in m.probes:
                branches = successors(m, p, belief)
                if branches is not None:
                    cost = min(cost, p.cost + max(walk(b, h - 1)
                                                   for b in branches.values()))
        return cost
    return walk(initial, m.horizon)


def next_request(m: DynamicContract, cert: Mapping[str, Any],
                 prior_public_symbols: tuple[str, ...]) -> dict[str, Any]:
    """Model-gated executor request ONLY. Unknown symbol => conservative read."""
    check(m, cert)
    if (not isinstance(prior_public_symbols, tuple) or any(
            not isinstance(s, str) or not s for s in prior_public_symbols)):
        raise ValueError("invalid public trace")
    node = cert["root"]
    spent = 0
    for symbol in prior_public_symbols:
        if node["kind"] != "probe":
            raise ValueError("extra observation after terminal decision")
        spent += next(p.cost for p in m.probes if p.name == node["probe"])
        if symbol not in node["branches"]:
            return {"request": "read", "reason": "out_of_model_observation",
                    "model_bound_valid_for_trace": False,
                    "already_spent_cost": spent, "additional_read_cost": m.read_cost}
        node = node["branches"][symbol]
    if node["kind"] == "probe":
        return {"request": "probe", "probe": node["probe"], "already_spent_cost": spent,
                "model_bound_valid_for_trace": True}
    if node["kind"] == "authorize":
        return {"request": "authorize", "repair": node["repair"],
                "already_spent_cost": spent, "model_bound_valid_for_trace": True}
    return {"request": "read", "reason": "remaining_belief_ambiguity",
            "already_spent_cost": spent, "model_bound_valid_for_trace": True}


def cases() -> dict[str, DynamicContract]:
    """Explicitly SYNTHETIC counterexamples and control cases."""
    shifting = DynamicContract(
        {"delivered": "CONTINUE", "held": "REINITIALIZE",
         "post_probe": "REINITIALIZE"},
        ("delivered", "held"), (),
        (DynamicProbe("diagnostic_move", 1, {
            "delivered": (("ack", "post_probe"),),
            "held": (("no_ack", "held"),),
            "post_probe": (("ack", "post_probe"),),
        }),), 5, 1
    )
    dangerous = DynamicContract(
        {"delivered": "CONTINUE", "held": "REINITIALIZE",
         "contact": "HALT"},
        ("delivered", "held"), ("contact",),
        (DynamicProbe("apparently_informative_but_contact_unsafe", 1, {
            "delivered": (("ack", "delivered"), ("touch", "contact")),
            "held": (("no_ack", "held"),),
            "contact": (("touch", "contact"),),
        }),), 5, 1
    )
    unrevealing = DynamicContract(
        {"delivered": "CONTINUE", "held": "REINITIALIZE"},
        ("delivered", "held"), (),
        (DynamicProbe("nonzero_but_not_informative", 2, {
            "delivered": (("same", "delivered"),),
            "held": (("same", "held"),),
        }),), 5, 2
    )
    return {"shifting_repair": shifting, "unsafe_probe_veto": dangerous,
            "costly_uninformative_probe": unrevealing}


if __name__ == "__main__":
    from pprint import pprint
    for name, model in cases().items():
        certificate = synthesize(model)
        pprint({"synthetic_only": True, "name": name,
                "certificate": certificate, "independent_check": check(model, certificate)})
