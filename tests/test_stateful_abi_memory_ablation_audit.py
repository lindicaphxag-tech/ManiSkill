"""CPU-only falsification tests for the frozen action-memory study denominator."""
import json
import tempfile
import unittest
from pathlib import Path

from research.stateful_abi_memory_aggregate import aggregate, ARMS, MODEL, PROTOCOL


class FrozenMemoryAblationAuditor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for chunk in range(4):
            seeds = list(range(22001 + 8 * chunk, 22009 + 8 * chunk))
            rows = []
            for seed in seeds:
                k = seed - 22001
                row = {
                    "seed": seed,
                    "initial_obs_diff": {a: 0.0 for a in ARMS if a != "source"},
                    "steps": {a: 50 for a in ARMS},
                    "success_once": {
                        "source": k < 28,
                        "memory": k < 8,
                        "projected": k < 28,
                        "memory_blind_projected": 8 <= k < 26,
                        "naive": k < 2,
                    },
                    "refusals": {},
                    "approximations": {},
                    "max_required_native_amp": 1.0,
                }
                rows.append(row)
            doc = {
                "seed_chunk": str(chunk),
                "seed_list": seeds,
                "all_preregistered_seeds": [22001, 22032],
                "checkpoint_sha256": MODEL,
                "training_performed": False,
                "backend": "physx_cpu",
                "protocol": PROTOCOL,
                "episodes": rows,
                "success_count": {
                    arm: sum(int(r["success_once"][arm]) for r in rows)
                    for arm in ARMS
                },
            }
            self.write(chunk, doc)

    def tearDown(self):
        self.tmp.cleanup()

    def file(self, chunk):
        return self.root / f"stateful_abi_memory_ablation_chunk_{chunk}.json"

    def load(self, chunk):
        return json.loads(self.file(chunk).read_text())

    def write(self, chunk, record):
        self.file(chunk).write_text(json.dumps(record))

    def test_complete_positive_single_task_mechanism(self):
        d = aggregate(self.root)
        self.assertEqual(d["total_distinct_original_states"], 32)
        self.assertEqual(d["successful_episodes_by_arm"]["projected"], 28)
        self.assertEqual(d["successful_episodes_by_arm"]["memory_blind_projected"], 18)
        self.assertEqual(d["primary_memory_projected_only"], 10)
        self.assertEqual(d["primary_memory_blind_only"], 0)
        self.assertEqual(d["status"], "MECHANISM_SUPPORTED_SINGLE_TASK")
        self.assertFalse(d["independent_third_party_replication"])

    def test_null_result_is_retained_not_silently_selected(self):
        for c in range(4):
            d = self.load(c)
            for row in d["episodes"]:
                row["success_once"]["memory_blind_projected"] = row["success_once"]["projected"]
            d["success_count"]["memory_blind_projected"] = d["success_count"]["projected"]
            self.write(c, d)
        r = aggregate(self.root)
        self.assertEqual(r["status"], "MECHANISM_NOT_SUPPORTED")
        self.assertEqual(r["primary_net_benefit"], 0)

    def test_source_incompetence_is_separate_gate(self):
        for c in range(4):
            d = self.load(c)
            for row in d["episodes"]:
                row["success_once"]["source"] = False
            d["success_count"]["source"] = 0
            self.write(c, d)
        self.assertEqual(aggregate(self.root)["status"], "SOURCE_INCOMPETENT")

    def test_missing_seed_rejected(self):
        d = self.load(0)
        d["episodes"].pop()
        self.write(0, d)
        with self.assertRaises(ValueError):
            aggregate(self.root)

    def test_duplicated_or_swapped_seed_rejected(self):
        d = self.load(1)
        d["episodes"][0]["seed"] = d["episodes"][1]["seed"]
        self.write(1, d)
        with self.assertRaises(ValueError):
            aggregate(self.root)

    def test_tampered_checkpoint_rejected(self):
        d = self.load(2)
        d["checkpoint_sha256"] = "not the frozen public policy"
        self.write(2, d)
        with self.assertRaises(ValueError):
            aggregate(self.root)

    def test_success_denominator_tampering_rejected(self):
        d = self.load(3)
        d["success_count"]["projected"] += 1
        self.write(3, d)
        with self.assertRaises(ValueError):
            aggregate(self.root)

    def test_state_observation_mismatch_rejected(self):
        d = self.load(0)
        d["episodes"][0]["initial_obs_diff"]["memory_blind_projected"] = 0.02
        self.write(0, d)
        with self.assertRaises(ValueError):
            aggregate(self.root)

    def test_nonexact_projection_cannot_be_mislabelled(self):
        d = self.load(0)
        d["episodes"][0]["approximations"] = {
            "memory_blind_projected": [{"exactness": "EXACT", "step": 2}]
        }
        self.write(0, d)
        with self.assertRaises(ValueError):
            aggregate(self.root)

    def test_unexpected_files_and_incomplete_chunk_rejected(self):
        self.file(3).unlink()
        with self.assertRaises(ValueError):
            aggregate(self.root)


if __name__ == "__main__":
    unittest.main()
