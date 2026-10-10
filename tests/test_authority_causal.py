"""Independent contingent-policy enumerator tests; all synthetic."""
import random
import unittest
from dataclasses import replace
from math import inf
from research.authority_causal import (
    Model, Probe, solve, evaluate_tree, brute_best, validate,
    exact_bisimulation_quotient, counterexample,
)

class CausalTests(unittest.TestCase):
    def test_probe_rewrites_hidden_controller_target(self):
        m = counterexample()
        p = solve(m, 1)
        self.assertEqual(p.name, "reset_and_watch")
        self.assertAlmostEqual(p.value, .1)
        self.assertEqual([c.name for _, c in p.branches], ["repair_b", "repair_b"])
        self.assertAlmostEqual(evaluate_tree(m, ("reset_and_watch", ("repair_a","repair_b"))), 5.1)
        self.assertAlmostEqual(brute_best(m, 1), .1)

    def test_old_state_information_can_be_useless_after_intervention(self):
        p = Probe("scramble", .15, ("old_a","old_b"),
                  (((.5,.5),(0.,0.)), ((0.,0.),(.5,.5))))
        m = replace(counterexample(), probes=(p,))
        self.assertEqual(solve(m, 1).name, "QUERY")
        self.assertAlmostEqual(evaluate_tree(m, ("scramble",("repair_a","repair_b"))), 5.15)
        self.assertAlmostEqual(brute_best(m, 1), 2.)

    def test_passive_indistinguishable_states_query(self):
        p = Probe("unhelpful", .2, ("same",),
                  (((1.,0.),),((0.,1.),)))
        m = replace(counterexample(), probes=(p,))
        self.assertEqual(solve(m, 2).name, "QUERY")
        self.assertAlmostEqual(brute_best(m, 2), 2.)

    def test_probe_model_risk_gate_is_local_only(self):
        m = replace(counterexample(), probe_failure_cap=.2, failures=(False, True))
        self.assertEqual(solve(m, 2).name, "QUERY")
        self.assertEqual(evaluate_tree(m, ("reset_and_watch",("QUERY","QUERY"))), inf)

    def test_exact_transition_bisimulation_preserves_value(self):
        p = Probe("measure", .3, ("no","yes"), (
            ((.25,.25,0.),(0.,0.,.5)),
            ((.25,.25,0.),(0.,0.,.5)),
            ((0.,0.,.5),(.25,.25,0.))))
        m = Model(("a1","a2","b"),(.2,.3,.5),("r0","r1"),
                  ((0.,0.,5.),(5.,5.,0.)),1.,(p,))
        q = exact_bisimulation_quotient(m)
        self.assertEqual(len(q.states),2)
        for h in (0,1,2):
            self.assertAlmostEqual(solve(m,h).value,solve(q,h).value)
        self.assertAlmostEqual(brute_best(m,1),brute_best(q,1))

    def test_same_loss_can_hide_different_transition_class(self):
        p = Probe("test",0.,("x","y"),(
            ((1.,0.,0.),(0.,0.,0.)),
            ((0.,0.,0.),(0.,0.,1.)),
            ((0.,0.,1.),(0.,0.,0.))))
        m = Model(("h0","h1","h2"),(.4,.4,.2),("r0","r1"),
                  ((0.,0.,5.),(5.,5.,0.)),1.,(p,))
        self.assertEqual(len(exact_bisimulation_quotient(m).states),3)

    def test_60_seeded_models_horizons_zero_one_two(self):
        rng = random.Random(20261010)
        for _ in range(60):
            kernel=[]
            for s in range(2):
                w=[rng.random()+.01 for i in range(4)]
                z=sum(w)
                kernel.append(tuple(tuple(w[j*2+i]/z for i in range(2)) for j in range(2)))
            p = Probe("active",rng.uniform(0,.4),("x","y"),tuple(kernel))
            m = Model(("a","b"),(.35,.65),("r0","r1"),
                      ((0.,rng.uniform(1,7)),(rng.uniform(1,7),0.)),
                      rng.uniform(.1,3),(p,),
                      risk_cap=rng.choice([None,.1,.5,1.]))
            for horizon in (0,1,2):
                self.assertAlmostEqual(solve(m,horizon).value,brute_best(m,horizon),places=9)

    def test_nonstochastic_joint_kernel_rejected(self):
        m = counterexample()
        bad = replace(m.probes[0],kernel=(((1.,1.),(0.,0.)),((0.,0.),(0.,1.))))
        with self.assertRaises(ValueError): validate(replace(m,probes=(bad,)))

    def test_failure_flag_prevents_incorrect_state_merge(self):
        m = replace(counterexample(),repairs=("one",),losses=((0.,0.),),failures=(False,True))
        self.assertEqual(len(exact_bisimulation_quotient(m).states),2)

if __name__ == "__main__":
    unittest.main()
