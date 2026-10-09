"""Finite BeliefBridge repair-aware active probing with bounded adversarial observations.

A static, deterministic, REPAIR-PRESERVING public probe can be repeated. Of all
responses over an episode, up to K may be corrupted to another element of the
predeclared finite alphabet. Decisions are AUTHORIZE only if ALL possible
histories agree on the exact repair, else public PROBE or privileged READ.
The model, K, probe cost and response alphabet are assumed known; NOTHING
here proves a physical observation model or robot safety.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from typing import Mapping

@dataclass(frozen=True)
class Model:
    repairs: Mapping[str,str]
    probe_truth: Mapping[str,str]
    alphabet: tuple[str,...]
    probe_cost: int
    read_cost: int
    max_probes: int
    corruption_budget: int
    probe_preserves_repair: bool=True

def validate(m: Model):
    assert m.repairs and set(m.repairs)==set(m.probe_truth)
    assert m.alphabet and len(set(m.alphabet))==len(m.alphabet)
    assert set(m.probe_truth.values())<=set(m.alphabet)
    assert all(type(s) is str and s for s in list(m.repairs)+list(m.repairs.values())+list(m.alphabet))
    assert m.probe_preserves_repair,'unattested changing probe forbidden'
    assert 1<=m.probe_cost<=m.read_cost<=100
    assert 0<=m.max_probes<=6 and 0<=m.corruption_budget<=2
    assert 1<=len(m.repairs)<=8
    return tuple(sorted((h,0) for h in m.repairs))

def post(m,belief,observed):
    assert observed in m.alphabet
    return tuple(sorted((h,spent+(observed!=m.probe_truth[h]))
        for h,spent in belief if spent+(observed!=m.probe_truth[h])<=m.corruption_budget))

def unique_repair(m,belief):
    options={m.repairs[h] for h,_ in belief}
    return next(iter(options)) if len(options)==1 else None

def synthesize(m):
    initial=validate(m)
    @lru_cache(None)
    def dp(belief,depth):
        if (repair:=unique_repair(m,belief)) is not None:
            return 0,{'kind':'authorize','repair':repair,'belief':list(map(list,belief)),'worst_cost':0}
        best=m.read_cost
        node={'kind':'read','belief':list(map(list,belief)),'worst_cost':best}
        if depth:
            children={};worst=0
            for a in m.alphabet:
                after=post(m,belief,a)
                if after:
                    cost,child=dp(after,depth-1)
                    children[a]=child;worst=max(worst,cost)
            candidate=m.probe_cost+worst
            if children and candidate<best:
                best=candidate
                node={'kind':'probe','belief':list(map(list,belief)),
                      'branches':children,'worst_cost':best}
        return best,node
    cost,root=dp(initial,m.max_probes)
    return {'model_only':True,'cost':cost,'root':root,
            'scope':'At most K corruptions over static predeclared deterministic response alphabet; NOT physical sensing or task-level safety.'}

def verify(m,proof):
    initial=validate(m)
    def visit(node,belief,remaining):
        if node.get('belief')!=list(map(list,belief)):raise ValueError('forged posterior')
        kind=node.get('kind')
        if kind=='read':cost=m.read_cost
        elif kind=='authorize':
            if node.get('repair')!=unique_repair(m,belief):raise ValueError('wrong repair authorization')
            cost=0
        elif kind=='probe':
            if not remaining:raise ValueError('probe depth exceeded')
            should={a:post(m,belief,a) for a in m.alphabet if post(m,belief,a)}
            if set(node.get('branches',{}))!=set(should):raise ValueError('missing outcome')
            cost=m.probe_cost+max(visit(node['branches'][a],b,remaining-1) for a,b in should.items())
        else:raise ValueError('forged action')
        if node.get('worst_cost')!=cost:raise ValueError('falsified cost')
        return cost
    cost=visit(proof['root'],initial,m.max_probes)
    if cost!=proof.get('cost'):raise ValueError('wrong root cost')
    @lru_cache(None)
    def brute(b,remaining):
        if unique_repair(m,b) is not None:return 0
        cost=m.read_cost
        if remaining:
            future=[post(m,b,a) for a in m.alphabet]
            future=[t for t in future if t]
            cost=min(cost,m.probe_cost+max(brute(t,remaining-1) for t in future))
        return cost
    optimum=brute(initial,m.max_probes)
    if optimum!=cost:raise ValueError('feasible but not globally minimax')
    return {'status':'VALID_FINITE_MODEL_ONLY','worst_cost':cost,'states':len(initial),
            'models_physical_sensor_drift':False}

def follow(m,proof,observations):
    verify(m,proof)
    node=proof['root']
    for outcome in observations:
        if node['kind']!='probe':raise ValueError('late observation')
        if outcome not in node['branches']:
            return {'decision':'read','unmodeled_observation':True,
                    'minimax_certificate_valid_for_trace':False}
        node=node['branches'][outcome]
    if node['kind']=='authorize':
        return {'decision':'authorize','repair':node['repair']}
    return {'decision':node['kind']}

def proof_example():
    m=Model(repairs={'applied':'continue','held':'reset'},
      probe_truth={'applied':'a','held':'h'},alphabet=('a','h'),
      probe_cost=1,read_cost=5,max_probes=3,corruption_budget=1)
    plan=synthesize(m)
    assert plan['cost']==3,plan
    assert verify(m,plan)['worst_cost']==3
    import itertools
    enumerated=0
    for real in m.repairs:
        for seq in itertools.product(m.alphabet,repeat=3):
            if sum(v!=m.probe_truth[real] for v in seq)<=m.corruption_budget:
                for n in range(4):
                    decision=follow(m,plan,seq[:n])
                    if decision['decision']!='probe':break
                assert decision['decision']=='authorize' and decision['repair']==m.repairs[real],(real,seq,decision)
                enumerated+=1
    none=Model(m.repairs,m.probe_truth,m.alphabet,1,5,1,0)
    assert synthesize(none)['cost']==1
    insufficient=Model(m.repairs,m.probe_truth,m.alphabet,1,5,2,1)
    assert synthesize(insufficient)['cost']==5
    affordable_read=Model(m.repairs,m.probe_truth,m.alphabet,1,2,3,1)
    assert synthesize(affordable_read)['cost']==2
    tampered=synthesize(m)
    tampered['root']['branches']['h']={'kind':'authorize','repair':'reset',
        'belief':[['applied',1],['held',0]],'worst_cost':0}
    try:verify(m,tampered)
    except ValueError:pass
    else:raise AssertionError('unsafe one-response repair certificate accepted')
    return {'status':'PASS_MODEL_ONLY','K0_min_cost':1,'K1_three_probes_min_cost':3,
            'K1_two_probes_force_read_cost':5,'K1_cheap_privileged_read':2,
            'adversarial_ground_truth_sequences_checked':enumerated,
            'forged_one_response_certificate':'REJECTED'}

if __name__=='__main__':
    import json
    print(json.dumps(proof_example(),indent=2))
