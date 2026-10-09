"""Multi-ACK robust SE(3) authorizer: adversarial and controller-recurrence gates."""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import TargetPose
from research.multi_ack_se3_bounded import common_multi_history_command
from research.two_history_se3_robust import common_two_history_command, Reason

def pose(pos, rot=(0,0,0)):
    return TargetPose.from_arrays(pos, Rotation.from_rotvec(rot).as_quat())

def call(old, target=None, **override):
    cfg=dict(pos_lower=[-.1]*3,pos_upper=[.1]*3,rot_lower=[.2]*3,
       position_budget_m=.05,rotation_budget_rad=.05,
       hypotheses_complete=True,trusted_provenance=True,
       age_steps=0,max_age_steps=0,
       root_translation_root_left_rotation_verified=True)
    cfg.update(override)
    return common_multi_history_command(tuple(old),
        target or pose([0,0,0]),**cfg)

class KHistoryCertificateTests(unittest.TestCase):
    def test_four_states_have_one_real_common_action(self):
        old=[pose([j,0,0],(0,0,k)) for j,k in
             [(-.015,-.015),(-.005,.005),(.005,-.005),(.015,.015)]]
        c=call(old)
        self.assertTrue(c.authorized)
        self.assertEqual(c.hypotheses,4)
        command=np.asarray(c.normalized_6d)
        displacement=(command[:3]+1)/2*.2-.1
        actual_rot=Rotation.from_euler("XYZ",command[3:]*.2)
        maxpos=max(np.max(np.abs(np.asarray(p.position)+displacement))
                   for p in old)
        maxrot=max((actual_rot*Rotation.from_quat(p.quaternion_xyzw)).magnitude()
                   for p in old)
        self.assertLessEqual(maxpos,c.worst_position_inf_m+1e-10)
        self.assertAlmostEqual(maxrot,c.worst_orientation_geodesic_rad,places=8)

    def test_pair_preserves_original_source_implementation(self):
        old=(pose([-.01,0,0],(0,0,-.005)),pose([.01,0,0],(0,0,.005)))
        common=dict(pos_lower=[-.1]*3,pos_upper=[.1]*3,
                    rot_lower=[.2]*3,position_budget_m=.05,
                    rotation_budget_rad=.05,hypotheses_complete=True,
                    trusted_provenance=True,age_steps=0,max_age_steps=0,
                    root_translation_root_left_rotation_verified=True)
        a=common_multi_history_command(old,pose([0,0,0]),**common)
        b=common_two_history_command(old,pose([0,0,0]),**common)
        self.assertEqual(a,b)

    def test_geometrically_incompatible_belief_refused(self):
        c=call([pose([j,0,0]) for j in (-.1,0,.1)])
        self.assertFalse(c.authorized)
        self.assertIs(c.reason,Reason.REFUSE_POSITION_BUDGET)
        self.assertIsNone(c.normalized_6d)

    def test_missing_provenance_stale_or_chart_refused(self):
        old=[pose([0,0,0]) for _ in range(3)]
        for kw,expected in [
           (dict(hypotheses_complete=False),Reason.REFUSE_INCOMPLETE_HYPOTHESES),
           (dict(trusted_provenance=False),Reason.REFUSE_STALE_OR_UNTRUSTED),
           (dict(age_steps=2,max_age_steps=1),Reason.REFUSE_STALE_OR_UNTRUSTED),
           (dict(root_translation_root_left_rotation_verified=False),
               Reason.REFUSE_UNVERIFIED_CONTROLLER)]:
            self.assertIs(call(old,**kw).reason,expected)

    def test_native_orientation_chart_refuses_saturated_command(self):
        old=[pose([0,0,0]) for _ in range(3)]
        out=call(old,pose([0,0,0],(0,0,1.0)))
        self.assertFalse(out.authorized)
        self.assertIs(out.reason,Reason.REFUSE_UNREPRESENTABLE_ROTATION)

    def test_over_budget_hypotheses_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"1–16"):
            call([pose([0,0,0]) for _ in range(17)])

    def test_randomized_authorizations_verify_all_native_outcomes(self):
        rng=np.random.default_rng(9210)
        n_ok=0
        for _ in range(100):
            positions=rng.uniform(-.02,.02,(4,3))
            rotations=rng.uniform(-.02,.02,(4,3))
            old=[pose(p,r) for p,r in zip(positions,rotations)]
            c=call(old)
            if not c.authorized: continue
            n_ok+=1
            native=np.array(c.normalized_6d)
            translation=native[:3]*.1
            rotation=Rotation.from_euler("XYZ",native[3:]*.2)
            for p in old:
                actual=np.array(p.position)+translation
                self.assertLessEqual(float(np.max(abs(actual))),.05+1e-7)
                actual_q=rotation*Rotation.from_quat(p.quaternion_xyzw)
                self.assertLessEqual(float(actual_q.magnitude()),.05+1e-7)
        self.assertGreater(n_ok,50)

if __name__=="__main__":
    unittest.main()
