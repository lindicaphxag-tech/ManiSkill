import pytest

from research.semantic_invariants.embodied_semantic_instrumentation import (
    SemanticTransportScenario,
    plan_minimum_semantic_instrumentation,
)
from research.semantic_invariants.embodied_semantic_transport import (
    MonomialSemanticTransport,
    SemanticTransportFactor,
)


def _factor(name, transport, evidence):
    return SemanticTransportFactor(name, transport, evidence)


def _scenario(name, transports, evidence):
    return SemanticTransportScenario(
        name=name,
        factors=tuple(
            _factor(f"f{index}", transport, f"{evidence}/f{index}")
            for index, transport in enumerate(transports)
        ),
        evidence_id=evidence,
    )


def test_double_swap_requires_one_internal_tap():
    identity = MonomialSemanticTransport.identity(2)
    swap = MonomialSemanticTransport((1, 0), (1.0, 1.0))

    reference = _scenario("reference", (identity, identity), "ref")
    hidden = _scenario("double-swap", (swap, swap), "fault")

    cert = plan_minimum_semantic_instrumentation(
        reference=reference,
        candidates=(hidden,),
    )

    assert cert.externally_distinguishable == ()
    assert cert.hidden_hypothesis_count == 1
    assert cert.minimum_internal_taps == ("f0",)

    item = cert.externally_hidden[0]
    assert item.scenario == "double-swap"
    assert item.distinguishing_taps == ("f0",)
    assert item.witness.after_factor == "f0"
    assert item.witness.residual_linf == pytest.approx(1.0)


def test_two_disjoint_hidden_faults_require_two_taps():
    identity = MonomialSemanticTransport.identity(2)
    swap = MonomialSemanticTransport((1, 0), (1.0, 1.0))

    reference = _scenario(
        "reference",
        (identity, identity, identity),
        "ref",
    )
    early = _scenario(
        "early-cancel",
        (swap, swap, identity),
        "early",
    )
    late = _scenario(
        "late-cancel",
        (identity, swap, swap),
        "late",
    )

    cert = plan_minimum_semantic_instrumentation(
        reference=reference,
        candidates=(early, late),
    )

    assert cert.hidden_hypothesis_count == 2
    assert cert.minimum_internal_taps == ("f0", "f1")
    by_name = {item.scenario: item for item in cert.externally_hidden}
    assert by_name["early-cancel"].distinguishing_taps == ("f0",)
    assert by_name["late-cancel"].distinguishing_taps == ("f1",)


def test_one_tap_can_cover_multiple_hidden_hypotheses():
    identity = MonomialSemanticTransport.identity(2)
    swap = MonomialSemanticTransport((1, 0), (1.0, 1.0))

    reference = _scenario(
        "reference",
        (identity, identity, identity),
        "ref",
    )
    first = _scenario(
        "cancel-at-second",
        (swap, swap, identity),
        "s1",
    )
    second = _scenario(
        "cancel-at-third",
        (swap, identity, swap),
        "s2",
    )

    cert = plan_minimum_semantic_instrumentation(
        reference=reference,
        candidates=(first, second),
    )

    assert cert.minimum_internal_taps == ("f0",)
    assert {
        item.scenario: item.distinguishing_taps
        for item in cert.externally_hidden
    } == {
        "cancel-at-second": ("f0",),
        "cancel-at-third": ("f0", "f1"),
    }


def test_external_difference_needs_no_internal_instrumentation():
    identity = MonomialSemanticTransport.identity(2)
    swap = MonomialSemanticTransport((1, 0), (1.0, 1.0))

    reference = _scenario("reference", (identity, identity), "ref")
    visible = _scenario("visible", (swap, identity), "visible")

    cert = plan_minimum_semantic_instrumentation(
        reference=reference,
        candidates=(visible,),
    )

    assert cert.externally_distinguishable == ("visible",)
    assert cert.externally_hidden == ()
    assert cert.minimum_internal_taps == ()


def test_reference_chain_may_contain_legitimate_nonidentity_conversion():
    up = MonomialSemanticTransport((0,), (1000.0,))
    down = MonomialSemanticTransport((0,), (0.001,))
    identity = MonomialSemanticTransport.identity(1)

    # Both chains are externally identity.  Only the reference performs a
    # legitimate mm<->m conversion internally, so one internal tap is necessary
    # to distinguish the candidate that silently omits both conversions.
    reference = _scenario("reference", (up, down), "ref-mm-m")
    omitted = _scenario("omitted-unit-conversion", (identity, identity), "fault")

    cert = plan_minimum_semantic_instrumentation(
        reference=reference,
        candidates=(omitted,),
        atol=1e-12,
    )

    assert cert.minimum_internal_taps == ("f0",)
    witness = cert.externally_hidden[0].witness
    assert witness.reference_output == pytest.approx((1000.0,))
    assert witness.candidate_output == pytest.approx((1.0,))


def test_semantically_equivalent_candidate_is_not_mislabeled_hidden():
    identity = MonomialSemanticTransport.identity(2)
    reference = _scenario("reference", (identity, identity), "ref")
    equivalent = _scenario("equivalent", (identity, identity), "same")

    cert = plan_minimum_semantic_instrumentation(
        reference=reference,
        candidates=(equivalent,),
    )

    assert cert.hidden_hypothesis_count == 0
    assert cert.externally_distinguishable == ()
    assert cert.minimum_internal_taps == ()


def test_digest_binds_candidate_evidence_identity():
    identity = MonomialSemanticTransport.identity(2)
    swap = MonomialSemanticTransport((1, 0), (1.0, 1.0))
    reference = _scenario("reference", (identity, identity), "ref")

    first = _scenario("fault", (swap, swap), "evidence-v1")
    second = _scenario("fault", (swap, swap), "evidence-v2")

    a = plan_minimum_semantic_instrumentation(
        reference=reference,
        candidates=(first,),
    )
    b = plan_minimum_semantic_instrumentation(
        reference=reference,
        candidates=(second,),
    )

    assert a.minimum_internal_taps == b.minimum_internal_taps == ("f0",)
    assert a.digest != b.digest


def test_factor_name_or_order_drift_fails_closed():
    identity = MonomialSemanticTransport.identity(2)
    reference = _scenario("reference", (identity, identity), "ref")

    bad = SemanticTransportScenario(
        name="bad",
        factors=(
            _factor("other", identity, "bad/0"),
            _factor("f1", identity, "bad/1"),
        ),
        evidence_id="bad",
    )

    with pytest.raises(ValueError, match="names/order"):
        plan_minimum_semantic_instrumentation(
            reference=reference,
            candidates=(bad,),
        )
