"""Finite-sample assurance gate for physical probe response labels.

Conformal calibration is valid only under exchangeability of independent reset
CLUSTERS and when the action-probe selector/score predictor is fixed without
using these calibration residuals (or under separately proved adaptive validity).
Never turn an empirical maximum radius or correlated truth worlds into a
physical safety guarantee.

For two candidate hidden ACK histories use Bonferroni alpha/2 for each
hypothesis, so an incorrect exclusion of the true history has <=alpha
marginal rate under these strong assumptions. If alpha/(num hypotheses)
< 1/(n+1), NO FINITE split-conformal radius is possible: abstain/read.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf, isfinite
from typing import Sequence

@dataclass(frozen=True)
class MarginalResponseCoverage:
    radius_m: float
    finite: bool
    group_count: int
    joint_error_budget: float
    per_hypothesis_alpha: float
    conformal_rank: int
    explanation: str
    independent_selector_required: bool = True
    independent_reset_clusters_required: bool = True
    contact_and_ood_safety_guaranteed: bool = False

def calibrated_nonexclusion_radius(
    cluster_worst_case_residuals_m: Sequence[float],
    *,
    joint_alpha: float,
    possible_histories: int,
    selector_fixed_before_calibration: bool,
    score_model_fixed_before_calibration: bool,
) -> MarginalResponseCoverage:
    if (not 0 < joint_alpha < 1
        or type(possible_histories) is not int or possible_histories < 2
        or type(selector_fixed_before_calibration) is not bool
        or type(score_model_fixed_before_calibration) is not bool):
        raise ValueError("Invalid joint error budget, histories or provenance")
    n=len(cluster_worst_case_residuals_m)
    if n==0 or any(
            type(v) not in (int,float) or not isfinite(v) or v<0
            for v in cluster_worst_case_residuals_m):
        raise ValueError("One finite nonnegative worst-case response error per independent reset required")
    per_h=joint_alpha/possible_histories
    k=ceil((n+1)*(1-per_h))
    if (not selector_fixed_before_calibration or
        not score_model_fixed_before_calibration):
        return MarginalResponseCoverage(inf,False,n,joint_alpha,per_h,k,
            "ABSTAIN: predictor/probe selection used this calibration set; split guarantee invalid")
    if k>n:
        return MarginalResponseCoverage(inf,False,n,joint_alpha,per_h,k,
            "ABSTAIN: finite conformal radius impossible at requested group-level risk and n")
    sorted_scores=sorted(float(v) for v in cluster_worst_case_residuals_m)
    return MarginalResponseCoverage(sorted_scores[k-1],True,n,joint_alpha,per_h,k,
        "FINITE MARGINAL RESPONSE COVERAGE ONLY under future reset exchangeability and fixed selector; not conditional robot safety")

def minimum_clusters_for_nonvacuous(joint_alpha: float, possible_histories: int) -> int:
    """Minimum independent exchangeable group scores for a finite Bonferroni radius."""
    if not 0 < joint_alpha < 1 or type(possible_histories) is not int or possible_histories<2:
        raise ValueError("invalid risk request")
    a=joint_alpha/possible_histories
    return ceil(1/a)-1
