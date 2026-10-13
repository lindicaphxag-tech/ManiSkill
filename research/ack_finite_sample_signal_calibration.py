"""Finite-sample simultaneous ACK-signal likelihood bounds.

Construct two-sided Clopper–Pearson binomial intervals for the held/applied
probability of a PRECOMMITTED binary public signal, simultaneously over an
ENTIRE prospectively fixed finite candidate set. Uses Bonferroni coverage.

This is an auditable arithmetic certificate CONDITIONAL ON iid reset-level
calibration within each ACK truth, fixed signal rule/action list, and no
held-out evaluation reuse. A SHA256 digest is an integrity fingerprint,
not attestation of real PhysX collection or statistical independence.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from typing import Mapping, Sequence

from scipy.stats import beta

from research.ack_native_probe_source_adapter import NativeProbeProposal
from research.ack_robust_readback_value import BinaryProbeEvidence


@dataclass(frozen=True)
class SignalCalibration:
    proposal_name: str
    held_probability_interval: tuple[float, float]
    applied_probability_interval: tuple[float, float]
    samples_per_history: int
    marginal_miscoverage_budget: float
    family_miscoverage_budget: float
    calibration_reset_ids: tuple[int, ...]
    source_digest_sha256: str
    evidence: BinaryProbeEvidence
    # The caller must verify this external condition; a digest cannot.
    physical_response_safety_certified: bool = False


def exact_binomial_interval(successes: int, total: int, alpha: float
                            ) -> tuple[float, float]:
    """Exact central Clopper–Pearson interval for a fixed Bernoulli outcome."""
    if (not isinstance(total, int) or isinstance(total, bool)
            or not isinstance(successes, int) or isinstance(successes, bool)
            or not isinstance(alpha, (int, float))
            or not isfinite(alpha) or not 0 < alpha < 1
            or total < 1 or not 0 <= successes <= total):
        raise ValueError("invalid binomial count or miscoverage probability")
    lower = 0.0 if successes == 0 else float(
        beta.ppf(alpha / 2, successes, total - successes + 1)
    )
    upper = 1.0 if successes == total else float(
        beta.ppf(1 - alpha / 2, successes + 1, total - successes)
    )
    if not (isfinite(lower) and isfinite(upper)
            and 0 <= lower <= upper <= 1):
        raise RuntimeError("cannot compute conservative binomial bounds")
    return lower, upper


def _source_proposal_fingerprint_entry(proposal: NativeProbeProposal) -> dict:
    """Canonical pre-outcome action identity, not proof of physical provenance.

    Include ALL source-replayed commands and all counterfactual history
    targets for the FULL frozen proposal family. A name-only receipt can be
    silently transplanted to a different native action with the same name.
    """
    candidate = proposal.candidate
    if candidate.name != proposal.name:
        raise ValueError("candidate and native-source proposal names disagree")
    if not proposal.source_kinematics_verified:
        raise ValueError("source-replayed native action required")
    return {
        "name": proposal.name,
        "native_action": list(proposal.native_action),
        "history_targets": {
            history: list(candidate.targets[history])
            for history in sorted(candidate.targets)
        },
        "declared_action_cost_not_motor_energy": float(candidate.cost),
        "maximum_translation_deviation_m": float(
            proposal.maximum_translation_deviation_m
        ),
        "source_kinematics_verified": bool(proposal.source_kinematics_verified),
        "controller_mapping_attested_claim": bool(
            candidate.controller_mapping_attested
        ),
        "physical_admissibility_attested_claim": bool(
            candidate.physical_admissibility_attested
        ),
    }



def _optimistic_family_error_limit(
    independent_reset_clusters_per_truth: int,
    precommitted_probe_count: int,
    family_miscoverage: float,
) -> float:
    """Exact two-sided CP perfect-signal tail after Bonferroni correction.

    CONDITIONAL thought experiment: every held sample has Z=0, every applied
    sample Z=1, both histories have the same n independent reset clusters
    and all K prospective actions are calibrated (2*K binomial intervals).
    This is the *best possible* data for this fixed CP/Bonferroni procedure,
    not a physical likelihood bound from the 48-world pilot.
    """
    n, k, delta = (
        independent_reset_clusters_per_truth,
        precommitted_probe_count,
        family_miscoverage,
    )
    if type(n) is not int or n < 1 or type(k) is not int or k < 1:
        raise ValueError("positive integer independent-reset and candidate counts required")
    if not isinstance(delta, (int, float)) or not isfinite(delta) or not 0 < delta < 1:
        raise ValueError("family miscoverage must lie strictly between 0 and 1")
    # For 0/n events the two-sided CP upper endpoint is
    # 1-(alpha/2)^(1/n), where alpha=delta/(2*K). Compute robustly near zero.
    from math import expm1, log
    return float(-expm1(log(float(delta) / (4 * k)) / n))


def optimistic_perfect_signal_binary_ack_risk(
    independent_reset_clusters_per_truth: int,
    precommitted_probe_count: int,
    *,
    family_miscoverage: float = 0.05,
) -> float:
    """Best achievable *certified* symmetric binary error for this protocol.

    Exactly balanced known prior p=0.5, unit false-history costs, an ideal
    separating binary signal and equal n IID reset-level samples per truth.
    Under the current two-sided Clopper-Pearson + Bonferroni family bounds,
    minimax classification risk is min(1/2, CP extreme-probability tail).
    Real sensors, unknown priors and clustered dependence can be worse.
    This is NOT a universal information-theoretic impossibility theorem.
    """
    e = _optimistic_family_error_limit(
        independent_reset_clusters_per_truth, precommitted_probe_count,
        family_miscoverage,
    )
    return min(0.5, e)


def minimum_resets_per_truth_for_optimistic_ack_risk(
    maximum_wrong_history_risk: float,
    precommitted_probe_count: int,
    *,
    family_miscoverage: float = 0.05,
) -> int:
    """Necessary IID reset count *for this CP/Bonferroni method*, best case.

    Returns n per true ACK history AND per precommitted action; the same
    reset seeds may be paired across truths/probes, but are not n*K*2
    statistically independent reset clusters. Never use this number to
    assert that sufficient observations, physical costs or safety exist.
    """
    from math import ceil, log, log1p
    cap = float(maximum_wrong_history_risk)
    if not isfinite(cap) or not 0 < cap < 0.5:
        raise ValueError("symmetric wrong-history risk target must be in (0,0.5)")
    # Validate K, delta without requiring a fake observed dataset.
    _optimistic_family_error_limit(1, precommitted_probe_count,
                                   family_miscoverage)
    n = max(1, ceil(log(float(family_miscoverage) /
                        (4 * precommitted_probe_count)) / log1p(-cap)))
    while optimistic_perfect_signal_binary_ack_risk(
        n, precommitted_probe_count,
        family_miscoverage=family_miscoverage,
    ) > cap:
        n += 1
    while n > 1 and optimistic_perfect_signal_binary_ack_risk(
        n - 1, precommitted_probe_count,
        family_miscoverage=family_miscoverage,
    ) <= cap:
        n -= 1
    return n


def simultaneous_ack_signal_calibration(
    proposals: Sequence[NativeProbeProposal],
    observations: Mapping[str, Sequence[tuple[int, str, int]]],
    *,
    heldout_evaluation_reset_ids: Sequence[int],
    frozen_binary_signal_rule: str,
    family_miscoverage: float = 0.05,
    independently_verified_reset_sampling: bool = False,
    externally_verified_physical_source: bool = False,
    independently_calibrated_action_costs: bool = False,
) -> tuple[SignalCalibration, ...]:
    """Pre-decision calibration for the FULL frozen candidate family.

    Each candidate must have exactly one binary public signal for each ACK
    truth on each registered calibration reset, with NO overlap against
    evaluation resets. Paired worlds MAY reuse seeds across histories/probes;
    within-truth independence across distinct reset clusters is an external
    assumption, NOT proven by the seed identifiers.

    Reserve familywise error `family_miscoverage` across 2*K marginal
    intervals. Posthoc candidate subsetting, signal threshold tuning, or
    correlated reset pseudoreplication would invalidate that guarantee.
    """
    if not isinstance(frozen_binary_signal_rule, str) or not (
        frozen_binary_signal_rule.strip()
    ):
        raise ValueError("precommitted binary signal rule required")
    if not isinstance(family_miscoverage, (int, float)) or not (
        isfinite(family_miscoverage) and 0 < family_miscoverage < 1
    ):
        raise ValueError("familywise miscoverage must be strictly between 0 and 1")
    if not proposals or any(
        not isinstance(p, NativeProbeProposal) for p in proposals
    ):
        raise TypeError("nonempty typed native-source candidate family required")
    if len({p.name for p in proposals}) != len(proposals):
        raise ValueError("nonempty distinct prospective candidate family required")
    if set(observations) != {p.name for p in proposals}:
        raise ValueError("full original candidate family must be calibrated")
    # Canonically bind *all* actual prospective actions, their replayed
    # history targets and declared costs. Each action's receipt changes if
    # ANY member of the frozen family changes, including a name-reused
    # substituted action. This is a content digest, not source authentication.
    proposal_register = [
        _source_proposal_fingerprint_entry(p)
        for p in sorted(proposals, key=lambda p: p.name)
    ]
    eval_ids = set(heldout_evaluation_reset_ids)
    if len(eval_ids) != len(heldout_evaluation_reset_ids) or any(
        type(i) is not int for i in eval_ids
    ):
        raise ValueError("evaluation reset identifiers must be unique integers")
    alpha = float(family_miscoverage) / (2 * len(proposals))
    calibrated = []
    for proposal in proposals:
        raw = observations[proposal.name]
        if not isinstance(raw, Sequence):
            raise TypeError("original per-probe response sequence required")
        records = []
        for seed, truth, z in raw:
            if type(seed) is not int or truth not in ("held", "applied") or type(z) is not int or z not in (0, 1):
                raise ValueError("invalid original reset/ACK/binary signal tuple")
            if seed in eval_ids:
                raise ValueError("calibration and evaluation resets overlap")
            records.append((seed, truth, z))
        keys = {(seed, truth) for seed, truth, _ in records}
        if len(keys) != len(records):
            raise ValueError("duplicate reset/ACK row: no pseudoreplication")
        held = {seed: z for seed, truth, z in records if truth == "held"}
        applied = {seed: z for seed, truth, z in records if truth == "applied"}
        if not held or set(held) != set(applied):
            raise ValueError("paired original reset conditions are incomplete")
        ordered = sorted(records)
        fingerprint = sha256(
            json.dumps({
                "signal_rule": frozen_binary_signal_rule,
                "schema": "ack-signal-calibration-full-native-action-register-v2",
                "family_source_register": proposal_register,
                "proposal": proposal.name,
                "observations": ordered,
                "heldout": sorted(eval_ids),
                "alpha": float(family_miscoverage),
            }, separators=(",", ":"), sort_keys=True,
                allow_nan=False).encode()
        ).hexdigest()
        n = len(held)
        h_interval = exact_binomial_interval(sum(held.values()), n, alpha)
        a_interval = exact_binomial_interval(sum(applied.values()), n, alpha)
        # It would be unsafe to infer independence or physical legitimacy
        # from data labels or SHA256 fingerprints alone.
        attested = (
            independently_verified_reset_sampling is True
            and externally_verified_physical_source is True
        )
        evidence = BinaryProbeEvidence(
            proposal=proposal,
            p_signal_held=h_interval,
            p_signal_applied=a_interval,
            independent_holdout_calibration_attested=attested,
            calibrated_cost_attested=independently_calibrated_action_costs is True,
            calibration_receipt=f"sha256:{fingerprint}",
        )
        calibrated.append(SignalCalibration(
            proposal.name, h_interval, a_interval, n, alpha,
            float(family_miscoverage), tuple(sorted(held)), fingerprint,
            evidence
        ))
    return tuple(calibrated)
