"""Pure-stdlib adversarial tests for reviewer-side ORIGINAL physical data audit."""
from __future__ import annotations
import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from research.frozen_policy_transfer.review.query_timing_frontier import (
    EVIDENCE, ADAPTIVE, paired, sign_test, source_hashes, study,
)


class QueryTimingOriginalEvidenceTests(unittest.TestCase):
    def test_exact_two_sided_pair(self):
        self.assertEqual(sign_test(0, 0), 1)
        self.assertEqual(sign_test(0, 1), 1)
        self.assertEqual(sign_test(0, 5), 0.0625)
        self.assertEqual(sign_test(3, 9), 598 / 4096)
        self.assertEqual(sign_test(1, 1), 1)
        for a, b in ((-1, 2), (2, -1), (1.0, 1)):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                sign_test(a, b)

    def test_paired_count_keeps_original_failure(self):
        first, second = ADAPTIVE, "fault_fixed_query_t5"
        rows = [
            {"seed": 1, "success_once": {first: True, second: True}},
            {"seed": 2, "success_once": {first: False, second: True}},
            {"seed": 3, "success_once": {first: False, second: False}},
            {"seed": 4, "success_once": {first: True, second: False}},
        ]
        c = paired(rows, first, second)
        self.assertEqual(c["first_only_seeds"], [4])
        self.assertEqual(c["second_only_seeds"], [2])
        self.assertEqual(c["both_succeed"], 1)
        self.assertEqual(c["both_fail"], 1)

    def test_source_manifests_are_present_and_immutable(self):
        hashes = source_hashes(EVIDENCE)
        self.assertEqual(len(hashes), 9)
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "copy"
            shutil.copytree(EVIDENCE, dest)
            first = sorted(dest.glob("query_time_*_original4.json"))[0]
            first.write_bytes(first.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                source_hashes(dest)

    def test_missing_or_added_original_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "copy"
            shutil.copytree(EVIDENCE, dest)
            source_file = sorted(dest.glob("query_time_*_original4.json"))[0]
            source_file.unlink()
            with self.assertRaises(ValueError):
                source_hashes(dest)
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "copy"
            shutil.copytree(EVIDENCE, dest)
            (dest / "unregistered.json").write_text("{}")
            with self.assertRaises(ValueError):
                source_hashes(dest)

    def test_full_prospective_sources_do_not_hide_counterexample(self):
        report = study(EVIDENCE)
        self.assertEqual(report["study_n_original_registered_reset_states"], 32)
        t = report["pooled_exact_task_success_and_query_read_counts"]
        self.assertEqual(t["fault_robust_then_single_privileged_query"]["task_success"], 31)
        self.assertEqual(t["fault_robust_then_single_privileged_query"]["actual_target_decision_reads"], 7)
        self.assertEqual(t["fault_fixed_query_t5"]["task_success"], 32)
        self.assertEqual(t["fault_fixed_query_t5"]["actual_target_decision_reads"], 32)
        self.assertEqual(report["t5_additional_success_seed"], 290012)
        p = report["paired_adaptive_vs_all_comparators"]["fault_fixed_query_t5"]
        self.assertEqual(p["first_only_seeds"], [])
        self.assertEqual(p["second_only_seeds"], [290012])
        self.assertEqual(report["fixed_t5_minus_adaptive_extra_privileged_reads"], 25)
        self.assertAlmostEqual(report["descriptive_break_even_cost_per_target_read_success_equivalents"], .04)


if __name__ == "__main__":
    unittest.main()
