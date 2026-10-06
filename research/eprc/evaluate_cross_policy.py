from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.eprc.cross_policy_dec_gate import (
    PolicyCase,
    ProspectiveGate,
    ResponseProspectiveGate,
    evaluate_gate,
    evaluate_response_gate,
    score_pair,
)


def _case(raw: dict) -> PolicyCase:
    return PolicyCase(
        raw_action_jacobian=np.asarray(raw["raw_action_jacobian"], dtype=float),
        action_to_physical_jacobian=np.asarray(
            raw["action_to_physical_jacobian"], dtype=float
        ),
        support_ids=tuple(str(x) for x in raw.get("support_ids", [])),
        static_representation=str(raw["static_representation"]),
        coarse_contract_class=str(raw["coarse_contract_class"]),
        runtime_decision=str(raw["runtime_decision"]),
        physical_support_to_support_chart_jacobian=(
            None
            if raw.get("physical_support_to_support_chart_jacobian") is None
            else np.asarray(raw["physical_support_to_support_chart_jacobian"], dtype=float)
        ),
        heldout_physical_response=(
            None
            if raw.get("heldout_physical_response") is None
            else np.asarray(raw["heldout_physical_response"], dtype=float)
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate the frozen cross-policy DEC prospective gate."
    )
    parser.add_argument("evidence_json", type=Path)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.evidence_json.read_text(encoding="utf-8"))
    gate_raw = payload.get("gate", {})
    gate = ProspectiveGate(
        min_pairs=int(gate_raw.get("min_pairs", 20)),
        min_dec_auc=float(gate_raw.get("min_dec_auc", 0.70)),
        required_auc_margin=float(gate_raw.get("required_auc_margin", 0.05)),
    )

    pairs = []
    for item in payload["pairs"]:
        pairs.append(score_pair(_case(item["a"]), _case(item["b"])))

    secondary_decision_result = evaluate_gate(pairs, gate=gate)
    response_raw = payload.get("response_gate", {})
    response_gate = ResponseProspectiveGate(
        min_pairs=int(response_raw.get("min_pairs", 20)),
        min_dec_spearman=float(response_raw.get("min_dec_spearman", 0.50)),
        required_spearman_margin=float(
            response_raw.get("required_spearman_margin", 0.10)
        ),
    )
    primary_response_result = evaluate_response_gate(pairs, gate=response_gate)
    report = {
        "primary_heldout_response_gate": asdict(primary_response_result),
        "secondary_decision_agreement_gate": asdict(secondary_decision_result),
    }
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=True))

    if args.require_pass and not primary_response_result.passed:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
