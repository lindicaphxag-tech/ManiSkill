from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Literal


class TransportKind(str, Enum):
    EXACT = "exact"
    STATEFUL_EXACT = "stateful_exact"
    APPROXIMATE_REQUIRED = "approximate_required"
    INCOMPATIBLE = "incompatible"


GoalSpace = Literal[
    "joint_position",
    "joint_velocity",
    "cartesian_position",
    "cartesian_pose",
    "torque",
]


@dataclass(frozen=True)
class ControllerSemanticType:
    """Semantic type of a controller-native action interface.

    The type records the physical goal space, update semantics, coordinate
    frame, parameterization, and hidden controller state needed to interpret a
    native action.  Equality of tensor shape is intentionally irrelevant.
    """

    goal_space: GoalSpace
    update_mode: str
    frame: str
    parameterization: str
    hidden_state: FrozenSet[str] = frozenset()
    interpolation: str = "unspecified"
    actuator_semantics: str = "unspecified"

    @property
    def exact_family_key(self) -> tuple[str, str, str]:
        return (
            self.goal_space,
            self.frame,
            self.parameterization,
        )


@dataclass(frozen=True)
class Compatibility:
    kind: TransportKind
    required_source_state: FrozenSet[str]
    required_target_state: FrozenSet[str]
    reason: str


def classify_transport(
    source: ControllerSemanticType,
    target: ControllerSemanticType,
) -> Compatibility:
    """Classify whether a semantic transport may be exact before execution.

    Version 0 is deliberately conservative.  It grants exact transport only
    when source and target share one physical goal space, coordinate frame and
    parameterization.  Different update modes are allowed if the hidden state
    required to interpret each side is available.

    Different goal spaces (for example joint position versus joint velocity)
    are not declared exact merely because dimensions match.
    """
    src_state = frozenset(source.hidden_state)
    dst_state = frozenset(target.hidden_state)

    if source.goal_space != target.goal_space:
        return Compatibility(
            kind=TransportKind.APPROXIMATE_REQUIRED,
            required_source_state=src_state,
            required_target_state=dst_state,
            reason=(
                "source and target encode different physical goal spaces; "
                "a richer dynamics/reachable-set contract is required"
            ),
        )

    if source.frame != target.frame:
        return Compatibility(
            kind=TransportKind.APPROXIMATE_REQUIRED,
            required_source_state=src_state,
            required_target_state=dst_state,
            reason=(
                "coordinate frames differ; an explicit state-dependent frame "
                "transform must be proven before exact transport"
            ),
        )

    if source.parameterization != target.parameterization:
        return Compatibility(
            kind=TransportKind.APPROXIMATE_REQUIRED,
            required_source_state=src_state,
            required_target_state=dst_state,
            reason=(
                "native parameterizations differ; exactness requires a "
                "bijective chart conversion over the represented domain"
            ),
        )

    if source.interpolation != target.interpolation:
        return Compatibility(
            kind=TransportKind.APPROXIMATE_REQUIRED,
            required_source_state=src_state,
            required_target_state=dst_state,
            reason=(
                "controllers expose the same instantaneous goal but different "
                "interpolation semantics; endpoint equality is insufficient "
                "for trace-level equivalence"
            ),
        )

    if source.actuator_semantics != target.actuator_semantics:
        return Compatibility(
            kind=TransportKind.APPROXIMATE_REQUIRED,
            required_source_state=src_state,
            required_target_state=dst_state,
            reason=(
                "actuator semantics differ; exact trace equivalence is not "
                "licensed by goal-space equality alone"
            ),
        )

    stateful = bool(src_state or dst_state)
    return Compatibility(
        kind=(
            TransportKind.STATEFUL_EXACT
            if stateful
            else TransportKind.EXACT
        ),
        required_source_state=src_state,
        required_target_state=dst_state,
        reason=(
            "controllers share one semantic family; hidden state must be "
            "supplied exactly" if stateful
            else "controllers share one stateless semantic family"
        ),
    )


def joint_position_semantic_type(
    *,
    update_mode: Literal["absolute", "delta_current", "delta_target"],
    normalized: bool,
    interpolation: str = "none",
    actuator_semantics: str = "pd_joint_position",
) -> ControllerSemanticType:
    hidden: FrozenSet[str]
    if update_mode == "absolute":
        hidden = frozenset()
    elif update_mode == "delta_current":
        hidden = frozenset({"current_qpos"})
    elif update_mode == "delta_target":
        hidden = frozenset({"target_qpos"})
    else:
        raise ValueError(f"unsupported update mode: {update_mode}")

    # Normalization is a native chart detail, not a different physical
    # parameterization: encode/decode handles it exactly.
    return ControllerSemanticType(
        goal_space="joint_position",
        update_mode=update_mode,
        frame="joint_coordinates",
        parameterization="qpos",
        hidden_state=hidden,
        interpolation=interpolation,
        actuator_semantics=actuator_semantics,
    )
