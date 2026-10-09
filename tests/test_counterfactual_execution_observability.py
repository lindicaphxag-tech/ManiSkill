"""Adversarial tests for non-identifiability source claims; no SciPy/PyTorch/robot."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from research.audit_counterfactual_execution_observability import (
    DEFAULT_SOURCE, PUBLIC, audit, checked_sources, measurement
)

class SourceIdentifiabilityAudit(unittest.TestCase):
    def test_entire_128_truth_cell_archive_not_just_chosen_positives(self):
        o=audit()
        self.assertEqual(o["source_original_manifest_SHA256_verified_file_count"],34)
        self.assertEqual(o["source_32_reset_clusters"],32)
        self.assertEqual(o["registered_real_ACK_truth_cells"],128)
        self.assertEqual(o["observation_pairs_actually_available"],187)
        self.assertEqual(o["exact_six_value_public_XYZ_collisions_with_distinct_hidden_full_pose"],3)
        self.assertEqual({r["reset_seed"] for r in o["source_frozen_conflict_witnesses"]},
                         {2110003,2110004,2110012})
        self.assertTrue(o["not_an_unconditional_robot_safety_theorem"])

    def test_witness_has_distinct_real_hidden_full_poses_and_exact_same_public_data(self):
        o=audit()
        for w in o["source_frozen_conflict_witnesses"]:
            self.assertEqual(tuple(w["truth_conditions"]),(1,3))
            self.assertEqual(tuple(w["physical_truth_A"]),("applied","held"))
            self.assertEqual(tuple(w["physical_truth_B"]),("applied","applied"))
            self.assertTrue(w["six_public_XYZ_numbers_bitwise_equal_after_JSON_load"])
            self.assertGreater(w["commanded_target_position_separation_m_min_two_audits"],.039)
            self.assertGreater(w["commanded_target_orientation_separation_rad_min_two_audits"],.04)
            self.assertTrue(w["actual_delivered_neutral_t4_probe_both_worlds"])
            self.assertNotEqual(w["actual_hidden_target_index_A"],w["actual_hidden_target_index_B"])

    def test_manifest_tampering_fails_before_any_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)
            for p in DEFAULT_SOURCE.iterdir():
                if p.is_file():shutil.copyfile(p,dest/p.name)
            target=dest/"factorial_pull_cube_chunk0_truth3_original8.json"
            target.write_bytes(target.read_bytes()+b"\n")
            with self.assertRaisesRegex(ValueError,"IMMUTABLE_FIRST_PHYSX_SOURCE_CHANGED"):
                checked_sources(dest)

    def test_probe_that_did_not_physically_execute_is_not_observable(self):
        states,_=checked_sources(DEFAULT_SOURCE)
        r=json.loads(json.dumps(states[("pull_cube",2110003)][3]))
        r["shared_neutral_probe_step4"][PUBLIC]["physically_dispatched"]=False
        self.assertIsNone(measurement(r))
        r=states[("pull_cube",2110003)][3]
        self.assertIsNotNone(measurement(r))

    def test_target_ground_truth_label_not_in_runtime_features(self):
        states,_=checked_sources(DEFAULT_SOURCE)
        a=states[("pull_cube",2110004)][1]
        b=states[("pull_cube",2110004)][3]
        self.assertEqual(measurement(a),measurement(b))
        self.assertNotEqual(a["public_t3_evidence"]["audit_only_true_candidate_indices"],
                            b["public_t3_evidence"]["audit_only_true_candidate_indices"])
        self.assertEqual(a["initial_source_physical_obs_sha256"],
                         b["initial_source_physical_obs_sha256"])

if __name__=="__main__":
    unittest.main()
