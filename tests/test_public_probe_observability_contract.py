"""Falsifying tests for conditional probe-identifiability, NOT native-PhysX tests."""
import math
import unittest

from research.public_probe_observability_contract import (
    Gate, Observation, ProbeContract, ProbePlan, _segment_distance, _segment_separation_lower_bound,
    plan_public_probe, identify_after_probe,
)


def contract(**changes):
    args = dict(
        targets_xyz_m=((0.02, 0, 0), (0.03, 0, 0)),
        public_before_xyz_m=(0, 0, 0),
        source_desired_target_xyz_m=(0.025, 0, 0),
        gain_min=0.4, gain_max=0.6,
        public_model_error_l2_m=0.001,
        numerical_guard_m=0.0001,
        native_delta_min_xyz_m=(-0.1, -0.1, -0.1),
        native_delta_max_xyz_m=(0.1, 0.1, 0.1),
        max_probe_translation_l2_m=0.05,
        max_target_deviation_linf_m=0.08,
        histories_complete=True, provenance_trusted=True,
        controller_chart_verified=True,
        calibration_independent_attested=True,
    )
    args.update(changes)
    return ProbeContract(**args)


class GeometryTests(unittest.TestCase):
    def test_crossing_segments(self):
        self.assertAlmostEqual(_segment_distance(
            ((-1, 0, 0), (1, 0, 0)),
            ((0, -1, 0), (0, 1, 0))), 0.0, places=12)

    def test_parallel_overlap_and_skew(self):
        self.assertEqual(_segment_distance(
            ((0, 0, 0), (1, 0, 0)),
            ((0.5, 0, 0), (2, 0, 0))), 0.0)
        self.assertAlmostEqual(_segment_distance(
            ((0, 0, 0), (1, 0, 0)),
            ((0, -1, 2), (0, 1, 2))), 2.0, places=12)

    def test_interior_boundaries_against_fine_grid(self):
        # No optimization using a source trajectory; 17 deterministic geometries.
        for k in range(17):
            a = ((0, 0, 0), (1 + k / 100.0, 0.25, 0.1))
            b = ((0.3, -0.2, 0.1 + k / 20.0), (0.4, 0.8, 0.4))
            exact = _segment_distance(a, b)
            brute = min(math.dist(
                tuple(a[0][j] + s / 40.0 * (a[1][j] - a[0][j]) for j in range(3)),
                tuple(b[0][j] + t / 40.0 * (b[1][j] - b[0][j]) for j in range(3)))
                for s in range(41) for t in range(41))
            self.assertGreaterEqual(exact, 0.0)
            self.assertLessEqual(exact, brute + 1e-10)


    def test_certified_lower_bound_never_overstates_sampled_distance(self):
        # If a conservative certificate already exceeds any sampled candidate
        # minimum, it is not a valid geometric separation lower bound.
        for k in range(21):
            a = ((0., 0., 0.), (1., 0.000001*k, 0.))
            b = ((0.1, 0.0000003*k, 0.00001),
                 (1.1, 0.0000008*k, 0.00001))
            certified = _segment_separation_lower_bound(a, b)
            sampled_upper = min(math.dist(
                tuple(a[0][j] + s / 20. * (a[1][j]-a[0][j]) for j in range(3)),
                tuple(b[0][j] + t / 20. * (b[1][j]-b[0][j]) for j in range(3)))
                for s in range(21) for t in range(21))
            self.assertLessEqual(certified, sampled_upper + 1e-10)

    def test_zero_gain_stall_impossibility(self):
        # All histories allow y=x when zero physical progress is possible.
        p = contract(gain_min=0.0)
        decision = plan_public_probe(p, [(0., .05, 0.)],
                                     privileged_query_available=True)
        self.assertEqual(decision.gate, Gate.QUERY_REQUIRED)


