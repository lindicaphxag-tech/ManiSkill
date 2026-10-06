import numpy as np

from research.eprc.groot_joint_dec_assay import (
    GROOT_CHUNK_PATH,
    GROOT_POSE_PATH,
    GROOT_PROCESSOR_PATH,
    GROOT_SOURCE_SHA,
    GrootJointChart,
    cross_reference_agreement,
    physical_contract,
)


def _fixture():
    base = np.array([0.3, -0.4, 0.1, 0.8])
    response = np.array(
        [
            [0.8, 0.1],
            [0.2, -0.6],
            [0.0, 1.0],
            [0.4, 0.3],
        ]
    )
    charts = [
        GrootJointChart("absolute", np.zeros(4)),
        GrootJointChart("relative", np.array([0.1, -0.2, 0.4, 0.6])),
        GrootJointChart("relative", np.array([-0.5, 0.3, -0.1, 0.2])),
    ]
    return base, response, charts


def test_groot_source_anchor_is_frozen():
    assert GROOT_SOURCE_SHA == "51d4c89f72fda44cbf77285c6a8114b52676b8a1"
    assert GROOT_PROCESSOR_PATH.endswith("state_action_processor.py")
    assert GROOT_POSE_PATH.endswith("pose.py")
    assert GROOT_CHUNK_PATH.endswith("action_chunking.py")


def test_relative_actions_change_values_but_not_local_physical_contract():
    base, response, charts = _fixture()

    a_abs = charts[0].encode_absolute(base)
    a_rel = charts[1].encode_absolute(base)
    assert not np.allclose(a_abs, a_rel)

    _, j_abs, sig_abs = physical_contract(charts[0], base, response)
    _, j_rel, sig_rel = physical_contract(charts[1], base, response)

    assert np.allclose(j_abs, j_rel, atol=1e-8)
    assert sig_abs.rank == sig_rel.rank


def test_reference_state_changes_output_coordinates_not_dec():
    base, response, charts = _fixture()
    assert not np.allclose(
        charts[1].encode_absolute(base),
        charts[2].encode_absolute(base),
    )

    ok, distances = cross_reference_agreement(charts, base, response)
    assert ok
    assert max(distances) < 1e-8


def test_round_trip_matches_groot_issue_490_semantics():
    base, _, charts = _fixture()
    rel = charts[1].encode_absolute(base)
    restored = charts[1].decode_to_absolute(rel)
    assert np.allclose(restored, base)
