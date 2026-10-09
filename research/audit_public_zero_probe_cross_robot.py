"""Full-denominator public ZERO-probe PhysX assay auditor (stdlib).

Calibration and heldout truth are used ONLY by this OFFLINE evaluator. Empirical
finite-sample response envelopes are NOT independent deterministic attestations.
Even a heldout success cannot authorize unknown real-world robot probes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import sqrt, isfinite
from pathlib import Path

from research.public_probe_observability_contract import (
    Gate, Observation, ProbeContract, plan_public_probe, identify_after_probe,
    _point_segment_distance,
)

PRECOMMIT_SHA = "e862a731b02d718c7e405f380b848f9b85ce7af4"
FIRST = {"panda": 640001, "xarm6_robotiq": 650001}


def _v3(x):
    v = tuple(float(z) for z in x)
    if len(v) != 3 or not all(isfinite(z) for z in v):
        raise ValueError("Invalid physical XYZ")
    return v


def _dist(a, b):
    return sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def _response_fit(x, y, m, lo=0.0, hi=1.0):
    d = [mj - xj for mj, xj in zip(m, x)]
    q = sum(z*z for z in d)
    alpha = max(lo, min(hi, sum((yj-xj)*z for xj, yj, z in zip(x, y, d))/q)) if q else lo
    residual = _dist(y, [xj + alpha*z for xj, z in zip(x, d)])
    return alpha, residual


def load_all(folder: Path) -> dict:
    all_rows = {}
    for robot, first in FIRST.items():
        for chunk in (0, 1):
            fn = folder / f"public_zero_probe_{robot}_chunk{chunk}_original4.json"
            raw = fn.read_bytes()
            j = json.loads(raw)
            expected = list(range(first+4*chunk, first+4*chunk+4))
            if (j.get("schema") != "public_zero_probe_cross_robot_native_physx_v1"
                    or j.get("preregistration_git_blob") != PRECOMMIT_SHA
                    or j.get("robot") != robot or j.get("chunk") != chunk
                    or j.get("seeds") != expected
                    or j.get("split") != ("CALIBRATION" if chunk == 0 else "UNSEEN_HELDOUT")
                    or j.get("actual_native_physics") is not True
                    or len(j.get("rows", [])) != 4):
                raise ValueError(f"Changed, missing or omitted original PhysX source: {fn}")
            for i, row in enumerate(j["rows"]):
                if (row.get("seed") != expected[i] or row.get("robot") != robot
                        or row.get("native_physx_cpu_executed") is not True
                        or row.get("known_delivered_probe_native_6d") != [0.0]*6
                        or row.get("target_getter_only_after_step_for_audit") is not True
                        or row.get("fault_step") != 2 or row.get("probe_step") != 3
                        or row.get("source_policy_used") is not False):
                    raise ValueError("Source state/physical condition not faithfully recorded")
                history = tuple(_v3(m) for m in row["history_targets_xyz_m_from_command_observer"])
                if len(history) != 2 or _dist(*history) < 1e-5:
                    raise ValueError("Two genuine distinct controller target histories required")
                bs = row["truth_branches"]
                if set(bs) != {"applied", "held"}:
                    raise ValueError("Missing physical ACK-truth branch")
                for truth in ("applied", "held"):
                    b = bs[truth]
                    before = _v3(b["public_before"])
                    after = _v3(b["public_after"])
                    true_idx = 0 if truth == "applied" else 1
                    # Post-step actual-target agreement is audit-only.
                    if not 0 <= b["target_observer_residual_max_m"] <= 1e-4:
                        raise ValueError("Action-history observer was physically falsified")
                    if abs(_dist(before, after) - b["observed_probe_displacement_m"]) > 1e-7:
                        raise ValueError("Public before/after displacement ledger tampered")
                    if truth == "held" and b["physical_fault_native_zero_applied"] is not True:
                        raise ValueError("Missing real native ACK hold at t2")
                    if truth == "applied" and b["physical_fault_native_zero_applied"] is not False:
                        raise ValueError("Fault truth reversed")
                    alpha, residual = _response_fit(before, after, history[true_idx])
                    all_rows[(robot, expected[i], truth)] = {
                        "robot": robot, "seed": expected[i], "truth": truth,
                        "true_idx": true_idx, "history": history,
                        "before": before, "after": after,
                        "raw_fitted_gain": alpha, "raw_fitted_model_residual_m": residual,
                        "original_file_sha256": hashlib.sha256(raw).hexdigest()}
    if len(all_rows) != 32:
        raise ValueError("Missing complete 16 reset states x 2 physically stepped ACK truths")
    return all_rows


def audit(rows: dict) -> dict:
    out = dict(schema="public_zero_probe_physx_empirical_disjoint_calibration_audit_v1",
               preoutcome_git_blob=PRECOMMIT_SHA,
               genuine_independent_robot_implementations=2,
               physical_reset_states=16, physically_realized_truth_worlds=32,
               trained_ppo_task_runs=0,
               no_private_target_getter_in_probe_decision=True,
               calibration_is_NOT_deterministic_attestation=True,
               categories={})
    for robot, first in FIRST.items():
        train = [rows[(robot, seed, truth)]
                 for seed in range(first, first+4)
                 for truth in ("applied", "held")]
        test = [rows[(robot, seed, truth)]
                for seed in range(first+4, first+8)
                for truth in ("applied", "held")]
        lo = max(0., min(r["raw_fitted_gain"] for r in train) - 0.05)
        hi = min(1., max(r["raw_fitted_gain"] for r in train) + 0.05)
        eps = max(r["raw_fitted_model_residual_m"] for r in train) + 0.002
        if not (0 <= lo <= hi <= 1 and eps <= 0.25):
            raise ValueError("Invalid prespecified calibration-only gain/noise envelope")
        violations, hypothetically_separable, confident_correct, confident_wrong = [], 0, 0, 0
        per_seed = []
        for row in test:
            x, y = row["before"], row["after"]
            # The present physical intervention IS zero native delta. No nonzero
            # candidate is evaluated against unstepped counterfactual physics.
            # Setting attested True is explicitly ONLY an offline sensitivity
            # calculation "IF this finite calibration interval held"; the
            # actual deployable runtime MUST keep it False.
            midpoint = tuple(sum(h[j] for h in row["history"])/2 for j in range(3))
            diag = ProbeContract(
                targets_xyz_m=row["history"], public_before_xyz_m=x,
                source_desired_target_xyz_m=midpoint,
                gain_min=lo, gain_max=hi,
                public_model_error_l2_m=eps, numerical_guard_m=1e-7,
                native_delta_min_xyz_m=(-.1, -.1, -.1),
                native_delta_max_xyz_m=(.1, .1, .1),
                max_probe_translation_l2_m=0.0,
                max_target_deviation_linf_m=0.2,
                histories_complete=True, provenance_trusted=True,
                controller_chart_verified=True,
                calibration_independent_attested=True)
            plan = plan_public_probe(diag, [], privileged_query_available=True)
            # Offline ACTUAL true history consistency under the empirical model
            vec = tuple(row["history"][row["true_idx"]][j]-x[j] for j in range(3))
            a = tuple(x[j]+lo*vec[j] for j in range(3))
            b = tuple(x[j]+hi*vec[j] for j in range(3))
            model_resid = _point_segment_distance(y, (a,b))
            violated = model_resid > eps + 1e-7
            if violated:
                violations.append({"seed": row["seed"], "truth": row["truth"],
                                   "excess_m": model_resid-eps})
            label = None
            if plan.gate is Gate.PROBE_ZERO:
                hypothetically_separable += 1
                observation = identify_after_probe(plan, y, known_native_dispatch_confirmed=True)
                if observation.status is Observation.UNIQUE:
                    label = observation.history_index
                    if label == row["true_idx"]:
                        confident_correct += 1
                    else:
                        confident_wrong += 1
            per_seed.append(dict(seed=row["seed"], truth=row["truth"],
                                 model_violation=violated,
                                 true_history_residual_m=model_resid,
                                 hypothetical_zero_probe_gate=plan.gate.value,
                                 identified_history_index=label,
                                 ground_truth_index_audit_only=row["true_idx"]))
        out["categories"][robot] = dict(
            calibration_worlds=8, heldout_worlds=8,
            empirical_gain_interval=[lo,hi], empirical_epsilon_m=eps,
            heldout_model_violation_count=len(violations),
            heldout_violation_details=violations,
            hypothetically_disjoint_zero_probe_count=hypothetically_separable,
            correct_confident_labels=confident_correct,
            wrong_confident_labels=confident_wrong,
            heldout_all_original_truth_cases=per_seed)
    out["claim_limit"] = ("Post-result empirical diagnostics only; a finite train-derived "
                          "interval is NOT a physically certified response envelope; "
                          "even successful classification would NOT certify future physics, "
                          "real safety or genuine autonomous nonzero active probing.")
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = audit(load_all(args.source_dir))
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("PUBLIC_ZERO_PROBE_32_PHYSICAL_WORLDS_AUDIT", json.dumps({
        k:{x:v for x,v in val.items() if x not in ("heldout_violation_details","heldout_all_original_truth_cases")}
        for k,val in data["categories"].items()}, sort_keys=True))


if __name__ == "__main__":
    main()
