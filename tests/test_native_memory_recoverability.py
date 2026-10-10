import unittest
from math import sin, cos, pi
from research.native_memory_recoverability import (
    Target, Belief, diameter, relative_target_command,
    public_observation_without_validated_likelihood,
    trusted_target_read, privileged_public_reanchor)
from research.native_memory_funnel_certificate import Pose, assess

I=(0.,0.,0.,1.)
def target(x,angle=0.):
    return Target((x,0.,0.),(0.,0.,sin(angle/2),cos(angle/2)))

class NativeMemoryCapabilityContractTests(unittest.TestCase):
    def test_delta_cannot_shrink_translation_or_rotation_support(self):
        b=Belief((target(-.04,-.2),target(.04,.1),target(.0,.15)))
        before=diameter(b)
        q=(0.,sin(.2),0.,cos(.2))
        ans=relative_target_command(b,root_translation_m=(.012,-.01,.02),
                                    root_left_rotation_xyzw=q,verified_native_frame=True)
        self.assertAlmostEqual(ans.after.translation_linf_m,before.translation_linf_m,places=10)
        self.assertAlmostEqual(ans.after.rotation_geodesic_rad,before.rotation_geodesic_rad,places=7)
        self.assertEqual(ans.privileged_writes,0)
        self.assertFalse(ans.exact_memory_identity_restored)
    def test_existing_funnel_negative_lower_bound_agrees_with_operator(self):
        b=Belief((target(-.04),target(.04)))
        op=relative_target_command(b,root_translation_m=(.01,0.,0.),
                                   root_left_rotation_xyzw=I,verified_native_frame=True)
        self.assertAlmostEqual(op.after.translation_linf_m,.08)
        f=assess(histories=(Pose((-.04,0.,0.),I),Pose((.04,0.,0.),I)),
                 desired=Pose((0.,0.,0.),I),delta_lower=(-.05,)*3,
                 delta_upper=(.05,)*3,position_budget_inf_m=.02,
                 rotation_budget_rad=.05,
                 controller_frame="root_translation:root_aligned_body_rotation",
                 verified_contract=True)
        self.assertEqual(f.status,"IMPOSSIBLE_UNDER_COMMON_RELATIVE_DELTA")
    def test_public_pose_observation_does_not_forge_target_provenance(self):
        b=Belief((target(0.),target(.015)))
        r=public_observation_without_validated_likelihood(b)
        self.assertEqual(r.belief_after,b)
        self.assertGreater(r.after.translation_linf_m,0)
        self.assertEqual(r.privileged_reads,0)
    def test_trusted_getter_reduces_epistemic_not_physical_uncertainty(self):
        b=Belief((target(0.),target(.025)))
        r=trusted_target_read(b,verified_native_target=target(.025),provenance_attested=True)
        self.assertEqual(r.privileged_reads,1)
        self.assertFalse(r.changed_physical_target)
        self.assertEqual(r.after.translation_linf_m,0.)
    def test_setter_requires_verified_privilege(self):
        b=Belief((target(0.),target(.04)))
        with self.assertRaises(ValueError):
            privileged_public_reanchor(b,public_achieved=target(.01),
                 internal_write_verified=False,controller_contract_verified=True)
        r=privileged_public_reanchor(b,public_achieved=target(.01),
                 internal_write_verified=True,controller_contract_verified=True)
        self.assertEqual(r.privileged_writes,1)
        self.assertTrue(r.changed_physical_target)
        self.assertTrue(r.exact_memory_identity_restored)
        self.assertEqual(r.belief_after.hypotheses[0].position,(.01,0.,0.))
    def test_unsafe_or_unproven_action_chart_refuses(self):
        b=Belief((target(0.),))
        with self.assertRaises(ValueError):
            relative_target_command(b,root_translation_m=(0.,0.,0.),
                 root_left_rotation_xyzw=I,verified_native_frame=False)
    def test_quaternion_sign_is_same_rotation(self):
        b=Belief((Target((0.,0.,0.),I),Target((0.,0.,0.),(0.,0.,0.,-1.))))
        self.assertAlmostEqual(diameter(b).rotation_geodesic_rad,0.,places=10)
    def test_invalid_hypotheses_fail_closed(self):
        with self.assertRaises(ValueError):Belief(())
        with self.assertRaises(ValueError):Belief(tuple(target(i) for i in range(17)))
        with self.assertRaises(ValueError):Target((0.,0.,0.),(0.,0.,0.,0.))
        with self.assertRaises(ValueError):Target((0.,0.,float('nan')),I)
    def test_multi_step_relative_probes_do_not_collapse(self):
        b=Belief((target(-.02,-.1),target(.01,.2)))
        start=diameter(b)
        for i in range(12):
            b=relative_target_command(b,root_translation_m=((i%3-1)*.003,.001,0.),
                 root_left_rotation_xyzw=(0.,0.,sin(.02),cos(.02)),
                 verified_native_frame=True).belief_after
        end=diameter(b)
        self.assertAlmostEqual(start.translation_linf_m,end.translation_linf_m,places=9)
        self.assertAlmostEqual(start.rotation_geodesic_rad,end.rotation_geodesic_rad,places=7)

if __name__=="__main__":unittest.main()
