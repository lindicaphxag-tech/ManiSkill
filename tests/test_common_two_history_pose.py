import numpy as np
import pytest
from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize
from research.common_two_history_pose import common_two_history_pose as f

def case(q,**kw):
    d=dict(target_pos=np.zeros((2,3)),target_quat=q,goal_pos=[0]*3,
      goal_quat=[0,0,0,1],pos_tolerance=[.01]*3,rot_tolerance=.2,
      pos_lower=[-.1]*3,pos_upper=[.1]*3,rotation_scale=[.5]*3,
      external_response_calibrated=True)
    d.update(kw)
    return f(**d)

def test_independent_100_case_so3_midpoint_optimality():
    rng=np.random.default_rng(20261014)
    for _ in range(100):
        axes=rng.normal(size=(2,3));axes/=np.linalg.norm(axes,axis=1)[:,None]
        rotations=R.from_rotvec(axes*rng.uniform(-.14,.14,size=(2,1)))
        half=(rotations[0].inv()*rotations[1]).magnitude()/2
        z=case(rotations.as_quat(),rot_tolerance=half+.0001)
        assert z.authorized
        assert abs(z.worst_orientation_error-half-1e-9)<1e-7
        def loss(v):
            A=R.from_rotvec(v)
            return max((A*r).magnitude() for r in rotations)
        opt=minimize(loss,-.5*(rotations[0].as_rotvec()+rotations[1].as_rotvec()),
                     method="Nelder-Mead")
        assert loss(opt.x)+1e-7>=half

def test_insufficient_task_tolerance():
    q=R.from_euler("z",np.array([-.1,.1]).reshape(-1,1)).as_quat()
    assert case(q,rot_tolerance=.02).reason=="TASK_ENVELOPE_IMPOSSIBLE"

def test_untested_tracking_rejected():
    q=R.from_euler("z",np.array([-.03,.03]).reshape(-1,1)).as_quat()
    assert not case(q,external_response_calibrated=False).authorized

def test_unrepresentable_actuator():
    q=R.from_euler("z",np.array([.3,.35]).reshape(-1,1)).as_quat()
    assert case(q,rotation_scale=[.01]*3).reason=="MIDPOINT_NATIVE_ROTATION_OUT_OF_RANGE"

def test_position_and_uncertainty_fail_closed():
    q=R.from_euler("z",np.array([-.03,.03]).reshape(-1,1)).as_quat()
    assert not case(q,target_pos=[[0,0,0],[.06,0,0]]).authorized
    assert not case(q,rot_tolerance=.04,response_error_rot=.03).authorized

def test_invalid_data_rejected():
    q=R.from_euler("z",np.array([-.03,.03]).reshape(-1,1)).as_quat()
    with pytest.raises(ValueError):case(q*2)
    with pytest.raises(ValueError):case(q,rot_tolerance=-1)
