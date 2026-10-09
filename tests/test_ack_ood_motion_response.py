"""Deterministic source-separated OOD empirical classifier falsifiers."""
import unittest
from research.ood_ack_motion_response import (
    FROZEN_GAIN,PRIOR_PHYSX_PUBLIC_MODEL_GIT_BLOB,
    predict_ood_public_history,response_segment_residual)

class TestOODPublicMotion(unittest.TestCase):
    def test_frozen_prior_physical_model_id_and_gains(self):
        self.assertEqual(PRIOR_PHYSX_PUBLIC_MODEL_GIT_BLOB,
                         "8b3e11cf342170984093321993eb4dc9bf168ffc")
        self.assertEqual(set(FROZEN_GAIN),{"panda","xarm6_robotiq"})
        self.assertEqual(FROZEN_GAIN["panda"][0],0.37494315058733085)

    def test_true_public_observation_identifies_separate_target(self):
        d=predict_ood_public_history(
            robot="panda",public_before_xyz=(0,0,0),
            public_after_xyz=(.022,0,0),
            applied_history_target_xyz=(.05,0,0),
            held_history_target_xyz=(-.05,0,0))
        self.assertEqual(d["label"],"applied")
        self.assertEqual(d["matching_histories"],["applied"])
        self.assertTrue(d["no_privileged_state_reads_for_inference"])

    def test_overlapping_histories_abstain(self):
        d=predict_ood_public_history(
            robot="panda",public_before_xyz=(0,0,0),
            public_after_xyz=(0,0,0),
            applied_history_target_xyz=(0,0,0),
            held_history_target_xyz=(0,0,0))
        self.assertEqual(d["status"],"ABSTAIN_OVERLAP")
        self.assertIsNone(d["label"])

    def test_unmodeled_public_response_falsifies(self):
        d=predict_ood_public_history(
            robot="panda",public_before_xyz=(0,0,0),
            public_after_xyz=(9,0,0),
            applied_history_target_xyz=(.05,0,0),
            held_history_target_xyz=(-.05,0,0))
        self.assertEqual(d["status"],"MODEL_FALSIFIED")
        self.assertIsNone(d["label"])

    def test_zero_response_alpha_interval_can_make_probing_impossible(self):
        d=predict_ood_public_history(
            robot="xarm6_robotiq",public_before_xyz=(0,0,0),
            public_after_xyz=(0,0,0),
            applied_history_target_xyz=(.05,0,0),
            held_history_target_xyz=(-.05,0,0))
        self.assertEqual(d["status"],"MODEL_FALSIFIED")

    def test_finite_input_and_gain_gate(self):
        with self.assertRaises(ValueError):
            predict_ood_public_history(
                robot="other",public_before_xyz=(0,0,0),
                public_after_xyz=(0,0,0),
                applied_history_target_xyz=(0,0,0),
                held_history_target_xyz=(0,0,0))
        with self.assertRaises(ValueError):
            response_segment_residual([0,0,0],[0,0,0],[1,0,0],.8,.2)
        with self.assertRaises(ValueError):
            response_segment_residual([0,0,0],[float("nan"),0,0],
                                      [1,0,0],.2,.8)

if __name__=="__main__":
    unittest.main()
