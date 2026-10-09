"""Model-only grouped-corruption minimax hostile control tests. No robot claims."""
import copy,random,unittest
from itertools import product
from research.group_fault_probe_minimax import (
    Model,example,synthesize,certify,next_action,posterior,validate,selftest
)

class GroupCorrelatedFaultTest(unittest.TestCase):
    def test_full_adversarial_example_and_strong_single_channel_baseline(self):
        result=selftest()
        self.assertEqual(result["K1_3_distinct_groups_cost"],3)
        self.assertEqual(result["K1_repeated_1_group_cost"],5)
        self.assertEqual(result["exhaustive_physical_world_fault_group_traces"],12)

    def test_missing_response_model_or_action_auth_rejected(self):
        m=example()
        cases=[
            Model(m.repairs,{"a":m.responses["a"]},m.groups,m.alphabets,m.costs,5,3,1,m.preserves_repair),
            Model(m.repairs,m.responses,m.groups,m.alphabets,m.costs,5,3,1,{p:False for p in m.groups}),
            Model(m.repairs,m.responses,m.groups,m.alphabets,m.costs,5,3,-1,m.preserves_repair)
        ]
        for bad in cases:
            with self.assertRaises(ValueError):synthesize(bad)

    def test_self_consistent_unauthorized_or_nonoptimal_read_rejected(self):
        m=example()
        plan=synthesize(m)
        dishonest=copy.deepcopy(plan)
        dishonest["tree"]["branches"]["h"]["belief"]=[["nonsense",0]]
        with self.assertRaises(ValueError):certify(m,dishonest)
        lazy=copy.deepcopy(plan)
        lazy["tree"]={"action":"read","belief":[["applied",0],["held",0]],"value":5}
        lazy["worst_cost"]=5
        with self.assertRaisesRegex(ValueError,"NOT minimax"):certify(m,lazy)

    def test_random_small_latent_games_exhaust_all_one_fault_group_traces(self):
        rng=random.Random(20261010)
        total=0
        for _ in range(60):
            h=('h0','h1','h2')[:rng.choice((2,3))]
            groups=('g0','g1','g2')[:rng.choice((2,3))]
            truth={g:{a:rng.choice(('0','1')) for a in h} for g in groups}
            repair={a:rng.choice(('A','B')) for a in h}
            m=Model(repair,truth,{g:g for g in groups},
                {g:('0','1') for g in groups},{g:1 for g in groups},
                rng.choice((2,3,4,5)),rng.choice((1,2,3)),
                rng.choice((0,1)),{g:True for g in groups})
            tree=synthesize(m)
            self.assertEqual(certify(m,tree)["verified_minimax_cost"],tree["worst_cost"])
            for real in h:
                possible=[()] + ([(x,) for x in groups] if m.faulty_group_budget else [])
                for faulty in possible:
                    def visit(node):
                        nonlocal total
                        if node["action"]=="authorize":
                            self.assertEqual(node["repair"],m.repairs[real])
                            total+=1
                        elif node["action"]=="read":
                            total+=1
                        else:
                            p=node["probe"]
                            for reply in (m.alphabets[p] if p in faulty else (m.responses[p][real],)):
                                if reply in node["branches"]:visit(node["branches"][reply])
                                else:total+=1
                    visit(tree["tree"])
        self.assertGreater(total,200)

    def test_uncalibrated_response_falls_back_to_read(self):
        m=example()
        p=synthesize(m)
        first=p["tree"]["probe"]
        ans=next_action(m,p,((first,"unregistered_sensor_symbol"),))
        self.assertEqual(ans["action"],"read")
        self.assertFalse(ans["certificate_valid"])
if __name__=="__main__":unittest.main()
