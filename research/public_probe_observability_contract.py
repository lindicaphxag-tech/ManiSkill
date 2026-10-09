"""Conditional public-motion ACK-history identifiability, before expensive PhysX tests.

All guarantees rely on independently ATTESTED response envelopes. This module
does not calibrate them or claim robot/collision safety, PPO task success,
hardware support, or ability to observe undisclosed controller target states.

A known-delivered *common* XYZ translation d creates an observation segment
x + alpha * (M_h + d - x), alpha in [lo,hi], for each finite history h.
Any public observation can deviate in L2 norm by independently bounded epsilon.
Pairwise disjoint epsilon-tubes permit a unique history diagnosis; otherwise
the caller must query the authoritative controller target or refuse.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite, sqrt
from typing import Sequence


class Gate(str, Enum):
    PROBE_ZERO = "PROBE_ZERO"
    PROBE_TRANSLATE = "PROBE_TRANSLATE"
    QUERY_REQUIRED = "QUERY_REQUIRED"
    REFUSE = "REFUSE"


class Observation(str, Enum):
    UNIQUE = "UNIQUE"
    AMBIGUOUS_QUERY = "AMBIGUOUS_QUERY"
    MODEL_FALSIFIED = "MODEL_FALSIFIED"
    REFUSE_UNVERIFIED_DISPATCH = "REFUSE_UNVERIFIED_DISPATCH"


Vec3 = tuple[float, float, float]
Segment = tuple[Vec3, Vec3]


def _vec(a: Sequence[float], name: str) -> Vec3:
    try:
        v = tuple(float(z) for z in a)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must contain three finite coordinates") from exc
    if len(v) != 3 or not all(isfinite(z) and abs(z) <= 100.0 for z in v):
        raise ValueError(f"{name} must contain exactly three finite bounded XYZ coordinates")
    return v  # type: ignore[return-value]


def _dot(a: Vec3, b: Vec3) -> float:
    return sum(x * y for x, y in zip(a, b))


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return tuple(x - y for x, y in zip(a, b))  # type: ignore[return-value]


def _add(a: Vec3, b: Vec3) -> Vec3:
    return tuple(x + y for x, y in zip(a, b))  # type: ignore[return-value]


def _mul(a: Vec3, s: float) -> Vec3:
    return tuple(s * x for x in a)  # type: ignore[return-value]


def _norm(v: Vec3) -> float:
    return sqrt(_dot(v, v))


def _clamp(x: float) -> float:
    return min(1.0, max(0.0, x))


def _point_segment_distance(y: Vec3, seg: Segment) -> float:
    a, b = seg
    u = _sub(b, a)
    q = _dot(u, u)
    t = _clamp(_dot(_sub(y, a), u) / q) if q else 0.0
    return _norm(_sub(y, _add(a, _mul(u, t))))


def _segment_distance(seg_a: Segment, seg_b: Segment) -> float:
    """Exact minimum between two closed segments up to float roundoff.

    Quadratic convex minimization in two segment parameters: a global
    unconstrained stationary point (when nonparallel) OR one of four
    boundaries. Endpoints and boundary projections cover degeneracies.
    """
    a, b = seg_a
    c, d = seg_b
    u, v, w = _sub(b, a), _sub(d, c), _sub(a, c)
    uu, vv = _dot(u, u), _dot(v, v)
    uv, uw, vw = _dot(u, v), _dot(u, w), _dot(v, w)
    candidates = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
    for s in (0.0, 1.0):
        t = _clamp(_dot(v, _sub(_add(a, _mul(u, s)), c)) / vv) if vv else 0.0
        candidates.append((s, t))
    for t in (0.0, 1.0):
        s = _clamp(_dot(u, _sub(_add(c, _mul(v, t)), a)) / uu) if uu else 0.0
        candidates.append((s, t))
    det = uu * vv - uv * uv
    if det > 1e-12 * max(uu * vv, 1e-30):
        s = (uv * vw - vv * uw) / det
        t = (uu * vw - uv * uw) / det
        if 0.0 <= s <= 1.0 and 0.0 <= t <= 1.0:
            candidates.append((s, t))
    return min(_norm(_sub(_add(a, _mul(u, s)), _add(c, _mul(v, t))))
               for s, t in candidates)



def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _segment_separation_lower_bound(seg_a: Segment, seg_b: Segment) -> float:
    """CERTIFIED lower bound on minimum Euclidean segment separation.

    For ANY unit vector n, the gap between scalar projection intervals of two
    segments is <= their true Euclidean minimum distance (Cauchy-Schwarz).
    The maximum of finitely many such gaps stays a VALID lower bound,
    even for degenerate or near-parallel segments. Unlike a floating-point
    two-variable closest-points optimizer, it can never over-certify due to
    omitted or numerically unstable stationary points (up to rounding guard).
    """
    a0, a1 = seg_a
    b0, b1 = seg_b
    u, v = _sub(a1, a0), _sub(b1, b0)
    candidate_axes: list[Vec3] = [
        (1.,0.,0.), (0.,1.,0.), (0.,0.,1.),
        _cross(u, v)]
    # Closest endpoint to opposing infinite line provides helpful support
    # normals for skew/near-parallel cases; NEVER assume a candidate optimal.
    for endpoint in seg_a:
        w = _sub(endpoint, b0)
        vv = _dot(v, v)
        candidate_axes.append(_sub(w, _mul(v, _dot(w,v)/vv)) if vv else w)
    for endpoint in seg_b:
        w = _sub(endpoint, a0)
        uu = _dot(u, u)
        candidate_axes.append(_sub(w, _mul(u, _dot(w,u)/uu)) if uu else w)
    candidate_axes.extend(_sub(x,y) for x in seg_a for y in seg_b)
    lower = 0.0
    for n in candidate_axes:
        length = _norm(n)
        if length < 1e-14:
            continue
        na = [_dot(n,x)/length for x in seg_a]
        nb = [_dot(n,x)/length for x in seg_b]
        # A gap in one scalar projection is a safe spatial separation witness.
        gap = max(0.0, min(na)-max(nb), min(nb)-max(na))
        lower = max(lower, gap)
    # Account for floating-point projection / subtraction near the boundary.
    return max(0.0, lower - 1e-10)

@dataclass(frozen=True)
class ProbeContract:
    # Every credible controller commanded target, not private target truth.
    targets_xyz_m: tuple[Vec3, ...]
    public_before_xyz_m: Vec3
    source_desired_target_xyz_m: Vec3
    gain_min: float
    gain_max: float
    public_model_error_l2_m: float
    numerical_guard_m: float
    native_delta_min_xyz_m: Vec3
    native_delta_max_xyz_m: Vec3
    max_probe_translation_l2_m: float
    max_target_deviation_linf_m: float
    histories_complete: bool
    provenance_trusted: bool
    controller_chart_verified: bool
    calibration_independent_attested: bool

    def validated(self) -> "ProbeContract":
        if not (2 <= len(self.targets_xyz_m) <= 16):
            raise ValueError("Require 2..16 explicit target hypotheses")
        for i, target in enumerate(self.targets_xyz_m):
            _vec(target, f"target[{i}]")
        _vec(self.public_before_xyz_m, "public before")
        _vec(self.source_desired_target_xyz_m, "source desired")
        low = _vec(self.native_delta_min_xyz_m, "native delta lower")
        high = _vec(self.native_delta_max_xyz_m, "native delta upper")
        values = (self.gain_min, self.gain_max,
                  self.public_model_error_l2_m, self.numerical_guard_m,
                  self.max_probe_translation_l2_m, self.max_target_deviation_linf_m)
        if not all(isinstance(x, (int, float)) and isfinite(x) for x in values):
            raise ValueError("Nonfinite envelope or budget")
        if not (0 <= self.gain_min <= self.gain_max <= 1
                and 0 <= self.public_model_error_l2_m <= .25
                and 1e-12 <= self.numerical_guard_m <= 1e-4
                and 0 <= self.max_probe_translation_l2_m <= .2
                and 0 <= self.max_target_deviation_linf_m <= .2
                and all(l <= 0 <= h for l, h in zip(low, high))):
            raise ValueError("Unsupported gain, error, guard, native chart or probe budget")
        return self


@dataclass(frozen=True)
class ProbePlan:
    gate: Gate
    translation_xyz_m: Vec3 | None
    # Strictly positive means pairwise public response sets cannot overlap.
    worst_pair_clearance_after_noise_m: float
    segments_by_history: tuple[Segment, ...]
    model_error_l2_m: float
    numerical_guard_m: float
    reason: str


@dataclass(frozen=True)
class ProbeObservation:
    status: Observation
    history_index: int | None
    compatible_indices: tuple[int, ...]
    residuals_m: tuple[float, ...]
    reason: str


def _segments(p: ProbeContract, d: Vec3) -> tuple[Segment, ...]:
    x = p.public_before_xyz_m
    out = []
    for m in p.targets_xyz_m:
        vec = _sub(_add(m, d), x)
        out.append((_add(x, _mul(vec, p.gain_min)),
                    _add(x, _mul(vec, p.gain_max))))
    return tuple(out)


def _admissible(p: ProbeContract, d: Vec3) -> bool:
    if (_norm(d) > p.max_probe_translation_l2_m + 1e-12
            or any(a < l - 1e-12 or a > h + 1e-12
                   for a, l, h in zip(d, p.native_delta_min_xyz_m,
                                       p.native_delta_max_xyz_m))):
        return False
    return all(max(abs(mj + dj - qj) for mj, dj, qj in
                   zip(m, d, p.source_desired_target_xyz_m))
               <= p.max_target_deviation_linf_m + 1e-12
               for m in p.targets_xyz_m)


def plan_public_probe(p: ProbeContract,
                      candidates_xyz_m: Sequence[Sequence[float]],
                      *, privileged_query_available: bool) -> ProbePlan:
    """Only authorize physical probes under verified chart and observation contract.

    The caller must separately verify actual physical probe delivery before
    interpreting observations. No privileged controller getter is used here.
    """
    p.validated()
    def blocked(reason: str) -> ProbePlan:
        return ProbePlan(Gate.QUERY_REQUIRED if privileged_query_available else Gate.REFUSE,
                         None, 0.0, (), p.public_model_error_l2_m,
                         p.numerical_guard_m, reason)
    if not (p.histories_complete and p.provenance_trusted and p.controller_chart_verified):
        return blocked("Incomplete history/provenance or unverified native action chart")
    if not p.calibration_independent_attested:
        return blocked("Public-motion response envelope has no independent attestation")
    # A zero target delta is a genuine known-delivered active measurement
    # only if the real robot controller permits it and the action actually runs.
    seen: set[Vec3] = set()
    feasible: list[tuple[float, float, Vec3, tuple[Segment, ...]]] = []
    for raw in [(0.0, 0.0, 0.0), *candidates_xyz_m]:
        d = _vec(raw, "probe delta")
        if d in seen:
            continue
        seen.add(d)
        if not _admissible(p, d):
            continue
        segs = _segments(p, d)
        worst = min(_segment_separation_lower_bound(segs[i], segs[j])
                    for i in range(len(segs)) for j in range(i + 1, len(segs)))
        clearance = worst - 2 * (p.public_model_error_l2_m + p.numerical_guard_m)
        feasible.append((clearance, _norm(d), d, segs))
    if not feasible:
        return blocked("No common native translation keeps ALL hypothetical targets within declared cap")
    # Prefer a legal zero command whenever it is already observably identifying.
    certified_zeros = [r for r in feasible if r[1] == 0 and r[0] > 0]
    if certified_zeros:
        best = certified_zeros[0]
    else:
        best = sorted(feasible, key=lambda r: (-r[0], r[1], r[2]))[0]
    if best[0] <= 0:
        return blocked("Every legal public probe has intersecting uncertainty tubes")
    return ProbePlan(Gate.PROBE_ZERO if best[1] == 0 else Gate.PROBE_TRANSLATE,
                     best[2], best[0], best[3],
                     p.public_model_error_l2_m, p.numerical_guard_m,
                     "Conditional pairwise disjoint 3-D public observation tubes; no task-safety guarantee")


def identify_after_probe(plan: ProbePlan, public_after_xyz_m: Sequence[float],
                         *, known_native_dispatch_confirmed: bool) -> ProbeObservation:
    """No ACK truth leak: identify only from public XYZ against certified tubes."""
    if plan.gate not in (Gate.PROBE_ZERO, Gate.PROBE_TRANSLATE):
        raise ValueError("Cannot identify from an unapproved or absent physical probe")
    if not known_native_dispatch_confirmed:
        return ProbeObservation(Observation.REFUSE_UNVERIFIED_DISPATCH,
                                None, (), (), "Probe delivery itself was not confirmed")
    y = _vec(public_after_xyz_m, "public after")
    residuals = tuple(_point_segment_distance(y, s) for s in plan.segments_by_history)
    fit = tuple(i for i, r in enumerate(residuals)
                if r <= plan.model_error_l2_m + plan.numerical_guard_m)
    if len(fit) == 1:
        return ProbeObservation(Observation.UNIQUE, fit[0], fit, residuals,
                                "Exactly one history fits independently attested response envelope")
    if fit:
        return ProbeObservation(Observation.AMBIGUOUS_QUERY, None, fit, residuals,
                                "Several histories remain compatible; must query/refuse")
    return ProbeObservation(Observation.MODEL_FALSIFIED, None, (), residuals,
                            "Public achieved motion falsifies all predicted responses; fail closed")
