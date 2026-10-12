"""Pre-outcome, bounded-noise active probe choice for hidden ACK histories.

Conditional guarantee only: each history's response belongs to the segment
x + alpha * (target_h - x), alpha in [lo, hi], inflated by radius eps.
If all pairwise segments are farther than 2*eps, the observation sets cannot
intersect and a *later* measurement can identify a surviving history. This
module NEVER claims safe robot motion, controller calibration, or accuracy of
an unexecuted physics experiment.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

import numpy as np


def _vec3(v: Sequence[float]) -> np.ndarray:
    a = np.asarray(v, dtype=np.float64)
    if a.shape != (3,) or not np.isfinite(a).all():
        raise ValueError("expected finite XYZ vector")
    return a


def segment_distance(a0, a1, b0, b1) -> float:
    """Minimum Euclidean distance between two closed 3D segments.

    The interior stationarity solution is evaluated using cross products,
    NOT det=(u.u)*(v.v)-(u.v)**2. The latter catastrophically cancels
    for nearly parallel *crossing* segments, and may falsely report a
    positive separation. The four boundary projections cover parallel,
    degenerate and clipped interior solutions. If the floating point
    geometry cannot be resolved, raise instead of certifying separation.
    """
    p, q, r, s = (_vec3(v) for v in (a0, a1, b0, b1))
    u, v, w = q - p, s - r, p - r
    if not all(np.isfinite(z).all() for z in (u, v, w)):
        raise ValueError("segment coordinate differences overflowed")
    uu, vv, uv = float(u @ u), float(v @ v), float(u @ v)
    uw, vw = float(u @ w), float(v @ w)
    if not all(isfinite(z) for z in (uu, vv, uv, uw, vw)):
        raise ValueError("segment geometry overflowed")

    candidates: list[tuple[float, float]] = []
    for t in (0.0, 1.0):
        candidates.append((
            float(np.clip((t * uv - uw) / uu, 0, 1)) if uu else 0.0, t
        ))
    for t in (0.0, 1.0):
        candidates.append((
            t, float(np.clip((vw + t * uv) / vv, 0, 1)) if vv else 0.0
        ))

    # c=u x v stays informative at tiny angles even when the subtraction
    # uu*vv-uv**2 rounds to zero. For skew lines this finds their closest
    # interior pair; for coplanar crossing segments it recovers distance 0.
    c = np.cross(u, v)
    if not np.isfinite(c).all():
        raise ValueError("segment cross product overflowed")
    if np.any(c != 0):
        denom = float(c @ c)
        if denom == 0 or not isfinite(denom):
            raise ValueError("near-parallel interior geometry unresolved")
        delta = r - p
        a = float(np.cross(delta, v) @ c) / denom
        b = float(np.cross(delta, u) @ c) / denom
        if not isfinite(a) or not isfinite(b):
            raise ValueError("segment interior projection overflowed")
        if 0 <= a <= 1 and 0 <= b <= 1:
            candidates.append((a, b))
    # For exactly parallel or point-like float64 segments, a true minimum
    # occurs on at least one boundary, already checked above.
    distances = [float(np.linalg.norm(w + a * u - b * v))
                 for a, b in candidates]
    if not all(isfinite(distance) for distance in distances):
        raise ValueError("segment distance cannot be resolved safely")
    return min(distances)


@dataclass(frozen=True)
class Candidate:
    name: str
    # Targets are predictions from the *same* prospectively declared native
    # action under each plausible controller-memory history.
    targets: Mapping[str, Sequence[float]]
    cost: float
    controller_mapping_attested: bool
    physical_admissibility_attested: bool


@dataclass(frozen=True)
class Choice:
    candidate: str | None
    reason: str
    certified_gap_m: float
    worst_pair: tuple[str, str] | None
    score: float
    evaluated: int
    # Even a positive score is a conditional geometric certificate only.
    physical_safety_certified: bool = False


def choose_probe(
    before_xyz: Sequence[float],
    histories: Sequence[str],
    candidates: Sequence[Candidate],
    *,
    alpha_min: float,
    alpha_max: float,
    model_and_sensor_error_m: float,
    numerical_guard_m: float = 1e-9,
    maximum_cost: float,
    response_envelope_independently_attested: bool,
) -> Choice:
    """Maximize positive, pairwise guaranteed observation separation / cost.

    Does NOT examine any true ACK history or post-probe observation. A
    hypothesis is distinguishable only if every pair of noise-expanded
    possible-response segments is disjoint. Unsound/uncalibrated choices
    fail closed, regardless of apparent nominal response separation.
    """
    x = _vec3(before_xyz)
    names = tuple(histories)
    lo, hi = float(alpha_min), float(alpha_max)
    eps, guard, budget = (float(model_and_sensor_error_m),
                          float(numerical_guard_m), float(maximum_cost))
    if len(names) < 2 or len(set(names)) != len(names):
        raise ValueError("at least two distinct histories required")
    if not all(isfinite(z) for z in (lo, hi, eps, guard, budget)):
        raise ValueError("nonfinite response envelope or budget")
    if not (0 <= lo <= hi <= 1 and eps >= 0 and guard >= 0 and budget > 0):
        raise ValueError("invalid response envelope or budget")
    if response_envelope_independently_attested is not True:
        return Choice(None, "unattested response envelope", 0.0, None, 0.0, 0)

    best: Choice | None = None
    evaluated = 0
    for cand in candidates:
        if not isinstance(cand, Candidate):
            raise TypeError("all proposals must be typed candidates")
        if not (cand.controller_mapping_attested is True and
                cand.physical_admissibility_attested is True):
            continue
        if not isfinite(cand.cost) or cand.cost <= 0 or cand.cost > budget:
            continue
        if set(cand.targets) != set(names):
            continue
        targets = {name: _vec3(cand.targets[name]) for name in names}
        segments = {
            h: (x + lo * (targets[h] - x), x + hi * (targets[h] - x))
            for h in names
        }
        min_distance = float("inf")
        critical = None
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                d = segment_distance(*segments[a], *segments[b])
                if d < min_distance:
                    min_distance, critical = d, (a, b)
        evaluated += 1
        gap = min_distance - 2 * (eps + guard)
        if gap <= 0:
            continue
        score = gap / cand.cost
        result = Choice(cand.name, "conditional pairwise response tubes disjoint",
                        gap, critical, score, evaluated)
        if best is None or (score, gap, cand.name) > (best.score, best.certified_gap_m,
                                                     best.candidate or ""):
            best = result
    if best is None:
        return Choice(None, "no admissible probe separates every history", 0.0,
                      None, 0.0, evaluated)
    return Choice(best.candidate, best.reason, best.certified_gap_m,
                  best.worst_pair, best.score, evaluated)


@dataclass(frozen=True)
class Inference:
    """Post-execution conditional set-membership decision, not task safety."""
    status: str
    compatible_histories: tuple[str, ...]
    residuals_m: Mapping[str, float]
    physical_safety_certified: bool = False


def infer_after_probe(
    before_xyz: Sequence[float],
    after_xyz: Sequence[float],
    histories: Sequence[str],
    executed_candidate: Candidate,
    *,
    alpha_min: float,
    alpha_max: float,
    model_and_sensor_error_m: float,
    numerical_guard_m: float = 1e-9,
    response_envelope_independently_attested: bool,
    actual_probe_dispatch_confirmed: bool,
    fresh_public_observation_confirmed: bool,
) -> Inference:
    """Eliminate only ACK hypotheses incompatible with observed XYZ.

    A zero-survivor result FALSIFIES the asserted response envelope: it is
    not evidence that some unmodeled history can safely be chosen. All flags
    require independently authenticated evidence outside this pure module.
    """
    x, y = _vec3(before_xyz), _vec3(after_xyz)
    names = tuple(histories)
    lo, hi = float(alpha_min), float(alpha_max)
    eps, guard = float(model_and_sensor_error_m), float(numerical_guard_m)
    if len(names) < 2 or len(set(names)) != len(names):
        raise ValueError("at least two unique hypotheses required")
    if not all(isfinite(z) for z in (lo, hi, eps, guard)) or not (
        0 <= lo <= hi <= 1 and eps >= 0 and guard >= 0
    ):
        raise ValueError("invalid declared response envelope")
    if not isinstance(executed_candidate, Candidate) or (
        set(executed_candidate.targets) != set(names)
    ):
        raise ValueError("candidate histories mismatch")
    if not all(flag is True for flag in (
        response_envelope_independently_attested,
        executed_candidate.controller_mapping_attested,
        executed_candidate.physical_admissibility_attested,
        actual_probe_dispatch_confirmed,
        fresh_public_observation_confirmed,
    )):
        return Inference("UNATTESTED", names, {})
    residuals = {}
    surviving = []
    for h in names:
        target = _vec3(executed_candidate.targets[h])
        s0, s1 = x + lo * (target - x), x + hi * (target - x)
        residual = segment_distance(y, y, s0, s1)
        residuals[h] = residual
        if residual <= eps + guard:
            surviving.append(h)
    status = "UNIQUE" if len(surviving) == 1 else (
        "AMBIGUOUS" if surviving else "MODEL_FALSIFIED"
    )
    return Inference(status, tuple(surviving), residuals)


@dataclass(frozen=True)
class FixedGainNullAudit:
    """Conditional invariance witness, NOT a general physical no-gain theorem."""
    status: str
    center_gap_zero_m: float | None
    center_gap_probe_m: float | None
    cost_zero: float
    cost_probe: float
    probe_has_incremental_information: bool | None


def audit_fixed_gain_common_probe_null(
    zero_probe: Candidate,
    proposed_probe: Candidate,
    histories: Sequence[str],
    *,
    response_gain: float,
    common_gain_independently_attested: bool,
    action_invariant_noise_independently_attested: bool,
    common_shift_tolerance_m: float = 1e-9,
) -> FixedGainNullAudit:
    """Expose the rigorous fixed-gain affine NO-INFORMATION null.

    Assume y_h(a) = x + alpha * (m_h(0) + u(a) - x) + e_h,
    with the SAME known alpha for every history/candidate and the SAME
    translation u(a) for all histories, and probe-independent noise support.
    Then every pairwise center difference is alpha*(m_i(0)-m_j(0)),
    independent of the common action, so probing cannot improve pairwise
    response-ball separation. Neither action admissibility nor physical
    state calibration follows from this arithmetic check.
    """
    names = tuple(histories)
    if len(names) < 2 or len(set(names)) != len(names):
        raise ValueError("need distinct hidden histories")
    gain, tol = float(response_gain), float(common_shift_tolerance_m)
    if not (isfinite(gain) and 0 < gain <= 1 and isfinite(tol) and tol >= 0):
        raise ValueError("invalid gain or numerical tolerance")
    if not isinstance(zero_probe, Candidate) or not isinstance(
        proposed_probe, Candidate
    ):
        raise TypeError("two typed probes required")
    if set(zero_probe.targets) != set(names) or set(proposed_probe.targets) != set(names):
        raise ValueError("history sets must agree")
    if not (isfinite(zero_probe.cost) and zero_probe.cost > 0
            and isfinite(proposed_probe.cost) and proposed_probe.cost > 0):
        raise ValueError("both probe costs must be positive and finite")

    untrusted = not (
        common_gain_independently_attested is True
        and action_invariant_noise_independently_attested is True
        and zero_probe.controller_mapping_attested is True
        and proposed_probe.controller_mapping_attested is True
    )
    if untrusted:
        return FixedGainNullAudit("UNATTESTED", None, None,
            zero_probe.cost, proposed_probe.cost, None)

    base = np.stack([_vec3(zero_probe.targets[h]) for h in names])
    probe = np.stack([_vec3(proposed_probe.targets[h]) for h in names])
    shifts = probe - base
    if not np.all(np.linalg.norm(shifts - shifts[0], axis=1) <= tol):
        return FixedGainNullAudit("NOT_COMMON_AFFINE_SHIFT", None, None,
            zero_probe.cost, proposed_probe.cost, None)

    d_zero = min(
        float(np.linalg.norm(gain * (base[i] - base[j])))
        for i in range(len(names)) for j in range(i + 1, len(names))
    )
    d_probe = min(
        float(np.linalg.norm(gain * (probe[i] - probe[j])))
        for i in range(len(names)) for j in range(i + 1, len(names))
    )
    if not np.isclose(d_zero, d_probe, rtol=1e-12, atol=2 * tol):
        raise AssertionError("common-translation response-center invariant broken")
    return FixedGainNullAudit(
        "NO_INCREMENTAL_PAIRWISE_SEPARATION_UNDER_FIXED_GAIN",
        d_zero, d_probe, zero_probe.cost, proposed_probe.cost, False
    )
