"""Controller-chart-aware causal compensation for physically held task intents.

This is a testable mechanistic *candidate*, not a learned planner or physical
safety certification. It cannot use the actual hidden target or future
success; a separate privileged t4 read is charged to its caller.
"""
from __future__ import annotations
import numpy as np


def intent_replay_translation(
    current_native6, held_source_native6,
    *, source_low, source_high, target_low, target_high,
    gain: float = 0.5, align_min: float = 0.25, alignment_gate: bool = True,
):
    """Make ONE bounded native command; preserve Euler rotation and gripper.

    held_source_native6: exact frozen PPO output *before* physical fault mask
    at two consecutive stages. Convert original source translation through
    its declared physical chart, project source-lost translation onto current
    target-native direction only when it is still task-direction aligned.
    """
    u=np.asarray(current_native6,dtype=np.float64)
    held=np.asarray(held_source_native6,dtype=np.float64)
    lo_s=np.broadcast_to(np.asarray(source_low,dtype=np.float64),(3,))
    hi_s=np.broadcast_to(np.asarray(source_high,dtype=np.float64),(3,))
    lo_t=np.broadcast_to(np.asarray(target_low,dtype=np.float64),(3,))
    hi_t=np.broadcast_to(np.asarray(target_high,dtype=np.float64),(3,))
    if u.shape!=(6,) or held.shape!=(2,6):
        raise ValueError("Exact native six-vector and TWO delayed source actions required")
    if not all(np.isfinite(x).all() for x in (u,held,lo_s,hi_s,lo_t,hi_t)):
        raise ValueError("Nonfinite native action contract")
    if np.any(lo_s>=hi_s) or np.any(lo_t>=hi_t) or not (0<=gain<=1 and -1<=align_min<=1):
        raise ValueError("Unverified scale, gain or alignment")
    if np.max(np.abs(u[:3]))>1.0000002 or np.linalg.norm(u[3:])>1.0000002:
        raise ValueError("Current target-native command is illegal")
    if np.max(np.abs(held[:,:3]))>1.0000002:
        raise ValueError("Source PPO native command is illegal")

    # Physically meaningful translations, independent of the two native
    # controllers' potentially different normalized physical action scales.
    source_phys=(held[:,:3]+1)*.5*(hi_s-lo_s)+lo_s
    current_phys=(u[:3]+1)*.5*(hi_t-lo_t)+lo_t
    missing_phys=source_phys.sum(axis=0)
    nc=float(np.linalg.norm(current_phys))
    nm=float(np.linalg.norm(missing_phys))
    cos=(float(np.dot(current_phys,missing_phys)/(nc*nm))
         if nc>1e-10 and nm>1e-10 else None)
    out=u.copy()
    update=np.zeros(3)
    mode="no_nonzero_direction"
    if nc>1e-10 and nm>1e-10:
        if alignment_gate:
            if cos is not None and cos>=align_min:
                # A projection along the still-required source action avoids
                # inventing lateral recovery motion when old history is stale.
                unit=current_phys/nc
                update=gain*max(0.,float(np.dot(missing_phys,unit)))*unit
                mode="aligned_projection"
            else:
                mode="direction_mismatch_abstain"
        else:
            update=gain*missing_phys
            mode="unconditional_integral_control"
    proposed_phys=np.clip(current_phys+update,lo_t,hi_t)
    out[:3]=2*(proposed_phys-lo_t)/(hi_t-lo_t)-1
    if np.max(np.abs(out[:3]))>1+1e-8 or np.linalg.norm(out[3:])>1.0000002:
        raise RuntimeError("Invalid compensated native controller command")
    if not np.array_equal(out[3:],u[3:]):
        raise RuntimeError("SO3 rotation changed without a new certificate")
    return tuple(float(x) for x in out), {
        "cosine_of_public_intents":cos,
        "replay_mode":mode,
        "requested_increment_physical_m":update.tolist(),
        "realized_increment_physical_m":(proposed_phys-current_phys).tolist(),
        "rotational_command_unchanged":True,
        "actual_command_changed":bool(np.max(np.abs(out-u))>1e-8),
        "no_hidden_history_read_inside_this_function":True,
    }
