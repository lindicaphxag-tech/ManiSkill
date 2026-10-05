from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from controller_semantic_transport import (
    JointPositionMode,
    JointPositionSemantics,
    SemanticTransportCertificate,
    transport_joint_position_action,
)


@dataclass(frozen=True)
class FuzzCase:
    current_qpos: np.ndarray
    source_previous_target_qpos: np.ndarray | None
    target_previous_target_qpos: np.ndarray | None
    source_native_action: np.ndarray


@dataclass(frozen=True)
class SemanticViolation:
    case_index: int
    reference: SemanticTransportCertificate
    implementation_action: np.ndarray
    implementation_target: np.ndarray
    target_error: float
    kind: str


@dataclass(frozen=True)
class SemanticFuzzReport:
    total_cases: int
    exact_reference_cases: int
    violations: tuple[SemanticViolation, ...]

    @property
    def violation_rate_on_exact_cases(self) -> float:
        if self.exact_reference_cases == 0:
            return 0.0
        return len(self.violations) / self.exact_reference_cases


ConverterUnderTest = Callable[[FuzzCase], np.ndarray]


def sample_joint_position_cases(
    *,
    source: JointPositionSemantics,
    target: JointPositionSemantics,
    count: int,
    seed: int,
    qpos_low: float = -0.5,
    qpos_high: float = 0.5,
    native_low: float = -0.95,
    native_high: float = 0.95,
) -> tuple[FuzzCase, ...]:
    """Generate deterministic controller states, including hidden target memory."""
    if count <= 0:
        raise ValueError("count must be positive")
    if qpos_high <= qpos_low or native_high <= native_low:
        raise ValueError("sampling bounds must be ordered")
    if source.chart.dimension != target.chart.dimension:
        raise ValueError("source and target dimensions must match")

    rng = np.random.default_rng(seed)
    dim = source.chart.dimension
    out: list[FuzzCase] = []
    for _ in range(count):
        current = rng.uniform(qpos_low, qpos_high, size=dim)
        source_prev = (
            rng.uniform(qpos_low, qpos_high, size=dim)
            if source.mode is JointPositionMode.DELTA_TARGET
            else None
        )
        target_prev = (
            rng.uniform(qpos_low, qpos_high, size=dim)
            if target.mode is JointPositionMode.DELTA_TARGET
            else None
        )
        native = rng.uniform(native_low, native_high, size=dim)
        out.append(
            FuzzCase(
                current_qpos=current,
                source_previous_target_qpos=source_prev,
                target_previous_target_qpos=target_prev,
                source_native_action=native,
            )
        )
    return tuple(out)


def audit_converter(
    *,
    source: JointPositionSemantics,
    target: JointPositionSemantics,
    cases: tuple[FuzzCase, ...] | list[FuzzCase],
    converter: ConverterUnderTest,
    atol: float = 1e-9,
) -> SemanticFuzzReport:
    """Compare a repository converter with the semantic reference transport.

    Cases whose source goal is not representable in the target chart are not
    counted as exact-reference cases. The fuzzer therefore does not punish an
    implementation merely because exact conversion is mathematically
    impossible; those cases belong to a separate refusal/clipping policy test.
    """
    violations: list[SemanticViolation] = []
    exact = 0

    for index, case in enumerate(cases):
        reference = transport_joint_position_action(
            source=source,
            target=target,
            source_native_action=case.source_native_action,
            current_qpos=case.current_qpos,
            source_previous_target_qpos=case.source_previous_target_qpos,
            target_previous_target_qpos=case.target_previous_target_qpos,
            atol=atol,
        )
        if not reference.goal_equivalent:
            continue
        exact += 1

        implementation_action = np.asarray(converter(case), dtype=float)
        if implementation_action.shape != reference.target_native_action.shape:
            raise ValueError("converter returned an action with the wrong shape")
        implementation_target = target.canonical_target(
            implementation_action,
            current_qpos=case.current_qpos,
            previous_target_qpos=case.target_previous_target_qpos,
        )
        error = float(
            np.linalg.norm(
                implementation_target - reference.canonical_source_target
            )
        )
        if not np.all(np.isfinite(implementation_action)):
            kind = "non_finite_action"
        elif error > atol:
            kind = "semantic_target_mismatch"
        else:
            continue

        violations.append(
            SemanticViolation(
                case_index=index,
                reference=reference,
                implementation_action=implementation_action,
                implementation_target=implementation_target,
                target_error=error,
                kind=kind,
            )
        )

    return SemanticFuzzReport(
        total_cases=len(cases),
        exact_reference_cases=exact,
        violations=tuple(violations),
    )
