from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .contract_signature import (
    contract_signature,
    semantically_lift_jacobian,
    signature_distance,
)


MANISKILL_SOURCE_SHA = "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
MANISKILL_CONVERSION_PATH = "mani_skill/trajectory/utils/actions/conversion.py"


@dataclass(frozen=True)
class JointControllerChart:
    """Source-frozen ManiSkill joint-position action chart."""

    mode: str
    scale: np.ndarray
    anchor: np.ndarray

    def encode_target(self, target_qpos: np.ndarray) -> np.ndarray:
        target = np.asarray(target_qpos, dtype=float)
        if self.mode == "absolute":
            return target
        if self.mode in {"current_delta", "target_delta"}:
            return (target - self.anchor) / self.scale
        raise ValueError(f"unknown mode: {self.mode}")

    def decode_action(self, action: np.ndarray) -> np.ndarray:
        action = np.asarray(action, dtype=float)
        if self.mode == "absolute":
            return action
        if self.mode in {"current_delta", "target_delta"}:
            return self.anchor + self.scale * action
        raise ValueError(f"unknown mode: {self.mode}")

    @property
    def action_to_physical_jacobian(self) -> np.ndarray:
        if self.mode == "absolute":
            return np.eye(self.scale.size)
        if self.mode in {"current_delta", "target_delta"}:
            return np.diag(self.scale)
        raise ValueError(f"unknown mode: {self.mode}")


def finite_difference_action_jacobian(
    chart: JointControllerChart,
    base_target: np.ndarray,
    support_to_target: np.ndarray,
    *,
    eps: float = 1e-6,
) -> np.ndarray:
    """Estimate d(action coordinates)/d(support) through a source-frozen chart."""

    base_target = np.asarray(base_target, dtype=float)
    support_to_target = np.asarray(support_to_target, dtype=float)
    out = np.zeros((base_target.size, support_to_target.shape[1]), dtype=float)

    for j in range(support_to_target.shape[1]):
        delta = eps * support_to_target[:, j]
        plus = chart.encode_target(base_target + delta)
        minus = chart.encode_target(base_target - delta)
        out[:, j] = (plus - minus) / (2 * eps)
    return out


def physical_contract_for_chart(
    chart: JointControllerChart,
    base_target: np.ndarray,
    support_to_target: np.ndarray,
):
    j_action = finite_difference_action_jacobian(
        chart, base_target, support_to_target
    )
    j_phys = semantically_lift_jacobian(
        j_action, chart.action_to_physical_jacobian
    )
    return j_action, j_phys, contract_signature(j_phys)


def source_anchored_contract_agreement(
    charts: list[JointControllerChart],
    base_target: np.ndarray,
    support_to_target: np.ndarray,
    *,
    tolerance: float = 1e-7,
) -> tuple[bool, list[float]]:
    signatures = [
        physical_contract_for_chart(c, base_target, support_to_target)[2]
        for c in charts
    ]
    ref = signatures[0]
    distances = [signature_distance(ref, sig) for sig in signatures[1:]]
    return all(d <= tolerance for d in distances), distances
