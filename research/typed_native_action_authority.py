"""Typed native action chart admission and *measured* roundoff repair.

Motivation: original frozen-PPO PhysX strict-budget new64 trial encountered
native rotational unit-ball violation BEFORE the intended ACK injection at
StackCube seed 370029 (source-original action L2=1.0000009536743164).

This component is a *narrow numerical representability guard* for the exact
ManiSkill root_translation/root_aligned_body_rotation, normalize_action=True
target controller chart. It is NOT a new planner, an optimal projection on
SO(3), a collision/force certificate or a validator for unknown controller
types. It cannot retroactively turn the negative original cohort positive.

An admissible command is a 6D normalized translation BOX and a normalized
Euler XYZ ROTATION UNIT BALL. Inverse charts may produce an O(1e-6) numerical
overshoot of the rotational ball even when the original source policy action
was clipped. Instead of claiming clipped output is the exact requested target,
the gate reports the EXACT commanded-setpoint discrepancy of its candidate
under the verified root-aligned rotation semantics. It only authorizes if that
extra distortion is independently bounded by explicit per-task budgets.

No hidden state read and no numerical cutoff is inferred from task outcome.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from math import isfinite
import numpy as np
from scipy.spatial.transform import Rotation


class Admission(str, Enum):
    UNMODIFIED = "UNMODIFIED"
    ROUNDOFF_CANONICALIZED = "ROUNDOFF_CANONICALIZED"
    REFUSE_BAD_CONTRACT = "REFUSE_BAD_CONTRACT"
    REFUSE_NONFINITE = "REFUSE_NONFINITE"
    REFUSE_TRUE_UNREPRESENTABLE = "REFUSE_TRUE_UNREPRESENTABLE"
    REFUSE_SETPOINT_DISTORTION = "REFUSE_SETPOINT_DISTORTION"


@dataclass(frozen=True)
class NativeActionAuthority:
    status: Admission
    executable_native_6d: tuple[float, ...] | None
    original_native_rot_norm: float
    executed_native_rot_norm: float | None
    translation_extra_setpoint_error_inf_m: float
    rotation_extra_setpoint_error_rad: float
    canonicalization_excess_native_norm: float
    controller_frame: str
    note: str

    @property
    def authorized(self)->bool:
        return self.executable_native_6d is not None


def admit_typed_native_action(
    requested_normalized_6d,
    *,
    pos_lower,
    pos_upper,
    rot_scale,
    known_controller_frame: str,
    trusted_initial_controller_contract: bool,
    numerical_native_overshoot_limit: float = 2e-6,
    max_added_translation_setpoint_error_m: float = 1e-5,
    max_added_rotation_setpoint_error_rad: float = 1e-5,
    strict_interior_guard: float = 1e-8,
)->NativeActionAuthority:
    """Supply the *ACTUAL executable* action or refuse, never claim exactness.

    Source chart:
      position native p in [-1,1]^3 -> lower+(p+1)(upper-lower)/2
      rotation native r in Euclidean ball |r|_2<=1, physical root-left
      Euler "XYZ" angles r * rot_scale (scalar or length-3).

    We compare requested and actual canonicalized ROTATION OBJECTS, not
    raw Euler coordinate differences, and compare translated physical deltas
    coordinatewise. Thus singular Euler chart aliasing cannot silently
    consume an unmeasured orientation budget.

    This does NOT certify subsequent target-memory belief completeness or
    robot's achieved pose. A later K-history authority check must calculate
    the target residual using this exact executed action.
    """
    frame="root_translation:root_aligned_body_rotation"
    try:
        action=np.asarray(requested_normalized_6d,dtype=np.float64)
        low=np.broadcast_to(np.asarray(pos_lower,dtype=np.float64),(3,)).copy()
        high=np.broadcast_to(np.asarray(pos_upper,dtype=np.float64),(3,)).copy()
        scale=np.broadcast_to(np.asarray(rot_scale,dtype=np.float64),(3,)).copy()
    except (ValueError,TypeError):
        raise ValueError("Malformed normalized native action/controller limits")
    if action.shape!=(6,):
        raise ValueError("Native target action must be exactly one 6D vector")
    if (not np.isfinite(low).all() or not np.isfinite(high).all()
        or not np.isfinite(scale).all() or np.any(high<=low)
        or np.any(np.abs(scale)<=1e-12)):
        raise ValueError("Controller chart native limits invalid")
    values=(
        numerical_native_overshoot_limit,
        max_added_translation_setpoint_error_m,
        max_added_rotation_setpoint_error_rad,
        strict_interior_guard
    )
    if (not all(isfinite(float(v)) for v in values)
        or min(values)<0 or strict_interior_guard==0
        or strict_interior_guard>=.01 or numerical_native_overshoot_limit>=.01):
        raise ValueError("Predeclared guard and error allowances required")
    norm=float(np.linalg.norm(action[3:])) if np.isfinite(action[3:]).all() else float("inf")
    base=dict(
        original_native_rot_norm=norm,
        controller_frame=known_controller_frame,
        note=("Commanded-target action-chart admission only; no achieved-pose, "
              "force, collision or hidden ACK completeness guarantee")
    )
    def refused(why: Admission,pos_error=0.,rot_error=0.,over=0.):
        return NativeActionAuthority(
            status=why,executable_native_6d=None,executed_native_rot_norm=None,
            translation_extra_setpoint_error_inf_m=float(pos_error),
            rotation_extra_setpoint_error_rad=float(rot_error),
            canonicalization_excess_native_norm=float(over),**base)
    if (known_controller_frame!=frame
        or type(trusted_initial_controller_contract) is not bool
        or not trusted_initial_controller_contract):
        return refused(Admission.REFUSE_BAD_CONTRACT)
    if not np.isfinite(action).all():
        return refused(Admission.REFUSE_NONFINITE)
    if (np.max(np.abs(action[:3]))>1+numerical_native_overshoot_limit
        or norm>1+numerical_native_overshoot_limit):
        return refused(Admission.REFUSE_TRUE_UNREPRESENTABLE,over=max(0.,norm-1))
    # Input slightly inside ball is returned unchanged except for the exact
    # boundary: strict interior used only for the tiny numeric overshoot.
    out=action.copy()
    out[:3]=np.clip(out[:3],-1.,1.)
    if norm>1-strict_interior_guard:
        out[3:]*=(1-strict_interior_guard)/norm
    p0=low+(action[:3]+1)*(high-low)/2
    p1=low+(out[:3]+1)*(high-low)/2
    trans_error=float(np.max(np.abs(p1-p0)))
    # SO(3) geodesic comparison of actually interpreted Euler objects;
    # no unjustified equivalence of native Euclidean and angular errors.
    orig=Rotation.from_euler("XYZ",action[3:]*scale)
    real=Rotation.from_euler("XYZ",out[3:]*scale)
    rot_error=float((orig.inv()*real).magnitude())
    if (not isfinite(trans_error) or not isfinite(rot_error)
        or trans_error>max_added_translation_setpoint_error_m
        or rot_error>max_added_rotation_setpoint_error_rad):
        return refused(Admission.REFUSE_SETPOINT_DISTORTION,
            pos_error=trans_error,rot_error=rot_error,
            over=max(0.,norm-1))
    if (np.max(np.abs(out[:3]))>1
        or float(np.linalg.norm(out[3:]))>=1
        or not np.isfinite(out).all()):
        raise AssertionError("Internal physical native action representability bug")
    changed=bool(np.any(out!=action))
    return NativeActionAuthority(
        status=Admission.ROUNDOFF_CANONICALIZED if changed else Admission.UNMODIFIED,
        executable_native_6d=tuple(float(x) for x in out),
        executed_native_rot_norm=float(np.linalg.norm(out[3:])),
        translation_extra_setpoint_error_inf_m=trans_error,
        rotation_extra_setpoint_error_rad=rot_error,
        canonicalization_excess_native_norm=max(0.,norm-1),**base
    )
