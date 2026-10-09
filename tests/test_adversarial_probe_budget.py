"""Model-only regression: K-corrupted observation repairs, independent optimum and honest failure when K exceeded."""
import copy
import itertools
import random
import unittest
from research.adversarial_probe_budget import Model,synthesize,verify,follow,proof_example

class BudgetedProbeTest(unittest.TestCase):
    def test_forged_certificate_and_bounded_corruption(self):
        result=proof_example()
        self.assertEqual(result['K1_three_probes_min_cost'],3)
        self.assertEqual(result['forged_one_response_certificate'],'REJECTED')
        self.assertEqual(result['adversarial_ground_truth_sequences_checked'],8)

    def test_external_unmodelled_and_repair_mismatch(self):
        m=Model({'a':'A','h':'H'},{'a':'x','h':'y'},('x','y'),1,5,3,1)
        plan=synthesize(m)
        unknown=follow(m,plan,('bad',))
        self.assertEqual(unknown['decision'],'read')
        self.assertFalse(unknown['minimax_certificate_valid_for_trace'])
        broken=copy.deepcopy(plan)
        broken['root']['branches'].pop('y')
        with self.assertRaisesRegex(ValueError,'missing outcome'):
            verify(m,broken)

    def test_exceeding_corruption_budget_can_invalidate_authorization(self):
        m=Model({'real':'CONTINUE','other':'RESET'},
                {'real':'x','other':'y'},('x','y'),1,5,3,1)
        p=synthesize(m)
        # This deliberately VIOLATES the assumed K=1 support contract:
        # after two forged 'y' observations, real world 'x' may be lost.
        self.assertEqual(follow(m,p,('y','y'))['repair'],'RESET')
        self.assertNotEqual(follow(m,p,('y','y'))['repair'],m.repairs['real'])

    def test_small_random_exhaustive_safety_and_optimality(self):
        rng=random.Random(20261010)
        tested=0
        for _ in range(40):
            n=rng.choice([2,3])
            histories=tuple('abc'[:n]);alphabet=('x','y')
            truth={h:rng.choice(alphabet) for h in histories}
            repair={h:rng.choice(('R','S')) for h in histories}
            cost=rng.choice((2,3,5));depth=rng.choice((0,1,2,3))
            k=rng.choice((0,1))
            m=Model(repair,truth,alphabet,1,cost,depth,k)
            proof=synthesize(m)
            self.assertEqual(verify(m,proof)['worst_cost'],proof['cost'])
            for h in histories:
                for seq in itertools.product(alphabet,repeat=depth):
                    if sum(o!=truth[h] for o in seq)>k:continue
                    for t in range(depth+1):
                        outcome=follow(m,proof,seq[:t])
                        if outcome['decision']!='probe':break
                    if outcome['decision']=='authorize':
                        self.assertEqual(outcome['repair'],repair[h])
                    else:
                        self.assertEqual(outcome['decision'],'read')
                    tested+=1
        self.assertGreater(tested,50)

if __name__=='__main__':unittest.main()
