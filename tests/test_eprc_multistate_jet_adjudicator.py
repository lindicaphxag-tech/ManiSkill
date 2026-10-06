from research.eprc.multistate_jet_adjudicator import (
    FROZEN_SEEDS,
    adjudicate_records,
)


def _record(seed, *, first=False, jet=False, stable=True):
    return {
        "environment_reset_seed":seed,
        "protocol_id":"frozen-protocol",
        "locality_refinement":{
            "status":"executed_prospective_protocol",
            "contracting":first,
            "response_jet_diagnostic":{
                "supports_model_order_upgrade":jet,
            },
        },
        "dec":{"replicate_stability_certified":stable},
    }


def test_zero_rescues_drops_jet():
    records=[_record(s,first=False,jet=False) for s in FROZEN_SEEDS]
    out=adjudicate_records(records)
    assert out.jet_rescue_count==0
    assert out.promotion_decision=="DROP_JET_FROM_FLAGSHIP"


def test_one_rescue_keeps_secondary_only():
    records=[_record(s,first=False,jet=(i==0)) for i,s in enumerate(FROZEN_SEEDS)]
    out=adjudicate_records(records)
    assert out.jet_rescue_count==1
    assert out.promotion_decision=="KEEP_AS_SECONDARY_MECHANISM"


def test_three_rescues_promote_broader_test():
    records=[_record(s,first=False,jet=(i<3)) for i,s in enumerate(FROZEN_SEEDS)]
    out=adjudicate_records(records)
    assert out.jet_rescue_count==3
    assert out.promotion_decision=="PROMOTE_TO_BROADER_PROSPECTIVE_TEST"


def test_first_order_success_does_not_count_as_jet_rescue():
    records=[
        _record(FROZEN_SEEDS[0],first=True,jet=True),
        *[_record(s,first=False,jet=False) for s in FROZEN_SEEDS[1:]],
    ]
    out=adjudicate_records(records)
    assert out.jet_upgrade_count==1
    assert out.jet_rescue_count==0


def test_dec_stability_is_reported_not_hidden():
    records=[_record(s,stable=(i!=2)) for i,s in enumerate(FROZEN_SEEDS)]
    out=adjudicate_records(records)
    assert not out.all_dec_stable
