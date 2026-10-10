"""Falsifiable tests: no privileged labels in online inference or cohort leakage."""
import inspect,unittest
from dataclasses import replace
import torch
from research.conditional_residual_energy import (
  ConditionalResidualEnergy,public_features,authorize_from_public)

def kw():
    return dict(task='pull_cube',probe='zero',epsilon_m=.007,
        residuals_m=(.001,.012,.020,.030),
        public_before_xyz_m=(.5,.1,.2),
        public_after_xyz_m=(.502,.098,.205),
        rotation_spread_rad=.05)

class EnergyTests(unittest.TestCase):
    def test_permutation_equivariance_across_four_full_se3_histories(self):
        torch.manual_seed(20261010);m=ConditionalResidualEnergy().eval()
        f=public_features(**kw());perm=torch.tensor((2,0,3,1))
        self.assertTrue(torch.allclose(m(f)[perm],m(f[perm]),atol=1e-5,rtol=1e-5))
    def test_same_hypothesis_index_zero_vs_x_not_automatically_identical_response(self):
        f1=public_features(**kw())
        f2=public_features(**(kw() | {'probe':'x'}))
        self.assertFalse(torch.equal(f1,f2))
    def test_public_input_inference_refuses_privileged_truth_parameter(self):
        self.assertNotIn('truth',inspect.signature(authorize_from_public).parameters)
        with self.assertRaises(TypeError):
            authorize_from_public(ConditionalResidualEnergy(),threshold=.8,truth=3,**kw())
    def test_invalid_public_rejected_without_self_authorization(self):
        m=ConditionalResidualEnergy().eval()
        v=kw();v['residuals_m']=(.001,.003,float('nan'),.3)
        d=authorize_from_public(m,threshold=.8,**v)
        self.assertEqual(d.kind,'QUERY');self.assertIsNone(d.candidate_index)
    def test_bad_provenance_rejected(self):
        m=ConditionalResidualEnergy().eval()
        d=authorize_from_public(m,threshold=.8,**(kw()|{'probe':'unknown'}))
        self.assertEqual(d.kind,'QUERY')
    def test_unreliably_high_threshold_queries_even_for_good_logits(self):
        m=ConditionalResidualEnergy().eval()
        d=authorize_from_public(m,threshold=1.,**kw())
        self.assertEqual(d.kind,'QUERY')
    def test_float_softmax_rounding_to_one_never_bypasses_forced_query(self):
        class Saturated:
            def __call__(self,feature):
                return torch.tensor([5000.,-5000.,-5000.,-5000.])
        d=authorize_from_public(Saturated(),threshold=1.,**kw())
        self.assertEqual(d.kind,'QUERY')
        self.assertIsNone(d.candidate_index)
        self.assertEqual(d.reason,'DISABLED_CALIBRATION_THRESHOLD')
    def test_all_four_hypotheses_are_required(self):
        v=kw();v['residuals_m']=(.001,.004,.006)
        with self.assertRaisesRegex(ValueError,'Four'):public_features(**v)
    def test_nonfinite_scale_rejected(self):
        v=kw();v['epsilon_m']=float('inf')
        with self.assertRaises(ValueError):public_features(**v)

if __name__=='__main__':unittest.main()
