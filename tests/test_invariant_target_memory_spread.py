"""Two-sided SE3 source-model isometry falsifier."""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from research.invariant_target_memory_spread import (
    pairwise_history_distances, shared_root_action,
    necessary_common_goal_radii,
)

class TestGroupIsometry(unittest.TestCase):
    def test_500_random_common_actions(self):
        rng=np.random.default_rng(20261014)
        for _ in range(100):
            n=int(rng.integers(2,8))
            p=rng.normal(0,.2,(n,3))
            q=Rotation.random(n,random_state=rng).as_quat()
            dp0,dr0=pairwise_history_distances(p,q)
            for _ in range(5):
                p,q=shared_root_action(p,q,rng.uniform(-.08,.08,3),
                                         rng.uniform(-.12,.12,3))
                dp,dr=pairwise_history_distances(p,q)
                np.testing.assert_allclose(dp,dp0,atol=1e-12,rtol=0)
                np.testing.assert_allclose(dr,dr0,atol=1e-12,rtol=0)
    def test_angular_and_translation_lower_bounds(self):
        q=Rotation.from_euler("z",[[0],[.4]]).as_quat()
        p=[[0,0,0],[.01,0,0]]
        tolpos,tolang=necessary_common_goal_radii(p,q)
        self.assertAlmostEqual(tolpos,.005,places=12)
        self.assertAlmostEqual(tolang,.2,places=12)
    def test_untrusted_quaternion_rejected(self):
        with self.assertRaises(ValueError):
            pairwise_history_distances([[0]*3,[1]*3],[[0,0,0,0],[0,0,0,1]])

if __name__=="__main__": unittest.main()
