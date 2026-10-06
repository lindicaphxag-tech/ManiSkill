from validation.semrepair.semantic_identifiability_certificate import (
    HypothesisEvidence,
    qualify_identifiability,
)


def _h(name, obs, sem):
    return HypothesisEvidence(name, tuple(obs), tuple(sem), f"evidence:{name}")


def test_observational_collision_forces_fail():
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


def test_external_anchor_can_upgrade_collision_free_channel():
    report = qualify_identifiability(
        case="named state/action correspondence",
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
    assert report["status"] == "pass"


def test_anchor_never_overrides_observed_collision():
    report = qualify_identifiability(
        case="contradictory evidence",
        hypotheses=(
            _h("a", [0.0], [0.0]),
            _h("b", [0.0], [10.0]),
        ),
        observable_tolerance=0.0,
        semantic_separation=1.0,
        external_anchor={
            "kind": "repository_native_semantic_oracle",
            "evidence_id": "oracle:claimed",
        },
    )
    assert report["status"] == "fail"
