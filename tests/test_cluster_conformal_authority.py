import unittest,random
from research.cluster_conformal_authority import (
    cluster_calibrate,predict_set,choose_authority,required_resets_for_finite_threshold)
def rows(n,wrong=()):
    return [(i,t, ((.91,.03,.03,.03) if i not in wrong else (.05,.85,.05,.05)), 0)
            for i in range(n) for t in range(4)]
class ConformalTests(unittest.TestCase):
    def test_8_independent_resets_is_underpowered_for_90_percent(self):
        cert=cluster_calibrate(rows(8),task='pull_cube',probe='zero',alpha=.1)
        self.assertFalse(cert.finite_power)
        self.assertEqual(choose_authority((.99,.003,.003,.004),cert),('QUERY',None))
        self.assertEqual(cert.n_independent_resets,8)
    def test_9_independent_resets_has_finite_power_for_90_percent(self):
        cert=cluster_calibrate(rows(9),task='pull_cube',probe='zero',alpha=.1)
        self.assertTrue(cert.finite_power)
        self.assertEqual(choose_authority((.99,.003,.003,.004),cert),('AUTHORIZE',0))
    def test_19_independent_resets_are_required_for_95_percent(self):
        self.assertEqual(required_resets_for_finite_threshold(.05),19)
        self.assertFalse(cluster_calibrate(rows(18),task='pull_cube',probe='x',alpha=.05).finite_power)
        self.assertTrue(cluster_calibrate(rows(19),task='pull_cube',probe='x',alpha=.05).finite_power)
    def test_single_wrong_branch_contaminates_all_four_in_same_reset(self):
        data=rows(19)
        data=[(i,t,((.05,.85,.05,.05) if i==4 and t==3 else prob),label)
              for i,t,prob,label in data]
        cert=cluster_calibrate(data,task='stack_cube',probe='x',alpha=.05)
        self.assertGreater(cert.max_source_nonconformity_threshold,.9)
        self.assertEqual(choose_authority((.80,.10,.06,.04),cert)[0],'QUERY')
    def test_repeated_fault_truth_duplicate_fails(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            cluster_calibrate(rows(9)+rows(1),task='pull_cube',probe='zero',alpha=.1)
    def test_missing_fault_truth_fails(self):
        with self.assertRaisesRegex(ValueError,'Missing'):
            cluster_calibrate(rows(9)[:-1],task='pull_cube',probe='zero',alpha=.1)
    def test_nonfinite_runtime_response_fails_closed(self):
        cert=cluster_calibrate(rows(9),task='pull_cube',probe='x',alpha=.1)
        self.assertEqual(choose_authority((float('nan'),.4,.4,.2),cert),('QUERY',None))
    def test_training_truth_must_never_be_given_to_decision(self):
        cert=cluster_calibrate(rows(9),task='pull_cube',probe='zero',alpha=.1)
        with self.assertRaises(TypeError):
            choose_authority((.9,.03,.03,.04),cert,audit_true_state=0)
    def test_cluster_simulated_empirical_coverage(self):
        # True rank may be unlucky. For independently exchangeable repeated
        # clusters, conformal ranks are uniform up to ties; empirical coverage.
        rng=random.Random(2048);hits=0;rep=2000
        for _ in range(rep):
            ds=[rng.random() for _ in range(20)]
            cert=cluster_calibrate([
                (i,t,(1-ds[i],ds[i]/3,ds[i]/3,ds[i]/3),0)
                for i in range(19) for t in range(4)],
                task='pull_cube',probe='zero',alpha=.1)
            # event: true label is included in the full prediction set
            scores=(1-ds[19],ds[19]/3,ds[19]/3,ds[19]/3)
            hits+=int(0 in predict_set(scores,cert))
        self.assertGreater(hits/rep,.88)
if __name__=='__main__':unittest.main()
