import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from target_memory_action_feasibility import (
    ExecutionStatus, compile_target_goal
)


def build(goal_p,goal_euler,old_p=(0.,0.,0.),old_euler=(0.,0.,0.),**kwargs):
    return compile_target_goal(
        goal_p, Rotation.from_euler("XYZ",goal_euler).as_matrix(),
        old_p, Rotation.from_euler("XYZ",old_euler).as_matrix(),
        pos_lower=-.1,pos_upper=.1,rot_lower=-.1,**kwargs
    )


def test_exact_goal_preserves_physical_xyz_and_orientation():
    x=build([.05,-.04,.01],[.01,.02,-.03],old_euler=(.1,.05,-.1))
    assert x.status is ExecutionStatus.EXACT
    assert x.native_action is not None
    assert len(x.native_action)==6
    assert x.position_goal_residual_m<1e-8
    assert x.orientation_goal_residual_rad<1e-8


def test_too_large_rotation_fails_closed_without_native_command():
    x=build([0,0,0],[0,.2,0])
    assert x.status is ExecutionStatus.REFUSED
    assert x.native_action is None
    assert x.required_native_amplitude>1.9
    assert x.orientation_goal_residual_rad>.09


def test_bounded_projection_reports_nonzero_physical_residual():
    x=build([.15,-.2,0],[.2,0,0],allow_approximation=True)
    assert x.status is ExecutionStatus.APPROXIMATE
    assert x.native_action is not None
    assert max(abs(y) for y in x.native_action[:3])<=1
    assert np.linalg.norm(x.native_action[3:])<=1+1e-12
    assert x.position_goal_residual_m>.05
    assert x.orientation_goal_residual_rad>.09


def test_memory_reference_changes_native_action():
    a=build([.02,0,0],[0,0,0],old_p=(0,0,0))
    b=build([.02,0,0],[0,0,0],old_p=(.01,0,0))
    assert a.status is ExecutionStatus.EXACT
    assert b.status is ExecutionStatus.EXACT
    assert not np.allclose(a.native_action,b.native_action)


def test_non_orthogonal_rotation_refuses_invalid_input():
    with pytest.raises(ValueError,match="SO"):
        compile_target_goal([0,0,0],np.ones((3,3)),
                            [0,0,0],np.eye(3),
                            pos_lower=-.1,pos_upper=.1,rot_lower=-.1)


def test_euler_topological_branch_reports_goal_rotation_not_vector_error():
    ori=Rotation.from_euler("XYZ",[0.,0.,np.pi-.01]).as_matrix()
    prev=Rotation.from_euler("XYZ",[0.,0.,-np.pi+.01]).as_matrix()
    out=compile_target_goal([0,0,0],ori,[0,0,0],prev,
                            pos_lower=-.1,pos_upper=.1,rot_lower=-.1)
    assert out.status is ExecutionStatus.EXACT
    assert out.orientation_goal_residual_rad<1e-7
