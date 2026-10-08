import numpy as np
from research.crg_core.request_conditional_transfer import (
    TransferDecision, certify_response_transfer,
)


def decision(A, B, *, h=1.0, ea=0.05, eb=0.05, ra=0.0, rb=0.0,
             tau=0.2, valid=True, support=True, authority=True):
    return certify_response_transfer(
        np.array([[A]], dtype=float), np.array([[B]], dtype=float),
        np.array([h], dtype=float),
        operator_bound_a=ea, operator_bound_b=eb,
        locality_remainder_bound_a=ra, locality_remainder_bound_b=rb,
        trusted_response_tolerance=tau,
        model_a_admissible=valid, model_b_admissible=valid,
        support_admissible=support,
        controller_authority_admissible=authority,
    )


def test_small_disagreement_is_certified_only_with_complete_bounds():
    result=decision(1.0,1.05,tau=0.2)
    assert result.decision is TransferDecision.CERTIFIED_SIMILAR_RESPONSE
    assert result.response_disagreement_lower == 0
    assert np.isclose(result.response_disagreement_upper,0.15)
    assert result.conditional_on_physical_assumptions
    assert not result.external_empirical_verification


def test_certified_distinct_response_versus_overlap():
    assert decision(1.0,2.0,tau=0.2).decision is TransferDecision.CERTIFIED_DISTINCT_RESPONSE
    assert decision(1.0,2.0,tau=0.2,ea=0.5,eb=0.5).decision is TransferDecision.INCONCLUSIVE


def test_increasing_uncertainty_never_licenses_a_unsupported_transfer():
    assert decision(1.0,1.05,tau=0.2,ea=0.05).decision is TransferDecision.CERTIFIED_SIMILAR_RESPONSE
    assert decision(1.0,1.05,tau=0.2,ea=0.2).decision is TransferDecision.INCONCLUSIVE


def test_absent_identifiability_or_authority_is_fail_closed():
    for opts in (dict(valid=False),dict(support=False),dict(authority=False)):
        out=decision(1.0,1.0,**opts)
        assert out.decision is TransferDecision.UNSUPPORTED_LOCAL_MODEL
        assert out.response_disagreement_upper is None


def test_locality_remainder_must_not_be_omitted():
    assert decision(1.0,1.0,tau=0.2,ra=0.3).decision is TransferDecision.INCONCLUSIVE


def test_nonfinite_or_mismatched_maps_never_produce_certificate():
    assert decision(np.nan,1.0).decision is TransferDecision.UNSUPPORTED_LOCAL_MODEL
    assert decision(1.0,1.0,ea=float("nan")).decision is TransferDecision.UNSUPPORTED_LOCAL_MODEL
    out=certify_response_transfer(
        np.eye(2),np.eye(3),np.ones(2),
        operator_bound_a=0,operator_bound_b=0,
        locality_remainder_bound_a=0,locality_remainder_bound_b=0,
        trusted_response_tolerance=0.1,
        model_a_admissible=True,model_b_admissible=True,
        support_admissible=True,controller_authority_admissible=True,
    )
    assert out.decision is TransferDecision.UNSUPPORTED_LOCAL_MODEL


def test_unit_dependent_directional_transfer_not_global_jacobian_similarity():
    A=np.diag([1.0,9.0])
    B=np.diag([1.0,1.0])
    def check(h):
        return certify_response_transfer(
            A,B,np.array(h,dtype=float),
            operator_bound_a=0.0,operator_bound_b=0.0,
            locality_remainder_bound_a=0.0,locality_remainder_bound_b=0.0,
            trusted_response_tolerance=0.1,
            model_a_admissible=True,model_b_admissible=True,
            support_admissible=True,controller_authority_admissible=True,
        )
    assert check([1,0]).decision is TransferDecision.CERTIFIED_SIMILAR_RESPONSE
    assert check([0,1]).decision is TransferDecision.CERTIFIED_DISTINCT_RESPONSE
