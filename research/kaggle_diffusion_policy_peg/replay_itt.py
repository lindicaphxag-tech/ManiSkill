"""Intention-to-replay provenance and paired source-seed causal diagnostics.

A converter/controller intervention can itself determine whether a raw demo
replays. Discarding failures by intersecting successful episodes across arms
creates a post-treatment selection problem. This module preserves every
PRE-DECLARED original source seed and every intervention outcome *before*
any learned policy is fitted.

Produces descriptive finite-source replay effects, not policy success gains,
statistical significance, calibrated safety probability or randomization
over source commits. No third-party simulation output is constructed here.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

try:
    from research.kaggle_diffusion_policy_peg.assay_design import FACTORIAL
except ModuleNotFoundError as exc:
    if exc.name != "research":
        raise
    from assay_design import FACTORIAL


class UnverifiableReplayEvidence(ValueError):
    pass


def _digest(source_seeds: list[int]) -> str:
    return sha256(
        json.dumps(source_seeds, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_replay_record(
    *,
    selected_source_episodes: list[dict[str, Any]],
    successful_seeds_by_arm: dict[str, list[int]],
    dataset_identity: dict[str, Any],
) -> dict[str, Any]:
    source_seeds = [record.get("episode_seed") for record in selected_source_episodes]
    episode_ids = [record.get("episode_id") for record in selected_source_episodes]
    if (
        not source_seeds
        or any(type(x) is not int for x in source_seeds + episode_ids)
        or len(set(source_seeds)) != len(source_seeds)
        or len(set(episode_ids)) != len(episode_ids)
    ):
        raise UnverifiableReplayEvidence("original source episodes are missing, duplicate or malformed")
    if set(successful_seeds_by_arm) != {arm.name for arm in FACTORIAL}:
        raise UnverifiableReplayEvidence("exact 2x2 source intervention assignments required")
    source_set = set(source_seeds)
    entries: list[dict[str, Any]] = []
    for arm in FACTORIAL:
        success = successful_seeds_by_arm[arm.name]
        if (
            len(success) != len(set(success))
            or not set(success).issubset(source_set)
            or any(type(value) is not int for value in success)
            or success != [s for s in source_seeds if s in set(success)]
        ):
            raise UnverifiableReplayEvidence(f"source-seed replay evidence corrupted in {arm.name}")
        entries.append({
            "arm": arm.name, "source_commit": arm.source_commit,
            "controller_overlay_commit": arm.controller_overlay_commit,
            "successful_episode_seeds": list(success),
            "successful_seed_sha256": _digest(success),
        })
    if not isinstance(dataset_identity, dict) or any(
        not isinstance(dataset_identity.get(key), (str, int))
        for key in ("repository", "revision", "path", "sha256", "size_bytes")
    ):
        raise UnverifiableReplayEvidence("frozen public source dataset identity required")
    return {
        "schema": "maniskill-source-episode-itt-v1",
        "interpretation": "descriptive source-seed paired replay only; not training",
        "source_dataset": {
            key: dataset_identity[key]
            for key in ("repository", "revision", "path", "sha256", "size_bytes")
        },
        "original_source_episodes": [
            {"episode_id": i, "episode_seed": s}
            for i, s in zip(episode_ids, source_seeds, strict=True)
        ],
        "original_source_seed_sha256": _digest(source_seeds),
        "arms": entries,
    }


def evaluate_replay_record(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("schema") != "maniskill-source-episode-itt-v1":
        raise UnverifiableReplayEvidence("unsupported or missing replay schema")
    episodes = record.get("original_source_episodes")
    if not isinstance(episodes, list) or not episodes:
        raise UnverifiableReplayEvidence("missing predeclared episode population")
    ids = [x.get("episode_id") for x in episodes]
    seeds = [x.get("episode_seed") for x in episodes]
    if (
        any(type(x) is not int for x in ids + seeds)
        or len(set(ids)) != len(ids)
        or len(set(seeds)) != len(seeds)
        or record.get("original_source_seed_sha256") != _digest(seeds)
    ):
        raise UnverifiableReplayEvidence("invalid or modified original source episodes")
    dataset = record.get("source_dataset", {})
    if (
        not isinstance(dataset, dict)
        or not isinstance(dataset.get("repository"), str)
        or not isinstance(dataset.get("revision"), str)
        or not isinstance(dataset.get("path"), str)
        or not isinstance(dataset.get("sha256"), str)
        or len(dataset["sha256"]) != 64
        or type(dataset.get("size_bytes")) is not int
        or dataset["size_bytes"] <= 0
    ):
        raise UnverifiableReplayEvidence("missing or malformed frozen original archive identity")
    arms = record.get("arms")
    if not isinstance(arms, list) or len(arms) != len(FACTORIAL):
        raise UnverifiableReplayEvidence("not exactly four frozen intervention cells")
    source_set = set(seeds)
    flags: dict[str, list[int]] = {}
    for arm, expected in zip(arms, FACTORIAL, strict=True):
        if (
            arm.get("arm") != expected.name
            or arm.get("source_commit") != expected.source_commit
            or arm.get("controller_overlay_commit") != expected.controller_overlay_commit
        ):
            raise UnverifiableReplayEvidence("source/overlay mismatched to 2x2 intervention")
        surviving = arm.get("successful_episode_seeds")
        if (
            not isinstance(surviving, list)
            or any(type(x) is not int for x in surviving)
            or len(set(surviving)) != len(surviving)
            or not set(surviving).issubset(source_set)
            or surviving != [s for s in seeds if s in set(surviving)]
            or arm.get("successful_seed_sha256") != _digest(surviving)
        ):
            raise UnverifiableReplayEvidence("corrupted/reordered/unknown source-seed replay evidence")
        surviving_set = set(surviving)
        flags[expected.name] = [int(seed in surviving_set) for seed in seeds]
    b, c, k, ck = (flags[arm.name] for arm in FACTORIAL)
    n = len(seeds)
    all_four = sum(all(group[i] for group in (b, c, k, ck)) for i in range(n))
    contrasts = {
        "converter_when_controller_legacy": sum(x-y for x,y in zip(c,b,strict=True))/n,
        "converter_when_controller_changed": sum(x-y for x,y in zip(ck,k,strict=True))/n,
        "controller_when_converter_legacy": sum(x-y for x,y in zip(k,b,strict=True))/n,
        "controller_when_converter_changed": sum(x-y for x,y in zip(ck,c,strict=True))/n,
        "difference_in_differences": sum(
            x-y-z+w for x,y,z,w in zip(ck,c,k,b,strict=True)
        )/n,
    }
    pairs = (
        ("converter_pr1495_only", "upstream_baseline"),
        ("controller_pr1472_only", "upstream_baseline"),
        ("combined_pr1495_pr1472", "upstream_baseline"),
        ("combined_pr1495_pr1472", "converter_pr1495_only"),
        ("combined_pr1495_pr1472", "controller_pr1472_only"),
    )
    discordances = {
        f"{treatment}__vs__{control}": {
            "gain_only": sum(t == 1 and c == 0 for t,c in zip(flags[treatment], flags[control],strict=True)),
            "harm_only": sum(t == 0 and c == 1 for t,c in zip(flags[treatment], flags[control],strict=True)),
        }
        for treatment, control in pairs
    }
    patterns = Counter(
        "".join(str(flags[a.name][i]) for a in FACTORIAL)
        for i in range(n)
    )
    return {
        "status": "source_pop_replay_descriptive_only",
        "original_episodes": n,
        "original_source_seed_sha256": _digest(seeds),
        "per_arm": {
            name: {
                "replay_successes": sum(binary),
                "original_episodes": n,
                "replay_success_rate": sum(binary)/n,
                "replay_failures": n-sum(binary),
            }
            for name,binary in flags.items()
        },
        "per_episode_pattern_order": [a.name for a in FACTORIAL],
        "per_episode_binary_pattern_counts": dict(sorted(patterns.items())),
        "all_four_successes": all_four,
        "all_four_selected_fraction": all_four/n,
        "excluded_from_common_training_subset": n-all_four,
        "population_replay_contrasts": contrasts,
        "paired_discordant_replays": discordances,
        "limitations": [
            "Replays are physical simulator conversions, not Diffusion Policy training success.",
            "Deterministic frozen-source code interventions are not independently randomized treatments.",
            "No iid source-seed sampling assumption or inferential p-value is claimed.",
            "No post-treatment survivor intersection is used as an effect denominator.",
            "The provenance record is author-generated and requires independent source archive verification.",
            "Training on a common survivor subset remains selected and does not estimate this full-source estimand.",
        ],
    }


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("replay_record", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        result = evaluate_replay_record(json.loads(args.replay_record.read_text(encoding="utf-8")))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}))
        raise SystemExit(2) from exc
    output = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.output is not None:
        args.output.write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
