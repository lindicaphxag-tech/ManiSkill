"""Multi-history commanded-target action authority: independent physical-chart witnesses."""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import TargetPose, ActionHistoryObserver
from research.multi_history_authority import (
    Authority, certify_multi_history_action,
)

ID=tuple(float(x) for x in (0,0,0,1))

def pose(x,y=0,z=0,angle=0):
    return TargetPose.from_arrays((x,y,z),Rotation.from_euler("XYZ",(0,0,angle)).as_quat())

def certificate(poses,desired=pose(.0),**opts):
    kwargs=dict(pos_lower=(-.2,-.2,-.2),pos_upper=(.2,.2,.2),
                rot_lower=(.5,.5,.5),
                position_budget_m=.06,rotation_budget_rad=.06,
                histories_complete=True,trusted_history=True,
                age_steps=0,max_age_steps=0,
                root_left_rotation_verified=True)
    kwargs.update(opts)
    return certify_multi_history_action(tuple(poses),desired,**kwargs)

def genuine_native_result(start,action):
    actual=ActionHistoryObserver([-.2]*3,[.2]*3,.5)
    actual.reset(start)
    t=actual.prepare(action)
    actual.acknowledge(t.ticket,applied=True)
    return actual.pose


class MultiHistoryAuthorityTest(unittest.TestCase):
    def test_four_distinct_translation_histories_physical_replay(self):
        hist=[pose(-.05),pose(.02),pose(.06),pose(.0)]
        cert=certificate(hist,position_budget_m=.06)
        self.assertTrue(cert.authorized,cert)
        self.assertEqual(cert.credible_history_count,4)
        self.assertAlmostEqual(cert.exact_position_radius_m,.055,places=8)
        for p in hist:
            real=genuine_native_result(p,cert.command_normalized_6d)
            self.assertLessEqual(np.max(np.abs(np.asarray(real.position))),.05500001)
            self.assertLessEqual(
                (Rotation.from_quat(real.quaternion_xyzw).magnitude()),1e-8)

    def test_position_radius_is_exact_under_legal_box_saturation(self):
        rng=np.random.default_rng(13)
        for _ in range(31):
            states=[pose(float(a)) for a in rng.uniform(-.14,.14,size=5)]
            result=certificate(states,position_budget_m=1.0)
            # Independent brute finite grid plus analytic box center lower bound:
            # no alternative feasible translational action can achieve lower
            # max absolute target error than the analytical clipped midpoint.
            base=np.array([x.position for x in states])
            u=np.clip(-(.5*(np.min(base,axis=0)+np.max(base,axis=0))),-.2,.2)
            true=float(np.max(np.abs(base+u)))
            self.assertAlmostEqual(result.exact_position_radius_m,true,12)
            for a in np.linspace(-.2,.2,17):
                worst=float(np.max(np.abs(base+np.array([a,0,0]))))
                self.assertGreaterEqual(worst+1e-10,true)

    def test_three_rotations_have_real_evaluated_upper_and_lower_bounds(self):
        hist=[pose(0,angle=v) for v in (-.07,.0,.11,.02)]
        cert=certificate(hist,rotation_budget_rad=.10)
        self.assertTrue(cert.authorized,cert)
        self.assertAlmostEqual(cert.universal_rotation_lower_bound_rad,.09,places=7)
        self.assertGreaterEqual(cert.verified_rotation_upper_bound_rad+1e-8,
                                cert.universal_rotation_lower_bound_rad)
        self.assertGreaterEqual(cert.evaluated_orientation_centers,4)
        self.assertGreater(cert.representable_orientation_centers,0)
        for p in hist:
            actual=genuine_native_result(p,cert.command_normalized_6d)
            relative=Rotation.from_quat(actual.quaternion_xyzw)
            self.assertLessEqual(relative.magnitude(),cert.verified_rotation_upper_bound_rad+1e-7)

    def test_rotation_unrepresentable_not_silently_clipped(self):
        hist=[pose(0,angle=v) for v in (.8,1.0,1.2)]
        res=certificate(hist,rot_lower=.02,rotation_budget_rad=1.2)
        self.assertEqual(res.authority,Authority.REFUSE_NATIVE_ROTATION)
        self.assertIsNone(res.command_normalized_6d)

    def test_true_bounding_failures_not_relabelled_as_success(self):
        hist=[pose(-.11),pose(.11),pose(.0)]
        p=certificate(hist,position_budget_m=.05)
        self.assertEqual(p.authority,Authority.REFUSE_POSITION_BOUND)
        self.assertIsNone(p.command_normalized_6d)
        rot=certificate([pose(0,angle=a) for a in (-.09,0,.09)],rotation_budget_rad=.02)
        self.assertEqual(rot.authority,Authority.REFUSE_ROTATION_BOUND)

    def test_fail_closed_incomplete_stale_untrusted_and_controller_unknown(self):
        h=(pose(-.01),pose(.01),pose(0),pose(.03))
        for kw,reason in [
            ({"histories_complete":False},Authority.REFUSE_INCOMPLETE_HISTORIES),
            ({"trusted_history":False},Authority.REFUSE_UNTRUSTED_OR_STALE),
            ({"age_steps":2,"max_age_steps":1},Authority.REFUSE_UNTRUSTED_OR_STALE),
            ({"root_left_rotation_verified":False},Authority.REFUSE_UNVERIFIED_CHART),
        ]:
            c=certificate(h,**kw)
            self.assertEqual(c.authority,reason)
            self.assertIsNone(c.command_normalized_6d)

    def test_invalid_numeric_and_belief_budget_rejected(self):
        for values in [(),(pose(0),),tuple(pose(i/100) for i in range(257))]:
            with self.assertRaises(ValueError):certificate(values)
        with self.assertRaises(ValueError):certificate([pose(0),pose(.1)],pos_lower=(0,0,0),pos_upper=(0,0,0))
        with self.assertRaises(ValueError):certificate([pose(0),pose(.1)],position_budget_m=float("nan"))

    def test_two_history_overlap_never_claims_new_global_so3_theorem(self):
        h=[pose(0,angle=-.05),pose(0,angle=.05)]
        c=certificate(h)
        self.assertTrue(c.authorized)
        self.assertAlmostEqual(c.universal_rotation_lower_bound_rad,.05,8)
        self.assertAlmostEqual(c.verified_rotation_upper_bound_rad,.05,8)
        self.assertEqual(c.credible_history_count,2)


if __name__=="__main__":
    unittest.main()
