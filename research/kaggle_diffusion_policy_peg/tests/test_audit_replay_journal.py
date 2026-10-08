"""Pure-stdlib adversarial tests of source-frozen, crash-stable replay accounting."""
from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research.kaggle_diffusion_policy_peg.assay_design import FACTORIAL
from research.kaggle_diffusion_policy_peg.audit_replay_journal import audit_replay_journal
from research.kaggle_diffusion_policy_peg.replay_itt import (
    UnverifiableReplayEvidence, _digest,
)
from test_replay_itt import fixture


class ReplayJournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "per_arm_replay").mkdir()
        original = fixture()
        self.episodes = original["original_source_episodes"]
        self.seeds = [x["episode_seed"] for x in self.episodes]
        self.pre = {
            "schema": "maniskill-source-population-precommit-v1",
            "source_dataset": original["source_dataset"],
            "source_episodes": self.episodes,
            "source_episode_seeds_sha256": _digest(self.seeds),
            "four_frozen_interventions": [
                {"arm": a.name, "source_commit": a.source_commit,
                 "controller_overlay_commit": a.controller_overlay_commit}
                for a in FACTORIAL
            ],
        }
        self._write(self.root / "source_population_precommit.json", self.pre)
        self.per_arm = {
            a["arm"]: a["successful_episode_seeds"] for a in original["arms"]
        }

    def tearDown(self):
        self.temp.cleanup()

    def _write(self, path, obj):
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    def write_arm(self, arm_name, successes=None):
        spec = next(a for a in FACTORIAL if a.name == arm_name)
        successes = self.per_arm[arm_name] if successes is None else successes
        data = {
            "schema": "maniskill-completed-arm-replay-v1",
            "arm": arm_name, "source_commit": spec.source_commit,
            "controller_overlay_commit": spec.controller_overlay_commit,
            "production_tree": "a"*40,
            "source_population_sha256": _digest(self.seeds),
            "successful_episode_seeds": successes,
            "successful_count": len(successes), "replay_status": "completed",
        }
        self._write(self.root / "per_arm_replay" / f"{arm_name}.json", data)
        return data

    def all_arms(self):
        for arm in FACTORIAL:
            self.write_arm(arm.name)

    def rejected(self, reason):
        with self.assertRaisesRegex(UnverifiableReplayEvidence, reason):
            audit_replay_journal(self.root)

    def test_zero_success_arm_is_measured_zero_not_an_execution_error(self):
        self.all_arms()
        self.write_arm(FACTORIAL[2].name, [])
        result = audit_replay_journal(self.root)
        self.assertEqual(result["status"], "source_pop_replay_descriptive_only")
        self.assertEqual(result["per_arm"][FACTORIAL[2].name]["replay_successes"], 0)
        self.assertEqual(result["original_episodes"], 4)
        self.assertEqual(result["all_four_successes"], 0)

    def test_incomplete_arm_is_unknown_and_no_four_cell_effect_estimated(self):
        self.write_arm(FACTORIAL[0].name)
        result = audit_replay_journal(self.root)
        self.assertEqual(result["status"], "INCOMPLETE_NO_FOUR_CELL_ESTIMATE")
        self.assertEqual(result["arms"][FACTORIAL[0].name]["replay_successes"], 2)
        self.assertIsNone(result["arms"][FACTORIAL[1].name]["replay_successes"])
        self.assertNotIn("population_replay_contrasts", result)

    def test_missing_precommit_refuses_all_results(self):
        self.all_arms()
        (self.root / "source_population_precommit.json").unlink()
        self.rejected("source population not frozen")

    def test_mismatched_source_population_hash_refused(self):
        self.all_arms()
        self.pre["source_episode_seeds_sha256"] = "0"*64
        self._write(self.root / "source_population_precommit.json", self.pre)
        self.rejected("unverifiable initial")

    def test_unknown_arm_result_refused(self):
        self.all_arms()
        (self.root / "per_arm_replay" / "smuggled_intervention.json").write_text("{}")
        self.rejected("unknown intervention arm")

    def test_changed_source_commit_refused(self):
        self.all_arms()
        path = self.root / "per_arm_replay" / f"{FACTORIAL[1].name}.json"
        data = json.loads(path.read_text())
        data["source_commit"] = "untrusted"
        self._write(path, data)
        self.rejected("arm result identity")

    def test_one_arm_reordered_source_seeds_refused(self):
        self.all_arms()
        path = self.root / "per_arm_replay" / f"{FACTORIAL[0].name}.json"
        data = json.loads(path.read_text())
        data["successful_episode_seeds"].reverse()
        self._write(path, data)
        self.rejected("corrupt, reordered")

    def test_contradictory_completed_census_refused(self):
        self.all_arms()
        original = fixture()
        original["arms"][0]["successful_episode_seeds"] = []
        self._write(self.root / "replay_intention_to_treat.json", original)
        self.rejected("contradicts arm journal")

    def test_executable_runner_precommits_before_first_arm_and_allows_zero(self):
        path = Path(__file__).resolve().parents[1] / "run_assay_factorial.py"
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        precommit = text.index('(OUTPUT / "source_population_precommit.json").write_text(')
        first_replay = text.index('    for arm, start_commit, extra_commit in arms:')
        first_intersection = text.index('    common_seeds = [')
        journal = text.index('(OUTPUT / "per_arm_replay" / f"{arm}.json").write_text(')
        self.assertLess(precommit, first_replay)
        self.assertLess(first_replay, journal)
        self.assertLess(journal, first_intersection)
        index_func = next(
            x for x in tree.body if isinstance(x, ast.FunctionDef)
            and x.name == "index_converted_episodes"
        )
        body = ast.get_source_segment(text, index_func)
        self.assertNotIn('if not result:', body)
        self.assertIn('return result', body)

    def test_full_four_arm_replay_no_filtering_of_failure_denominator(self):
        self.all_arms()
        result = audit_replay_journal(self.root)
        self.assertEqual(
            [result["per_arm"][arm.name]["replay_failures"] for arm in FACTORIAL],
            [2, 2, 3, 1],
        )
        self.assertEqual(result["all_four_successes"], 1)
        self.assertEqual(result["original_episodes"], 4)


if __name__ == "__main__":
    unittest.main()
