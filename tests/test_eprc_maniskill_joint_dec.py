import numpy as np

from research.eprc.maniskill_joint_dec_assay import (
    JointControllerChart,
    MANISKILL_CONVERSION_PATH,
    MANISKILL_SOURCE_SHA,
    physical_contract_for_chart,
    source_anchored_contract_agreement,
)
from research.eprc.contract_signature import contract_signature, signature_distance


def _fixture():
    base_target = np.array([0.2, -0.3, 0.7, -1.0])
    support_to_target = np.array(
        [
            [1.0, 0.2],
            [0.0, 0.7],
            [0.4, 0.0],
            [0.1, -0.3],
        ]
    )
    current = np.array([0.1, -0.1, 0.4, -0.8])
    previous_target = np.array([0.15, -0.25, 0.5, -0.9])
    scale = np.array([0.05, 0.20, 0.10, 0.40])

    charts = [
        JointControllerChart("absolute", np.ones(4), np.zeros(4)),
        JointControllerChart("current_delta", scale, current),
        JointControllerChart("target_delta", scale, previous_target),
    ]
    return base_target, support_to_target, charts


def test_source_anchor_is_explicit_and_immutable():
    assert MANISKILL_SOURCE_SHA == "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
    assert MANISKILL_CONVERSION_PATH.endswith("trajectory/utils/actions/conversion.py")


def test_raw_action_contracts_differ_across_real_maniskill_charts():
    base_target, support_to_target, charts = _fixture()

    raw = [
        physical_contract_for_chart(c, base_target, support_to_target)[0]
        for c in charts
    ]
    d = signature_distance(contract_signature(raw[0]), contract_signature(raw[1]))
    assert d > 0.1


def test_semantic_lifting_recovers_same_physical_contract():
    base_target, support_to_target, charts = _fixture()

    physical = [
        physical_contract_for_chart(c, base_target, support_to_target)[1]
        for c in charts
    ]
    for j in physical[1:]:
        assert np.allclose(j, physical[0], atol=1e-8)

    ok, distances = source_anchored_contract_agreement(
        charts, base_target, support_to_target
    )
    assert ok
    assert max(distances) < 1e-8


def test_anchor_changes_action_values_but_not_local_physical_contract():
    base_target, support_to_target, charts = _fixture()

    a = charts[1].encode_target(base_target)
    b = charts[2].encode_target(base_target)
    assert not np.allclose(a, b)

    _, j_phys_a, sig_a = physical_contract_for_chart(
        charts[1], base_target, support_to_target
    )
    _, j_phys_b, sig_b = physical_contract_for_chart(
        charts[2], base_target, support_to_target
    )

    assert np.allclose(j_phys_a, j_phys_b)
    assert signature_distance(sig_a, sig_b) < 1e-8
