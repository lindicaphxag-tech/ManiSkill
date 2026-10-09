"""Deterministic preregistered phase query and untrusted-controller negative tests."""
from types import SimpleNamespace
import unittest
from research.phase_information_gate import phase_information_gate as gate

def c(p,r,ok=True):
    return SimpleNamespace(authorized=ok,worst_position_inf_m=p,worst_orientation_geodesic_rad=r)

class PhaseInformationGates(unittest.TestCase):
    def test_pull_low_local_setpoint_risk_early_query(self):
        query,ratio=gate(c(.030,.010),task="pull_cube",step=4)
        self.assertTrue(query)
        self.assertAlmostEqual(ratio,.6)
    def test_pull_high_risk_continue_if_still_authorized(self):
        q,r=gate(c(.040,.010),task="pull_cube",step=4)
        self.assertFalse(q);self.assertAlmostEqual(r,.8)
    def test_refusal_triggers_one_trusted_query(self):
        self.assertTrue(gate(c(.060,.001,False),task="pull_cube",step=4)[0])
    def test_stack_always_one_early_query(self):
        self.assertTrue(gate(c(.001,.001),task="stack_cube",step=4)[0])
    def test_no_out_of_phase_or_double_query(self):
        for t in (0,1,2,3,5,10):
            self.assertFalse(gate(c(.001,.001),task="stack_cube",step=t)[0])
        self.assertFalse(gate(c(.001,.001),task="stack_cube",step=4,already_queried=True)[0])
    def test_out_of_task_or_malformed_certificate_fails_closed(self):
        for v in (-.01,float("nan")):
            with self.assertRaises(ValueError):gate(c(v,.01),task="pull_cube",step=4)
        with self.assertRaises(ValueError):gate(c(.01,.01),task="unknown",step=4)
        with self.assertRaises(ValueError):gate(SimpleNamespace(authorized=True),task="stack_cube",step=4)
        with self.assertRaises(ValueError):gate(c(.01,.01),task="stack_cube",step=True)
    def test_constant_threshold_not_learned_from_current_test(self):
        self.assertEqual(gate(c(.0375,.0),task="pull_cube",step=4)[0],False)
        self.assertEqual(gate(c(.0374,.0),task="pull_cube",step=4)[0],True)

if __name__=="__main__":
    unittest.main()
