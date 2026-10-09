"""Original 128 causal truth cells never become 128 IID statistical samples."""
import unittest
from research.review_original_factorial128_cluster_risk import (
    analyze_clustering,exact_one_sided_upper,_stats,A,B,C
)

class FirstOriginalPairedPhysicalCausalClusterRisk(unittest.TestCase):
    def test_original_first_run_1280_physical_worlds_32_independent_clusters(self):
        d=analyze_clustering()
        self.assertEqual(d["real_task_reset_independent_sample_units"],32)
        self.assertEqual(d["correlated_physical_ACK_truth_cells"],128)
        self.assertEqual(d["actual_native_PhysX_controller_worlds"],1280)
        a,b,c=(d["pooled"]["strategy"][x] for x in (A,B,C))
        self.assertEqual([x["official_successes"] for x in (a,b,c)],[104]*3)
        self.assertEqual([x["true_target_reads"] for x in (a,b,c)],[102,122,127])
        self.assertEqual([x["accepted_events"] for x in (a,b,c)],[26,6,0])
        self.assertEqual(a["accepted_clusters"],20)
        self.assertEqual(a["wrong_events"],0)
        self.assertEqual(a["wrong_clusters"],0)
        self.assertAlmostEqual(a["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],
                               1-.05**(1/20),places=12)
        self.assertGreater(a["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],.13)
        self.assertLess(a["naive_per_decision_iid_95pct_upper_NOT_JUSTIFIED"],
                        a["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"])
        for task in ("pull_cube","stack_cube"):
            x=d["per_task"][task]["strategy"][A]
            self.assertEqual(x["accepted_clusters"],10)
            self.assertEqual(x["wrong_clusters"],0)
            self.assertGreater(x["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],.25)
        savings=d["task_stratified_32cluster_bootstrap_getter_savings_EXPLORATORY"]
        self.assertEqual(savings["A_vs_B"]["observed_total_original_private_getters_saved"],20)
        self.assertEqual(savings["A_vs_mandatory_C"]["observed_total_original_private_getters_saved"],25)
        self.assertGreater(savings["A_vs_mandatory_C"]["bootstrap_total_getters_saved_95pct_exploratory"][0],0)
        self.assertEqual(savings["A_vs_mandatory_C"]["observed_clusters_where_method_spent_more"],0)
        self.assertEqual(savings["A_vs_mandatory_C"]["total_independent_task_reset_clusters"],32)
        self.assertEqual(d["native_task_paired_differences_A_vs_C"]["A_only"],0)
        self.assertEqual(d["native_task_paired_differences_A_vs_C"]["fixed_only"],0)

    def test_one_wrong_event_in_multiple_correlated_truths_counts_one_wrong_cluster(self):
        rows=[]
        for t in range(4):
            rows.append({"task":"pull_cube","seed":1234,"truth":t,
                         "success":{a:True for a in (A,B,C)},
                         "reads":{a:0 for a in (A,B,C)},
                         "public_xyz":{a:2 for a in (A,B,C)},
                         "confidence":{A:t in (0,1),B:False},
                         "wrong":{A:t==1,B:False}})
        r=_stats([rows])["strategy"][A]
        self.assertEqual(r["accepted_events"],2)
        self.assertEqual(r["accepted_clusters"],1)
        self.assertEqual(r["wrong_events"],1)
        self.assertEqual(r["wrong_clusters"],1)
        self.assertEqual(r["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],1.)

    def test_always_query_must_not_be_declared_zero_risk_bound(self):
        rows=[{"success":{A:True,B:True,C:True},"reads":{A:1,B:1,C:1},
               "public_xyz":{A:2,B:2,C:0},"confidence":{A:False,B:False},
               "wrong":{A:False,B:False}} for _ in range(4)]
        v=_stats([rows])["strategy"]
        self.assertEqual(v[A]["accepted_clusters"],0)
        self.assertEqual(v[A]["exact_one_sided_95pct_upper_any_wrong_in_authorizing_reset_if_iid"],1.)
        self.assertEqual(v[C]["naive_per_decision_iid_95pct_upper_NOT_JUSTIFIED"],1.)

    def test_bad_source_label_missing_authorization_fails_closed(self):
        rows=[{"success":{A:True,B:True,C:True},"reads":{A:0,B:0,C:1},
               "public_xyz":{A:2,B:2,C:0},"confidence":{A:False,B:False},
               "wrong":{A:True,B:False}} for _ in range(4)]
        with self.assertRaisesRegex(ValueError,"Source wrong without"):
            _stats([rows])

    def test_exact_binomial_bounds_and_no_128_iid_shortcut(self):
        self.assertAlmostEqual(exact_one_sided_upper(0,20),1-.05**(1/20),places=12)
        self.assertAlmostEqual(exact_one_sided_upper(0,26),1-.05**(1/26),places=12)
        self.assertEqual(exact_one_sided_upper(0,0),1.)
        self.assertEqual(exact_one_sided_upper(1,1),1.)
        with self.assertRaises(ValueError):exact_one_sided_upper(2,1)

if __name__=="__main__":
    unittest.main()
