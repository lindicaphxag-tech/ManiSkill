"""Action-history observer for ManiSkill root-aligned, target-relative EE control.

Independent of private controller state getters. Predicts the commanded target
from the reset achieved pose and exactly acknowledged issued *native* actions.
No claim about achieved pose, IK success, contact safety, or undocumented modes.
"""
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(frozen=True)
class TargetPose:
    position: Tuple[float, float, float]
    quaternion_xyzw: Tuple[float, float, float, float]

    @classmethod
    def from_arrays(cls, position, quaternion_xyzw):
        p = np.asarray(position, dtype=np.float64).reshape(3)
        q = np.asarray(quaternion_xyzw, dtype=np.float64).reshape(4)
        if not np.all(np.isfinite(p)) or not np.all(np.isfinite(q)):
            raise ValueError("Nonfinite pose")
        norm = float(np.linalg.norm(q))
        if abs(norm - 1.0) > 1e-4:
            raise ValueError("Invalid quaternion norm")
        return cls(tuple(map(float, p)), tuple(map(float, q / norm)))


@dataclass(frozen=True)
class PendingTarget:
    ticket: Tuple[int, int]
    predicted: TargetPose


class ActionHistoryObserver:
    """Two-phase acknowledged target tracker; unsafe uncertainty fails closed.

    Supported contract only:
      normalize_action=True, use_delta=True, use_target=True,
      frame=root_translation:root_aligned_body_rotation.
    Native 6D action is clipped for rotation norm by ManiSkill, but actions
    *outside* its stated representable set are rejected here instead.

    Call reset once per episode using achieved EE pose immediately after the
    controller reset. For each issued action call prepare -> env.step ->
    acknowledge(ticket, applied=True) only after confirmed application.
    Unknown delivery must acknowledge(applied=None), invalidating observer.
    No read of _target_pose / controller.get_state is required.
    """

    FRAME = "root_translation:root_aligned_body_rotation"

    def __init__(self, pos_lower, pos_upper, rot_lower, *,
                 frame=FRAME, use_delta=True, use_target=True,
                 normalize_action=True):
        if frame != self.FRAME or not (use_delta and use_target and normalize_action):
            raise ValueError("Unsupported controller semantics; refuse state inference")
        self.low = np.broadcast_to(np.asarray(pos_lower, dtype=float), (3,)).copy()
        self.high = np.broadcast_to(np.asarray(pos_upper, dtype=float), (3,)).copy()
        self.rot_scale = np.asarray(rot_lower, dtype=float)
        if self.rot_scale.shape not in ((), (3,)):
            raise ValueError("Unsupported rotational scale shape")
        if not np.all(np.isfinite(self.low)) or not np.all(np.isfinite(self.high)):
            raise ValueError("Nonfinite position bounds")
        if not np.all(self.high > self.low) or not np.all(np.isfinite(self.rot_scale)):
            raise ValueError("Invalid action scales")
        if np.any(np.abs(self.rot_scale) <= 1e-12):
            raise ValueError("Degenerate rotational scale")
        self.epoch = 0
        self.sequence = 0
        self._pose: Optional[TargetPose] = None
        self._pending: Optional[PendingTarget] = None
        self._valid = False

    def reset(self, achieved_pose: TargetPose):
        if not isinstance(achieved_pose, TargetPose):
            raise TypeError("Reset requires an explicit TargetPose")
        self.epoch += 1
        self.sequence = 0
        self._pose = achieved_pose
        self._pending = None
        self._valid = True

    @property
    def pose(self) -> TargetPose:
        if not self._valid or self._pose is None:
            raise RuntimeError("Observer unsynchronized; reset/resync required")
        if self._pending is not None:
            raise RuntimeError("Previous action not acknowledged")
        return self._pose

    def prepare(self, native_action) -> PendingTarget:
        previous = self.pose
        action = np.asarray(native_action, dtype=np.float64)
        if action.shape != (6,) or not np.all(np.isfinite(action)):
            raise ValueError("Expected finite native shape (6,)")
        if np.any(np.abs(action[:3]) > 1.0 + 1e-6):
            raise ValueError("Unrepresentable target translation")
        if np.linalg.norm(action[3:]) > 1.0 + 1e-6:
            raise ValueError("Unrepresentable target rotation")
        # Each normalized position dimension is mapped affinely to its
        # physical per-axis bound; rotation is XYZ Euler in root-aligned frame.
        delta_pos = self.low + (np.clip(action[:3], -1, 1) + 1) * (self.high-self.low) / 2
        delta_rot = np.clip(action[3:], -1, 1) * self.rot_scale
        new_pos = np.asarray(previous.position) + delta_pos
        old_rotation = Rotation.from_quat(previous.quaternion_xyzw)
        new_quat = (Rotation.from_euler("XYZ", delta_rot) * old_rotation).as_quat()
        candidate = TargetPose.from_arrays(new_pos, new_quat)
        self.sequence += 1
        pending = PendingTarget((self.epoch, self.sequence), candidate)
        self._pending = pending
        return pending

    def acknowledge(self, ticket: Tuple[int, int], *, applied: Optional[bool]):
        if not self._valid or self._pending is None:
            raise RuntimeError("No valid in-flight action")
        if ticket != self._pending.ticket:
            self._valid = False
            self._pending = None
            raise RuntimeError("Stale or mismatched action acknowledgement")
        if applied is None:
            self._valid = False
        elif applied is True:
            self._pose = self._pending.predicted
        elif applied is not False:
            raise TypeError("applied must be True, False or None")
        self._pending = None
