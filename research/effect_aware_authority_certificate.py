"""Effect-aware repair and partial-getter contract with checkable optimality.

All claims are finite-model conditional. A *real* controller does NOT inherit
these safety/optimality properties until its transition/repair/getter model and
atomic read epochs are independently validated.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from typing import Any, Mapping


@dataclass(frozen=True)
class Action:
    name: str
    cost: int
    transitions: Mapping[str, tuple[tuple[str, str], ...]]


@dataclass(frozen=True)
class Contract:
    initial: tuple[str, ...]
    goals: tuple[str, ...]
    forbidden: tuple[str, ...]
    probes: tuple[Action, ...]
    repair_effects: Mapping[str, Mapping[str, tuple[str, ...]]]
    read_support: Mapping[str, tuple[str, ...]]
    read_atomic_and_fresh: bool
    read_cost: int
    stop_cost: int
    horizon: int


def validate(m: Contract) -> tuple[str, ...]:
    all_states=set(m.read_support)
    if not all_states or any(not isinstance(s,str) or not s for s in all_states):
        raise ValueError("Need finite nonempty hidden controller state registry")
    for key,items in [("initial",m.initial),("goals",m.goals),
                      ("forbidden",m.forbidden)]:
        if (not isinstance(items,tuple) or len(items)!=len(set(items)) or
            any(s not in all_states for s in items)):
            raise ValueError("Invalid "+key+" state registry")
    if (not m.initial or not m.goals or
        set(m.initial)&set(m.forbidden) or
        set(m.goals)&set(m.forbidden)):
        raise ValueError("Unsafe or empty initialization/goal")
    if type(m.read_atomic_and_fresh) is not bool:
        raise ValueError("Read atomicity must be a verified boolean model condition")
    if (type(m.horizon) is not int or m.horizon<0 or
        type(m.read_cost) is not int or m.read_cost<=0 or
        type(m.stop_cost) is not int or m.stop_cost<=0):
        raise ValueError("Invalid nonnegative depth / positive costs")
    if not m.repair_effects:
        raise ValueError("No modeled repair actions")
    for name,effects in m.repair_effects.items():
        if not isinstance(name,str) or not name or set(effects)!=all_states:
            raise ValueError("Incomplete repair effect transition registry")
        for s,dest in effects.items():
            if (not isinstance(dest,tuple) or not dest or
                len(dest)!=len(set(dest)) or any(x not in all_states for x in dest)):
                raise ValueError("Missing or invalid repair outcomes")
    for s,outcomes in m.read_support.items():
        if (not isinstance(outcomes,tuple) or not outcomes or
            len(set(outcomes))!=len(outcomes) or
            any(not isinstance(v,str) or not v for v in outcomes)):
            raise ValueError("Incomplete / ambiguous read response symbols")
    names=set()
    for p in m.probes:
        if (not isinstance(p.name,str) or not p.name or p.name in names or
            type(p.cost) is not int or p.cost<=0 or set(p.transitions)!=all_states):
            raise ValueError("Invalid probe name/cost or transition coverage")
        names.add(p.name)
        for state,edges in p.transitions.items():
            if (not isinstance(edges,tuple) or not edges or
                len(set(edges))!=len(edges)):
                raise ValueError("Missing or duplicate probe transitions")
            for obs,nxt in edges:
                if (not isinstance(obs,str) or not obs or nxt not in all_states):
                    raise ValueError("Invalid probe observation or latent transition")
    return tuple(sorted(m.initial))


def model_hash(m:Contract)->str:
    validate(m)
    payload={
        "initial":sorted(m.initial),"goals":sorted(m.goals),
        "forbidden":sorted(m.forbidden),"read_atomic_and_fresh":m.read_atomic_and_fresh,
        "read_cost":m.read_cost,"stop_cost":m.stop_cost,"horizon":m.horizon,
        "read_support":sorted((s,sorted(v)) for s,v in m.read_support.items()),
        "repairs":sorted((name,sorted((s,sorted(v)) for s,v in mapping.items()))
                         for name,mapping in m.repair_effects.items()),
        "probes":sorted((p.name,p.cost,sorted((s,sorted(edges))
                                              for s,edges in p.transitions.items()))
                         for p in m.probes),
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,
                                     separators=(",",":")).encode()).hexdigest()


def safe_repairs(m:Contract, belief:tuple[str,...])->tuple[str,...]:
    goals=set(m.goals)
    return tuple(sorted(name for name,table in m.repair_effects.items()
                        if all(set(table[s])<=goals for s in belief)))


def _probed(m:Contract,p:Action,belief:tuple[str,...]):
    edges=[(obs,nxt) for s in belief for obs,nxt in p.transitions[s]]
    if any(nxt in m.forbidden for _,nxt in edges):
        return None
    return {obs:tuple(sorted({nxt for o,nxt in edges if o==obs}))
            for obs in sorted({o for o,_ in edges})}


def _read(m:Contract,belief:tuple[str,...]):
    return {obs:tuple(s for s in belief if obs in m.read_support[s])
            for obs in sorted({v for s in belief for v in m.read_support[s]})}


def synthesize(m:Contract)->dict[str,Any]:
    start=validate(m)
    @lru_cache(None)
    def find(b:tuple[str,...],h:int,used:bool):
        repairs=safe_repairs(m,b)
        if repairs:
            return 0,{"kind":"authorize","repair":repairs[0],"belief":list(b),"cost":0}
        best=m.stop_cost
        node={"kind":"halt","belief":list(b),"cost":best}
        # A fresh getter can only be used once. An aliased getter does not
        # magically reveal the full latent state.
        if not used and m.read_atomic_and_fresh:
            children={o:find(s,h,True) for o,s in _read(m,b).items()}
            v=m.read_cost+max(c for c,_ in children.values())
            if v<best:
                best=v
                node={"kind":"read","belief":list(b),"cost":v,
                      "branches":{o:n for o,(_,n) in children.items()}}
        if h>0:
            for p in sorted(m.probes,key=lambda p:p.name):
                if p.cost>=best:
                    continue
                succ=_probed(m,p,b)
                if succ is None:
                    continue
                children={o:find(s,h-1,used) for o,s in succ.items()}
                v=p.cost+max(c for c,_ in children.values())
                if v<best:
                    best=v
                    node={"kind":"probe","probe":p.name,"belief":list(b),
                          "cost":v,"branches":{o:n for o,(_,n) in children.items()}}
        return best,node
    value,root=find(start,m.horizon,False)
    cert={"schema":"effect_aware_partial_getter_v1","model_hash":model_hash(m),
          "minimax_cost":value,"root":root,
          "evidence_scope":"FINITE_MODEL_ONLY_UNVERIFIED_REAL_CONTROLLER"}
    verify_policy(m,cert)
    verify_optimality(m,cert)
    return cert


def verify_policy(m:Contract,cert:Mapping[str,Any])->dict[str,int|bool]:
    """Separate soundness checker; no call to synthesize."""
    start=validate(m)
    if (cert.get("schema")!="effect_aware_partial_getter_v1" or
        cert.get("model_hash")!=model_hash(m)):
        raise ValueError("Stale or forged model provenance")
    look={p.name:p for p in m.probes}
    counts={"authorized":0,"halts":0,"reads":0,"probes":0}
    def walk(node,b,h,used):
        if not isinstance(node,Mapping) or node.get("belief")!=list(b):
            raise ValueError("Incorrect posterior after actual modeled transition")
        kind=node.get("kind")
        if kind=="authorize":
            if node.get("repair") not in safe_repairs(m,b):
                raise ValueError("Unsafe repair effect or unverified goal")
            counts["authorized"]+=1
            value=0
        elif kind=="halt":
            counts["halts"]+=1
            value=m.stop_cost
        elif kind in ("read","probe"):
            children=node.get("branches")
            if not isinstance(children,dict):
                raise ValueError("Missing observation branch map")
            if kind=="read":
                if used or not m.read_atomic_and_fresh:
                    raise ValueError("Stale, unauthenticated, or repeated privileged read")
                succ=_read(m,b)
                base=m.read_cost
                h_next,used_next=h,True
                counts["reads"]+=1
            else:
                if h<=0 or node.get("probe") not in look:
                    raise ValueError("Invalid probe/depth")
                p=look[node["probe"]]
                succ=_probed(m,p,b)
                if succ is None:
                    raise ValueError("Probe might reach forbidden hidden state")
                base=p.cost
                h_next,used_next=h-1,used
                counts["probes"]+=1
            if set(children)!=set(succ):
                raise ValueError("Missing, fabricated or omitted possible public responses")
            value=base+max(walk(children[o],s,h_next,used_next)
                           for o,s in succ.items())
        else:
            raise ValueError("Unexpected decision kind")
        if type(node.get("cost")) is not int or node["cost"]!=value:
            raise ValueError("Incorrect computed worst-case cost")
        return value
    got=walk(cert["root"],start,m.horizon,False)
    if type(cert.get("minimax_cost")) is not int or cert["minimax_cost"]!=got:
        raise ValueError("Bad root value")
    return {"all_branches_sound":True,"checked_worst_cost":got,**counts}


def verify_optimality(m:Contract,cert:Mapping[str,Any],
                      *,max_oracle_nodes:int=200000)->dict[str,int|bool]:
    """Independent exhaustive Bellman verifier; no planner or tree recursion.

    This is an algorithmically independent finite-model optimality check, not
    a formal proof about unknown physical dynamics. Refuse resource overflow.
    """
    verify_policy(m,cert)
    if type(max_oracle_nodes) is not int or max_oracle_nodes<1:
        raise ValueError("Invalid oracle complexity bound")
    counter=[0]
    @lru_cache(None)
    def oracle(b:tuple[str,...],h:int,used:bool)->int:
        counter[0]+=1
        if counter[0]>max_oracle_nodes:
            raise ValueError("Exact optimality not checked: oracle state cap exceeded")
        # Derive repair feasibility directly without using safe_repairs().
        goals=set(m.goals)
        for effects in m.repair_effects.values():
            if all(all(dest in goals for dest in effects[s]) for s in b):
                return 0
        possibilities=[m.stop_cost]
        if not used and m.read_atomic_and_fresh:
            symbols={obs for s in b for obs in m.read_support[s]}
            possibilities.append(
                m.read_cost+max(
                    oracle(tuple(s for s in b if obs in m.read_support[s]),h,True)
                    for obs in symbols))
        if h:
            for p in m.probes:
                pairs=[(obs,nxt) for s in b for obs,nxt in p.transitions[s]]
                if any(nxt in m.forbidden for _,nxt in pairs):
                    continue
                symbols={obs for obs,_ in pairs}
                possibilities.append(
                    p.cost+max(
                        oracle(tuple(sorted({nxt for o,nxt in pairs if o==obs})),
                               h-1,used)
                        for obs in symbols))
        return min(possibilities)
    optimum=oracle(validate(m),m.horizon,False)
    if cert["minimax_cost"]!=optimum:
        raise ValueError("Sound certificate is NOT minimax optimal")
    return {"exact_independent_oracle_optimal":True,"optimal_cost":optimum,
            "oracle_belief_states":counter[0],"real_robot_certified":False}


def request(m:Contract,cert:Mapping[str,Any],
            events:tuple[tuple[str,str,bool],...])->dict[str,Any]:
    """Runtime request only. Read responses MUST carry verified fresh epoch flag.

    PhysX or hardware adapters must independently validate that Boolean; this
    function cannot authenticate an event delivered by an untrusted caller.
    """
    verify_policy(m,cert)
    if not isinstance(events,tuple):
        raise ValueError("Events must be a tuple")
    node=cert["root"]
    spent=0
    for event in events:
        if (not isinstance(event,tuple) or len(event)!=3 or
            not isinstance(event[0],str) or not isinstance(event[1],str) or
            type(event[2]) is not bool):
            raise ValueError("Invalid typed observation event")
        kind,symbol,fresh=event
        if node["kind"] not in ("probe","read") or kind!=node["kind"]:
            raise ValueError("Observation does not match requested intervention")
        if kind=="read" and not fresh:
            return {"request":"halt","reason":"read_epoch_unattested",
                    "model_bound_valid":False,"already_spent":spent+m.read_cost}
        spent+=m.read_cost if kind=="read" else next(
            p.cost for p in m.probes if p.name==node["probe"])
        if symbol not in node["branches"]:
            return {"request":"halt","reason":"out_of_model_response",
                    "model_bound_valid":False,"already_spent":spent}
        node=node["branches"][symbol]
    out={"request":node["kind"],"already_spent":spent,"model_bound_valid":True}
    if node["kind"]=="authorize":
        out["repair"]=node["repair"]
    if node["kind"]=="probe":
        out["probe"]=node["probe"]
    return out


def examples()->dict[str,Contract]:
    # An aliased read cannot justify unsafe correction. A fresh, fully
    # discriminating getter plus complete repair postcondition can.
    states=("good","held","bad")
    repairs={"GO":{"good":("good",),"held":("bad",),"bad":("bad",)},
             "RESET":{"good":("good",),"held":("good",),"bad":("good",)}}
    base={"initial":("good","held"),"goals":("good",),"forbidden":("bad",),
          "probes":(),"repair_effects":repairs,"read_cost":2,
          "stop_cost":10,"horizon":1}
    # Explicit common RESET makes the first example trivial; use separate
    # outcomes where no repair is universally successful.
    unsafe={"GO":{"good":("good",),"held":("bad",),"bad":("bad",)},
            "RESET":{"good":("bad",),"held":("good",),"bad":("good",)}}
    common={**base,"repair_effects":unsafe,
            "read_support":{"good":("same",),"held":("same",),"bad":("error",)},
            "read_atomic_and_fresh":True}
    distinct={**base,"repair_effects":unsafe,
              "read_support":{"good":("good_seen",),"held":("held_seen",),
                              "bad":("error",)},"read_atomic_and_fresh":True}
    stale={**distinct,"read_atomic_and_fresh":False}
    return {"aliased_getter":Contract(**common),
            "fresh_discriminating_getter":Contract(**distinct),
            "unattested_getter":Contract(**stale)}


if __name__=="__main__":
    for name,m in examples().items():
        cert=synthesize(m)
        print(name,json.dumps({"first":cert["root"]["kind"],
            "worst_abstract_cost":cert["minimax_cost"],
            "oracle":verify_optimality(m,cert)},sort_keys=True))
