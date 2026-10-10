import unittest
from math import sqrt,pi
from research.native_memory_funnel_certificate import Pose,assess

I=(0.,0.,0.,1.)
def p(x,quat=I):return Pose((x,0.,0.),quat)
def gate(h,**kw):
    return assess(histories=h,desired=p(0.),
      delta_lower=(-.05,-.05,-.05),delta_upper=(.05,.05,.05),
      position_budget_inf_m=.02,rotation_budget_rad=.05,
      controller_frame="root_translation:root_aligned_body_rotation",
      verified_contract=True,**kw)

class MemoryFunnelTests(unittest.TestCase):
    def test_relative_zero_x_unable_to_collapse_8cm_memory_span(self):
        d=gate((p(-.04),p(.04)))
        self.assertEqual(d.status,"IMPOSSIBLE_UNDER_COMMON_RELATIVE_DELTA")
        self.assertAlmostEqual(d.exact_translation_lower_bound_m,.04)
        self.assertAlmostEqual(d.translation_pair_diameter_inf_m,.08)
    def test_irreducible_so3_geodesic_spread(self):
        from math import sin,cos
        q=(0.,0.,sin(.2/2),cos(.2/2))
        d=gate((p(0.),p(0.,q)))
        self.assertEqual(d.status,"IMPOSSIBLE_UNDER_COMMON_RELATIVE_DELTA")
        self.assertAlmostEqual(d.rotation_pair_diameter_rad,.2,places=6)
        self.assertAlmostEqual(d.universal_rotation_lower_bound_rad,.1,places=6)
    def test_saturation_can_prevent_even_single_history(self):
        d=gate((p(.3),))
        self.assertEqual(d.status,"IMPOSSIBLE_UNDER_COMMON_RELATIVE_DELTA")
        self.assertAlmostEqual(d.exact_translation_lower_bound_m,.25,places=7)
    def test_possible_geometric_budget_does_not_authorize_motion(self):
        d=gate((p(-.005),p(.005)))
        self.assertEqual(d.status,"UNKNOWN_FEASIBLE_GOAL_BUT_MEMORY_CANNOT_COLLAPSE")
        self.assertEqual(d.active_privileged_write_cost,0)
    def test_privileged_write_never_free_or_certified_safe(self):
        d=gate((p(-.005),p(.005)),has_authorized_absolute_target_write=True)
        self.assertEqual(d.status,"POTENTIAL_PRIVILEGED_REANCHOR_MUST_BE_EXECUTED_AND_AUDITED")
        self.assertEqual(d.active_privileged_write_cost,1)
    def test_single_history_still_not_safe_certificate(self):
        self.assertEqual(gate((p(.001),)).status,
                         "UNKNOWN_SINGLE_MEMORY_REQUIRES_NATIVE_VERIFICATION")
    def test_wrong_controller_action_contract_rejected(self):
        d=assess(histories=(p(0.),),desired=p(0.),
           delta_lower=(-.05,)*3,delta_upper=(.05,)*3,
           position_budget_inf_m=.05,rotation_budget_rad=.05,
           controller_frame="body_translation:body_aligned_body_rotation",
           verified_contract=True)
        self.assertEqual(d.status,"REFUSE_UNVERIFIED_CONTROLLER_CHART")
    def test_invalid_quaternion_rejected(self):
        with self.assertRaises(ValueError):gate((p(0.,(0.,0.,0.,.8)),))
    def test_unsound_underreported_translation_budget_rejected(self):
        with self.assertRaises(ValueError):
            assess(histories=(p(0.),),desired=p(0.),delta_lower=(-1.,)*3,
                   delta_upper=(1.,)*3,position_budget_inf_m=-.01,
                   rotation_budget_rad=.1,controller_frame="root_translation:root_aligned_body_rotation",
                   verified_contract=True)

if __name__=="__main__":unittest.main()
