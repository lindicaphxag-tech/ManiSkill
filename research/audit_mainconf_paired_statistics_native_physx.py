"""Recompute REVIEWER-LEVEL paired statistics from immutable 640-world PhysX data.

Not new physics, not independent laboratory reproduction, not a confirmatory
success claim. Original 64 resets / 10 actually stepped controller worlds have
common random seed but shared task policy and correlated simulated dynamics.

Uses Python standard library only; Pin exact full-original Git blob.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha1
from itertools import combinations
import json
from math import comb, sqrt
from pathlib import Path

SOURCE = Path("research/frozen_policy_transfer/evidence/"
              "ood_pd_drive_known_ack_anchor_original64_960101_970132/"
              "INDEPENDENT_PANDA_PHYSX_OOD_ANCHOR_REAL640.json")
ORIGINAL_BLOB = "2fbbd40b7a91a347fd7afa004a8b1c1c4042b749"
ARMS = ("old", "anchor", "strong")
EPS = {"pull_cube": 0.006944262561376447,
       "stack_cube": 0.00719087965534261}
ALPHA = 0.05


def git_blob(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def exact_binomial_upper(x: int, n: int, alpha: float = ALPHA) -> float:
    """One-sided exact 1-alpha Clopper-Pearson upper for Bernoulli iid cases."""
    if not 0 <= x <= n or not n:
        raise ValueError("Bernoulli observations required")
    if x == n:
        return 1.0
    lo, hi = 0.0, 1.0
    # P_X<=x | p_upper == alpha; binomial CDF decreasing with p.
    for _ in range(100):
        mid = (lo + hi) / 2
        cdf = sum(comb(n, k) * mid**k * (1-mid)**(n-k)
                  for k in range(x+1))
        if cdf > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def exact_two_sided_sign_p(positives: int, negatives: int) -> float:
    """Descriptive sign analysis after omitting ties (iid sign null only)."""
    n = positives + negatives
    if n == 0:
        return 1.0
    return min(1.0, 2.0 * sum(comb(n, k) for k in
                             range(min(positives, negatives)+1)) / 2**n)


def paired_binary(rows, a: str, b: str):
    both = sum(bool(r[a]) and bool(r[b]) for r in rows)
    a_only = sum(bool(r[a]) and not bool(r[b]) for r in rows)
    b_only = sum(not bool(r[a]) and bool(r[b]) for r in rows)
    neither = len(rows) - both - a_only - b_only
    return {"both_success": both, "a_only_success": a_only,
            "b_only_success": b_only, "neither_success": neither,
            "exploratory_exact_discordance_sign_p":
                exact_two_sided_sign_p(a_only, b_only)}


def paired_reads(rows, a: str, b: str):
    better_a = sum(r[a] < r[b] for r in rows)
    better_b = sum(r[b] < r[a] for r in rows)
    ties = len(rows) - better_a - better_b
    return {"a_uses_less": better_a, "b_uses_less": better_b, "ties": ties,
            "a_total": sum(r[a] for r in rows),
            "b_total": sum(r[b] for r in rows),
            "net_reads_saved_by_a": sum(r[b]-r[a] for r in rows),
            "exploratory_exact_sign_p": exact_two_sided_sign_p(better_a, better_b)}


def score(rows):
    n = len(rows)
    result = {"n_original_reset_states": n, "n_actual_native_controller_worlds": n*10,
              "by_policy": {}}
    for arm in ("old", "anchor", "strong"):
        result["by_policy"][arm] = {
            "official_task_success": sum(r[f"{arm}_success"] for r in rows),
            "privileged_target_decision_reads": sum(r[f"{arm}_reads"] for r in rows)}
    for arm in ("old", "anchor"):
        k = sum(r[f"{arm}_authorized"] for r in rows)
        wrong = sum(r[f"{arm}_wrong_confident"] for r in rows)
        nbad = sum(r["true_response_outside_model"] for r in rows)
        result["by_policy"][arm].update({
            "public_unique_full_history_authorizations": k,
            "wrong_confident_full_history_authorizations": wrong,
            "wrong_confident_one_sided_95pct_exact_upper_if_iid_accepted": (
                exact_binomial_upper(wrong, k) if k else None),
            "actual_true_history_response_outside_original_model": nbad,
            "public_achieved_XYZ_reads": n*(4 if arm=="anchor" else 2)})
    result["paired_anchor_v_old_task"] = paired_binary(
        rows, "anchor_success", "old_success")
    result["paired_old_v_strong_task"] = paired_binary(
        rows, "old_success", "strong_success")
    result["paired_anchor_v_strong_task"] = paired_binary(
        rows, "anchor_success", "strong_success")
    result["paired_old_v_anchor_reads"] = paired_reads(
        rows, "old_reads", "anchor_reads")
    result["paired_old_v_strong_reads"] = paired_reads(
        rows, "old_reads", "strong_reads")
    result["paired_anchor_v_strong_reads"] = paired_reads(
        rows, "anchor_reads", "strong_reads")
    result["model_failure_diagnostic"] = {
        "future_true_model_outside_count": sum(
            r["true_response_outside_model"] for r in rows),
        "future_true_model_outside_rate": (
            sum(r["true_response_outside_model"] for r in rows)/n if n else None),
        "pre_fault_anchor_flagged_model_failure": sum(
            r["true_response_outside_model"] and not r["pre_fault_anchor_pass"] for r in rows),
        "pre_fault_anchor_missed_model_failure": sum(
            r["true_response_outside_model"] and r["pre_fault_anchor_pass"] for r in rows),
        "pre_fault_anchor_false_alert_model_valid": sum(
            not r["true_response_outside_model"] and not r["pre_fault_anchor_pass"] for r in rows),
        "pre_fault_anchor_passed_model_valid": sum(
            not r["true_response_outside_model"] and r["pre_fault_anchor_pass"] for r in rows)}
    return result


def analyse():
    raw = SOURCE.read_bytes()
    if git_blob(raw) != ORIGINAL_BLOB:
        raise ValueError("Full original physical source Git blob changed")
    data = json.loads(raw)
    assert data["original_registered_source_reset_states"] == 64
    assert data["source_original_native_physx_worlds"] == 640
    records = data["all_original_trial_rows"]
    seen = set()
    rows = []
    for src in records:
        task, seed = src["task"], src["seed"]
        if task not in EPS or (task, seed) in seen:
            raise ValueError("Unknown/duplicate actual PPO trial")
        seen.add((task, seed))
        if not ((960101 <= seed <= 960132 and task == "pull_cube") or
                (970101 <= seed <= 970132 and task == "stack_cube")):
            raise ValueError("Trial outside prospective native physical population")
        combo = ("A" if seed % 2 == 0 else "H") + (
            "A" if (seed//2) % 2 == 0 else "H")
        drive = "slow" if (seed//4) % 2 == 0 else "fast"
        if combo != src["true_joint_ack"] or drive != src["physics_drive_mode"]:
            raise ValueError("Precommitted physical truth or gain violated")
        old = src["narrow_public_evidence"]
        anchor = src["anchor_public_evidence"]
        def validate_public(e, short):
            truth = e["audit_only_true_candidate_indices"]
            residuals = e["candidate_residuals_m"]
            if len(truth) != 1 or len(residuals) != 4:
                raise ValueError("Must have one real target and four plausible controller histories")
            if e["prior_training_epsilon_m"] != EPS[task]:
                raise ValueError("Changed original native physical response eps")
            winning = [i for i, r in enumerate(residuals) if r <= EPS[task]+1e-12]
            separated = len(winning) == 1 and all(
                v > EPS[task]+0.002 for i, v in enumerate(residuals) if i != winning[0])
            auth = separated and (short == "old" or bool(src["anchor_known_t1_evidence"]["passes"]))
            if auth is not e["authorized"]:
                raise ValueError("Public native target authorization not determined by public evidence")
            wrong = auth and winning[0] != truth[0]
            if wrong is not e["wrong_confident"]:
                raise ValueError("Wrong confident target event cannot be recomputed")
            if e["audit_only_hidden_target_was_NOT_decision_input"] is not True:
                raise ValueError("Leakage of hidden native controller memory into decision")
            return residuals[truth[0]], auth, wrong
        d_old, auth_old, wrong_old = validate_public(old, "old")
        d_anchor, auth_anchor, wrong_anchor = validate_public(anchor, "anchor")
        if abs(d_old-d_anchor) > 1e-6:
            raise ValueError("Paired physics changes actual native response model")
        x = {"task": task, "seed": seed, "drive": drive, "actual_ACK": combo,
             "true_response_outside_model": d_old > EPS[task],
             "true_response_residual_m": d_old,
             "pre_fault_anchor_pass": bool(src["anchor_known_t1_evidence"]["passes"])}
        for arm, suc, cost in (
            ("old", src["narrow_success"], src["narrow_reads"]),
            ("anchor", src["anchor_success"], src["anchor_reads"]),
            ("strong", src["strong_success"], src["strong_reads"])):
            if type(suc) is not bool or type(cost) is not int or cost not in (0, 1):
                raise ValueError("Nonphysical or uncounted official result and decision read")
            x[f"{arm}_success"] = suc
            x[f"{arm}_reads"] = cost
        x.update(old_authorized=auth_old, old_wrong_confident=wrong_old,
                 anchor_authorized=auth_anchor, anchor_wrong_confident=wrong_anchor)
        rows.append(x)
    if len(rows) != 64:
        raise ValueError("Not 64 prospectively frozen unique states")
    group = defaultdict(list)
    for x in rows:
        group[(x["task"], x["drive"], x["actual_ACK"])].append(x)
    if len(group) != 16 or any(len(v) != 4 for v in group.values()):
        raise ValueError("Source true physics stratification 2 task × 2 gains × 4 ACK incomplete")
    report = {
        "schema": "main_conf_immutable_real_physx_640_world_paired_stat_and_risk_budget_v1",
        "source_original_full_native_PhysX_git_blob": ORIGINAL_BLOB,
        "source_original_trial_population": [(r["task"], r["seed"]) for r in rows],
        "overall": score(rows),
        "per_task": {task: score([r for r in rows if r["task"] == task])
                     for task in ("pull_cube", "stack_cube")},
        "per_physical_drive": {gain: score([r for r in rows if r["drive"] == gain])
                               for gain in ("slow", "fast")},
        "full_16_cells": {":".join(key): score(vals) for key, vals in sorted(group.items())},
        "not_confirmatory_hypothesis_test": True,
        "zero_confident_errors_NOT_certificate": True,
        "confidence_upper_bounds_require_iid_acceptance_cases": True,
        "fixed_source_seed_independence_not_established": True,
        "multiple_posthoc_analyses_not_adjusted": True,
        "positive_or_negative_task_improvement_not_assumed": True,
        "same_actuation_but_anchor_uses_twice_public_XYZ": True,
        "comparator_source_policy_real_physically_stepped": True,
        "source_errors_fail_closed": True}
    r = report["overall"]
    assert r["by_policy"]["old"]["official_task_success"] == 56
    assert r["by_policy"]["anchor"]["official_task_success"] == 56
    assert r["by_policy"]["strong"]["official_task_success"] == 55
    assert r["by_policy"]["old"]["privileged_target_decision_reads"] == 56
    assert r["by_policy"]["anchor"]["privileged_target_decision_reads"] == 62
    assert r["by_policy"]["strong"]["privileged_target_decision_reads"] == 50
    assert r["by_policy"]["old"]["public_unique_full_history_authorizations"] == 8
    assert r["by_policy"]["anchor"]["public_unique_full_history_authorizations"] == 2
    assert r["model_failure_diagnostic"] == {
        "future_true_model_outside_count": 8,
        "future_true_model_outside_rate": 0.125,
        "pre_fault_anchor_flagged_model_failure": 4,
        "pre_fault_anchor_missed_model_failure": 4,
        "pre_fault_anchor_false_alert_model_valid": 30,
        "pre_fault_anchor_passed_model_valid": 26}
    return report


if __name__ == "__main__":
    import sys
    result = analyse()
    result_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if result_path:
        result_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("SOURCE_GIT_PINNED_REAL_640_PHYSX_TASK_PAIRED_AND_RISK", json.dumps({
        "overall": result["overall"],
        "by_task": result["per_task"],
        "by_gain": result["per_physical_drive"],
        "one_sided_95_exact_wrong_confidence_upper_old":
          result["overall"]["by_policy"]["old"]["wrong_confident_one_sided_95pct_exact_upper_if_iid_accepted"],
        "one_sided_95_exact_wrong_confidence_upper_anchor":
          result["overall"]["by_policy"]["anchor"]["wrong_confident_one_sided_95pct_exact_upper_if_iid_accepted"]},
        sort_keys=True))
