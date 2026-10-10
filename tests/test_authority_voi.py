"""The oracle has only synthetic-model evidence, not PhysX validation."""
import random
import unittest

from research.authority_voi import (Model, Probe, authority_counterexample,
                                    brute_policy_cost, entropy_heuristic,
                                    one_step_plan, quotient_model, select_plan,
                                    validate)

class TestAuthorityVOI(unittest.TestCase):
    def test_task_relevance_falsifies_entropy_heuristic(self):
        m = authority_counterexample()
        chosen, entropy = select_plan(m), entropy_heuristic(m)
        self.assertEqual(chosen.name, "repair_group")
        self.assertEqual(entropy.name, "identity_within_group")
        self.assertAlmostEqual(chosen.expected_total_loss, .2)
        self.assertAlmostEqual(entropy.expected_total_loss, 2.2)
        self.assertAlmostEqual(one_step_plan(m).expected_total_loss, 2.)
        self.assertGreater(entropy.information_gain_bits, chosen.information_gain_bits)
        for p in m.probes:
            self.assertAlmostEqual(one_step_plan(m, p).expected_total_loss,
                                   brute_policy_cost(m, p))

    def test_no_help_from_diagnostic_nuisance(self):
        m = Model(("a","b"), (.2,.8), ("same",), ((0.,0.),), 3.,
                  (Probe("nuisance", .3, ("a","b"), ((1.,0.),(0.,1.))),))
        self.assertEqual(select_plan(m).name, "none")
        self.assertAlmostEqual(one_step_plan(m, m.probes[0]).expected_total_loss,.3)

    def test_uninformative_probe_query(self):
        m = Model(("x","y"), (.5,.5), ("A","B"),
                  ((0.,10.), (10.,0.)), 2.,
                  (Probe("uninformative",1.,("x","y"),((.5,.5),(.5,.5))),))
        self.assertEqual(select_plan(m).name,"none")
        self.assertAlmostEqual(one_step_plan(m,m.probes[0]).expected_total_loss,3.)

    def test_strict_risk_cap_demands_query(self):
        p = Probe("zero",0.,("o",),((1.,),(1.,)))
        m = Model(("a","b"),(.5,.5),("A","B"),
                  ((0.,10.),(10.,0.)),2.,(p,),risk_cap=.1)
        self.assertEqual(one_step_plan(m).decisions[0][1].kind,"query")
        self.assertAlmostEqual(brute_policy_cost(m,p),2.)

    def test_partial_probe_requires_outcome_dependent_query(self):
        p = Probe("partial",.1,("A","unknown"),((.5,.5),(0.,1.)))
        m = Model(("a","b"),(.5,.5),("A","B"),
                  ((0.,10.),(10.,0.)),2.,(p,),risk_cap=.2)
        decisions = dict(one_step_plan(m,p).decisions)
        self.assertEqual(decisions["A"].kind,"action")
        self.assertEqual(decisions["unknown"].kind,"query")
        self.assertAlmostEqual(one_step_plan(m,p).expected_total_loss,1.6)
        self.assertAlmostEqual(one_step_plan(m,p).expected_total_loss,
                               brute_policy_cost(m,p))

    def test_exact_oracle_250_seeded_finite_models(self):
        rng = random.Random(20261010)
        for _ in range(250):
            n, k = rng.randint(2,4),rng.randint(1,3)
            w = [rng.random()+.1 for _ in range(n)]
            prior = tuple(v/sum(w) for v in w)
            rows=[]
            for _h in range(n):
                v = [rng.random()+.1 for _j in range(k)]
                rows.append(tuple(t/sum(v) for t in v))
            probe = Probe("actual",rng.random(),tuple(f"o{i}" for i in range(k)),tuple(rows))
            losses = tuple(tuple(rng.randint(0,9) for _ in range(n)) for _ in range(2))
            m=Model(tuple(f"h{i}" for i in range(n)),prior,("a","b"),losses,
                    rng.random()*4,(probe,),risk_cap=rng.choice([None,0.,.1,.25,.5,1.]),
                    bad_loss_cutoff=3.)
            self.assertAlmostEqual(one_step_plan(m,probe).expected_total_loss,
                                   brute_policy_cost(m,probe),places=10)

    def test_exact_quotient_preserves_value_and_information(self):
        states=tuple(f"s{i}" for i in range(1000))
        p=Probe("observe",.1,("a","b"),tuple((.9,.1) if i%2 else (.2,.8)
                                           for i in range(1000)))
        loss=(tuple(0. if i%2 else 10. for i in range(1000)),
              tuple(10. if i%2 else 0. for i in range(1000)))
        m=Model(states,(.001,)*1000,("a","b"),loss,2.,(p,),risk_cap=.25)
        reduced=quotient_model(m)
        self.assertEqual(len(reduced.states),2)
        for x,y in zip((one_step_plan(m),one_step_plan(m,p)),
                       (one_step_plan(reduced),one_step_plan(reduced,reduced.probes[0]))):
            self.assertAlmostEqual(x.expected_total_loss,y.expected_total_loss)
            self.assertAlmostEqual(x.information_gain_bits,y.information_gain_bits)

    def test_non_normalized_likelihood_fails_closed(self):
        p=Probe("broken",1.,("yes","no"),((.7,.7),(.5,.5)))
        m=Model(("a","b"),(.5,.5),("A",),((0.,0.),),2.,(p,))
        with self.assertRaises(ValueError):
            validate(m)

if __name__=="__main__":
    unittest.main()
