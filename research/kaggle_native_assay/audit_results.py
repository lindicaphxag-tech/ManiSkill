#!/usr/bin/env python3
"""Verify integrity and the narrow claims in a native controller assay bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def read_json(root: Path, name: str) -> dict[str, Any]:
    path = root / name
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{name} must contain a JSON object")
    return value


def audit(root: Path) -> list[str]:
    manifest = read_json(root, "artifacts_manifest.json")
    log = read_json(root, "experiment_log.json")
    result = read_json(root, "assay_result.json")
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != {
        "assay_result.json",
        "experiment_log.json",
    }:
        raise ValueError("Manifest must hash the result and experiment log")

    for name, record in files.items():
        data = (root / name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if record.get("size_bytes") != len(data) or record.get("sha256") != digest:
            raise ValueError(f"Artifact integrity mismatch: {name}")

    commit = log.get("commit")
    if not commit or manifest.get("repository_commit") != commit:
        raise ValueError("Manifest and experiment log name different source commits")
    if log.get("status") != "passed" or manifest.get("status") != "passed":
        raise ValueError("Experiment log and manifest do not both report passed")
    if result.get("status") != "passed" or log.get("measurements") != result:
        raise ValueError("Result status or duplicated measurements disagree")
    assay = result.get("assay")
    if assay == "native-pickcube-pr1495-exact-head":
        supported_pr_heads = {
            "875ae4d8777678119b2f192ee186c6c15e6894d5",
            "5a09b2a4f5a1b1076f88ba01cdacf1683f5494af",
        }
        if commit not in supported_pr_heads:
            raise ValueError(f"Unrecognized exact PR #1495 head: {commit}")
        if log.get("pull_request") != "https://github.com/mani-skill/ManiSkill/pull/1495":
            raise ValueError("Experiment log does not identify ManiSkill PR #1495")
        if log.get("validation_harness") != "test_pr1495_native_assay.py":
            raise ValueError("Unexpected native validation harness")
        harness_path = Path(__file__).with_name("test_pr1495_native_assay.py")
        harness_sha256 = hashlib.sha256(harness_path.read_bytes()).hexdigest()
        if log.get("validation_harness_sha256") != harness_sha256:
            raise ValueError("Native validation harness SHA-256 does not match the published source")
        if result.get("cuda_available") is not True or result.get("render_backend") != "gpu":
            raise ValueError("Recorded exact-head run did not use CUDA with GPU rendering")
        if result.get("seed") != 2026:
            raise ValueError("Unexpected native rollout seed")
        measurements = result.get("results", {})
        try:
            one_step = measurements["unsaturated_xyz"]["1"]
            short = measurements["unsaturated_xyz"]["16"]["pr1495"]
            long = measurements["composed_saturated_xyz"]["64"]["pr1495"]
            repaired_first = float(one_step["pr1495"]["first_command_error_rad"])
            legacy_first = float(one_step["legacy"]["first_command_error_rad"])
            repaired_short = float(short["final_orientation_error_rad"])
            repaired_long = float(long["final_orientation_error_rad"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Exact-head native measurements are incomplete") from error
        values = (repaired_first, legacy_first, repaired_short, repaired_long)
        if not all(math.isfinite(value) and value >= 0 for value in values):
            raise ValueError("Exact-head orientation errors must be finite and nonnegative")
        if repaired_first >= legacy_first or repaired_first >= 1e-5:
            raise ValueError("PR conversion did not improve unsaturated first-command reconstruction")
        if repaired_short >= 1e-3 or repaired_long >= 1e-3:
            raise ValueError("PR conversion exceeded the recorded native rollout error bounds")
        return [
            f"SHA-256 and sizes verified for {len(files)} artifacts",
            f"Exact source commit and PR URL verified: {commit}",
            f"Published native harness hash verified: {harness_sha256}",
            f"Unsaturated first-command error: PR {repaired_first:.3g} rad, legacy {legacy_first:.3g} rad",
            "The saturated 16-step comparison is intentionally not treated as a superiority claim.",
        ]

    if assay != "native-pickcube-multiaxis-delta-pose":
        raise ValueError("Unexpected assay identity")
    if result.get("torch_cuda_available") is not True or result.get("render_backend") != "gpu":
        raise ValueError("Recorded run did not use CUDA with GPU rendering")
    if "Tesla T4" not in str(log.get("hardware", "")):
        raise ValueError("Recorded hardware does not identify the requested Tesla T4")

    horizons = result.get("horizon_results", {})
    single_step = horizons.get("within_single_step_rotation_limit", {}).get("1")
    if not isinstance(single_step, dict):
        raise ValueError("Missing unsaturated one-step orientation measurement")
    legacy = float(single_step["legacy_first_command_error_rad"])
    repaired = float(single_step["repaired_first_command_error_rad"])
    if not all(math.isfinite(value) and value >= 0 for value in (legacy, repaired)):
        raise ValueError("First-command errors must be finite and nonnegative")
    if not repaired < legacy or repaired > 1e-5:
        raise ValueError("Repaired unsaturated command does not meet its narrow regression claim")

    return [
        f"SHA-256 and sizes verified for {len(files)} artifacts",
        f"Source commit: {commit}",
        f"CUDA + GPU-rendered Tesla T4 assay; repaired unsaturated first-command error "
        f"{repaired:.3g} rad vs legacy {legacy:.3g} rad",
        "This audit does not establish policy success, general performance, or exact-head validation of an upstream PR.",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="directory containing assay artifacts")
    args = parser.parse_args()
    for finding in audit(args.bundle):
        print(finding)


if __name__ == "__main__":
    main()
