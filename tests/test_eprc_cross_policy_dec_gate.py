import numpy as np

from research.eprc.cross_policy_dec_gate import (
    PairScores,
    PolicyCase,
    ProspectiveGate,
    auc_for_distance,
    evaluate_gate,
    score_pair,
)


def test_semantic_lifting_beats_raw_distance_on_reparameterized_equivalent_pair():
    j_phys = np.array([[1.0, 0.0], [0.2, 1.0]])
    r = np.array([[3.0, 0.5], [0.0, 0.4]])

    a = PolicyCase(
        raw_action_jacobian=j_phys,
        action_to_physical_jacobian=np.eye(2),
        support_ids=("cube_a", "cube_b"),
        static_representation="absolute",
        coarse_contract_class="RELATIONAL_INVARIANT",
        runtime_decision="REPAIR",
    )
    b = PolicyCase(
        raw_action_jacobian=r @ j_phys,
        action_to_physical_jacobian=np.linalg.inv(r),
        support_ids=("cube_a", "cube_b"),
        static_representation="relative",
        coarse_contract_class="RELATIONAL_INVARIANT",
        runtime_decision="REPAIR",
    )

    scores = score_pair(a, b)
    assert scores.dec_distance < 1e-10
    assert scores.raw_distance > 0.1
    assert scores.decisions_agree


def test_auc_for_distance_rewards_small_distance_for_agreement():
    auc = auc_for_distance(
        [0.1, 0.2, 0.8, 0.9],
        [True, True, False, False],
    )
    assert auc == 1.0


def test_gate_is_frozen_and_requires_margin_over_all_baselines():
    pairs = []
    for i in range(24):
        agree = i < 12
        dec = 0.1 + 0.01 * i if agree else 0.8 + 0.01 * i
        raw = 0.45 + 0.01 * (i % 4)
        support = 0.4 if agree else 0.6
        static = 0.0 if i % 3 else 1.0
        coarse = 0.0 if i % 4 else 1.0
        pairs.append(
            PairScores(
                dec_distance=dec,
                raw_distance=raw,
                support_distance=support,
                static_metadata_distance=static,
                coarse_class_distance=coarse,
                decisions_agree=agree,
            )
        )

    result = evaluate_gate(
        pairs,
        gate=ProspectiveGate(
            min_pairs=20,
            min_dec_auc=0.70,
            required_auc_margin=0.05,
        ),
    )
    assert result.passed
    assert result.dec_auc == 1.0
    assert result.dec_auc >= max(
        result.raw_auc,
        result.support_auc,
        result.static_metadata_auc,
        result.coarse_class_auc,
    ) + 0.05


def test_gate_refuses_underpowered_evidence():
    one = PairScores(0.0, 0.0, 0.0, 0.0, 0.0, True)
    result = evaluate_gate([one] * 5)
    assert not result.passed
    assert "insufficient" in result.reason
