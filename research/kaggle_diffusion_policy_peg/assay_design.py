"""Source-frozen, attribution-aware PegInsertionSide policy experiment arms.

The historical paired run compares baseline with both proposed changes
applied. That cannot isolate either upstream PR. Factorial v1 explicitly
contains every (converter, controller) treatment combination and requires
independently replaying the *same original source episode seeds* for all 4.
"""
from __future__ import annotations

from dataclasses import dataclass


BASE = "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERTER = "875ae4d8777678119b2f192ee186c6c15e6894d5"
CONTROLLER = "eed9be164797d41540421bda8adb3840377d7087"


@dataclass(frozen=True)
class AssayArm:
    name: str
    source_commit: str
    controller_overlay_commit: str | None
    converter_changed: bool
    controller_changed: bool

    @property
    def source_tuple(self) -> tuple[str, str, str | None]:
        return self.name, self.source_commit, self.controller_overlay_commit


PAIRED = (
    AssayArm("upstream_baseline", BASE, None, False, False),
    AssayArm("combined_pr1495_pr1472", CONVERTER, CONTROLLER, True, True),
)
FACTORIAL = (
    AssayArm("upstream_baseline", BASE, None, False, False),
    AssayArm("converter_pr1495_only", CONVERTER, None, True, False),
    AssayArm("controller_pr1472_only", BASE, CONTROLLER, False, True),
    AssayArm("combined_pr1495_pr1472", CONVERTER, CONTROLLER, True, True),
)


def assay_arms(mode: str) -> tuple[AssayArm, ...]:
    if mode == "paired":
        return PAIRED
    if mode == "factorial":
        return FACTORIAL
    raise ValueError("invalid assay design; expected paired or factorial")


def verify_factorial_design(arms: tuple[AssayArm, ...]) -> None:
    if len(arms) != 4:
        raise ValueError("causal factorial experiment requires four arms")
    if {arm.name for arm in arms} != {arm.name for arm in FACTORIAL}:
        raise ValueError("missing required named factorial cell")
    observed = set()
    for arm in arms:
        expected_commit = CONVERTER if arm.converter_changed else BASE
        expected_overlay = CONTROLLER if arm.controller_changed else None
        if (
            arm.source_commit != expected_commit
            or arm.controller_overlay_commit != expected_overlay
        ):
            raise ValueError("source commits do not match treatment assignment")
        observed.add((arm.converter_changed, arm.controller_changed))
    if observed != {(False, False), (False, True), (True, False), (True, True)}:
        raise ValueError("factorial experiment lacks full converter/controller crossing")


def four_cell_differences(
    values: dict[str, float],
) -> dict[str, float]:
    """Exploratory additive contrasts, *not* statistically identified effects.

    All four cells must have the same training seed, source episode set,
    evaluation schedule and denominators to interpret these contrasts.
    """
    required = {a.name for a in FACTORIAL}
    if set(values) != required:
        raise ValueError("four source-matched cell values are required")
    base = values["upstream_baseline"]
    conv = values["converter_pr1495_only"]
    ctrl = values["controller_pr1472_only"]
    combined = values["combined_pr1495_pr1472"]
    return {
        "converter_when_controller_legacy": conv - base,
        "converter_when_controller_changed": combined - ctrl,
        "controller_when_converter_legacy": ctrl - base,
        "controller_when_converter_changed": combined - conv,
        "difference_in_differences": combined - conv - ctrl + base,
    }
