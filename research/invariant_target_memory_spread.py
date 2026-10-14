"""SO(3) and translation target-history spread invariance under shared action.

Verified model scope only: p'_h=p_h+delta; R'_h=A(delta_rot) R_h.
The triangle inequality implies no common action can make every history
closer than half the pairwise diameter to a single goal. This is standard
group-invariance geometry, not a new robotics theorem or hardware proof.
"""
import numpy as np
from scipy.spatial.transform import Rotation


def pairwise_history_distances(positions, quaternions_xyzw):
    p=np.asarray(positions,dtype=float)
    q=np.asarray(quaternions_xyzw,dtype=float)
    if (p.ndim!=2 or p.shape[1]!=3 or len(p)<2 or not np.isfinite(p).all()
            or q.shape!=(len(p),4) or not np.isfinite(q).all()):
        raise ValueError("N>=2 finite XYZ and quaternion histories required")
    if np.any(abs(np.linalg.norm(q,axis=1)-1)>1e-5):
        raise ValueError("input quaternions must be unit")
    rot=Rotation.from_quat(q)
    pos_dist,rot_dist=[],[]
    for i in range(len(p)):
        for j in range(i+1,len(p)):
            pos_dist.append(float(np.linalg.norm(p[i]-p[j])))
            rot_dist.append(float((rot[i].inv()*rot[j]).magnitude()))
    return np.asarray(pos_dist),np.asarray(rot_dist)


def shared_root_action(positions, quaternions_xyzw, delta_xyz, delta_euler_xyz):
    p=np.asarray(positions,dtype=float)
    q=np.asarray(quaternions_xyzw,dtype=float)
    d=np.asarray(delta_xyz,dtype=float)
    e=np.asarray(delta_euler_xyz,dtype=float)
    if d.shape!=(3,) or e.shape!=(3,) or not np.isfinite(d).all() or not np.isfinite(e).all():
        raise ValueError("bad common source-model action")
    pairwise_history_distances(p,q)
    A=Rotation.from_euler("XYZ",e)
    return p+d,(A*Rotation.from_quat(q)).as_quat()


def necessary_common_goal_radii(positions,quaternions_xyzw):
    """Half of max history diameter, necessary not sufficient for >2 states."""
    dp,dr=pairwise_history_distances(positions,quaternions_xyzw)
    return float(max(dp)/2),float(max(dr)/2)
