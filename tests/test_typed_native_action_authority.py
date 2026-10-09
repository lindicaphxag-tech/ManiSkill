"""Independent typed native admissibility falsifiers, including REAL sourced failure witness.

Original genuine CPU PhysX strict-shared-budget cohort:
StackCube seed 370029, step 0, native inverse rotation L2
1.0000009536743164, physical fault scheduled at t=2 NOT reached.
This test uses the SOURCE-REPORTED NORM, but reconstructs a synthetic
rotation vector with that norm; it is NOT the original full 6D action.
It is a numerical regression, not a simulator result or rescued task claim.
"""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import ActionHistoryObserver,TargetPose
from research.typed_native_action_authority import Admission,admit_typed_native_action

FRAME="root_translation:root_aligned_body_rotation"
ID=TargetPose.from_arrays((0,0,0),(0,0,0,1))

def gate(a,**kw):
    opts=dict(pos_lower=(-.1,-.1,-.1),pos_upper=(.1,.1,.1),
              rot_scale=(.5,.5,.5),
              known_controller_frame=FRAME,
              trusted_initial_controller_contract=True)
    opts.update(kw)
    return admit_typed_native_action(a,**opts)

def realized_original_native(a):
    observer=ActionHistoryObserver([-.1]*3,[.1]*3,.5)
    observer.reset(ID)
    ticket=observer.prepare(a)
    observer.acknowledge(ticket.ticket,applied=True)
    return observer.pose

class TypedActionContractTest(unittest.TestCase):
    def test_real_provenance_reported_370029_rotation_norm_repaired_not_task_outcome(self):
        reported=1.0000009536743164
        original=np.array([0,0,0,reported,0.,0.],dtype=float)
        before=reported
        x=gate(original)
        self.assertAlmostEqual(x.original_native_rot_norm,before,places=14)
        self.assertTrue(x.authorized)
        self.assertEqual(x.status,Admission.ROUNDOFF_CANONICALIZED)
        self.assertLess(x.executed_native_rot_norm,1-1e-6)
        self.assertLess(x.rotation_extra_setpoint_error_rad,1e-5)
        pose=realized_original_native(np.asarray(x.executable_native_6d,dtype=np.float32))
        source=Rotation.from_euler("XYZ",original[3:]*.5)
        result=Rotation.from_quat(pose.quaternion_xyzw)
        self.assertLessEqual((source.inv()*result).magnitude(),
                             x.rotation_extra_setpoint_error_rad+1e-6)

    def test_true_out_of_ball_refused_even_if_componentwise_within_bounds(self):
        vec=[0,0,0,.9,.9,0.]
        self.assertTrue(max(abs(v) for v in vec[3:])<=1)
        x=gate(vec)
        self.assertEqual(x.status,Admission.REFUSE_TRUE_UNREPRESENTABLE)
        self.assertFalse(x.authorized)
        self.assertIsNone(x.executable_native_6d)

    def test_valid_small_action_remains_byte_identical_in_float64_chart(self):
        a=[.31,-.24,.44,.11,-.05,.2]
        x=gate(a)
        self.assertEqual(x.status,Admission.UNMODIFIED)
        self.assertEqual(x.executable_native_6d,tuple(a))
        self.assertEqual(x.rotation_extra_setpoint_error_rad,0.)
        self.assertEqual(x.translation_extra_setpoint_error_inf_m,0.)

    def test_rounded_translation_recomputes_actual_physical_setpoint_error(self):
        a=[1+7e-7,0,0,.1,0,0]
        x=gate(a)
        self.assertTrue(x.authorized)
        self.assertEqual(x.status,Admission.ROUNDOFF_CANONICALIZED)
        self.assertAlmostEqual(x.translation_extra_setpoint_error_inf_m,7e-8,places=12)
        bad=gate(a,max_added_translation_setpoint_error_m=1e-9)
        self.assertFalse(bad.authorized)
        self.assertEqual(bad.status,Admission.REFUSE_SETPOINT_DISTORTION)

    def test_tight_rotation_error_budget_must_refuse_despite_small_overshoot(self):
        x=gate([0,0,0,1+7e-7,0,0],
               max_added_rotation_setpoint_error_rad=1e-12)
        self.assertFalse(x.authorized)
        self.assertEqual(x.status,Admission.REFUSE_SETPOINT_DISTORTION)
        self.assertGreater(x.rotation_extra_setpoint_error_rad,0)

    def test_wrong_controller_chart_or_unsupported_reset_history_is_not_admitted(self):
        for kw in [
            {"known_controller_frame":"body_rotation:root_translation"},
            {"trusted_initial_controller_contract":False},
        ]:
            x=gate([0]*6,**kw)
            self.assertEqual(x.status,Admission.REFUSE_BAD_CONTRACT)

    def test_nonfinite_and_malformed_are_rejected(self):
        bad=gate([0,0,0,np.nan,0,0])
        self.assertEqual(bad.status,Admission.REFUSE_NONFINITE)
        for seq in [(0,0),[0]*7]:
            with self.assertRaises(ValueError):gate(seq)
        with self.assertRaises(ValueError):
            gate([0]*6,pos_lower=(0,0,0),pos_upper=(0,1,1))

    def test_euler_so3_actual_geometry_randomized_and_float32_serialized(self):
        rng=np.random.default_rng(39)
        for _ in range(97):
            direction=rng.normal(size=3)
            direction/=np.linalg.norm(direction)
            # Original query generated from a true all-inlier, boundary or
            # infinitesimal float32 overshoot native action.
            radius=float(rng.uniform(1-1e-6,1+1e-6))
            action=np.r_[rng.uniform(-.9,.9,size=3),direction*radius]
            x=gate(action)
            self.assertTrue(x.authorized,x)
            native=np.asarray(x.executable_native_6d,dtype=np.float32)
            self.assertLess(float(np.linalg.norm(native[3:].astype(float))),1)
            physically_executed=realized_original_native(native)
            requested=Rotation.from_euler("XYZ",action[3:]*.5)
            commanded=Rotation.from_quat(physically_executed.quaternion_xyzw)
            self.assertLessEqual((requested.inv()*commanded).magnitude(),
                                 x.rotation_extra_setpoint_error_rad+1e-6)
            self.assertLess(x.rotation_extra_setpoint_error_rad,1e-5)

if __name__=="__main__":
    unittest.main()
