"""Unit tests of exact paired uncertainty and original source-integrity guards."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from paired_query_stats import (
    _binomial_cdf,
    _binomial_survival,
    _load_original_rows,
    analyze_originals,
    clopper_pearson,
    exact_discordant_sign_test,
    paired_difference_interval_bonferroni,
)


class ExactPairedInference(unittest.TestCase):
    def test_exact_discordant_p_reference(self):
        # 5 success improvements, 2 deteriorations -> 2*(1+7+21)/128
        self.assertEqual(exact_discordant_sign_test(5,2), 0.453125)
        self.assertEqual(exact_discordant_sign_test(0,0), 1.0)
        self.assertEqual(exact_discordant_sign_test(4,0), 0.125)
        self.assertEqual(exact_discordant_sign_test(1,1), 1.0)

    def test_exact_binomial_tails_and_confidence_limits(self):
        self.assertAlmostEqual(_binomial_cdf(0,1,0.4), .6)
        self.assertAlmostEqual(_binomial_survival(1,1,0.4), .4)
        self.assertAlmostEqual(clopper_pearson(0,1)[1], .975,places=10)
        self.assertAlmostEqual(clopper_pearson(1,1)[0], .025,places=10)
        self.assertEqual(clopper_pearson(0,10)[0],0)
        self.assertEqual(clopper_pearson(10,10)[1],1)
        lo,hi=clopper_pearson(15,64)
        self.assertLess(lo,15/64)
        self.assertGreater(hi,15/64)

    def test_conservative_joint_risk_difference_interval(self):
        lo,hi=paired_difference_interval_bonferroni(5,2,64)
        self.assertLess(lo,0)
        self.assertGreater(hi,0)
        self.assertLessEqual(lo,3/64)
        self.assertGreaterEqual(hi,3/64)
        with self.assertRaises(ValueError):
            paired_difference_interval_bonferroni(50,20,64)

    def test_no_invalid_count_or_alpha(self):
        for args in [(-1,7),(8,7),(1,0),(1.0,4),(True,4)]:
            with self.subTest(args=args),self.assertRaises(ValueError):
                clopper_pearson(*args)
        for args in [(-1,0),(0,-1),(1.0,1)]:
            with self.subTest(args=args),self.assertRaises(ValueError):
                exact_discordant_sign_test(*args)
        for alpha in [0,1,float("nan"),float("inf")]:
            with self.subTest(alpha=alpha),self.assertRaises(ValueError):
                clopper_pearson(1,4,alpha)

    def test_source_pinned_original_full_64_denominator(self):
        result=analyze_originals()
        self.assertEqual(result["n"],64)
        self.assertEqual(result["n_trained_policies"],2)
        self.assertEqual(result["selective_success"],60)
        self.assertEqual(result["mandatory_success"],57)
        self.assertEqual(result["selective_privileged_decision_reads"],15)
        self.assertEqual(result["mandatory_privileged_decision_reads"],64)
        self.assertEqual(result["paired_adaptive_only_success"],5)
        self.assertEqual(result["paired_mandatory_only_success"],2)
        self.assertEqual(result["exact_two_sided_discordant_sign_test_p"],.453125)
        self.assertEqual(result["relative_read_reduction"],.765625)
        self.assertEqual(set(result["per_task_original_paired"]),{"pull_cube","stack_cube"})

    def test_missing_sha256_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                _load_original_rows(Path(tmp))

    def test_fake_improvement_does_not_pass_original_locked_counts(self):
        source=_load_original_rows()
        fake=[dict(x) for x in source]
        fake[0]["selective_success"]=False
        with patch("paired_query_stats._load_original_rows", return_value=fake):
            with self.assertRaisesRegex(ValueError,"preregistered outcomes changed"):
                analyze_originals()


if __name__=="__main__":
    unittest.main()
