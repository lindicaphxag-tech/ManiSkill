"""Independent minimal bounded-corruption selective-confirmation contracts."""
from itertools import product
import math
import numpy as np
import pytest

from research.adversarial_ack_selective_confirmation_physx import (
    CHANNEL, CHANNEL_PROBS, corrupted_message, distance, exact_group,
    exact_receiver_case, build_modes
)
from research.two_ack_so3_native_protocol import HISTORY_ORDER


def toy_worlds(feature_by_history=None, action_by_history=None):
    if feature_by_history is None:
        feature_by_history={h:[0.,0.,0.] for h in HISTORY_ORDER}
    if action_by_history is None:
        action_by_history={h:[float(i),0,0,0,0,0]
                           for i,h in enumerate(HISTORY_ORDER)}
    return {h:{
        "public_relative_rotation_log_rad":feature_by_history[h],
        "source_announced_corrective_native_actions":action_by_history,
    } for h in HISTORY_ORDER}


@pytest.mark.parametrize("history",HISTORY_ORDER)
def test_all_3_receipt_channel_modes_are_exact_and_adversarially_bounded(history):
    seen=set()
    for mode in CHANNEL:
        delivered=corrupted_message(history,mode)
        assert distance(history,delivered)<=1
        seen.add(delivered)
    assert len(seen)==3
    assert sum(CHANNEL_PROBS)==1


def test_single_corrective_action_requires_zero_trusted_reply_bits():
    supports={h:frozenset({(0,0,0)}) for h in HISTORY_ORDER}
    labels={h:2 for h in HISTORY_ORDER}
    for h,r in product(HISTORY_ORDER,repeat=2):
        if distance(h,r)>1:
            continue
        decision=exact_receiver_case(supports,labels,h,r,(0,0,0))
        assert decision["extra_trusted_reply_bits"]==0
        assert not decision["map_wrong"]


def test_sensor_observation_can_avoid_query_even_with_corrupted_ACK():
    supports={h:frozenset({(i,0,0)})
              for i,h in enumerate(HISTORY_ORDER)}
    labels={h:i for i,h in enumerate(HISTORY_ORDER)}
    for i,h in enumerate(HISTORY_ORDER):
        for mode in CHANNEL:
            r=corrupted_message(h,mode)
            out=exact_receiver_case(supports,labels,h,r,(i,0,0))
            assert out["extra_trusted_reply_bits"]==0
            assert out["expected_posterior_map_mode"]==i


def test_full_alias_can_force_two_bit_query_even_after_corrupted_ACK():
    s={h:frozenset({(0,0,0)}) for h in HISTORY_ORDER}
    l={h:i for i,h in enumerate(HISTORY_ORDER)}
    # An observed receipt can be true or a one-bit flipped source: at most
    # three feasible histories, so maximum uncertainty is 3 commands.
    for h in HISTORY_ORDER:
        r=corrupted_message(h,"flip_first_bit")
        a=exact_receiver_case(s,l,h,r,(0,0,0))
        assert a["extra_trusted_reply_bits"]==2
        assert len(a["all_feasible_required_modes"])==3


def test_corrupted_receipt_expected_Bayes_error_is_lower_than_naive():
    w=toy_worlds()
    group=exact_group(w,.04,.004)
    assert group["robust_zero_worst_case_wrong_commands"]
    assert group["expected_extra_reply_bits"]<=2
    assert 0<=group["Bayes_MAP_expected_wrong_correction_fraction_same_observation"]<=1
    assert (
        group["Bayes_MAP_expected_wrong_correction_fraction_same_observation"]
        <=group["naive_ACK_expected_wrong_correction_fraction"]+1e-12
    )


def test_graphless_all_alias_requires_admitted_baseline_query():
    w=toy_worlds()
    g=exact_group(w,.04,.004)
    assert g["expected_extra_reply_bits"]==2
    assert g["expected_extra_bits_saved_vs_full_ACK"]==0


def test_source_candidate_actions_must_not_depend_on_private_truth():
    w=toy_worlds()
    w["10"]["source_announced_corrective_native_actions"]["01"]=[
        99.,0,0,0,0,0
    ]
    with pytest.raises(RuntimeError):
        build_modes(w)


def test_unsupported_corruption_cannot_be_certified():
    supports={h:frozenset({(0,0,0)}) for h in HISTORY_ORDER}
    labels={h:i for i,h in enumerate(HISTORY_ORDER)}
    with pytest.raises(RuntimeError):
        exact_receiver_case(supports,labels,"11","00",(0,0,0))


@pytest.mark.parametrize("seed",range(18))
def test_random_complete_finite_cases_exhaustively_guarantee_safe_actions(seed):
    rng=np.random.default_rng(seed)
    feat={h:rng.uniform(-.05,.05,size=3).tolist()
          for h in HISTORY_ORDER}
    actions={h:[float(rng.integers(0,4)),0,0,0,0,0]
             for h in HISTORY_ORDER}
    g=exact_group(toy_worlds(feat,actions),.015,.004)
    assert g["robust_zero_worst_case_wrong_commands"]
    assert 0<=g["expected_extra_reply_bits"]<=2
    assert g["Bayes_MAP_expected_wrong_correction_fraction_same_observation"] <= (
        g["naive_ACK_expected_wrong_correction_fraction"]+1e-12
    )
