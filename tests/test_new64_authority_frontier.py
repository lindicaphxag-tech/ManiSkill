"""Independent stdlib regressions for real-data 64-state exact authority audit."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from research.frozen_policy_transfer.review.authority_frontier_64 import (
    ADAPTIVE, MANDATORY, NO_QUERY, EXPECTED_FILES,
    audit_authority_frontier, compute_frontier, exact_matched_success,
    verify_original_sha256, wilson_interval
)

ROOT = (Path(__file__).resolve().parents[1] /
    "research/frozen_policy_transfer/evidence/robust_query_new64_142001_152032")


class ExactPairTest(unittest.TestCase):
    def test_known_five_to_two_discordances_not_significant(self):
        # 5 selective-only wins, 2 mandatory-only wins, 10 both succeed.
        a = [True]*5 + [False]*2 + [True]*10
        b = [False]*5 + [True]*2 + [True]*10
        result = exact_matched_success(a,b)
        self.assertEqual((result["adaptive_only"],result["comparison_only"]), (5,2))
        self.assertEqual(result["two_sided_exploratory_exact_p"], .453125)
        self.assertEqual(result["delta_success_count"], 3)

    def test_exact_zero_discordances_and_binary_dtype_failclosed(self):
        self.assertEqual(exact_matched_success([True,False],[True,False])["two_sided_exploratory_exact_p"],1.0)
        with self.assertRaises(ValueError):
            exact_matched_success([1,False],[True,False])
        with self.assertRaises(ValueError):
            exact_matched_success([True],[False,True])

    def test_uncertainty_bounds_are_not_certificates(self):
        a,b = wilson_interval(15,64)
        self.assertLess(a,15/64)
        self.assertGreater(b,15/64)
        with self.assertRaises(ValueError):
            wilson_interval(-1,64)


class FullPhysXOriginalArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answer = audit_authority_frontier(ROOT)

    def test_all_original_source_hashes_and_paired_frozen_evidence(self):
        q = self.answer
        self.assertEqual(len(q["source_original_8_files_sha256"]),8)
        self.assertEqual(q["pooled_64_state_descriptive"]["original_state_count"],64)
        z = q["pooled_64_state_descriptive"]
        self.assertEqual(z["arm_success_counts"][ADAPTIVE],60)
        self.assertEqual(z["arm_success_counts"][MANDATORY],57)
        self.assertEqual(z["arm_success_counts"][NO_QUERY],47)
        self.assertEqual(z["privileged_decision_readbacks"][ADAPTIVE],15)
        self.assertEqual(z["privileged_decision_readbacks"][MANDATORY],64)
        self.assertEqual(z["relative_target_query_reduction_vs_mandatory"],49/64)
        self.assertEqual(
            (z["exact_paired_outcomes"][MANDATORY]["adaptive_only"],
             z["exact_paired_outcomes"][MANDATORY]["comparison_only"]), (5,2))
        self.assertEqual(z["exact_paired_outcomes"][MANDATORY]["two_sided_exploratory_exact_p"], .453125)
        self.assertFalse(z["noninferiority_statistically_established"])
        self.assertFalse(q["external_investigator_has_reproduced_physics"])

    def test_two_task_frozen_policy_not_64_independent_models(self):
        q=self.answer
        self.assertEqual(q["two_actual_frozen_ppo_task_families"],["pull_cube","stack_cube"])
        p=q["per_frozen_policy_task_stratum"]["pull_cube"]
        s=q["per_frozen_policy_task_stratum"]["stack_cube"]
        self.assertEqual((p["original_state_count"],s["original_state_count"]),(32,32))
        self.assertEqual((p["arm_success_counts"][ADAPTIVE],s["arm_success_counts"][ADAPTIVE]),(32,28))
        self.assertEqual((p["privileged_decision_readbacks"][ADAPTIVE],s["privileged_decision_readbacks"][ADAPTIVE]),(2,13))
        self.assertEqual(
            self.answer["pooled_64_state_descriptive"]["observed_success_vs_privileged_read_cost_crossings"][NO_QUERY]["equal_empirical_aggregate_utility_lambda"],
            13/15)

    def test_changed_original_sha256_is_rejected_without_simulator(self):
        with tempfile.TemporaryDirectory() as t:
            local=Path(t)
            shutil.copyfile(ROOT/"SHA256SUMS",local/"SHA256SUMS")
            for name in EXPECTED_FILES:
                shutil.copyfile(ROOT/name,local/name)
            first=local/EXPECTED_FILES[0]
            first.write_bytes(first.read_bytes()+b"\n")
            with self.assertRaisesRegex(ValueError,"hash mismatch"):
                verify_original_sha256(local)

    def test_shard_omission_and_rogue_hash_file_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            local=Path(t)
            shutil.copyfile(ROOT/"SHA256SUMS",local/"SHA256SUMS")
            for name in EXPECTED_FILES:
                shutil.copyfile(ROOT/name,local/name)
            (local/EXPECTED_FILES[4]).unlink()
            with self.assertRaises(FileNotFoundError):
                verify_original_sha256(local)
            expected=(local/"SHA256SUMS").read_text()
            (local/"SHA256SUMS").write_text(expected+"f"*64+"  imaginary_new_patient.json\n")
            with self.assertRaisesRegex(ValueError,"Pinned original experiment SHA256SUMS"):
                verify_original_sha256(local)

    def test_corrupted_source_and_coordinated_manifest_rewrite_cannot_pass(self):
        # An unanchored checksum file proves only that the current two files
        # agree, not that they match what was originally publicly archived.
        # Deliberately alter BOTH sources and the corresponding digest.
        with tempfile.TemporaryDirectory() as t:
            local=Path(t)
            shutil.copyfile(ROOT/"SHA256SUMS",local/"SHA256SUMS")
            for name in EXPECTED_FILES:
                shutil.copyfile(ROOT/name,local/name)
            first=local/EXPECTED_FILES[0]
            original=first.read_bytes()
            original_sha=hashlib.sha256(original).hexdigest()
            first.write_bytes(original+b"\\n")
            new_sha=hashlib.sha256(first.read_bytes()).hexdigest()
            manifest=local/"SHA256SUMS"
            assert original_sha in manifest.read_text()
            manifest.write_text(manifest.read_text().replace(original_sha,new_sha))
            # A mutable SHA manifest would now accept the forged JSON.
            # The earlier publicly committed Git blob identity MUST reject.
            with self.assertRaisesRegex(ValueError,"Pinned original experiment SHA256SUMS"):
                verify_original_sha256(local)

    def test_forged_info_cost_and_fake_arm_success_refused(self):
        row={
            "task":"pull_cube","seed":142001,
            "success":{ADAPTIVE:True, MANDATORY:True, NO_QUERY:False,
                       "fault_optimistic_unverified_ack":False},
            "selective_readback":0,
        }
        assert compute_frontier([row])["privileged_decision_readbacks"][ADAPTIVE]==0
        bad=copy.deepcopy(row)
        bad["selective_readback"]=-1
        with self.assertRaisesRegex(ValueError,"Invalid selective"):
            compute_frontier([bad])
        bad=copy.deepcopy(row)
        bad["success"][MANDATORY]=3
        with self.assertRaisesRegex(ValueError,"Method outcome"):
            compute_frontier([bad])
        with self.assertRaisesRegex(ValueError,"duplicated"):
            compute_frontier([row,row])


if __name__ == "__main__":
    unittest.main()
