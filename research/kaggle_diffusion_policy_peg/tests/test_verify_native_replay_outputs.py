"""Reconcile synthetic native trajectory bytes independently from manifest text.

These are *artificial* two-timestep HDF5 fixtures. No GPU, simulator or
external validation is claimed. The tests exercise file content, not just a
64-character digest shape.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import h5py

from research.kaggle_diffusion_policy_peg.assay_design import FACTORIAL
from research.kaggle_diffusion_policy_peg.replay_itt import (
    _digest, UnverifiableReplayEvidence,
)
from research.kaggle_diffusion_policy_peg.verify_native_replay_outputs import (
    NATIVE_FILE, verify_native_replay_outputs,
)
from test_replay_itt import fixture


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


class ActualNativeReplayVerificationTests(unittest.TestCase):
    def setUp(self):
        self.work = TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        self.out = self.root / "assay_output_factorial"
        self.native = self.root / "demos" / "converted"
        (self.out / "per_arm_replay").mkdir(parents=True)
        sample = fixture()
        self.episodes = sample["original_source_episodes"]
        self.source_seeds = [e["episode_seed"] for e in self.episodes]
        self.successes = {
            row["arm"]: row["successful_episode_seeds"] for row in sample["arms"]
        }
        pre = {
            "schema": "maniskill-source-population-precommit-v1",
            "source_dataset": sample["source_dataset"],
            "source_episodes": self.episodes,
            "source_episode_seeds_sha256": _digest(self.source_seeds),
            "four_frozen_interventions": [
                {
                    "arm": a.name, "source_commit": a.source_commit,
                    "controller_overlay_commit": a.controller_overlay_commit,
                }
                for a in FACTORIAL
            ],
        }
        self.write_json(self.out / "source_population_precommit.json", pre)
        self.write_json(self.out / "replay_intention_to_treat.json", sample)
        for arm in FACTORIAL:
            self.create_native(arm.name)
        self.regenerate_ledgers()

    def write_json(self, path, data):
        path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")

    def native_files(self, arm):
        h5_path = (
            self.native / arm / "PegInsertionSide-v1"
            / "motionplanning" / NATIVE_FILE
        )
        return h5_path, h5_path.with_suffix(".json")

    def create_native(self, arm):
        path, metadata_path = self.native_files(arm)
        path.parent.mkdir(parents=True, exist_ok=True)
        good = set(self.successes[arm])
        rows = []
        with h5py.File(path, "w") as h5:
            for i, entry in enumerate(self.episodes):
                passed = entry["episode_seed"] in good
                trajectory = h5.create_group(f"traj_{i}")
                trajectory.create_dataset("actions", data=[[0.0], [0.1]])
                trajectory.create_dataset(
                    "success", data=[False, passed], dtype=bool
                )
                rows.append({
                    "episode_id": i, "episode_seed": entry["episode_seed"],
                    "success": passed, "elapsed_steps": 2,
                })
        self.write_json(metadata_path, {"episodes": rows})

    def regenerate_ledgers(self):
        for arm in FACTORIAL:
            h5_file, metadata_file = self.native_files(arm.name)
            passed = self.successes[arm.name]
            row = {
                "schema": "maniskill-completed-arm-replay-v1",
                "arm": arm.name, "source_commit": arm.source_commit,
                "controller_overlay_commit": arm.controller_overlay_commit,
                "production_tree": "a" * 40,
                "source_population_sha256": _digest(self.source_seeds),
                "native_outcome_verifier": "RecordEpisode HDF5 terminal success matches JSON",
                "converted_hdf5_sha256": hash_file(h5_file),
                "converted_metadata_sha256": hash_file(metadata_file),
                "successful_episode_seeds": passed,
                "successful_count": len(passed),
                "failed_count": len(self.source_seeds) - len(passed),
                "full_source_census": True,
                "log_file": f"replay_{arm.name}.log",
                "replay_status": "completed",
            }
            self.write_json(
                self.out / "per_arm_replay" / f"{arm.name}.json", row
            )

    def reject(self, reason):
        with self.assertRaisesRegex(UnverifiableReplayEvidence, reason):
            verify_native_replay_outputs(self.out, self.native)

    def test_reopened_real_hdf5_files_match_four_arm_journal(self):
        value = verify_native_replay_outputs(self.out, self.native)
        self.assertEqual(
            value["status"], "SOURCE_FILES_AND_NATIVE_TERMINAL_OUTCOMES_VERIFIED"
        )
        self.assertEqual(value["original_episodes"], 4)
        self.assertEqual(
            [value["per_arm_native"][a.name]["native_terminal_successes"]
             for a in FACTORIAL], [2, 2, 1, 3]
        )
        self.assertTrue(any("author-controlled" in x for x in value["limitations"]))

    def test_manifest_hash_shape_with_missing_native_files_is_not_evidence(self):
        native, _ = self.native_files(FACTORIAL[0].name)
        native.unlink()
        self.reject("missing or symlinked native replay artifact")

    def test_bogus_native_file_digest_even_if_64_chars_is_rejected(self):
        file = self.out / "per_arm_replay" / f"{FACTORIAL[1].name}.json"
        record = json.loads(file.read_text())
        record["converted_hdf5_sha256"] = "f" * 64
        self.write_json(file, record)
        self.reject("content hash mismatch")

    def test_json_swapped_label_with_updated_sha_still_refused(self):
        _, metadata = self.native_files(FACTORIAL[1].name)
        rows = json.loads(metadata.read_text())
        rows["episodes"][0]["success"] = False
        self.write_json(metadata, rows)
        self.regenerate_ledgers()
        self.reject("native JSON/HDF5 final success mismatch")

    def test_hdf5_terminal_outcome_changed_with_rehashed_file_refused(self):
        h5_file, _ = self.native_files(FACTORIAL[0].name)
        with h5py.File(h5_file, "a") as h5:
            h5["traj_0"]["success"][-1] = False
        self.regenerate_ledgers()
        self.reject("native JSON/HDF5 final success mismatch")

    def test_episode_removed_with_updated_sha_refused(self):
        h5_file, metadata_file = self.native_files(FACTORIAL[2].name)
        with h5py.File(h5_file, "a") as h5:
            del h5["traj_3"]
        self.regenerate_ledgers()
        self.reject("native HDF5 trajectory missing")

    def test_unknown_seed_in_rehashed_native_metadata_denied(self):
        _, metadata = self.native_files(FACTORIAL[1].name)
        rows = json.loads(metadata.read_text())
        rows["episodes"][0]["episode_seed"] = 999
        self.write_json(metadata, rows)
        self.regenerate_ledgers()
        self.reject("native source-episode population mismatch")

    def test_empty_successful_arm_is_valid_if_native_failure_evidence_present(self):
        arm = FACTORIAL[2].name
        self.successes[arm] = []
        self.create_native(arm)
        self.regenerate_ledgers()
        value = verify_native_replay_outputs(self.out, self.native)
        # The original precommit/journal comparison is still independent:
        # update the second source-episode outcome track consistently.
        self.assertEqual(value["per_arm_native"][arm]["native_terminal_successes"], 0)

    def test_symlinked_original_native_file_refused(self):
        h5_file, _ = self.native_files(FACTORIAL[0].name)
        original = h5_file.with_name("original.h5")
        h5_file.rename(original)
        h5_file.symlink_to(original)
        self.reject("symlinked native replay artifact")


if __name__ == "__main__":
    unittest.main()
