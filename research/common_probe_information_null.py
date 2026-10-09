"""Conditional common-input probe identifiability (ordinary linear algebra).

MODEL ONLY, not physical safety or a new theorem. Root additive commanded
target and shared fixed-gain public response:
   M_h_after = M_h + u
   y_h = x + alpha * (M_h_after - x) + e_h
   ||e_h||_2 <= epsilon.
Both candidate observation centers translate by the SAME alpha*u,
so their separation, overlap and minimax worst-case class ambiguity
are independent of u. Unattested or state-/probe-dependent gain,
plant contact and noise invalidate the conclusion.

This source provides a falsifiable NULL for genuine dual-robot PhysX,
not a learned probing policy or a claimed exact dynamics bound.
"""
from __future__ import annotations

import math
from typing import Sequence


def xyz(v:Sequence[float])->tuple[float,float,float]:
    if len(v)!=3:raise ValueError("Three-dimensional achieved/root XYZ required")
    out=tuple(float(x) for x in v)
    if not all(math.isfinite(x) for x in out):raise ValueError("Unbounded coordinate")
    return out


def predicted_public_center(x,m,u,alpha):
    p=xyz(x); target=xyz(m); act=xyz(u)
    if not math.isfinite(alpha) or not 0<=alpha<=1:
        raise ValueError("Independently fixed and finite response gain alpha in [0,1] required")
    return tuple(p[i]+alpha*(target[i]+act[i]-p[i]) for i in range(3))


def public_center_separation(x,m_applied,m_held,u,alpha):
    a=predicted_public_center(x,m_applied,u,alpha)
    b=predicted_public_center(x,m_held,u,alpha)
    return math.dist(a,b)


def worst_case_two_tube_gap(x,m_applied,m_held,u,alpha,epsilon):
    """Positive indicates two closed alpha-fixed L2 error balls are disjoint.

    If <=0, the balls overlap and a public-XYZ-only label cannot be
    deterministically correct on every consistent measurement.
    This is a hypothetical *attested* radius, not an empirical fit.
    """
    if not math.isfinite(epsilon) or epsilon<0:
        raise ValueError("Error radius must be finite and nonnegative")
    return public_center_separation(x,m_applied,m_held,u,alpha)-2*epsilon


def ideal_shared_probe_invariance_witness(x,m_applied,m_held,u,alpha):
    """Check the exact symbolic cancellation with an f64 numerical witness.

    The theorem is algebraic. A finite precision comparison is only
    an implementation diagnostic; a true plant need not satisfy this.
    """
    public_gap=public_center_separation(x,m_applied,m_held,u,alpha)
    invariant=alpha*math.dist(xyz(m_applied),xyz(m_held))
    return {"measured_model_center_gap_m":public_gap,
            "symbolic_shared_gain_gap_m":invariant,
            "numerical_cancellation_error_m":abs(public_gap-invariant),
            "model_requires_shared_gain_noise_and_additive_chart":True,
            "not_physically_attested":True}
