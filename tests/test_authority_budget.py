"""Unbiased exhaustive policy-tree checks; no native simulator is invoked."""
import random
import unittest
from dataclasses import replace
from math import isclose
from research.authority_budget import (BudgetModel, Probe, validate, frontier, choose,
    exhaustive_choice, evaluate_unpruned, all_trees, counterexample)

class BudgetTests(unittest.TestCase):
    def test_whole_episode_risk_vetoes_sequential_probe(self):
        m=counterexample()
        loose=choose(m,2,.2)
        strict=choose(m,2,.1)
        self.assertEqual(loose.name,'probe')
        self.assertAlmostEqual(loose.cost,1.1136)
        self.assertAlmostEqual(loose.risk,.1536)
        self.assertEqual(strict.name,'QUERY')
        self.assertAlmostEqual(strict.cost,4.)
        self.assertLess(.08,.1)  # a local per-probe gate would permit both
        self.assertGreater(1-(1-.08)**2,.1)

    def test_no_unaccounted_initial_failure(self):
        m=counterexample()
        with self.assertRaisesRegex(ValueError,'Initial'):
            validate(replace(m,initial=(0.,0.,0.,0.,1.)))

    def test_must_absorb_failure(self):
        m=counterexample()
        p=m.probes[0]
        k=list(p.kernel)
        k[4]=((1.,0.,0.,0.,0.), (0.,)*5, (0.,)*5)
        with self.assertRaisesRegex(ValueError,'absorbing'):
            validate(replace(m,probes=(replace(p,kernel=tuple(k)),)))

    def test_without_safe_repair_or_query_fail_closed(self):
        m=BudgetModel(('x','y'),(.5,.5),('r',),((4.,4.),),1.,(),(False,False),1.,bad_loss_cutoff=0.)
        self.assertIsNone(choose(m,0,0.))
        self.assertEqual(choose(m,0,1.).name,'r')

    def test_equal_risk_pareto_uses_lower_cost(self):
        m=BudgetModel(('x',),(1.,),('r0','r1'),((1.,),(2.,)),5.,(),(False,),1.,bad_loss_cutoff=0.)
        f=frontier(m,0)
        self.assertEqual(len(f),1)
        self.assertEqual(f[0].name,'r0')

    def test_incorrect_cheap_failure_incentive_is_visible(self):
        m=counterexample()
        p=replace(m,failure_cost=0.)
        self.assertLessEqual(choose(p,2,1.).cost,choose(m,2,1.).cost)
        self.assertEqual(choose(p,2,.1).name,'QUERY')

    def test_full_policy_tree_optimality_50_seeded_models(self):
        rng=random.Random(20261010)
        for trial in range(50):
            n=3
            prior=(rng.random()+.1,rng.random()+.1,0.)
            prior=tuple(x/sum(prior) for x in prior)
            kernel=[]
            for _ in range(n-1):
                z=[rng.random()+.1 for _ in range(2*n)]
                kernel.append(tuple(tuple(z[j*n+i]/sum(z) for i in range(n))
                                    for j in range(2)))
            kernel.append(((0.,0.,1.),(0.,0.,0.)))
            p=Probe('p',rng.random(),('o0','o1'),tuple(kernel))
            m=BudgetModel(('a','b','F'),prior,('ra','rb'),
                          ((0.,10.,0.),(10.,0.,0.)),rng.uniform(.1,3.),
                          (p,),(False,False,True),rng.uniform(.2,6.))
            for horizon in range(3):
                f=frontier(m,horizon)
                self.assertTrue(all(not ((a.cost <= b.cost - 1e-9 and a.risk <= b.risk + 1e-9) or
                                         (a.risk <= b.risk - 1e-9 and a.cost <= b.cost + 1e-9))
                                    for a in f for b in f if a!=b))
                for budget in (0.,.1,.2,.5,1.):
                    chosen=choose(m,horizon,budget)
                    exhaustive=exhaustive_choice(m,horizon,budget)
                    if chosen is None:
                        self.assertIsNone(exhaustive)
                    else:
                        self.assertIsNotNone(exhaustive)
                        self.assertAlmostEqual(chosen.cost,exhaustive,places=8,msg=(trial,horizon,budget))
                        self.assertLessEqual(chosen.risk,budget+1e-9)

    def test_outcome_specific_risk_allocation(self):
        # Rare conditional error 0.2 is permitted under a 0.05 WHOLE-EPISODE
        # budget because the branch occurs with probability 0.2.
        p=Probe('measure',.05,('common','rare'),(
            ((.74/.9,0.),(.16/.9,0.)),
            ((0.,.06/.1),(0.,.04/.1)),
        ))
        m=BudgetModel(('a','b'),(.9,.1),('safe','risky'),
                      ((2.,2.),(0.,5.)),3.,(p,),
                      (False,False),1.,bad_loss_cutoff=2.)
        chosen=choose(m,1,.05)
        self.assertEqual(chosen.name,'measure')
        self.assertAlmostEqual(chosen.cost,1.85)
        self.assertAlmostEqual(chosen.risk,.04)
        rare=dict(chosen.children)['rare']
        self.assertEqual(rare.name,'risky')
        self.assertAlmostEqual(rare.risk,.2)
        self.assertAlmostEqual(exhaustive_choice(m,1,.05),chosen.cost)

if __name__=='__main__':unittest.main()
