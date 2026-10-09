"""No-GPU grouped paired reviewer checks, malicious originals must fail closed."""
import unittest
from research.review_low_signal_probe_value import _clopper_zero, _signflip_two_sided, _stratified_bootstrap

class LowSignalReviewerGroupInference(unittest.TestCase):
    def test_error_bound_cannot_be_reported_as_hardware_safety(self):
        self.assertAlmostEqual(_clopper_zero(8),1-.05**(1/8))
        self.assertGreater(_clopper_zero(8),.30)
        self.assertEqual(_clopper_zero(0),1.)

    def test_exact_cluster_signflip_not_96_independent(self):
        self.assertAlmostEqual(_signflip_two_sided([1,1,1,1]),.125)
        self.assertEqual(_signflip_two_sided([0]*16),1.)
        self.assertEqual(_signflip_two_sided([1,-1]),1.)

    def test_stratified_group_bootstrap_no_cross_robot_mix(self):
        d={"panda":[0]*8,"xarm6_robotiq":[1]*8}
        self.assertEqual(_stratified_bootstrap(d,draws=1000),[8,8])

if __name__=="__main__":
    unittest.main()
