"""Deliberately include a validated anchor that STILL accepts a wrong
history after the response regime shifts. This is the non-certificate test.
"""
import unittest
from research.public_ack_authority_core import (
    CompleteTargetHistory as H, KnownTargetAnchor as A,
    public_segment_residual,public_only_authority)

Q=(0.,0.,0.,1.)
A0=A((0.,0.,0.),(.01,0.,0.),(.04,0.,0.),1)

class PublicAuthorityTest(unittest.TestCase):
    def test_native_target_correct_history_known_anchor_uses_no_private_state(self):
        z=public_only_authority(A0,(0.,0.,0.),(.02,0.,0.),
                [H("actually_applied",(.05,0.,0.),Q),
                 H("actually_held",(0.,.05,0.),Q)],
                 epsilon_m=.003)
        self.assertEqual(z.mode,"AUTHORIZE_COMPLETE_HISTORY")
        self.assertEqual(z.selected_history_id,"actually_applied")
        self.assertEqual(z.public_samples_charged,4)
        self.assertAlmostEqual(z.anchor_residual_m,0)
    def test_anchor_model_mismatch_must_query(self):
        z=public_only_authority(A((0.,0.,0.),(.01,.02,0.),(.04,0.,0.),1),
                (0.,0.,0.),(.02,0.,0.),
                [H("applied",(.05,0.,0.),Q),H("held",(0.,.05,0.),Q)],
                epsilon_m=.003)
        self.assertEqual(z.mode,"QUERY_NATIVE_TARGET")
        self.assertEqual(z.reason,"KNOWN_ACK_MOTION_RESPONSE_MODEL_FAILED")
    def test_uninformative_anchor_must_query(self):
        z=public_only_authority(A((0.,0.,0.),(0.,0.,0.),(.001,0.,0.),1),
                (0.,0.,0.),(.02,0.,0.),
                [H("a",(.05,0.,0.),Q),H("b",(0.,.05,0.),Q)],
                epsilon_m=.003)
        self.assertEqual(z.mode,"QUERY_NATIVE_TARGET")
        self.assertEqual(z.reason,"KNOWN_ACK_ANCHOR_INSUFFICIENT_EXCITATION")
    def test_same_XYZ_different_orientation_not_identifiable(self):
        z=public_only_authority(A0,(0.,0.,0.),(.02,0.,0.),
            [H("a",(.05,0.,0.),Q),H("b",(.05,0.,0.),(.0,0,1.,0.))],
            epsilon_m=.003)
        self.assertEqual(z.mode,"QUERY_NATIVE_TARGET")
    def test_failed_model_can_still_pass_earlier_anchor_NOT_A_CERTIFICATE(self):
        # In a regime shift AFTER the known t1 action, target 0 is ACTUALLY
        # true but response on the public channel resembles target 1.
        z=public_only_authority(A0,(0.,0.,0.),(0.,.02,0.),
            [H("actually_executed",(.05,0.,0.),Q),
             H("wrong_prior",(0.,.05,0.),Q)],epsilon_m=.003)
        self.assertEqual(z.mode,"AUTHORIZE_COMPLETE_HISTORY")
        self.assertEqual(z.selected_history_id,"wrong_prior")
        # This test is a mandatory falsification of safety-certificate claims.
    def test_nonfinite_and_bad_quaternion_fail_closed(self):
        with self.assertRaises(ValueError):
            public_only_authority(A0,(0.,0.,0.),(float("nan"),0.,0.),
                [H("a",(.05,0.,0.),Q),H("b",(0.,.05,0.),Q)],epsilon_m=.003)
        with self.assertRaises(ValueError):
            public_only_authority(A0,(0.,0.,0.),(.01,0.,0.),
                [H("a",(.05,0.,0.),(0,0,0,2)),
                 H("b",(0.,.05,0.),Q)],epsilon_m=.003)
    def test_end_segment_and_orthogonal_distances(self):
        self.assertAlmostEqual(public_segment_residual(
            (0.,0.,0.),(.1,.02,0.),(.04,0.,0.)),(0.06**2+.02**2)**.5)
        self.assertAlmostEqual(public_segment_residual(
            (0.,0.,0.),(.02,0.,0.),(.04,0.,0.)),0.)
if __name__=="__main__": unittest.main()
