"""No-GPU synthetic adversarial audit of the prospective 64-state shadow comparison."""
import json
import tempfile
import unittest
from pathlib import Path

from research.action_abi_shadow_aggregate import aggregate, ARMS, TASKS, PROTOCOL, HF_REVISION


class ShadowAuditTest(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.folder = Path(self.t.name)
        for name, spec in TASKS.items():
            for chunk in range(4):
                seeds = list(range(spec["first"] + chunk * 8,
                                   spec["first"] + chunk * 8 + 8))
                episodes = []
                for i, seed in enumerate(seeds):
                    k = chunk * 8 + i
                    success = dict(source=k < 29, memory=k < 17,
                                   projected=k < 30, stateless=k < 12,
                                   naive=k < 12, shadow=k < 30)
                    episodes.append(dict(
                        seed=seed, success_once=success,
                        initial_obs_diff={a: 0.0 for a in ARMS if a != "source"},
                        steps={a: 25 for a in ARMS},refusals={},approximations={},
                        shadow_max_position_goal_residual_m=1e-8,
                        shadow_max_rotation_goal_residual_rad=1e-8))
                data=dict(
                    task=spec["env"],seed_chunk=str(chunk),
                    seed_list=seeds,all_preregistered_seeds=[
                        spec["first"],spec["first"]+31],
                    checkpoint_sha256=spec["sha"],hf_revision=HF_REVISION,
                    protocol=PROTOCOL,training_performed=False,backend="physx_cpu",
                    episodes=episodes,
                    success_count={a:sum(int(r["success_once"][a]) for r in episodes)
                                   for a in ARMS})
                self.save(name,chunk,data)

    def tearDown(self):
        self.t.cleanup()

    def name(self,task,chunk):
        return self.folder / f"abi_shadow_{task}_chunk_{chunk}.json"

    def load(self,task,chunk):
        return json.loads(self.name(task,chunk).read_text())

    def save(self,task,chunk,data):
        self.name(task,chunk).write_text(json.dumps(data))

    def test_frozen_complete_six_arm_replay(self):
        r=aggregate(self.folder)
        self.assertEqual(r["n_original_task_states"],64)
        for task in TASKS:
            self.assertEqual(r["results"][task]["shadow_observer_gate"],"MATCHED")
            self.assertEqual(r["results"][task]["matched_episode_outcomes"],32)

    def test_null_or_negative_shadow_result_retained(self):
        for chunk in range(4):
            block=self.load("pull_cube",chunk)
            for row in block["episodes"]:
                row["success_once"]["shadow"]=False
            block["success_count"]["shadow"]=0
            self.save("pull_cube",chunk,block)
        self.assertEqual(aggregate(self.folder)["results"]["pull_cube"]
                         ["shadow_observer_gate"],"NOT_MATCHED")

    def test_incompetent_original_policy_has_separate_status(self):
        for chunk in range(4):
            block=self.load("stack_cube",chunk)
            for row in block["episodes"]:
                row["success_once"]["source"]=False
            block["success_count"]["source"]=0
            self.save("stack_cube",chunk,block)
        self.assertEqual(aggregate(self.folder)["results"]["stack_cube"]
                         ["shadow_observer_gate"],"SOURCE_INCOMPETENT")

    def test_goal_residual_falsifies_equivalence_even_with_good_scores(self):
        block=self.load("stack_cube",0)
        block["episodes"][2]["shadow_max_position_goal_residual_m"]=0.001
        self.save("stack_cube",0,block)
        self.assertEqual(aggregate(self.folder)["results"]["stack_cube"]
                         ["shadow_observer_gate"],"NOT_MATCHED")

    def test_fail_closed_on_duplicate_missing_or_relabelled_seeds(self):
        self.name("pull_cube",3).unlink()
        with self.assertRaises(ValueError): aggregate(self.folder)

    def test_fail_closed_on_checkpoint_swap(self):
        block=self.load("stack_cube",0)
        block["checkpoint_sha256"]="unknown"
        self.save("stack_cube",0,block)
        with self.assertRaises(ValueError): aggregate(self.folder)

    def test_fail_closed_on_not_exact_misrepresentation(self):
        block=self.load("pull_cube",0)
        block["episodes"][0]["approximations"]={
            "shadow":[{"exactness":"EXACT"}]}
        self.save("pull_cube",0,block)
        with self.assertRaises(ValueError): aggregate(self.folder)

    def test_fail_closed_on_missing_history_or_observation_and_state(self):
        block=self.load("stack_cube",2)
        del block["episodes"][3]["success_once"]["shadow"]
        self.save("stack_cube",2,block)
        with self.assertRaises(ValueError): aggregate(self.folder)
        block=self.load("stack_cube",2)
        block["episodes"][3]["success_once"]["shadow"]=False
        block["episodes"][4]["initial_obs_diff"]["shadow"]=0.1
        self.save("stack_cube",2,block)
        with self.assertRaises(ValueError): aggregate(self.folder)


if __name__=="__main__":
    unittest.main()
