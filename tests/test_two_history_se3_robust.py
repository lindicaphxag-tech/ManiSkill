"""CPU falsification of two-target SE(3) common-command certificate.

No real robot, task success, real lost ACK, or external adoption.
"""
import math
import random
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import TargetPose
from research.two_history_se3_robust import (
    Reason,common_two_history_command,
)

def pose(position,axisangle=(0.,0.,0.)):
    return TargetPose.from_arrays(
        np.asarray(position,float),
        Rotation.from_rotvec(axisangle).as_quat()
    )

def choose(a=None,b=None,d=None,**changes):
    cfg=dict(
        histories=(a or pose((0.,0.,0.)),b or pose((.02,0.,0.),(0.,0.,.03))),
        desired=d or pose((0.,0.,.005)),
        pos_lower=-.1,pos_upper=.1,rot_lower=-.1,
        position_budget_m=.0105,rotation_budget_rad=.0155,
        hypotheses_complete=True,trusted_provenance=True,
        age_steps=0,max_age_steps=0,
        root_translation_root_left_rotation_verified=True
    )
    cfg.update(changes)
    return common_two_history_command(**cfg)


def predicted_errors(command,histories,desired):
    native=np.asarray(command.normalized_6d)
    u_pos=-.1+(native[:3]+1)*.1
    deltaR=Rotation.from_euler("XYZ",native[3:]*(-.1))
    targetR=Rotation.from_quat(desired.quaternion_xyzw)
    p_err=[]
    r_err=[]
    for h in histories:
        p_err.append(np.max(np.abs(np.asarray(h.position)+u_pos-np.asarray(desired.position))))
        actual=deltaR*Rotation.from_quat(h.quaternion_xyzw)
        r_err.append((targetR.inv()*actual).magnitude())
    return max(p_err),max(r_err)


class TwoHistorySE3Setpoint(unittest.TestCase):
    def test_four_task_frozen_constants_midpoint_authorized(self):
        a,b=pose((0,0,0)),pose((.02,0,0),(0,0,.03))
        d=pose((0,0,.005))
        out=choose(a,b,d)
        self.assertTrue(out.authorized)
        self.assertAlmostEqual(out.worst_position_inf_m,.01)
        self.assertAlmostEqual(out.worst_orientation_geodesic_rad,.015)
        pe,re=predicted_errors(out,(a,b),d)
        self.assertAlmostEqual(pe,.01,places=9)
        self.assertAlmostEqual(re,.015,places=8)

    def test_outcome_is_not_falsely_exact(self):
        result=choose()
        self.assertGreater(result.worst_position_inf_m,0)
        self.assertGreater(result.worst_orientation_geodesic_rad,0)
        self.assertIn("no collision",result.explanation)

    def test_incomplete_hypotheses_never_dispatch(self):
        out=choose(hypotheses_complete=False)
        self.assertEqual(out.reason,Reason.REFUSE_INCOMPLETE_HYPOTHESES)
        self.assertIsNone(out.normalized_6d)

    def test_missing_trust_or_stale_never_dispatch(self):
        self.assertEqual(choose(trusted_provenance=False).reason,
                         Reason.REFUSE_STALE_OR_UNTRUSTED)
        self.assertEqual(choose(age_steps=1).reason,
                         Reason.REFUSE_STALE_OR_UNTRUSTED)

    def test_wrong_frame_never_dispatch(self):
        self.assertEqual(
            choose(root_translation_root_left_rotation_verified=False).reason,
            Reason.REFUSE_UNVERIFIED_CONTROLLER)

    def test_tight_position_budget_refused(self):
        self.assertEqual(choose(position_budget_m=.009).reason,
                         Reason.REFUSE_POSITION_BUDGET)

    def test_tight_orientation_budget_refused(self):
        self.assertEqual(choose(rotation_budget_rad=.014).reason,
                         Reason.REFUSE_ROTATION_BUDGET)

    def test_exact_boundary_fails_closed(self):
        self.assertEqual(choose(position_budget_m=.01).reason,
                         Reason.REFUSE_POSITION_BUDGET)
        self.assertEqual(choose(rotation_budget_rad=.015).reason,
                         Reason.REFUSE_ROTATION_BUDGET)

    def test_rotation_limit_refuses_no_hidden_clipping(self):
        b=pose((.02,0,0),(0,0,2.4))
        out=choose(b=b,rotation_budget_rad=2.)
        self.assertEqual(out.reason,Reason.REFUSE_UNREPRESENTABLE_ROTATION)
        self.assertIsNone(out.normalized_6d)

    def test_action_bounds_add_saturation_error(self):
        a,b=pose((0,0,0)),pose((.02,0,0),(0,0,.03))
        d=pose((.2,0,.005))
        out=choose(a,b,d,pos_lower=-.01,pos_upper=.01,position_budget_m=.3)
        self.assertTrue(out.authorized)
        self.assertAlmostEqual(out.worst_position_inf_m,.19)
        self.assertGreater(out.position_saturation_excess_m[0],0)

    def test_bad_types_dimensions_and_nonfinite_rejected(self):
        cfgs=(
            {"pos_lower":float("nan")},
            {"rot_lower":0},
            {"pos_upper":-.1},
            {"position_budget_m":-1},
            {"rotation_budget_rad":math.inf},
            {"age_steps":-1},
            {"max_age_steps":True},
            {"numeric_guard":0},
            {"histories":(pose((0,0,0)),)},
        )
        for cfg in cfgs:
            with self.subTest(cfg=cfg),self.assertRaises((ValueError,TypeError)):
                choose(**cfg)

    def test_320_randomized_two_candidate_so3_geodesic_minimax(self):
        rng=random.Random(20261009)
        for j in range(320):
            c=np.array([rng.uniform(-.03,.03) for _ in range(3)])
            psep=np.array([rng.uniform(-.014,.014) for _ in range(3)])
            rvec=np.array([rng.uniform(-.04,.04) for _ in range(3)])
            drift=np.array([rng.uniform(-.01,.01) for _ in range(3)])
            a=pose(c)
            b=pose(c+psep,rvec)
            d=pose(c+drift)
            result=choose(a,b,d,position_budget_m=.1,rotation_budget_rad=.1)
            self.assertTrue(result.authorized,msg=f"seeded sample={j}: {result.reason}")
            pe,re=predicted_errors(result,(a,b),d)
            self.assertAlmostEqual(pe,result.worst_position_inf_m,places=7)
            self.assertAlmostEqual(re,result.worst_orientation_geodesic_rad,places=7)
            self.assertGreaterEqual(result.worst_orientation_geodesic_rad,0)
            self.assertLessEqual(result.worst_orientation_geodesic_rad,.04)

    def test_position_lower_bound_against_feasible_1d_grid(self):
        rng=random.Random(21901)
        for _ in range(100):
            a=rng.uniform(-.03,.03)
            b=a+rng.uniform(-.06,.06)
            target=rng.uniform(-.1,.1)
            low=-.04;high=.04
            r=choose(a=pose((a,0,0)),b=pose((b,0,0),(0,0,.03)),
                     d=pose((target,0,0)),pos_lower=low,pos_upper=high,
                     position_budget_m=.3)
            self.assertTrue(r.authorized)
            for u in np.linspace(low,high,201):
                e=max(abs(a+u-target),abs(b+u-target))
                self.assertGreaterEqual(e+1e-9,r.worst_position_inf_m)


if __name__ == "__main__":
    unittest.main()
