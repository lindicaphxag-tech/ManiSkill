"""Reproducibility and adversarial tests for original PhysX 64 failure analysis."""
from pathlib import Path
import shutil
import tempfile
import unittest
from research.frozen_policy_transfer.review.compound_ack_failure_witness_64 import (
    ARCHIVE, ADAPTIVE, FIXED, analyze, exact_two_sided_discordant_p,
)

class OriginalCompoundAckFailureWitnessTests(unittest.TestCase):
    def test_original_all64_and_important_13_falsifiers(self):
        o=analyze()
        self.assertEqual(o["full_denominator"],64)
        self.assertEqual(o["all_states"]["official_task_successes"],{
            "selective":45,"fixed":55})
        self.assertEqual(o["all_states"]["actual_private_reads"],{
            "selective":44,"fixed":64})
        self.assertEqual(len(o["task_groups"]["stack_cube"]["fixed_only_breakdown"][
            "no_private_target_read"]),8)
        self.assertEqual(len(o["task_groups"]["stack_cube"]["fixed_only_breakdown"][
            "one_private_target_read_but_failed"]),5)
        self.assertEqual(o["task_groups"]["pull_cube"]["official_task_successes"],{
            "selective":32,"fixed":32})
        self.assertEqual(o["task_groups"]["stack_cube"]["official_task_successes"],{
            "selective":13,"fixed":23})
        self.assertTrue(o["task_groups"]["stack_cube"]["fixed_only_breakdown"][
            "all_failed_selective_horizon_50"])
        self.assertEqual(len(o["strict_original_source_hashes"]),8)

    def test_source_manifest_fails_closed_under_raw_byte_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/"tampered"
            shutil.copytree(ARCHIVE,archive)
            raw=next(archive.glob("multiack-prospective-*/*_original8.json"))
            raw.write_bytes(raw.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"Altered or missing original"):
                analyze(archive)

    def test_original_missing_seed_refuses_instead_of_cherry_pick(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/"tampered"
            shutil.copytree(ARCHIVE,archive)
            shard=next(archive.glob("multiack-prospective-stack_cube-chunk0-*"))
            raw=shard/"compound_new64_stack_cube_chunk0_original8.json"
            raw.unlink()
            with self.assertRaises(ValueError):
                analyze(archive)

    def test_exact_paired_sign_test_not_fake_significance(self):
        self.assertAlmostEqual(
            exact_two_sided_discordant_p(3,13),.021270751953125)
        self.assertEqual(exact_two_sided_discordant_p(0,0),1.)
        self.assertEqual(exact_two_sided_discordant_p(0,1),1.)
        self.assertEqual(exact_two_sided_discordant_p(8,8),1.)


if __name__=="__main__":
    unittest.main()
