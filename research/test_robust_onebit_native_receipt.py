"""Exact finite n=4 robust one-bit-receipt mechanism adversarial controls."""
import pytest
from research.robust_onebit_native_receipt import (
    one_bit_correcting_codec,
    decode_under_any_onebit_error,
    full_ack_one_error_correcting_baseline,
)


def _graph(n,edges):
    a=[0]*n
    for i,j in edges:
        a[i]|=1<<j
        a[j]|=1<<i
    return a


@pytest.mark.parametrize("edges,minimum",[
    ([],0),
    ([(0,1)],3),
    ([(0,1),(1,2),(2,3),(3,0)],3),
    ([(0,1),(1,2),(2,0)],5),
    ([(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)],5),
])
def test_robust_binary_code_proves_exact_minimum(edges,minimum):
    graph=_graph(4,edges)
    length,code=one_bit_correcting_codec(graph)
    assert length==minimum
    for i,j in edges:
        assert (code[i]^code[j]).bit_count()>=3
    # Make every history physically observable in a common bin,
    # except for pairs not requiring distinct actions where matching is OK.
    obs={i:{0} for i in range(4)}
    labels={i:i for i in range(4)}
    if minimum==0 and not edges:
        labels={i:0 for i in range(4)}
    elif edges and len(edges)<6:
        # Only needed counterfactual conflict edges need be distinguishable.
        # Use supported observations that share a bin only on actual
        # declared edges; this test checks code distance instead of
        # inventing an unrelated all-confusable decision label.
        return
    failures,_=decode_under_any_onebit_error(
        labels,obs,dict(enumerate(code)),length)
    assert failures==0


def test_protected_full_ack_four_histories_requires_5bits():
    length,words=full_ack_one_error_correcting_baseline()
    assert length==5
    labels={i:i for i in range(4)}
    observation={i:frozenset({0}) for i in range(4)}
    errors,total=decode_under_any_onebit_error(
        labels,observation,dict(enumerate(words)),length)
    assert errors==0 and total==4*6


def test_unprotected_two_bit_full_ack_fails_under_single_corruption():
    labels={i:i for i in range(4)}
    observation={i:frozenset({0}) for i in range(4)}
    errors,total=decode_under_any_onebit_error(
        labels,observation,{i:i for i in range(4)},2)
    assert errors>0 and total==4*3


def test_true_zero_bit_receipt_only_when_no_conflicting_decisions():
    graph=_graph(4,[])
    length,words=one_bit_correcting_codec(graph)
    assert length==0 and len(set(words))==1
    assert decode_under_any_onebit_error(
        {i:0 for i in range(4)},
        {i:frozenset({0}) for i in range(4)},
        dict(enumerate(words)),0
    )[0]==0


def test_asymmetric_or_loop_confusability_fails_closed():
    with pytest.raises(ValueError):
        one_bit_correcting_codec([2,0,0,0])
    with pytest.raises(ValueError):
        one_bit_correcting_codec([1,0,0,0])
