"""Adversarial reproducibility tests: no test fixtures may masquerade as PhysX."""
import copy
import unittest
from research.reviewer_budget_frontier_2x2 import compute, mcnemar_exact, wilson

TASKS=("pull_cube","stack_cube")
TRUTHS=("held/held","applied/held","held/applied","applied/applied")


def fixture():
    rows=[]
    for task in TASKS:
        for i,truth in enumerate(TRUTHS):
            rows.append(dict(task=task,truth=truth,
                seed=2000000+len(rows),public_both_faults_exposed=True,
                public_sample_events=2,public_authorized=bool(i%2),
                wrong_confident=False,new_success=True,strong_success=True,
                fixed_success=True,held_success=i<3,
                new_reads=int(not i%2),strong_reads=1,fixed_reads=1))
    totals={
        "public":{"task_success":8,"private_reads":4},
        "strong_task":{"task_success":8,"private_reads":8},
        "fixed_t5":{"task_success":8,"private_reads":8},
        "always_held":{"task_success":6,"private_reads":0},
    }
    return dict(schema="both_true_unknown_ACKs_full_64_original_native_PhysX_audit_v1",
        all_episodes=rows, outcomes=totals,
        paired_new_vs_task_aware_strong=dict(both=8,neither=0,new_only=0,strong_only=0),
        public_confident_history_admissions=4,
        observed_confident_wrong_history=0)


class Reviewer2x2AuditTests(unittest.TestCase):
    def test_synthetic_shape_only_not_physx(self):
        d=compute(fixture(), expected_n=8, expected_per_stratum=1)
        self.assertEqual(d["totals"]["public_reads"],4)
        self.assertEqual(d["privileged_reads_saved_vs_task_aware"],4)
        self.assertEqual(d["marginal_public_XYZ_samples_vs_task_aware"],16)
        self.assertEqual(d["private_read_equivalent_break_even_per_XYZ_sample"],.25)
        self.assertTrue(d["not_new_simulation"])
        self.assertTrue(d["not_external_replication"])
    def test_reject_duplicate_reset(self):
        x=fixture()
        x["all_episodes"][1]["seed"]=x["all_episodes"][0]["seed"]
        with self.assertRaisesRegex(ValueError,"Duplicate"):compute(x, expected_n=8, expected_per_stratum=1)
    def test_reject_one_missing_fault(self):
        x=fixture()
        x["all_episodes"][0]["public_both_faults_exposed"]=False
        with self.assertRaisesRegex(ValueError,"missing"):compute(x, expected_n=8, expected_per_stratum=1)
    def test_reject_unreported_public_cost(self):
        x=fixture()
        x["all_episodes"][0]["public_sample_events"]=0
        with self.assertRaisesRegex(ValueError,"observations"):compute(x, expected_n=8, expected_per_stratum=1)
    def test_reject_private_read_leak(self):
        x=fixture()
        x["all_episodes"][1]["new_reads"]=1
        with self.assertRaisesRegex(ValueError,"fallback"):compute(x, expected_n=8, expected_per_stratum=1)
    def test_reject_false_aggregate(self):
        x=fixture()
        x["outcomes"]["public"]["task_success"]=7
        with self.assertRaisesRegex(ValueError,"aggregate"):compute(x, expected_n=8, expected_per_stratum=1)
    def test_reject_false_pairing(self):
        x=fixture()
        x["paired_new_vs_task_aware_strong"]["new_only"]=1
        with self.assertRaisesRegex(ValueError,"paired"):compute(x, expected_n=8, expected_per_stratum=1)
    def test_reject_selective_truth_exclusion(self):
        x=fixture()
        x["all_episodes"][0]["truth"]="held/applied"
        with self.assertRaisesRegex(ValueError,"Unbalanced"):compute(x, expected_n=8, expected_per_stratum=1)
    def test_exact_pair_test_and_zero_errors_not_guarantee(self):
        self.assertEqual(mcnemar_exact(1,2),1.0)
        self.assertEqual(mcnemar_exact(0,0),1.0)
        lo,hi=wilson(0,14)
        self.assertEqual(lo,0.)
        self.assertGreater(hi,.15)
    def test_success_is_strict_boolean(self):
        x=fixture()
        x["all_episodes"][3]["new_success"]=1
        with self.assertRaisesRegex(ValueError,"boolean"):compute(x, expected_n=8, expected_per_stratum=1)


if __name__=="__main__":
    unittest.main()
