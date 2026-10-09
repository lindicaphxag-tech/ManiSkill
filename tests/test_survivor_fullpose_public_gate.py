"""No simulator: falsify public full-pose history selection and full action provenance."""
import math
import unittest

from research.survivor_full_pose_public_gate import (
    choose_full_pose_history_from_public_xyz as choose
)

QUATS=((0.,0.,0.,1.),(0.,0.,math.sin(.3),math.cos(.3)),
       (0.,math.sin(.4),0.,math.cos(.4)),
       (math.sin(.2),0.,0.,math.cos(.2)))


class SurvivorPublicHistoryTests(unittest.TestCase):
    def test_discarded_rotations_must_not_block_unique_complete_pose(self):
        a=choose([.003,.02,.04,.07],QUATS,.006944262561376447)
        self.assertTrue(a['authorized'])
        self.assertEqual(a['index'],0)
        self.assertIn('INHERITS_COMPLETE_SE3_HISTORY',a['reason'])

    def test_ambiguous_positions_cannot_claim_unique_rotational_history(self):
        a=choose([.003,.004,.04,.07],QUATS,.006944262561376447)
        self.assertFalse(a['authorized'])
        self.assertEqual(a['viable'],[0,1])

    def test_unique_without_two_mm_margin_must_query(self):
        a=choose([.003,.008,.04,.07],QUATS,.006944262561376447)
        self.assertFalse(a['authorized'])
        self.assertEqual(a['reason'],'INSUFFICIENT_RESIDUAL_CLEARANCE')

    def test_no_compatible_public_response_falsifies_model(self):
        a=choose([.02,.03,.04,.07],QUATS,.006944262561376447)
        self.assertFalse(a['authorized'])
        self.assertEqual(a['reason'],'AMBIGUOUS_OR_MODEL_FALSIFIED_PUBLIC_XYZ')

    def test_incomplete_history_must_not_guess(self):
        for key in ('histories_complete','provenance_trusted','action_chart_verified'):
            with self.subTest(k=key):
                a=choose([.003,.02,.04,.07],QUATS,.006944262561376447,**{key:False})
                self.assertFalse(a['authorized'])

    def test_malformed_discarded_pose_invalidates_provenance(self):
        for bad in ((float('nan'),0,0,1),(0.,0.,0.,0.),(0.,0.,0.,2.)):
            with self.subTest(bad=bad):
                a=choose([.003,.02,.04,.07],[QUATS[0],bad,*QUATS[2:]],.006944262561376447)
                self.assertFalse(a['authorized'])

    def test_immutable_margin_and_error_bounds(self):
        self.assertFalse(choose([.003,.02,.04,.07],QUATS,.006944262561376447,
                                historical_margin_m=.0)['authorized'])
        self.assertFalse(choose([.003,.02,.04,.07],QUATS,-1.)['authorized'])
        self.assertFalse(choose([.003,.02,.04,.07],QUATS,float('nan'))['authorized'])

    def test_nonfinite_proprioception_fails_closed(self):
        for val in (float('nan'),float('inf'),-1):
            d=choose([.003,val,.04,.07],QUATS,.006944262561376447)
            self.assertFalse(d['authorized'])

    def test_no_private_full_pose_is_generated(self):
        a=choose([.003,.02,.04,.07],QUATS,.006944262561376447)
        self.assertEqual(set(a),{'authorized','index','reason','viable','orientation_evidence'})
        self.assertNotIn('quaternion',str(a).lower())


if __name__=="__main__":
    unittest.main()
