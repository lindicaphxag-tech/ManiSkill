"""Independent exhaustive finite receipt optimality tests.

Partitions are enumerated WITHOUT reusing the main algorithm's DSATUR
search. Exhaustive restricted-growth partition enumeration works for the
8-state H=3 cases (Bell number 4140).
"""
from fractions import Fraction
from itertools import product

import pytest

from research.zero_error_execution_receipt import (
    analyze_case,bayes_accuracy,conflict_graph,dsatur_coloring,model,
    proper_coloring,receipt_decoder
)


def all_set_partitions_by_restricted_growth(n):
    if n<1:
        return
    assignment=[0]*n
    def recurse(index,max_color):
        if index==n:
            yield tuple(assignment)
            return
        for c in range(max_color+2):
            assignment[index]=c
            yield from recurse(index+1,max(max_color,c))
    yield from recurse(1,0)


def independently_brute_minimum_colors(graph):
    n=len(graph)
    best=n
    for coloring in all_set_partitions_by_restricted_growth(n):
        colors=max(coloring)+1
        if colors>=best:
            continue
        if all(coloring[v]!=coloring[w] for v in range(n)
               for w in range(v+1,n) if graph[v]&(1<<w)):
            best=colors
    return best


@pytest.mark.parametrize("morphology",range(2))
@pytest.mark.parametrize("seed",range(111,123))
@pytest.mark.parametrize("resolution",range(3))
@pytest.mark.parametrize("noise",range(2))
def test_every_3_ack_history_exact_chromatic_minimal_against_independent_bruteforce(
    morphology,seed,resolution,noise
):
    m=model(morphology,3,seed,resolution,noise)
    g=conflict_graph(m["anchor"],m["observation_support"])
    color,k=dsatur_coloring(g)
    independently_optimal=independently_brute_minimum_colors(g)
    assert k==independently_optimal
    assert proper_coloring(g,color)
    _,nerrors=receipt_decoder(m["anchor"],m["observation_support"],color)
    assert nerrors==0


@pytest.mark.parametrize("morphology",range(2))
@pytest.mark.parametrize("seed",range(111,123))
@pytest.mark.parametrize("resolution",range(3))
@pytest.mark.parametrize("noise",range(2))
def test_all_4_ack_history_exact_collisions(morphology,seed,resolution,noise):
    m=model(morphology,4,seed,resolution,noise)
    graph=conflict_graph(m["anchor"],m["observation_support"])
    c,k=dsatur_coloring(graph)
    assert len(c)==16
    assert proper_coloring(graph,c)
    assert receipt_decoder(m["anchor"],m["observation_support"],c)[1]==0
    assert k<=16
    assert 0<bayes_accuracy(m["anchor"],m["observation_support"])<=1


def test_observation_aliasing_with_distinct_safe_commands_provably_needs_receipt():
    anchor={0:0,1:3,2:8,3:11}
    seen={0:frozenset({0}),1:frozenset({0}),2:frozenset({1}),3:frozenset({1})}
    graph=conflict_graph(anchor,seen)
    color,k=dsatur_coloring(graph)
    assert k==2
    assert receipt_decoder(anchor,seen,color)[1]==0
    assert bayes_accuracy(anchor,seen)<1
    assert bayes_accuracy(anchor,seen,dict(enumerate(color)))==1
    # Four full histories require 2 bits, yet side-informed fixed-length
    # zero-error receipt needs only 1 bit; standard graph coloring prior art.


def test_zero_provenance_observation_is_not_promoted_to_a_safety_guarantee():
    anchor={0:1,1:2}
    seen={0:frozenset({0}),1:frozenset({0})}
    graph=conflict_graph(anchor,seen)
    assert graph==[2,1]
    assert receipt_decoder(anchor,seen,{0:0,1:0})[1]>0
    assert dsatur_coloring(graph)[1]==2


def test_silent_controller_histories_can_share_receipt_when_correct_action_same():
    anchor={0:5,1:5,2:8}
    seen={0:frozenset({0}),1:frozenset({0}),2:frozenset({0})}
    graph=conflict_graph(anchor,seen)
    assert graph[0]&2==0
    color,k=dsatur_coloring(graph)
    assert k==2
    assert color[0]==color[1]
    assert receipt_decoder(anchor,seen,color)[1]==0


@pytest.mark.parametrize("bad_adj",[[1], [2,0], [0,0]*9])
def test_invalid_or_oversized_graph_refused(bad_adj):
    with pytest.raises(ValueError):
        dsatur_coloring(bad_adj)


def test_uninformative_belief_and_popcount_baselines_are_compared_fairly():
    m=model(0,4,113,2,1)
    anchor,support=m["anchor"],m["observation_support"]
    no_receipt=bayes_accuracy(anchor,support)
    count_receipt=bayes_accuracy(
        anchor,support,{h:h.bit_count() for h in anchor}
    )
    exact_color=dsatur_coloring(conflict_graph(anchor,support))[0]
    exact_receipt=bayes_accuracy(anchor,support,dict(enumerate(exact_color)))
    assert 0<no_receipt<=count_receipt<=exact_receipt+1e-12
    assert abs(exact_receipt-1)<1e-12


def test_full_original_registered_case_cardinality_and_safe_receipts():
    case=analyze_case(1,4,112,1,1)
    assert case["full_ack_bits"]==4
    assert case["saved_bits"]>=0
    assert case["minimum_receipt_bayes_anchor_accuracy"]==1
    assert case["zero_error_received_controller_anchor"]
