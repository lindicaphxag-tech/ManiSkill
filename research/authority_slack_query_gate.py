"""Task-independent, authority-slack proactive private-target query at one fixed phase.

Decision input is ONLY a complete native-controller setpoint certificate
computed from public achieved kinematics, learned policy output, and the
enumerated finite command-delivery hypotheses. No private true target pose,
test success, task name, or future outcome is accessible to the query rule.

Return (query, ratio). This is a heuristic query TIER, not a certificate that
a model won't fail, a globally optimal POMDP solution, or collision safety.
"""
import math

PROACTIVE_STEP=4
THRESHOLD=.75
POSITION_BUDGET=.05
ROTATION_BUDGET=.05


def proactive_authority_slack(certificate, *, step, already_queried=False):
    if type(step) is not int or step<0 or type(already_queried) is not bool:
        raise ValueError("Invalid observable step/query history")
    if not math.isfinite(THRESHOLD) or not 0<THRESHOLD<1:
        raise ValueError("Research threshold corrupt")
    if not hasattr(certificate,"authorized") or type(certificate.authorized) is not bool:
        raise ValueError("Incomplete finite-controller certificate")
    pos=float(certificate.worst_position_inf_m)
    rot=float(certificate.worst_orientation_geodesic_rad)
    if pos<0 or rot<0 or math.isnan(pos) or math.isnan(rot):
        raise ValueError("Invalid nonnegative bound")
    ratio=max(pos/POSITION_BUDGET,rot/ROTATION_BUDGET)
    if step!=PROACTIVE_STEP or already_queried:
        return False,ratio
    # If the predicted common action refuses, a trusted query may resolve it.
    # If it is representable but close to its authority tolerance, query NOW.
    return bool(not certificate.authorized or ratio>=THRESHOLD),ratio
