import pytest
from validation.semrepair.evidence_qualified_authority import (
    AuthorityInput, authorize_pre_dispatch, decide_commit
)

def base(**overrides):
    values=dict(
        case="qualified",
        measurement_certificate_id="measurement:1",
        measurement_qualified=True,
        repair_certificate_id="repair:1",
        repair_verified=True,
        interaction_certificate_id="interaction:1",
        interaction_authorized=True,
        execution_evidence_id="execution:1",
        execution_non_regressive=True,
        effect_policy_id="effect-policy:1",
    )
    values.update(overrides)
    return AuthorityInput(**values)

def test_lerobot_exact_roundtrip_cannot_authorize_nonidentifying_semantics():
    d=authorize_pre_dispatch(base(
        case="lerobot-roundtrip-collision",
        measurement_certificate_id="identifiability:6538e1d6",
        measurement_qualified=False,
    ))
    assert not d.authorized
    assert d.stage=="measurement_qualification"

def test_maniskill_semantically_clean_but_execution_regressive_repair_is_denied():
    d=authorize_pre_dispatch(base(
        case="maniskill-clean-adapter-v2",
        execution_evidence_id="workflow:37407944746",
        execution_non_regressive=False,
    ))
    assert not d.authorized
    assert d.stage=="execution_effect"

def test_partial_compensating_bundle_is_denied_before_execution_gate():
    d=authorize_pre_dispatch(base(
        case="maniskill-converter-only",
        interaction_certificate_id="interaction:paired-semantic-v2",
        interaction_authorized=False,
    ))
    assert not d.authorized
    assert d.stage=="repair_interaction"

def test_authorized_dispatch_still_requires_post_effect_evidence_to_commit():
    d=authorize_pre_dispatch(base())
    assert d.authorized
    assert decide_commit(d,post_effect_evidence_id=None,effect_observed=None).state=="ambiguous"
    assert decide_commit(d,post_effect_evidence_id="receipt:2",effect_observed=False).state=="aborted"
    assert decide_commit(d,post_effect_evidence_id="receipt:3",effect_observed=True).state=="committed"

def test_missing_identity_fails_closed():
    with pytest.raises(ValueError,match="measurement_certificate_id"):
        authorize_pre_dispatch(base(measurement_certificate_id=""))
