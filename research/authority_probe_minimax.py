"""Finite, authority-aware minimax probe synthesis with independently checked plans.

This is a MODEL-ONLY certificate, not a safety guarantee for an actual robot.
Assumptions: static hidden history, complete response supports, and known
repair-preserving probe semantics. Costs are abstract integer units.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping


@dataclass(frozen=True)
class Probe:
    name: str
    cost: int
    support_by_history: Mapping[str, tuple[str, ...]]
    preserves_repair: bool = True


@dataclass(frozen=True)
class Model:
    repair_by_history: Mapping[str, str]
    probes: tuple[Probe, ...]
    authoritative_read_cost: int
    max_probe_depth: int


def validate_model(model: Model) -> tuple[str, ...]:
    if (type(model.authoritative_read_cost) is not int
            or model.authoritative_read_cost <= 0):
        raise ValueError("read cost must be a positive integer")
    if type(model.max_probe_depth) is not int or model.max_probe_depth < 0:
        raise ValueError("negative or noninteger probe depth")
    if not model.repair_by_history:
        raise ValueError("no hidden histories")
    if any(not isinstance(k, str) or not k or not isinstance(v, str) or not v
           for k, v in model.repair_by_history.items()):
        raise ValueError("history and repair identifiers must be nonempty strings")
    histories = tuple(sorted(model.repair_by_history))
    seen: set[str] = set()
    for probe in model.probes:
        if not probe.name or probe.name in seen:
            raise ValueError("duplicate or empty probe")
        seen.add(probe.name)
        if type(probe.cost) is not int or probe.cost <= 0:
            raise ValueError("probe cost must be a positive integer")
        if probe.preserves_repair is not True:
            raise ValueError("unverified repair invariance")
        if set(probe.support_by_history) != set(histories):
            raise ValueError("missing history in response support")
        for history in histories:
            outcomes = probe.support_by_history[history]
            if (not isinstance(outcomes, tuple) or not outcomes
                    or len(set(outcomes)) != len(outcomes)
                    or any(not isinstance(x, str) or not x for x in outcomes)):
                raise ValueError("invalid complete possible observation set")
    return histories


def possible_posteriors(probe: Probe, belief: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    all_symbols = sorted({o for h in belief for o in probe.support_by_history[h]})
    return {o: tuple(h for h in belief if o in probe.support_by_history[h])
            for o in all_symbols}


def synthesize(model: Model) -> dict[str, Any]:
    """Exact minimum WORST-CASE abstract cost. Ties favor the authoritative read."""
    histories = validate_model(model)
    probes = sorted(model.probes, key=lambda x: x.name)

    @lru_cache(None)
    def go(belief: tuple[str, ...], depth: int) -> tuple[int, dict[str, Any]]:
        repairs = {model.repair_by_history[h] for h in belief}
        if len(repairs) == 1:
            return 0, {"kind": "authorize", "repair": next(iter(repairs)),
                       "belief": list(belief), "worst_remaining_cost": 0}
        best_cost = model.authoritative_read_cost
        best: dict[str, Any] = {
            "kind": "read", "belief": list(belief), "worst_remaining_cost": best_cost
        }
        if depth:
            for probe in probes:
                if probe.cost >= best_cost:
                    continue
                children = {}
                worst_child = 0
                for outcome, next_belief in possible_posteriors(probe, belief).items():
                    cost, subtree = go(next_belief, depth - 1)
                    worst_child = max(worst_child, cost)
                    children[outcome] = subtree
                total = probe.cost + worst_child
                if total < best_cost:
                    best_cost = total
                    best = {"kind": "probe", "probe": probe.name,
                            "belief": list(belief), "branches": children,
                            "worst_remaining_cost": total}
        return best_cost, best

    value, tree = go(histories, model.max_probe_depth)
    certificate = {
        "schema": "authority_aware_exact_minimax_v1",
        "semantics": "finite_static_histories_complete_adversarial_support",
        "read_cost_units": model.authoritative_read_cost,
        "depth_budget": model.max_probe_depth,
        "worst_cost_units": value,
        "root": tree,
        "not_claimed": ["real_robot_safety", "real_energy_cost", "true_response_calibration",
                        "novel_POMDP_algorithm", "third_party_adoption"],
    }
    certify(model, certificate)
    return certificate


def certify(model: Model, certificate: Mapping[str, Any]) -> dict[str, int | bool]:
    """Separate exhaustive verifier; never calls synthesizer or its optimizer."""
    histories = validate_model(model)
    lookup = {p.name: p for p in model.probes}
    if certificate.get("schema") != "authority_aware_exact_minimax_v1":
        raise ValueError("wrong certificate schema")
    if (certificate.get("read_cost_units") != model.authoritative_read_cost
            or certificate.get("depth_budget") != model.max_probe_depth):
        raise ValueError("wrong certificate provenance")
    counts = {"leaf_world_traces": 0, "authorized_leaf_world_traces": 0,
              "read_leaf_world_traces": 0}

    def walk(node: Mapping[str, Any], belief: tuple[str, ...], remaining: int) -> int:
        if node.get("belief") != list(belief):
            raise ValueError("incorrect posterior belief")
        kind = node.get("kind")
        if kind == "authorize":
            if any(model.repair_by_history[h] != node.get("repair") for h in belief):
                raise ValueError("wrong authority: distinct valid repair exists")
            cost = 0
            counts["authorized_leaf_world_traces"] += len(belief)
            counts["leaf_world_traces"] += len(belief)
        elif kind == "read":
            cost = model.authoritative_read_cost
            counts["read_leaf_world_traces"] += len(belief)
            counts["leaf_world_traces"] += len(belief)
        elif kind == "probe":
            if remaining == 0:
                raise ValueError("exceeds depth")
            probe = lookup.get(node.get("probe"))
            if probe is None:
                raise ValueError("unknown probe")
            post = possible_posteriors(probe, belief)
            branches = node.get("branches")
            if not isinstance(branches, dict) or set(branches) != set(post):
                raise ValueError("missing or fabricated observation branch")
            cost = probe.cost + max(walk(branches[o], b, remaining - 1)
                                    for o, b in post.items())
        else:
            raise ValueError("unknown decision kind")
        if type(node.get("worst_remaining_cost")) is not int or node["worst_remaining_cost"] != cost:
            raise ValueError("falsified worst-case cost")
        return cost

    derived = walk(certificate["root"], histories, model.max_probe_depth)
    if type(certificate.get("worst_cost_units")) is not int or certificate["worst_cost_units"] != derived:
        raise ValueError("root bound falsified")
    return {"checked_histories": len(histories), "worst_cost_units": derived,
            **counts, "model_only": True}


def brute_force_minimax_value(model: Model) -> int:
    """Uncached exhaustive oracle for small tests, independent of the planner."""
    histories = validate_model(model)
    def brute(belief: tuple[str, ...], depth: int) -> int:
        if len({model.repair_by_history[h] for h in belief}) == 1:
            return 0
        best = model.authoritative_read_cost
        if depth:
            for probe in model.probes:
                next_beliefs = possible_posteriors(probe, belief).values()
                best = min(best, probe.cost + max(brute(n, depth - 1) for n in next_beliefs))
        return best
    return brute(histories, model.max_probe_depth)


def showcase() -> dict[str, Any]:
    """Three SYNTHETIC examples, not PhysX performance evidence."""
    histories = ("H1", "H2", "H3", "H4")
    same = Model({h: "SAME_REPAIR" for h in histories}, (), 5, 2)
    distinct = {h: "ACTION_" + h for h in histories}
    cheap = Probe("cheap", 1, {"H1": ("left",), "H2": ("left",),
                               "H3": ("right",), "H4": ("right",)})
    exact = Probe("exact", 3, {h: (h,) for h in histories})
    ambiguous = Model(
        {"applied": "CONTINUE", "held": "REINITIALIZE"},
        (Probe("nonzero", 2, {"applied": ("ambiguous",),
                             "held": ("ambiguous",)}),), 5, 3
    )
    return {"synthetic_only": True, "examples": {
        "repair_quotient": synthesize(same),
        "globally_cheapest_probe": synthesize(Model(distinct, (cheap, exact), 5, 2)),
        "uninformative_actuation": synthesize(ambiguous),
    }}


if __name__ == "__main__":
    import json
    print(json.dumps(showcase(), sort_keys=True, indent=2))
