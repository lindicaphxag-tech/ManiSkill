"""Falsification tests for pre-selection, source-seed-paired replay effects.

All test data here are synthetic fixtures; no result is ManiSkill GPU output.
"""
from __future__ import annotations

import ast
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import unittest

from research.kaggle_diffusion_policy_peg.assay_design import FACTORIAL
from research.kaggle_diffusion_policy_peg.replay_itt import (
    UnverifiableReplayEvidence,
    build_replay_record,
    evaluate_replay_record,
)


def fixture():
    episodes = [
        {"episode_id": 100 + i, "episode_seed": seed}
        for i, seed in enumerate([21, 42, 63, 84])
    ]
    # The unit test does not fake robot dynamics: these are intentionally
    # artificial *binary* replay outcomes to test the acceptance algebra.
    success = {
        "upstream_baseline": [21, 63],
        "converter_pr1495_only": [21, 42],
        "controller_pr1472_only": [21],
        "combined_pr1495_pr1472": [21, 42, 63],
    }
    dataset = {
        "repository": "haosulab/ManiSkill_Demonstrations",
        "revision": "d674485bbffdd533914e52d272fdda34c0515608",
        "path": "demos/PegInsertionSide-v1.zip",
        "sha256": "7d61e4319a0395b220574f1e26ea65bd4ad1406387fbbea96a2ddbb6a9c",
        "size_bytes": 29475456,
    }
    return build_replay_record(
        selected_source_episodes=episodes,
        successful_seeds_by_arm=success,
        dataset_identity=dataset,
    )


class IntentionToReplayTests(unittest.TestCase):
    def setUp(self):
        self.record = fixture()

    def _refused(self, fragment):
        with self.assertRaisesRegex(UnverifiableReplayEvidence, fragment):
            evaluate_replay_record(self.record)

    def test_full_source_population_has_true_four_cell_differences(self):
        x = evaluate_replay_record(self.record)
        self.assertEqual(x["status"], "source_pop_replay_descriptive_only")
        self.assertEqual(x["original_episodes"], 4)
        self.assertEqual(
            [x["per_arm"][a.name]["replay_successes"] for a in FACTORIAL],
            [2, 2, 1, 3],
        )
        self.assertEqual(x["all_four_successes"], 1)
        self.assertEqual(x["excluded_from_common_training_subset"], 3)
        self.assertEqual(x["per_episode_binary_pattern_counts"], {
            "0000": 1, "0101": 1, "1001": 1, "1111": 1
        })
        self.assertEqual(
            x["population_replay_contrasts"]["difference_in_differences"], 0.5,
        )
        self.assertEqual(
            x["paired_discordant_replays"]["converter_pr1495_only__vs__upstream_baseline"],
            {"gain_only": 1, "harm_only": 1},
        )

    def test_intersection_success_cannot_be_used_as_pop_replay_denominator(self):
        x = evaluate_replay_record(self.record)
        self.assertEqual(x["all_four_selected_fraction"], 0.25)
        self.assertEqual(
            x["per_arm"]["controller_pr1472_only"]["replay_success_rate"], 0.25,
        )
        # Everyone is successful *on the selected common-only subset*,
        # trivially hiding 3 other predeclared episode outcomes.
        self.assertTrue(
            any("No post-treatment survivor" in y for y in x["limitations"])
        )

    def test_reorders_or_drops_predeclared_seeds_refused(self):
        self.record["original_source_episodes"].pop()
        self._refused("original source episodes")

    def test_wrong_source_assignment_refused(self):
        self.record["arms"][2]["source_commit"] = self.record["arms"][1]["source_commit"]
        self._refused("source/overlay mismatched")

    def test_modified_arm_seed_hash_refused(self):
        self.record["arms"][1]["successful_episode_seeds"] = [21]
        self._refused("corrupted/reordered/unknown")

    def test_unknown_source_seed_refused(self):
        self.record["arms"][0]["successful_episode_seeds"] = [21, 999]
        self._refused("corrupted/reordered/unknown")

    def test_missing_intervention_arm_refused(self):
        self.record["arms"].pop()
        self._refused("four frozen intervention")

    def test_wrong_source_dataset_identity_refused(self):
        self.record["source_dataset"]["sha256"] = "bad"
        self._refused("original archive identity")

    def test_replay_script_writes_itt_before_post_treatment_selection(self):
        script = (
            Path(__file__).resolve().parents[1] / "run_assay_factorial.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(script)
        source = [
            x for x in ast.walk(tree)
            if isinstance(x, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "replay_itt_record"
                for t in x.targets
            )
        ]
        intersection = [
            x for x in ast.walk(tree)
            if isinstance(x, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "common_seeds"
                for t in x.targets
            )
        ]
        self.assertEqual(len(source), 1)
        self.assertEqual(len(intersection), 1)
        self.assertLess(source[0].lineno, intersection[0].lineno)
        self.assertIn('"replay_intention_to_treat.json"', script)
        self.assertIn('"original_source_episodes"', script)

    def test_roundtrip_json_is_stable(self):
        self.assertEqual(
            evaluate_replay_record(json.loads(json.dumps(self.record))),
            evaluate_replay_record(self.record),
        )


if __name__ == "__main__":
    unittest.main()
