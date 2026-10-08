"""Independently re-open native ManiSkill 2x2 replay data, not just manifests.

Usage (requires the four real .h5 + .json files, not merely digest strings):
 python -m research.kaggle_diffusion_policy_peg.verify_native_replay_outputs \
   /path/to/assay_output_factorial \
   /path/to/demos/converted

The first folder holds population/journal receipts. The second is the actual
Kaggle DEMO_ROOT/converted with one untouched native HDF5+JSON per treatment.
This deliberately refuses digest-only audit: anyone can type 64 hex chars.
All generated test fixtures are synthetic, NOT simulator evidence.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import h5py

try:
    from research.kaggle_diffusion_policy_peg.assay_design import FACTORIAL
    from research.kaggle_diffusion_policy_peg.audit_replay_journal import (
        audit_replay_journal,
    )
    from research.kaggle_diffusion_policy_peg.replay_itt import (
        UnverifiableReplayEvidence,
    )
except ModuleNotFoundError as exc:
    if exc.name != "research":
        raise
    from assay_design import FACTORIAL
    from audit_replay_journal import audit_replay_journal
    from replay_itt import UnverifiableReplayEvidence

NATIVE_FILE = "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
MAX_BYTES = 5 * 1024**3  # defensive per-raw-file scan limit; adjust via code review


def _hash_file(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise UnverifiableReplayEvidence("missing or symlinked native replay artifact")
    if path.stat().st_size > MAX_BYTES or path.stat().st_size == 0:
        raise UnverifiableReplayEvidence("native artifact has invalid size")
    digest = sha256()
    with path.open("rb") as data:
        for chunk in iter(lambda: data.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _native_census(h5_path: Path, json_path: Path, expected_seeds: list[int]) -> list[int]:
    try:
        metadata = json.loads(json_path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise UnverifiableReplayEvidence("unreadable native replay metadata") from exc
    episodes = metadata.get("episodes") if isinstance(metadata, dict) else None
    if not isinstance(episodes, list) or len(episodes) != len(expected_seeds):
        raise UnverifiableReplayEvidence("native replay missing original source episodes")
    by_seed: dict[int, bool] = {}
    trajectory_keys = set()
    try:
        with h5py.File(h5_path, "r") as h5:
            for item in episodes:
                if (
                    not isinstance(item, dict)
                    or type(item.get("episode_seed")) is not int
                    or type(item.get("episode_id")) is not int
                    or type(item.get("success")) is not bool
                    or type(item.get("elapsed_steps")) is not int
                ):
                    raise UnverifiableReplayEvidence("native episode identity/outcome invalid")
                seed = item["episode_seed"]
                traj_key = f"traj_{item['episode_id']}"
                if seed in by_seed or traj_key in trajectory_keys:
                    raise UnverifiableReplayEvidence("native source seed or trajectory duplicate")
                if traj_key not in h5:
                    raise UnverifiableReplayEvidence("native HDF5 trajectory missing")
                trajectory_keys.add(traj_key)
                traj = h5[traj_key]
                if "success" not in traj or "actions" not in traj:
                    raise UnverifiableReplayEvidence("native HDF5 missing stepwise evidence")
                flags, actions = traj["success"], traj["actions"]
                if (
                    not isinstance(flags, h5py.Dataset)
                    or flags.dtype.kind != "b"
                    or flags.ndim != 1
                    or not isinstance(actions, h5py.Dataset)
                    or actions.ndim < 1
                    or len(flags) == 0
                    or len(flags) != len(actions)
                    or len(flags) != item["elapsed_steps"]
                ):
                    raise UnverifiableReplayEvidence("native HDF5 success timeline corrupted")
                last = bool(flags[-1])
                if item["success"] != last:
                    raise UnverifiableReplayEvidence("native JSON/HDF5 final success mismatch")
                by_seed[seed] = last
            # The exact subset and order are predefined by the ORIGINAL
            # demos, rather than whichever replay file happens to survive.
            if set(by_seed) != set(expected_seeds):
                raise UnverifiableReplayEvidence("native source-episode population mismatch")
    except OSError as exc:
        raise UnverifiableReplayEvidence("unreadable native HDF5 file") from exc
    return [seed for seed in expected_seeds if by_seed[seed]]


def verify_native_replay_outputs(journal_root: Path, converted_root: Path) -> dict:
    """Only FULL four-cell original HDF5 evidence can earn native-verified status."""
    journal_root, converted_root = Path(journal_root), Path(converted_root)
    overview = audit_replay_journal(journal_root)
    if overview["status"] != "source_pop_replay_descriptive_only":
        raise UnverifiableReplayEvidence("four real replay arms not completed")
    pre = json.loads(
        (journal_root / "source_population_precommit.json").read_text(encoding="utf-8")
    )
    original_seeds = [row["episode_seed"] for row in pre["source_episodes"]]
    verified: dict[str, dict] = {}
    for arm in FACTORIAL:
        ledger_path = journal_root / "per_arm_replay" / f"{arm.name}.json"
        item = json.loads(ledger_path.read_text(encoding="utf-8"))
        directory = converted_root / arm.name / "PegInsertionSide-v1" / "motionplanning"
        h5_path = directory / NATIVE_FILE
        metadata_path = h5_path.with_suffix(".json")
        h5_digest = _hash_file(h5_path)
        json_digest = _hash_file(metadata_path)
        if (
            h5_digest != item["converted_hdf5_sha256"]
            or json_digest != item["converted_metadata_sha256"]
        ):
            raise UnverifiableReplayEvidence(
                f"{arm.name} native HDF5 or metadata content hash mismatch"
            )
        actual_successes = _native_census(h5_path, metadata_path, original_seeds)
        if actual_successes != item["successful_episode_seeds"]:
            raise UnverifiableReplayEvidence(
                f"{arm.name} native terminal outcomes disagree with claimed replay ledger"
            )
        verified[arm.name] = {
            "real_files_checked": True,
            "hdf5_sha256": h5_digest,
            "metadata_sha256": json_digest,
            "original_episodes": len(original_seeds),
            "native_terminal_successes": len(actual_successes),
        }
    return {
        "status": "SOURCE_FILES_AND_NATIVE_TERMINAL_OUTCOMES_VERIFIED",
        "estimator": "original-source-episode replay only; NOT policy performance",
        "original_episodes": len(original_seeds),
        "per_arm_native": verified,
        "descriptive_replay_contrasts": overview["population_replay_contrasts"],
        "limitations": [
            "Files and claimed results are author-controlled; no independent execution attestation.",
            "No four-arm Kaggle execution is present merely because synthetic tests pass.",
            "No learned-policy training gain, external reproduction, or physical robot safety proven.",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("assay_output_factorial", type=Path)
    p.add_argument("converted_root", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    try:
        result = verify_native_replay_outputs(
            a.assay_output_factorial, a.converted_root
        )
    except (OSError, KeyError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "REJECTED", "reason": str(exc)}))
        raise SystemExit(2) from exc
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.output:
        a.output.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
