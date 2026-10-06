from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class CoordinateSemantic(str, Enum):
    JOINT_POSITION = "joint_position"
    JOINT_DELTA = "joint_delta"
    TASK_TRANSLATION = "task_translation"
    TASK_ROTATION_EULER = "task_rotation_euler"
    TASK_ROTATION_QUATERNION = "task_rotation_quaternion"
    WRENCH = "wrench"
    IMPEDANCE = "impedance"


@dataclass(frozen=True)
class SaturationContract:
    """Chart-local box saturation with explicit coordinate semantics."""

    semantics: tuple[CoordinateSemantic, ...]
    names: tuple[str, ...]
    lower: np.ndarray
    upper: np.ndarray

    def __post_init__(self):
        lower = np.asarray(self.lower, dtype=float)
        upper = np.asarray(self.upper, dtype=float)
        if len(self.semantics) == 0:
            raise ValueError("saturation contract must contain coordinates")
        if len(self.names) != len(self.semantics):
            raise ValueError("coordinate names and semantics must have equal length")
        if lower.shape != (len(self.semantics),) or upper.shape != lower.shape:
            raise ValueError("saturation bounds must match coordinate count")
        if np.any(~np.isfinite(lower)) or np.any(~np.isfinite(upper)):
            raise ValueError("saturation bounds must be finite")
        if np.any(upper <= lower):
            raise ValueError("every saturation upper bound must exceed lower bound")
        if len(set(self.names)) != len(self.names):
            raise ValueError("coordinate names must be unique")

    @property
    def dimension(self) -> int:
        return len(self.semantics)


@dataclass(frozen=True)
class SaturationCompatibilityCertificate:
    compatible: bool
    source_indices: tuple[int, ...]
    target_indices: tuple[int, ...]
    incompatible_names: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class SaturationCommutationWitness:
    commutes: bool
    source_then_transport: np.ndarray
    transport_then_target: np.ndarray
    residual: np.ndarray
    max_abs_residual: float
    reason: str


def compile_named_saturation_mapping(
    source: SaturationContract,
    target: SaturationContract,
    *,
    require_same_semantic: bool = True,
) -> SaturationCompatibilityCertificate:
    """Match named clip coordinates only when their meanings are compatible.

    This prevents a dictionary keyed by joint names / joint indices from being
    silently reused for task-space coordinates merely because dimensions happen
    to match.
    """
    target_by_name = {name: i for i, name in enumerate(target.names)}
    src: list[int] = []
    dst: list[int] = []
    bad: list[str] = []

    for i, name in enumerate(source.names):
        if name not in target_by_name:
            bad.append(name)
            continue
        j = target_by_name[name]
        if require_same_semantic and source.semantics[i] is not target.semantics[j]:
            bad.append(name)
            continue
        src.append(i)
        dst.append(j)

    compatible = not bad and len(src) == source.dimension
    return SaturationCompatibilityCertificate(
        compatible=compatible,
        source_indices=tuple(src),
        target_indices=tuple(dst),
        incompatible_names=tuple(bad),
        reason=(
            "every saturation coordinate has a name- and semantic-preserving target"
            if compatible
            else "saturation coordinates cannot be transferred by index/name alone"
        ),
    )


def apply_box_saturation(action: np.ndarray, contract: SaturationContract) -> np.ndarray:
    action = np.asarray(action, dtype=float)
    if action.shape != (contract.dimension,):
        raise ValueError("action dimension does not match saturation contract")
    return np.clip(
        action,
        np.asarray(contract.lower, dtype=float),
        np.asarray(contract.upper, dtype=float),
    )


def check_linear_saturation_commutation(
    *,
    source_action: np.ndarray,
    transport: np.ndarray,
    source_contract: SaturationContract,
    target_contract: SaturationContract,
    atol: float = 1e-10,
) -> SaturationCommutationWitness:
    """Witness whether a linear semantic transport commutes with saturation.

    The test is intentionally value-specific. Even if two charts share a local
    linear map, clipping changes semantics once one route crosses a chart-local
    representable boundary.
    """
    u = np.asarray(source_action, dtype=float)
    matrix = np.asarray(transport, dtype=float)
    if u.shape != (source_contract.dimension,):
        raise ValueError("source action dimension mismatch")
    if matrix.shape != (target_contract.dimension, source_contract.dimension):
        raise ValueError("transport shape must be [target_dim, source_dim]")

    source_then_transport = matrix @ apply_box_saturation(u, source_contract)
    transport_then_target = apply_box_saturation(matrix @ u, target_contract)
    residual = source_then_transport - transport_then_target
    max_abs = float(np.max(np.abs(residual)))
    commutes = bool(max_abs <= atol)
    return SaturationCommutationWitness(
        commutes=commutes,
        source_then_transport=source_then_transport,
        transport_then_target=transport_then_target,
        residual=residual,
        max_abs_residual=max_abs,
        reason=(
            "saturation commutes with this transport at the tested action"
            if commutes
            else "chart-local saturation changes the transported physical command"
        ),
    )
