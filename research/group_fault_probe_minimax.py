"""BeliefBridge: exact finite minimax probing with correlated sensor GROUP faults.

Up to K public sensing groups may behave arbitrarily for the whole episode;
repeated observations in one compromised group are NOT independent. Repairs
are authorized only on consensus of every retained hidden controller state.
All probes are pre-certified repair-preserving. This is a finite MODEL-ONLY
theorem/experiment, NOT physical robot safety or actual PhysX success.
"""
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Mapping
import copy
import json

@dataclass(frozen=True)
class Model:
    repairs: Mapping[str,str]
    responses: Mapping[str,Mapping[str,str]]
    groups: Mapping[str,str]
    alphabets: Mapping[str,tuple[str,...]]
    costs: Mapping[str,int]
    read_cost: int
    max_probes: int
    faulty_group_budget: int
    preserves_repair: Mapping[str,bool]

def validate(m):
    if not isinstance(m.repairs,Mapping) or not 2<=len(m.repairs)<=6:
        raise ValueError("invalid latent repair states")
    h=tuple(sorted(m.repairs))
    if any(type(x) is not str or not x or type(m.repairs[x]) is not str or not m.repairs[x] for x in h):
        raise ValueError("invalid state or repair label")
    if not isinstance(m.responses,Mapping) or not 1<=len(m.responses)<=5:
        raise ValueError("no finite probes")
    probes=tuple(sorted(m.responses))
    if any(set(d)!=set(probes) for d in (m.groups,m.alphabets,m.costs,m.preserves_repair)):
        raise ValueError("incomplete public probe descriptor")
    if type(m.read_cost) is not int or not 1<=m.read_cost<=50:
        raise ValueError("invalid privileged read cost")
    if type(m.max_probes) is not int or not 0<=m.max_probes<=5:
        raise ValueError("invalid probe horizon")
    if type(m.faulty_group_budget) is not int or not 0<=m.faulty_group_budget<=2:
        raise ValueError("invalid group corruption allowance")
    for p in probes:
        if set(m.responses[p])!=set(h):
            raise ValueError("incomplete probe response model")
        alphabet=m.alphabets[p]
        if (not isinstance(alphabet,tuple) or not alphabet
            or len(set(alphabet))!=len(alphabet)
            or any(type(x) is not str or not x for x in alphabet)
            or any(m.responses[p][x] not in alphabet for x in h)):
            raise ValueError("unmodeled public response alphabet")
        if type(m.groups[p]) is not str or not m.groups[p]:
            raise ValueError("unknown correlated-failure identity")
        if type(m.costs[p]) is not int or not 1<=m.costs[p]<=50:
            raise ValueError("unverified action acquisition cost")
        if m.preserves_repair[p] is not True:
            raise ValueError("probe can change authorized repair")
    groups=tuple(sorted(set(m.groups.values())))
    return h,probes,{g:(1<<i) for i,g in enumerate(groups)}

def posterior(m,b,p,o,bits):
    if p not in m.responses or o not in m.alphabets[p]:
        raise ValueError("observation outside declared complete support")
    bit=bits[m.groups[p]]
    result=[]
    for h,previous_faulty in b:
        required=previous_faulty | (bit if o!=m.responses[p][h] else 0)
        if required.bit_count()<=m.faulty_group_budget:
            result.append((h,required))
    return tuple(sorted(result))

def consensus(m,b):
    labels={m.repairs[h] for h,_ in b}
    return next(iter(labels)) if len(labels)==1 else None

def synthesize(m):
    histories,probes,bits=validate(m)
    original=tuple((h,0) for h in histories)
    @lru_cache(None)
    def optimize(b,remaining):
        match=consensus(m,b)
        if match is not None:
            return 0,{"action":"authorize","repair":match,"belief":[list(x) for x in b],"value":0}
        best=m.read_cost
        plan={"action":"read","belief":[list(x) for x in b],"value":best}
        if remaining:
            for p in probes:
                if m.costs[p]>=best:continue
                branches={}
                worst=0
                for o in m.alphabets[p]:
                    after=posterior(m,b,p,o,bits)
                    if after:
                        cost,sub=optimize(after,remaining-1)
                        branches[o]=sub
                        worst=max(worst,cost)
                if branches and m.costs[p]+worst<best:
                    best=m.costs[p]+worst
                    plan={"action":"probe","probe":p,"branches":branches,
                          "belief":[list(x) for x in b],"value":best}
        return best,plan
    cost,tree=optimize(original,m.max_probes)
    return {"model_only":True,"worst_cost":cost,"tree":tree,
            "scope":"Static deterministic responses; <=K arbitrarily wrong GROUPS; no certified physical independence."}

