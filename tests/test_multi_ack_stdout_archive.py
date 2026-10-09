"""No simulator required: independently verify source-logged double-ACK real PhysX results."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from research.frozen_policy_transfer.audit_original_multi_ack_16_stdout import (
    SOURCE, HERE, PREFIX, ARMS, SELECTIVE, MANDATORY, NO_QUERY,
    audit, exact_git_blob,
)


class OriginalTwoFaultResearchAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=audit()

    def test_frozen_original_16_full_denominator_and_both_policy_sha(self):
        self.assertEqual(self.data["original_16_physical_states"],16)
        self.assertEqual(set(self.data["task_reports"]),{"pull_cube","stack_cube"})
        self.assertEqual(self.data["all_original_method_success_counts"][SELECTIVE],15)
        self.assertEqual(self.data["all_original_method_success_counts"][MANDATORY],15)
        self.assertEqual(self.data["all_original_method_success_counts"][NO_QUERY],7)
        self.assertEqual(self.data["source_target_decision_readbacks"][SELECTIVE],9)
        self.assertEqual(self.data["source_target_decision_readbacks"][MANDATORY],32)
        self.assertAlmostEqual(self.data["reduced_private_reads_vs_two_mandatory"],23/32)
        self.assertEqual(len(self.data["all_source_episode_cases"]),16)
        self.assertFalse(self.data["independent_external_replication"])

    def test_physically_executed_four_history_commands_separate_from_fault_suppression(self):
        self.assertEqual(self.data["authentic_K4_history_decisions_selective"],99)
        self.assertEqual(self.data["authentic_K4_commanded_setpoints_physically_dispatched_and_audited"],92)
        self.assertTrue(all(e["two_physx_faults_selective_reached"]
            for e in self.data["all_source_episode_cases"]))
        # One robot, two separately pinned public policies, not 99 independent experiments.
        self.assertEqual(self.data["task_reports"]["pull_cube"]["new_independent_reset_states"],8)
        self.assertEqual(self.data["task_reports"]["stack_cube"]["new_independent_reset_states"],8)

    def test_belief_history_count_with_all_real_negative_trials(self):
        cases=self.data["all_source_episode_cases"]
        failures=[r for r in cases if not r["success_selective"]]
        self.assertEqual([(f["task"],f["seed"]) for f in failures],[("stack_cube",240007)])
        k0=[r for r in cases if r["K4_history_decisions"]==0]
        self.assertEqual([(f["task"],f["seed"]) for f in k0],[("pull_cube",230007)])
        double_reads=[r for r in cases if r["queries_selective"]==2]
        self.assertEqual([(r["task"],r["seed"]) for r in double_reads],[("pull_cube",230007)])
        self.assertEqual(sum(r["K4_real_dispatched_certificates"] for r in cases),92)

    def test_immutability_reference_is_source_captured_github_blob(self):
        for task, (_, _, _, blob, _) in SOURCE.items():
            p=HERE/PREFIX/f"{task}_eight_true_physx_stdout_episodes.json"
            self.assertEqual(exact_git_blob(p.read_bytes()),blob)
            x=json.loads(p.read_text())
            self.assertIn("NOT byte-identical original artifact",x["provenance"])
            self.assertEqual(len(x["episodes"]),8)

    def test_corrupt_archive_both_success_and_checksum_fails(self):
        # Simulate changing true source payload: SHA of the pinned Git blob
        # no longer matches. The source auditor is based on that fixed blob.
        for task,(_,_,_,blob,_) in SOURCE.items():
            p=HERE/PREFIX/f"{task}_eight_true_physx_stdout_episodes.json"
            changed=json.loads(p.read_text())
            changed["episodes"][0]["success_once"][SELECTIVE]=False
            forged=(json.dumps(changed,sort_keys=True)+"\n").encode()
            self.assertNotEqual(exact_git_blob(forged),blob)


if __name__=="__main__":
    unittest.main()
