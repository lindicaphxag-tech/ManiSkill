#!/usr/bin/env python3
"""Audit the internal consistency and limits of a packaged assay run.

This checks recorded metadata, local artifact presence, and optional source
archive/pairing evidence. It does not evaluate policy performance.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen
from zipfile import ZipFile


def _read_json(root: Path, name: str) -> dict[str, Any]:
    path = root / name
    if not path.is_file():
        raise ValueError(f"Required artifact is missing: {name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {name}")
    return value


def _seed_digest(seeds: list[int]) -> str:
    payload = json.dumps(seeds, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _verify_source_dataset(
    dataset: dict[str, Any], requested_seeds: list[int] | None = None
) -> tuple[int, str]:
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
    archive_bytes = io.BytesIO() if requested_seeds is not None else None
    size = 0
    with urlopen(request, timeout=120) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            if archive_bytes is not None:
                archive_bytes.write(chunk)
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
    if archive_bytes is not None:
        with ZipFile(archive_bytes) as archive:
            metadata_paths = [
                name
                for name in archive.namelist()
                if name.endswith("/motionplanning/trajectory.json")
            ]
            if len(metadata_paths) != 1:
                raise ValueError(
                    "Expected one motion-planning trajectory metadata file in source archive"
                )
            metadata = json.loads(archive.read(metadata_paths[0]))
        source_seeds = [
            int(episode["episode_seed"])
            for episode in metadata.get("episodes", [])[: len(requested_seeds)]
        ]
        if source_seeds != requested_seeds:
            raise ValueError(
                "Requested episode seeds do not match the pinned source archive prefix"
            )
    return size, actual_sha256


def _audit_pairing_evidence(
    pairing: dict[str, Any],
    dataset: dict[str, Any],
    summary: dict[str, Any],
    run: dict[str, Any],
) -> list[str]:
    identity_fields = ("repository", "revision", "path", "sha256", "size_bytes")
    if any(
        pairing.get("source_dataset", {}).get(key) != dataset.get(key)
        for key in identity_fields
    ):
        raise ValueError("Pairing evidence names a different source dataset")

    requested = [int(seed) for seed in pairing.get("requested_episode_seeds", [])]
    if not requested or len(requested) != len(set(requested)):
        raise ValueError("Requested source episode seeds are empty or duplicated")
    if pairing.get("requested_episode_seeds_sha256") != _seed_digest(requested):
        raise ValueError("Requested source episode seed hash does not match its list")
    if len(requested) != int(run.get("config", {}).get("replay_count", -1)):
        raise ValueError("Requested seed list length differs from replay_count")

    arms = pairing.get("arms")
    if not isinstance(arms, dict) or len(arms) != 2:
        raise ValueError("Pairing evidence must include exactly two arms")
    run_arms = run.get("arms", [])
    outcomes = summary.get("arm_replay_outcomes", [])
    if len(run_arms) != 2 or len(outcomes) != 2 or set(run_arms) != set(arms):
        raise ValueError("Run, summary, and pairing evidence disagree on the two arms")
    arm_seed_sets: dict[str, set[int]] = {}
    for index, arm in enumerate(run_arms):
        evidence = arms[arm]
        seeds = [int(seed) for seed in evidence.get("successful_episode_seeds", [])]
        if len(seeds) != len(set(seeds)) or not set(seeds).issubset(requested):
            raise ValueError(f"Invalid successful source seeds for arm {arm}")
        if int(evidence.get("successful_count", -1)) != len(seeds):
            raise ValueError(f"Successful seed count differs for arm {arm}")
        if evidence.get("successful_episode_seeds_sha256") != _seed_digest(seeds):
            raise ValueError(f"Successful seed hash differs for arm {arm}")
        if [seed for seed in requested if seed in set(seeds)] != seeds:
            raise ValueError(f"Successful seeds are not in source order for arm {arm}")
        if int(outcomes[index].get("episodes_saved", -1)) != len(seeds):
            raise ValueError(f"Successful seed count differs from replay summary for arm {arm}")
        arm_seed_sets[arm] = set(seeds)

    paired = [int(seed) for seed in pairing.get("paired_episode_seeds", [])]
    expected = [
        seed
        for seed in requested
        if all(seed in values for values in arm_seed_sets.values())
    ]
    if paired != expected:
        raise ValueError("Paired seed list is not the ordered intersection of both arms")
    paired_count = int(pairing.get("paired_count", -1))
    if paired_count != len(paired) or paired_count != int(
        summary.get("paired_demo_count", -2)
    ):
        raise ValueError("Paired seed count differs from the summary")
    paired_hash = pairing.get("paired_episode_seeds_sha256")
    if paired_hash != _seed_digest(paired):
        raise ValueError("Paired seed hash does not match its list")
    if paired_hash != summary.get("paired_source_seed_sha256"):
        raise ValueError("Paired seed hash differs from the summary")
    if paired_hash != run.get("config", {}).get("paired_source_seed_sha256"):
        raise ValueError("Paired seed hash differs from the run config")
    config = run.get("config", {})
    if paired_count < int(config.get("minimum_paired_demos", 0)):
        raise ValueError("Paired seed count is below the configured minimum")
    run_pairing = run.get("pairing", {})
    if run_pairing.get("requested_episode_seeds_sha256") != _seed_digest(requested):
        raise ValueError("Requested seed hash differs from the experiment log")
    if int(run_pairing.get("paired_episode_count", -1)) != paired_count:
        raise ValueError("Paired seed count differs from the experiment log")
    if run_pairing.get("paired_source_seed_sha256") != paired_hash:
        raise ValueError("Paired seed hash differs from the experiment log")
    run_arm_hashes = run_pairing.get("successful_episode_seeds_sha256", {})
    for arm, evidence in arms.items():
        if run_arm_hashes.get(arm) != evidence.get("successful_episode_seeds_sha256"):
            raise ValueError(f"Arm seed hash differs from the experiment log for {arm}")
    return [
        "Pairing evidence verifies the exact ordered intersection: "
        f"{paired_count} seeds from {len(requested)} requested source episodes"
    ]


def audit(root: Path, verify_source_dataset: bool = False) -> list[str]:
    summary = _read_json(root, "assay_summary.json")
    run = _read_json(root, "experiment_log.json")
    dataset = _read_json(root, "raw_dataset.json")
    manifest = _read_json(root, "artifacts_manifest.json")
    findings: list[str] = []
    pairing_name = manifest.get("pairing_evidence")
    pairing = _read_json(root, pairing_name) if pairing_name else None

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
        requested_seeds = (
            [int(seed) for seed in pairing.get("requested_episode_seeds", [])]
            if pairing
            else None
        )
        verified_size, verified_sha256 = _verify_source_dataset(
            dataset, requested_seeds
        )
        findings.append(
            f"Pinned source archive downloaded and verified: {verified_size} bytes, "
            f"SHA-256 {verified_sha256}"
        )
        if requested_seeds is not None:
            findings.append("Requested seeds match the pinned archive metadata prefix")
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
    if pairing:
        findings.extend(_audit_pairing_evidence(pairing, dataset, summary, run))
    else:
        findings.append(
            f"Paired replay count is internally bounded ({paired_count} <= "
            f"{min(saved_counts)} saved in the smaller arm); this legacy result "
            "does not include seed lists, so membership cannot be recomputed"
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

    required_on_success = {
        "run_summaries",
        "metrics_jsonl",
        "metrics_csv",
        "pairing_evidence",
    }
    for field in (
        "run_summaries",
        "metrics_jsonl",
        "metrics_csv",
        "event_files_directory",
        "pairing_evidence",
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
