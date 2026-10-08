"""Independent, outcome-only audit of calibrated transfer decision semantics.

The frozen pilot made decisions before observing outcomes. This checker
reads its *unchanged* aggregate after execution and corrects only the
accounting: "distinct" refuses transfer, it does not authorize it.

No policy queries, calibration, threshold changes or case exclusions occur.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from math import isfinite


VALID_DECISIONS = {
    "STATISTICALLY_SIMILAR",
    "STATISTICALLY_DISTINCT",
    "ABSTAIN_UNCERTAIN",
    "REJECT_INVALID_LOCAL_MODEL",
}
EXPECTED_TEST_SEEDS = (263, 269, 271, 277)


def adjudicate_transfer_report(raw: dict, *, tolerance: float = 1.0) -> dict:
    if raw.get("schema") != "crg-transfer-conformal-fresh-state-pilot-result-v1":
        raise ValueError("unexpected original pilot result schema")
    if raw.get("preregistered_test_seeds") != list(EXPECTED_TEST_SEEDS):
        raise ValueError("changed fresh-state test split")
    if raw.get("n_test_state_clusters") != 4 or raw.get("n_dependent_test_pairs") != 8:
        raise ValueError("frozen four-state/eight-request denominator violated")
    if raw.get("all_states_retained") is not True:
        raise ValueError("missing intended test state")
    if not isfinite(float(tolerance)) or tolerance != 1.0:
        raise ValueError("the originally frozen response tolerance must remain 1.0")
    rows = raw.get("test_state_diagnostics")
    if not isinstance(rows, list) or len(rows) != 4:
        raise ValueError("four raw state outcome rows are required")
    seeds = [r.get("seed") for r in rows]
    if seeds != list(EXPECTED_TEST_SEEDS):
        raise ValueError("test state order or identity changed")
    totals = {
        "transfer_authorized_count": 0,
        "distinct_nontransfer_count": 0,
        "uncertain_abstentions": 0,
        "invalid_model_rejections": 0,
        "false_transfer_authorization_count": 0,
        "false_distinct_rejection_count": 0,
        "correct_distinct_nontransfer_count": 0,
        "decisive_screening_count": 0,
    }
    detail = []
    for state in rows:
        pairs = state.get("pairs")
        if not isinstance(pairs, list) or len(pairs) != 2:
            raise ValueError("missing one paired held-out request")
        if [p.get("heldout_id") for p in pairs] != ["A", "B"]:
            raise ValueError("A/B requests missing or reordered")
        record = []
        for pair in pairs:
            decision = pair.get("decision")
            gap = pair.get("true_gap")
            if decision not in VALID_DECISIONS or not isinstance(gap, (int, float)) or not isfinite(gap) or gap < 0:
                raise ValueError("invalid original decision or observed response gap")
            similar = decision == "STATISTICALLY_SIMILAR"
            distinct = decision == "STATISTICALLY_DISTINCT"
            if similar:
                totals["transfer_authorized_count"] += 1
            elif distinct:
                totals["distinct_nontransfer_count"] += 1
            elif decision == "ABSTAIN_UNCERTAIN":
                totals["uncertain_abstentions"] += 1
            else:
                totals["invalid_model_rejections"] += 1
            totals["decisive_screening_count"] += int(similar or distinct)
            false_authorization = similar and gap > tolerance
            false_rejection = distinct and gap <= tolerance
            totals["false_transfer_authorization_count"] += int(false_authorization)
            totals["false_distinct_rejection_count"] += int(false_rejection)
            totals["correct_distinct_nontransfer_count"] += int(distinct and gap > tolerance)
            record.append({
                "heldout_id": pair["heldout_id"],
                "decision": decision,
                "observed_gap": float(gap),
                "actual_transfer_authorized": similar,
                "false_transfer_authorization": false_authorization,
                "false_nontransfer_rejection": false_rejection,
            })
        detail.append({"state_seed": state["seed"], "paired_requests": record})
    if sum(totals[k] for k in (
        "transfer_authorized_count", "distinct_nontransfer_count",
        "uncertain_abstentions", "invalid_model_rejections"
    )) != 8:
        raise AssertionError("decision counts did not sum to eight")

    # Original pilot's field is misnamed, counting both similarity and
    # distinct-response decisions as "authorized". It is retained in the
    # archive and asserted here to prevent silent reinterpretation.
    if raw.get("authorized_requests") != totals["decisive_screening_count"]:
        raise ValueError("original decisive count inconsistent with source outputs")

    return {
        "schema": "crg-frozen-pilot-transfer-accounting-v1",
        "source_frozen_protocol_sha256": raw.get("frozen_protocol_sha256"),
        "original_aggregate_authorized_requests_means_decisive_not_transfer": True,
        "n_independent_test_states": 4,
        "n_dependent_test_observations": 8,
        "frozen_response_tolerance": tolerance,
        "transfer_authorization_coverage": totals["transfer_authorized_count"] / 8,
        "decisive_classification_coverage": totals["decisive_screening_count"] / 8,
        "utility_outcome": (
            "ZERO_UTILITY_NO_TRANSFER"
            if totals["transfer_authorized_count"] == 0
            else "NONZERO_ACTUAL_TRANSFER_AUTHORIZATION"
        ),
        "not_matched_coverage_baseline_comparison": True,
        "not_independent_replication": True,
        "statistics": totals,
        "per_state_audit": detail,
        "claim_boundary": (
            "These are realized 3-RNG-seed MEAN first-action response differences, "
            "not single-run collision or physical deployment failure rates. "
            "A false distinct rejection is not a false transfer authorization. "
            "No invalid/rejected state was excluded."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("original_pilot_result", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.original_pilot_result.read_text(encoding="utf-8"))
    out = adjudicate_transfer_report(raw)
    payload = json.dumps(out, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
