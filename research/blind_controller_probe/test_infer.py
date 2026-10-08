"""Adversarial pure-stdlib checks for the exact production inference code."""
import unittest

from research.blind_controller_probe.infer import (
    ABSTAIN, ACHIEVED, REFUSE, TARGET, infer_zero_delta_reference,
)


class IdentifiabilityTests(unittest.TestCase):
    def setUp(self):
        self.achieved = (0.0, 0.0, 0.0)
        self.old = (0.006, 0.0, 0.0)

    def check(self, after, wanted):
        d = infer_zero_delta_reference(self.achieved, self.old, after)
        self.assertEqual(d.decision, wanted)
        return d

    def test_achieved_relative_zero_action(self):
        v = self.check((0.0, 0.0, 0.0), ACHIEVED)
        self.assertAlmostEqual(v.gap_m, 0.006)

    def test_target_relative_zero_action(self):
        self.check(self.old, TARGET)

    def test_noise_bounded_achieved(self):
        self.check((0.00004, 0.0, 0.0), ACHIEVED)

    def test_noise_bounded_target(self):
        self.check((0.00597, 0.0, 0.0), TARGET)

    def test_both_wrong_cannot_authorize_mode(self):
        self.check((0.003, 0.0, 0.0), ABSTAIN)

    def test_zero_gap_is_unidentifiable_even_if_after_matches(self):
        self.old = self.achieved
        self.check(self.achieved, ABSTAIN)

    def test_tiny_gap_is_unidentifiable(self):
        self.old = (0.0005, 0.0, 0.0)
        self.check(self.achieved, ABSTAIN)

    def test_tracking_gap_above_local_cap_refuses(self):
        self.old = (0.05, 0.0, 0.0)
        self.check(self.achieved, REFUSE)

    def test_nonnumeric_attack_denied(self):
        with self.assertRaises(ValueError):
            self.check(("bad", 0.0, 0.0), ACHIEVED)

    def test_nonfinite_attack_denied(self):
        with self.assertRaises(ValueError):
            self.check((float("nan"), 0.0, 0.0), ACHIEVED)

    def test_wrong_telemetry_dimension_denied(self):
        with self.assertRaises(ValueError):
            self.check((0.0, 0.0), ACHIEVED)

    def test_uncertainty_bounds_must_not_overlap(self):
        with self.assertRaises(ValueError):
            infer_zero_delta_reference(
                self.achieved, self.old, self.achieved,
                error_tolerance_m=0.001, min_identifiable_gap_m=0.001
            )

    def test_negative_unsafe_authority_bound_denied(self):
        with self.assertRaises(ValueError):
            infer_zero_delta_reference(
                self.achieved, self.old, self.achieved,
                max_preprobe_gap_m=-1,
            )

    def test_ambiguous_near_both_means_abstain(self):
        self.old = (0.0011, 0.0, 0.0)
        self.check((0.00055, 0.0, 0.0), ABSTAIN)

    def test_simulation_mode_labels_cannot_be_inputs(self):
        # The public inference routine receives only three 3D locations,
        # no policy/checkpoint/controller config/use_target label.
        import inspect
        params = inspect.signature(infer_zero_delta_reference).parameters
        self.assertEqual(
            list(params)[:3],
            ["achieved_before", "target_before", "commanded_target_after"],
        )
        self.assertNotIn("use_target", params)
        self.assertNotIn("mode", params)


if __name__ == "__main__":
    unittest.main()
