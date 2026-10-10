"""Synthetic model-mismatch tests; no native robotics execution."""
import unittest
from math import inf
from research.authority_voi import one_step_plan
from research.authority_voi_robust import (minimax_plan,outcome_policy_cost,
                                           shifted_sensor_pair)

class TestModelMismatch(unittest.TestCase):
    def test_nominal_sensor_flips_to_harmful_deployment(self):
        nominal,shifted=shifted_sensor_pair()
        plan=one_step_plan(nominal,nominal.probes[0])
        self.assertAlmostEqual(plan.expected_total_loss,.6)
        self.assertEqual(tuple(d.action for _,d in plan.decisions),
                         ("repair_a","repair_b"))
        self.assertEqual(outcome_policy_cost(shifted,"signal",
                         ("repair_a","repair_b")),inf)
        unbounded=type(shifted)(shifted.states,shifted.prior,
            shifted.actions,shifted.action_loss,shifted.query_cost,
            shifted.probes,risk_cap=None)
        self.assertAlmostEqual(outcome_policy_cost(unbounded,"signal",
                               ("repair_a","repair_b")),9.6)

    def test_robust_choice_prefers_unbiased_query(self):
        nominal,shifted=shifted_sensor_pair()
        chosen=minimax_plan((nominal,shifted))
        self.assertEqual(chosen.probe_name,"none")
        self.assertAlmostEqual(chosen.worst_expected_loss,2.)
        self.assertEqual(chosen.action_per_outcome,("QUERY",))

    def test_single_model_agrees_with_exact_oracle(self):
        nominal,_=shifted_sensor_pair()
        self.assertAlmostEqual(minimax_plan((nominal,)).worst_expected_loss,
                               one_step_plan(nominal,nominal.probes[0]).expected_total_loss)

    def test_differing_query_cost_contract_is_rejected(self):
        nominal,shifted=shifted_sensor_pair()
        altered=type(shifted)(shifted.states,shifted.prior,shifted.actions,
            shifted.action_loss,3.,shifted.probes,risk_cap=shifted.risk_cap)
        with self.assertRaises(ValueError):
            minimax_plan((nominal,altered))

if __name__=="__main__":
    unittest.main()
