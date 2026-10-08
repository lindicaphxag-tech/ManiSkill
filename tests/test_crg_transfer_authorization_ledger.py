"""Synthetic accounting regressions; not frozen policy experimental evidence."""
import copy

import pytest

from research.crg_core.prospective.transfer_authorization_ledger import (
    adjudicate_transfer_report,
)


def _report():
    rows = [
        (263, [("STATISTICALLY_SIMILAR", 0.1),
               ("STATISTICALLY_SIMILAR", 1.5)]),
        (269, [("STATISTICALLY_DISTINCT", 2.0),
               ("STATISTICALLY_DISTINCT", 0.5)]),
        (271, [("ABSTAIN_UNCERTAIN", 10.0),
               ("REJECT_INVALID_LOCAL_MODEL", 0.0)]),
        (277, [("STATISTICALLY_DISTINCT", 3.0),
               ("STATISTICALLY_SIMILAR", 0.4)]),
    ]
    return {
        "schema": "crg-transfer-conformal-fresh-state-pilot-result-v1",
        "preregistered_test_seeds": [263, 269, 271, 277],
        "n_test_state_clusters": 4,
        "n_dependent_test_pairs": 8,
        "all_states_retained": True,
        "frozen_protocol_sha256": "a" * 64,
        # Old authorisation counter erroneously includes DISTINCT.
        "authorized_requests": 6,
        "test_state_diagnostics": [
            {"seed": seed, "pairs": [
                {"heldout_id": hid, "decision": d, "true_gap": gap}
                for hid, (d, gap) in zip(("A", "B"), pairs, strict=True)
            ]} for seed, pairs in rows
        ],
    }


def test_distinct_is_refusal_not_transfer_authorization():
    result = adjudicate_transfer_report(_report())
    stats = result["statistics"]
    assert stats["transfer_authorized_count"] == 3
    assert stats["distinct_nontransfer_count"] == 3
    assert stats["uncertain_abstentions"] == 1
    assert stats["invalid_model_rejections"] == 1
    assert stats["decisive_screening_count"] == 6
    assert stats["false_transfer_authorization_count"] == 1
    assert stats["false_distinct_rejection_count"] == 1
    assert stats["correct_distinct_nontransfer_count"] == 2
    assert result["transfer_authorization_coverage"] == 3/8
    assert result["decisive_classification_coverage"] == 6/8
    assert result["utility_outcome"] == "NONZERO_ACTUAL_TRANSFER_AUTHORIZATION"


def test_only_distinct_decisions_must_report_zero_actual_transfer_utility():
    raw = _report()
    for state in raw["test_state_diagnostics"]:
        for p in state["pairs"]:
            p["decision"] = "STATISTICALLY_DISTINCT"
    raw["authorized_requests"] = 8
    result = adjudicate_transfer_report(raw)
    assert result["statistics"]["transfer_authorized_count"] == 0
    assert result["statistics"]["distinct_nontransfer_count"] == 8
    assert result["decisive_classification_coverage"] == 1.0
    assert result["transfer_authorization_coverage"] == 0.0
    assert result["utility_outcome"] == "ZERO_UTILITY_NO_TRANSFER"


def test_incomplete_or_reordered_states_and_pairs_fail_closed():
    report = _report()
    report["test_state_diagnostics"].pop()
    with pytest.raises(ValueError, match="four raw"):
        adjudicate_transfer_report(report)
    report = _report()
    report["test_state_diagnostics"][0]["pairs"][0]["heldout_id"] = "B"
    with pytest.raises(ValueError, match="A/B requests"):
        adjudicate_transfer_report(report)
    report = _report()
    report["preregistered_test_seeds"] = [263, 269, 271, 271]
    with pytest.raises(ValueError, match="split"):
        adjudicate_transfer_report(report)


def test_frozen_threshold_and_old_counter_consistency():
    raw = _report()
    with pytest.raises(ValueError, match="frozen response tolerance"):
        adjudicate_transfer_report(raw, tolerance=2.0)
    raw["authorized_requests"] = 3
    with pytest.raises(ValueError, match="decisive count"):
        adjudicate_transfer_report(raw)


def test_nonfinite_observations_are_never_excluded():
    raw = _report()
    raw["test_state_diagnostics"][0]["pairs"][1]["true_gap"] = float("nan")
    with pytest.raises(ValueError, match="invalid original decision"):
        adjudicate_transfer_report(raw)
