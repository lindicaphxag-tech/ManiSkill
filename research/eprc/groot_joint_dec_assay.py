from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .contract_signature import contract_signature, signature_distance


GROOT_SOURCE_SHA = "51d4c89f72fda44cbf77285c6a8114b52676b8a1"
GROOT_PROCESSOR_PATH = "gr00t/data/state_action/state_action_processor.py"
GROOT_POSE_PATH = "gr00t/data/state_action/pose.py"
GROOT_CHUNK_PATH = "gr00t/data/state_action/action_chunking.py"


@dataclass(frozen=True)
class GrootJointChart:
    mode: str
    reference_state: np.ndarray

    def encode_absolute(self, absolute_action: np.ndarray) -> np.ndarray:
        a = np.asarray(absolute_action, dtype=float)
        if self.mode == "absolute":
            return a
        if self.mode == "relative":
            return a - self.reference_state
        raise ValueError(f"unknown mode: {self.mode}")

    def decode_to_absolute(self, action: np.ndarray) -> np.ndarray:
        a = np.asarray(action, dtype=float)
        if self.mode == "absolute":
            return a
        if self.mode == "relative":
            return self.reference_state + a
        raise ValueError(f"unknown mode: {self.mode}")

    @property
    def action_to_physical_jacobian(self) -> np.ndarray:
        return np.eye(self.reference_state.size)


def finite_difference_chart_jacobian(
    chart: GrootJointChart,
    base_absolute_action: np.ndarray,
    support_to_target: np.ndarray,
    *,
    eps: float = 1e-6,
) -> np.ndarray:
    base = np.asarray(base_absolute_action, dtype=float)
    response = np.asarray(support_to_target, dtype=float)
    out = np.zeros((base.size, response.shape[1]), dtype=float)

    for j in range(response.shape[1]):
        delta = eps * response[:, j]
        plus = chart.encode_absolute(base + delta)
        minus = chart.encode_absolute(base - delta)
        out[:, j] = (plus - minus) / (2 * eps)
    return out


def physical_contract(
    chart: GrootJointChart,
    base_absolute_action: np.ndarray,
    support_to_target: np.ndarray,
):
    j_action = finite_difference_chart_jacobian(
        chart, base_absolute_action, support_to_target
    )
    # For GR00T JointPose relative actions, semantic lifting is addition of a
    # frozen reference state, whose local derivative wrt action is identity.
    j_phys = chart.action_to_physical_jacobian @ j_action
    return j_action, j_phys, contract_signature(j_phys)


def cross_reference_agreement(
    charts: list[GrootJointChart],
    base_absolute_action: np.ndarray,
    support_to_target: np.ndarray,
    *,
    tolerance: float = 1e-8,
) -> tuple[bool, list[float]]:
    signatures = [
        physical_contract(c, base_absolute_action, support_to_target)[2]
        for c in charts
    ]
    ref = signatures[0]
    distances = [signature_distance(ref, sig) for sig in signatures[1:]]
    return all(d <= tolerance for d in distances), distances
