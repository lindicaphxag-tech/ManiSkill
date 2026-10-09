"""Historic real StackCube t0 float32/float64 SO(3) boundary witness.

Scientific claim: only native commanded-target admissibility after a
float32 dispatch. No measured PhysX rollout nor hardware safety claim.
"""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation

from research.action_abi_history_observer import TargetPose, ActionHistoryObserver
from research.native_action_precision_contract import authorize_native_cartesian_ee


class RealNativeTypedPrecisionGate(unittest.TestCase):
    def setUp(self):
        self.historic_rounding_component=np.float32(0.5773508548736572)
        self.rot=np.array([self.historic_rounding_component]*3,dtype=np.float32)
        self.old=TargetPose.from_arrays([0,0,0],[0,0,0,1])
        self.target=TargetPose.from_arrays(
            [0,0,0],
            Rotation.from_euler("XYZ",-0.1*(self.rot/np.linalg.norm(self.rot.astype(np.float64)))).as_quat(),
        )
        self.kw=dict(
            proposed_native_action=np.r_[np.zeros(3,dtype=np.float32),self.rot],
            desired_commanded_target=self.target,
            possible_previous_target_poses=(self.old,),
            low_xyz=-.1,high_xyz=.1,normalized_euler_rot_scale=-.1,
            max_position_inf_m=.001,max_orientation_geodesic_rad=.001,
            complete_trusted_histories=True,verified_root_left_chart=True,
        )

    def test_observed_f32_f64_rounding_crosses_the_true_gate(self):
        f32=float(np.linalg.norm(self.rot))
        f64=float(np.linalg.norm(self.rot.astype(np.float64)))
        self.assertLessEqual(f32,1+1e-6)
        self.assertGreater(f64,1+1e-6)
        self.assertAlmostEqual(f32,1.0000009536743164,places=12)
        self.assertAlmostEqual(f64,1.0000010144344997,places=12)
        self.assertGreater(f64-f32,0)
        observer=ActionHistoryObserver(-.1,.1,-.1)
        observer.reset(self.old)
        with self.assertRaisesRegex(ValueError,"Unrepresentable target rotation"):
            observer.prepare(np.r_[np.zeros(3),self.rot])

    def test_native_f32_legalized_then_recomputed_setpoint(self):
        cert=authorize_native_cartesian_ee(**self.kw)
        self.assertTrue(cert.accepted,cert.reason)
        self.assertTrue(cert.is_nonexact_projection)
        self.assertLess(cert.worst_commanded_orientation_error_rad,.001)
        self.assertLessEqual(
            np.linalg.norm(np.asarray(cert.normalized_command[3:],dtype=np.float64)),1+1e-8)
        observer=ActionHistoryObserver(-.1,.1,-.1)
        observer.reset(self.old)
        observer.prepare(cert.normalized_command) # Real native observer accepts same transported bytes.
        self.assertIsNotNone(observer._pending)

    def test_wrong_desired_setpoint_never_authorized_by_radial_projection(self):
        cfg=dict(self.kw)
        cfg["desired_commanded_target"]=self.old
        cfg["max_orientation_geodesic_rad"]=.0001
        cert=authorize_native_cartesian_ee(**cfg)
        self.assertFalse(cert.accepted)
        self.assertEqual(cert.reason,"UNBOUNDED_COMMANDED_ORIENTATION_ERROR")
        self.assertIsNone(cert.normalized_command)

    def test_two_histories_can_fail_even_if_command_is_native_legal(self):
        second=TargetPose.from_arrays([.02,0,0],[0,0,0,1])
        cfg=dict(self.kw)
        cfg["possible_previous_target_poses"]=(self.old,second)
        cfg["max_position_inf_m"]=.01
        fail=authorize_native_cartesian_ee(**cfg)
        self.assertFalse(fail.accepted)
        self.assertEqual(fail.reason,"UNBOUNDED_COMMANDED_POSITION_ERROR")
        cfg["max_position_inf_m"]=.025
        ok=authorize_native_cartesian_ee(**cfg)
        self.assertTrue(ok.accepted)
        self.assertAlmostEqual(ok.worst_commanded_position_error_m,.02)

    def test_untrusted_or_wrong_native_chart_always_refuses(self):
        for key in ("complete_trusted_histories","verified_root_left_chart"):
            with self.subTest(key=key):
                cfg=dict(self.kw)
                cfg[key]=False
                v=authorize_native_cartesian_ee(**cfg)
                self.assertFalse(v.accepted)
                self.assertIsNone(v.normalized_command)

    def test_bad_native_shapes_nonfinite_scales_budgets_and_history_set(self):
        cases=[
            {"proposed_native_action":[0]*5},
            {"proposed_native_action":[0,0,0,0,0,float("nan")]},
            {"low_xyz":.1,"high_xyz":-.1},
            {"normalized_euler_rot_scale":0},
            {"max_position_inf_m":-1},
            {"max_orientation_geodesic_rad":float("nan")},
            {"possible_previous_target_poses":()},
        ]
        for item in cases:
            with self.subTest(item=item):
                cfg=dict(self.kw);cfg.update(item)
                cert=authorize_native_cartesian_ee(**cfg)
                self.assertFalse(cert.accepted)
                self.assertIsNone(cert.normalized_command)

    def test_128_deterministic_randomized_transport_roundtrips(self):
        rng=np.random.default_rng(20261009)
        for i in range(128):
            rot=rng.normal(size=3).astype(np.float32)
            rot*=np.float32(rng.uniform(.99,1.01)/np.linalg.norm(rot.astype(np.float64)))
            proposed=np.r_[np.zeros(3,dtype=np.float32),rot]
            projected=rot.astype(np.float64)/max(1.,np.linalg.norm(rot.astype(np.float64)))
            desired=TargetPose.from_arrays([0,0,0],
                        Rotation.from_euler("XYZ",-.1*projected).as_quat())
            cfg=dict(self.kw)
            cfg.update(proposed_native_action=proposed,desired_commanded_target=desired)
            cert=authorize_native_cartesian_ee(**cfg)
            self.assertTrue(cert.accepted,f"{i} {cert.reason}")
            self.assertLess(cert.worst_commanded_orientation_error_rad,.001)
            observer=ActionHistoryObserver(-.1,.1,-.1)
            observer.reset(self.old)
            observer.prepare(cert.normalized_command)


if __name__=="__main__":
    unittest.main()