def certify(m,certificate):
    histories,probes,bits=validate(m)
    original=tuple((h,0) for h in histories)
    def inspect(node,b,remaining):
        if node.get("belief")!=[list(x) for x in b]:
            raise ValueError("forged posterior")
        action=node.get("action")
        if action=="authorize":
            if consensus(m,b) is None or node.get("repair")!=consensus(m,b):
                raise ValueError("incorrect repair authorization")
            cost=0
        elif action=="read":cost=m.read_cost
        elif action=="probe":
            p=node.get("probe")
            if not remaining or p not in probes:raise ValueError("bad probe")
            exits={o:posterior(m,b,p,o,bits) for o in m.alphabets[p]}
            exits={o:s for o,s in exits.items() if s}
            if not exits or set(node.get("branches",{}))!=set(exits):
                raise ValueError("missing reachable response")
            cost=m.costs[p]+max(inspect(node["branches"][o],sub,remaining-1)
                                for o,sub in exits.items())
        else:raise ValueError("invalid action")
        if type(node.get("value")) is not int or node["value"]!=cost:
            raise ValueError("falsified path cost")
        return cost
    submitted=inspect(certificate["tree"],original,m.max_probes)
    if type(certificate.get("worst_cost")) is not int or certificate["worst_cost"]!=submitted:
        raise ValueError("root cost incorrect")
    # Independent minimax recursion does NOT consult the submitted action tree.
    @lru_cache(None)
    def oracle(b,remaining):
        if consensus(m,b) is not None:return 0
        best=m.read_cost
        if remaining:
            for p in probes:
                succ=[posterior(m,b,p,o,bits) for o in m.alphabets[p]]
                succ=[x for x in succ if x]
                if succ:
                    best=min(best,m.costs[p]+max(oracle(x,remaining-1) for x in succ))
        return best
    if submitted!=oracle(original,m.max_probes):
        raise ValueError("feasible but NOT minimax optimal")
    return {"verified_minimax_cost":submitted,"model_only":True}

def next_action(m,certificate,transcript):
    certify(m,certificate)
    node=certificate["tree"]
    for p,o in transcript:
        if node["action"]!="probe" or node["probe"]!=p:
            raise ValueError("unrequested observation")
        if o not in node["branches"]:
            return {"action":"read","unmodeled":True,"certificate_valid":False}
        node=node["branches"][o]
    return {"action":node["action"],"repair":node.get("repair"),"probe":node.get("probe")}

def example(groups=3,corrupt=1,depth=3,read=5):
    names=tuple("abc"[:groups])
    return Model({"applied":"continue","held":"reset"},
      {p:{"applied":"a","held":"h"} for p in names},
      {p:p for p in names},{p:("a","h") for p in names},
      {p:1 for p in names},read,depth,corrupt,{p:True for p in names})

def selftest():
    m=example()
    cert=synthesize(m)
    assert cert["worst_cost"]==3
    assert certify(m,cert)["verified_minimax_cost"]==3
    assert synthesize(example(1))["worst_cost"]==5
    assert synthesize(example(2))["worst_cost"]==5
    assert synthesize(example(3,0))["worst_cost"]==1
    observed=0
    # Enumerate every adaptive outcome, under each actual hidden state and
    # all choices of <=1 entire compromised sensing group.
    for actual in m.repairs:
        for faulty in ((),("a",),("b",),("c",)):
            def walk(node):
                nonlocal observed
                if node["action"]=="authorize":
                    assert node["repair"]==m.repairs[actual]
                    observed+=1
                elif node["action"]=="read":
                    observed+=1
                else:
                    p=node["probe"]
                    outcomes=m.alphabets[p] if p in faulty else (m.responses[p][actual],)
                    for answer in outcomes:
                        nxt=node["branches"].get(answer)
                        if nxt is not None:walk(nxt)
                        else:observed+=1
            walk(cert["tree"])
    assert observed==12,observed
    forged=copy.deepcopy(cert)
    forged["tree"]["branches"]["h"]={"action":"authorize","repair":"reset",
        "belief":[["applied",1],["held",0]],"value":0}
    try:certify(m,forged)
    except ValueError:pass
    else:raise AssertionError("unsafe forged consensus")
    suboptimal=copy.deepcopy(cert)
    suboptimal["tree"]={"action":"read","belief":[["applied",0],["held",0]],"value":5}
    suboptimal["worst_cost"]=5
    try:certify(m,suboptimal)
    except ValueError:pass
    else:raise AssertionError("self-consistent nonoptimal plan")
    # Deliberately VIOLATES K=1: two compromised groups can misauthorize.
    wrong=next_action(m,cert,(("a","h"),("b","h")))
    assert wrong["action"]=="authorize" and wrong["repair"]=="reset"
    return {"status":"PASS_CORRELATED_FAULT_FINITE_MODEL_ONLY",
        "K0_worst_cost":1,"K1_3_distinct_groups_cost":3,
        "K1_2_distinct_groups_cost":5,
        "K1_repeated_1_group_cost":5,
        "exhaustive_physical_world_fault_group_traces":observed,
        "K_plus_1_corruption_produces_wrong_repair":True,
        "not_claimed":"actual robot task success or sensor independence"}
if __name__=="__main__":
    print(json.dumps(selftest(),indent=2))
