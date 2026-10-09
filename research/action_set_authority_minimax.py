"""Finite worst-case probing over INTERSECTIONS of valid concrete actions.

This is a novel representational adapter within the local project only, NOT
a newly invented AND/OR decision-tree algorithm nor real robot/VLA safety.
Only use valid_by_history if an independently verified controller certifier
provides COMPLETE legitimate concrete actions per hidden history. Probe
supports are complete and the underlying valid-action sets remain invariant.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from typing import Mapping, Any


@dataclass(frozen=True)
class ActionProbe:
    name: str
    cost: int
    support_by_history: Mapping[str, tuple[str,...]]
    preserves_action_sets: bool = True


@dataclass(frozen=True)
class ActionSetModel:
    valid_by_history: Mapping[str,tuple[str,...]]
    probes: tuple[ActionProbe,...]
    read_cost: int
    max_depth: int


def validate(m:ActionSetModel):
    if type(m.read_cost) is not int or m.read_cost<=0 or type(m.max_depth) is not int or m.max_depth<0:
        raise ValueError("positive integer read cost and nonnegative probe budget needed")
    if not m.valid_by_history:
        raise ValueError("missing hidden histories")
    states=tuple(sorted(m.valid_by_history))
    if any(not isinstance(h,str) or not h or
           not isinstance(acts,tuple) or not acts or
           len(set(acts))!=len(acts) or
           any(not isinstance(a,str) or not a for a in acts)
           for h,acts in m.valid_by_history.items()):
        raise ValueError("each state needs a nonempty finite unique concrete action set")
    names=set()
    for p in m.probes:
        if not p.name or p.name in names or type(p.cost) is not int or p.cost<=0:
            raise ValueError("invalid or duplicate probe/cost")
        names.add(p.name)
        if p.preserves_action_sets is not True:
            raise ValueError("unverified probe preserves every history's valid commands")
        if set(p.support_by_history)!=set(states):
            raise ValueError("missing history public response support")
        for h in states:
            x=p.support_by_history[h]
            if not isinstance(x,tuple) or not x or len(set(x))!=len(x) or any(
                    not isinstance(v,str) or not v for v in x):
                raise ValueError("incomplete or invalid response support")
    return states


def common(m,belief):
    sets=[set(m.valid_by_history[h]) for h in belief]
    return sorted(set.intersection(*sets))


def post(p,belief):
    obs=sorted({outcome for h in belief for outcome in p.support_by_history[h]})
    return {o:tuple(h for h in belief if o in p.support_by_history[h]) for o in obs}


def plan(m):
    states=validate(m)
    probes=sorted(m.probes,key=lambda p:p.name)

    @lru_cache(None)
    def go(belief,depth):
        acts=common(m,belief)
        if acts:
            return 0,{"kind":"authorize","action":acts[0],
                      "belief":list(belief),"worst_remaining_cost":0}
        best=m.read_cost
        tree={"kind":"read","belief":list(belief),"worst_remaining_cost":best}
        if depth:
            for p in probes:
                if p.cost>=best:continue
                branches={}
                worst=0
                for signal,new_belief in post(p,belief).items():
                    v,child=go(new_belief,depth-1)
                    worst=max(worst,v)
                    branches[signal]=child
                cost=p.cost+worst
                if cost<best:
                    best=cost
                    tree={"kind":"probe","probe":p.name,"belief":list(belief),
                          "branches":branches,"worst_remaining_cost":cost}
        return best,tree

    cost,root=go(states,m.max_depth)
    cert={"schema":"finite_common_action_minimax_v1",
          "root":root,"worst_cost":cost,
          "read_cost":m.read_cost,"max_depth":m.max_depth,
          "not_claimed":["real_robot_safety","known_real_response_support",
                         "novel_POMDP_optimization","physical_task_gain"]}
    verify(m,cert)
    return cert


def verify(m,cert):
    """Independent DFS checker, no call to plan() or its optimizer."""
    states=validate(m)
    lookup={p.name:p for p in m.probes}
    if (cert.get("schema")!="finite_common_action_minimax_v1"
            or cert.get("read_cost")!=m.read_cost
            or cert.get("max_depth")!=m.max_depth):
        raise ValueError("wrong finite action-set certificate provenance")

    def walk(node,belief,depth):
        if node.get("belief")!=list(belief):
            raise ValueError("false surviving history set")
        kind=node.get("kind")
        if kind=="authorize":
            action=node.get("action")
            if action not in common(m,belief):
                raise ValueError("false authority: action invalid for some surviving history")
            cost=0
        elif kind=="read":
            cost=m.read_cost
        elif kind=="probe":
            if depth==0:raise ValueError("exceeds max probe count")
            p=lookup.get(node.get("probe"))
            if p is None:raise ValueError("unknown probe")
            branches=node.get("branches")
            expected=post(p,belief)
            if not isinstance(branches,dict) or set(branches)!=set(expected):
                raise ValueError("missing or fabricated public observation response")
            cost=p.cost+max(walk(branches[o],v,depth-1)
                            for o,v in expected.items())
        else:
            raise ValueError("invalid tree")
        if type(node.get("worst_remaining_cost")) is not int or node["worst_remaining_cost"]!=cost:
            raise ValueError("falsified worst cost")
        return cost

    real=walk(cert["root"],states,m.max_depth)
    if type(cert.get("worst_cost")) is not int or real!=cert["worst_cost"]:
        raise ValueError("fake root cost")
    return {"verified":True,"worst_cost":real,"input_histories":len(states)}


def exhaustive_oracle(m):
    """Independent uncached minimax recursion for small finite tests."""
    states=validate(m)
    def brute(b,depth):
        if common(m,b):return 0
        best=m.read_cost
        if depth:
            for p in m.probes:
                worst=max(brute(v,depth-1) for v in post(p,b).values())
                best=min(best,p.cost+worst)
        return best
    return brute(states,m.max_depth)


def decision(m,certificate,responses:tuple[str,...]):
    verify(m,certificate)
    node=certificate["root"]
    if not isinstance(responses,tuple):raise ValueError("tuple response trace required")
    for observation in responses:
        if node["kind"]!="probe":
            raise ValueError("response after terminal decision")
        if observation not in node["branches"]:
            return {"request":"read","certificate_valid_for_trace":False,
                    "reason":"unmodeled_public_response"}
        node=node["branches"][observation]
    if node["kind"]=="authorize":
        return {"request":"authorize","action":node["action"],
                "certificate_valid_for_trace":True}
    if node["kind"]=="read":
        return {"request":"read","certificate_valid_for_trace":True}
    return {"request":"probe","probe":node["probe"],"certificate_valid_for_trace":True}
