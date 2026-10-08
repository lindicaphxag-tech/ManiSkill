import numpy as np
from scipy.spatial.transform import Rotation

from target_memory_feasibility import (
    TransportDecision,
    compile_target_memory_action,
)


def _compile(pos, rot=None, **kwargs):
    prior_p=np.array([0.1,-0.2,0.3])
    prior_R=Rotation.from_euler("XYZ",[0.2,0.1,-0.05]).as_matrix()
    desired_R=prior_R if rot is None else rot
    return compile_target_memory_action(
        prior_p,prior_R,np.asarray(pos,dtype=float),desired_R,**kwargs
    )


def test_exact_translation_encodes_identity_delta():
    w=_compile([0.1,-0.2,0.3])
    assert w.decision is TransportDecision.EXACT
    np.testing.assert_allclose(w.native_action, np.zeros(6),atol=1e-11)
    assert w.position_goal_residual_m<1e-11
    assert w.orientation_goal_residual_rad<1e-11


def test_strict_refuses_out_of_bounds_physical_position():
    w=_compile([0.35,-0.2,0.3])
    assert w.decision is TransportDecision.REFUSED
    assert w.native_action is None
    assert w.required_native_amplitude>1


def test_projection_reports_real_position_goal_error():
    w=_compile([0.35,-0.2,0.3],mode="project")
    assert w.decision is TransportDecision.APPROXIMATE
    np.testing.assert_allclose(w.native_action[:3],[1,0,0],atol=1e-11)
    assert abs(w.position_goal_residual_m-0.15)<1e-10
    assert w.orientation_goal_residual_rad<1e-11


def test_left_multiplicative_rotation_matches_controller_contract():
    prior_R=Rotation.from_euler("XYZ",[0.2,0.1,-0.05]).as_matrix()
    true_delta=Rotation.from_euler("XYZ",[0.04,-0.02,0.01]).as_matrix()
    goal=true_delta@prior_R
    w=_compile([0.12,-0.22,0.31],rot=goal)
    assert w.decision is TransportDecision.EXACT
    assert w.position_goal_residual_m<1e-10
    assert w.orientation_goal_residual_rad<1e-10


def test_rotation_ball_projection_and_residual():
    previous=Rotation.from_euler("XYZ",[0.2,0.1,-0.05]).as_matrix()
    goal=Rotation.from_euler("XYZ",[0.16,0.0,0.0]).as_matrix()@previous
    w=_compile([0.1,-0.2,0.3],rot=goal,mode="project")
    assert w.decision is TransportDecision.APPROXIMATE
    assert np.linalg.norm(w.native_action[3:])<=1+1e-12
    assert w.orientation_goal_residual_rad>0.05


def test_refuse_nonorthogonal_goal_rotation():
    bad=np.diag([1,1,1.1])
    w=_compile([0.1,-0.2,0.3],rot=bad)
    assert w.decision is TransportDecision.REFUSED
    assert "orientation" in w.reason


def test_refuse_invalid_limit_and_unknown_mode():
    assert _compile([0.1,-0.2,0.3],pos_lower=0.5,pos_upper=0.2).decision is TransportDecision.REFUSED
    assert _compile([0.1,-0.2,0.3],mode="unsafe").decision is TransportDecision.REFUSED


def test_strict_never_silently_approximates_rotation():
    prior_R=Rotation.from_euler("XYZ",[0.2,0.1,-0.05]).as_matrix()
    goal=Rotation.from_euler("XYZ",[0.19,0,0]).as_matrix()@prior_R
    strict=_compile([0.1,-0.2,0.3],rot=goal,mode="strict")
    approximate=_compile([0.1,-0.2,0.3],rot=goal,mode="project")
    assert strict.decision is TransportDecision.REFUSED
    assert approximate.decision is TransportDecision.APPROXIMATE
