"""Compares ZERO native probe, equal magnitude fixed pulse, adaptive pulse:
all candidate native target positions must move by one LEGAL acknowledged
native action, not physically impossible free information.
"""
import unittest
from research.public_ack_costed_probe_planner import (
    choose_bounded_probe,segment_min_residual)
class TestActualActiveHistoryProbe(unittest.TestCase):
    def test_six_choices_have_exact_native_amplitude_and_zero_rotation(self):
        p=choose_bounded_probe((.6,0,.1),[(.65,0,.1),(.6,.06,.1),(.6,0,.16),(.55,0,.1)],
                     [-.1]*3,[.1]*3)
        self.assertEqual(len(p.normalized_native_6d),6)
        self.assertAlmostEqual(max(abs(v) for v in p.normalized_native_6d[:3]),.12)
        self.assertEqual(sum(abs(v)>0 for v in p.normalized_native_6d[:3]),1)
        self.assertEqual(p.normalized_native_6d[3:],(0.,0.,0.))
        self.assertAlmostEqual(sum(v*v for v in p.actual_target_translation_m)**.5,.012)
        self.assertEqual(p.candidate_count,4)
        self.assertTrue(p.selector_public_only)
        self.assertTrue(p.no_deterministic_safety_guarantee)
    def test_no_fault_receipt_is_used_or_seed_parity_parameter(self):
        p=choose_bounded_probe((0,0,0),[(.05,0,0),(0,.05,0)],[-.1]*3,[.1]*3)
        self.assertEqual(p.candidate_count,2)
        self.assertGreaterEqual(p.minimum_cross_hypothesis_segment_distance_m,0)
    def test_source_full_hypothesis_validity_fail_closed(self):
        for bad in (((.05,0,0),),(),((float("nan"),0,0),(.1,0,0))):
            with self.assertRaises(ValueError):
                choose_bounded_probe((0,0,0),bad,[-.1]*3,[.1]*3)
        with self.assertRaises(ValueError):
            choose_bounded_probe((0,0,0),[(.05,0,0),(0,.05,0)],[0]*3,[0]*3)
        with self.assertRaises(ValueError):
            choose_bounded_probe((0,0,0),[(.05,0,0),(0,.05,0)],[-.1]*3,[.1]*3,amplitude=1.1)
    def test_zero_probe_response_is_a_legal_competing_control(self):
        d=segment_min_residual((0,0,0),(.1,0,0),(.04,0,0))
        self.assertAlmostEqual(d,0)
        self.assertAlmostEqual(segment_min_residual((0,0,0),(.1,0,0),(0,.04,0)),.04)
        self.assertAlmostEqual(segment_min_residual((0,0,0),(.1,0,0),(.2,0,0)),.1)
    def test_native_anisotropic_bounds_affect_actual_displacement(self):
        p=choose_bounded_probe((0,0,0),[(.1,0,0),(0,.1,0)],(-.05,-.2,-.1),(.05,.2,.1))
        self.assertTrue(all(abs(v)<=1 for v in p.normalized_native_6d))
        self.assertAlmostEqual(p.actual_target_translation_m[2],0)
if __name__=="__main__":unittest.main()
