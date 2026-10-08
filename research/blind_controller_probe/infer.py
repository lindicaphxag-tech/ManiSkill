"""Telemetry-assisted reference-frame hypothesis test for one zero-delta probe.

No model fit; *not* a black-box estimator. Requires trustworthy commanded
target telemetry. Fail closed when hypotheses overlap or data are invalid.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Sequence

ACHIEVED = "ACHIEVED_RELATIVE"
TARGET = "PREVIOUS_TARGET_RELATIVE"
ABSTAIN = "ABSTAIN"
REFUSE = "REFUSE"


@dataclass(frozen=True)
class Inference:
    decision: str
    reason: str
    gap_m: float | None
    achieved_error_m: float | None
    target_error_m: float | None


def _vector(x: Sequence[float]) -> tuple[float, float, float]:
    try:
        z = tuple(float(v) for v in x)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid 3D telemetry") from exc
    if len(z) != 3 or not all(isfinite(v) for v in z):
        raise ValueError("invalid 3D telemetry")
    return z


def _distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def infer_zero_delta_reference(
    achieved_before: Sequence[float],
    target_before: Sequence[float],
    commanded_target_after: Sequence[float],
    *,
    error_tolerance_m: float = 0.0001,
    min_identifiable_gap_m: float = 0.001,
    max_preprobe_gap_m: float = 0.04,
) -> Inference:
    """Decide using observations only, never the true mode/config label.

    If the true post-probe telemetry has error <= error_tolerance_m,
    a classification is uniquely supported only if the incompatible
    hypothesis is farther than the error bound. In an uninformative or
    unsafe trial return ABSTAIN/REFUSE rather than force a guess.
    """
    if (
        not all(isfinite(float(x)) for x in
                (error_tolerance_m, min_identifiable_gap_m, max_preprobe_gap_m))
        or error_tolerance_m <= 0
        or min_identifiable_gap_m < 2 * error_tolerance_m
        or max_preprobe_gap_m <= min_identifiable_gap_m
    ):
        raise ValueError("invalid uncertainty or authority boundary")
    achieved = _vector(achieved_before)
    previous = _vector(target_before)
    after = _vector(commanded_target_after)
    gap = _distance(achieved, previous)
    da, dt = _distance(after, achieved), _distance(after, previous)
    if gap > max_preprobe_gap_m:
        return Inference(REFUSE, "pre-probe target tracking gap exceeds local cap",
                         gap, da, dt)
    if gap < min_identifiable_gap_m:
        return Inference(ABSTAIN, "achieved/previous-target hypotheses overlap",
                         gap, da, dt)
    if da <= error_tolerance_m and dt > error_tolerance_m:
        return Inference(ACHIEVED, "post-probe target matches achieved reference",
                         gap, da, dt)
    if dt <= error_tolerance_m and da > error_tolerance_m:
        return Inference(TARGET, "post-probe target retains previous target",
                         gap, da, dt)
    return Inference(ABSTAIN, "both candidate explanations inconsistent or ambiguous",
                     gap, da, dt)
