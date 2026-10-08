"""Fail-closed reviewer evidence gate for paired PegInsertionSide Diffusion Policy.

This is an *artifact auditor* (not a trainer). It reports descriptive paired
training/evaluation curves only after checking declared provenance, complete
optimizer/evaluation traces, exact source-seed pairing and metric arithmetic.
It never turns author-controlled files into proof of independent execution,
does not claim statistical significance with one seed, and cannot isolate the
#1495 converter effect from the combined #1495+#1472 arm.

Example:
    python research/kaggle_diffusion_policy_peg/policy_evidence_gate.py \
      /path/to/kaggle/assay_output --output /path/to/reviewer.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


BASE = "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERSION = "875ae4d8777678119b2f192ee186c6c15e6894d5"
CONTROLLER = "eed9be164797d41540421bda8adb3840377d7087"
ARMS = ("upstream_baseline", "combined_pr1495_pr1472")
EVAL_TAGS = ("eval/success_once", "eval/success_at_end")


class UnverifiablePolicyEvidence(ValueError):
    """Do not promote incomplete, unpaired or inconsistent runs to claims."""


def _json(root: Path, name: str) -> Any:
    path = root / name
    if not path.is_file():
        raise UnverifiablePolicyEvidence(f"missing source artifact: {name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise UnverifiablePolicyEvidence(f"unreadable JSON artifact: {name}") from exc


def _strict_int(value: object, field: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise UnverifiablePolicyEvidence(f"invalid integer {field}")
    return value


def _source_seed_digest(seeds: list[int]) -> str:
    return hashlib.sha256(
        json.dumps(seeds, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _verified_pairing(
    pairing: dict[str, Any], manifest: dict[str, Any],
    record: dict[str, Any], summaries: dict[str, dict[str, Any]],
) -> tuple[int, str]:
    if manifest.get("pairing_evidence") != "pairing_evidence.json":
        raise UnverifiablePolicyEvidence("pairing evidence is not in artifact manifest")
    requested = pairing.get("requested_episode_seeds")
    paired = pairing.get("paired_episode_seeds")
    if not isinstance(requested, list) or not isinstance(paired, list):
        raise UnverifiablePolicyEvidence("paired source seeds are missing")
    if (
        not requested
        or any(type(s) is not int for s in requested)
        or len(set(requested)) != len(requested)
        or any(type(s) is not int for s in paired)
        or len(set(paired)) != len(paired)
    ):
        raise UnverifiablePolicyEvidence("invalid or repeated source episode seeds")
    requested_digest = _source_seed_digest(requested)
    if requested_digest != pairing.get("requested_episode_seeds_sha256"):
        raise UnverifiablePolicyEvidence("source episode-seed digest mismatch")
    if requested_digest != record.get("pairing", {}).get("requested_episode_seeds_sha256"):
        raise UnverifiablePolicyEvidence("paired experiment source-seed digest mismatch")
    each_arm = pairing.get("arms")
    if not isinstance(each_arm, dict) or set(each_arm) != set(ARMS):
        raise UnverifiablePolicyEvidence("missing per-arm successful source-seed evidence")
    successes = []
    for arm in ARMS:
        data = each_arm[arm]
        seeds = data.get("successful_episode_seeds")
        if not isinstance(seeds, list) or any(type(x) is not int for x in seeds):
            raise UnverifiablePolicyEvidence("malformed source-seed list")
        if len(set(seeds)) != len(seeds) or not set(seeds).issubset(requested):
            raise UnverifiablePolicyEvidence("unmatched or duplicated arm episode seeds")
        if [s for s in requested if s in set(seeds)] != seeds:
            raise UnverifiablePolicyEvidence("successful episode seeds reordered")
        if data.get("successful_episode_seeds_sha256") != _source_seed_digest(seeds):
            raise UnverifiablePolicyEvidence("successful episode-seed digest mismatch")
        if data.get("successful_count") != len(seeds):
            raise UnverifiablePolicyEvidence("per-arm episode count mismatch")
        successes.append(set(seeds))
    expected = [s for s in requested if all(s in group for group in successes)]
    if paired != expected:
        raise UnverifiablePolicyEvidence("paired list is not the ordered arm intersection")
    paired_digest = _source_seed_digest(paired)
    cfg = record.get("config", {})
    if (
        paired_digest != pairing.get("paired_episode_seeds_sha256")
        or paired_digest != cfg.get("paired_source_seed_sha256")
        or paired_digest != record.get("pairing", {}).get("paired_source_seed_sha256")
        or len(paired) != pairing.get("paired_count")
        or len(paired) != cfg.get("effective_paired_num_demos")
    ):
        raise UnverifiablePolicyEvidence("paired source-seed identity mismatch")
    if len(paired) < _strict_int(cfg.get("minimum_paired_demos"), "minimum paired demos", 1):
        raise UnverifiablePolicyEvidence("paired demonstration count below protocol minimum")
    for arm in ARMS:
        if summaries[arm].get("paired_source_seed_sha256") != paired_digest:
            raise UnverifiablePolicyEvidence("trained arm differs from pinned paired seeds")
        if summaries[arm].get("paired_num_demos") != len(paired):
            raise UnverifiablePolicyEvidence("trained arm paired demo count mismatch")
    return len(paired), paired_digest


def gate(root: Path) -> dict[str, Any]:
    """Return a descriptive package or refuse any unsupported performance claim."""
    root = Path(root)
    manifest = _json(root, "artifacts_manifest.json")
    run = _json(root, "experiment_log.json")
    pairing = _json(root, "pairing_evidence.json")
    summary = _json(root, "run_summaries.json")
    if (
        not isinstance(manifest, dict) or not isinstance(run, dict)
        or not isinstance(pairing, dict) or not isinstance(summary, list)
    ):
        raise UnverifiablePolicyEvidence("unexpected artifact schema")
    if run.get("status") != "passed" or manifest.get("status") != "passed":
        raise UnverifiablePolicyEvidence("training run did not complete successfully")
    if (
        run.get("base_commit") != BASE
        or run.get("conversion_pr", {}).get("head") != CONVERSION
        or run.get("controller_pr", {}).get("head") != CONTROLLER
    ):
        raise UnverifiablePolicyEvidence("unfrozen base / converter / controller source")
    if run.get("arms") != list(ARMS):
        raise UnverifiablePolicyEvidence("incorrect intervention arms")
    if len(summary) != 2 or {x.get("arm") for x in summary} != set(ARMS):
        raise UnverifiablePolicyEvidence("must have exactly two complete trained arms")
    by_arm = {x["arm"]: x for x in summary}
    for arm, commit, overlay in (
        (ARMS[0], BASE, None),
        (ARMS[1], CONVERSION, CONTROLLER),
    ):
        item = by_arm[arm]
        if item.get("source_commit") != commit or item.get("controller_overlay_commit") != overlay:
            raise UnverifiablePolicyEvidence(f"source intervention identity wrong for {arm}")
        for required in ("source_tree", "runtime_compatibility_sha256", "demo_sha256"):
            if not isinstance(item.get(required), str) or not item[required]:
                raise UnverifiablePolicyEvidence(f"missing {required} provenance for {arm}")
    paired_count, pairing_sha = _verified_pairing(pairing, manifest, run, by_arm)

    cfg = run.get("config", {})
    iters = _strict_int(cfg.get("total_iters"), "total_iters", 1)
    freq = _strict_int(cfg.get("eval_freq"), "eval_freq", 1)
    n = _strict_int(cfg.get("num_eval_episodes"), "num_eval_episodes", 2)
    # Require the exact precommitted evaluation schedule; no selection of
    # the best-looking step after inspecting one arm is permitted.
    expected_steps = sorted(set(range(0, iters + 1, freq)) | {iters})
    metric_path = root / "metrics.jsonl"
    if not metric_path.is_file():
        raise UnverifiablePolicyEvidence("training/evaluation scalar file missing")
    samples: dict[tuple[str, str], dict[int, float]] = {}
    for index, line in enumerate(metric_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            arm, tag = item["arm"], item["tag"]
            step, value = item["step"], item["value"]
        except (ValueError, TypeError, KeyError) as exc:
            raise UnverifiablePolicyEvidence(f"invalid scalar row {index}") from exc
        if arm not in ARMS or not isinstance(tag, str):
            raise UnverifiablePolicyEvidence("scalar row has unknown arm or tag")
        if type(step) is not int or step < 0 or step > iters:
            raise UnverifiablePolicyEvidence("scalar row has impossible optimizer step")
        if type(value) not in (int, float) or not math.isfinite(value):
            raise UnverifiablePolicyEvidence("nonfinite optimizer or evaluation scalar")
        entries = samples.setdefault((arm, tag), {})
        if step in entries:
            raise UnverifiablePolicyEvidence("duplicate scalar metric at evaluation step")
        entries[step] = float(value)

    for arm in ARMS:
        losses = samples.get((arm, "losses/total_loss"), {})
        if not losses or max(losses) < iters:
            raise UnverifiablePolicyEvidence(f"missing complete optimizer loss trace for {arm}")
        for tag in EVAL_TAGS:
            series = samples.get((arm, tag), {})
            if sorted(series) != expected_steps:
                raise UnverifiablePolicyEvidence(
                    f"incomplete or unmatched evaluation schedule for {arm}/{tag}"
                )
            for step, value in series.items():
                if value < 0 or value > 1:
                    raise UnverifiablePolicyEvidence("success rate lies outside [0,1]")
                successes = round(value * n)
                # Float32 TensorBoard scalar noise is acceptable; changing
                # the denominator or inventing between-episode fractions isn't.
                if abs(value - successes / n) > 1e-6:
                    raise UnverifiablePolicyEvidence(
                        f"success rate not representable by {n} episodes"
                    )
    curves = [
        {
            "optimizer_step": step,
            **{
                arm: {
                    tag: {
                        "rate": samples[(arm, tag)][step],
                        "successful_episodes": round(samples[(arm, tag)][step] * n),
                        "evaluated_episodes": n,
                    }
                    for tag in EVAL_TAGS
                }
                for arm in ARMS
            },
        }
        for step in expected_steps
    ]
    return {
        "status": "descriptive_single_seed_paired_training_only",
        "source": "ManiSkill baseline 62ff3a5 / converter PR1495 + controller PR1472",
        "paired_source_demonstrations": paired_count,
        "source_seed_digest": pairing_sha,
        "training_seed": cfg.get("seed"),
        "evaluation_steps": expected_steps,
        "curves": curves,
        "limitations": [
            "Authored run metadata and SHA-256 cannot establish independent execution authenticity.",
            "Single training seed and finite evaluation episodes: no statistical superiority claim.",
            "This two-arm design measures combined #1495+#1472 changes, not isolated PR #1495 effect.",
            "The reported success rate cannot prove real-robot deployment safety.",
            "This gate requires 100% completed paired training and complete TensorBoard metric steps.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = gate(args.artifact_root)
    except UnverifiablePolicyEvidence as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}, sort_keys=True))
        raise SystemExit(2) from exc
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