class ContractTests(unittest.TestCase):
    def test_angular_probe_can_split_overlap_without_private_reads(self):
        p = contract()
        no_active = plan_public_probe(p, [], privileged_query_available=True)
        self.assertEqual(no_active.gate, Gate.QUERY_REQUIRED)
        d = plan_public_probe(p, [(0, 0.05, 0)], privileged_query_available=True)
        self.assertEqual(d.gate, Gate.PROBE_TRANSLATE)
        self.assertEqual(d.translation_xyz_m, (0.0, 0.05, 0.0))
        self.assertGreater(d.worst_pair_clearance_after_noise_m, 0)
        seg = d.segments_by_history[0]
        actual = tuple((seg[0][j] + seg[1][j]) / 2 for j in range(3))
        o = identify_after_probe(d, actual, known_native_dispatch_confirmed=True)
        self.assertEqual(o.status, Observation.UNIQUE)
        self.assertEqual(o.history_index, 0)

    def test_prefer_zero_motion_when_already_distinguishable(self):
        p = contract(targets_xyz_m=((0, 0, 0), (0.08, 0, 0)),
                     max_target_deviation_linf_m=0.09)
        d = plan_public_probe(p, [(0, 0.01, 0)], privileged_query_available=True)
        self.assertEqual(d.gate, Gate.PROBE_ZERO)
        self.assertEqual(d.translation_xyz_m, (0.0, 0.0, 0.0))

    def test_three_history_all_pairs_must_separate(self):
        p = contract(targets_xyz_m=((0.02, 0, 0),
                                    (0.03, 0, 0),
                                    (0.03, 0, 0)))
        d = plan_public_probe(p, [(0, .05, 0)], privileged_query_available=True)
        self.assertEqual(d.gate, Gate.QUERY_REQUIRED)

    def test_unattested_or_incomplete_refuse_without_query(self):
        for edits in ({"calibration_independent_attested": False},
                      {"histories_complete": False},
                      {"provenance_trusted": False},
                      {"controller_chart_verified": False}):
            p = contract(**edits)
            self.assertEqual(plan_public_probe(p, [(0, .05, 0)],
                             privileged_query_available=False).gate, Gate.REFUSE)
            self.assertEqual(plan_public_probe(p, [(0, .05, 0)],
                             privileged_query_available=True).gate, Gate.QUERY_REQUIRED)

    def test_native_or_target_cap_excludes_unsafe_probes(self):
        p = contract(native_delta_max_xyz_m=(.1, .01, .1),
                     native_delta_min_xyz_m=(-.1, -.01, -.1))
        self.assertEqual(plan_public_probe(p, [(0, .05, 0)],
                          privileged_query_available=True).gate, Gate.QUERY_REQUIRED)
        p = contract(max_target_deviation_linf_m=0.001)
        self.assertEqual(plan_public_probe(p, [(0, .05, 0)],
                          privileged_query_available=False).gate, Gate.REFUSE)

    def test_model_falsification_and_ack_of_probe_itself(self):
        d = plan_public_probe(contract(), [(0, .05, 0)],
                              privileged_query_available=True)
        self.assertEqual(identify_after_probe(d, (10, 0, 0),
                         known_native_dispatch_confirmed=True).status,
                         Observation.MODEL_FALSIFIED)
        self.assertEqual(identify_after_probe(d, (0, 0, 0),
                         known_native_dispatch_confirmed=False).status,
                         Observation.REFUSE_UNVERIFIED_DISPATCH)

    def test_bad_contract_rejected_and_no_guess_from_missing_probe(self):
        for edits in ({"gain_min": .8, "gain_max": .4},
                      {"public_model_error_l2_m": float("nan")},
                      {"targets_xyz_m": ((0, 0, 0),)},
                      {"native_delta_min_xyz_m": (0.01, -0.1, -0.1)}):
            with self.assertRaises(ValueError):
                plan_public_probe(contract(**edits), [],
                                  privileged_query_available=True)
        denied = plan_public_probe(contract(calibration_independent_attested=False),
                                   [], privileged_query_available=True)
        with self.assertRaises(ValueError):
            identify_after_probe(denied, (0, 0, 0),
                                 known_native_dispatch_confirmed=True)

    def test_probe_candidate_order_deterministic(self):
        p = contract()
        one = plan_public_probe(p, [(0, .05, 0), (0, -.05, 0)],
                                privileged_query_available=True)
        two = plan_public_probe(p, [(0, -.05, 0), (0, .05, 0)],
                                privileged_query_available=True)
        self.assertEqual(one, two)


if __name__ == "__main__":
    unittest.main()
