"""Two-history conditional full-pose recovery without execution ACK.

Source controller uses p' = p + d, R' = A(u) R. A two-history SO(3)
midpoint minimizes maximum angular distance for unrestricted rotations.
The solution is evaluated under the actual normalized six-action bounds.
This checks SOURCE COMMANDED TARGETS ONLY, not actual pose tracking,
obstacle/contact safety, hardware, goal-task success or novel math priority.
"""
from dataclasses import dataclass
import warnings
import numpy as np
from scipy.spatial.transform import Rotation

@dataclass(frozen=True)
class Result:
    authorized: bool
    reason: str
    native_six: tuple | None
    worst_axis_position_error: tuple
    worst_orientation_error: float
    half_history_angle_lower_bound: float

def _a(x,shape):
    y=np.asarray(x,dtype=float)
    if y.shape!=shape or not np.isfinite(y).all():
        raise ValueError("nonfinite or invalid shape")
    return y

def common_two_history_pose(target_pos,target_quat,goal_pos,goal_quat,
        pos_tolerance,rot_tolerance,pos_lower,pos_upper,rotation_scale,
        *,response_error_xyz=(0,0,0),response_error_rot=0.,
        external_response_calibrated=False,guard=1e-9):
    x=_a(target_pos,(2,3)); q=_a(target_quat,(2,4))
    g=_a(goal_pos,(3,)); gq=_a(goal_quat,(4,))
    tol=_a(pos_tolerance,(3,)); e=_a(response_error_xyz,(3,))
    lo=_a(pos_lower,(3,));hi=_a(pos_upper,(3,))
    s=np.asarray(rotation_scale,dtype=float)
    if s.shape==():s=np.repeat(s,3)
    s=_a(s,(3,))
    if np.any(abs(np.linalg.norm(q,axis=1)-1)>1e-5) or abs(np.linalg.norm(gq)-1)>1e-5:
        raise ValueError("nonunit quaternion")
    if (np.any(tol<0) or np.any(e<0) or np.any(hi<=lo)
        or np.any(abs(s)<1e-12) or not np.isfinite([rot_tolerance,response_error_rot,guard]).all()
        or rot_tolerance<0 or response_error_rot<0 or guard<=0):
        raise ValueError("invalid limits")
    desired=g-(x.min(axis=0)/2+x.max(axis=0)/2)
    d=np.clip(desired,lo,hi)
    maxpos=np.max(abs(x+d-g),axis=0)+e+guard
    native_pos=2*(d-lo)/(hi-lo)-1
    r=Rotation.from_quat(q);goal=Rotation.from_quat(gq)
    angle=float((r[0].inv()*r[1]).magnitude());half=angle/2
    def reject(why,rotation_error=float("inf")):
        return Result(False,why,None,tuple(map(float,maxpos)),rotation_error,half)
    if external_response_calibrated is not True:
        return reject("CALIBRATION_UNATTESTED")
    if np.any(maxpos>tol) or half+response_error_rot+guard>rot_tolerance:
        return reject("TASK_ENVELOPE_IMPOSSIBLE")
    mid=r[0]*(r[0].inv()*r[1])**0.5
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        u=(goal*mid.inv()).as_euler("XYZ")/s
    # The principal Euler branch is a sufficient candidate; rejecting does
    # NOT prove no alternative chart action could satisfy a looser tolerance.
    if not np.isfinite(u).all() or np.linalg.norm(u)>1+1e-10:
        return reject("MIDPOINT_NATIVE_ROTATION_OUT_OF_RANGE")
    A=Rotation.from_euler("XYZ",u*s)
    maxangle=max(float((goal.inv()*(A*ri)).magnitude()) for ri in r)
    maxangle+=response_error_rot+guard
    if maxangle>rot_tolerance:return reject("ROTATION_ENVELOPE_FAILED",maxangle)
    return Result(True,"SOURCE_TARGET_MODEL_ONLY",tuple(map(float,native_pos))+tuple(map(float,u)),
                  tuple(map(float,maxpos)),maxangle,half)
