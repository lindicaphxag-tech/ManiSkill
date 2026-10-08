"""No GPU required: adversarial audit of 64 prespecified genuine task states."""
import json
import tempfile
import unittest
from pathlib import Path

from research.action_abi_pull_stack_aggregate import TASKS, ARMS, HF_REVISION, PROTOCOL, aggregate


class CrossTaskAuditor(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        for task, spec in TASKS.items():
            for chunk in range(4):
                subset = spec["seeds"][8*chunk:8*chunk+8]
                episodes = []
                for n, seed in enumerate(subset):
                    i = chunk*8+n
                    success = {
                        "source": i < 29,
                        "memory": i < 26,
                        "projected": i < 29,
                        "stateless": 8 <= i < 25,
                        "naive": i < 10,
                    }
                    episodes.append({
                        "seed": seed,
                        "success_once": success,
                        "initial_obs_diff": {a:0.0 for a in ARMS if a != "source"},
                        "steps": {a:30 for a in ARMS},
                        "refusals": {},
                        "approximations": {},
                    })
                block = {
                    "task": spec["task"], "seed_chunk": str(chunk),
                    "seed_list": subset,
                    "all_preregistered_seeds": [spec["seeds"][0],spec["seeds"][-1]],
                    "checkpoint_sha256": spec["sha256"],
                    "hf_revision": HF_REVISION,
                    "training_performed": False, "backend": "physx_cpu",
                    "protocol": PROTOCOL,
                    "episodes": episodes,
                    "success_count": {
                        a: sum(int(row["success_once"][a]) for row in episodes)
                        for a in ARMS
                    },
                }
                self.save(task,chunk,block)

    def tearDown(self):
        self.temp.cleanup()

    def filename(self,task,chunk):
        return self.folder / f"abi_independent_{task}_chunk_{chunk}.json"

    def load(self,task,chunk):
        return json.loads(self.filename(task,chunk).read_text())

    def save(self,task,chunk,content):
        self.filename(task,chunk).write_text(json.dumps(content))

    def test_all_64_seeds_and_two_model_hashes(self):
        result = aggregate(self.folder)
        self.assertEqual(result["total_original_task_states"], 64)
        self.assertEqual(set(result["results"]), set(TASKS))
        for v in result["results"].values():
            self.assertEqual(v["status"],"PREDECLARED_MEMORY_GAIN_PRESENT")
            self.assertEqual(v["n"],32)
            self.assertFalse(result["third_party_independent_reproduction"])

    def test_incompetent_original_source_cannot_establish_transfer(self):
        d=self.load("stack_cube",0)
        for row in d["episodes"]: row["success_once"]["source"]=False
        d["success_count"]["source"]=0
        self.save("stack_cube",0,d)
        self.assertEqual(aggregate(self.folder)["results"]["stack_cube"]["status"],
                         "SOURCE_INCOMPETENT")

    def test_null_gain_kept(self):
        for chunk in range(4):
            d=self.load("pull_cube",chunk)
            for row in d["episodes"]:
                row["success_once"]["stateless"]=row["success_once"]["projected"]
            d["success_count"]["stateless"]=d["success_count"]["projected"]
            self.save("pull_cube",chunk,d)
        self.assertEqual(aggregate(self.folder)["results"]["pull_cube"]["status"],
                         "PREDECLARED_MEMORY_GAIN_NOT_PRESENT")

    def test_missing_chunk_fail_closed(self):
        self.filename("pull_cube",3).unlink()
        with self.assertRaises(ValueError):aggregate(self.folder)

    def test_missing_seed_or_outcome_fail_closed(self):
        d=self.load("stack_cube",1)
        d["episodes"][0]["seed"]=d["episodes"][1]["seed"]
        self.save("stack_cube",1,d)
        with self.assertRaises(ValueError):aggregate(self.folder)

    def test_checkpoint_substitution_fail_closed(self):
        d=self.load("pull_cube",2)
        d["checkpoint_sha256"]="some other source trained model"
        self.save("pull_cube",2,d)
        with self.assertRaises(ValueError):aggregate(self.folder)

    def test_unverified_obs_abi_fail_closed(self):
        d=self.load("stack_cube",3)
        d["episodes"][0]["initial_obs_diff"]["stateless"]=0.01
        self.save("stack_cube",3,d)
        with self.assertRaises(ValueError):aggregate(self.folder)

    def test_approximation_not_exact(self):
        d=self.load("pull_cube",0)
        d["episodes"][0]["approximations"]={"projected":[{"exactness":"EXACT"}]}
        self.save("pull_cube",0,d)
        with self.assertRaises(ValueError):aggregate(self.folder)


if __name__=="__main__":
    unittest.main()
