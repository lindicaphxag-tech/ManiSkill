"""Adversarial group-correct facts for prospective B=0.60 original PhysX source."""
import unittest
from research.review_strong060_cluster_risk import (
    analyze_clustering, exact_one_sided_upper, _stats, A, B, C
)

class ProspectivelyFrozenPhysicalClusterAudit(unittest.TestCase):
    def test_original_32_clusters_and_both_actual_comparators(self):
        d=analyze_clustering()
        self.assertEqual(d["original_run_id"],37961696443)
        self.assertEqual(d["real_task_reset_independent_sample_units"],32)
        self.assertEqual(d["correlated_physical_ACK_truth_cells"],128)
        self.assertEqual(d["actual_native_PhysX_controller_worlds"],1280)
        a,b,c=(d["pooled"]["strategy"][x] for x in (A,B,C))
        self.assertEqual([r["official_successes"] for r in (a,b,c)],[109,109,110])
        self.assertEqual([r["true_target_reads"] for r in (a,b,c)],[94,98,128])
        self.assertEqual([r["accepted_events"] for r in (a,b,c)],[34,30,0])
        self.assertEqual([a["accepted_clusters"],b["accepted_clusters"]],[22,21])
        self.assertEqual([a["wrong_clusters"],b["wrong_clusters"]],[0,0])
        self.assertAlmostEqual(
            a["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],
            1-.05**(1/22), places=12
        )
        self.assertGreater(
            a["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],.12
        )
        self.assertEqual(d["paired_A_vs_B_060_authority_cells"],
                         {"neither":92,"both_authorize":28,"A_only":6,"B_only":2})
        self.assertEqual(d["whole_reset_A_vs_B_private_getter_savings"],4)
        self.assertAlmostEqual(d["whole_reset_read_delta_exact_signflip_p_EXPLORATORY"],
                               .2890625,places=12)
        self.assertEqual(
            d["native_task_paired_differences_A_vs_C"]["fixed_only"],1
        )
        self.assertEqual(
            d["task_stratified_32cluster_bootstrap_getter_savings_EXPLORATORY"]
              ["A_vs_B"]["observed_total_original_private_getters_saved"],4
        )

    def test_any_wrong_is_whole_reset_not_four_iid_trials(self):
        vals=[{"success":{A:True,B:True,C:True},
               "reads":{A:0,B:0,C:1},
               "public_xyz":{A:2,B:2,C:0},
               "confidence":{A:i in (0,1),B:False},
               "wrong":{A:i==1,B:False}} for i in range(4)]
        result=_stats([vals])["strategy"][A]
        self.assertEqual(result["accepted_events"],2)
        self.assertEqual(result["accepted_clusters"],1)
        self.assertEqual(result["wrong_events"],1)
        self.assertEqual(result["wrong_clusters"],1)

    def test_always_abstain_cannot_receive_perfect_zero_error_certificate(self):
        rr=[{"success":{A:True,B:True,C:True},
             "reads":{A:1,B:1,C:1},
             "public_xyz":{A:2,B:2,C:0},
             "confidence":{A:False,B:False},
             "wrong":{A:False,B:False}} for _ in range(4)]
        v=_stats([rr])["strategy"][A]
        self.assertEqual(v["accepted_clusters"],0)
        self.assertEqual(v["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],1.)

    def test_bad_wrong_label_without_authorization_is_rejected(self):
        rr=[{"success":{A:True,B:True,C:True},
             "reads":{A:0,B:0,C:1},
             "public_xyz":{A:2,B:2,C:0},
             "confidence":{A:False,B:False},
             "wrong":{A:True,B:False}} for _ in range(4)]
        with self.assertRaisesRegex(ValueError,"Source wrong without"):
            _stats([rr])

    def test_exact_bounds_are_conditional_and_not_128_independent(self):
        self.assertAlmostEqual(exact_one_sided_upper(0,22),1-.05**(1/22),places=12)
        self.assertAlmostEqual(exact_one_sided_upper(0,21),1-.05**(1/21),places=12)
        self.assertGreater(exact_one_sided_upper(0,22),exact_one_sided_upper(0,34))
        self.assertEqual(exact_one_sided_upper(0,0),1.)
        with self.assertRaises(ValueError):exact_one_sided_upper(2,1)

if __name__ == "__main__":
    unittest.main()
