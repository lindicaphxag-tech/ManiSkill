"""Preregistration overlap witness: 160 experiment rows are only 128 reset identities."""
import copy
import unittest
from unittest.mock import patch
from research.audit_cross_study_reset_overlap import (
    analyze, checked_protocols, registered_pairs
)


class CrossCohortLeakageAccounting(unittest.TestCase):
    def test_exact_pinned_three_protocols_and_nonindependent_reset_states(self):
        d=analyze()
        self.assertEqual(d["registered_episode_rows_across_three_studies"],160)
        self.assertEqual(d["unique_task_reset_identifiers_across_three_studies"],128)
        self.assertEqual(d["mixed64_reused_from_previous_survivor32"],32)
        self.assertEqual(d["mixed64_wholly_new_task_reset_ids_relative_to_both_prior_studies"],32)
        self.assertEqual(d["reused_mixed_conditions_with_same_held_held_fault_truth"],16)
        self.assertEqual(d["reused_reset_ids_with_DIFFERENT_t2_applied_truth"],16)
        self.assertFalse(d["any_prior_task_success_or_baseline_selection_information_leakage_excluded"])

    def test_reject_missing_or_reordered_original_survivor_reset(self):
        docs=checked_protocols()
        forged=copy.deepcopy(docs)
        forged["survivor32"]["new_population"]["pull_cube_seeds"][0]=12345
        with self.assertRaisesRegex(ValueError,"Nonconsecutive"):
            registered_pairs(forged)

    def test_reject_posthoc_mutation_of_declared_mixed_population(self):
        docs=checked_protocols()
        forged=copy.deepcopy(docs)
        forged["mixed64"]["unseen_population"]["tasks"]["stack_cube"]["end"]+=1
        with patch("research.audit_cross_study_reset_overlap.checked_protocols",return_value=forged):
            with self.assertRaisesRegex(ValueError,"registered reset count"):
                analyze()

    def test_same_initial_state_does_not_imply_same_ack_truth(self):
        docs=checked_protocols()
        reg,truth=registered_pairs(docs)
        odd=("stack_cube",870001)
        even=("stack_cube",870002)
        self.assertIn(odd,reg["mixed64"] & reg["survivor32"])
        self.assertIn(even,reg["mixed64"] & reg["survivor32"])
        self.assertEqual(truth[("mixed64",*odd)],("held","held"))
        self.assertEqual(truth[("mixed64",*even)],("applied","held"))
        self.assertEqual(truth[("survivor32",*even)],("held","held"))


if __name__=="__main__":
    unittest.main()
