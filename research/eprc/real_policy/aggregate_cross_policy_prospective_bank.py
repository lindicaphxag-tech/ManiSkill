from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from research.eprc.cross_policy_dec_gate import (
    PolicyCase,
    ResponseProspectiveGate,
    evaluate_response_gate,
    score_pair,
)


FROZEN_SEEDS = (17, 29, 43, 59, 71, 89, 101, 131, 151, 181)
FROZEN_PAIR_COUNT = 20
FROZEN_GATE = ResponseProspectiveGate(
    min_pairs=20,
    min_dec_spearman=0.50,
    required_spearman_margin=0.10,
)


def _case(raw: dict) -> PolicyCase:
    return PolicyCase(
        raw_action_jacobian=np.asarray(raw["raw_action_jacobian"], dtype=float),
        action_to_physical_jacobian=np.asarray(
            raw["action_to_physical_jacobian"], dtype=float
        ),
        support_ids=tuple(raw["support_ids"]),
        static_representation=str(raw["static_representation"]),
        coarse_contract_class=str(raw["coarse_contract_class"]),
        runtime_decision=str(raw["runtime_decision"]),
        physical_support_to_support_chart_jacobian=np.asarray(
            raw["physical_support_to_support_chart_jacobian"], dtype=float
        ),
        heldout_physical_response=np.asarray(
            raw["heldout_physical_response"], dtype=float
        ),
    )


def main(input_dir: Path, output: Path) -> int:
    states = []
    for seed in FROZEN_SEEDS:
        matches = list(input_dir.rglob(f"state-{seed}.json"))
        if len(matches) != 1:
            raise RuntimeError(
                f"expected exactly one artifact for frozen seed {seed}, found {len(matches)}"
            )
        states.append(json.loads(matches[0].read_text(encoding="utf-8")))

    pairs_raw = [pair for state in states for pair in state["pairs"]]
    if len(pairs_raw) != FROZEN_PAIR_COUNT:
        raise RuntimeError(f"frozen bank changed: {len(pairs_raw)} != 20")

    pair_scores = [
        score_pair(_case(pair["a"]), _case(pair["b"]))
        for pair in pairs_raw
    ]
    primary = evaluate_response_gate(pair_scores, gate=FROZEN_GATE)

    state_diagnostics = []
    unstable_states = []
    for state in states:
        d = state["policies"]["diffusion"]
        v = state["policies"]["vqbet"]
        diag = {
            "reset_seed": state["reset_seed"],
            "diffusion_stable": bool(d["stable"]),
            "diffusion_q95": float(d["q95_signature_radius"]),
            "vqbet_stable": bool(v["stable"]),
            "vqbet_q95": float(v["q95_signature_radius"]),
            "diffusion_queries": int(d["query_count"]),
            "vqbet_queries": int(v["query_count"]),
        }
        state_diagnostics.append(diag)
        if not (diag["diffusion_stable"] and diag["vqbet_stable"]):
            unstable_states.append(state["reset_seed"])

    payload = {
        "schema": "eprc-cross-policy-prospective-result-v1",
        "frozen_seeds": list(FROZEN_SEEDS),
        "n_pairs": len(pair_scores),
        "primary_gate": asdict(primary),
        "unstable_states_retained": unstable_states,
        "n_unstable_states": len(unstable_states),
        "state_diagnostics": state_diagnostics,
        "interpretation": (
            "PASS" if primary.passed else
            "FAIL_FROZEN_CROSS_POLICY_DEC_GATE"
        ),
        "no_exclusion_applied": True,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if primary.passed else 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.input_dir, args.output))
