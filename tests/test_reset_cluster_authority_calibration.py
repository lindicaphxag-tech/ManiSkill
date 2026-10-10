"""Adversarial tests: correlated ACK cells must not inflate sample size."""
import unittest
from dataclasses import replace
from research.reset_cluster_authority_calibration import Cell,Cluster,calibrate,decide,cp_upper,cp_lower

def population(n,wrong=(),allowed=(),tasks=('pull','stack')):
    return tuple(Cluster(t,i,tuple(Cell(f'T{j}',float(i in allowed or not allowed),
                         not (t,i,j) in wrong) for j in range(4)))
                 for t in tasks for i in range(n))

class CalibrationTests(unittest.TestCase):
    def test_old_16_reset_zero_error_cannot_certify_ten_percent(self):
        d=calibrate(population(16),tasks=('pull','stack'),grid=(0.,.25,.5,1.))
        self.assertFalse(d.certified)
        self.assertEqual(decide(10.,d),'QUERY')
        self.assertGreater(cp_upper(0,16,.05/(2*2*4)),.3)

    def test_128_reset_errorfree_population_works_under_declared_assumptions(self):
        d=calibrate(population(128),tasks=('pull','stack'),grid=(0.,.25,.5,1.))
        self.assertTrue(d.certified)
        self.assertEqual(decide(1.,d),'AUTHORIZE')
        self.assertEqual(decide(float('nan'),d),'QUERY')
        self.assertEqual(decide(.5,d),'QUERY')
        self.assertLess(max(v.upper_conditional_wrong for v in d.bounds),.1)

    def test_correlated_truths_are_not_four_independent_resets(self):
        d=calibrate(population(16),tasks=('pull','stack'),grid=(1.,),delta=.05)
        self.assertFalse(d.certified)
        self.assertAlmostEqual(cp_upper(0,16,.05),1-.05**(1/16))
        self.assertNotEqual(cp_upper(0,16,.05),cp_upper(0,64,.05))

    def test_one_bad_task_prevents_common_threshold(self):
        d=calibrate(population(128,wrong={('stack',i,0) for i in range(28)}),
                    tasks=('pull','stack'),grid=(1.,))
        self.assertFalse(d.certified)

    def test_all_query_fails_nontrivial_coverage(self):
        d=calibrate(population(128),tasks=('pull','stack'),grid=(2.,))
        self.assertFalse(d.certified)

    def test_repeated_reset_rejected(self):
        c=population(128)
        with self.assertRaisesRegex(ValueError,'repeated'):
            calibrate(c+(c[0],),tasks=('pull','stack'),grid=(0.,))

    def test_missing_truth_rejected(self):
        c=list(population(128));c[1]=replace(c[1],truths=c[1].truths[:-1])
        with self.assertRaisesRegex(ValueError,'truth'):
            calibrate(tuple(c),tasks=('pull','stack'),grid=(0.,))

    def test_audit_label_must_be_boolean(self):
        c=list(population(128));t=list(c[0].truths);t[0]=replace(t[0],correct_afterrun=1)
        c[0]=replace(c[0],truths=tuple(t))
        with self.assertRaisesRegex(ValueError,'truth'):
            calibrate(tuple(c),tasks=('pull','stack'),grid=(0.,))

    def test_too_little_coverage_invalidates_zero_wrong(self):
        d=calibrate(population(128,allowed={0,1,2,3}),tasks=('pull','stack'),
                    grid=(1.,),min_coverage=.2)
        self.assertFalse(d.certified)

    def test_cp_monotonicity_and_duality(self):
        for n in (8,16,32,128,512):
            for k in (0,1,n//4,n//2,n-1,n):
                lo,up=cp_lower(k,n,.05),cp_upper(k,n,.05)
                self.assertTrue(0<=lo<=up<=1)
                self.assertAlmostEqual(lo,1-cp_upper(n-k,n,.05),places=9)

    def test_cp_crosscheck_scipy_if_available(self):
        try: from scipy.stats import beta
        except ImportError: return
        for n in (10,40,200,512):
            for k in (1,n//4,n//2,n-1):
                self.assertAlmostEqual(cp_upper(k,n,.01),float(beta.ppf(.99,k+1,n-k)),places=8)
                self.assertAlmostEqual(cp_lower(k,n,.01),float(beta.ppf(.01,k,n-k+1)),places=8)

    def test_execution_cannot_pass_ground_truth(self):
        d=calibrate(population(128),tasks=('pull','stack'),grid=(1.,))
        with self.assertRaises(TypeError):
            decide(1.,d,truth='held')

if __name__=='__main__':unittest.main()
