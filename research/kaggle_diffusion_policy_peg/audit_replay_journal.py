"""Review intervention replay evidence, including interrupted and zero-success arms.

The sampler population was committed before *any* treatment. Each arm's
production-source result is a separate durable record. Absent arm data means
UNKNOWN, never a failed replay and never a full four-arm comparison.

Only completed, matched four-arm records are promoted to a descriptive
full-source population comparison by replay_itt.evaluate_replay_record.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from research.kaggle_diffusion_policy_peg.assay_design import FACTORIAL
    from research.kaggle_diffusion_policy_peg.replay_itt import (
        UnverifiableReplayEvidence, build_replay_record, evaluate_replay_record,
        _digest,
    )
except ModuleNotFoundError as exc:
    if exc.name != "research":
        raise
    from assay_design import FACTORIAL
    from replay_itt import (
        UnverifiableReplayEvidence, build_replay_record, evaluate_replay_record,
        _digest,
    )


def audit_replay_journal(root: Path) -> dict:
    root = Path(root)
    population_file = root / "source_population_precommit.json"
    if not population_file.is_file():
        raise UnverifiableReplayEvidence(
            "source population not frozen before intervention; no comparison"
        )
    pre = json.loads(population_file.read_text(encoding="utf-8"))
    if pre.get("schema") != "maniskill-source-population-precommit-v1":
        raise UnverifiableReplayEvidence("invalid pre-intervention source commitment")
    episodes = pre.get("source_episodes")
    if not isinstance(episodes, list) or not episodes:
        raise UnverifiableReplayEvidence("missing pre-intervention episode list")
    seeds = [ep.get("episode_seed") for ep in episodes]
    indices = [ep.get("episode_id") for ep in episodes]
    if (
        any(type(x) is not int for x in seeds + indices)
        or len(set(seeds)) != len(seeds)
        or len(set(indices)) != len(indices)
        or pre.get("source_episode_seeds_sha256") != _digest(seeds)
    ):
        raise UnverifiableReplayEvidence("unverifiable initial source-seed population")
    assignments = pre.get("four_frozen_interventions")
    expected = [
        {"arm": arm.name, "source_commit": arm.source_commit,
         "controller_overlay_commit": arm.controller_overlay_commit}
        for arm in FACTORIAL
    ]
    if assignments != expected:
        raise UnverifiableReplayEvidence("treatment assignment differs from frozen 2x2 protocol")
    directory = root / "per_arm_replay"
    files = list(directory.glob("*.json")) if directory.is_dir() else []
    allowed = {f"{arm.name}.json" for arm in FACTORIAL}
    if any(file.name not in allowed for file in files):
        raise UnverifiableReplayEvidence("unknown intervention arm in results directory")
    arm_successes: dict[str, list[int]] = {}
    partial = {}
    source_set = set(seeds)
    for arm in FACTORIAL:
        file = directory / f"{arm.name}.json"
        if not file.is_file():
            partial[arm.name] = {
                "status": "UNKNOWN_NOT_COMPLETED",
                "replay_successes": None, "original_episodes": len(seeds),
            }
            continue
        record = json.loads(file.read_text(encoding="utf-8"))
        if (
            record.get("schema") != "maniskill-completed-arm-replay-v1"
            or record.get("replay_status") != "completed"
            or record.get("arm") != arm.name
            or record.get("source_commit") != arm.source_commit
            or record.get("controller_overlay_commit") != arm.controller_overlay_commit
            or record.get("source_population_sha256") != _digest(seeds)
            or not isinstance(record.get("production_tree"), str)
            or len(record["production_tree"]) != 40
        ):
            raise UnverifiableReplayEvidence("arm result identity does not match frozen source")
        successes = record.get("successful_episode_seeds")
        if (
            not isinstance(successes, list)
            or any(type(s) is not int for s in successes)
            or len(set(successes)) != len(successes)
            or not set(successes).issubset(source_set)
            or successes != [s for s in seeds if s in set(successes)]
            or record.get("successful_count") != len(successes)
        ):
            raise UnverifiableReplayEvidence("corrupt, reordered or foreign per-arm replay seeds")
        arm_successes[arm.name] = successes
        partial[arm.name] = {
            "status": "COMPLETED",
            "replay_successes": len(successes),
            "original_episodes": len(seeds),
        }
    if len(arm_successes) < 4:
        return {
            "status": "INCOMPLETE_NO_FOUR_CELL_ESTIMATE",
            "original_episodes": len(seeds),
            "original_source_seed_sha256": _digest(seeds),
            "arms": partial,
            "limitations": [
                "Missing arms are unknown, NOT zero-success or failure measurements.",
                "No selected-subset or full-population causal contrast is computed.",
                "No learned Diffusion Policy metrics are available from this journal.",
            ],
        }
    full = build_replay_record(
        selected_source_episodes=episodes,
        successful_seeds_by_arm=arm_successes,
        dataset_identity=pre.get("source_dataset", {}),
    )
    original_itt_file = root / "replay_intention_to_treat.json"
    if original_itt_file.is_file():
        original = json.loads(original_itt_file.read_text(encoding="utf-8"))
        # The two independently written audit tracks must byte-semantically
        # agree on source population, treatment assignments and outcomes.
        if original != full:
            raise UnverifiableReplayEvidence(
                "independently recorded full replay census contradicts arm journal"
            )
    result = evaluate_replay_record(full)
    result["source_audit"] = "four_arm_journal_matches_frozen_population"
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("assay_output", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        result = audit_replay_journal(args.assay_output)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}))
        raise SystemExit(2) from exc
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
