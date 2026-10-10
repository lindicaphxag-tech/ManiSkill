"""Small adversarial probability families; theoretical model assumptions only."""
import unittest
from dataclasses import replace
from research.authority_budget import counterexample, choose, evaluate_unpruned
from research.authority_family import family_choice, altered_failure_rate

class FamilyTests(unittest.TestCase):
    def test_adverse_transition_change_rejects_nominal_two_probes(self):
        m=counterexample()
        bad=altered_failure_rate(m,.25)
        nominal=choose(m,2,.2)
        self.assertEqual(nominal.name,'probe')
        family=family_choice((m,bad),2,.2)
        self.assertEqual(family.policy,'QUERY')
        self.assertAlmostEqual(family.worst_cost,4.)
        self.assertEqual(family.worst_risk,0.)
        def to_tree(p):
            if not p.children:return p.name
            rules=dict(p.children)
            return (p.name,tuple(to_tree(rules[o]) if o in rules else 'QUERY'
                                 for o in m.probes[0].observations))
        cost,risk=evaluate_unpruned(bad,to_tree(nominal))
        self.assertGreater(risk,.2)

    def test_single_model_matches_exact_frontier(self):
        m=counterexample()
        for cap in (.1,.2,1.):
            result=family_choice((m,),2,cap)
            optimal=choose(m,2,cap)
            self.assertAlmostEqual(result.worst_cost,optimal.cost)

    def test_family_contract_drift_is_rejected(self):
        m=counterexample()
        with self.assertRaisesRegex(ValueError,'only varies'):
            family_choice((m,replace(m,query_cost=3.)),1,.2)

    def test_empty_family_and_shift_invalid(self):
        with self.assertRaises(ValueError): family_choice((),1,.1)
        with self.assertRaises(ValueError): altered_failure_rate(counterexample(),1.5)

if __name__=='__main__':unittest.main()
