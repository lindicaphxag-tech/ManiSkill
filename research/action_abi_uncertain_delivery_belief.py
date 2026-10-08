"""Finite-state belief certificate for ambiguous action execution in EE target ABI.

A controller's last commanded target may not be uniquely recoverable after
missing or ambiguous action acknowledgement. Conservatively propagate all
possible target poses, never collapse a branch without positive evidence.

This is a CPU-only model-level research guard, not a demonstrated robot-safety
system, physics experiment, hardware fault recovery, or collision checker.
"""
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from scipy.spatial.transform import Rotation

from research.action_abi_history_observer import ActionHistoryObserver, TargetPose


@dataclass(frozen=True)
class BeliefCertificate:
    authorized: bool
    reason: str
    native_action: Optional[Tuple[float, ...]]
    possible_targets: int
    maximum_native_spread: float


class UncertainDeliveryBelief:
    """Two-phase target observer that branches on an unknown command delivery.

    Supported: documented Panda root-frame translation and root-aligned-body
    orientation update, acknowledged normalized 6-D native actions.
    An uncertain delivery preserves BOTH possibilities (applied / not applied);
    do not mistake a good-looking achieved pose for controller target history.

    The number of branches is explicitly capped; exceeding it is an error
    invalidating further execution, NOT pruning away inconvenient hypotheses.
    """

    def __init__(self, pos_lower, pos_upper, rot_lower, *, max_hypotheses=16):
        if not isinstance(max_hypotheses, int) or not 1 <= max_hypotheses <= 65536:
            raise ValueError("Invalid finite belief budget")
        self.mapping = ActionHistoryObserver(pos_lower, pos_upper, rot_lower)
        self.max_hypotheses = max_hypotheses
        self.epoch = 0
        self.sequence = 0
        self.hypotheses: Tuple[TargetPose, ...] = ()
        self.pending = None
        self.valid = False

    def reset(self, initial_target: TargetPose):
        if not isinstance(initial_target, TargetPose):
            raise TypeError("Explicit initial target evidence required")
        self.epoch += 1
        self.sequence = 0
        self.hypotheses = (initial_target,)
        self.pending = None
        self.valid = True

    def _assert_idle(self):
        if not self.valid:
            raise RuntimeError("Belief invalidated: require documented resynchronization")
        if self.pending is not None:
            raise RuntimeError("Pending action must be acknowledged")

    @staticmethod
    def _canonical(pose):
        p = np.asarray(pose.position)
        q = np.asarray(pose.quaternion_xyzw)
        if q[np.argmax(np.abs(q))] < 0:
            q = -q
        return tuple(np.round(np.r_[p, q], 11))

    def _deduplicate(self, poses):
        result = {}
        for pose in poses:
            result[self._canonical(pose)] = pose
        if len(result) > self.max_hypotheses:
            self.valid = False
            self.hypotheses = ()
            raise RuntimeError("Belief branching exceeded budget: fail closed")
        return tuple(result.values())

    def _forward_one(self, old, native_action):
        # Explicit oracle is ONLY our own published deterministic recurrence.
        # It reads no controller field or physics state.
        self.mapping.reset(old)
        ticket = self.mapping.prepare(native_action)
        self.mapping.acknowledge(ticket.ticket, applied=True)
        return self.mapping.pose

    def prepare(self, native_action):
        self._assert_idle()
        a = np.asarray(native_action, dtype=float)
        if a.shape != (6,) or not np.all(np.isfinite(a)):
            raise ValueError("Native action must have finite 6D shape")
        future = tuple(self._forward_one(p, a) for p in self.hypotheses)
        self.sequence += 1
        token = (self.epoch, self.sequence)
        self.pending = (token, tuple(self.hypotheses), future)
        return token

    def acknowledge(self, token, *, applied: Optional[bool]):
        if not self.valid or self.pending is None:
            raise RuntimeError("No pending action")
        expected, previous, future = self.pending
        if token != expected:
            self.valid = False
            self.pending = None
            raise RuntimeError("Stale/out-of-order acknowledgement: fail closed")
        if applied is True:
            candidates = future
        elif applied is False:
            candidates = previous
        elif applied is None:
            candidates = previous + future
        else:
            raise TypeError("applied must be True, False or None")
        self.pending = None
        self.hypotheses = self._deduplicate(candidates)

    def require_external_resync(self, measured_command_target: TargetPose):
        """Only trust explicit true controller-target readback or hard reset.

        Caller must provide provenance: achieved EE pose alone is NOT target
        readback. No automatic inference from incomplete state/observation.
        """
        self.reset(measured_command_target)

    def certify_common_exact_action(self, desired_target: TargetPose, *, tolerance=1e-6):
        """Authorize only if ONE legal native command reaches the same target
        from every target history in this finite exact model.

        No collision, contact, IK, tracking, or physical robot safety guarantee.
        Does not authorize bounded projections as 'exact'.
        """
        self._assert_idle()
        if not isinstance(desired_target, TargetPose):
            raise TypeError("Desired target must be a TargetPose")
        if not (0 < tolerance < 1e-3):
            raise ValueError("Tolerance must be positive and small")
        candidates = []
        low = self.mapping.low
        high = self.mapping.high
        for old in self.hypotheses:
            delta = np.asarray(desired_target.position) - np.asarray(old.position)
            native_pos = 2*(delta-low)/(high-low)-1
            desired_rot = Rotation.from_quat(desired_target.quaternion_xyzw)
            old_rot = Rotation.from_quat(old.quaternion_xyzw)
            xyz = (desired_rot*old_rot.inv()).as_euler("XYZ")
            native_rot = xyz/self.mapping.rot_scale
            if not np.all(np.isfinite(native_pos)) or not np.all(np.isfinite(native_rot)):
                return BeliefCertificate(False, "NONFINITE_INVERSE", None,
                                         len(self.hypotheses), float("inf"))
            if (np.max(np.abs(native_pos)) > 1+tolerance
                    or np.linalg.norm(native_rot)>1+tolerance):
                return BeliefCertificate(False, "UNREPRESENTABLE_FOR_A_HYPOTHESIS",
                                         None, len(self.hypotheses), float("inf"))
            candidates.append(np.r_[native_pos, native_rot])
        anchor = candidates[0]
        spread = max(float(np.max(np.abs(c-anchor))) for c in candidates)
        if spread>tolerance:
            return BeliefCertificate(False, "AMBIGUOUS_PREVIOUS_TARGET",
                                     None, len(self.hypotheses), spread)
        # Valid within representability tolerance; never emit above [-1,1].
        # Rotation *norm* is the legality constraint, not component clipping.
        command = anchor.copy()
        command[:3] = np.clip(command[:3], -1, 1)
        rnorm = float(np.linalg.norm(command[3:]))
        if rnorm>1:
            command[3:]/=rnorm
        return BeliefCertificate(True, "EXACT_WITHIN_DECLARED_NUMERIC_TOLERANCE",
                                 tuple(map(float, command)), len(self.hypotheses),spread)


def positional_diameter(poses):
    """Largest pairwise difference of possible commanded-target positions."""
    if not poses:
        raise ValueError("Belief cannot be empty")
    x = np.asarray([p.position for p in poses], dtype=float)
    return float(max(np.linalg.norm(x[i]-x[j])
                     for i in range(len(x)) for j in range(i+1,len(x)))
                 ) if len(x)>1 else 0.0
