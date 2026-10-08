import copy
import math

import numpy as np
import pytest

from research.crg_core.paired_state_conformal_transfer import (
    ScreenDecision,
    audit_heldout_state,
    fit_state_block_envelope,
    screen_new_state_pair,
)

PROTOCOL = "1" * 64


def _pair(heldout, error=0.0):
    return {
        "heldout_id": heldout,
        "map_a": [[1.0]],
        "map_b": [[0.0]],
        "support_delta": [1.0],
        "observed_response_a": [1.0 + error],
        "observed_response_b": [0.0],
    }


def _state(i, error=0.01):
    return {
        "state_id": f"fresh-{i}",
        "pairs": [_pair("A", error), _pair("B", error/2)],
    }


def _calibration():
    return [_state(i, i/100) for i in range(1, 10)]


def _screen(env, tolerance, *, state_id="unseen-100", valid=True):
    return screen_new_state_pair(
        env, test_state_id=state_id, pair=_pair("A"),
        trusted_response_tolerance=tolerance,
        local_model_a_admissible=valid,
        local_model_b_admissible=valid,
        support_admissible=True,
        controller_authority_admissible=True,
    )


def test_nine_state_clusters_are_required_for_90_percent_marginal_coverage():
    env=fit_state_block_envelope(_calibration(),alpha=0.1,source_protocol_digest=PROTOCOL)
    assert env.n_calibration_states==9
    assert env.k_order_statistic==9
    assert np.isclose(env.radius,0.09,atol=1e-12)
    assert len(env.calibration_digest)==64
    assert "marginal" in env.coverage_interpretation.lower()
    assert fit_state_block_envelope(_calibration(),alpha=0.1,source_protocol_digest=PROTOCOL)==env
    with pytest.raises(ValueError,match="insufficient"):
        fit_state_block_envelope(_calibration()[:8],alpha=0.1,source_protocol_digest=PROTOCOL)


def test_runtime_decision_changes_action_authorization_with_uncertainty():
    env=fit_state_block_envelope(_calibration(),source_protocol_digest=PROTOCOL)
    similar=_screen(env,1.1)
    assert similar.decision is ScreenDecision.STATISTICALLY_SIMILAR
    assert np.isclose(similar.interval_upper,1.09)
    assert not similar.deterministically_certified
    assert not similar.externally_verified
    distinct=_screen(env,0.9)
    assert distinct.decision is ScreenDecision.STATISTICALLY_DISTINCT
    uncertain=_screen(env,1.03)
    assert uncertain.decision is ScreenDecision.ABSTAIN_UNCERTAIN
    assert uncertain.interval_lower < uncertain.tolerance < uncertain.interval_upper


def test_model_invalidity_and_state_leakage_fail_closed():
    env=fit_state_block_envelope(_calibration(),source_protocol_digest=PROTOCOL)
    assert _screen(env,1.1,valid=False).decision is ScreenDecision.REJECT_INVALID_LOCAL_MODEL
    with pytest.raises(ValueError,match="leakage"):
        _screen(env,1.1,state_id="fresh-4")
    with pytest.raises(ValueError,match="response tolerance"):
        _screen(env,float("nan"))
    with pytest.raises(ValueError,match="nonfinite"):
        screen_new_state_pair(
            env,test_state_id="other",pair=_pair("A")|{"map_a":[[float("nan")]]},
            trusted_response_tolerance=1.1,
            local_model_a_admissible=True,local_model_b_admissible=True,
            support_admissible=True,controller_authority_admissible=True,
        )


def test_entire_state_a_b_pair_is_the_statistical_unit():
    env=fit_state_block_envelope(_calibration(),source_protocol_digest=PROTOCOL)
    prediction=[_screen(env,1.1),_screen(env,1.1)]
    good=audit_heldout_state(env,_state(100,0.02),prediction)
    assert good["state_block_covered"]
    assert good["false_authorizations"]==0
    assert good["denominator_observations"]==2
    assert good["denominator_state_clusters"]==1
    assert not good["external_validation"]
    # A posthoc failure must NOT be filtered merely because it is inconvenient.
    bad=audit_heldout_state(env,_state(101,0.3),prediction)
    assert not bad["state_block_covered"]
    assert bad["false_authorizations"]==2
    with pytest.raises(ValueError,match="overlap"):
        audit_heldout_state(env,_state(4,0.02),prediction)


def test_no_dropped_or_reordered_heldouts_or_duplicate_calibration_ids():
    state=_calibration()
    state[2]["pairs"].pop()
    with pytest.raises(ValueError,match="exactly A and B"):
        fit_state_block_envelope(state,source_protocol_digest=PROTOCOL)
    state=_calibration()
    state[0]["pairs"]=[state[0]["pairs"][1],state[0]["pairs"][0]]
    with pytest.raises(ValueError,match="A then B"):
        fit_state_block_envelope(state,source_protocol_digest=PROTOCOL)
    state=_calibration()
    state[3]["state_id"]=state[4]["state_id"]
    with pytest.raises(ValueError,match="duplicate"):
        fit_state_block_envelope(state,source_protocol_digest=PROTOCOL)


def test_untrusted_metadata_invalid_digest_is_rejected():
    with pytest.raises(ValueError,match="nonhex"):
        fit_state_block_envelope(_calibration(),source_protocol_digest="z"*64)
    with pytest.raises(ValueError,match="immutable"):
        fit_state_block_envelope(_calibration(),source_protocol_digest="main")
