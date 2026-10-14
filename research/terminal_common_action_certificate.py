"""Conditional target-position feasibility under ambiguous execution histories.

Native contract: normalized root-frame target-relative delta translation,
use_delta=use_target=normalize_action=True. This does NOT certify contact,
collision, rotation, controller tracking, or real robot safety.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class PositionAuthority:
    authorized: bool
    reason: str
    native_six_position_only: tuple[float, ...] | None
    maximum_axis_residual_m: tuple[float, float, float]
    historical_half_diameter_m: tuple[float, float, float]
    n_histories: int
    physical_safety_certified: bool = False


def _xyz(value, name):
    v = np.asarray(value, dtype=np.float64)
    if v.shape != (3,) or not np.isfinite(v).all():
        raise ValueError(f"finite XYZ required for {name}")
    return v


def conditional_common_position_authority(
    histories_xyz, goal_xyz, task_tolerance_xyz, action_pos_lower,
    action_pos_upper, *, external_error_bound_xyz=(0., 0., 0.),
    external_error_envelope_attested=False, numerical_guard=1e-10,
):
    """Minimize max-history goal error over ONE native action, without ACK truth.

    The common controller translation delta_j belongs to [low_j, high_j].
    min_delta max_h |x_hj+delta-g_j| has solution
        clip(g_j-(min_h x_hj+max_h x_hj)/2, low_j, high_j)
    and has unconditional lower bound history_diameter_j/2.
    This follows elementary Chebyshev minimax geometry and is NOT a new
    optimal-control theorem. Exact real-arithmetic solution; float tolerance
    guard is not a proof of hardware safety.
    """
    x = np.asarray(histories_xyz, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 1 or not np.isfinite(x).all():
        raise ValueError("nonempty finite N-by-3 hypotheses required")
    g = _xyz(goal_xyz, "goal")
    tol = _xyz(task_tolerance_xyz, "task_tolerance")
    lo = _xyz(action_pos_lower, "action_low")
    hi = _xyz(action_pos_upper, "action_high")
    err = _xyz(external_error_bound_xyz, "external_error")
    if np.any(tol < 0) or np.any(err < 0) or np.any(lo >= hi):
        raise ValueError("invalid native action or error bounds")
    if not np.isfinite(numerical_guard) or numerical_guard <= 0:
        raise ValueError("positive finite numerical guard required")
    mn, mx = x.min(axis=0), x.max(axis=0)
    midpoint = mn / 2 + mx / 2
    delta = np.clip(g - midpoint, lo, hi)
    resid = x + delta - g
    worst = np.max(np.abs(resid), axis=0) + err + numerical_guard
    floor = (mx - mn) / 2 + err
    if not all(np.isfinite(v).all() for v in (midpoint, delta, resid, worst, floor)):
        raise ValueError("nonfinite arithmetic result")
    native = 2 * (delta - lo) / (hi - lo) - 1
    if not np.isfinite(native).all() or np.any(np.abs(native) > 1+1e-8):
        raise ValueError("unrepresentable action")
    admit = bool(np.all(worst <= tol)) and external_error_envelope_attested is True
    if external_error_envelope_attested is not True:
        reason = "UNATTESTED_RESPONSE_ERROR_ENVELOPE"
    elif admit:
        reason = "MODEL_CONDITIONAL_POSITION_ONLY"
    elif np.any(floor + numerical_guard > tol):
        reason = "COMMON_DELTA_CANNOT_SHRINK_HISTORY_DIAMETER"
    else:
        reason = "NATIVE_DELTA_RANGE_TOO_NARROW"
    return PositionAuthority(admit, reason,
        tuple(map(float, [*native, 0., 0., 0.])) if admit else None,
        tuple(map(float, worst)), tuple(map(float, floor)), len(x))
