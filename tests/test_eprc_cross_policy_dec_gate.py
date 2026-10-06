import numpy as np

from research.eprc.cross_policy_dec_gate import (
    PairScores,
    PolicyCase,
    ProspectiveGate,
    auc_for_distance,
    ResponseProspectiveGate,
    evaluate_gate,
    evaluate_response_gate,
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
        support = 0.40 + 0.05 * (i % 4)
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


def test_cross_policy_gate_cancels_action_and_support_chart_changes():
    j_phys = np.array([[1.0, 0.2], [0.4, 1.2]])
    dh = np.array([[2.0, 0.3], [0.0, 0.5]])
    dg = np.array([[0.4, 0.1], [0.0, 1.8]])

    a = PolicyCase(
        raw_action_jacobian=j_phys,
        action_to_physical_jacobian=np.eye(2),
        support_ids=("cube_a", "cube_b"),
        static_representation="absolute/world-support",
        coarse_contract_class="RELATIONAL_INVARIANT",
        runtime_decision="REPAIR",
        physical_support_to_support_chart_jacobian=np.eye(2),
    )
    b = PolicyCase(
        raw_action_jacobian=dh @ j_phys @ np.linalg.inv(dg),
        action_to_physical_jacobian=np.linalg.inv(dh),
        support_ids=("cube_a", "cube_b"),
        static_representation="relative/object-support",
        coarse_contract_class="RELATIONAL_INVARIANT",
        runtime_decision="REPAIR",
        physical_support_to_support_chart_jacobian=dg,
    )

    scores = score_pair(a, b)
    assert scores.dec_distance < 1e-10
    assert scores.raw_distance > 0.1
    assert scores.decisions_agree


def test_primary_response_gate_uses_external_heldout_response_not_runtime_decision():
    pairs = []
    for i in range(24):
        target = 0.03 * i
        # DEC tracks the independently supplied held-out response distance.
        dec = target + 0.001 * (i % 3)
        # Frozen baselines are deliberately weak/non-monotone.
        raw = 0.4 + 0.1 * (i % 5)
        support = float(i % 2)
        static = float(i % 3 == 0)
        coarse = float(i % 4 == 0)
        pairs.append(
            PairScores(
                dec_distance=dec,
                raw_distance=raw,
                support_distance=support,
                static_metadata_distance=static,
                coarse_class_distance=coarse,
                decisions_agree=(i % 2 == 0),
                heldout_response_distance=target,
            )
        )

    result = evaluate_response_gate(
        pairs,
        gate=ResponseProspectiveGate(
            min_pairs=20,
            min_dec_spearman=0.50,
            required_spearman_margin=0.10,
        ),
    )
    assert result.passed
    assert result.dec_spearman > 0.99


def test_decision_agreement_can_be_arbitrary_without_changing_response_gate_target():
    pairs = [
        PairScores(
            dec_distance=float(i),
            raw_distance=float(20 - i),
            support_distance=float(i % 2),
            static_metadata_distance=float(i % 3 == 0),
            coarse_class_distance=float(i % 4 == 0),
            decisions_agree=False,
            heldout_response_distance=float(i),
        )
        for i in range(20)
    ]
    result = evaluate_response_gate(pairs)
    assert result.passed
    assert result.dec_spearman == 1.0


def test_response_gate_rejects_missing_external_evidence():
    pairs = [
        PairScores(0.1, 0.2, 0.0, 0.0, 0.0, True)
        for _ in range(20)
    ]
    result = evaluate_response_gate(pairs)
    assert not result.passed
    assert "held-out physical response evidence" in result.reason
