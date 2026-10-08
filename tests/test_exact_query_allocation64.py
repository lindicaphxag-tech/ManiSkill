"""Exact source-locked 17-query random schedule evidence and destructive controls."""
import copy
import hashlib
import shutil
import tempfile
import unittest
from math import comb
from pathlib import Path
from research.frozen_policy_transfer.review.exact_query_allocation64 import (
    EXPECTED_FILES, ensure_original_source,
    exact_uniform_fixed_query_distribution, original_allocation_audit
)

ARCHIVE=(Path(__file__).resolve().parents[1]/
    "research/frozen_policy_transfer/evidence/"
    "certify_query_periodic_placebo_new64_260001_270032")


class ExactFinitePopulationTest(unittest.TestCase):
    def test_three_term_enumeration_with_negative_consequences(self):
        self.assertEqual(
            exact_uniform_fixed_query_distribution([1,0,-1],1),
            {-1:1,0:1,1:1})
        self.assertEqual(
            exact_uniform_fixed_query_distribution([1,0,-1],2),
            {-1:1,0:1,1:1})
        self.assertEqual(exact_uniform_fixed_query_distribution([1,0,-1],0),{0:1})

    def test_invalid_query_budget_or_fake_gain_rejected(self):
        for budget in (-1,3):
            with self.assertRaises(ValueError):
                exact_uniform_fixed_query_distribution([1,0],budget)
        with self.assertRaises(ValueError):
            exact_uniform_fixed_query_distribution([1,2,-1],2)

    def test_original_official_physx_full64_future_fixed_queries(self):
        result=original_allocation_audit(ARCHIVE)
        self.assertEqual(len(result["original_eight_source_sha256"]),8)
        self.assertEqual(result["adaptive_actual_successes"],58)
        self.assertEqual(result["never_query_observed_successes"],41)
        self.assertEqual(result["mandatory_fixed_step3_query_observed_successes"],60)
        self.assertEqual(result["adaptive_actually_used_readbacks"],17)
        self.assertEqual(result["fixed_step3_readback_budget"],17)
        self.assertEqual(
            result["conditional_fixed_step3_query_gain_histogram"],
            {"-1":0,"0":45,"1":19})
        self.assertTrue(result["actually_executed_periodic_arm_matches_matched_step3_outcomes"])
        self.assertEqual(result["uniform_random_fixed_schedule_expected_successes"],46.046875)
        counts=result["uniform_random_fixed_schedule_success_distribution_exact_integer_counts"]
        self.assertEqual(sum(counts.values()),comb(64,17))
        self.assertEqual(min(map(int,counts)),41)
        self.assertEqual(max(map(int,counts)),58)
        self.assertEqual(result["uniform_random_success_at_least_adaptive"]["numerator"],"171")
        self.assertEqual(result["uniform_random_success_at_least_adaptive"]["denominator"],"1379370175283520")
        self.assertFalse(result["independent_external_reproduction"])
        # CRITICAL: the adaptive policy is not just a fixed YES/NO query switch;
        # it genuinely queries later and changes closed-loop action trajectories.
        exceptions=result["adaptive_outcome_not_recoverable_by_fixed_query_or_never_query"]
        self.assertEqual([(e["seed"],e["adaptive_query_step"]) for e in exceptions],
                         [(270005,6),(270030,5)])
        self.assertTrue(all(e["adaptive_succeeded"] and
                            not e["fixed_read_success"] and
                            not e["never_read_success"] for e in exceptions))

    def test_source_and_manifest_coordinated_tampering_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            shutil.copyfile(ARCHIVE/"SHA256SUMS",p/"SHA256SUMS")
            for f in EXPECTED_FILES:shutil.copyfile(ARCHIVE/f,p/f)
            file=p/EXPECTED_FILES[0]
            old=file.read_bytes()
            file.write_bytes(old+b"\n")
            manifest=p/"SHA256SUMS"
            original=manifest.read_text()
            forged=original.replace(
                hashlib.sha256(old).hexdigest(),
                hashlib.sha256(file.read_bytes()).hexdigest())
            self.assertNotEqual(original,forged)
            manifest.write_text(forged)
            with self.assertRaisesRegex(ValueError,"original published finite-population SHA manifest"):
                ensure_original_source(p)

    def test_missing_original_episode_shard_and_bad_digest_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            shutil.copyfile(ARCHIVE/"SHA256SUMS",p/"SHA256SUMS")
            for f in EXPECTED_FILES:shutil.copyfile(ARCHIVE/f,p/f)
            (p/EXPECTED_FILES[2]).unlink()
            with self.assertRaises(FileNotFoundError):
                ensure_original_source(p)


if __name__=="__main__":
    unittest.main()
