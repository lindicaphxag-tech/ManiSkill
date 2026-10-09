"""Adversarial tests of the complete original task-level paired source accounting."""
from pathlib import Path
import shutil
import tempfile
import unittest

from research.frozen_policy_transfer.review.verify_two_prospective_history_cohorts import (
    EVIDENCE, STUDIES, analyze, exact_one_sided_zero_upper, sha_manifest
)

class TwoCohortsReviewerTests(unittest.TestCase):
    def test_original_complete_recomputation_from_96_real_task_states(self):
        z=analyze()
        p=z["studies"]["primary64"]["descriptive_paired_full_source"]
        q=z["studies"]["replication32"]["descriptive_paired_full_source"]
        self.assertEqual((p["n"],p["physical_worlds"],p["new_success"],p["gated_success"]), (64,512,58,58))
        self.assertEqual((p["new_reads"],p["gated_reads"],p["public_unique"],p["wrong_confident"]), (39,57,25,0))
        self.assertEqual((q["n"],q["physical_worlds"],q["new_success"],q["gated_success"]), (32,256,28,28))
        self.assertEqual((q["new_reads"],q["gated_reads"],q["public_unique"],q["wrong_confident"]), (22,27,10,0))
        self.assertEqual(z["studies"]["replication32"]["by_task"]["pull_cube"]["new_reads"], 13)
        self.assertEqual(z["studies"]["replication32"]["by_task"]["pull_cube"]["gated_reads"], 11)
        total=z["descriptive_sum_of_TWO_SEPARATELY_PREREGISTERED_protocols_NOT_one_joint_trial"]
        self.assertEqual((total["n"],total["physical_worlds"],total["new_success"],total["new_reads"],
                          total["gated_reads"],total["public_unique"]), (96,768,86,61,84,35))
        self.assertAlmostEqual(total["read_reduction_fraction_descriptive"], 23/84)

    def test_exact_zero_event_bounds_are_not_zero(self):
        for n in (10,25,32,64):
            upper=exact_one_sided_zero_upper(n)
            self.assertGreater(upper,0)
            self.assertLess(upper,1)
        self.assertAlmostEqual(exact_one_sided_zero_upper(25),1-.05**(1/25))
        self.assertAlmostEqual(exact_one_sided_zero_upper(64),1-.05**(1/64))
        for invalid in (0,-2,True,1.0):
            with self.subTest(value=invalid),self.assertRaises(ValueError):
                exact_one_sided_zero_upper(invalid)

    def test_reject_mutated_raw_physics_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/"evidence"
            shutil.copytree(EVIDENCE, dst)
            folder=dst/STUDIES["primary64"]["folder"]
            victim=next(folder.glob("*_original8.json"))
            victim.write_bytes(victim.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"changed"):
                analyze(dst)

    def test_reject_deleted_trial_and_unlisted_source(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/"evidence"
            shutil.copytree(EVIDENCE, dst)
            folder=dst/STUDIES["replication32"]["folder"]
            next(folder.glob("*_original4.json")).unlink()
            with self.assertRaises(ValueError):
                analyze(dst)
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/"evidence"
            shutil.copytree(EVIDENCE, dst)
            folder=dst/STUDIES["primary64"]["folder"]
            (folder/"forged_extra.json").write_text("{}")
            with self.assertRaises(ValueError):
                sha_manifest(folder,STUDIES["primary64"])

if __name__=="__main__":
    unittest.main()
