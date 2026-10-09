"""Strictly informationally honest proactive query and fail-closed behavioral tests."""
from types import SimpleNamespace
import unittest
from research.authority_slack_query_gate import proactive_authority_slack

def cert(p,r,auth=True):
    return SimpleNamespace(authorized=auth,worst_position_inf_m=p,worst_orientation_geodesic_rad=r)

class AuthoritySlackPrecommitTests(unittest.TestCase):
    def test_authorizes_continue_below_threshold_without_query(self):
        decide,ratio=proactive_authority_slack(cert(.02,.01),step=4)
        self.assertFalse(decide)
        self.assertAlmostEqual(ratio,.4)

    def test_queries_within_budget_before_it_is_too_late(self):
        decision,ratio=proactive_authority_slack(cert(.04,.01),step=4)
        self.assertTrue(decision)
        self.assertAlmostEqual(ratio,.8)

    def test_considers_rotation_geodesic_not_only_position(self):
        decision,ratio=proactive_authority_slack(cert(.005,.045),step=4)
        self.assertTrue(decision)
        self.assertAlmostEqual(ratio,.9)

    def test_unrepresentable_common_command_queries_once(self):
        self.assertEqual(proactive_authority_slack(cert(float("inf"),float("inf"),False),step=4),(True,float("inf")))
        self.assertFalse(proactive_authority_slack(cert(.05,.05,False),step=5)[0])

    def test_query_only_phase_and_never_twice(self):
        for t in (0,2,3,5,19):
            self.assertFalse(proactive_authority_slack(cert(.049,.049),step=t)[0])
        self.assertFalse(proactive_authority_slack(cert(.049,.049),step=4,already_queried=True)[0])

    def test_nan_bad_bounds_refuse_before_query(self):
        for x in (-.01,float("nan")):
            with self.assertRaises(ValueError):
                proactive_authority_slack(cert(x,0),step=4)
        with self.assertRaises(ValueError):
            proactive_authority_slack(cert(0,0),step=True)
        with self.assertRaises(ValueError):
            proactive_authority_slack(cert(0,0),step=4,already_queried=1)
        with self.assertRaises(ValueError):
            proactive_authority_slack(SimpleNamespace(authorized=True),step=4)

if __name__=="__main__":
    unittest.main()
