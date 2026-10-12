"""Source-constrained, same-native-action ACK probe proposals.

Never invent history-dependent commanded targets: reconstruct each predicted
target from one identical legal native six-dimensional command and the
existing documented ManiSkill target-relative ActionHistoryObserver.
This adapter does not run PhysX or attest contact/sensor-response envelopes.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

import numpy as np

from research.action_abi_history_observer import ActionHistoryObserver, TargetPose
from research.ack_robust_active_probe import Candidate


@dataclass(frozen=True)
class NativeProbeProposal:
    name: str
    native_action: tuple[float, float, float, float, float, float]
    candidate: Candidate
    maximum_translation_deviation_m: float
    source_kinematics_verified: bool
    physical_safety_certified: bool = False


def propose_from_common_native_action(
    histories: Mapping[str, TargetPose],
    native_action: Sequence[float],
    *,
    name: str,
    pos_lower: Sequence[float] | float,
    pos_upper: Sequence[float] | float,
    rot_lower: Sequence[float] | float,
    declared_action_cost: float,
    independent_controller_mapping_attestation: bool = False,
    external_physical_admissibility_attestation: bool = False,
    equality_tolerance_m: float = 1e-10,
) -> NativeProbeProposal:
    """Generate *all* targets from the SAME legal normalized robot action.

    The mapping is the published root-translation / root-aligned-body-rotation
    recurrence. There is no action-history target getter or private
    acknowledgement input. Attestation flags remain false unless external
    evidence is supplied; deriving an action from source is not physical
    calibration. Declared cost is not motor power or measured robot energy.
    """
    if not isinstance(histories, Mapping) or len(histories) < 2:
        raise ValueError("at least two explicit hidden controller histories required")
    if any(not isinstance(h, str) or not h or not isinstance(p, TargetPose)
           for h, p in histories.items()):
        raise TypeError("nonempty named TargetPose histories required")
    action = np.asarray(native_action, dtype=np.float64)
    if action.shape != (6,) or not np.isfinite(action).all():
        raise ValueError("single finite 6D native action required")
    if np.any(np.abs(action[:3]) > 1) or np.linalg.norm(action[3:]) > 1:
        raise ValueError("native action outside declared normalized controller domain")
    if not isinstance(name, str) or not name:
        raise ValueError("named action required")
    cost, tol = float(declared_action_cost), float(equality_tolerance_m)
    if not isfinite(cost) or cost <= 0 or not isfinite(tol) or tol < 0:
        raise ValueError("invalid action cost or positional tolerance")

    model = ActionHistoryObserver(pos_lower, pos_upper, rot_lower)
    output = {}
    shifts = []
    for h, pose in histories.items():
        # Crucially: instantiate a new observer per hidden state, never
        # mutate an already active true-world controller or read its target.
        model.reset(pose)
        ticket = model.prepare(action)
        model.acknowledge(ticket.ticket, applied=True)
        predicted = model.pose
        previous_xyz = np.asarray(pose.position, dtype=np.float64)
        predicted_xyz = np.asarray(predicted.position, dtype=np.float64)
        if not np.isfinite(predicted_xyz).all():
            raise ValueError("predicted target coordinate overflow")
        output[h] = tuple(map(float, predicted_xyz))
        shifts.append(predicted_xyz - previous_xyz)
    max_deviation = max(float(np.linalg.norm(shift - shifts[0]))
                        for shift in shifts)
    if max_deviation > tol:
        # A root-frame translation that depends on hidden history violates
        # the documented source recurrence; do not silently use a forged
        # non-affine candidate.
        raise ValueError("source recurrence violated common root-frame shift")
    cand = Candidate(
        name=name,
        targets=output,
        cost=cost,
        controller_mapping_attested=independent_controller_mapping_attestation is True,
        physical_admissibility_attested=external_physical_admissibility_attestation is True,
    )
    return NativeProbeProposal(
        name=name,
        native_action=tuple(float(v) for v in action),
        candidate=cand,
        maximum_translation_deviation_m=max_deviation,
        source_kinematics_verified=True,
    )


def verify_candidate_against_native_source(
    claimed: Candidate,
    histories: Mapping[str, TargetPose],
    native_action: Sequence[float],
    *,
    pos_lower: Sequence[float] | float,
    pos_upper: Sequence[float] | float,
    rot_lower: Sequence[float] | float,
    equality_tolerance_m: float = 1e-10,
) -> None:
    """Refuse apparently separable geometric targets not reachable by one action.

    A fake per-history target forecast would otherwise pass the pure geometric
    certificate. This is a provenance check, NOT a robot collision certificate.
    """
    if not isinstance(claimed, Candidate):
        raise TypeError("typed Candidate required")
    generated = propose_from_common_native_action(
        histories, native_action, name=claimed.name,
        pos_lower=pos_lower, pos_upper=pos_upper, rot_lower=rot_lower,
        declared_action_cost=claimed.cost,
        equality_tolerance_m=equality_tolerance_m,
    ).candidate
    if set(generated.targets) != set(claimed.targets):
        raise ValueError("claimed target histories not equal to actual source histories")
    tol = float(equality_tolerance_m)
    for h, value in generated.targets.items():
        claimed_xyz = np.asarray(claimed.targets[h], dtype=np.float64)
        if (claimed_xyz.shape != (3,) or not np.isfinite(claimed_xyz).all()
                or np.linalg.norm(claimed_xyz - np.asarray(value)) > tol):
            raise ValueError("history-dependent target forecast not induced by native action")
