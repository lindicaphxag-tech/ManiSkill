from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .linear_authority import (
    LinearActionAuthority,
    certified_support_radius_linear_authority,
)


class RepairabilityBottleneck(str, Enum):
    CERTIFIED = "CERTIFIED"
    ROBOT_LIMITED = "ROBOT_LIMITED"
    POLICY_LIMITED = "POLICY_LIMITED"
    AUTHORITY_LIMITED = "AUTHORITY_LIMITED"
    MODEL_LIMITED = "MODEL_LIMITED"
    AUTHORITY_AND_MODEL_LIMITED = "AUTHORITY_AND_MODEL_LIMITED"


@dataclass(frozen=True)
class RepairabilityDecomposition:
    bottleneck: RepairabilityBottleneck
    controller_image_residual: float
    policy_image_residual: float
    policy_restriction_gap: float
    minimum_required_support_radius: float
    authority_radius: float
    trust_radius: float
    certified_radius: float
    support_radius_slack: float
    recommended_runtime_response: str


def _image_residual(matrix: np.ndarray, target: np.ndarray) -> float:
    a = np.asarray(matrix, dtype=float)
    d = np.asarray(target, dtype=float)
    projection = a @ np.linalg.pinv(a) @ d
    return float(np.linalg.norm(d - projection))


def decompose_repairability(
    action_support_jacobian: np.ndarray,
    action_to_physical_jacobian: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    nominal_action: np.ndarray,
    authority: LinearActionAuthority,
    trust_radius: float,
    structural_tolerance: float = 1e-8,
) -> RepairabilityDecomposition:
    """Separate structural policy/robot limitations from local radius limitations.

    The controller image Im(C) describes physical directions the controller can
    express locally.  The policy-consistent image Im(CJ) is a subset reachable
    through the frozen policy's intervention-identified response.

    Because Im(CJ) is contained in Im(C),

        dist(d, Im(CJ)) >= dist(d, Im(C)),

    and the difference is a non-negative structural policy-restriction gap.
    """

    j = np.asarray(action_support_jacobian, dtype=float)
    c = np.asarray(action_to_physical_jacobian, dtype=float)
    d = np.asarray(target_physical_correction, dtype=float)
    a0 = np.asarray(nominal_action, dtype=float)

    if j.ndim != 2 or c.ndim != 2 or c.shape[1] != j.shape[0]:
        raise ValueError("semantic lift and action-support Jacobian do not compose")
    if d.ndim != 1 or d.size != c.shape[0]:
        raise ValueError("target physical correction dimension mismatch")

    g = c @ j
    controller_residual = _image_residual(c, d)
    policy_residual = _image_residual(g, d)
    gap = max(0.0, policy_residual - controller_residual)

    radius = certified_support_radius_linear_authority(
        a0, j, authority, trust_radius=trust_radius
    )

    if controller_residual > structural_tolerance:
        return RepairabilityDecomposition(
            bottleneck=RepairabilityBottleneck.ROBOT_LIMITED,
            controller_image_residual=controller_residual,
            policy_image_residual=policy_residual,
            policy_restriction_gap=gap,
            minimum_required_support_radius=float("inf"),
            authority_radius=radius.authority_radius,
            trust_radius=radius.trust_radius,
            certified_radius=radius.certified_radius,
            support_radius_slack=float("-inf"),
            recommended_runtime_response="change controller/embodiment or replan in a different physical command space",
        )

    if policy_residual > structural_tolerance:
        return RepairabilityDecomposition(
            bottleneck=RepairabilityBottleneck.POLICY_LIMITED,
            controller_image_residual=controller_residual,
            policy_image_residual=policy_residual,
            policy_restriction_gap=gap,
            minimum_required_support_radius=float("inf"),
            authority_radius=radius.authority_radius,
            trust_radius=radius.trust_radius,
            certified_radius=radius.certified_radius,
            support_radius_slack=float("-inf"),
            recommended_runtime_response="replan, switch policy, or retrain; do not claim policy-consistent local repair",
        )

    xi = np.linalg.pinv(g) @ d
    required = float(np.linalg.norm(xi))
    slack = float(radius.certified_radius - required)

    if required <= radius.certified_radius + structural_tolerance:
        bottleneck = RepairabilityBottleneck.CERTIFIED
        response = "apply certified policy-consistent repair"
    else:
        authority_tight = radius.authority_radius < required - structural_tolerance
        trust_tight = radius.trust_radius < required - structural_tolerance
        if authority_tight and trust_tight:
            bottleneck = RepairabilityBottleneck.AUTHORITY_AND_MODEL_LIMITED
            response = "replan or reduce perturbation; both controller authority and local model validity are insufficient"
        elif authority_tight:
            bottleneck = RepairabilityBottleneck.AUTHORITY_LIMITED
            response = "change controller mode/authority or replan; local policy response is structurally adequate"
        else:
            bottleneck = RepairabilityBottleneck.MODEL_LIMITED
            response = "re-probe or replan; requested correction lies outside the certified local model region"

    return RepairabilityDecomposition(
        bottleneck=bottleneck,
        controller_image_residual=controller_residual,
        policy_image_residual=policy_residual,
        policy_restriction_gap=gap,
        minimum_required_support_radius=required,
        authority_radius=radius.authority_radius,
        trust_radius=radius.trust_radius,
        certified_radius=radius.certified_radius,
        support_radius_slack=slack,
        recommended_runtime_response=response,
    )
