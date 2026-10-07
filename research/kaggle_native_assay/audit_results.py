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
    if result.get("assay") != "native-pickcube-multiaxis-delta-pose":
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
