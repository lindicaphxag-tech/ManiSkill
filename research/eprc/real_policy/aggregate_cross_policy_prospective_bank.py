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



FROZEN_RESTORE_AMENDMENT = "reset-fresh-space-block-position-4ulp-v2"
FROZEN_LEROBOT_COMMIT = "3c0a209f9fac4d2a57617e686a7f2a2309144ba2"
FROZEN_REVISIONS = {
    "diffusion": ("lerobot/diffusion_pusht", "d3d143b0342488252497853815b27ce3c0384c6b"),
    "vqbet": ("lerobot/vqbet_pusht", "390e5e4c079c880b22e873dad53ecfac706bc78a"),
}
FROZEN_HELDOUTS = {"A": [4.0, -2.0, 0.02], "B": [-5.0, 3.0, -0.025]}


def validate_frozen_state_provenance(state: dict, expected_seed: int) -> None:
    """Reject mixed v1/v2 restore outputs or altered checkpoint/protocol data.

    This validates declared artifact metadata only, not independent authorship,
    execution authenticity, or the Pymunk physical validity of the observations.
    """
    expected = {
        "schema": "eprc-cross-policy-state-v1",
        "reset_seed": expected_seed,
        "state_restore_protocol": FROZEN_RESTORE_AMENDMENT,
        "lerobot_commit": FROZEN_LEROBOT_COMMIT,
        "probe_epsilon": 0.125,
        "physical_probe": [2.0, 2.0, 0.01],
        "randomness_seeds": [123, 456, 789],
        "heldouts": FROZEN_HELDOUTS,
    }
    for field, frozen in expected.items():
        if state.get(field) != frozen:
            raise RuntimeError(
                f"frozen bank seed {expected_seed}: {field} drift "
                f"(expected {frozen!r}, got {state.get(field)!r})"
            )
    policies = state.get("policies")
    if not isinstance(policies, dict) or set(policies) != set(FROZEN_REVISIONS):
        raise RuntimeError(f"frozen bank seed {expected_seed}: missing policy family")
    for kind, (model_id, revision) in FROZEN_REVISIONS.items():
        p = policies[kind]
        if p.get("model_id") != model_id or p.get("revision") != revision:
            raise RuntimeError(
                f"frozen bank seed {expected_seed}: {kind} checkpoint identity drift"
            )
        if p.get("replicate_count") != 3:
            raise RuntimeError(
                f"frozen bank seed {expected_seed}: {kind} replicate count drift"
            )
    pairs = state.get("pairs")
    if not isinstance(pairs, list) or len(pairs) != 2:
        raise RuntimeError(f"frozen bank seed {expected_seed}: expected two pairs")
    for i, heldout_id in enumerate(("A", "B")):
        pair = pairs[i]
        if (
            pair.get("pair_id") != f"seed-{expected_seed}-{heldout_id}"
            or pair.get("reset_seed") != expected_seed
            or pair.get("heldout_id") != heldout_id
            or not isinstance(pair.get("a"), dict)
            or not isinstance(pair.get("b"), dict)
        ):
            raise RuntimeError(
                f"frozen bank seed {expected_seed}: pair identity or ordering drift"
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


def main(input_dir: Path, output: Path, *, require_pass: bool = False) -> int:
    states = []
    for seed in FROZEN_SEEDS:
        matches = list(input_dir.rglob(f"state-{seed}.json"))
        if len(matches) != 1:
            raise RuntimeError(
                f"expected exactly one artifact for frozen seed {seed}, found {len(matches)}"
            )
        state = json.loads(matches[0].read_text(encoding="utf-8"))
        validate_frozen_state_provenance(state, seed)
        states.append(state)

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
        "state_restore_protocol": FROZEN_RESTORE_AMENDMENT,
        "environment_amendment": "post-run-v1-to-v2-4ulp-block-position",
        "original_v1_bank_completed": False,
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
    return 3 if require_pass and not primary.passed else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(args.input_dir, args.output, require_pass=args.require_pass))
