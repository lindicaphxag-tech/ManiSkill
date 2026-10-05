from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Literal, Sequence


Compatibility = Literal["native_equal", "transport_required", "incompatible"]


def _tuple_or_none(value: Sequence[float] | None) -> tuple[float, ...] | None:
    if value is None:
        return None
    return tuple(float(x) for x in value)


@dataclass(frozen=True)
class ActionBlockContract:
    """Minimal physical-semantic contract for one contiguous action block."""

    name: str
    semantic_space: str
    manifold: str
    reference: str
    frame: str
    units: tuple[str, ...]
    normalized: bool
    physical_lower: tuple[float, ...] | None = None
    physical_upper: tuple[float, ...] | None = None
    required_state: tuple[str, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        name: str,
        semantic_space: str,
        manifold: str,
        reference: str,
        frame: str,
        units: Sequence[str],
        normalized: bool,
        physical_lower: Sequence[float] | None = None,
        physical_upper: Sequence[float] | None = None,
        required_state: Sequence[str] = (),
    ) -> "ActionBlockContract":
        low = _tuple_or_none(physical_lower)
        high = _tuple_or_none(physical_upper)
        units_t = tuple(str(x) for x in units)
        state_t = tuple(str(x) for x in required_state)
        if not name or not semantic_space or not manifold or not reference or not frame:
            raise ValueError("contract string fields must be non-empty")
        if not units_t:
            raise ValueError("units must be non-empty")
        if (low is None) != (high is None):
            raise ValueError("physical_lower and physical_upper must be provided together")
        if low is not None:
            if len(low) != len(high):
                raise ValueError("physical bounds must have equal lengths")
            if len(units_t) not in (1, len(low)):
                raise ValueError("units must have length 1 or match physical bounds")
            if any(lo > hi for lo, hi in zip(low, high, strict=True)):
                raise ValueError("physical lower bound exceeds upper bound")
        return cls(
            name=name,
            semantic_space=semantic_space,
            manifold=manifold,
            reference=reference,
            frame=frame,
            units=units_t,
            normalized=bool(normalized),
            physical_lower=low,
            physical_upper=high,
            required_state=state_t,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "semantic_space": self.semantic_space,
            "manifold": self.manifold,
            "reference": self.reference,
            "frame": self.frame,
            "units": list(self.units),
            "normalized": self.normalized,
            "physical_lower": None if self.physical_lower is None else list(self.physical_lower),
            "physical_upper": None if self.physical_upper is None else list(self.physical_upper),
            "required_state": list(self.required_state),
        }


@dataclass(frozen=True)
class ContractCompatibility:
    status: Compatibility
    reasons: tuple[str, ...]


def compare_action_blocks(
    source: ActionBlockContract,
    target: ActionBlockContract,
) -> ContractCompatibility:
    """Classify whether two blocks are native-equal, transportable, or incompatible.

    v0 intentionally treats differences in semantic space, manifold, frame, or
    units as incompatible unless an explicit cross-space operator is supplied by
    a higher layer. Reference, normalization, bounds, and required-state
    differences preserve the physical semantic space but require transport.
    """
    incompatible = []
    for field in ("semantic_space", "manifold", "frame", "units"):
        if getattr(source, field) != getattr(target, field):
            incompatible.append(
                f"{field}: {getattr(source, field)!r} != {getattr(target, field)!r}"
            )
    if incompatible:
        return ContractCompatibility("incompatible", tuple(incompatible))

    transport = []
    for field in (
        "reference",
        "normalized",
        "physical_lower",
        "physical_upper",
        "required_state",
    ):
        if getattr(source, field) != getattr(target, field):
            transport.append(
                f"{field}: {getattr(source, field)!r} != {getattr(target, field)!r}"
            )
    if transport:
        return ContractCompatibility("transport_required", tuple(transport))
    return ContractCompatibility("native_equal", ())


@dataclass(frozen=True)
class ExecutableActionContract:
    """Resolved action semantics that contribute to executable-policy identity."""

    schema_version: str
    checkpoint_revision: str
    controller_id: str
    blocks: tuple[ActionBlockContract, ...]
    normalization_digest: str
    preprocessor_digest: str
    postprocessor_digest: str
    software: tuple[tuple[str, str], ...] = ()

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "checkpoint_revision": self.checkpoint_revision,
            "controller_id": self.controller_id,
            "blocks": [block.to_dict() for block in self.blocks],
            "normalization_digest": self.normalization_digest,
            "preprocessor_digest": self.preprocessor_digest,
            "postprocessor_digest": self.postprocessor_digest,
            "software": {k: v for k, v in self.software},
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def compare_executable_contracts(
    left: ExecutableActionContract,
    right: ExecutableActionContract,
) -> ContractCompatibility:
    reasons = []
    incompatible = []
    if len(left.blocks) != len(right.blocks):
        return ContractCompatibility(
            "incompatible",
            (f"block count: {len(left.blocks)} != {len(right.blocks)}",),
        )
    for i, (a, b) in enumerate(zip(left.blocks, right.blocks, strict=True)):
        result = compare_action_blocks(a, b)
        if result.status == "incompatible":
            incompatible.extend(f"block[{i}] {x}" for x in result.reasons)
        elif result.status == "transport_required":
            reasons.extend(f"block[{i}] {x}" for x in result.reasons)
    if incompatible:
        return ContractCompatibility("incompatible", tuple(incompatible))

    for field in (
        "controller_id",
        "normalization_digest",
        "preprocessor_digest",
        "postprocessor_digest",
    ):
        if getattr(left, field) != getattr(right, field):
            reasons.append(
                f"{field}: {getattr(left, field)!r} != {getattr(right, field)!r}"
            )

    # Checkpoint revision and software versions change executable identity but do
    # not by themselves prove semantic incompatibility. They still prevent a
    # native-equality claim.
    if left.checkpoint_revision != right.checkpoint_revision:
        reasons.append(
            f"checkpoint_revision: {left.checkpoint_revision!r} != "
            f"{right.checkpoint_revision!r}"
        )
    if left.software != right.software:
        reasons.append("resolved software versions differ")

    if reasons:
        return ContractCompatibility("transport_required", tuple(reasons))
    return ContractCompatibility("native_equal", ())
