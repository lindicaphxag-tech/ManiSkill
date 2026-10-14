"""Independent LP-oracle verification of common positional action authority."""
import unittest
import numpy as np
from scipy.optimize import linprog
from research.terminal_common_action_certificate import (
    conditional_common_position_authority as decide,
)


def lp_minimax_axis(x, goal, low, high):
    n=len(x)
    A=np.empty((2*n,2))
    A[:n,0],A[:n,1]=1.,-1.
    A[n:,0],A[n:,1]=-1.,-1.
    b=np.r_[goal-x, x-goal]
    sol=linprog([0,1],A_ub=A,b_ub=b,
                bounds=[(low,high),(0,None)],method="highs")
    if not sol.success:
        raise RuntimeError(sol.message)
    return float(sol.fun)


class TestPositionAuthority(unittest.TestCase):
    def test_250_independent_random_lp_oracles(self):
        r=np.random.default_rng(20261014)
        for _ in range(250):
            x=r.normal(size=(int(r.integers(1,12)),3))*.3
            goal=r.normal(size=3)*.2
            low=r.uniform(-.5,-.05,3)
            high=r.uniform(.05,.5,3)
            d=decide(x,goal,np.ones(3)*100,low,high,
                     external_error_envelope_attested=True)
            self.assertTrue(d.authorized)
            for j in range(3):
                exact=lp_minimax_axis(x[:,j],goal[j],low[j],high[j])
                self.assertAlmostEqual(d.maximum_axis_residual_m[j]-1e-10,
                                       exact,places=8)
    def test_model_safe_with_task_tolerance(self):
        c=decide([[0.,0,0],[.02,-.02,.01]],[.1]*3,[.03]*3,
                 [-.2]*3,[.2]*3,external_error_envelope_attested=True)
        self.assertTrue(c.authorized)
        self.assertEqual(len(c.native_six_position_only),6)
        self.assertFalse(c.physical_safety_certified)
    def test_no_common_solution_if_history_diameter_too_large(self):
        c=decide([[-.1,0,0],[.1,0,0]],[0]*3,[.05]*3,
                 [-1]*3,[1]*3,external_error_envelope_attested=True)
        self.assertEqual(c.reason,"COMMON_DELTA_CANNOT_SHRINK_HISTORY_DIAMETER")
    def test_actuation_limit(self):
        c=decide([[0]*3],[2,0,0],[.1]*3,
                 [-.1]*3,[.1]*3,external_error_envelope_attested=True)
        self.assertEqual(c.reason,"NATIVE_DELTA_RANGE_TOO_NARROW")
    def test_unattested_fails_closed(self):
        c=decide([[0]*3],[0]*3,[1]*3,[-1]*3,[1]*3)
        self.assertFalse(c.authorized)
        self.assertEqual(c.reason,"UNATTESTED_RESPONSE_ERROR_ENVELOPE")
    def test_extra_error_closes_authority(self):
        c=decide([[0]*3],[0]*3,[.01]*3,[-1]*3,[1]*3,
                 external_error_bound_xyz=[.02,0,0],
                 external_error_envelope_attested=True)
        self.assertFalse(c.authorized)
    def test_invalid_shapes(self):
        for v in ([],[[1,2]],[[float('nan'),0,0]]):
            with self.assertRaises(ValueError):
                decide(v,[0]*3,[1]*3,[-1]*3,[1]*3)
    def test_same_action_cannot_remove_history_spread(self):
        x=np.array([[.1,-.3,.4],[-.2,.8,.4]])
        d=np.array([.27,.1,-.22])
        np.testing.assert_allclose(np.ptp(x+d,axis=0),np.ptp(x,axis=0))

if __name__=="__main__": unittest.main()
