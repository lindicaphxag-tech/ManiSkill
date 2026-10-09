"""No-GPU adversarial contracts for the preregistered two-robot low-signal probing study."""
import unittest
from research.low_signal_probe_selection_physx import (
    PROBES, CAL, TEST, SCALE, ROBOTS, calibration_selection, preflight
)

class LowSignalProbeSourceContract(unittest.TestCase):
    def test_preoutcome_git_provenance_and_distinct_cohorts(self):
        d=preflight()
        self.assertEqual(SCALE,.08)
        self.assertEqual(len(set(ROBOTS)),2)
        for name in ROBOTS:
            self.assertTrue(set(range(CAL[name],CAL[name]+8)).isdisjoint(set(range(TEST[name],TEST[name]+8))))
        self.assertEqual(d["expected_world_counts"]["total"],192)

    def test_frozen_probe_equal_nonzero_native6_norm(self):
        self.assertEqual(sum(x*x for x in PROBES["x"]),sum(x*x for x in PROBES["y"]))
        self.assertGreater(sum(x*x for x in PROBES["x"]),0)
        self.assertEqual(PROBES["zero"],(0.,)*6)

    def test_select_by_calibration_score_not_hidden_test_truth(self):
        def class_model(dx,r):
            return {"class_models":{
                "held":{"mean_public_motion_m":[0.,0.,0.],"envelope_radius_m":r},
                "applied":{"mean_public_motion_m":[dx,0.,0.],"envelope_radius_m":r}
            }}
        pick,scores=calibration_selection({"x":class_model(.004,.001),
                                           "y":class_model(.008,.001)})
        self.assertEqual(pick,"y")
        self.assertGreater(scores["y"]["worst_response_ball_margin_m"],
                           scores["x"]["worst_response_ball_margin_m"])
        tied,_=calibration_selection({"x":class_model(.004,.001),"y":class_model(.004,.001)})
        self.assertEqual(tied,"x")

    def test_calibration_overlap_can_be_negative_and_is_not_safety_certificate(self):
        bad={"class_models":{
              "held":{"mean_public_motion_m":[0.,0.,0.],"envelope_radius_m":.003},
              "applied":{"mean_public_motion_m":[.001,0.,0.],"envelope_radius_m":.003}}}
        pick,s=calibration_selection({"x":bad,"y":bad})
        self.assertEqual(pick,"x")
        self.assertLess(s[pick]["worst_response_ball_margin_m"],0)

if __name__=="__main__":
    unittest.main()
