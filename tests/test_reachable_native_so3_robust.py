"""Novel representability counterexample and adversarial credibility guards."""
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import TargetPose
from research.multi_ack_se3_bounded import common_multi_history_command
from research.reachable_native_so3_robust import reachable_common_history_command
from research.two_history_se3_robust import Reason

def pose(deg):
    return TargetPose.from_arrays([0,0,0],
        Rotation.from_euler("z",np.deg2rad(deg)).as_quat())

def kwargs(angles,rotbudget=.17):
    return tuple(pose(t) for t in angles),pose(0),dict(
        pos_lower=[-.1]*3,pos_upper=[.1]*3,rot_lower=.1,
        position_budget_m=.01,rotation_budget_rad=rotbudget,
        hypotheses_complete=True,trusted_provenance=True,
        age_steps=0,max_age_steps=0,
        root_translation_root_left_rotation_verified=True)

def test_constructive_old_reject_new_authorize_two_histories():
    h,g,k=kwargs([12,15])
    old=common_multi_history_command(h,g,**k)
    new=reachable_common_history_command(h,g,**k)
    assert not old.authorized and new.authorized
    assert new.hypotheses==2 and np.linalg.norm(new.normalized_6d[3:])<1
    A=Rotation.from_euler("XYZ",np.asarray(new.normalized_6d[3:])*.1)
    assert max((A*Rotation.from_quat(q.quaternion_xyzw)).magnitude() for q in h)<.17

def test_many_histories_under_same_native_control():
    h,g,k=kwargs([12,13,14,15])
    old=common_multi_history_command(h,g,**k)
    new=reachable_common_history_command(h,g,**k)
    assert not old.authorized and new.authorized and new.hypotheses==4
    A=Rotation.from_euler("XYZ",np.asarray(new.normalized_6d[3:])*.1)
    assert all((A*Rotation.from_quat(q.quaternion_xyzw)).magnitude()<.17 for q in h)

def test_never_loses_old_authorized_command():
    h,g,k=kwargs([-1,1],rotbudget=.1)
    old=common_multi_history_command(h,g,**k)
    new=reachable_common_history_command(h,g,**k)
    assert old.authorized and new.authorized
    assert new.normalized_6d==old.normalized_6d

def test_denies_untrusted_histories():
    h,g,k=kwargs([12,15]);k["trusted_provenance"]=False
    assert reachable_common_history_command(h,g,**k).reason==Reason.REFUSE_STALE_OR_UNTRUSTED

def test_no_unauthorized_position_violation():
    h,g,k=kwargs([12,15]);g=TargetPose.from_arrays([1,0,0],[0,0,0,1])
    assert reachable_common_history_command(h,g,**k).reason==Reason.REFUSE_POSITION_BUDGET

def test_no_false_authority_when_lower_bound_impossible():
    h,g,k=kwargs([-12,12],rotbudget=.02)
    assert not reachable_common_history_command(h,g,**k).authorized

def test_stale_refusal_remains_refusal():
    h,g,k=kwargs([12,15]);k["age_steps"]=2;k["max_age_steps"]=1
    assert reachable_common_history_command(h,g,**k).reason==Reason.REFUSE_STALE_OR_UNTRUSTED
