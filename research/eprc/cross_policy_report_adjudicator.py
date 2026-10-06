from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from research.eprc.contract_signature import contract_signature, signature_distance


@dataclass(frozen=True)
class CrossPolicyAdjudication:
    protocol_id: str
    policy_a: str
    policy_b: str
    dec_signature_distance: float
    heldout_response_relative_distance: float
    robust_decisions_agree: bool
    both_dec_stable: bool
    both_reports_completed: bool
    comparable: bool
    reason: str


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "completed":
        raise ValueError(f"{path}: report is not completed")
    return data


def adjudicate(report_a: dict, report_b: dict) -> CrossPolicyAdjudication:
    protocol_a = report_a["protocol_id"]
    protocol_b = report_b["protocol_id"]
    if protocol_a != protocol_b:
        return CrossPolicyAdjudication(
            protocol_id=f"{protocol_a} != {protocol_b}",
            policy_a=report_a["policy_identity"]["model_id"],
            policy_b=report_b["policy_identity"]["model_id"],
            dec_signature_distance=float("nan"),
            heldout_response_relative_distance=float("nan"),
            robust_decisions_agree=False,
            both_dec_stable=False,
            both_reports_completed=True,
            comparable=False,
            reason="protocol mismatch",
        )

    required_equal = (
        "state_restore_protocol",
        "environment_reset_seed",
        "fine_physical_probe",
        "coarse_physical_probe",
        "heldout_physical_delta",
        "jacobian_support_units",
        "support_metric_physical",
    )
    for field in required_equal:
        if report_a[field] != report_b[field]:
            return CrossPolicyAdjudication(
                protocol_id=protocol_a,
                policy_a=report_a["policy_identity"]["model_id"],
                policy_b=report_b["policy_identity"]["model_id"],
                dec_signature_distance=float("nan"),
                heldout_response_relative_distance=float("nan"),
                robust_decisions_agree=False,
                both_dec_stable=False,
                both_reports_completed=True,
                comparable=False,
                reason=f"frozen field mismatch: {field}",
            )

    ja = np.asarray(report_a["dec"]["first_action_step_jacobian"], dtype=float)
    jb = np.asarray(report_b["dec"]["first_action_step_jacobian"], dtype=float)
    if ja.shape != jb.shape:
        raise ValueError("first-action DEC Jacobian shapes differ")

    dec_distance = signature_distance(contract_signature(ja), contract_signature(jb))

    ya = np.asarray(report_a["heldout_first_action_response"], dtype=float)
    yb = np.asarray(report_b["heldout_first_action_response"], dtype=float)
    if ya.shape != yb.shape:
        raise ValueError("held-out response shapes differ")
    denom = max(float(np.linalg.norm(ya)), float(np.linalg.norm(yb)), 1e-12)
    response_distance = float(np.linalg.norm(ya - yb) / denom)

    decision_agree = (
        report_a["robust_crg"]["decision"] == report_b["robust_crg"]["decision"]
    )
    stable = bool(
        report_a["dec"]["replicate_stability_certified"]
        and report_b["dec"]["replicate_stability_certified"]
    )

    return CrossPolicyAdjudication(
        protocol_id=protocol_a,
        policy_a=report_a["policy_identity"]["model_id"],
        policy_b=report_b["policy_identity"]["model_id"],
        dec_signature_distance=float(dec_distance),
        heldout_response_relative_distance=response_distance,
        robust_decisions_agree=decision_agree,
        both_dec_stable=stable,
        both_reports_completed=True,
        comparable=True,
        reason=(
            "same frozen physical protocol; descriptive two-policy witness only"
            if stable
            else "same frozen protocol but at least one DEC failed the stability gate"
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_a", type=Path)
    parser.add_argument("report_b", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = adjudicate(_load(args.report_a), _load(args.report_b))
    payload = asdict(result)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result.comparable else 2


if __name__ == "__main__":
    raise SystemExit(main())
