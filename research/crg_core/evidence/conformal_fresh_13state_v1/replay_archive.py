"""Read-only original-pilot replay plus true transfer-authorization audit.

Run on all 13 raw PushT state records (not a posthoc filtered subset).
Calls an archived byte-for-byte copy of the ORIGINAL frozen pilot evaluator
and the separately merged pre-outcome authorization-ledger correction.
"""
from __future__ import annotations

from hashlib import sha1
import argparse
import json
from pathlib import Path

import numpy as np

from research.crg_core.evidence.conformal_fresh_13state_v1.evaluator_at_source import evaluate
from research.crg_core.prospective.transfer_authorization_ledger import (
    adjudicate_transfer_report,
)

HERE = Path(__file__).resolve().parent
EXPECTED_PROTOCOL_BLOB = "b3ec5e5f4b6226c03d169ff857a97efe2a71d5c8"
EXPECTED_EVALUATOR_BLOB = "337623c2f864ffbe4696b0837c6658ff15341c99"
FROZEN_TEST = (263, 269, 271, 277)
CALIBRATION = (211, 223, 227, 229, 233, 239, 241, 251, 257)


def _github_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode() + bytes([0]) + data).hexdigest()


def _assert_equal(actual, expected, key):
    if type(actual) is not type(expected):
        raise AssertionError(f"{key}: original type mismatch")
    if isinstance(actual, dict):
        if set(actual) != set(expected):
            raise AssertionError(f"{key}: fields mismatch")
        for k in actual:
            _assert_equal(actual[k], expected[k], f"{key}.{k}")
    elif isinstance(actual, list):
        if len(actual) != len(expected):
            raise AssertionError(f"{key}: list size mismatch")
        for i, (a, b) in enumerate(zip(actual, expected, strict=True)):
            _assert_equal(a, b, f"{key}[{i}]")
    elif isinstance(actual, float):
        if not np.isclose(actual, expected, atol=1e-10, rtol=0):
            raise AssertionError(f"{key}: replay {actual!r} != original {expected!r}")
    elif actual != expected:
        raise AssertionError(f"{key}: replay value mismatch")


def replay_archive(root: Path = HERE) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    original = json.loads((root / "aggregate_original.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "crg-fresh13-owner-evidence-v1":
        raise ValueError("unexpected artifact manifest")
    if manifest.get("source_head_sha") != "bb22b80023a714a040756736db021df8c42e488e":
        raise ValueError("original prospective source changed")
    if manifest.get("source_workflow_run_id") != 37714189503:
        raise ValueError("original prospective run ID changed")
    if manifest.get("frozen_protocol_git_blob_sha1") != EXPECTED_PROTOCOL_BLOB:
        raise ValueError("manifest protocol blob is not the preregistered version")
    if _github_blob_sha1(root / "protocol_frozen.json") != EXPECTED_PROTOCOL_BLOB:
        raise ValueError("protocol edited after outcomes")
    if _github_blob_sha1(root / "evaluator_at_source.py") != EXPECTED_EVALUATOR_BLOB:
        raise ValueError("original source evaluator copy was modified")
    if (manifest.get("calibration_state_seeds") != list(CALIBRATION)
        or manifest.get("test_state_seeds") != list(FROZEN_TEST)):
        raise ValueError("state membership changed")
    for seed in (*CALIBRATION, *FROZEN_TEST):
        if not (root / f"state-{seed}.json").is_file():
            raise ValueError(f"frozen intended state missing: {seed}")
    result = evaluate(root / "protocol_frozen.json", root)
    # The original calibration_digest SHA-256 hashes a JSON serialization
    # of raw IEEE floats. A different NumPy/BLAS environment may perturb the
    # last decimal digit, changing the byte hash without meaningfully
    # changing the calibrated radius or any decision. Preserve both hashes
    # and require a full numerical replay of every other original field.
    original_fingerprint = original["calibration_digest"]
    replayed_fingerprint = result["calibration_digest"]
    original_for_compare = dict(original)
    replay_for_compare = dict(result)
    original_for_compare.pop("calibration_digest")
    replay_for_compare.pop("calibration_digest")
    _assert_equal(replay_for_compare, original_for_compare, "original_aggregate")
    corrected = adjudicate_transfer_report(original)
    stats = corrected["statistics"]
    if (stats["transfer_authorized_count"] != 0
        or stats["invalid_model_rejections"] != 8
        or stats["decisive_screening_count"] != 0
        or corrected["utility_outcome"] != "ZERO_UTILITY_NO_TRANSFER"):
        raise AssertionError("frozen negative evidence unexpectedly changed")

    stability = {
        "diffusion_stable_calibration": 0,
        "diffusion_stable_test": 0,
        "vqbet_stable_calibration": 0,
        "vqbet_stable_test": 0,
        "both_stable_test": 0,
    }
    for kind, seeds in (("calibration", CALIBRATION), ("test", FROZEN_TEST)):
        for seed in seeds:
            raw = json.loads((root / f"state-{seed}.json").read_text(encoding="utf-8"))
            diffusion = raw["policies"]["diffusion"]["stable"]
            vqbet = raw["policies"]["vqbet"]["stable"]
            stability[f"diffusion_stable_{kind}"] += int(diffusion)
            stability[f"vqbet_stable_{kind}"] += int(vqbet)
            if kind == "test":
                stability["both_stable_test"] += int(diffusion and vqbet)

    # Two logically distinct causes: the originally frozen validity gate
    # rejects all requests, AND the calibrated q exceeds the fixed tau.
    # Since nominal gap >= 0, any upper bound center + q >= q > tau.
    q = float(original["calibration_radius"])
    tau = corrected["frozen_response_tolerance"]
    return {
        "schema": "crg-fresh13-frozen-negative-evidence-replay-v1",
        "original_source_replayed": True,
        "original_calibration_digest_preserved": original_fingerprint,
        "recomputed_calibration_digest": replayed_fingerprint,
        "calibration_digest_byte_exact": original_fingerprint == replayed_fingerprint,
        "every_non_digest_original_field_numerically_checked": True,
        "float_value_replay_absolute_tolerance": 1e-10,
        "run_id": 37714189503,
        "protocol_blob_sha1": EXPECTED_PROTOCOL_BLOB,
        "n_calibration_state_clusters": len(CALIBRATION),
        "n_test_state_clusters": len(FROZEN_TEST),
        "n_dependent_test_requests": 8,
        "policy_query_count": original["total_policy_queries"],
        "raw_calibration_radius": q,
        "fixed_application_tolerance": tau,
        "uncertainty_radius_exceeds_tolerance": q > tau,
        "similar_transfer_cannot_be_authorized_even_without_validity_gate": q > tau,
        "state_cluster_empirical_coverage": [
            original["state_blocks_covered"], original["state_blocks_total"]
        ],
        "naive_point_reference_wrong_decisions": original["naive_point_reference_false_decisions"],
        "stability_counts": stability,
        "corrected_transfer_accounting": corrected,
        "research_verdict": "ZERO_UTILITY_NO_TRANSFER",
        "not_a_deterministic_policy_safety_certificate": True,
        "not_an_independent_external_replication": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    obj = replay_archive()
    result = json.dumps(obj, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
