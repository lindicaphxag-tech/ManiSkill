"""Adversarial checks for posthoc scorer; no simulator or GPU needed."""
import math
import unittest

from research.replay_strong_matched_public_score128 import score_from_residuals, decide_score


class StrongScorerReanalysisContract(unittest.TestCase):
    def test_original_residual_weights_are_reproducible(self):
        eps = 0.006944262561376447
        r = [0.0031382162487262693, 0.005367528780046506, 0.005220886117161147, 0.005744083718509923]
        got = score_from_residuals(r, eps)
        expected = [0.2904449800516353, 0.23860422566205736, 0.2424766931728762, 0.22847410111343117]
        for a,b in zip(got, expected):
            self.assertAlmostEqual(a, b, places=13)

    def test_true_history_can_be_excluded_without_zero_residual_certificate(self):
        eps = 0.006944262561376447
        residuals = [0.0, 0.020, 0.024, 0.030]
        weights = score_from_residuals(residuals, eps)
        row = {"same_sensor_posterior_evidence": {
            "candidate_residuals_m": residuals,
            "prior_training_epsilon_m": eps,
            "posterior_weights": weights,
            "audit_only_true_candidate_indices": [1],
        }}
        admitted, wrong, index, _ = decide_score(row, 0.60)
        self.assertTrue(admitted)
        self.assertTrue(wrong)
        self.assertEqual(index, 0)

    def test_acceptance_at_060_not_at_095(self):
        eps = 0.006944262561376447
        residuals = [0.0, 0.013, 0.013, 0.013]
        weights = score_from_residuals(residuals, eps)
        self.assertLess(max(weights), .95)
        self.assertGreater(max(weights), .60)
        row = {"same_sensor_posterior_evidence": {
            "candidate_residuals_m": residuals,
            "prior_training_epsilon_m": eps,
            "posterior_weights": weights,
            "audit_only_true_candidate_indices": [0],
        }}
        self.assertTrue(decide_score(row, .60)[0])
        self.assertFalse(decide_score(row, .95)[0])

    def test_invalid_source_weights_are_not_silently_used(self):
        eps = .00694426256
        row = {"same_sensor_posterior_evidence": {
            "candidate_residuals_m": [0.0, .01, .02, .03],
            "prior_training_epsilon_m": eps,
            "posterior_weights": [1., 0., 0., 0.],
            "audit_only_true_candidate_indices": [0],
        }}
        with self.assertRaisesRegex(ValueError, "disagree"):
            decide_score(row, .6)

    def test_invalid_scaling_and_ground_truth_fail_closed(self):
        with self.assertRaises(ValueError):
            score_from_residuals([0., 0., float("nan"), 0.], .01)
        with self.assertRaises(ValueError):
            score_from_residuals([0., 0., 0., 0.], 0.)
        weights = score_from_residuals([0., .01, .02, .03], .01)
        row = {"same_sensor_posterior_evidence": {
            "candidate_residuals_m": [0., .01, .02, .03],
            "prior_training_epsilon_m": .01,
            "posterior_weights": weights,
            "audit_only_true_candidate_indices": [],
        }}
        with self.assertRaisesRegex(ValueError, "ground truth"):
            decide_score(row, .6)


if __name__ == "__main__":
    unittest.main()
