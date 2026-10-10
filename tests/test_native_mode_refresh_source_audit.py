import json
import tempfile
import unittest
from pathlib import Path
from hashlib import sha256
from research.audit_native_mode_refresh_dev_physx import audit,TASKS

def fixture(root):
    for task,seeds in TASKS.items():
        rows=[]
        for seed in seeds:
            for truth in range(4):
                rows.append(dict(task=task,seed=seed,actual_ack_truth=truth,
                   pre_t4_native_action_prefix_max_abs=0.,
                   pre_t4_public_ee_xyz_max_abs_m=0.,
                   privileged_internal_write_count=0,privileged_runtime_mode_writes=2,
                   proposed_decision_getter_count=0,
                   proposed_public_achieved_pose_read_count=1,
                   all_actual_PhysX_steps_completed=True,
                   source_original_full_runner_worlds=10,
                   proposed_full_runner_worlds=11,
                   source_baseline_zero_success=truth<3,
                   source_baseline_privileged_getter_success=truth<3,
                   proposed_mode_refresh_success=truth<3,
                   privileged_getter_comparator_count=1))
        doc=dict(schema="native_mode_refresh_development_frozen_ppo_physical_v1",
                 task=task,no_PPO_training=True,cost_model_two_privileged_mode_writes_and_zero_hidden_state_writes=True,
                 actual_independent_reset_clusters=4,
                 actual_correlated_ACK_task_pairs=16,
                 actually_physical_native_controller_worlds=336,rows=rows)
        p=Path(root)/f"native_mode_refresh_{task}_original.json"
        p.write_text(json.dumps(doc))
        (Path(root)/f"native_mode_refresh_{task}_original.sha256").write_text(sha256(p.read_bytes()).hexdigest())

class NativeReanchorSourceAudit(unittest.TestCase):
    def test_constructed_source_not_physx(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d);a=audit(d)
            self.assertEqual(a["independent_reset_clusters"],8)
            self.assertEqual(a["ack_trials_repeated_correlated"],32)
            self.assertEqual(a["by_task"]["pull_cube"]["zero_success"],12)
            self.assertEqual(a["by_task"]["pull_cube"]["unique_mode_refresh_saves_over_zero"],0)
    def test_sha_tamper_fails(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            p=Path(d)/"native_mode_refresh_pull_cube_original.json"
            p.write_text(p.read_text()+" ")
            with self.assertRaises(ValueError):audit(d)
    def test_missing_ack_fails_even_after_correct_hash(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            p=Path(d)/"native_mode_refresh_pull_cube_original.json"
            z=json.loads(p.read_text());z["rows"].pop()
            p.write_text(json.dumps(z))
            (Path(d)/"native_mode_refresh_pull_cube_original.sha256").write_text(sha256(p.read_bytes()).hexdigest())
            with self.assertRaises(ValueError):audit(d)
    def test_missing_or_unpaid_privileged_setter_fails(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            p=Path(d)/"native_mode_refresh_pull_cube_original.json"
            z=json.loads(p.read_text())
            z["rows"][0]["privileged_runtime_mode_writes"]=0
            p.write_text(json.dumps(z))
            (Path(d)/"native_mode_refresh_pull_cube_original.sha256").write_text(sha256(p.read_bytes()).hexdigest())
            with self.assertRaises(ValueError):audit(d)

if __name__=="__main__":unittest.main()
