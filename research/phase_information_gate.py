"""Precommitted task-phase private memory query heuristic (not a novel theorem).

This policy was motivated by failures in already-inspected DEVELOPMENT states,
and needs fresh 820001/830001 genuinely executed PhysX states for any claim.

It does NOT use true controller target, seed identity, labels, contact force,
future outcome, or a privileged oracle. It DOES deliberately use task ID.
"""
import math

STEP=4
THRESHOLD=.75


def phase_information_gate(certificate, *, task, step, already_queried=False):
    if task not in ("pull_cube","stack_cube") or type(step) is not int or step<0 or type(already_queried) is not bool:
        raise ValueError("Unsupported task or query time")
    if type(certificate.authorized) is not bool:
        raise ValueError("Finite authorized source certificate required")
    try:
        pos=float(certificate.worst_position_inf_m)
        rot=float(certificate.worst_orientation_geodesic_rad)
    except (TypeError,AttributeError) as e:
        raise ValueError("Incomplete K-history controller authority witness") from e
    if math.isnan(pos) or math.isnan(rot) or pos<0 or rot<0:
        raise ValueError("Invalid nonnegative source setpoint envelope")
    normalized=max(pos/.05,rot/.05)
    if step!=STEP or already_queried:
        return False,normalized
    if task=="stack_cube":
        return True,normalized
    # Intentionally opposite to naive immediate-error margin:
    # early read is sought when a locally 'comfortable' certificate might
    # allow the controller to defer sensing into a future critical phase.
    # A refused common action also demands true state for any continuation.
    return bool(not certificate.authorized or normalized<THRESHOLD),normalized
