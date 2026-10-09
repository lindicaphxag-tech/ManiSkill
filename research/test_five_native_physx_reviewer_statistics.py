"""No green check by self-report: test original physical source assay, exact binomial
edge cases, matched-seed denominator and all five preserved negative outcomes.
"""
import unittest
from research.audit_five_native_physx_reviewer_statistics import (
    cp_interval,exact_two_sided_sign,original_file,extract,report)

class SourceReviewerStatistics(unittest.TestCase):
    def test_exact_binomial_tails(self):
        p=cp_interval(0,18)
        self.assertAlmostEqual(p["exact_two_sided_95pct_high"],1-(.025)**(1/18),places=10)
        self.assertEqual(p["exact_two_sided_95pct_low"],0)
        self.assertAlmostEqual(cp_interval(18,18)["exact_two_sided_95pct_low"],(.025)**(1/18),places=10)
        self.assertEqual(cp_interval(18,18)["exact_two_sided_95pct_high"],1)
        self.assertEqual(exact_two_sided_sign(0,0),1)
        self.assertAlmostEqual(exact_two_sided_sign(30,3),2*sum(
            __import__("math").comb(33,k) for k in range(4))/2**33)
    def test_source_has_320_distinct_actual_resets(self):
        rr=report()
        self.assertEqual(rr["independent_64_reset_populations"],5)
        self.assertEqual(rr["total_distinct_registered_reset_states"],320)
        self.assertTrue(rr["cohorts_NOT_pooled_due_different_physics_and_probe_cost"])
    def test_original_first_mixed_lookups_and_task_successes(self):
        a=report()["complete"]["first_mixed_t3_held"]["all64_paired_analysis"]
        self.assertEqual((a["controller_a_success"],a["controller_b_success"]),(58,58))
        self.assertEqual((a["controller_a_privileged_reads"],a["controller_b_privileged_reads"]),(31,58))
        self.assertEqual(a["paired_success"],{"both":57,"a_only":1,"b_only":1,"neither":5})
        self.assertEqual(a["controller_a_wrong_confident_histories"],0)
        self.assertEqual(a["controller_a_confident_histories"],33)
    def test_original_four_truth_confident_errors_must_remain(self):
        a=report()["complete"]["four_joint_t4"]["all64_paired_analysis"]
        self.assertEqual((a["controller_a_success"],a["controller_b_success"]),(58,57))
        self.assertEqual((a["controller_a_privileged_reads"],a["controller_b_privileged_reads"]),(46,62))
        self.assertEqual((a["controller_a_confident_histories"],a["controller_a_wrong_confident_histories"]),(18,2))
        # 2/18 incorrect confident selections is scientifically nonzero.
        self.assertGreater(a["controller_a_wrong_among_accepted_exact_CP_95pct_DESCRIPTIVE"]["exact_two_sided_95pct_low"],0)
    def test_negative_new_cohorts_not_hidden(self):
        x=report()["complete"]
        dual=x["one_v_two_t4_t5"]["all64_paired_analysis"]
        self.assertEqual((dual["controller_a_success"],dual["controller_b_success"]),(48,48))
        self.assertEqual((dual["controller_a_privileged_reads"],dual["controller_b_privileged_reads"]),(43,41))
        self.assertEqual(dual["paired_success"],{"both":48,"a_only":0,"b_only":0,"neither":16})
        calibration=x["old_v_prior_score_radius"]["all64_paired_analysis"]
        self.assertEqual((calibration["controller_a_success"],calibration["controller_b_success"]),(58,58))
        self.assertEqual((calibration["controller_a_privileged_reads"],calibration["controller_b_privileged_reads"]),(53,51))
        shift=x["actual_joint_PD_shift_t1_anchor"]["all64_paired_analysis"]
        self.assertEqual((shift["controller_a_success"],shift["controller_b_success"]),(56,56))
        self.assertEqual((shift["controller_a_privileged_reads"],shift["controller_b_privileged_reads"]),(62,56))
        self.assertEqual(shift["controller_a_confident_histories"],2)
        self.assertEqual(shift["controller_b_confident_histories"],8)
        self.assertEqual(shift["paired_success"],{"both":56,"a_only":0,"b_only":0,"neither":8})
    def test_separate_task_strata_and_no_independent_external_claim(self):
        r=report()
        self.assertTrue(r["no_statistical_noninferiority_claims"])
        self.assertTrue(r["stats_are_descriptive_and_exploratory_within_only_two_frozen_PPO_tasks"])
        for c in r["complete"].values():
            self.assertEqual(c["disaggregated"]["pull_cube"]["genuinely_original_matched_reset_states"],32)
            self.assertEqual(c["disaggregated"]["stack_cube"]["genuinely_original_matched_reset_states"],32)
    def test_all_files_sha_pinned_and_not_mutated(self):
        for name in ("first_mixed_t3_held","four_joint_t4","one_v_two_t4_t5","old_v_prior_score_radius","actual_joint_PD_shift_t1_anchor"):
            data,sha=original_file(name)
            self.assertEqual(len(sha),64)
            self.assertEqual(len(extract(name,data)),64)

if __name__=="__main__":unittest.main()
