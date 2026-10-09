"""Dependency-free BEFORE-outcome falsifiers for cross-robot ACK-amplitude shift.

No generated synthetic labels are advertised as native PhysX outcomes.
"""
import unittest
from copy import deepcopy
from research.cross_robot_ack_amplitude_inference import predict
from research.cross_robot_online_proprio_classifier import decide

class TestAmplitudeShiftNoRetuning(unittest.TestCase):
    def setUp(self):
        self.model={
            "radius_margin_m":0.002,
            "class_models":{
                "applied":{"mean_public_motion_m":[0.02,0.,0.],
                           "envelope_radius_m":0.004},
                "held":{"mean_public_motion_m":[0.,0.,0.],
                        "envelope_radius_m":0.004}
            }
        }
    def test_original_method_is_bit_for_bit_unchanged_at_scale_one(self):
        x=[0.019,0.,0.]
        self.assertEqual(predict(x,self.model,1.0,"frozen_scale1"),
                         decide(x,self.model))
    def test_affine_at_scale_one_matches_original_without_retraining(self):
        x=[0.019,0.,0.]
        a=predict(x,self.model,1.0,"command_affine")
        b=decide(x,self.model)
        for k in b:
            self.assertEqual(a[k],b[k])
    def test_predeclared_smaller_command_can_falsify_frozen_envelope(self):
        # Synthetic numerical witness only: not measured robot behavior.
        response=[0.008,0,0]
        frozen=predict(response,self.model,0.4,"frozen_scale1")
        scaled=predict(response,self.model,0.4,"command_affine")
        self.assertIsNone(frozen["label"])
        self.assertEqual(scaled["label"],"applied")
    def test_original_source_model_not_modified_by_affine(self):
        before=deepcopy(self.model)
        predict([0.008,0,0],self.model,0.4,"command_affine")
        self.assertEqual(self.model,before)
    def test_ambiguous_both_envelopes_refuse(self):
        m=deepcopy(self.model)
        m["class_models"]["held"]["envelope_radius_m"]=0.020
        m["class_models"]["applied"]["envelope_radius_m"]=0.020
        self.assertIsNone(predict([0.008,0,0],m,0.4,"command_affine")["label"])
    def test_unknown_or_unsafe_amplitude_rejected(self):
        for amp in [0.,-0.1,1.5,float("nan"),float("inf"),"0.4"]:
            with self.assertRaises(ValueError):
                predict([0,0,0],self.model,amp,"command_affine")
    def test_no_modification_of_original_label_contract(self):
        r=predict([0.,0.,0.],self.model,0.4,"command_affine")
        self.assertEqual(r["private_target_getter_calls_at_decision"],0)
        self.assertEqual(r["label"],"held")
    def test_public_xyz_nonfinite_fails_closed(self):
        with self.assertRaises(ValueError):
            predict([float("nan"),0,0],self.model,0.4,"command_affine")

if __name__=="__main__":
    unittest.main()
