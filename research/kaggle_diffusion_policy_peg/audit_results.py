#!/usr/bin/env python3
"""Audit the internal consistency and limits of a packaged assay run.

This checks recorded metadata and local artifact presence. It cannot validate
the source dataset digest or recompute paired-seed membership when those raw
inputs are intentionally not included in the public result package.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen


def _read_json(root: Path, name: str) -> dict[str, Any]:
    path = root / name
    if not path.is_file():
        raise ValueError(f"Required artifact is missing: {name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {name}")
    return value


def _verify_source_dataset(dataset: dict[str, Any]) -> tuple[int, str]:
    repository = str(dataset["repository"])
    revision = str(dataset["revision"])
    source_path = str(dataset["path"])
    url = (
        "https://huggingface.co/datasets/"
        f"{quote(repository, safe='/')}/resolve/{quote(revision, safe='')}/"
        f"{quote(source_path, safe='/')}?download=true"
    )
    request = Request(url, headers={"User-Agent": "ManiSkill-assay-evidence-auditor/1"})
    digest = hashlib.sha256()
    size = 0
    with urlopen(request, timeout=120) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    actual_sha256 = digest.hexdigest()
    if size != int(dataset["size_bytes"]):
        raise ValueError(
            f"Downloaded source dataset size mismatch: expected {dataset['size_bytes']}, got {size}"
        )
    if actual_sha256 != dataset["sha256"]:
        raise ValueError(
            f"Downloaded source dataset SHA-256 mismatch: expected {dataset['sha256']}, got {actual_sha256}"
        )
    return size, actual_sha256


def audit(root: Path, verify_source_dataset: bool = False) -> list[str]:
    summary = _read_json(root, "assay_summary.json")
    run = _read_json(root, "experiment_log.json")
    dataset = _read_json(root, "raw_dataset.json")
    manifest = _read_json(root, "artifacts_manifest.json")
    findings: list[str] = []

    run_status = run.get("status")
    manifest_status = manifest.get("status")
    if manifest_status != run_status:
        raise ValueError(
            f"Status mismatch: manifest={manifest_status!r}, run={run_status!r}"
        )
    findings.append(f"Run state: {run_status}")

    summary_dataset = summary.get("source_dataset")
    if not isinstance(summary_dataset, dict):
        raise ValueError("assay_summary.json has no source_dataset object")
    identity_fields = ("repository", "revision", "path", "sha256", "size_bytes")
    mismatched = [
        key for key in identity_fields if summary_dataset.get(key) != dataset.get(key)
    ]
    if mismatched:
        raise ValueError(f"Dataset identity differs between records: {mismatched}")
    digest = str(dataset.get("sha256", ""))
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Recorded source dataset SHA-256 is malformed")
    if int(dataset.get("size_bytes", 0)) <= 0:
        raise ValueError("Recorded source dataset size must be positive")
    if verify_source_dataset:
        verified_size, verified_sha256 = _verify_source_dataset(dataset)
        findings.append(
            f"Pinned source archive downloaded and verified: {verified_size} bytes, "
            f"SHA-256 {verified_sha256}"
        )
    else:
        findings.append(
            "Source dataset identity agrees across records; SHA-256 is recorded, "
            f"not recomputed (archive exported={bool(manifest.get('raw_demos_exported'))})"
        )

    outcomes = summary.get("arm_replay_outcomes")
    if not isinstance(outcomes, list) or len(outcomes) != 2:
        raise ValueError("Expected exactly two arm_replay_outcomes")
    saved_counts = []
    for outcome in outcomes:
        replayed = int(outcome["episodes_replayed"])
        saved = int(outcome["episodes_saved"])
        if replayed < 0 or saved < 0 or saved > replayed:
            raise ValueError(f"Invalid replay counts: {outcome}")
        saved_counts.append(saved)
        expected_rate = 100.0 * saved / replayed if replayed else 0.0
        if abs(float(outcome["success_percent"]) - expected_rate) > 0.011:
            raise ValueError(f"Replay percentage does not match counts: {outcome}")

    paired_count = int(summary.get("paired_demo_count", -1))
    if paired_count < 0 or paired_count > min(saved_counts):
        raise ValueError("Paired demo count exceeds one arm's replayed successes")
    if int(summary.get("baseline_loaded_trajectories", -1)) != paired_count:
        raise ValueError("Baseline trainer trajectory count differs from paired demo count")
    config = run.get("config", {})
    if int(config.get("effective_paired_num_demos", -1)) != paired_count:
        raise ValueError("Paired demo count differs from experiment config")
    paired_hash = summary.get("paired_source_seed_sha256")
    if not isinstance(paired_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", paired_hash):
        raise ValueError("Paired source-seed SHA-256 is missing or malformed")
    if config.get("paired_source_seed_sha256") != paired_hash:
        raise ValueError("Paired source-seed hash differs between records")
    findings.append(
        f"Paired replay count is internally bounded ({paired_count} <= "
        f"{min(saved_counts)} saved in the smaller arm); seed membership cannot "
        "be recomputed because replayed trajectories are not exported"
    )

    updates = int(summary.get("training_updates_completed", -1))
    if updates < 0:
        raise ValueError("training_updates_completed is missing or negative")
    if updates == 0:
        evaluation_error = summary.get("evaluation_error")
        if not evaluation_error:
            raise ValueError("Zero-update run has no recorded evaluation error")
        log_path = root / "upstream_baseline.log"
        if not log_path.is_file():
            raise ValueError("Zero-update run has no upstream_baseline.log")
        baseline_log = log_path.read_text(encoding="utf-8", errors="replace")
        error_type = str(evaluation_error).split(":", maxsplit=1)[0]
        if error_type not in baseline_log:
            raise ValueError(
                "Evaluation error type in summary is absent from upstream_baseline.log"
            )
        findings.append(f"Failure signature is corroborated by upstream_baseline.log ({error_type})")
        findings.append(
            "No optimizer update completed: this run provides no policy-performance evidence"
        )
    else:
        findings.append(f"Optimizer updates recorded: {updates}")

    required_on_success = {"run_summaries", "metrics_jsonl", "metrics_csv"}
    for field in (
        "run_summaries",
        "metrics_jsonl",
        "metrics_csv",
        "event_files_directory",
    ):
        name = manifest.get(field)
        if not name:
            findings.append(f"Artifact {field}: not listed in manifest")
            if run_status == "passed" and field in required_on_success:
                raise ValueError(f"Successful run has no manifest entry for {field}")
            continue
        path = root / name
        present = path.is_dir() if field == "event_files_directory" else path.is_file()
        findings.append(f"Artifact {field}: {'present' if present else 'absent'} ({name})")
        if run_status == "passed" and field in required_on_success and not present:
            raise ValueError(f"Successful run is missing manifest artifact: {field}")

    if run_status != "passed":
        findings.append(
            "Failure is preserved as failure; absent metrics/checkpoints are not treated as zero-valued results"
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "result_dir",
        type=Path,
        help="Directory containing assay_summary.json and the recorded run files",
    )
    parser.add_argument(
        "--verify-source-dataset",
        action="store_true",
        help="Download the pinned public archive and recompute its size and SHA-256",
    )
    args = parser.parse_args()
    try:
        findings = audit(args.result_dir, verify_source_dataset=args.verify_source_dataset)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"AUDIT FAILED: {exc}", file=sys.stderr)
        return 1
    print("STRUCTURAL AUDIT PASSED (this does not validate policy performance)")
    for finding in findings:
        print(f"- {finding}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
