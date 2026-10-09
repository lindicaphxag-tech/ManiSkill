"""No physical safety guarantee from tiny/training-reused probe response sets."""
import math
import unittest

from research.probe_calibration_assurance import (
    calibrated_nonexclusion_radius as radius,
    minimum_clusters_for_nonvacuous as minimum,
)

class ProbeCalibrationAssuranceTests(unittest.TestCase):
    def test_eight_clusters_two_histories_95pct_is_vacuous(self):
        d=radius([0.001]*8,joint_alpha=.05,possible_histories=2,
                 selector_fixed_before_calibration=True,
                 score_model_fixed_before_calibration=True)
        self.assertEqual(d.group_count,8)
        self.assertEqual(d.conformal_rank,9)
        self.assertFalse(d.finite)
        self.assertEqual(d.radius_m,math.inf)
        self.assertEqual(minimum(.05,2),39)

    def test_joint_histories_requires_additional_clusters(self):
        self.assertEqual(minimum(.05,4),79)
        self.assertFalse(radius([.001]*39,joint_alpha=.05,possible_histories=4,
                                selector_fixed_before_calibration=True,
                                score_model_fixed_before_calibration=True).finite)

    def test_same_data_selected_probe_is_invalid_even_with_more_clusters(self):
        r=radius([0.001]*100,joint_alpha=.05,possible_histories=2,
                 selector_fixed_before_calibration=False,
                 score_model_fixed_before_calibration=True)
        self.assertFalse(r.finite)
        self.assertIn("selection used",r.explanation)

    def test_finite_not_robot_safety_and_needs_exchangeability(self):
        r=radius([.001]*38+[.002],joint_alpha=.05,possible_histories=2,
                 selector_fixed_before_calibration=True,
                 score_model_fixed_before_calibration=True)
        self.assertTrue(r.finite)
        self.assertAlmostEqual(r.radius_m,.002)
        self.assertFalse(r.contact_and_ood_safety_guaranteed)
        self.assertTrue(r.independent_reset_clusters_required)

    def test_reject_nonfinite_duplicate_unsupported_nonfinite_samples(self):
        for values in ([],[float("nan")],[float("inf")],[-1.],[".01"]):
            with self.assertRaises(ValueError):
                radius(values,joint_alpha=.05,possible_histories=2,
                       selector_fixed_before_calibration=True,
                       score_model_fixed_before_calibration=True)
        with self.assertRaises(ValueError):
            minimum(0.,2)

if __name__=="__main__":
    unittest.main()
