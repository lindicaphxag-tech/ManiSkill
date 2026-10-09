"""Standard-library-only archive corruption and paired-source checker tests."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from research.review_original_anchor128_source import FIRST,review

class FirstActualPhysXSourceReview(unittest.TestCase):
    def test_all_first_original_physical_worlds_and_hashed_log_sources(self):
        d=review(FIRST)
        self.assertEqual(d["checked_files"],19)
        self.assertEqual(d["original_physical_worlds"],128)
        self.assertEqual(d["independent_robot_reset_seeds"],16)
        self.assertEqual(d["matched_pair_prefixes"],64)
        self.assertEqual(d["rotation_probe_changed_recorded_target_so3_gt_0_001rad"],32)
        self.assertTrue(d["source_only_original_recorded_metrics_not_raw_quaternion_remeasurement"])
        for robot in ("panda","xarm6_robotiq"):
            values=d["by_robot_and_probe_repair"][robot]
            self.assertEqual(values["zero/no_probe_transition_ablation"]["recorded_fullSE3_target_restoration_passes"],16)
            self.assertEqual(values["zero/actual_transition_compensation"]["recorded_fullSE3_target_restoration_passes"],16)
            self.assertEqual(values["rotation_z/no_probe_transition_ablation"]["recorded_fullSE3_target_restoration_passes"],0)
            self.assertEqual(values["rotation_z/actual_transition_compensation"]["recorded_fullSE3_target_restoration_passes"],16)

    def test_one_byte_original_source_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"evidence"
            shutil.copytree(FIRST,target)
            raw=target/"anchor_repair_panda_chunk0.json"
            raw.write_bytes(raw.read_bytes()+b"\n")
            with self.assertRaisesRegex(ValueError,"checksum"):
                review(target)

    def test_missing_original_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"evidence"
            shutil.copytree(FIRST,target)
            (target/"anchor_repair_xarm6_robotiq_chunk1.json").unlink()
            with self.assertRaises(FileNotFoundError):
                review(target)


if __name__=="__main__":
    unittest.main()
