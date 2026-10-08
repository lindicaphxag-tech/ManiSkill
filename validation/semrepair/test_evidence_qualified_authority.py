import pytest

from validation.semrepair.evidence_qualified_authority import (
    EvidenceBundle,
    authorize_pre_dispatch,
    decide_commit,
    seal_certificate,
)


CTX_A = "a" * 64
CTX_B = "b" * 64


def cert(kind, *, case="case-a", ctx=CTX_A, **fields):
    base = {
        "certificate_type": kind,
        "case_id": case,
        "context_digest": ctx,
        "issuer_id": f"issuer/{kind}@v1",
    }
    base.update(fields)
    return seal_certificate(base)


def good_bundle(**overrides):
    values = dict(
        case_id="case-a",
        context_digest=CTX_A,
        effect_policy_id="effect-policy:v1",
        measurement_certificate=cert(
            "measurement",
            measurement_qualified=True,
            decision="measurement_qualified",
        ),
        repair_certificate=cert("repair", status="verified"),
        interaction_certificate=cert("interaction", authorized=True),
        execution_certificate=cert("execution", non_regressive=True),
    )
    values.update(overrides)
    return EvidenceBundle(**values)


def test_nonidentifying_measurement_stops_before_later_gates():
    measurement = cert(
        "measurement",
        measurement_qualified=False,
        decision="non_identifying_measurement",
    )
    d = authorize_pre_dispatch(
        EvidenceBundle(
            case_id="case-a",
            context_digest=CTX_A,
            effect_policy_id="effect-policy:v1",
            measurement_certificate=measurement,
        )
    )
    assert not d.authorized
    assert d.stage == "measurement_qualification"


def test_missing_repair_certificate_fails_closed():
    b = good_bundle(repair_certificate=None)
    d = authorize_pre_dispatch(b)
    assert not d.authorized
    assert d.stage == "local_repair_verification"


def test_partial_compensating_bundle_is_denied():
    b = good_bundle(
        interaction_certificate=cert("interaction", authorized=False)
    )
    d = authorize_pre_dispatch(b)
    assert not d.authorized
    assert d.stage == "repair_interaction"


def test_execution_regression_is_denied():
    b = good_bundle(
        execution_certificate=cert("execution", non_regressive=False)
    )
    d = authorize_pre_dispatch(b)
    assert not d.authorized
    assert d.stage == "execution_effect"


def test_all_bound_certificates_can_authorize_dispatch():
    d = authorize_pre_dispatch(good_bundle())
    assert d.authorized
    assert d.stage == "dispatch_authorized"


def test_tampering_after_certificate_sealing_is_rejected():
    measurement = cert(
        "measurement",
        measurement_qualified=False,
        decision="non_identifying_measurement",
    )
    measurement["measurement_qualified"] = True
    with pytest.raises(ValueError, match="digest mismatch"):
        authorize_pre_dispatch(
            good_bundle(measurement_certificate=measurement)
        )


def test_cross_context_certificate_splicing_is_rejected():
    alien = cert(
        "repair",
        case="case-b",
        ctx=CTX_B,
        status="verified",
    )
    with pytest.raises(ValueError, match="case_id mismatch|context_digest mismatch"):
        authorize_pre_dispatch(
            good_bundle(repair_certificate=alien)
        )


def test_same_case_but_different_context_is_rejected():
    alien = cert(
        "repair",
        case="case-a",
        ctx=CTX_B,
        status="verified",
    )
    with pytest.raises(ValueError, match="context_digest mismatch"):
        authorize_pre_dispatch(
            good_bundle(repair_certificate=alien)
        )


def test_authorized_dispatch_still_requires_post_effect_certificate():
    d = authorize_pre_dispatch(good_bundle())
    assert d.authorized
    assert decide_commit(d, post_effect_certificate=None).state == "ambiguous"

    negative = cert("post_effect", effect_observed=False)
    assert decide_commit(d, post_effect_certificate=negative).state == "aborted"

    positive = cert("post_effect", effect_observed=True)
    assert decide_commit(d, post_effect_certificate=positive).state == "committed"


def test_post_effect_certificate_from_other_context_is_rejected():
    d = authorize_pre_dispatch(good_bundle())
    alien = cert(
        "post_effect",
        case="case-a",
        ctx=CTX_B,
        effect_observed=True,
    )
    with pytest.raises(ValueError, match="context_digest mismatch"):
        decide_commit(d, post_effect_certificate=alien)
