"""Exact finite zero-error action-receipt study for quantized controller anchors.

Existing side-information characteristic graph + exact graph coloring are
classical information theory; this is a new candidate systems protocol, NOT
first-priority mathematical discovery. Toy controller model only; no claim
of native PhysX task or hardware safety.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
import random
import subprocess


PLAN=Path("research/EXECUTION_RECEIPT_FINITE_PREREG_20261013.json")
PLAN_BLOB="b0acaad21cae056f609b7614ed6f0a37a432c22c"


def registered():
    source_sha=subprocess.check_output(["git","hash-object",str(PLAN)],
                                        text=True).strip()
    if source_sha!=PLAN_BLOB:
        raise RuntimeError("Prospectively frozen protocol was altered")
    p=json.loads(PLAN.read_text(encoding="utf-8"))
    if (p["freeze"]!="BEFORE_ORIGINAL_TEST_OUTPUT"
        or p["ack_history_lengths"]!=[3,4]
        or p["morphologies"]!=["Panda-like","xArm6-like"]
        or p["observation_quantizations"]!=[0.8,1.4,2.1]
        or p["noise_radius_fraction_of_quantization"]!=[0.,.08]
        or p["seed_ids"]!=list(range(111,123))):
        raise RuntimeError("Incorrect frozen scenario and cohort")
    return p


def model(morphology_index, count, seed, quant_index, noise_index):
    if morphology_index not in (0,1) or count not in (3,4):
        raise ValueError("Unregistered exact ACK model")
    pools=((4,6,8,12,14),(6,9,10,15,18))
    choice=random.Random(20261013+seed*19+count*7+
                         morphology_index*101)
    steps=tuple(choice.choices(pools[morphology_index],k=count))
    q=(16,28,42)[quant_index]
    noise=Fraction((0,2)[noise_index]*q,25)
    anchor={h:sum(((h>>i)&1)*step for i,step in enumerate(steps))
            for h in range(1<<count)}
    # Controller observation is a coarse quantized endpoint with
    # bounded, rather than unbounded-Gaussian, sensor noise.
    possible={
        h:frozenset(range(
            math.floor((Fraction(a)-noise)/q),
            math.floor((Fraction(a)+noise)/q)+1
        )) for h,a in anchor.items()
    }
    return {
        "morphology":morphology_index,"count":count,"seed":seed,
        "quantization_index":quant_index,"noise_index":noise_index,
        "steps":steps,"quantization":q,"noise":str(noise),
        "anchor":anchor,"observation_support":possible
    }


def conflict_graph(anchor, support):
    """Conflicting histories can produce the same z but require different u."""
    n=len(anchor)
    if tuple(sorted(anchor))!=tuple(range(n)) or tuple(sorted(support))!=tuple(range(n)):
        raise ValueError("History alphabet not complete")
    adj=[0]*n
    for h in range(n):
        for k in range(h+1,n):
            if anchor[h]!=anchor[k] and not support[h].isdisjoint(support[k]):
                adj[h]|=1<<k
                adj[k]|=1<<h
    return adj


def dsatur_coloring(adj, *, exact=True):
    """Deterministic DSATUR; exact branch-and-bound for <=16 ACK histories."""
    n=len(adj)
    if n<1 or n>16:
        raise ValueError("Finite exhaustive study only, max 16 states")
    if any(((adj[i]>>i)&1) for i in range(n)):
        raise ValueError("Self-loop invalid")
    if any(bool((adj[i]>>j)&1)!=bool((adj[j]>>i)&1)
           for i in range(n) for j in range(n)):
        raise ValueError("Graph must be undirected")

    def choose(colors):
        available=[v for v in range(n) if colors[v]==-1]
        def priority(v):
            neighbours={colors[u] for u in range(n)
                        if ((adj[v]>>u)&1) and colors[u]>=0}
            return (len(neighbours),adj[v].bit_count(),-v)
        return max(available,key=priority)

    def blocked(v,colors):
        return {colors[u] for u in range(n)
                if ((adj[v]>>u)&1) and colors[u]>=0}

    greedy=[-1]*n
    used=0
    for _ in range(n):
        v=choose(greedy)
        invalid=blocked(v,greedy)
        c=next(i for i in range(n+1) if i not in invalid)
        greedy[v]=c
        used=max(used,c+1)
    if not exact:
        return tuple(greedy),used

    best=used
    best_colors=tuple(greedy)
    trial=[-1]*n

    def recurse(n_assigned,used_colors):
        nonlocal best,best_colors
        if used_colors>=best:
            return
        if n_assigned==n:
            best,best_colors=used_colors,tuple(trial)
            return
        v=choose(trial)
        taken=blocked(v,trial)
        for c in range(min(used_colors+1,best)):
            if c in taken or c>=best:
                continue
            trial[v]=c
            recurse(n_assigned+1,max(used_colors,c+1))
            trial[v]=-1

    recurse(0,0)
    assert proper_coloring(adj,best_colors)
    return best_colors,best


def proper_coloring(adj,coding):
    n=len(adj)
    if len(coding)!=n or any(not isinstance(x,int) or x<0 for x in coding):
        return False
    return all(coding[i]!=coding[j] for i in range(n)
               for j in range(i+1,n) if ((adj[i]>>j)&1))


def receipt_decoder(anchor,support,receipt):
    """Exhaustive observability/zero-error test; returns z+tag→anchor."""
    decoder={}
    mistakes=0
    for h,a in anchor.items():
        for z in support[h]:
            key=(z,receipt[h])
            if key in decoder and decoder[key]!=a:
                mistakes+=1
            else:
                decoder[key]=a
    return decoder,mistakes


def bayes_accuracy(anchor,support,receipt=None):
    """Exact Bayes maximum posterior anchor using identical public z + tags.

    Prior P(h)=1/n; conditional sensor quantization P(z|h) is
    uniform over finite support[h]. This is a strong matched baseline, not
    an ad-hoc wrong guess or an algorithm that may access private h.
    """
    n=len(anchor)
    masses=defaultdict(lambda:defaultdict(Fraction))
    for h,a in anchor.items():
        for z in support[h]:
            key=(z,None if receipt is None else receipt[h])
            masses[key][a]+=Fraction(1,n*len(support[h]))
    return float(sum((max(x.values()) for x in masses.values()),Fraction(0)))


def analyze_case(morphology_index,count,seed,quant_index,noise_index):
    m=model(morphology_index,count,seed,quant_index,noise_index)
    graph=conflict_graph(m["anchor"],m["observation_support"])
    color,num=dsatur_coloring(graph)
    greedy,kgreedy=dsatur_coloring(graph,exact=False)
    _,errors=receipt_decoder(m["anchor"],m["observation_support"],color)
    if errors or not proper_coloring(graph,color):
        raise RuntimeError("Minimal receipt unsafe under original sensor supports")
    full={h:h for h in m["anchor"]}
    popcount={h:h.bit_count() for h in m["anchor"]}
    full_error=receipt_decoder(m["anchor"],m["observation_support"],full)[1]
    greedy_error=receipt_decoder(m["anchor"],m["observation_support"],greedy)[1]
    if full_error or greedy_error:
        raise RuntimeError("Full/unoptimized greedy receipt violated baseline")
    bits=math.ceil(math.log2(num)) if num>1 else 0
    greedy_bits=math.ceil(math.log2(kgreedy)) if kgreedy>1 else 0
    if bits>count or bits>greedy_bits:
        raise RuntimeError("Exact coloring exceeded admissible receipt baseline")
    return {
        "morphology":m["morphology"],"history_bits":count,"seed":seed,
        "quantization_index":quant_index,"noise_index":noise_index,
        "controller_steps_scaled_x20":list(m["steps"]),
        "minimum_distinct_tags":num,"exact_minimum_receipt_bits":bits,
        "full_ack_bits":count,"saved_bits":count-bits,
        "greedy_receipt_bits":greedy_bits,
        "number_of_histories":len(m["anchor"]),
        "sensor_only_bayes_anchor_accuracy":bayes_accuracy(
            m["anchor"],m["observation_support"]),
        "popcount_receipt_bayes_anchor_accuracy":bayes_accuracy(
            m["anchor"],m["observation_support"],popcount),
        "minimum_receipt_bayes_anchor_accuracy":bayes_accuracy(
            m["anchor"],m["observation_support"],dict(enumerate(color))),
        "zero_error_received_controller_anchor":True,
        "number_of_conflicts":sum(x.bit_count() for x in graph)//2,
    }


def execute(output):
    p=registered()
    cases=[
        analyze_case(m,h,seed,q,e)
        for m,h,seed,q,e in product(
            range(2),p["ack_history_lengths"],
            p["seed_ids"],range(3),range(2)
        )
    ]
    if len(cases)!=288:
        raise RuntimeError("Missing preregistered controller condition")
    for r in cases:
        if abs(r["minimum_receipt_bayes_anchor_accuracy"]-1)>1e-12:
            raise RuntimeError("Exact receipt cannot decode in a supported observation")
        if r["sensor_only_bayes_anchor_accuracy"]>1.+1e-12:
            raise RuntimeError("Nonsense Bayesian posterior")
    qualifying=[
        r for r in cases if r["saved_bits"]/r["full_ack_bits"]>=.25
    ]
    per_morphology={
        str(m):{
            "count":sum(r["morphology"]==m for r in cases),
            "mean_saved_bits":sum(r["saved_bits"] for r in cases
                                  if r["morphology"]==m)/144,
            "at_least_25pct_saving":sum(
                r["morphology"]==m and
                r["saved_bits"]/r["full_ack_bits"]>=.25
                for r in cases
            ),
            "mean_sensor_only_bayes_accuracy":sum(
                r["sensor_only_bayes_anchor_accuracy"] for r in cases
                if r["morphology"]==m
            )/144,
        } for m in range(2)
    }
    report={
        "registered_original_protocol_blob":PLAN_BLOB,
        "original_finite_controller_cases":288,
        "number_of_scenario_morphologies":2,
        "cases_with_at_least_25pct_receipt_bit_saving":len(qualifying),
        "original_preregistered_gate_passed":len(qualifying)>=144,
        "zero_error_protocol_all_cases":True,
        "this_is_classic_functional_zero_error_source_coding":True,
        "not_original_information_theory_theorem":True,
        "not_physx_hardware_or_task_success_evidence":True,
        "per_morphology":per_morphology,
        "all_cases":cases
    }
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",
                      encoding="utf-8")
    print("ZERO_ERROR_RECEIPT_COMPLETE",json.dumps({
        k:v for k,v in report.items() if k!="all_cases"
    },sort_keys=True),flush=True)


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("exact_execution_receipt_conditions.json"))
    args=ap.parse_args()
    execute(args.out)
