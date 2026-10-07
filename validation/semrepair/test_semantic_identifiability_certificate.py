from validation.semrepair.semantic_identifiability_certificate import (
    HypothesisEvidence,
    qualify_identifiability,
)


def _h(name, obs, sem):
    return HypothesisEvidence(name, tuple(obs), tuple(sem), f"evidence:{name}")


def test_observational_collision_forces_fail_without_anchor():
    report = qualify_identifiability(
        case="paired wrong inverse hides wrong forward mapping",
        hypotheses=(
            _h("correct-anchor", [0.0], [1.0, 2.0]),
            _h("wrong-anchor", [0.0], [20.0, 60.0]),
        ),
        observable_tolerance=0.0,
        semantic_separation=1.0,
    )
    assert report["status"] == "fail"
    assert report["authority"] == "reject_until_external_semantic_anchor"
    assert len(report["collisions"]) == 1


def test_no_finite_collision_is_not_automatic_pass():
    report = qualify_identifiability(
        case="finite sample only",
        hypotheses=(
            _h("a", [0.0], [0.0]),
            _h("b", [1.0], [1.0]),
        ),
        observable_tolerance=0.0,
        semantic_separation=0.5,
    )
    assert report["status"] == "undetermined"
    assert not report["collisions"]


def test_external_anchor_must_carry_hypothesis_observables():
    try:
        qualify_identifiability(
            case="named map without evidence values",
            hypotheses=(
                _h("a", [0.0], [0.0]),
                _h("b", [1.0], [1.0]),
            ),
            observable_tolerance=0.0,
            semantic_separation=0.5,
            external_anchor={
                "kind": "explicit_named_index_map",
                "evidence_id": "host-spec:joint-action-map@sha256:abc",
            },
        )
    except ValueError as exc:
        assert "hypothesis_observables" in str(exc)
    else:
        raise AssertionError("anchor without observations must not qualify")


def test_external_anchor_can_resolve_primary_collision():
    report = qualify_identifiability(
        case="named state/action correspondence",
        hypotheses=(
            _h("correct-anchor", [0.0], [1.0, 2.0]),
            _h("wrong-anchor", [0.0], [20.0, 60.0]),
        ),
        observable_tolerance=0.0,
        semantic_separation=1.0,
        external_anchor={
            "kind": "explicit_named_index_map",
            "evidence_id": "host-spec:joint-action-map@sha256:abc",
            "tolerance": 0.0,
            "hypothesis_observables": {
                "correct-anchor": [0.0],
                "wrong-anchor": [1.0],
            },
        },
    )
    assert report["status"] == "pass"
    assert report["authority"] == "identifiability_gate_pass"
    assert report["collisions"]
    assert not report["unresolved_pairs"]


def test_anchor_that_preserves_collision_fails():
    report = qualify_identifiability(
        case="anchor is non-identifying too",
        hypotheses=(
            _h("a", [0.0], [0.0]),
            _h("b", [0.0], [10.0]),
        ),
        observable_tolerance=0.0,
        semantic_separation=1.0,
        external_anchor={
            "kind": "repository_native_semantic_oracle",
            "evidence_id": "oracle:non-identifying",
            "tolerance": 0.0,
            "hypothesis_observables": {
                "a": [7.0],
                "b": [7.0],
            },
        },
    )
    assert report["status"] == "fail"
    assert report["authority"] == "reject_until_stronger_semantic_anchor"
    assert len(report["unresolved_pairs"]) == 1


def test_anchor_must_cover_exact_hypothesis_set():
    try:
        qualify_identifiability(
            case="partial anchor",
            hypotheses=(
                _h("a", [0.0], [0.0]),
                _h("b", [0.0], [10.0]),
            ),
            observable_tolerance=0.0,
            semantic_separation=1.0,
            external_anchor={
                "kind": "explicit_named_index_map",
                "evidence_id": "map:partial",
                "hypothesis_observables": {"a": [0.0]},
            },
        )
    except ValueError as exc:
        assert "coverage mismatch" in str(exc)
    else:
        raise AssertionError("partial anchor coverage must fail")
