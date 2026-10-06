from research.eprc.local_model_admissibility import (
    LocalModelAdmissibility,
    classify_local_model_admissibility,
)


def test_all_four_admissibility_quadrants_are_distinct():
    cases = {
        (True, True): LocalModelAdmissibility.ADMISSIBLE_FIRST_ORDER,
        (False, True): LocalModelAdmissibility.INFORMATION_LIMITED,
        (True, False): LocalModelAdmissibility.LOCALITY_LIMITED,
        (False, False): LocalModelAdmissibility.REJECT_LOCAL_MODEL,
    }
    for (stable, local), expected in cases.items():
        out = classify_local_model_admissibility(
            dec_stable=stable, locality_contracting=local
        )
        assert out.state is expected


def test_only_both_pass_authorizes_repair_certificate():
    for stable in (False, True):
        for local in (False, True):
            out = classify_local_model_admissibility(
                dec_stable=stable, locality_contracting=local
            )
            assert out.repair_certificate_authorized is (stable and local)


def test_information_limited_is_only_case_that_authorizes_same_scale_queries():
    out = classify_local_model_admissibility(
        dec_stable=False, locality_contracting=True
    )
    assert out.same_scale_queries_authorized

    for case in [(True, True), (True, False), (False, False)]:
        assert not classify_local_model_admissibility(
            dec_stable=case[0], locality_contracting=case[1]
        ).same_scale_queries_authorized
