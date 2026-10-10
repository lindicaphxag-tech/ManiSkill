import unittest
from dataclasses import replace
from research.cira_intervention_gate import (Candidate, Outcome, Pair, ResetCluster,
     evaluate, cp_upper)

class TestCIRAInterventionGate(unittest.TestCase):
    def sample(self,n=256,*,active=True,zero=False,wrong=False,matched=True,
               fit=(999999,),model=True,contract="contract-v1"):
        clusters=[]
        for i in range(n):
            z=Outcome(zero,False,0,0)
            x=Outcome(active,wrong,0,1)
            pairs=tuple(Pair(str(j),z,x,matched,matched) for j in range(4))
            clusters.append(ResetCluster("stack","Panda",i,pairs))
        return Candidate("X","Panda",contract,"response-model-v1",
                         fit,tuple(clusters),model)

    def gate(self,c,**kwargs):
        return evaluate(candidates=(c,),task="stack",controller="Panda",
                        live_action_contract_sha="contract-v1",**kwargs)

    def test_small_cluster_risk_cannot_certify(self):
        self.assertGreater(cp_upper(0,16,.025),.1)
        self.assertLess(cp_upper(0,256,.025),.1)

    def test_synthetic_large_sample_positive_logic_not_task_result(self):
        d=self.gate(self.sample())
        self.assertEqual(d.selected,"X")
        self.assertEqual(d.authority,"QUERY")

    def test_task_harm_despite_information_cannot_pass(self):
        d=self.gate(self.sample(active=False,zero=True))
        self.assertEqual(d.selected,"ZERO")
        self.assertIn("NO_CONFIDENT_POSITIVE_TASK_ADVANTAGE",
                      d.diagnostics[0]["rejection_reasons"])

    def test_wrong_authorization_blocks_apparent_reward(self):
        d=self.gate(self.sample(wrong=True))
        self.assertEqual(d.selected,"ZERO")
        self.assertIn("UNCERTIFIED_COMPLETE_STATE_AUTHORITY_RISK",
                      d.diagnostics[0]["rejection_reasons"])

    def test_action_response_model_unvalidated(self):
        d=self.gate(self.sample(model=False))
        self.assertEqual(d.selected,"ZERO")
        self.assertIn("ACTION_RESPONSE_MODEL_NOT_INDEPENDENTLY_VALIDATED",
                      d.diagnostics[0]["rejection_reasons"])

    def test_native_abi_mismatch(self):
        d=self.gate(self.sample(contract="bad"))
        self.assertEqual(d.selected,"ZERO")
        self.assertIn("NATIVE_ACTION_CONTRACT_MISMATCH",
                      d.diagnostics[0]["rejection_reasons"])

    def test_fit_cluster_leakage(self):
        d=self.gate(self.sample(fit=(4,999)))
        self.assertEqual(d.selected,"ZERO")
        self.assertIn("MODEL_FIT_CALIBRATION_LEAKAGE",
                      d.diagnostics[0]["rejection_reasons"])

    def test_unmatched_initial_state_or_sensing(self):
        d=self.gate(self.sample(matched=False))
        self.assertEqual(d.selected,"ZERO")
        self.assertIn("UNMATCHED_SENSING_OR_INITIAL_STATE",
                      d.diagnostics[0]["rejection_reasons"])

    def test_ack_truths_are_not_independent_units(self):
        d=self.gate(self.sample(n=16))
        self.assertEqual(d.selected,"ZERO")
        self.assertEqual(d.diagnostics[0]["n_independent_resets"],16)
        self.assertEqual(d.diagnostics[0]["n_correlated_truth_cells"],64)

    def test_multiplicity_adjustment(self):
        a=self.sample()
        b=replace(a,name="Y")
        d=evaluate(candidates=(a,b),task="stack",controller="Panda",
                   live_action_contract_sha="contract-v1")
        self.assertAlmostEqual(d.diagnostics[0]["alpha_per_statement"],.0125)

    def test_invalid_cost_refuses(self):
        c=self.sample()
        changed=replace(c.clusters[0].pairs[0],
                        active=Outcome(True,False,2,1))
        first=replace(c.clusters[0],pairs=(changed,)+c.clusters[0].pairs[1:])
        d=self.gate(replace(c,clusters=(first,)+c.clusters[1:]))
        self.assertEqual(d.selected,"ZERO")
        self.assertIn("INVALID_OUTCOME",d.diagnostics[0]["rejection_reasons"])

if __name__=="__main__":
    unittest.main()
